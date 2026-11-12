import copy,json,pathlib,shutil,tempfile,unittest
from policy import RULE,verify
from scope import rows,verify as audit,classify,inventory,verify_index
PRIOR=pathlib.Path('experiments/domain-model/s2/verification/2026-11-11-namespace-diagnosis/snapshots')
WORK=pathlib.Path('experiments/domain-model/s2/verification/2026-11-12-single-policy-test/host')
if not WORK.exists():WORK=pathlib.Path('work/s2-single-policy-test')
class Policy(unittest.TestCase):
 def setUp(self):
  self.old=json.loads((WORK/'prior-native.json').read_text());self.new=copy.deepcopy(self.old);self.new['Spec']['linux']['seccomp']['syscalls'].append(copy.deepcopy(RULE))
 def test_exact(self):verify(self.new,self.old)
 def test_extra_allow(self):
  self.new['Spec']['linux']['seccomp']['syscalls'].append({'names':['mount'],'action':'SCMP_ACT_ALLOW'})
  with self.assertRaises(AssertionError):verify(self.new,self.old)
 def test_wider_flags(self):
  self.new['Spec']['linux']['seccomp']['syscalls'][-1]['args'][0]['op']='SCMP_CMP_MASKED_EQ'
  with self.assertRaises(AssertionError):verify(self.new,self.old)
 def test_default(self):
  self.new['Spec']['linux']['seccomp']['defaultAction']='SCMP_ACT_ALLOW'
  with self.assertRaises(AssertionError):verify(self.new,self.old)
 def test_nnp(self):
  self.new['Spec']['process']['noNewPrivileges']=False
  with self.assertRaises(AssertionError):verify(self.new,self.old)
 def test_not_applied(self):
  with self.assertRaises(AssertionError):verify(self.old,self.old)
 def test_mount_access(self):
  self.new['Spec']['mounts'][0]['options']=[]
  with self.assertRaises(AssertionError):verify(self.new,self.old)
class Scope(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.tmp.name);self.snap=self.root/'snapshots';self.snap.mkdir();self.scope=json.loads((WORK/'prior-snapshot-scope.json').read_text())
  for row in self.scope['analysis']:
   for ext in ['.json','.tar.gz']:shutil.copyfile(PRIOR/(row['id']+ext),self.snap/(row['id']+ext))
 def tearDown(self):self.tmp.cleanup()
 def closing(self):
  for row in self.scope['closing']:
   for ext in ['.json','.tar.gz']:shutil.copyfile(PRIOR/(row['id']+ext),self.snap/(row['id']+ext))
 def test_real_11_plus_1(self):
  self.closing();classify(self.snap,self.scope['analysis'],self.scope['closing']);self.assertEqual(audit(self.snap,self.scope['analysis'])['snapshotsVerified'],11)
 def test_missing(self):
  next(self.snap.glob('*.json')).unlink()
  with self.assertRaises(FileNotFoundError):audit(self.snap,self.scope['analysis'])
 def test_tampered(self):
  next(self.snap.glob('*.json')).write_text('{}')
  with self.assertRaises(AssertionError):audit(self.snap,self.scope['analysis'])
 def test_closing_stable(self):
  before=audit(self.snap,self.scope['analysis']);self.closing();self.assertEqual(before,audit(self.snap,self.scope['analysis']))
 def test_closing_index_tamper(self):
  self.closing();(self.root/'snapshot-scope.json').write_text(json.dumps(self.scope));(self.root/'index.json').write_text(json.dumps(inventory(self.root)));verify_index(self.root)
  (self.snap/(self.scope['closing'][0]['id']+'.tar.gz')).write_bytes(b'tampered')
  with self.assertRaises((AssertionError,__import__('tarfile').ReadError)):verify_index(self.root)
 def test_unclassified(self):
  self.closing()
  with self.assertRaises(AssertionError):classify(self.snap,self.scope['analysis'],[])
if __name__=='__main__':unittest.main(verbosity=2)
