import hashlib,json,os,pathlib,tempfile,time,unittest
from artifacts import Store,Rejected
class ArtifactTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.tmp.name).resolve()/'store';self.store=Store(self.root,100000);self.req={'name':'fixed','version':'1','platform':'fixture','url':'fixture://public','bytes':3,'sha256':hashlib.sha256(b'abc').hexdigest(),'buildInputHashes':{}};self.end=time.monotonic()+5
 def tearDown(self):self.tmp.cleanup()
 def acquire(self,producer=lambda sink:sink(b'abc')):return self.store.acquire(self.req,producer,self.end)
 def test_missing(self):self.assertIsNone(self.store.lookup(self.req,self.end))
 def test_hit_rehash_skips_producer(self):
  first=self.acquire();second=self.acquire(lambda _:self.fail('producer on hit'));self.assertFalse(first['cacheHit']);self.assertTrue(second['cacheHit']);self.assertEqual(first['actual'],second['actual'])
 def test_corruption_is_not_recertified(self):
  p=pathlib.Path(self.acquire()['path']);p.chmod(0o600);p.write_bytes(b'xyz')
  with self.assertRaises(Rejected):self.acquire()
 def test_version_mismatch(self):
  self.acquire();self.req['version']='2'
  with self.assertRaises(Rejected):self.acquire()
 def test_build_input_mismatch(self):
  self.acquire();self.req['buildInputHashes']={'recipe':'changed'}
  with self.assertRaises(Rejected):self.acquire()
 def test_partial_cleaned(self):
  with self.assertRaises(Rejected):self.acquire(lambda sink:sink(b'ab'))
  self.assertEqual([p.name for p in self.root.iterdir()],['.lock'])
 def test_producer_failure_cleaned(self):
  def fail(sink):sink(b'a');raise RuntimeError('registration failed')
  with self.assertRaises(RuntimeError):self.acquire(fail)
  self.assertEqual([p.name for p in self.root.iterdir()],['.lock'])
 def test_symlink_rejected(self):
  p=pathlib.Path(self.acquire()['path']);p.unlink();p.symlink_to('/etc/hosts')
  with self.assertRaises(Rejected):self.acquire()
 def test_unowned_partial_counts_capacity(self):
  pending=self.root/'.pending-other';pending.mkdir();(pending/'data').write_bytes(b'x'*40000)
  with self.assertRaises(Rejected):self.acquire()
  self.assertTrue((pending/'data').exists())
 def test_registration_incomplete(self):
  (self.root/'bad').mkdir()
  with self.assertRaises(Rejected):self.acquire()
 def test_capacity_before_producer(self):
  self.store.limit=1
  with self.assertRaises(Rejected):self.acquire(lambda _:self.fail('producer'))
 def test_deadline(self):
  self.end=time.monotonic()-1
  with self.assertRaises(Rejected):self.acquire()
if __name__=='__main__':unittest.main()
