import json
import pathlib
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import trace_reanalysis as tool


def exec_line(pid, precheck):
    arg = '/usr/bin/true' if precheck else '/usr/local/bin/node'
    return f'[pid {pid}] execve("/proc/self/fd/3", ["bwrap", "{arg}"], 0) = 0'


def fixture(form='single-line', denial=True):
    lines = []
    for pid, child, precheck in [(41, 42, True), (43, 44, False)]:
        lines.append(exec_line(pid, precheck))
        start = f'[pid {pid}] ' + tool.START
        if form == 'attach':
            lines += [start + f'/usr/bin/strace: Process {child} attached', f') = {child}']
        elif form == 'unfinished':
            lines += [start + ' <unfinished ...>', f'[pid {pid}] <... clone resumed>) = {child}']
        else:
            lines += [start + f') = {child}']
        if denial:
            lines.append(f'[pid {child}] mount(NULL, "/", NULL, MS_REC|MS_SILENT|MS_SLAVE, NULL) = -1 EPERM (Operation not permitted)')
    return '\n'.join(lines) + '\n'


class TraceReanalysisTests(unittest.TestCase):
    def parse(self, text, **kwargs):
        return tool.parse_trace(text, **kwargs)

    def inconclusive(self, text, reason=None):
        result = self.parse(text)
        self.assertEqual(result['status'], 'inconclusive')
        self.assertTrue(result['issues'])
        if reason:
            self.assertIn(reason, [i['reason'] for i in result['issues']])
        return result

    def test_actual_candidate_source_lines_and_frozen_result(self):
        path = tool.DEFAULT_ROOT / 'host/candidate-observation.json'
        data = path.read_bytes()
        result = json.loads(data)
        trace = result['calls'][-1]['stderr']
        parsed = self.parse(trace)
        self.assertEqual(tool.digest(trace.encode()), tool.CANDIDATE_SHA)
        self.assertEqual(tool.trace_observation(result)['status'], 'inconclusive')
        self.assertEqual(parsed['status'], 'first-clone-passed-next-blocked')
        self.assertEqual([(c['pid'], c['return'], c['source']['startLine'], c['completion']['startLine']) for c in parsed['namespaceClones']], [(41, 42, 64, 65), (43, 44, 132, 132)])
        self.assertEqual([(d['pid'], d['source']['startLine']) for d in parsed['nextDenied']], [(42, 110), (44, 178)])
        self.assertEqual([e['source']['startLine'] for e in parsed['bwrapExecutions']], [55, 123])
        self.assertEqual(parsed['joins'][0]['sourceLines'], [64, 65])
        for source in ([c[k] for c in parsed['namespaceClones'] for k in ['source', 'completion']]
                       + [e['source'] for e in parsed['bwrapExecutions'] + parsed['nextDenied']]):
            self.assertEqual(source['raw'], trace.splitlines()[source['startLine'] - 1])
            self.assertEqual(source['startLine'], source['endLine'])
        self.assertFalse(parsed['payloadStarted'])
        self.assertFalse(parsed['lsmCauseConfirmed'])
        self.assertEqual(data, path.read_bytes())

    def test_actual_baseline_two_denied_clones(self):
        result = json.loads((tool.DEFAULT_ROOT / 'host/baseline-observation.json').read_text())
        parsed = self.parse(result['calls'][-1]['stderr'])
        self.assertEqual(parsed['status'], 'clone-still-denied')
        self.assertEqual([(c['return'], c['errno']) for c in parsed['namespaceClones']], [(-1, 'EPERM')] * 2)
        self.assertEqual(tool.trace_observation(result)['status'], parsed['status'])

    def test_evidence_offsets_are_derived_not_hardcoded(self):
        original = self.parse(fixture('attach'))
        shifted = self.parse('unrelated startup diagnostic\n\n' + fixture('attach'))
        self.assertEqual(shifted['status'], original['status'])
        for a, b in zip(original['namespaceClones'], shifted['namespaceClones']):
            self.assertEqual(b['source']['startLine'], a['source']['startLine'] + 2)
            self.assertEqual(b['completion']['startLine'], a['completion']['startLine'] + 2)

    def test_single_line(self):
        self.assertEqual(self.parse(fixture())['status'], 'first-clone-passed-next-blocked')

    def test_unfinished_resumed(self):
        self.assertEqual(self.parse(fixture('unfinished'))['status'], 'first-clone-passed-next-blocked')

    def test_child_denial_before_parent_resume(self):
        lines = fixture('unfinished').splitlines()
        lines[2], lines[3] = lines[3], lines[2]
        self.assertEqual(self.parse('\n'.join(lines) + '\n')['status'], 'first-clone-passed-next-blocked')

    def test_unfinished_pids_can_interleave_without_cross_linking(self):
        lines = fixture('unfinished').splitlines()
        text = '\n'.join(lines[i] for i in [0, 1, 4, 5, 2, 3, 6, 7]) + '\n'
        self.assertEqual(self.parse(text)['status'], 'first-clone-passed-next-blocked')

    def test_unfinished_completion_order_can_differ(self):
        lines = fixture('unfinished').splitlines()
        text = '\n'.join(lines[i] for i in [0, 1, 4, 5, 6, 7, 2, 3]) + '\n'
        self.assertEqual(self.parse(text)['status'], 'first-clone-passed-next-blocked')

    def test_adjacent_attach(self):
        self.assertEqual(self.parse(fixture('attach'))['status'], 'first-clone-passed-next-blocked')

    def test_synthetic_payload_completed(self):
        for form in ['single-line', 'unfinished', 'attach']:
            with self.subTest(form=form):
                self.assertEqual(self.parse(fixture(form, False), payload_started=True, exit_code=0, stdout='NATIVE_PAYLOAD_STARTED\n')['status'], 'synthetic-payload-completed')

    def test_payload_flag_without_marker_is_not_completion(self):
        self.assertEqual(self.parse(fixture(denial=False), payload_started=True, exit_code=0)['status'], 'inconclusive')

    def test_attach_return_child_mismatch(self):
        self.inconclusive(fixture('attach').replace('Process 42 attached', 'Process 99 attached'), 'attach-child-return-mismatch')

    def test_intervening_other_pid_output_refused(self):
        self.inconclusive(fixture('attach').replace('\n) = 42', '\n[pid 99] getpid() = 99\n) = 42'), 'attach-completion-not-adjacent-or-ambiguous')

    def test_other_parent_attach_cannot_steal_completion(self):
        self.inconclusive(fixture('attach').replace('\n) = 42', '\n[pid 99] ' + tool.START + '/usr/bin/strace: Process 42 attached\n) = 42'), 'attach-completion-not-adjacent-or-ambiguous')

    def test_pid_prefixed_attach_completion_is_not_guessed(self):
        self.inconclusive(fixture('attach').replace('\n) = 42', '\n[pid 41] ) = 42'), 'attach-completion-not-adjacent-or-ambiguous')

    def test_orphan_completion(self):
        self.inconclusive(fixture() + ') = 44\n', 'orphan-unprefixed-completion')

    def test_incomplete_call(self):
        self.inconclusive(exec_line(41, True) + '\n[pid 41] ' + tool.START + ' <unfinished ...>\n', 'incomplete-clone')

    def test_truncated_final_line(self):
        self.inconclusive(fixture().rstrip('\n'), 'unterminated-final-line')

    def test_additional_or_reordered_flags_not_substring_match(self):
        for replacement in [tool.FLAGS + '|CLONE_VM', tool.FLAGS.replace('CLONE_NEWNS|CLONE_NEWIPC', 'CLONE_NEWIPC|CLONE_NEWNS')]:
            with self.subTest(flags=replacement):
                self.inconclusive(fixture().replace(tool.FLAGS, replacement, 1), 'unsupported-clone-format-or-flags')

    def test_duplicate_completion(self):
        self.inconclusive(fixture('unfinished').replace('[pid 41] <... clone resumed>) = 42', '[pid 41] <... clone resumed>) = 42\n[pid 41] <... clone resumed>) = 42'), 'orphan-or-duplicate-clone-resume')

    def test_resumed_parent_mismatch(self):
        self.inconclusive(fixture('unfinished').replace('[pid 41] <... clone resumed>', '[pid 99] <... clone resumed>'), 'incomplete-clone')

    def test_duplicate_attach_notice(self):
        notice = '/usr/bin/strace: Process 42 attached'
        self.inconclusive(fixture('attach').replace(notice, notice + notice), 'unsupported-clone-format-or-flags')

    def test_duplicate_pending(self):
        start = '[pid 41] ' + tool.START + ' <unfinished ...>'
        self.inconclusive(fixture('unfinished').replace(start, start + '\n' + start), 'duplicate-pending-clone')

    def test_duplicate_child(self):
        self.inconclusive(fixture().replace(') = 44', ') = 42'), 'duplicate-or-conflicting-child')

    def test_different_pid_mount_not_attributed(self):
        result = self.inconclusive(fixture().replace('[pid 42] mount', '[pid 99] mount'))
        self.assertEqual([d['pid'] for d in result['nextDenied']], [44])
        self.assertEqual([d['pid'] for d in result['unlinkedDenied']], [99])

    def test_parent_mount_not_child_evidence(self):
        self.inconclusive(fixture().replace('[pid 42] mount', '[pid 41] mount'))

    def test_mount_before_clone_not_attributed(self):
        lines = fixture().splitlines()
        self.inconclusive('\n'.join(lines[i] for i in [2, 0, 1, 3, 4, 5]) + '\n')

    def test_unknown_notice_and_syscall_formats(self):
        for text in [fixture('attach').replace('/usr/bin/strace:', 'strace:'), fixture().replace('clone(', 'clone3(', 1), fixture().replace(') = 42', ') = ?')]:
            with self.subTest(text=text):
                self.inconclusive(text)

    def test_extra_unknown_clone3_not_ignored(self):
        self.inconclusive(fixture() + '[pid 41] clone3({}, 88) = 100\n', 'unsupported-clone3')

    def test_limits_trace_line_pending_and_observations(self):
        with self.assertRaisesRegex(ValueError, '16MiB'):
            self.parse('x' * (tool.MAX_BYTES + 1))
        self.inconclusive('x' * (tool.MAX_LINE + 1) + '\n', 'line-limit')
        with patch.object(tool, 'MAX_PENDING_BYTES', 4):
            self.inconclusive(fixture('unfinished'), 'pending-line-limit')
        with patch.object(tool, 'MAX_PENDING', 1):
            lines = fixture('unfinished').splitlines()
            self.inconclusive('\n'.join(lines[i] for i in [0, 1, 4, 5, 2, 3, 6, 7]) + '\n', 'pending-count-limit')
        with patch.object(tool, 'MAX_OBSERVATIONS', 2):
            self.inconclusive(fixture(), 'observation-limit')

    def test_utf8_byte_limit_and_incremental_hash(self):
        self.assertEqual(tool.trace_digest('한글\n'), tool.digest('한글\n'.encode()))
        with patch.object(tool, 'MAX_BYTES', 10):
            with self.assertRaisesRegex(ValueError, '16MiB'):
                self.parse('한' * 4)

    def test_saved_archive_reanalysis_and_input_immutability(self):
        before = {str(p): tool.digest(p.read_bytes()) for p in tool.DEFAULT_ROOT.rglob('*') if p.is_file()}
        result = tool.reanalyze(tool.DEFAULT_ROOT)
        self.assertEqual(result['historicalStatus'], 'inconclusive')
        self.assertEqual(result['modes']['candidate']['derived']['status'], 'first-clone-passed-next-blocked')
        self.assertEqual(before, {str(p): tool.digest(p.read_bytes()) for p in tool.DEFAULT_ROOT.rglob('*') if p.is_file()})
        self.assertFalse(result['runtimeReexecuted'])

    def test_cli_refuses_historical_output_and_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            existing = pathlib.Path(tmp) / 'existing.json'
            existing.write_text('keep')
            for output in [tool.DEFAULT_ROOT / 'new-derived.json', existing]:
                with self.subTest(output=output), patch.object(sys, 'argv', ['trace_reanalysis.py', '--output', str(output)]):
                    with self.assertRaises(SystemExit):
                        tool.main()
            self.assertEqual(existing.read_text(), 'keep')

    def test_changed_archive_is_rejected_before_derivation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / 'evidence'
            shutil.copytree(tool.DEFAULT_ROOT, root)
            archive = root / 'host/recovery-unit-candidate.tar.gz'
            archive.write_bytes(archive.read_bytes() + b'changed')
            with self.assertRaises(AssertionError):
                tool.reanalyze(root)

    def test_candidate_trace_hash_is_required(self):
        with patch.object(tool, 'CANDIDATE_SHA', '0' * 64):
            with self.assertRaisesRegex(ValueError, 'approved-candidate-trace'):
                tool.reanalyze(tool.DEFAULT_ROOT)


class DeferredContextTests(unittest.TestCase):
    def ordered(self, events, before):
        lines = fixture('unfinished').splitlines()
        return '\n'.join(lines[:2] + (events + lines[3:4] + lines[2:3] if before else lines[2:3] + events + lines[3:4]) + lines[4:]) + '\n'

    def assert_context_rejected(self, event, reason):
        for before in [True, False]:
            with self.subTest(before=before):
                trace = self.ordered([event], before)
                result = tool.parse_trace(trace)
                self.assertEqual(result['status'], 'inconclusive')
                issue = next(i for i in result['issues'] if i['reason'] == reason)
                self.assertEqual(trace.splitlines()[issue['line'] - 1], event)

    def test_exec_order_has_same_conservative_result(self):
        self.assert_context_rejected('[pid 42] execve("/usr/bin/other", ["other"], 0) = 0', 'child-exec-outside-denial-scope')

    def test_split_mount_order_has_same_conservative_result(self):
        self.assert_context_rejected('[pid 42] mount(NULL, "/", NULL, MS_SLAVE, NULL <unfinished ...>', 'unsupported-child-mount')

    def test_resumed_mount_order_has_same_conservative_result(self):
        self.assert_context_rejected('[pid 42] <... mount resumed>) = -1 EPERM (Operation not permitted)', 'unsupported-child-mount')

    def test_successful_unsupported_mount_order_is_conservative(self):
        self.assert_context_rejected('[pid 42] mount(NULL, "/", NULL, MS_SLAVE, NULL) = 0', 'unsupported-child-mount')

    def test_unrelated_pid_context_is_not_attributed(self):
        for before in [True, False]:
            result = tool.parse_trace(self.ordered(['[pid 99] execve("/other", ["other"], 0) = 0', '[pid 99] mount(NULL, "/", NULL, 0, NULL <unfinished ...>'], before))
            self.assertEqual(result['status'], 'first-clone-passed-next-blocked')

    def test_pre_clone_context_is_not_attributed(self):
        text = '[pid 42] execve("/other", ["other"], 0) = 0\n' + fixture('unfinished')
        self.assertEqual(tool.parse_trace(text)['status'], 'first-clone-passed-next-blocked')

    def test_pending_other_parent_does_not_extend_child_lifetime_backwards(self):
        lines = fixture('unfinished').splitlines()
        text = '\n'.join(lines[:2] + ['[pid 44] execve("/other", ["other"], 0) = 0'] + lines[4:6] + lines[2:4] + lines[6:]) + '\n'
        self.assertEqual(tool.parse_trace(text)['status'], 'first-clone-passed-next-blocked')

    def test_reversed_parent_returns_keep_context_with_correct_child(self):
        lines = fixture('unfinished').splitlines()
        event = '[pid 42] execve("/other", ["other"], 0) = 0'
        text = '\n'.join(lines[:2] + lines[4:6] + [event] + lines[6:] + lines[2:4]) + '\n'
        result = tool.parse_trace(text)
        self.assertEqual(result['status'], 'inconclusive')
        self.assertEqual([d['pid'] for d in result['nextDenied']], [44])

    def test_context_is_retained_after_another_parent_finishes(self):
        lines = fixture('unfinished').splitlines()
        text = '\n'.join(lines[:2] + ['[pid 42] execve("/other", ["other"], 0) = 0'] + lines[4:] + lines[2:4]) + '\n'
        self.assertEqual(tool.parse_trace(text)['status'], 'inconclusive')

    def test_rejected_context_denial_is_retained_but_not_admitted(self):
        text = self.ordered(['[pid 42] execve("/other", ["other"], 0) = 0'], True)
        result = tool.parse_trace(text)
        self.assertEqual([d['pid'] for d in result['nextDenied']], [44])
        self.assertEqual([d['pid'] for d in result['contextRejectedDenied']], [42])
        self.assertEqual(result['childContext'][0]['parentPid'], 41)

    def test_duplicate_context_is_explicit_and_bounded(self):
        event = '[pid 42] execve("/other", ["other"], 0) = 0'
        result = tool.parse_trace(self.ordered([event, event], True))
        self.assertEqual(result['status'], 'inconclusive')
        self.assertIn('duplicate-child-context', [i['reason'] for i in result['issues']])

    def test_context_event_limit_cannot_hide_missing_child_event(self):
        events = ['[pid 99] execve("/other", ["other"], 0) = 0', '[pid 42] execve("/other", ["other"], 0) = 0']
        with patch.object(tool, 'MAX_CONTEXT_EVENTS', 1):
            result = tool.parse_trace(self.ordered(events, True))
        self.assertEqual(result['status'], 'inconclusive')
        self.assertFalse(result['contextComplete'])
        self.assertEqual(result['contextEventsStored'], 1)
        self.assertEqual(result['nextDenied'], [])
        self.assertIn('child-context-limit', [i['reason'] for i in result['issues']])

    def test_context_byte_limit_is_fail_closed_in_both_orders(self):
        for before in [True, False]:
            with self.subTest(before=before), patch.object(tool, 'MAX_CONTEXT_BYTES', 1):
                result = tool.parse_trace(self.ordered(['[pid 42] execve("/other", ["other"], 0) = 0'], before))
                self.assertEqual(result['status'], 'inconclusive')
                self.assertEqual(result['contextBytesStored'], 0)
                self.assertFalse(result['contextComplete'])

    def test_exact_context_capacity_is_not_reported_as_missing(self):
        event = '[pid 99] execve("/other", ["other"], 0) = 0'
        with patch.object(tool, 'MAX_CONTEXT_BYTES', len(event.encode())), patch.object(tool, 'MAX_CONTEXT_EVENTS', 1):
            result = tool.parse_trace(self.ordered([event], True))
        self.assertEqual(result['status'], 'first-clone-passed-next-blocked')
        self.assertTrue(result['contextComplete'])
        self.assertEqual(result['childContext'], [])


if __name__ == '__main__':
    unittest.main()
