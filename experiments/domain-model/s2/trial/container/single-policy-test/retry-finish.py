"""Remove only the recorded round's owned guest resources, VM, prefix and new caches."""
import argparse,json,pathlib,subprocess,os,shutil,hashlib,time
from deadline import run
p=argparse.ArgumentParser();p.add_argument('--work',required=True);a=p.parse_args();work=pathlib.Path(a.work);budget=json.loads((work/'budget.json').read_text());ownership=json.loads((work/'ownership.json').read_text());root=pathlib.Path(ownership['root']);assert root==pathlib.Path('/tmp/ontosary-s2-policy-retry-20261112')
lima=str(root/'prefix/bin/limactl');env={**os.environ,'LIMA_HOME':str(root/'lima')};base=pathlib.Path(__file__).parent
# New runtime units are forbidden here; guest cleanup only inspects/removes registered units.
def execute(args,check=True):
 r=run(args,budget,'finish',work/'cleanup-commands.jsonl',requested=30,env=env)
 if check:assert r['exitCode']==0,r
 return r
if (work/'inputs.tar.gz').exists():
 execute([lima,'copy',str(base/'retry-remove.py'),'s2-lifecycle:/tmp/policy-remove.py'])
 execute([lima,'shell','--workdir=/tmp','s2-lifecycle','sudo','python3','/tmp/policy-remove.py'])
 execute([lima,'shell','--workdir=/tmp','s2-lifecycle','sudo','tar','-czf','/tmp/policy-removal.tar.gz','-C','/opt/ontosary-policy-retry','removal'])
 execute([lima,'copy','s2-lifecycle:/tmp/policy-removal.tar.gz',str(work/'removal.tar.gz')])
 import tarfile
 with tarfile.open(work/'removal.tar.gz') as t:t.extractall(work/'removal',filter='data')
 assert json.loads((work/'removal/removal/cleanup.json').read_text())['status']=='guest-cleanup-passed'
execute([lima,'stop','--force','s2-lifecycle'],False);execute([lima,'delete','--force','s2-lifecycle'])
listing=subprocess.check_output([lima,'list','--json'],env=env,text=True,timeout=5);assert not listing.strip()
remaining=[x for x in subprocess.check_output(['ps','-axo','pid=,ppid=,command='],text=True).splitlines() if str(root/'prefix') in x or str(root/'lima') in x];assert not remaining,remaining
urls={'274d59968f7fc4016d852a0fa9a95e78a7253670ae8095bcb06076eec1f922f8':'https://cloud-images.ubuntu.com/releases/resolute/release-20261016/ubuntu-26.04-server-cloudimg-arm64.img','975f12320da58d431eba0c59caf918381721d37c81297f52a261383a54420186':'https://github.com/containerd/nerdctl/releases/download/v2.4.2/nerdctl-full-2.4.2-linux-arm64.tar.gz'}
rows=[]
for c in ownership['cache']:
 path=pathlib.Path(c['path']);r=dict(c)
 if not c['existedBefore'] and path.exists():
  url=(path/'url').read_text().strip();assert url==urls[path.name] and hashlib.sha256(url.encode()).hexdigest()==path.name
  data=path/'data'
  if data.exists():
   digest=hashlib.file_digest(data.open('rb'),'sha256').hexdigest();assert digest==c['expectedDataSha256'];r.update(dataSha256=digest,bytes=data.stat().st_size)
  else:
   partial=list(path.glob('data.tmp.*'));assert len(partial)==1;r.update(incomplete=True,partialName=partial[0].name,partialBytes=partial[0].stat().st_size,partialSha256=hashlib.file_digest(partial[0].open('rb'),'sha256').hexdigest())
  shutil.rmtree(path);r['removed']=True
 else:r['removed']=False
 r['existsAfter']=path.exists();rows.append(r)
shutil.rmtree(root);(work/'host-cleanup.json').write_text(json.dumps({'status':'host-cleanup-passed','rootAbsent':not root.exists(),'vmList':listing,'ownedProcessesRemaining':remaining,'cache':rows,'sharedPruneUsed':False,'originalSourceCachePreserved':pathlib.Path('/tmp/ontosary-vendure-preparation-20261108/vendure/package-lock.json').exists()},indent=2)+'\n')
