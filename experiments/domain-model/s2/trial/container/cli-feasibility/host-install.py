"""Transfer only snapshotted probe/code and pinned image definition into the owned VM."""
import json,os,pathlib,subprocess,tarfile,hashlib
root=pathlib.Path('/tmp/ontosary-s2-cli-feasibility-20261111');work=pathlib.Path('work/s2-cli-feasibility');base=pathlib.Path('experiments/domain-model/s2/trial/container');os.environ['LIMA_HOME']=str(root/'lima');lima=str(root/'prefix/bin/limactl')
archive=work/'preparation-inputs.tar.gz';members={}
with tarfile.open(archive,'w:gz') as t:
 for f,name in [(base/'Dockerfile','build/Dockerfile'),(base/'cli-feasibility/discover.mjs','probe/discover.mjs'),(base/'cli-feasibility/prepare.py','prepare.py')]+[(p,'lifecycle/'+p.name) for p in (base/'lifecycle').glob('*.py')]:
  t.add(f,arcname=name);members[name]=hashlib.sha256(f.read_bytes()).hexdigest()
(work/'preparation-inputs.json').write_text(json.dumps({'archiveSha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'members':members},indent=2)+'\n')
def run(args,timeout=30):subprocess.run([lima,*args],check=True,timeout=timeout)
run(['copy',str(archive),'s2-lifecycle:/tmp/s2-cli-inputs.tar.gz'])
run(['shell','--workdir=/tmp','s2-lifecycle','sudo','mkdir','/opt/ontosary-cli-feasibility'])
run(['shell','--workdir=/tmp','s2-lifecycle','sudo','tar','-xzf','/tmp/s2-cli-inputs.tar.gz','-C','/opt/ontosary-cli-feasibility'])
run(['shell','--workdir=/tmp','s2-lifecycle','sudo','python3','/opt/ontosary-cli-feasibility/prepare.py'],420)
run(['shell','--workdir=/tmp','s2-lifecycle','sudo','tar','-czf','/tmp/s2-cli-preparation.tar.gz','-C','/opt/ontosary-cli-feasibility','preparation','auxiliary','image.json'])
run(['copy','s2-lifecycle:/tmp/s2-cli-preparation.tar.gz',str(work/'preparation.tar.gz')])
with tarfile.open(work/'preparation.tar.gz') as t:t.extractall(work/'preparation',filter='data')
