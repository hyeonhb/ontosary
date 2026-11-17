import datetime,hashlib,json,pathlib,tempfile,time,unittest
from unittest.mock import patch
import guest
from identity import RUNTIME_ENV
class ImportTests(unittest.TestCase):
 def test_actual_import_identity_mismatch_stops_before_reaper(self):
  with tempfile.TemporaryDirectory() as tmp:
   shared=pathlib.Path(tmp);raw=b'public fake image';(shared/'reused-image.tar').write_bytes(raw);image={'name':'fixture','target':'expected'}
   (shared/'image-export.json').write_text(json.dumps({'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'image':image}));(shared/'budget.json').write_text(json.dumps({'deadlines':{'environment':{'utc':(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=10)).isoformat()}}}))
   with patch.object(guest,'SHARED',shared),patch.object(guest.c,'command',return_value=(0,'','')) as cmd,patch.object(guest.image,'identify',return_value={'name':'fixture','target':'foreign'}) as identify:
    with self.assertRaisesRegex(RuntimeError,'import-image-identity'):guest.imported()
    self.assertEqual(cmd.call_count,1);self.assertEqual(cmd.call_args.kwargs['env'],RUNTIME_ENV);self.assertEqual(identify.call_args.kwargs['env'],RUNTIME_ENV);self.assertFalse((shared/'import-verified.json').exists())
 def test_partial_archive_rejected_before_runtime_load(self):
  with tempfile.TemporaryDirectory() as tmp:
   shared=pathlib.Path(tmp);(shared/'reused-image.tar').write_bytes(b'partial');(shared/'image-export.json').write_text(json.dumps({'bytes':999,'sha256':'expected','image':{}}));(shared/'budget.json').write_text(json.dumps({'deadlines':{'environment':{'utc':(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=10)).isoformat()}}}))
   with patch.object(guest,'SHARED',shared),patch.object(guest.c,'command') as cmd:
    with self.assertRaisesRegex(RuntimeError,'import-archive-bytes'):guest.imported()
    cmd.assert_not_called()
if __name__=='__main__':unittest.main()
