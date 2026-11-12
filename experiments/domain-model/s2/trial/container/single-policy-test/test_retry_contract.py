"""Actual package entry-point rejection and single-clock nested deadline regressions."""
import copy,datetime,importlib.util,json,pathlib,shutil,subprocess,sys,tempfile,time,unittest
from unittest.mock import patch
import command
from scope import rows,verify,classify,verify_index
from deadline import limit,run,DeadlineExpired
BASE=pathlib.Path(__file__).parent;OLD=pathlib.Path('experiments/domain-model/s2/verification/2026-11-12-single-policy-test');EARLIER=OLD.parent/'2026-11-11-namespace-diagnosis'
class PackageTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.w=pathlib.Path(self.tmp.name)/'work';self.w.mkdir();self.s=self.w/'snapshots';self.s.mkdir();self.out=pathlib.Path(self.tmp.name)/'out'
  scope=json.loads((OLD/'snapshot-scope.json').read_text());self.analysis=scope['analysis'];self.row=scope['closing'][0];self.command=['python3','fixed-close.py','--round','retry'];self.phase='finish'
  for row in self.analysis+[self.row]:
   for ext in ['.json','.tar.gz']:shutil.copyfile(OLD/'snapshots'/(row['id']+ext),self.s/(row['id']+ext))
  meta=json.loads((self.s/(self.row['id']+'.json')).read_text());meta.update(category='closing',phase=self.phase,command=self.command);(self.s/(self.row['id']+'.json')).write_text(json.dumps(meta))
  self.closing=[{**rows(self.s,[self.row['id']])[0],'phase':self.phase,'command':self.command}]
  self.plan={'output':str(self.out),'source':str(BASE),'closingAllowed':[{'phase':self.phase,'command':self.command}]}
  self.save()
 def registration_matches(self):
  row=self.closing[0];p=self.s/(row['id']+'.json');meta=json.loads(p.read_text());meta.update(command=row['command'],phase=row['phase']);p.write_text(json.dumps(meta));row.update(rows(self.s,[row['id']])[0])
 def tearDown(self):self.tmp.cleanup()
 def save(self):
  for n,v in [('analysis-scope.json',self.analysis),('closing-registry.json',self.closing),('plan.json',self.plan)]: (self.w/n).write_text(json.dumps(v))
 def invoke(self,success=False):
  p=subprocess.run([sys.executable,str(BASE/'package.py'),'--work',str(self.w),'--out',str(self.out)],capture_output=True,text=True,timeout=5)
  if success:self.assertEqual(p.returncode,0,p.stderr);return
  self.assertNotEqual(p.returncode,0);self.assertFalse(self.out.exists());self.assertFalse(list(self.out.parent.glob('.policy-package-*')));return p
 def test_registered_stable(self):
  before=verify(self.s,self.analysis);self.invoke(True);self.assertEqual(before,verify(self.out/'snapshots',self.analysis));verify_index(self.out)
 def test_unregistered_package(self):
  self.closing=[];self.save();self.invoke()
 def test_runtime_registration_package(self):
  self.closing[0]['command']=['python3','runtime.py'];self.registration_matches();self.save();self.assertIn('closing-command-not-allowed',self.invoke().stderr)
 def test_same_executable_wrong_args(self):
  self.closing[0]['command']=self.command+['--execute'];self.registration_matches();self.save();self.assertIn('closing-command-not-allowed',self.invoke().stderr)
 def test_wrong_phase(self):
  self.closing[0]['phase']='environment';self.registration_matches();self.save();self.assertIn('closing-command-not-allowed',self.invoke().stderr)
 def test_duplicate(self):
  self.closing*=2;self.save();self.invoke()
 def test_overlap(self):
  self.analysis.append(self.closing[0]);self.save();self.invoke()
 def test_missing(self):
  (self.s/(self.row['id']+'.tar.gz')).unlink();self.invoke()
 def test_tamper(self):
  (self.s/(self.row['id']+'.json')).write_text('{}');self.invoke()
 def test_index_closing_tamper(self):
  self.invoke(True);(self.out/'snapshots'/(self.row['id']+'.json')).write_text('{}')
  with self.assertRaises(AssertionError):verify_index(self.out)
 def test_index_closing_missing(self):
  self.invoke(True);(self.out/'snapshots'/(self.row['id']+'.json')).unlink()
  with self.assertRaises(AssertionError):verify_index(self.out)
 def test_output_not_overwritten(self):
  self.invoke(True);before=(self.out/'index.json').read_bytes();p=subprocess.run([sys.executable,str(BASE/'package.py'),'--work',str(self.w),'--out',str(self.out)],capture_output=True);self.assertNotEqual(p.returncode,0);self.assertEqual(before,(self.out/'index.json').read_bytes())
 def test_real_prior_scopes(self):
  a=json.loads((OLD/'host/prior-snapshot-scope.json').read_text());classify(EARLIER/'snapshots',a['analysis'],a['closing']);self.assertEqual(verify(EARLIER/'snapshots',a['analysis'])['snapshotsVerified'],11)
  b=json.loads((OLD/'snapshot-scope.json').read_text());classify(OLD/'snapshots',b['analysis'],b['closing']);self.assertEqual((len(b['analysis']),len(b['closing'])),(6,6))
class DeadlineTests(unittest.TestCase):
 def setUp(self):
  self.utc=datetime.datetime(2026,11,12,tzinfo=datetime.timezone.utc);self.b={'deadlines':{'environment':{'monotonic':1200,'utc':(self.utc+datetime.timedelta(seconds=1200)).isoformat()}}}
 def test_no_450_limit(self):self.assertEqual(limit(self.b,'environment',mono=100,utc=self.utc+datetime.timedelta(seconds=100)),1100)
 def test_prior_snapshot_and_download_consumed(self):
  self.assertEqual(limit(self.b,'environment',mono=320,utc=self.utc+datetime.timedelta(seconds=320)),880);self.assertEqual(limit(self.b,'environment',mono=600,utc=self.utc+datetime.timedelta(seconds=600)),600)
 def test_earlier_clock(self):
  self.assertEqual(limit(self.b,'environment',mono=200,utc=self.utc+datetime.timedelta(seconds=800)),400);self.assertEqual(limit(self.b,'environment',mono=800,utc=self.utc+datetime.timedelta(seconds=200)),400)
 def test_expired_no_dispatch(self):
  for n in [1200,1201]:
   with self.assertRaises(DeadlineExpired):limit(self.b,'environment',mono=n,utc=self.utc)
 def test_timeout_and_failure_ledger(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=pathlib.Path(tmp)/'ledger';b={'deadlines':{'environment':{'monotonic':time.monotonic()+5,'utc':(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=5)).isoformat()}}}
   a=run([sys.executable,'-c','import time; time.sleep(1)'],b,'environment',p,requested=.03);self.assertEqual(a['exitCode'],124);self.assertTrue(a['terminationRequested'] and a['cleanupRequired'])
   a=run([sys.executable,'-c','raise SystemExit(7)'],b,'environment',p);self.assertEqual(a['exitCode'],7);self.assertTrue(a['cleanupRequired']);self.assertEqual(len(p.read_text().splitlines()),2)
 def test_wrapper_snapshot_consumes_remaining(self):
  with tempfile.TemporaryDirectory() as tmp:
   w=pathlib.Path(tmp);b={'events':[],'deadlines':{'environment':{'monotonic':time.monotonic()+.03,'utc':(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=.03)).isoformat()}}};(w/'budget.json').write_text(json.dumps(b))
   def snapshot_delay(*args):time.sleep(.05);return 'fake-snapshot'
   with patch.object(command,'snapshot',snapshot_delay):r=command.execute(w/'budget.json',w/'log','environment',['nonexistent-must-not-start'],1)
   self.assertEqual(r['exitCode'],124);self.assertNotIn('pid',r);self.assertEqual(json.loads((w/'budget.json').read_text())['events'][0]['snapshot'],'fake-snapshot')
 def test_expired_logs_without_spawn(self):
  with tempfile.TemporaryDirectory() as tmp:
   a=run(['nonexistent-must-not-dispatch'],self.b,'environment',pathlib.Path(tmp)/'ledger');self.assertEqual(a['exitCode'],124);self.assertFalse(a['terminationRequested']);self.assertNotIn('pid',a)
if __name__=='__main__':unittest.main(verbosity=2)

class SnapshotRegistrationTests(unittest.TestCase):
 setUp=PackageTests.setUp
 tearDown=PackageTests.tearDown
 save=PackageTests.save
 invoke=PackageTests.invoke
 # Use real historical fixture content with new execution registration metadata.
 def test_registration_at_creation(self):
  before=verify(self.s,self.analysis);identity=command.snapshot(self.w,self.command,self.phase,'closing');registered=json.loads((self.w/'closing-registry.json').read_text());self.assertEqual(registered[-1]['id'],identity);self.invoke(True);self.assertEqual(before,verify(self.out/'snapshots',self.analysis))
 def test_forbidden_registration_creates_nothing(self):
  before=set(p.name for p in self.s.iterdir())
  with self.assertRaises(AssertionError):command.snapshot(self.w,['python3','runtime.py'],'finish','closing')
  self.assertEqual(before,set(p.name for p in self.s.iterdir()))
 def test_analysis_after_freeze_creates_nothing(self):
  before=set(p.name for p in self.s.iterdir())
  with self.assertRaises(ValueError):command.snapshot(self.w,['python3','runtime.py'],'diagnosis','analysis')
  self.assertEqual(before,set(p.name for p in self.s.iterdir()))
