from pathlib import Path
import tempfile
import unittest

from observation import TARGET, confirming_pid, eligible
from prepare_directory import prepare


class ObservationTests(unittest.TestCase):
    trace = ('91 execve("/proc/self/exe", ["codex-linux-sandbox", "--"], 0xaa) = 0\n'
             f'91 mkdirat(AT_FDCWD, "{TARGET}", 0700) = -1 EROFS (Read-only file system)\n'
             'error building bubblewrap command: Read-only file system (os error 30)')

    def test_pid_order_path_and_errno(self):
        self.assertEqual(confirming_pid(self.trace), 91)
        for text in [self.trace.replace('91 mkdir', '92 mkdir'), self.trace.replace('EROFS', 'EPERM'),
                     self.trace.replace(TARGET, TARGET + '1'), '\n'.join(reversed(self.trace.splitlines()))]:
            self.assertIsNone(confirming_pid(text))

    def test_incomplete_or_unexpected_state_blocks_preparation(self):
        n = dict(exitCode=1, truncated=False, timedOut=False, stderr=self.trace, stdout='',
                 before=dict(tmp='/tmp', uid=22002, readOnly=True, target=None))
        worker = dict(native=n, configUnchanged=True, outputContent=None)
        outer = dict(truncated=False, timedOut=False, exitCode=0)
        self.assertTrue(eligible(outer, worker))
        for key in ['timedOut', 'truncated']:
            self.assertFalse(eligible(outer, dict(worker, native={**n, key: True})))
        n['before']['target'] = {'uid': 0}
        self.assertFalse(eligible(outer, worker))

    def test_existing_entry_is_never_modified(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            entry = root / Path(TARGET).name
            entry.symlink_to(root / 'missing')
            with self.assertRaises(FileExistsError):
                prepare(str(root))
            self.assertTrue(entry.is_symlink())
