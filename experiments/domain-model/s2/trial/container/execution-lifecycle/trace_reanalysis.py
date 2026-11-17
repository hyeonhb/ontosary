"""Bounded, offline interpretation of the sealed policy-pair trace.

This is deliberately not imported by the runtime or historical verifier.
Only namespace clone observations are parsed; unrelated startup/thread syscalls
are outside the evidence scope. Source lines are never rewritten.
"""
import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / 'single-policy-test'),
                str(HERE.parent / 'lifecycle')]
from policy_pair import FLAGS, trace_observation
from verify_pair import verify
from verify_recovery import contents
from scope import verify_index

MAX_BYTES = 16 * 1024 * 1024
MAX_LINE = 65536
MAX_PENDING_BYTES = 4096
MAX_PENDING = 32
MAX_OBSERVATIONS = 256
MAX_ISSUES = 64
MAX_CONTEXT_EVENTS = 128
MAX_CONTEXT_BYTES = 65536
PID = re.compile(r'\[pid\s+([1-9][0-9]{0,9})\]\s+(.*)')
START = 'clone(child_stack=NULL, flags=' + FLAGS
RETURN = r'\)\s+= (-?[0-9]{1,10})(?: (EPERM|EACCES) \([^\n]*\))?'
COMPLETE = re.compile(re.escape(START) + RETURN)
ATTACH = re.compile(re.escape(START) + r'/usr/bin/strace: Process ([1-9][0-9]{0,9}) attached')
RESUMED = re.compile(r'<\.\.\. clone resumed>' + RETURN)
BARE = re.compile(RETURN)
DENIED = re.compile(r'(mount|unshare|setns|pivot_root|chroot|setgroups|setresuid|setresgid)\(.*\)\s+= -1 (EPERM|EACCES) \([^\n]*\)')
CANDIDATE_SHA = '9a949992b23a81361f821d9ec6fd227eebcd4a6a1c1cf8801ee698660e117c5c'
DEFAULT_ROOT = pathlib.Path('experiments/domain-model/s2/verification/2026-11-17-policy-pair')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def trace_digest(trace):
    """Bound UTF-8 input without a second whole-trace byte buffer."""
    if len(trace) > MAX_BYTES:
        raise ValueError('trace-exceeds-16MiB')
    size, sha = 0, hashlib.sha256()
    for offset in range(0, len(trace), MAX_LINE):
        chunk = trace[offset:offset + MAX_LINE].encode()
        size += len(chunk)
        if size > MAX_BYTES:
            raise ValueError('trace-exceeds-16MiB')
        sha.update(chunk)
    return sha.hexdigest()


def source_lines(trace):
    """One forward scan; never materialize an unbounded line or line list."""
    offset = 0
    while offset < len(trace):
        newline = trace.find('\n', offset)
        end = len(trace) if newline < 0 else newline
        if end - offset > MAX_LINE:
            yield None, False
            return
        yield trace[offset:end], newline >= 0
        offset = end + 1


def parse_trace(trace, *, payload_started=False, exit_code=1, stdout=''):
    """One line pass; bounded pending state, and bounded evidence output.

    Unfinished/resumed calls are matched only by PID. Attach-split namespace
    clones additionally require the very next physical line, with no PID,
    and the exact attached child as return value. No global substitutions.
    """
    trace_sha = trace_digest(trace)
    pending, executions, children = {}, {}, {}
    clones, denied, issues, joins = [], [], [], []
    context = []
    context_bytes = 0
    context_complete = True
    adjacent = None
    previous = ''
    number = 0

    def issue(reason, line):
        if len(issues) < MAX_ISSUES:
            issues.append({'reason': reason, 'line': line})

    def evidence(line, raw):
        return {'startLine': line, 'endLine': line, 'raw': raw}

    def finish(pid, match, first, line, raw, form, attached=None):
        value = int(match[1])
        errno = match[2]
        if (value <= 0 and (value != -1 or errno is None)) or (value > 0 and errno):
            issue('unsupported-clone-return', line)
            return
        if attached is not None and value != attached:
            issue('attach-child-return-mismatch', line)
            return
        if pid not in executions:
            issue('clone-without-bwrap-exec', first['startLine'])
        if value > 0 and (value == pid or value in children or value in executions):
            issue('duplicate-or-conflicting-child', line)
        clone = {'pid': pid, 'kind': executions.get(pid, {}).get('kind', 'unknown'),
                 'flags': FLAGS, 'return': value, 'errno': errno, 'format': form,
                 'source': first, 'completion': evidence(line, raw),
                 'execLine': executions.get(pid, {}).get('source', {}).get('startLine')}
        clones.append(clone)
        if value > 0:
            children[value] = clone
        if form == 'attach-adjacent':
            joins.append({'parentPid': pid, 'childPid': value,
                          'sourceLines': [first['startLine'], line],
                          'notice': '/usr/bin/strace: Process ' + str(value) + ' attached',
                          'reason': 'exact clone flags, adjacent unprefixed return, attached child equals return'})

    for number, (raw, terminated) in enumerate(source_lines(trace), 1):
        if raw is None or len(raw.encode()) > MAX_LINE:
            issue('line-limit', number)
            break
        if len(clones) + len(denied) + len(executions) >= MAX_OBSERVATIONS:
            issue('observation-limit', number)
            break
        if len(issues) >= MAX_ISSUES:
            break
        if not terminated:
            issue('unterminated-final-line', number)
        # An attach split is never allowed to skip intervening output.
        if adjacent is not None:
            pid = adjacent
            first, form, attached = pending.pop(pid)
            adjacent = None
            match = BARE.fullmatch(raw)
            if match:
                finish(pid, match, first, number, raw, form, attached)
                previous = raw
                continue
            issue('attach-completion-not-adjacent-or-ambiguous', number)

        match = PID.fullmatch(raw)
        if not match:
            if BARE.fullmatch(raw):
                # Startup SIGCHLD forks also have this shape. Recognize their
                # immediate provenance only to exclude them, never as evidence.
                other = re.fullmatch(r'(?:\[pid\s+[0-9]+\]\s+)?clone\(child_stack=NULL, flags=SIGCHLD/usr/bin/strace: Process ([1-9][0-9]{0,9}) attached', previous)
                if not other or int(other[1]) != int(BARE.fullmatch(raw)[1]):
                    issue('orphan-unprefixed-completion', number)
            elif 'flags=' + FLAGS in raw:
                issue('namespace-clone-without-pid', number)
            previous = raw
            continue
        pid, body = int(match[1]), match[2]
        previous = raw
        failure = DENIED.fullmatch(body)
        context_reason = None
        if body.startswith(('execve(', '<... execve resumed>')):
            context_reason = 'child-exec-outside-denial-scope'
        elif not failure and body.startswith(('mount(', '<... mount resumed>')):
            context_reason = 'unsupported-child-mount'
        # Until a pending clone returns, any PID may be its child. Keep only
        # the two unsupported context kinds, with an independent finite budget.
        # The same capture/filter path handles already-known children as well.
        if context_reason and (pending or pid in children):
            size = len(raw.encode())
            if len(context) >= MAX_CONTEXT_EVENTS or context_bytes + size > MAX_CONTEXT_BYTES:
                issue('child-context-limit', number)
                context_complete = False
            else:
                context.append({'pid': pid, 'reason': context_reason,
                                'source': evidence(number, raw)})
                context_bytes += size
        if body.startswith('execve(') and '["bwrap",' in body:
            if pid in executions or pid in children:
                issue('duplicate-or-reused-bwrap-pid', number)
            # Keep the old role convention explicit. The saved second argv is
            # strace-abbreviated; command-preparation is not a payload exec.
            kind = 'precheck' if '"/usr/bin/true"' in body else 'command-preparation'
            if (not re.match(r'execve\("/proc/self/fd/[0-9]{1,10}", \["bwrap", ', body)
                    or body.rfind('], ') < 0 or not body.endswith(') = 0')):
                issue('unsupported-bwrap-exec', number)
            executions[pid] = {'pid': pid, 'kind': kind, 'source': evidence(number, raw),
                               'argvAbbreviated': '...],' in body,
                               'roleBasis': 'bwrap argv contains /usr/bin/true; otherwise command-preparation (frozen convention)'}
        if body.startswith('clone(') and (pid in executions or 'CLONE_NEWNS' in body):
            if pid in pending:
                issue('duplicate-pending-clone', number)
                pending.pop(pid)
            first = evidence(number, raw)
            complete = COMPLETE.fullmatch(body)
            attach = ATTACH.fullmatch(body)
            if complete:
                finish(pid, complete, first, number, raw, 'single-line')
            elif attach or body == START + ' <unfinished ...>':
                if len(raw.encode()) > MAX_PENDING_BYTES:
                    issue('pending-line-limit', number)
                elif len(pending) >= MAX_PENDING:
                    issue('pending-count-limit', number)
                else:
                    form = 'attach-adjacent' if attach else 'unfinished-resumed'
                    pending[pid] = (first, form, int(attach[1]) if attach else None)
                    if attach:
                        adjacent = pid
            else:
                issue('unsupported-clone-format-or-flags', number)
        elif body.startswith('clone3(') and pid in executions:
            issue('unsupported-clone3', number)
        elif body.startswith('<... clone resumed>'):
            if pid in pending:
                first, form, attached = pending.pop(pid)
                resumed = RESUMED.fullmatch(body)
                if resumed and form == 'unfinished-resumed':
                    finish(pid, resumed, first, number, raw, form)
                else:
                    issue('unsupported-clone-resume', number)
            elif pid in executions:
                issue('orphan-or-duplicate-clone-resume', number)
        else:
            if failure:
                denied.append({'pid': pid, 'syscall': failure[1], 'errno': failure[2],
                               'source': evidence(number, raw),
                               'parentPid': None, 'cloneLine': None})
            if pid in pending and not body.startswith(('--- ', '+++ ')):
                issue('same-pid-output-during-pending-clone', number)

    for first, _, _ in pending.values():
        issue('incomplete-clone', first['startLine'])
    known = (len(clones) == len(executions) == 2
             and {c['pid'] for c in clones} == set(executions)
             and {c['kind'] for c in clones} == {'precheck', 'command-preparation'})
    if not known:
        issue('expected-one-clone-per-bwrap-role', number)
    # Resolve bounded context once, before admitting any deferred denial. This
    # is a pass over at most MAX_CONTEXT_EVENTS records, never over input again.
    invalid_children, child_context, seen_context = set(), [], set()
    for event in context:
        clone = children.get(event['pid'])
        if clone and event['source']['startLine'] > clone['source']['startLine']:
            event = {**event, 'parentPid': clone['pid'], 'cloneLine': clone['source']['startLine']}
            child_context.append(event)
            invalid_children.add(event['pid'])
            issue(event['reason'], event['source']['startLine'])
            key = (event['pid'], event['source']['raw'])
            if key in seen_context:
                issue('duplicate-child-context', event['source']['startLine'])
            seen_context.add(key)
    # A child's denial may precede its parent's resumed return. Both orders
    # require the same complete, supported context after the clone start.
    for failure in denied:
        clone = children.get(failure['pid'])
        if clone and failure['source']['startLine'] > clone['source']['startLine']:
            failure['parentPid'] = clone['pid']
            failure['cloneLine'] = clone['source']['startLine']
    related = [d for d in denied if d['parentPid'] is not None]
    linked = [d for d in related if context_complete and d['pid'] not in invalid_children]
    status = 'inconclusive'
    if not issues and known:
        if all(c['return'] == -1 and c['errno'] == 'EPERM' for c in clones) and not payload_started:
            status = 'clone-still-denied'
        elif all(c['return'] > 0 for c in clones):
            if payload_started and exit_code == 0 and 'NATIVE_PAYLOAD_STARTED' in stdout and not linked:
                status = 'synthetic-payload-completed'
            elif not payload_started and {d['parentPid'] for d in linked} == set(executions):
                status = 'first-clone-passed-next-blocked'
    if status == 'inconclusive' and not issues:
        issue('insufficient-or-conflicting-outcome-evidence', number)
    return {'status': status, 'traceSha256': trace_sha,
            'payloadStarted': payload_started, 'commandExitCode': exit_code,
            'lsmCauseConfirmed': False, 'bwrapExecutions': list(executions.values()),
            'namespaceClones': clones, 'nextDenied': linked,
            'contextRejectedDenied': [d for d in related if not context_complete or d['pid'] in invalid_children],
            'unlinkedDenied': [d for d in denied if d['parentPid'] is None],
            'childContext': child_context,
            'contextComplete': context_complete,
            'contextEventsStored': len(context), 'contextBytesStored': context_bytes,
            'joins': joins, 'issues': issues, 'linesVisited': number,
            'pendingClonePids': list(pending),
            'supportedFormats': ['PID-prefixed single-line clone',
                                 'PID-matched unfinished/resumed clone',
                                 'exact /usr/bin/strace attach notice plus immediate unprefixed return'],
            'unsupportedFormats': ['clone3 or different flags/order',
                                   'nonadjacent attach completion or ambiguous/mismatched PID',
                                   'split bwrap exec or split child mount',
                                   'truncated final line or any exceeded limit'],
            'scope': 'PID-prefixed bwrap exec, exact namespace clone, subsequent child denial; unrelated startup syscalls excluded',
            'limits': {'traceBytes': MAX_BYTES, 'lineBytes': MAX_LINE,
                       'pendingLineBytes': MAX_PENDING_BYTES, 'pendingCalls': MAX_PENDING,
                       'observations': MAX_OBSERVATIONS, 'issues': MAX_ISSUES,
                       'contextEvents': MAX_CONTEXT_EVENTS, 'contextBytes': MAX_CONTEXT_BYTES}}


def reanalyze(root):
    """Validate the immutable historical bundle before reading sealed results."""
    root = pathlib.Path(root)
    index = verify_index(root)
    replay = verify(root / 'host')
    units = json.loads((root / 'host/units.json').read_text())
    if ([u['mode'] for u in units] != ['baseline', 'candidate']
            or replay['passedUnits'] != 2 or len(replay['sealsVerified']) != 2):
        raise ValueError('expected-two-sealed-policy-units')
    result = {'indexSha256': digest((root / 'index.json').read_bytes()),
              'inputRoot': str(root), 'indexVerification': index,
              'historicalStatus': replay['status'], 'runtimeReexecuted': False,
              'fixtureOnly': True, 'validSubmission': False, 'trialAuthorized': False,
              'readyForTrial': False, 'results': None, 'modes': {}}
    for unit in units:
        mode = unit['mode']
        archive = root / 'host' / ('recovery-unit-' + mode + '.tar.gz')
        member = 'runs/' + unit['runId'] + '/result/auxiliary/result.json'
        data = contents(archive)[member]
        observation = json.loads(data)
        old = trace_observation(observation)
        call = observation['calls'][-1]
        if mode == 'candidate' and trace_digest(call['stderr']) != CANDIDATE_SHA:
            raise ValueError('not-the-approved-candidate-trace')
        parsed = parse_trace(call['stderr'], payload_started=observation['nativePayloadStarted'],
                             exit_code=call['exitCode'], stdout=call['stdout'])
        result['modes'][mode] = {'archive': str(archive.relative_to(root)),
                                'archiveSha256': digest(archive.read_bytes()),
                                'member': member, 'resultSha256': digest(data),
                                'previousAutomaticStatus': old['status'], 'derived': parsed}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=pathlib.Path, default=DEFAULT_ROOT)
    parser.add_argument('--output', type=pathlib.Path, required=True)
    args = parser.parse_args()
    if args.output.resolve().is_relative_to(args.root.resolve()):
        parser.error('derived output must be outside the historical evidence directory')
    if args.output.exists():
        parser.error('output already exists; refusing overwrite')
    result = reanalyze(args.root)
    source = pathlib.Path(__file__).resolve()
    repo = pathlib.Path(subprocess.check_output(['git', '-C', str(HERE), 'rev-parse', '--show-toplevel'], text=True).strip())
    relative = str(source.relative_to(repo))
    commit = subprocess.check_output(['git', '-C', str(repo), 'log', '-1', '--format=%H', '--', relative], text=True).strip()
    if not commit or subprocess.check_output(['git', '-C', str(repo), 'show', commit + ':' + relative]) != source.read_bytes():
        raise ValueError('commit-the-offline-tool-before-publishing-derived-evidence')
    result['tool'] = {'path': relative, 'sha256': digest(source.read_bytes()),
                      'sourceCommit': commit,
                      'dependencyHashes': {str(p.relative_to(repo)): digest(p.read_bytes()) for p in [HERE / 'policy_pair.py', HERE / 'verify_pair.py', HERE / 'verify_recovery.py', HERE.parent / 'single-policy-test/scope.py']},
                      'checkoutHead': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({m: x['derived']['status'] for m, x in result['modes'].items()}))


if __name__ == '__main__':
    main()
