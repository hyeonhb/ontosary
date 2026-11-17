import datetime,fcntl,importlib.util,json,os,pathlib,subprocess,sys,tempfile,time,unittest
from unittest.mock import patch
import engine
from collector import collect,Rejected
class DeadlineTests(unittest.TestCase):
 def test_lock_wait_is_bounded(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=pathlib.Path(tmp)/'lock'
   with p.open('w') as held:
    fcntl.flock(held,fcntl.LOCK_EX)
    started=time.monotonic()
    with self.assertRaisesRegex(RuntimeError,'lock-deadline'):
     with engine.c.lock(p,time.monotonic()+.03):self.fail('acquired')
    self.assertLess(time.monotonic()-started,.3)
 def test_command_deadline_charged_before_spawn(self):
  with tempfile.TemporaryDirectory() as tmp,patch.object(engine.c.subprocess,'Popen') as spawn:
   with self.assertRaisesRegex(RuntimeError,'command-deadline'):engine.c.command(pathlib.Path(tmp),['unreachable'],deadline=time.monotonic()-1)
   spawn.assert_not_called()
 def test_descendant_output_pipe_cannot_extend_deadline(self):
  with tempfile.TemporaryDirectory() as tmp:
   started=time.monotonic();code,_,_=engine.c.command(pathlib.Path(tmp),[sys.executable,'-c','import subprocess,time;subprocess.Popen(["sleep","10"]);time.sleep(10)'],timeout=.05,deadline=time.monotonic()+.1,check=False)
   self.assertEqual(code,124);self.assertLess(time.monotonic()-started,.5)
 def test_registration_rejects_restart_of_120s(self):
  with self.assertRaisesRegex(RuntimeError,'invalid-registration-budget'):engine.register('normal-1',120,datetime.datetime.now(datetime.timezone.utc).isoformat())
 def test_retired_round_entrypoints_fail_before_runtime(self):
  base=pathlib.Path(__file__).parent.parent/'single-policy-test'
  for name in ['retry-job.py','retry-guest.py','retry-install.py','retry-remove.py','retry-export.py']:
   p=subprocess.run([sys.executable,str(base/name),'prepare'],capture_output=True,text=True,timeout=2);self.assertNotEqual(p.returncode,0);self.assertIn('retired',p.stderr)
if __name__=='__main__':unittest.main()
