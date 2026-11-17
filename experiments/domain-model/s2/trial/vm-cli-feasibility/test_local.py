"""Local draft regressions only; no VM, CLI binary, network or provider calls."""
import datetime
import hashlib
import io
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tarfile
import tempfile
import time
import unittest
from unittest.mock import patch

HERE = pathlib.Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / 'container/lifecycle')]
import host
spec = importlib.util.spec_from_file_location('vm_guest_draft', HERE / 'guest.py')
guest = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guest)
import materialize
from checks import check
from collector import Rejected
from deadline import run


class LocalDraftTests(unittest.TestCase):
    def test_failure_still_dispatches_cleanup(self):
        calls = []
        def fail():
            calls.append('work')
            raise RuntimeError('audit-or-recovery-failed')
        _, errors = host.finish_despite_failure(fail, lambda: calls.append('cleanup'))
        self.assertEqual(calls, ['work', 'cleanup'])
        self.assertEqual(errors, [{'phase': 'work', 'error': 'audit-or-recovery-failed'}])

    def test_both_errors_are_preserved(self):
        def fail():
            raise RuntimeError('failure')
        _, errors = host.finish_despite_failure(fail, fail)
        self.assertEqual([e['phase'] for e in errors], ['work', 'cleanup'])

    def test_missing_evidence_never_passes(self):
        result = check({}, {}, 'normal-1')
        self.assertFalse(result['passed'])
        self.assertIn('native-sandbox-payload-not-started', result['reasons'])
        self.assertIn('positive:sourceRead', result['reasons'])
        self.assertIn('parent:fdOpen', result['reasons'])
        self.assertIn('network-positive:ipv4', result['reasons'])

    def test_collection_rejects_unconfirmed_termination(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp).resolve()
            for state in [{}, {'terminationConfirmed': False},
                          {'terminationConfirmed': True, 'pendingCommand': True}]:
                with self.subTest(state=state), self.assertRaisesRegex(RuntimeError, 'without-termination'):
                    guest.collect(root, state)
                self.assertFalse((root / 'collected').exists())

    def test_collection_rejects_symlink_and_hardlink(self):
        for link in ['symbolic', 'hard']:
            with self.subTest(link=link), tempfile.TemporaryDirectory() as tmp:
                root = pathlib.Path(tmp).resolve()
                (root / 'source').mkdir()
                (root / 'target').write_text('synthetic')
                if link == 'symbolic':
                    (root / 'source/input.txt').symlink_to(root / 'target')
                else:
                    os.link(root / 'target', root / 'source/input.txt')
                with self.assertRaises(Rejected):
                    guest.collect(root, {'terminationConfirmed': True, 'finishMono': time.monotonic() + 1})

    def test_expired_deadline_never_dispatches_fake_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            budget = {'deadlines': {'test': {
                'utc': (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=1)).isoformat(),
                'monotonic': time.monotonic() - 1}}}
            with patch('deadline.subprocess.Popen') as popen:
                result = run(['fake-command'], budget, 'test', root / 'ledger.jsonl')
                popen.assert_not_called()
            self.assertEqual(result['exitCode'], 124)
            self.assertFalse(result['terminationRequested'])

    def test_local_process_is_killed_at_deadline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            budget = {'deadlines': {'test': {
                'utc': (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=.2)).isoformat(),
                'monotonic': time.monotonic() + .2}}}
            result = run([sys.executable, '-c', 'import time;time.sleep(10)'], budget, 'test', root / 'ledger.jsonl')
            self.assertEqual(result['exitCode'], 124)
            self.assertTrue(result['terminationRequested'])
            with self.assertRaises(ProcessLookupError):
                os.kill(result['pid'], 0)

    def test_draft_runtime_entrypoints_refuse_without_side_effects(self):
        for name in ['host.py', 'guest.py', 'worker.py']:
            with self.subTest(name=name):
                p = subprocess.run([sys.executable, str(HERE / name)], capture_output=True, text=True, timeout=3)
                self.assertNotEqual(p.returncode, 0)
                self.assertIn('runtime draft disabled', p.stderr)
        with self.assertRaisesRegex(host.Blocked, 'draft disabled'):
            host.execute('/nonexistent')

    def test_guest_properties_fail_closed(self):
        self.assertFalse(guest.security({}))
        fields = dict(User='s2fixture', Group='s2fixture', NoNewPrivileges='yes', CapabilityBoundingSet='',
                      AmbientCapabilities='', PrivateNetwork='yes', MemoryMax=str(4 * 1024**3), TasksMax='256',
                      CPUQuotaPerSecUSec='2s', ProtectControlGroups='yes', Delegate='no', KillMode='control-group')
        self.assertTrue(guest.security(fields))
        for key in fields:
            with self.subTest(key=key):
                bad = dict(fields)
                del bad[key]
                self.assertFalse(guest.security(bad))


class ExtractionTests(unittest.TestCase):
    """Synthetic OCI archives exercise the real blob verifier and selective extractor."""
    def fixture(self, root, members):
        raw = io.BytesIO()
        with tarfile.open(fileobj=raw, mode='w') as archive:
            for name, kind, data in members:
                member = tarfile.TarInfo(name)
                member.mode = 0o644
                member.type = kind
                if kind == tarfile.REGTYPE:
                    member.size = len(data)
                    archive.addfile(member, io.BytesIO(data))
                else:
                    member.linkname = data.decode()
                    archive.addfile(member)
        import gzip
        layer = gzip.compress(raw.getvalue())
        digest = lambda value: 'sha256:' + hashlib.sha256(value).hexdigest()
        diff = digest(raw.getvalue())
        config = json.dumps({'os': 'linux', 'architecture': 'arm64', 'rootfs': {'diff_ids': [diff]}}).encode()
        manifest = json.dumps({'config': {'digest': digest(config)}, 'layers': [{
            'digest': digest(layer), 'mediaType': 'application/vnd.oci.image.layer.v1.tar+gzip'}]}).encode()
        path = root / 'archive.tar'
        with tarfile.open(path, 'w') as archive:
            for data in [layer, config, manifest]:
                member = tarfile.TarInfo('blobs/' + digest(data).replace(':', '/'))
                member.size = len(data)
                archive.addfile(member, io.BytesIO(data))
        return {'path': str(path), 'actual': {'sha256': digest(path.read_bytes())[7:], 'bytes': path.stat().st_size},
                'request': {'image': {'target': digest(manifest), 'config': digest(config), 'chain': diff}}}

    def exercise(self, members, expected_error=None, cap=512):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            record = self.fixture(root, members)
            with patch.object(materialize, 'SELECTED', {'public/tool'}), patch.object(materialize, 'EXPECTED', {}), patch.object(materialize, 'MAX_BYTES', cap):
                if expected_error:
                    with self.assertRaisesRegex(ValueError, expected_error):
                        materialize.extract(record, root / 'output', time.monotonic() + 2)
                else:
                    result = materialize.extract(record, root / 'output', time.monotonic() + 2)
                    self.assertEqual((root / 'output/public/tool').read_bytes(), b'tool')
                    self.assertEqual(result['linksExtracted'], 0)
                    self.assertFalse(result['rootfsInstalled'])

    def test_selective_regular_file(self):
        self.exercise([('public/tool', tarfile.REGTYPE, b'tool'), ('unselected', tarfile.REGTYPE, b'ignored')])

    def test_traversal(self):
        self.exercise([('../outside', tarfile.REGTYPE, b'x')], 'unsafe-archive-path')

    def test_ancestor_links(self):
        for kind in [tarfile.SYMTYPE, tarfile.LNKTYPE]:
            with self.subTest(kind=kind):
                self.exercise([('public', kind, b'outside')], 'ancestor-link')

    def test_whiteout(self):
        self.exercise([('public/.wh.tool', tarfile.REGTYPE, b'')], 'selected-whiteout')

    def test_duplicate_selected_member(self):
        self.exercise([('public/tool', tarfile.REGTYPE, b'tool')] * 2, 'selected-file-replaced')

    def test_cumulative_byte_limit(self):
        self.exercise([('public/tool', tarfile.REGTYPE, b'tool')], 'selected-byte-limit', cap=3)

    def test_missing_selected_member(self):
        self.exercise([('unselected', tarfile.REGTYPE, b'tool')], 'missing-selected-public-file')


if __name__ == '__main__':
    unittest.main()
