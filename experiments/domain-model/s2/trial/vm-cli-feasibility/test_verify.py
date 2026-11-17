"""Adversarial edits to the stored zero-runtime record must not become success."""
import copy
import json
import pathlib
import shutil
import tempfile
import unittest

import verify

EVIDENCE = verify.ROOT / 'experiments/domain-model/s2/verification/2026-11-17-vm-cli-feasibility'


class StoppedRecordTests(unittest.TestCase):
    def setUp(self):
        self.records = [json.loads((EVIDENCE / name).read_text()) for name in
                        ['result.json', 'stop.json', 'first-command.json', 'closure.json']]

    def test_stored_record_is_inconclusive_only(self):
        result = verify.verify(EVIDENCE)
        self.assertEqual(result['status'], 'inconclusive')
        self.assertFalse(result['runtimeVerified'])
        self.assertEqual((result['observedUnits'], result['requiredUnits']), (0, 4))

    def test_missing_or_spurious_runtime_observations(self):
        mutations = [('status', 'feasible-for-next-integration'), ('runtimeVerified', True),
                     ('observedUnits', 4), ('actualUnits', [{'passed': True}]),
                     ('executionCodeHashes', {'fake': 'fake'}), ('requiredUnits', []),
                     ('results', {}), ('cleanupStatus', 'complete')]
        for key, value in mutations:
            with self.subTest(key=key):
                rows = copy.deepcopy(self.records)
                rows[0][key] = value
                with self.assertRaises(ValueError):
                    verify.validate_record(*rows)

    def test_missing_field_fails(self):
        rows = copy.deepcopy(self.records)
        del rows[0]['counts']['sandboxCalls']
        with self.assertRaises(KeyError):
            verify.validate_record(*rows)

    def test_counter_cannot_be_boolean_or_nonzero(self):
        for value in [False, 1]:
            with self.subTest(value=value):
                rows = copy.deepcopy(self.records)
                rows[0]['counts']['modelCalls'] = value
                with self.assertRaises(ValueError):
                    verify.validate_record(*rows)

    def test_gate_cannot_be_restarted(self):
        rows = copy.deepcopy(self.records)
        rows[1]['gateMonotonic'] += 900
        with self.assertRaisesRegex(ValueError, 'gate reset'):
            verify.validate_record(*rows)

    def test_remaining_process_prevents_closed_record(self):
        rows = copy.deepcopy(self.records)
        rows[3]['ownedProcesses'] = [123]
        with self.assertRaises(ValueError):
            verify.validate_record(*rows)

    def test_tampered_raw_evidence_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp).resolve() / 'evidence'
            shutil.copytree(EVIDENCE, path)
            (path / 'result.json').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'evidence hash/size'):
                verify.verify(path)

    def test_unindexed_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp).resolve() / 'evidence'
            shutil.copytree(EVIDENCE, path)
            (path / 'unexpected.json').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'unindexed evidence'):
                verify.verify(path)

    def test_symlink_cannot_replace_indexed_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp).resolve() / 'evidence'
            shutil.copytree(EVIDENCE, path)
            (path / 'result.json').unlink()
            (path / 'result.json').symlink_to(EVIDENCE / 'result.json')
            with self.assertRaises(Exception):
                verify.verify(path)


if __name__ == '__main__':
    unittest.main()
