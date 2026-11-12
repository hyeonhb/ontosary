"""One owned Lima preparation; every nested stage inherits the absolute host deadline."""
import argparse,hashlib,json,pathlib,os,tarfile,math,sys
from deadline import run,limit
p=argparse.ArgumentParser();p.add_argument('--work',required=True);a=p.parse_args();work=pathlib.Path(a.work);budget=json.loads((work/'budget.json').read_text());plan=json.loads((work/'plan.json').read_text());assert plan['round']=='2026-11-12-policy-retry'
root=pathlib.Path('/tmp/ontosary-s2-policy-retry-20261112');limit(budget,'environment');root.mkdir(exist_ok=False)
urls=[('274d59968f7fc4016d852a0fa9a95e78a7253670ae8095bcb06076eec1f922f8','8eb876c2ccc4b6ff89e4a65d511815923b285e04503ba465809bf587f763da24'),('975f12320da58d431eba0c59caf918381721d37c81297f52a261383a54420186','fe0ef0e9840ee8932640e6058f84b7fa98050f9726e44af44883a5b804ae830e')]
cache=[{'path':str(pathlib.Path.home()/'Library/Caches/lima/download/by-url-sha256'/u),'expectedDataSha256':h,'existedBefore':(pathlib.Path.home()/'Library/Caches/lima/download/by-url-sha256'/u).exists()} for u,h in urls]
(work/'ownership.json').write_text(json.dumps({'root':str(root),'cache':cache},indent=2)+'\n')
for c in cache:
 if c['existedBefore']:
  limit(budget,'environment');assert hashlib.file_digest((pathlib.Path(c['path'])/'data').open('rb'),'sha256').hexdigest()==c['expectedDataSha256']
def execute(args):
 result=run(args,budget,'environment',work/'preparation-commands.jsonl',env={**os.environ,'LIMA_HOME':str(root/'lima')})
 if result['exitCode']:raise SystemExit(result['exitCode'])
archive=root/'lima.tar.gz';execute(['curl','--fail','--location','--max-time',str(limit(budget,'environment')),'--output',str(archive),'https://github.com/lima-vm/lima/releases/download/v2.3.0/lima-2.3.0-Darwin-arm64.tar.gz'])
limit(budget,'environment');assert hashlib.sha256(archive.read_bytes()).hexdigest()=='b7af444bd8f91d3c307477e562f2cf3bd7595d62b9429185e4fa841563578cfc'
prefix=root/'prefix';prefix.mkdir();execute([sys.executable,'-c','import tarfile,sys; t=tarfile.open(sys.argv[1]); t.extractall(sys.argv[2],filter="data")',str(archive),str(prefix)])
execute([str(prefix/'bin/limactl'),'start','--yes','--name=s2-lifecycle','--timeout='+str(math.ceil(limit(budget,'environment')))+'s','experiments/domain-model/s2/trial/container/lima.yaml'])
