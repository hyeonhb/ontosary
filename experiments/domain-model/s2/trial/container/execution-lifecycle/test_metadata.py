import contextlib,datetime,hashlib,io,json,os,pathlib,stat,tempfile,time,types,unittest
from unittest.mock import patch
import metadata,guest,exporter
from collector import Rejected
class MetadataTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.tmp.name).resolve();self.shared=self.root/'manager';self.shared.mkdir();self.transport=self.root/'transport';self.transport.mkdir(mode=0o700);self.source=self.transport/'value.json';self.value={'x.py':'a'*64};self.source.write_text(json.dumps(self.value));self.source.chmod(0o600);self.owner=os.getuid();self.transfer=self.owner+1000
 def tearDown(self):self.tmp.cleanup()
 @contextlib.contextmanager
 def ownership(self,bad=None):
  source_inode=self.source.stat().st_ino;parent_inode=self.transport.stat().st_ino;real_stat=os.stat;real_fstat=os.fstat
  def convert(s):
   if s.st_ino not in [source_inode,parent_inode]:return s
   d={n:getattr(s,n) for n in dir(s) if n.startswith('st_')};d['st_uid']=self.transfer if bad is None or s.st_ino==parent_inode else bad;return types.SimpleNamespace(**d)
  with patch('os.stat',side_effect=lambda *a,**k:convert(real_stat(*a,**k))),patch('os.fstat',side_effect=lambda *a,**k:convert(real_fstat(*a,**k))):yield
 def publish(self,name='input-members.json',digest=None,binding=None):
  return metadata.publish(self.shared,self.source,name,digest or hashlib.sha256(self.source.read_bytes()).hexdigest(),self.transfer,time.monotonic()+2,binding)
 def test_distinct_transfer_uid_publishes_manager_owned_bytes(self):
  with self.ownership():receipt=self.publish()
  self.assertNotEqual(receipt['sourceUid'],receipt['managerUid']);self.assertEqual(receipt['managerUid'],self.owner);self.assertEqual(receipt['mode'],'0o600');self.assertEqual((self.shared/'input-members.json').read_bytes(),self.source.read_bytes())
 def test_bad_owner_mode_hash_and_schema_leave_no_publication(self):
  with self.ownership(bad=self.transfer+1),self.assertRaisesRegex(Rejected,'owner-mode'):self.publish()
  self.source.chmod(0o622)
  with self.ownership(),self.assertRaisesRegex(Rejected,'owner-mode'):self.publish()
  self.source.chmod(0o600)
  with self.ownership(),self.assertRaisesRegex(Rejected,'metadata-hash'):self.publish(digest='b'*64)
  self.source.write_text('{"../outside":"bad"}')
  with self.ownership(),self.assertRaisesRegex(Rejected,'member-binding'):self.publish()
  self.assertFalse((self.shared/'input-members.json').exists());self.assertFalse(list(self.shared.glob('.metadata-*')))
 def test_symlink_hardlink_fifo_rejected_without_block(self):
  for kind in ['link','hard','fifo']:
   p=self.transport/'bad'
   if kind=='link':p.symlink_to(self.source)
   elif kind=='hard':os.link(self.source,p)
   else:os.mkfifo(p)
   with self.ownership(),self.assertRaises((Rejected,OSError)):metadata.publish(self.shared,p,'input-members.json','a'*64,self.transfer,time.monotonic()+1)
   p.unlink()
 def test_atomic_publication_failure_leaves_no_partial(self):
  with self.ownership(),patch.object(metadata.os,'rename',side_effect=OSError('injected')),self.assertRaises(OSError):self.publish()
  self.assertFalse((self.shared/'input-members.json').exists());self.assertFalse(list(self.shared.glob('.metadata-*')))
 def test_publish_import_export_connection(self):
  image={'name':'fixture','target':'sha256:'+'a'*64,'config':'sha256:'+'b'*64,'chain':'sha256:'+'c'*64,'platform':'linux/arm64'};data=b'public image';self.value={'image':image,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'buildKey':'d'*64};self.source.write_text(json.dumps(self.value))
  with self.ownership():self.publish('image-export.json',binding='d'*64)
  (self.shared/'reused-image.tar').write_bytes(data);(self.shared/'budget.json').write_text(json.dumps({'deadlines':{'environment':{'utc':(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=20)).isoformat()}}}))
  with patch.object(guest,'SHARED',self.shared),patch.object(guest.c,'command',return_value=(0,'','')),patch.object(guest.image,'identify',return_value=image),patch.object(guest,'activate_observer'),contextlib.redirect_stdout(io.StringIO()):guest.imported()
  result=exporter.export(self.root/'runs-root',self.shared,self.root/'out',time.monotonic()+2)
  self.assertEqual(result['status'],'diagnostic');self.assertTrue((self.root/'out/evidence.tar.gz').exists())
if __name__=='__main__':unittest.main()
