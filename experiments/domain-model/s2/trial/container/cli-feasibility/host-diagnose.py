"""Transfer only the fixed local blocker diagnosis; collect no CLI state directory."""
import hashlib,json,os,pathlib,subprocess,tarfile
root=pathlib.Path('/tmp/ontosary-s2-cli-feasibility-20261111');work=pathlib.Path('work/s2-cli-feasibility');base=pathlib.Path('experiments/domain-model/s2/trial/container/cli-feasibility');os.environ['LIMA_HOME']=str(root/'lima');lima=str(root/'prefix/bin/limactl')
archive=work/'diagnosis-inputs.tar.gz';members={}
with tarfile.open(archive,'w:gz') as t:
 for name,destination in [('diagnose.mjs','probe/diagnose.mjs'),('diagnose.py','diagnose.py'),('policy.toml','policy.toml')]:
  f=base/name;t.add(f,arcname=destination);members[destination]=hashlib.sha256(f.read_bytes()).hexdigest()
(work/'diagnosis-inputs.json').write_text(json.dumps({'archiveSha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'members':members},indent=2)+'\n')
def run(args,timeout=20):subprocess.run([lima,*args],check=True,timeout=timeout)
run(['copy',str(archive),'s2-lifecycle:/tmp/s2-cli-diagnosis-inputs.tar.gz'])
run(['shell','--workdir=/tmp','s2-lifecycle','sudo','tar','-xzf','/tmp/s2-cli-diagnosis-inputs.tar.gz','-C','/opt/ontosary-cli-feasibility'])
run(['shell','--workdir=/tmp','s2-lifecycle','sudo','python3','/opt/ontosary-cli-feasibility/diagnose.py'],90)
run(['shell','--workdir=/tmp','s2-lifecycle','sudo','tar','-czf','/tmp/s2-cli-diagnosis.tar.gz','-C','/opt/ontosary-cli-feasibility','diagnosis','diagnostic-input/auxiliary','diagnostic-input/source'])
run(['copy','s2-lifecycle:/tmp/s2-cli-diagnosis.tar.gz',str(work/'diagnosis.tar.gz')])
with tarfile.open(work/'diagnosis.tar.gz') as t:t.extractall(work/'diagnosis',filter='data')
