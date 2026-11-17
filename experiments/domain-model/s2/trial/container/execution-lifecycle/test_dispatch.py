"""Exercise the actual CLI dispatcher without VM or subprocess dispatch."""
import contextlib,datetime,io,json,pathlib,shutil,sys,tempfile,time,unittest
from unittest.mock import patch
import round as runner
import recovery

class DispatchTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.w=pathlib.Path(self.tmp.name).resolve();self.calls=[];self.original=RuntimeError('original-action-failure');self.stderr=io.StringIO()
  command=lambda a:['python3',str(runner.HERE/'round.py'),a,'--work',str(self.w)]
  self.plan={'vmRoot':str(self.w/'ontosary-s2-dispatch'),'vmName':'fake','store':str(self.w/'store'),'round':'dispatch-test','source':str(runner.HERE),'output':str(self.w/'published'),'analysisAllowed':[{'phase':'environment' if a=='prepare' else 'exploration','command':command(a)} for a in ['prepare','fixtures']],'closingAllowed':[{'phase':'finish','command':command(a)} for a in ['cleanup','seal']]}
  runner.write(self.w/'plan.json',self.plan);runner.write(self.w/'budget.json',{'deadlines':{'finish':{'utc':(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(minutes=5)).isoformat(),'monotonic':time.monotonic()+300}}})
  # Real analysis archive and hashes, not a mocked scope registry.
  runner.snapshot(self.w,command('prepare'),'environment')
 def tearDown(self):self.tmp.cleanup()
 def action(self,r):self.calls.append(r.action);raise self.original
 def cleanup(self,r):self.calls.append('cleanup');return {'cleanupStatus':'complete'}
 def invoke(self,action='prepare',failure=None,cleanup_failure=False,record_failure=False,stderr_failure=False,actual_cleanup=False,normal=False):
  real_write=runner.write;real_snapshot=runner.snapshot
  def write(path,value):
   if path.name=={'scope':'analysis-scope.json','registry':'closing-registry.json'}.get(failure) or record_failure and path.name=='dispatch-failure.json':raise OSError('injected-write-'+path.name)
   return real_write(path,value)
  def snap(*args,**kwargs):
   if failure=='snapshot':raise OSError('injected-snapshot')
   if failure=='registration':
    original=pathlib.Path.write_text
    def fail_registry(path,*a,**kw):
     if path.name=='closing-registry.tmp':raise OSError('injected-registration')
     return original(path,*a,**kw)
    with patch.object(pathlib.Path,'write_text',fail_registry):return real_snapshot(*args,**kwargs)
   return real_snapshot(*args,**kwargs)
  def clean(r):
   if actual_cleanup:self.calls.append('cleanup');return recovery.cleanup(r)
   result=self.cleanup(r)
   if cleanup_failure:raise RuntimeError('injected-cleanup')
   return result
  with contextlib.ExitStack() as stack:
   stack.enter_context(patch.object(runner.Round,action,(lambda r:self.calls.append(action)) if normal else (lambda r:self.action(r))))
   stack.enter_context(patch.object(runner.Round,'cleanup',clean));stack.enter_context(patch.object(runner,'write',side_effect=write));stack.enter_context(patch.object(runner,'snapshot',side_effect=snap));stack.enter_context(patch.object(sys,'argv',['round.py',action,'--work',str(self.w)]));stack.enter_context(patch.object(sys,'stderr',self.stderr))
   if stderr_failure:stack.enter_context(patch.object(self.stderr,'write',side_effect=OSError('injected-stderr')))
   try:runner.main()
   except Exception as e:return e
  return None
 def flatten(self,error):
  return [error]+[v for e in getattr(error,'exceptions',[]) for v in self.flatten(e)]
 def check_failure(self,error,extra=None):
  self.assertIsNotNone(error);self.assertEqual(self.calls.count('cleanup'),1);errors=self.flatten(error);self.assertIn(self.original,errors)
  if extra:self.assertTrue(any(extra in str(e) for e in errors),errors)
 def refused(self):
  # Dispatcher refuses more work and actual seal/package path before new snapshot.
  count=len(list((self.w/'snapshots').iterdir()))
  for action in ['prepare','fixtures','seal']:
   with patch.object(sys,'argv',['round.py',action,'--work',str(self.w)]):
    with self.assertRaises(Exception):runner.main()
  self.assertEqual(len(list((self.w/'snapshots').iterdir())),count)
 def test_original_failure_keeps_real_registration(self):
  for action in ['prepare','fixtures']:
   with self.subTest(action=action):
    if action=='fixtures':self.tearDown();self.setUp()
    e=self.invoke(action);self.assertIs(e,self.original);self.check_failure(e)
    scope=runner.registered_scope(self.w);self.assertEqual((len(scope['analysis']),len(scope['closing'])),(1,1))
    runner.require_failure_audit(runner.Round(self.w));self.assertEqual(scope['closing'][0]['command'][2],'cleanup');self.assertTrue(json.loads((self.w/'dispatch-failure.json').read_text())['auditRegistered'])
    # Successful audit may package failure diagnostics; this is not task success.
    self.assertGreater(runner.package(self.w,self.w/'published')['files'],0)
 def test_analysis_write_failures_cleanup_and_block(self):
  self.check_failure(self.invoke('prepare','scope'),'analysis-scope');self.refused()
  with self.assertRaises(Exception):runner.package(self.w,self.w/'published')
 def test_fixtures_analysis_write_failure(self):
  self.check_failure(self.invoke('fixtures','scope'),'analysis-scope');self.refused()
 def test_registry_write_failures_preserve_partial_scope(self):
  self.check_failure(self.invoke('prepare','registry'),'closing-registry');self.assertTrue((self.w/'analysis-scope.json').exists());self.refused()
  with self.assertRaises(Exception):runner.package(self.w,self.w/'published')
 def test_fixtures_registry_write_failure(self):
  self.check_failure(self.invoke('fixtures','registry'),'closing-registry');self.refused()
 def test_snapshot_creation_failure_is_not_success(self):
  self.check_failure(self.invoke('prepare','snapshot'),'injected-snapshot');self.refused();self.assertFalse(json.loads((self.w/'dispatch-failure.json').read_text())['auditRegistered'])
 def test_fixtures_snapshot_creation_failure(self):
  self.check_failure(self.invoke('fixtures','snapshot'),'injected-snapshot');self.refused()
 def test_actual_snapshot_registration_failure_keeps_orphan_and_rejects_package(self):
  self.check_failure(self.invoke('fixtures','registration'),'injected-registration');self.refused()
  self.assertEqual(json.loads((self.w/'closing-registry.json').read_text()),[])
  self.assertEqual(len(list((self.w/'snapshots').glob('*.json'))),2)
  with self.assertRaisesRegex(AssertionError,'unclassified'):runner.package(self.w,self.w/'published')
 def test_audit_and_cleanup_errors_preserve_original(self):
  e=self.invoke(failure='scope',cleanup_failure=True);self.check_failure(e,'injected-cleanup');self.assertTrue(any('analysis-scope' in str(x) for x in self.flatten(e)));self.refused()
 def test_record_and_stderr_errors_cannot_skip_cleanup(self):
  e=self.invoke(failure='registry',cleanup_failure=True,record_failure=True,stderr_failure=True);self.check_failure(e,'injected-stderr');text=' '.join(str(x) for x in self.flatten(e));self.assertIn('dispatch-failure.json',text);self.assertIn('injected-cleanup',text)
  with self.assertRaises(Exception):runner.package(self.w,self.w/'published')
 def test_diagnostic_is_bounded(self):
  self.original=RuntimeError('x'*100000);e=self.invoke(failure='scope');self.check_failure(e);self.assertLess(len(self.stderr.getvalue().encode()),8192);self.assertLess((self.w/'dispatch-failure.json').stat().st_size,8192)
 def test_lost_failure_record_cannot_hide_missing_cleanup_registration(self):
  self.check_failure(self.invoke(failure='snapshot',record_failure=True,stderr_failure=True),'injected-snapshot')
  self.assertFalse((self.w/'dispatch-failure.json').exists());self.refused()
 def test_cleanup_exception_without_audit_failure_is_distinct(self):
  e=self.invoke(cleanup_failure=True);self.check_failure(e,'injected-cleanup');record=json.loads((self.w/'dispatch-failure.json').read_text());self.assertTrue(record['auditRegistered']);self.assertEqual([x['phase'] for x in record['errors']],['action','cleanup']);self.assertEqual(record['cleanupStatus'],'unknown')
 def test_every_record_write_and_stderr_can_fail(self):
  with patch.object(runner,'write',side_effect=OSError('all-record-writes')):
   e=self.invoke(stderr_failure=True)
  self.check_failure(e,'all-record-writes');self.assertTrue(any('injected-stderr' in str(x) for x in self.flatten(e)))
  with self.assertRaises(Exception):runner.package(self.w,self.w/'published')
 def test_partial_registry_is_not_erased(self):
  original_action=self.action
  def partial(r):
   runner.write(self.w/'closing-registry.json',[{'id':'incomplete'}]);return original_action(r)
  self.action=partial;e=self.invoke();self.check_failure(e)
  registry=json.loads((self.w/'closing-registry.json').read_text());self.assertEqual(registry[0],{'id':'incomplete'});self.assertEqual(len(registry),2);self.refused()
  with self.assertRaises(Exception):runner.package(self.w,self.w/'published')
 def test_unprintable_exception_still_dispatches_cleanup(self):
  class Unprintable(Exception):
   def __str__(self):raise ValueError('cannot-render-error')
  self.original=Unprintable();e=self.invoke(failure='scope');self.check_failure(e);self.assertIn('<unprintable exception>',self.stderr.getvalue())
 def test_normal_action_does_not_add_failure_cleanup(self):
  self.assertIsNone(self.invoke(normal=True));self.assertEqual(self.calls,['prepare']);self.assertFalse((self.w/'dispatch-failure.json').exists())
 def test_normal_fixtures_does_not_add_failure_cleanup(self):
  self.assertIsNone(self.invoke('fixtures',normal=True));self.assertEqual(self.calls,['fixtures'])
 def test_record_failure_reaches_existing_cleanup_stop_delete_absence(self):
  root=pathlib.Path(self.plan['vmRoot']);(root/'prefix/bin').mkdir(parents=True);(root/'prefix/bin/limactl').touch();(root/'lima/fake').mkdir(parents=True)
  runner.write(self.w/'ownership.json',{'root':str(root),'vmName':'fake','vmRegistrations':1})
  def cmd(r,args,**kwargs):
   action='list' if args[1]=='-c' else args[1];self.calls.append(action)
   if action=='delete':shutil.rmtree(root/'lima/fake')
   return {'exitCode':0},json.dumps({'exitCode':0,'stdout':'','stderr':''}) if action=='list' else ''
  with patch.object(runner.Round,'cmd',cmd),patch.object(runner.Round,'guest',side_effect=TimeoutError('injected-export')),patch.object(recovery.subprocess,'check_output',return_value=''),patch.object(recovery.subprocess,'run',side_effect=AssertionError('no subprocess')):
   e=self.invoke(failure='scope',actual_cleanup=True)
  self.check_failure(e,'analysis-scope');self.assertEqual(self.calls,['prepare','cleanup','stop','delete','list']);self.assertFalse(root.exists())
  result=json.loads((self.w/'cleanup.json').read_text());self.assertEqual(result['cleanupStatus'],'complete');self.assertEqual(result['evidenceStatus'],'missing');self.refused()
if __name__=='__main__':unittest.main()
