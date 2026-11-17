import datetime,hashlib,io,json,pathlib,shutil,tarfile,tempfile,time,unittest
from unittest.mock import patch
import round as runner,recovery
class CleanupTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.w=pathlib.Path(self.tmp.name).resolve();self.root=self.w/'ontosary-s2-test';(self.root/'prefix/bin').mkdir(parents=True);(self.root/'prefix/bin/limactl').touch();(self.root/'lima/vm').mkdir(parents=True);self.calls=[];self.failure=set();self.left=300
  for n,v in [('plan.json',{'vmRoot':str(self.root),'vmName':'vm','store':str(self.w/'store'),'round':'test'}),('budget.json',{'deadlines':{'finish':{'utc':(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=300)).isoformat(),'monotonic':time.monotonic()+300}}}),('ownership.json',{'root':str(self.root),'vmName':'vm','vmRegistrations':1})]:(self.w/n).write_text(json.dumps(v))
  self.r=runner.Round(self.w);self.r.cmd=self.cmd;self.r.guest=self.guest
  self.data=b'{}';self.index={'state.json':{'sha256':hashlib.sha256(self.data).hexdigest(),'bytes':2}}
 def tearDown(self):self.tmp.cleanup()
 def guest(self,args,**kw):
  self.calls.append(('export',kw['timeout']))
  if 'transport' in self.failure:raise TimeoutError('transport')
  return {'exitCode':1 if 'export' in self.failure else 0},json.dumps({'status':'diagnostic'})
 def cmd(self,args,**kw):
  action='list' if args[1]=='-c' else args[1];self.calls.append((action,kw['timeout']))
  if action=='copy':
   name=args[2].split('/')[-1];p=pathlib.Path(args[-1]);p.write_bytes(b'partial')
   if name in self.failure:raise RuntimeError('copy:'+name)
   if name=='index.json':p.write_text(json.dumps(self.index))
   else:
    with tarfile.open(p,'w:gz') as t:m=tarfile.TarInfo('state.json');m.size=2;t.addfile(m,io.BytesIO(self.data))
  if action=='delete' and 'delete' not in self.failure:shutil.rmtree(self.root/'lima/vm')
  if action=='list':return {'exitCode':0},json.dumps({'exitCode':1 if 'absence' in self.failure else 0,'stdout':'','stderr':'No instance found'})
  return {'exitCode':1 if action in self.failure else 0},''
 def clean(self):
  with patch.object(recovery,'remaining',return_value=self.left):return self.r.cleanup()
 def test_archive_and_index_copy_errors_do_not_skip_disposal(self):
  for failure in ['evidence.tar.gz','index.json']:
   with self.subTest(failure=failure):
    if not (self.root/'lima/vm').exists():(self.root/'lima/vm').mkdir(parents=True);(self.root/'prefix/bin').mkdir(parents=True);(self.root/'prefix/bin/limactl').touch()
    self.failure={failure};r=self.clean();self.assertEqual(r['cleanupStatus'],'complete');self.assertEqual(r['evidenceStatus'],'missing');self.assertFalse((self.w/'recovery-final.tar.gz').exists());self.assertFalse(list(self.w.glob('.recovery-*')))
 def test_export_exit_and_transport_exception_still_dispose(self):
  for failure in ['export','transport']:
   with self.subTest(failure=failure):
    if not self.root.exists():(self.root/'lima/vm').mkdir(parents=True);(self.root/'prefix/bin').mkdir(parents=True);(self.root/'prefix/bin/limactl').touch()
    self.failure={failure};self.calls=[];r=self.clean();self.assertEqual([x[0] for x in self.calls],['export','stop','delete','list']);self.assertEqual(r['cleanupStatus'],'complete')
 def test_record_failure_still_disposes(self):
  with patch.object(recovery,'write',side_effect=OSError('record-failure')):r=self.clean()
  self.assertTrue(r['vmAbsent']);self.assertIn('cleanup-record',[x['phase'] for x in r['errors']])
 def test_stop_failure_does_not_skip_delete(self):
  self.failure={'stop'};r=self.clean();self.assertEqual(r['cleanupStatus'],'complete');self.assertIn('stop',[x['phase'] for x in r['errors']])
 def test_delete_or_absence_failure_keeps_management_root(self):
  for fail in ['delete','absence']:
   self.failure={fail};r=self.clean();self.assertEqual(r['cleanupStatus'],'unconfirmed');self.assertTrue(self.root.exists())
 def test_reserve_preempts_retrieval(self):
  self.left=89;r=self.clean();self.assertNotIn('export',[x[0] for x in self.calls]);self.assertEqual(r['cleanupStatus'],'complete');self.assertTrue(all(t<=89 for _,t in self.calls))
 def test_duplicate_cleanup_never_reuses_old_archive(self):
  a=self.clean();before=list(self.calls);b=self.clean();self.assertEqual(self.calls,before);self.assertEqual(a['evidenceStatus'],'diagnostic');self.assertEqual(b['evidenceStatus'],'not-retried')
 def test_wrong_owner_refuses_all_deletion(self):
  p=self.w/'ownership.json';s=json.loads(p.read_text());s['vmName']='foreign';p.write_text(json.dumps(s));r=self.clean();self.assertEqual(r['cleanupStatus'],'unconfirmed');self.assertEqual(self.calls,[])
 def test_verified_pair_published_after_both_copies(self):
  r=self.clean();self.assertEqual(r['evidenceStatus'],'diagnostic');self.assertEqual([x[0] for x in self.calls],['export','copy','copy','stop','delete','list']);self.assertTrue((self.w/'recovery-final.tar.gz').exists())
if __name__=='__main__':unittest.main()
