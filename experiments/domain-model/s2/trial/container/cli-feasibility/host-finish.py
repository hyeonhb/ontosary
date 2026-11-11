"""Run the snapshotted guest cleanup and export only its finite audit."""
import os,pathlib,subprocess,tarfile
root=pathlib.Path('/tmp/ontosary-s2-cli-feasibility-20261111');work=pathlib.Path('work/s2-cli-feasibility');os.environ['LIMA_HOME']=str(root/'lima');lima=str(root/'prefix/bin/limactl')
def run(args,timeout=20):subprocess.run([lima,*args],check=True,timeout=timeout)
run(['copy','experiments/domain-model/s2/trial/container/cli-feasibility/finish.py','s2-lifecycle:/tmp/s2-cli-finish.py'])
run(['shell','--workdir=/tmp','s2-lifecycle','sudo','python3','/tmp/s2-cli-finish.py'],60)
run(['shell','--workdir=/tmp','s2-lifecycle','sudo','tar','-czf','/tmp/s2-cli-removal.tar.gz','-C','/opt/ontosary-cli-feasibility','removal'])
run(['copy','s2-lifecycle:/tmp/s2-cli-removal.tar.gz',str(work/'removal.tar.gz')])
with tarfile.open(work/'removal.tar.gz') as t:t.extractall(work/'removal',filter='data')
