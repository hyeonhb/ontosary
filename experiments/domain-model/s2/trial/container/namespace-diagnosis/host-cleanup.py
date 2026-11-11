"""Remove only this round's owned VM/prefix and newly-created URL/hash-verified cache leaves."""
import hashlib,json,os,pathlib,shutil,subprocess,time
WORK=pathlib.Path('work/s2-namespace-diagnosis');ownership=json.loads((WORK/'ownership.json').read_text());root=pathlib.Path(ownership['root']);assert root==pathlib.Path('/tmp/ontosary-s2-namespace-diagnosis-20261111')
assert json.loads((WORK/'removal/removal/cleanup.json').read_text())['status']=='guest-cleanup-passed'
log=(WORK/'host-cleanup.jsonl').open('x')
def record(value):log.write(json.dumps(value)+'\n');log.flush()
def command(args,timeout=30):
 start=time.monotonic();p=subprocess.run(args,env={**os.environ,'LIMA_HOME':str(root/'lima')},capture_output=True,timeout=timeout);record({'command':args,'seconds':time.monotonic()-start,'exitCode':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode()});p.check_returncode();return p.stdout.decode()
lima=str(root/'prefix/bin/limactl')
command([lima,'stop','--force','s2-lifecycle']);command([lima,'delete','--force','s2-lifecycle']);listing=command([lima,'list','--json']);assert not listing.strip()
processes=subprocess.check_output(['ps','-axo','pid=,ppid=,command='],text=True);remaining=[line for line in processes.splitlines() if str(root/'prefix') in line or str(root/'lima') in line];assert not remaining,remaining
urls={'274d59968f7fc4016d852a0fa9a95e78a7253670ae8095bcb06076eec1f922f8':'https://cloud-images.ubuntu.com/releases/resolute/release-20261016/ubuntu-26.04-server-cloudimg-arm64.img','975f12320da58d431eba0c59caf918381721d37c81297f52a261383a54420186':'https://github.com/containerd/nerdctl/releases/download/v2.4.2/nerdctl-full-2.4.2-linux-arm64.tar.gz'}
rows=[]
for cache in ownership['cache']:
 p=pathlib.Path(cache['path']);row={**cache}
 if not cache['existedBefore'] and p.exists():
  url=(p/'url').read_text().strip();assert url==urls[p.name] and hashlib.sha256(url.encode()).hexdigest()==p.name
  h=hashlib.sha256()
  with (p/'data').open('rb') as f:
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
  assert h.hexdigest()==cache['expectedDataSha256'];row.update(url=url,dataSha256=h.hexdigest(),bytes=(p/'data').stat().st_size)
  shutil.rmtree(p);row['removed']=True
 else:row['removed']=False
 row['existsAfter']=p.exists();rows.append(row)
shutil.rmtree(root)
result={'status':'host-cleanup-passed','vmList':listing,'ownedProcessesRemaining':remaining,'root':str(root),'rootAbsent':not root.exists(),'cache':rows,'sharedPruneUsed':False,'originalSourceCachePreserved':pathlib.Path('/tmp/ontosary-vendure-preparation-20261108/vendure/package-lock.json').exists()}
(WORK/'host-cleanup.json').write_text(json.dumps(result,indent=2)+'\n');record(result);print(json.dumps(result))
