"""The approved Sol batch can resume an unconfirmed seal, but not a mismatched one."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from holdout import collect, read, sol_record


class RoutingPolicy(unittest.TestCase):
    def test_resume_and_stop_before_the_next_model_call(self):
        model = 'gpt-6.2-sol'
        plan = read(sol_record/'contract.json')
        for reported, stop in (([],False), ([model],False), ([model,'other'],True)):
            with self.subTest(reported=reported), TemporaryDirectory() as directory:
                work = Path(directory)
                for task in ('quantity','refresh'):
                    inspected = work/task/'inspection'
                    inspected.mkdir(parents=True)
                    (inspected/'preflight.json').write_bytes((sol_record/'preflight'/(task+'.json')).read_bytes())
                    (inspected/'inputs.json').write_text('{}')
                first, second, *_ = plan['order']
                def seal(attempt, names):
                    run = attempt['id']
                    path = work/'attempts'/run/run
                    path.mkdir(parents=True)
                    (path/'seal.json').write_text(json.dumps({'requestedModel':model,'serverReportedModels':names}))
                seal(first,reported)
                # If resumed, the next dispatched call returns an explicit mismatch.
                with patch('holdout.command', side_effect=lambda *args: seal(second,['other'])) as dispatch, \
                     patch('holdout.subprocess.check_output', return_value=plan['cliVersion']), \
                     self.assertRaisesRegex(ValueError,'mismatch'):
                    collect(work,plan)
                self.assertEqual(dispatch.call_count,0 if stop else 1)


if __name__ == '__main__':
    unittest.main()
