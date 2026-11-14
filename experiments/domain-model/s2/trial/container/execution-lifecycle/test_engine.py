import copy,json,os,pathlib,subprocess,sys,tempfile,time,unittest
import engine as e
from collector import inventory
class EngineTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.tmp.name);self.rid='a'*12;self.run=self.root/'runs'/self.rid;self.run.mkdir(parents=True);(self.root/'units').mkdir();(self.root/'shared').mkdir()
  self.cg=self.root/'cgroup';self.cg.mkdir();(self.cg/'cgroup.events').write_text('populated 0\n');(self.cg/'cgroup.procs').write_text('');(self.cg/'cgroup.kill').write_text('')
  for n in ['source','auxiliary']:(self.run/n).mkdir()
  (self.run/'source/input').write_text('positive')
  now=time.monotonic();self.state={'runId':self.rid,'mode':'normal-1','state':'running','outcome':'exit','reason':'exit','exitCode':0,'image':{'target':'image','chain':'chain'},'slice':'ontosary-'+self.rid+'.slice','service':'ontosary-execution-'+self.rid+'.service','cgroup':str(self.cg),'cgroupInode':self.cg.stat().st_ino,'containerName':'ontosary-'+self.rid,'containerId':'b'*64,'deadlines':{'work':now+80,'remove':now+110,'finish':now+120},'createPending':False,'startPending':False,'execPending':False,'terminationConfirmed':False,'removalConfirmed':False,'collectionStatus':'not-started','cleanupDone':False,'runtimeRequests':[]}
  self.fake={'rid':self.rid,'cid':'b'*64,'present':True};self.save();e.c.write(self.root/'gate.json',{'runId':self.rid,'allowNext':False});e.c.write(self.run/'baseline.json',inventory({n:self.run/n for n in ['source','auxiliary']}))
  for n in ['slice','service']:(self.root/'units'/self.state[n]).write_text('owned unit')
 def tearDown(self):self.tmp.cleanup()
 def save(self):e.c.write(self.run/'state.json',self.state);e.c.write(self.root/'fake.json',self.fake)
 def invoke(self,action='finalize',ok=True,extra=[]):
  p=subprocess.run([sys.executable,str(pathlib.Path(__file__).with_name('fixture_entrypoint.py')),action,self.rid,*extra],capture_output=True,text=True,timeout=5,env={**os.environ,'S2_TEST_ROOT':str(self.root)})
  if ok:self.assertEqual(p.returncode,0,p.stderr)
  else:self.assertNotEqual(p.returncode,0)
  return p
 def current(self):return e.c.read(self.run/'state.json')
 def test_normal_delete_before_collect_and_seal(self):
  self.invoke();s=self.current();self.assertTrue(s['removalConfirmed']);self.assertLessEqual(s['removedAt']['mono'],s['collectionStarted']['mono']);self.assertFalse(e.c.read(self.root/'gate.json')['allowNext']);self.invoke('observe');self.assertTrue(e.c.read(self.root/'gate.json')['allowNext'])
 def test_precheck_rejection_no_result_explicit_recovery(self):
  self.state.update(outcome='precheck-rejected',reason='precheck-rejected');self.save();self.invoke();self.invoke('observe');self.assertFalse((self.run/'result').exists());self.assertFalse(e.c.read(self.root/'gate.json')['allowNext']);self.invoke('recover');self.assertTrue(e.c.read(self.root/'gate.json')['allowNext']);self.assertEqual(self.current()['outcome'],'precheck-rejected')
 def test_start_failure_cleanup(self):
  self.state.update(outcome='start-failed',reason='start-failed');self.save();self.invoke();self.assertTrue(self.current()['removalConfirmed']);self.assertEqual(self.current()['collectionStatus'],'suppressed')
 def test_timeout_diagnostic(self):
  self.state.update(outcome='timeout',reason='timeout');self.save();self.invoke();self.assertEqual(e.c.read(self.run/'result/fixture.json')['classification'],'diagnostic')
 def test_wrapper_death_diagnostic(self):
  self.state.update(outcome='wrapper-death',reason='wrapper-death');self.save();self.invoke();self.assertTrue(self.current()['removalConfirmed']);self.assertTrue(self.current()['recoveryRequired'])
 def test_supervisor_death_suppressed(self):
  self.state.update(outcome=None,reason=None);self.save();self.invoke();self.assertEqual(self.current()['outcome'],'supervisor-death');self.assertFalse((self.run/'result').exists());self.invoke('observe');self.assertFalse(e.c.read(self.root/'gate.json')['allowNext'])
 def test_pending_never_absent_by_missing_id(self):
  self.state.update(containerId=None,createPending=True);self.save();self.invoke(ok=False);self.assertFalse(self.current()['removalConfirmed']);self.assertFalse((self.run/'result').exists());self.assertTrue(self.current()['discardVM'])
 def test_query_error_not_absence(self):
  self.fake['queryFail']=True;self.save();self.invoke(ok=False);self.assertFalse(self.current()['removalConfirmed']);self.assertTrue(self.current()['discardVM'])
 def test_remove_error_not_absence(self):
  self.fake['removeFail']=True;self.save();self.invoke(ok=False);self.assertTrue(self.current()['terminationConfirmed']);self.assertFalse(self.current()['removalConfirmed']);self.assertFalse((self.run/'result').exists())
 def test_foreign_container_never_deleted(self):
  self.fake['foreign']=True;self.save();self.invoke(ok=False);self.assertTrue(e.c.read(self.root/'fake.json')['present'])
 def test_duplicate_cleanup_single_publication(self):
  self.invoke();before=(self.run/'result/fixture.json').read_bytes();self.invoke();self.assertEqual(before,(self.run/'result/fixture.json').read_bytes());calls=[json.loads(x) for x in (self.root/'fake-calls.jsonl').read_text().splitlines()];self.assertEqual(sum('rm' in x for x in calls),1)
 def test_collector_failure_blocks(self):
  (self.run/'source/evil').symlink_to('/etc/hosts');self.invoke(ok=False);self.assertTrue(self.current()['removalConfirmed']);self.assertFalse((self.run/'result').exists());self.assertFalse(e.c.read(self.root/'gate.json')['allowNext'])
 def test_expired_work_request_not_dispatched(self):
  self.state['deadlines']['work']=time.monotonic()-1;self.save();self.invoke('test-request',False,['start']);self.assertTrue(self.current()['startPending']);self.assertFalse((self.root/'fake-calls.jsonl').exists())
 def test_timeout_request_remains_pending(self):
  self.fake['requestTimeout']=True;self.save();self.invoke('test-request',False,['create']);self.assertTrue(self.current()['createPending'])
 def test_create_nonzero_keeps_unsettled_request(self):
  self.fake['requestExit']=2;self.save();self.invoke('test-request',False,['create']);self.assertTrue(self.current()['createPending']);self.assertEqual(self.current()['containerId'],'b'*64)
 def test_start_failure_settled_only_after_inspect(self):
  self.fake['requestExit']=1;self.save();self.invoke('test-request',True,['start']);self.assertFalse(self.current()['startPending'])
if __name__=='__main__':unittest.main()
