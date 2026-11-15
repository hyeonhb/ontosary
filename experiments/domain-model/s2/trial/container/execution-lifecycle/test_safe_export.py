import contextlib,io,json,os,pathlib,tarfile,tempfile,time,unittest
from unittest.mock import patch
import guest
from collector import collect,inventory,Rejected,SafeFiles
from exporter import DIAGNOSTICS
class ExportTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.base=pathlib.Path(self.tmp.name).resolve();self.root=self.base/'owned';self.shared=self.base/'shared';self.shared.mkdir();self.run=self.root/'runs'/'aaaaaaaaaaaa';self.run.mkdir(parents=True);self.target=self.base/'published'
  for n in ['source','auxiliary','shell-home','cli-state','scratch']:(self.run/n).mkdir()
  (self.run/'source/public').write_bytes(b'public source');(self.run/'auxiliary/answer').write_bytes(b'answer');(self.run/'shell-home/secret').write_bytes(b'RAW-DO-NOT-READ')
  self.term={'state':'stopped-confirmed','confirmed':True,'admissionClosed':True,'runId':self.run.name,'containerId':'cid','image':{'target':'image'},'cgroup':'owned','cgroupInode':1,'source':str(self.run/'source'),'auxiliary':str(self.run/'auxiliary'),'reason':'exit','exitCode':0}
  self.state={**self.term,'state':'collecting','collectionStatus':'collecting','terminationConfirmed':True,'removalConfirmed':True,'cleanupDone':True,'serviceInactiveConfirmed':True,'unitFilesRemoved':True};self.save()
  (self.run/'termination.json').write_text(json.dumps(self.term));(self.run/'removed.json').write_text(json.dumps({'containerAbsent':True,'taskAbsent':True,'pending':False}))
  self.baseline=inventory({n:self.run/n for n in ['source','auxiliary']})
 def tearDown(self):
  for root,dirs,files in os.walk(self.base):os.chmod(root,0o700)
  self.tmp.cleanup()
 def save(self):(self.run/'state.json').write_text(json.dumps(self.state))
 def collected(self):
  record=collect(self.run,self.baseline,self.term);self.state['collectionStatus']='collected';self.state['state']='finalized';self.save();return record
 def export(self,**kwargs):
  with patch.object(guest.c,'ROOT',self.root),patch.object(guest,'SHARED',self.shared),contextlib.redirect_stdout(io.StringIO()):return guest.export(target=self.target,deadline=kwargs.pop('deadline',time.monotonic()+3),**kwargs)
 def members(self):
  with tarfile.open(self.target/'evidence.tar.gz') as t:return {m.name:t.extractfile(m).read() for m in t}
 def test_collector_to_exact_export(self):
  self.collected();r=self.export();files=self.members();prefix='runs/'+self.run.name+'/'
  self.assertEqual(set(files),{prefix+n for n in ['state.json','termination.json','removed.json','result/fixture.json','result/source/public','result/auxiliary/answer']}|{'export-status.json'})
  self.assertEqual(files[prefix+'result/source/public'],b'public source');self.assertEqual(set(json.loads((self.target/'index.json').read_text())),set(files));self.assertEqual(r['metadataIncludedFiles'],len(files)+1)
 def test_hardlink_collector_rejection_cannot_reenter_export(self):
  canary=self.base/'manager-canary';canary.write_bytes(b'PUBLIC-CANARY');os.link(canary,self.run/'source/hardlink')
  with self.assertRaisesRegex(Rejected,'hardlink'):self.collected()
  self.state['collectionStatus']='failed';self.save();self.export();self.assertNotIn(b'PUBLIC-CANARY',b''.join(self.members().values()))
 def test_ineligible_states_never_open_worker_roots(self):
  for status,term,removal in [('suppressed',True,True),('failed',True,True),('collected',False,True),('collected',True,False)]:
   with self.subTest(status=status,term=term,removal=removal):
    self.state.update(collectionStatus=status,terminationConfirmed=term,removalConfirmed=removal);self.save();self.target=self.base/(status+str(term)+str(removal));opened=[];real=os.open
    def traced(path,*args,**kw):
     opened.append(str(path));self.assertNotIn(str(path),['source','auxiliary','shell-home','cli-state','scratch','result']);return real(path,*args,**kw)
    with patch('os.open',side_effect=traced):self.export()
 def test_revoked_success_remains_diagnostic(self):
  self.collected();(self.run/'result').rename(self.run/'quarantined-result');self.state['collectionStatus']='suppressed';self.save();self.export();self.assertFalse(any('/result/' in n for n in self.members()))
 def test_tampered_manifest_rejected(self):
  self.collected();p=self.run/'result/fixture.json';os.chmod(p,0o644);r=json.loads(p.read_text());r['snapshot']['files']['source/public']['sha256']='bad';p.write_text(json.dumps(r));os.chmod(p,0o444)
  with self.assertRaisesRegex(Rejected,'manifest-mismatch'):self.export()
  self.assertFalse(self.target.exists())
 def test_result_binding_tamper(self):
  self.collected();self.state['containerId']='other';self.save()
  with self.assertRaisesRegex(Rejected,'export-binding'):self.export()
 def test_symlink_parent_symlink_fifo_hardlink_diagnostic(self):
  self.state['collectionStatus']='suppressed';self.save();p=self.run/'events.jsonl'
  for kind in ['symlink','fifo','hardlink']:
   with self.subTest(kind=kind):
    if kind=='symlink':p.symlink_to(self.run/'state.json')
    elif kind=='fifo':os.mkfifo(p)
    else:os.link(self.run/'state.json',p)
    with self.assertRaises((Rejected,OSError)):self.export()
    p.unlink();self.assertFalse(self.target.exists())
  parent=self.root/'runs';parent.rename(self.root/'real-runs');parent.symlink_to(self.root/'real-runs',target_is_directory=True)
  with self.assertRaises(OSError):self.export()
 def test_oversize_rejected_before_body_open(self):
  self.state['collectionStatus']='suppressed';self.save();p=self.run/'events.jsonl'
  with p.open('wb') as f:f.truncate(16*1024*1024+1)
  real=os.open
  def check(path,*a,**kw):
   if str(path)=='events.jsonl':self.fail('oversized body opened')
   return real(path,*a,**kw)
  with patch('os.open',side_effect=check),self.assertRaisesRegex(Rejected,'byte-limit'):self.export()
 def test_total_bytes_and_final_metadata_included(self):
  self.collected();r=self.export();target=self.target;self.target=self.base/'second'
  with self.assertRaisesRegex(Rejected,'byte-limit'):self.export(max_bytes=r['boundedBytes']-100)
  self.assertFalse(self.target.exists())
 def test_total_file_count_includes_external_index(self):
  self.collected();r=self.export();self.target=self.base/'second'
  with self.assertRaisesRegex(Rejected,'file-count-limit'):self.export(max_files=r['metadataIncludedFiles']-1)
 def test_expired_deadline_and_partial_archive_unpublished(self):
  self.collected()
  with self.assertRaisesRegex(Rejected,'time'):self.export(deadline=time.monotonic()-1)
  with self.assertRaisesRegex(Rejected,'injected'):self.export(fail_after=2)
  self.assertFalse(self.target.exists());self.assertEqual(list(self.base.glob('.s2-export-*')),[])
 def test_previous_archive_cannot_be_reported_as_new_success(self):
  self.collected();self.export()
  with self.assertRaisesRegex(Rejected,'already-published'):self.export()
 def test_unlisted_manager_file_is_excluded(self):
  self.state['collectionStatus']='suppressed';self.save();(self.run/'arbitrary').write_bytes(b'unlisted');self.export();self.assertFalse(any(n.endswith('/arbitrary') for n in self.members()))
 def test_result_symlink_and_unsealed_files_rejected(self):
  self.collected();p=self.run/'result/source/public';os.chmod(p,0o644)
  with self.assertRaisesRegex(Rejected,'unsealed-file'):self.export()
 def test_depth_bound(self):
  stage=self.base/'stage';stage.mkdir();safe=SafeFiles(stage,time.monotonic()+1)
  with self.assertRaisesRegex(Rejected,'export-name'):safe.copy(self.run/'state.json','/'.join(['x']*17))
 def test_replacement_and_growth_during_safe_read_rejected(self):
  from collector import SafeFiles
  for kind in ['replace','grow']:
   stage=self.base/('stage-'+kind);stage.mkdir();source=self.base/('race-'+kind);source.write_bytes(b'public');safe=SafeFiles(stage,time.monotonic()+2);original=os.read;injected=False
   def racing(fd,size):
    nonlocal injected
    data=original(fd,size)
    if data and not injected:
     injected=True
     if kind=='replace':source.unlink();source.write_bytes(b'public')
     else:
      with source.open('ab') as f:f.write(b'grew')
    return data
   with self.subTest(kind=kind),patch('os.read',side_effect=racing),self.assertRaisesRegex(Rejected,'file-changed|file-grew'):safe.copy(source,'copied')
 def test_time_limit_while_reading_and_pending_state(self):
  stage=self.base/'read-stage';stage.mkdir();safe=SafeFiles(stage,time.monotonic()+.01);original=os.read
  def slow(fd,size):
   result=original(fd,size);time.sleep(.02);return result
  with patch('os.read',side_effect=slow),self.assertRaisesRegex(Rejected,'time-limit'):safe.copy(self.run/'state.json','state.json')
  self.collected();self.state['execPending']=True;self.save();self.export();self.assertFalse(any('/result/' in n for n in self.members()))
if __name__=='__main__':unittest.main()
