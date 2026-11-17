"""Probe reviewed round.main; only temporary files and mocked actions, no VM.

Run from checkout root at d970072. This demonstrates historical behavior;
it is not a regression test that should keep passing after the fix.
"""
import json
import pathlib
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path.cwd() / 'experiments/domain-model/s2/trial/container/execution-lifecycle'))
import round as runner

cases = []
for action in ['prepare', 'fixtures']:
    for failure in ['none', 'scope-write', 'registry-write', 'snapshot']:
        with tempfile.TemporaryDirectory() as td:
            work = pathlib.Path(td).resolve()
            (work / 'snapshots').mkdir()
            (work / 'plan.json').write_text(json.dumps({'vmRoot': str(work / 'unused-vm-root'), 'vmName': 'not-created'}))
            (work / 'budget.json').write_text('{}')
            calls = []
            def fail_action(self):
                calls.append(action)
                raise RuntimeError('original-' + action + '-failure')
            def cleanup(self):
                calls.append('cleanup')
            original_write = runner.write
            def write(path, value):
                target = {'scope-write': 'analysis-scope.json', 'registry-write': 'closing-registry.json'}.get(failure)
                if path.name == target:
                    raise OSError('injected-' + failure + '-failure')
                return original_write(path, value)
            def snapshot(*args, **kwargs):
                calls.append('snapshot')
                if failure == 'snapshot':
                    raise OSError('injected-snapshot-failure')
            with patch.object(runner.Round, action, fail_action), patch.object(runner.Round, 'cleanup', cleanup), patch.object(runner, 'write', side_effect=write), patch.object(runner, 'snapshot', side_effect=snapshot), patch.object(sys, 'argv', ['round.py', action, '--work', str(work)]):
                try:
                    runner.main()
                    error = None
                except Exception as exc:
                    error = str(exc)
            called = 'cleanup' in calls
            assert called == (failure == 'none'), (action, failure, calls)
            cases.append({'action': action, 'failure': failure, 'calls': calls, 'surfacedError': error, 'cleanupCalled': called})
print(json.dumps({'runtimeCommandsExecuted': 0, 'cases': cases}, indent=2))
