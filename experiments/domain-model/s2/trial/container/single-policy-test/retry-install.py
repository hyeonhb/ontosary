"""Transfer pinned helpers; host authorizes candidate only before both environment clocks expire."""
import argparse,hashlib,json,os,pathlib,subprocess,sys,tarfile
from deadline import run,limit
p=argparse.ArgumentParser();p.add_argument('--work',required=True);a=p.parse_args();work=pathlib.Path(a.work);budget=json.loads((work/'budget.json').read_text());base=pathlib.Path(__file__).parent;container=base.parent
root=pathlib.Path('/tmp/ontosary-s2-policy-retry-20261112');lima=str(root/'prefix/bin/limactl');env={**os.environ,'LIMA_HOME':str(root/'lima')};guest='/opt/ontosary-policy-retry'
archive=work/'inputs.tar.gz';members={}
files=[(work/'Dockerfile','build/Dockerfile'),(container/'cli-feasibility/policy.toml','policy.toml'),(base/'retry-probe.mjs','probe/probe.mjs'),(work/'prior-native.json','prior-native.json'),(work/'budget.json','budget.json')]+[(base/n,n) for n in ['retry-job.py','retry-guest.py','retry-export.py','runtime_policy.py','policy.py','retry-metadata.py']]+[(p,'lifecycle/'+p.name) for p in (container/'lifecycle').glob('*.py')]
with tarfile.open(archive,'w:gz') as t:
 for p,name in files:t.add(p,arcname=name);members[name]=hashlib.sha256(p.read_bytes()).hexdigest()
(work/'inputs.json').write_text(json.dumps({'archiveSha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'members':members},indent=2)+'\n')
def execute(args,phase='environment',check=True):
 r=run([lima,*args],budget,phase,work/'install-commands.jsonl',env=env)
 if check and r['exitCode']:raise RuntimeError('host-stage:'+str(r['exitCode']))
 return r
shell=['shell','--workdir=/tmp','s2-lifecycle','sudo']
try:
 execute(['copy',str(archive),'s2-lifecycle:/tmp/policy-inputs.tar.gz']);execute(shell+['mkdir','-p',guest,'/opt/ontosary-fixture/code']);execute(shell+['tar','-xzf','/tmp/policy-inputs.tar.gz','-C',guest]);execute(shell+['cp','-a',guest+'/lifecycle/.','/opt/ontosary-fixture/code/'])
 execute(shell+['python3',guest+'/retry-guest.py','prepare'])
 # Separate host gate: actual candidate Spec has already passed, neither host clock may be expired.
 remaining=limit(budget,'environment');(work/'candidate-host-authorization.json').write_text(json.dumps({'remainingSeconds':remaining,'absoluteDeadline':budget['deadlines']['environment'],'scope':'candidate prepared but not started'})+'\n')
 execute(shell+['python3','-c',"import json,pathlib; r=pathlib.Path('/opt/ontosary-policy-retry'); p=r/'candidate-authorized.json'; assert not p.exists(); p.write_text((r/'candidate-prepared.json').read_text())"])
 execute(shell+['python3',guest+'/retry-guest.py','collect'],'diagnosis')
finally:
 execute(shell+['python3',guest+'/retry-metadata.py'],'finish',False)
 execute(shell+['python3',guest+'/retry-export.py'],'finish',False)
 execute(['copy','s2-lifecycle:/tmp/s2-policy-retry-evidence.tar.gz',str(work/'guest-evidence.tar.gz')],'finish',False)
 if (work/'guest-evidence.tar.gz').exists():
  with tarfile.open(work/'guest-evidence.tar.gz') as t:t.extractall(work/'guest',filter='data')
