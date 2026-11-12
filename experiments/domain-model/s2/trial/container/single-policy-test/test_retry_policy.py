import copy,json,pathlib,unittest
from runtime_policy import normalize,baseline_verify,verify
from policy import RULE
OLD=json.loads(pathlib.Path('experiments/domain-model/s2/verification/2026-11-12-single-policy-test/host/prior-native.json').read_text())
def fixture(cid,rid):
 oldcid=OLD['ID'];shared='/opt/ontosary-policy-retry';run='/opt/ontosary-fixture/runs/'+rid
 s=json.dumps(OLD).replace(oldcid,cid).replace(oldcid[:12],cid[:12]).replace('/opt/ontosary-namespace-diagnosis/baseline',run).replace('/opt/ontosary-namespace-diagnosis',shared).replace(run+'/output',run+'/auxiliary').replace(run+'/state',run+'/cli-state')
 n=json.loads(s);n['Spec']['annotations']['nerdctl/name']='ontosary-'+rid;n['Spec']['linux']['cgroupsPath']='ontosary-'+rid+'.slice:nerdctl:'+cid
 return n,{'run':run,'shared':shared,'slice_name':'ontosary-'+rid+'.slice'}
class RuntimePolicy(unittest.TestCase):
 def setUp(self):
  self.b,self.bi=fixture('a'*64,'1'*12);self.c,self.ci=fixture('b'*64,'2'*12);self.c['Spec']['linux']['seccomp']['syscalls'].append(copy.deepcopy(RULE))
 def reject(self):
  with self.assertRaises(AssertionError):verify(self.c,self.b,self.ci,self.bi)
 def test_exact_and_original(self):baseline_verify(self.b,OLD,**self.bi);verify(self.c,self.b,self.ci,self.bi)
 def test_unowned_mount(self):
  next(m for m in self.c['Spec']['mounts'] if m['destination']=='/source')['source']='/etc';self.reject()
 def test_extra_allow(self):self.c['Spec']['linux']['seccomp']['syscalls'].append({'names':['mount'],'action':'SCMP_ACT_ALLOW'});self.reject()
 def test_wider_flags(self):self.c['Spec']['linux']['seccomp']['syscalls'][-1]['args'][0]['op']='SCMP_CMP_MASKED_EQ';self.reject()
 def test_default(self):self.c['Spec']['linux']['seccomp']['defaultAction']='SCMP_ACT_ALLOW';self.reject()
 def test_nnp(self):self.c['Spec']['process']['noNewPrivileges']=False;self.reject()
 def test_not_applied(self):self.c['Spec']['linux']['seccomp']['syscalls'].pop();self.reject()
 def test_hook_change(self):self.c['Spec']['hooks']['createRuntime'][0]['path']='/bin/other';self.reject()
if __name__=='__main__':unittest.main(verbosity=2)
