import copy,json,os,pathlib,tempfile,time,unittest
from unittest.mock import patch
import engine,common,image
from identity import HOOK_ENV,RUNTIME_ENV,SYSTEM_PATH,normalize,Rejected
from runtime_env import validate_env
import test_identity
class RuntimeEnvironmentTests(unittest.TestCase):
 def test_exact_environment_at_subprocess_boundary(self):
  with tempfile.TemporaryDirectory() as tmp:
   run=pathlib.Path(tmp);(run/'state.json').write_text(json.dumps({'deadlines':{'remove':time.monotonic()+3}}))
   class Process:
    pid=999;returncode=0
    def communicate(self,timeout):return b'[]',b''
   with patch.dict(os.environ,{'PATH':'/worker/bin','FOREIGN':'contamination'}),patch.object(common.subprocess,'Popen',return_value=Process()) as popen:
    for name in ['nerdctl','ctr','/usr/local/bin/nerdctl','/usr/local/bin/ctr']:
     engine.command(run,[name,'test']);self.assertEqual(popen.call_args.kwargs['env'],RUNTIME_ENV);self.assertEqual(popen.call_args.args[0][0],'/usr/local/bin/'+pathlib.Path(name).name)
 def test_reject_missing_and_contaminated_environment(self):
  for bad in [{k:v for k,v in RUNTIME_ENV.items() if k!='PATH'},{**RUNTIME_ENV,'FOREIGN':'x'},{**RUNTIME_ENV,'PATH':':'+SYSTEM_PATH},{**RUNTIME_ENV,'PATH':'./bin'}]:
   with self.assertRaises(RuntimeError):validate_env(bad)
 def test_known_hook_duplicate_exact_only(self):
  fixture=test_identity.IdentityTests();fixture.setUp()
  self.assertEqual([x.split('=')[0] for x in HOOK_ENV],['HOME','LANG','PATH','PATH'])
  normalize(fixture.spec[0],fixture.ident[0])
  for env in [HOOK_ENV[:-1],HOOK_ENV+['PATH='+SYSTEM_PATH],HOOK_ENV[:-1]+['PATH=/foreign'],[HOOK_ENV[2],*HOOK_ENV[:2],HOOK_ENV[3]]]:
   n=copy.deepcopy(fixture.spec[0]);n['Spec']['hooks']['poststop'][0]['env']=env
   with self.assertRaises(Rejected):normalize(n,fixture.ident[0])
 def test_security_changes_are_full_spec_differences(self):
  f=test_identity.IdentityTests();f.setUp()
  for change in ['apparmor','rro','cap','network','memory']:
   with self.subTest(change=change):
    n=copy.deepcopy(f.spec[1]);s=n['Spec']
    if change=='apparmor':s['process'].pop('apparmorProfile')
    elif change=='rro':next(m for m in s['mounts'] if m['destination']=='/materials')['options']=['rbind','ro']
    elif change=='cap':s['process']['capabilities']['effective']=['CAP_SYS_ADMIN']
    elif change=='network':s['linux']['namespaces']=[x for x in s['linux']['namespaces'] if x['type']!='network']
    else:s['linux']['resources']['memory']['limit']*=2
    from identity import compare
    self.assertFalse(compare(n,f.spec[0],f.ident[1],f.ident[0],True)['accepted'])
if __name__=='__main__':unittest.main()
