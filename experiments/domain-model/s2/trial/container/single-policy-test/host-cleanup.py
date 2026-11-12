"""Remove only this round's owned VM/prefix and newly-created URL/hash-verified cache leaves."""
import hashlib,json,os,pathlib,shutil,subprocess,time
WORK=pathlib.Path('work/s2-single-policy-test');ownership=json.loads((WORK/'ownership.json').read_text());root=pathlib.Path(ownership['root']);assert root==pathlib.Path('/tmp/ontosary-s2-single-policy-test-20261112')
budget=json.loads((WORK/'budget.json').read_text());assert any(e['exitCode']==124 and e['command'][-1].endswith('/host-prepare.py') for e in budget['events'])
assert not (WORK/'inputs.tar.gz').exists(), 'guest-execution-requires-separate-cleanup'
log=(WORK/'host-cleanup.jsonl').open('x')
def record(value):log.write(json.dumps(value)+'\n');log.flush()
def command(args,timeout=30):
 start=time.monotonic();p=subprocess.run(args,env={**os.environ,'LIMA_HOME':str(root/'lima')},capture_output=True,timeout=timeout);record({'command':args,'seconds':time.monotonic()-start,'exitCode':p.returncode,'stdout':({'name':json.loads(p.stdout)['name'],'status':json.loads(p.stdout)['status']} if args[-2:]==['list','--json'] and p.stdout.strip() else p.stdout.decode()),'stderr':p.stderr.decode()});p.check_returncode();return p.stdout.decode()
lima=str(root/'prefix/bin/limactl')
before=json.loads(command([lima,'list','--json']));assert before['name']=='s2-lifecycle' and before['status']=='Stopped'
vmroot=root/'lima/s2-lifecycle';initialFiles=sorted(p.name for p in vmroot.iterdir());assert not any(n in initialFiles for n in ['basedisk','diffdisk','ha.pid','ha.stderr.log'])
command([lima,'delete','--force','s2-lifecycle']);listing=command([lima,'list','--json']);assert not listing.strip()
processes=subprocess.check_output(['ps','-axo','pid=,ppid=,command='],text=True);remaining=[line for line in processes.splitlines() if str(root/'prefix') in line or str(root/'lima') in line];assert not remaining,remaining
urls={'274d59968f7fc4016d852a0fa9a95e78a7253670ae8095bcb06076eec1f922f8':'https://cloud-images.ubuntu.com/releases/resolute/release-20261016/ubuntu-26.04-server-cloudimg-arm64.img','975f12320da58d431eba0c59caf918381721d37c81297f52a261383a54420186':'https://github.com/containerd/nerdctl/releases/download/v2.4.2/nerdctl-full-2.4.2-linux-arm64.tar.gz'}
rows=[]
for cache in ownership['cache']:
 p=pathlib.Path(cache['path']);row={**cache}
 if not cache['existedBefore'] and p.exists():
  url=(p/'url').read_text().strip();assert url==urls[p.name] and hashlib.sha256(url.encode()).hexdigest()==p.name
  data=p/'data'
  if data.exists():
   h=hashlib.file_digest(data.open('rb'),'sha256').hexdigest();assert h==cache['expectedDataSha256'];row.update(dataSha256=h,bytes=data.stat().st_size)
  else:
   partials=list(p.glob('data.tmp.*'));assert len(partials)==1 and partials[0].name=='data.tmp.54244.1'
   assert set(x.name for x in p.iterdir())=={'url','time','type',partials[0].name}
   row.update(incomplete=True,partialName=partials[0].name,partialSha256=hashlib.file_digest(partials[0].open('rb'),'sha256').hexdigest(),partialBytes=partials[0].stat().st_size,ownershipBasis='absent before sole Lima startup; exact URL directory and exclusive temporary downloader PID; no completed data')
  shutil.rmtree(p);row['removed']=True
 else:row['removed']=False
 row['existsAfter']=p.exists();rows.append(row)
shutil.rmtree(root)
result={'status':'host-cleanup-passed','vmBefore':'Stopped','prebootFiles':initialFiles,'guestBoots':0,'containersCreated':0,'runtimeTerminationClaim':False,'vmList':listing,'ownedProcessesRemaining':remaining,'root':str(root),'rootAbsent':not root.exists(),'cache':rows,'sharedPruneUsed':False,'originalSourceCachePreserved':pathlib.Path('/tmp/ontosary-vendure-preparation-20261108/vendure/package-lock.json').exists()}
(WORK/'host-cleanup.json').write_text(json.dumps(result,indent=2)+'\n');record(result);print(json.dumps(result))
