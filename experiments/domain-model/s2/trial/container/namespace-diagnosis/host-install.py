"""Transfer fixed diagnostic helpers and run at most two preparation units."""
import hashlib,json,os,pathlib,subprocess,tarfile
root=pathlib.Path('/tmp/ontosary-s2-namespace-diagnosis-20261111');work=pathlib.Path('work/s2-namespace-diagnosis');base=pathlib.Path('experiments/domain-model/s2/trial/container');src=base/'namespace-diagnosis';os.environ['LIMA_HOME']=str(root/'lima');lima=str(root/'prefix/bin/limactl')
archive=work/'inputs.tar.gz';members={}
files=[(base/'Dockerfile','build/Dockerfile'),(base/'cli-feasibility/policy.toml','policy.toml'),(src/'probe.mjs','probe/probe.mjs'),(src/'guest.py','guest.py'),(src/'export.py','export.py')]+[(p,'lifecycle/'+p.name) for p in (base/'lifecycle').glob('*.py')]
with tarfile.open(archive,'w:gz') as t:
 for p,name in files:t.add(p,arcname=name);members[name]=hashlib.sha256(p.read_bytes()).hexdigest()
(work/'inputs.json').write_text(json.dumps({'archiveSha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'members':members},indent=2)+'\n')
def run(args,timeout=30,check=True):return subprocess.run([lima,*args],check=check,timeout=timeout)
run(['copy',str(archive),'s2-lifecycle:/tmp/s2-namespace-inputs.tar.gz'])
run(['shell','--workdir=/tmp','s2-lifecycle','sudo','mkdir','/opt/ontosary-namespace-diagnosis'])
run(['shell','--workdir=/tmp','s2-lifecycle','sudo','tar','-xzf','/tmp/s2-namespace-inputs.tar.gz','-C','/opt/ontosary-namespace-diagnosis'])
result=run(['shell','--workdir=/tmp','s2-lifecycle','sudo','python3','/opt/ontosary-namespace-diagnosis/guest.py'],650,False)
run(['shell','--workdir=/tmp','s2-lifecycle','sudo','python3','/opt/ontosary-namespace-diagnosis/export.py'])
run(['copy','s2-lifecycle:/tmp/s2-namespace-evidence.tar.gz',str(work/'guest-evidence.tar.gz')])
with tarfile.open(work/'guest-evidence.tar.gz') as t:t.extractall(work/'guest',filter='data')
raise SystemExit(result.returncode)
