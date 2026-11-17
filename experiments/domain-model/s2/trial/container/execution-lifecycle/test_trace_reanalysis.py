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


if __name__ == '__main__':
    unittest.main()
