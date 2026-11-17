import io,json,os,pathlib,tarfile,time,unittest
from unittest.mock import patch
import test_safe_export,exporter
from collector import SafeFiles,Rejected
class DiagnosticTests(unittest.TestCase):
 def setUp(self):self.f=test_safe_export.ExportTests();self.f.setUp()
 def tearDown(self):self.f.tearDown()
 def export(self,**kw):return self.f.export(strict=False,**kw)
 def test_bad_metadata_retains_independent_service_and_spec_diagnostics(self):
  f=self.f;f.state['collectionStatus']='suppressed';f.save();(f.run/'service-raw.jsonl').write_text('{"LoadState":"not-found","timestamp":0}\n');(f.run/'native.json').write_text('{"raw":"preserved"}');(f.shared/'image-export.json').write_text('{"bad":"owner"}');real=SafeFiles.copy
  def copy(safe,path,name,*a,**kw):
   if pathlib.Path(path).name=='image-export.json':raise Rejected('file-owner:image-export.json')
   return real(safe,path,name,*a,**kw)
  with patch.object(SafeFiles,'copy',copy):r=self.export()
  files=f.members();status=json.loads(files['export-status.json']);self.assertEqual(r['status'],'partial');self.assertIn('runs/'+f.run.name+'/service-raw.jsonl',files);self.assertIn('runs/'+f.run.name+'/native.json',files);self.assertNotIn('image-export.json',files);self.assertIn('file-owner',status['rejections'][0]['reason'])
 def test_invalid_normal_result_becomes_diagnostics_without_result_members(self):
  f=self.f;f.collected();p=f.run/'result/source/public';p.chmod(0o644);r=self.export();self.assertEqual(r['status'],'partial');self.assertFalse(any('/result/' in n for n in f.members()))
 def test_rejected_hardlink_and_pending_worker_originals_never_read(self):
  f=self.f;canary=f.base/'canary';canary.write_bytes(b'FORBIDDEN-CANARY');os.link(canary,f.run/'source/hard')
  with self.assertRaises(Rejected):f.collected()
  f.state.update(collectionStatus='failed',execPending=True);f.save();self.export();self.assertNotIn(b'FORBIDDEN-CANARY',b''.join(f.members().values()))
 def test_special_and_parent_symlink_are_diagnostic_rejections(self):
  f=self.f;f.state['collectionStatus']='suppressed';f.save();os.mkfifo(f.run/'events.jsonl');r=self.export();self.assertEqual(r['status'],'partial');self.assertFalse(any(n.endswith('events.jsonl') for n in f.members()))
  f.target=f.base/'second';parent=f.root/'runs';parent.rename(f.root/'real');parent.symlink_to(f.root/'real',target_is_directory=True);r=self.export();self.assertEqual(r['status'],'partial');self.assertFalse(any(n.startswith('runs/') for n in f.members()))
 def test_count_byte_caps_stop_body_and_preserve_reserved_metadata(self):
  f=self.f;f.collected();r=self.export(max_files=8);self.assertEqual(r['status'],'partial');self.assertLessEqual(r['boundedBytes'],16*1024*1024);self.assertIn('export-status.json',f.members())
  f.target=f.base/'second';big=f.run/'events.jsonl'
  with big.open('wb') as p:p.truncate(16*1024*1024+1)
  r=self.export();status=json.loads(f.members()['export-status.json']);self.assertEqual(r['status'],'partial');self.assertTrue(status['collectionStopped']);self.assertNotIn('runs/'+f.run.name+'/events.jsonl',f.members())
 def test_archive_failure_and_expiry_publish_only_small_error_receipt(self):
  f=self.f;f.collected();r=self.export(fail_after=1);self.assertEqual(r['status'],'error-receipt');self.assertFalse((f.target/'evidence.tar.gz').exists());self.assertEqual([p.name for p in f.target.iterdir()],['receipt.json']);self.assertLess((f.target/'receipt.json').stat().st_size,8192)
  f.target=f.base/'second';r=self.export(deadline=time.monotonic()-1);self.assertEqual(r['status'],'error-receipt')
if __name__=='__main__':unittest.main()
