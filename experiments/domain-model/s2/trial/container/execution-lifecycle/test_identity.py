import copy,hashlib,json,pathlib,tarfile,unittest
from identity import normalize,compare,expected_legacy,Rejected,HOOK_ENV
ARCHIVE=pathlib.Path('experiments/domain-model/s2/verification/2026-11-12-policy-retry/host/guest-evidence.tar.gz')
class IdentityTests(unittest.TestCase):
 def setUp(self):
  self.raw=[];self.ident=[];self.spec=[]
  with tarfile.open(ARCHIVE) as t:
   for mode in ['baseline','candidate']:
    n=json.load(t.extractfile(mode+'/native.json'));s=json.load(t.extractfile(mode+'/state.json'));self.raw.append(n)
    i={'runId':s['runId'],'run':'/opt/ontosary-fixture/runs/'+s['runId'],'shared':'/opt/ontosary-policy-retry','slice':s['slice'],'containerId':s['containerId'],'image':s['image'],'inputHashes':{}}
    n,i,_=expected_legacy(n,i,s['image']);self.spec.append(n);self.ident.append(i)
 def verify(self):return compare(self.spec[1],self.spec[0],self.ident[1],self.ident[0],True)
 def test_saved_pair_explicit_environment_migration(self):self.assertTrue(self.verify()['accepted'])
 def test_raw_historical_duplicates_rejected(self):
  for n,i in zip(self.raw,self.ident):
   with self.assertRaises(Rejected):normalize(n,i)
 def test_other_run_path(self):
  self.spec[1]['Spec']['annotations']['nerdctl/state-dir']=self.spec[0]['Spec']['annotations']['nerdctl/state-dir']
  with self.assertRaises(Rejected):self.verify()
 def test_outside_mount(self):
  next(m for m in self.spec[1]['Spec']['mounts'] if m['destination']=='/source')['source']='/etc'
  with self.assertRaises(Rejected):self.verify()
 def test_duplicate_env(self):
  self.spec[1]['Spec']['process']['env'].append(self.spec[1]['Spec']['process']['env'][0])
  with self.assertRaises(Rejected):self.verify()
 def test_other_supervisor_pressure_path(self):
  self.spec[1]['Spec']['hooks']['poststop'][0]['env'].append('MEMORY_PRESSURE_WATCH=/sys/fs/cgroup/foreign/memory.pressure')
  with self.assertRaises(Rejected):self.verify()
 def test_extra_hook(self):
  self.spec[1]['Spec']['hooks']['poststop']*=2
  with self.assertRaises(Rejected):self.verify()
 def test_extra_command(self):
  self.spec[1]['Spec']['process']['args'].append('--foreign');self.assertFalse(self.verify()['accepted'])
 def test_extra_privilege(self):
  self.spec[1]['Spec']['process']['noNewPrivileges']=False;self.assertFalse(self.verify()['accepted'])
 def test_extra_seccomp(self):
  self.spec[1]['Spec']['linux']['seccomp']['syscalls'].append({'names':['mount'],'action':'SCMP_ACT_ALLOW'});self.assertFalse(self.verify()['accepted'])
 def test_duplicate_mount(self):
  self.spec[1]['Spec']['mounts'].append(copy.deepcopy(self.spec[1]['Spec']['mounts'][0]))
  with self.assertRaises(Rejected):self.verify()
 def test_nested_mount_reorder_rejected(self):
  m=self.spec[1]['Spec']['mounts'];i=next(i for i,x in enumerate(m) if x['destination']=='/home/runner/cli-state');j=next(i for i,x in enumerate(m) if x['destination']=='/home/runner/cli-state/config.toml');m[i],m[j]=m[j],m[i]
  with self.assertRaises(Rejected):self.verify()
 def test_independent_peer_order(self):
  m=self.spec[1]['Spec']['mounts'];i=next(i for i,x in enumerate(m) if x['destination']=='/source');j=next(i for i,x in enumerate(m) if x['destination']=='/output');m[i],m[j]=m[j],m[i];self.assertTrue(self.verify()['accepted'])
 def test_input_mismatch(self):
  self.ident[1]['inputHashes']={'probe':'bad'}
  with self.assertRaises(Rejected):self.verify()
 def test_hook_command_rejected(self):
  self.spec[1]['Spec']['hooks']['poststop'][0]['args'].append('--foreign')
  with self.assertRaises(Rejected):self.verify()
if __name__=='__main__':unittest.main()
