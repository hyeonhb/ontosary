"""One bounded, explicitly planned round. No model/auth/provider operations."""
import argparse,copy,datetime,hashlib,io,json,os,pathlib,signal,shutil,subprocess,sys,tarfile,tempfile,time,urllib.request
HERE=pathlib.Path(__file__).resolve().parent;CONTAINER=HERE.parent
sys.path[:0]=[str(HERE),str(CONTAINER/'single-policy-test')]
from deadline import run,limit
from artifacts import Store,download,verify_image_archive
from scope import rows,registered_scope,inventory,verify_index
from snapshot import snapshot
from package import package
sha=lambda p:hashlib.file_digest(pathlib.Path(p).open('rb'),'sha256').hexdigest()
def read(p):return json.loads(pathlib.Path(p).read_text())
def write(p,v):pathlib.Path(p).write_text(json.dumps(v,indent=2)+'\n')

class Round:
 def __init__(self,work):
  self.w=pathlib.Path(work);self.plan=read(self.w/'plan.json');self.budget=read(self.w/'budget.json');self.root=pathlib.Path(self.plan['vmRoot']);self.env={**os.environ,'LIMA_HOME':str(self.root/'lima')};self.lima=str(self.root/'prefix/bin/limactl');self.shell=[self.lima,'shell','--workdir=/tmp',self.plan['vmName'],'sudo'];self.phase='finish';self.counter=0;self.invocation=str(time.time_ns())
 def cmd(self,args,timeout=None,check=True):
  self.counter+=1;path=self.w/(self.action+'-'+self.invocation+'-command-'+str(self.counter)+'.log')
  with path.open('x') as log:r=run(args,self.budget,self.phase,self.w/'stage-commands.jsonl',timeout,stdout=log,env=self.env)
  if check and r['exitCode']:raise RuntimeError('stage-command:'+str(r['exitCode'])+':'+str(path))
  return r,path.read_text()
 def guest(self,args,**kw):return self.cmd(self.shell+args,**kw)
 def local(self):
  self.phase='plan';results=[];write(self.w/'local-gate.json',{'passed':False,'status':'running'})
  for directory,pattern in [('execution-lifecycle','test_*.py'),('lifecycle','test_*.py'),('single-policy-test','test_retry*.py')]:
   r,output=self.cmd([sys.executable,'-m','unittest','discover','-s',str(CONTAINER/directory),'-p',pattern,'-v'],60);results.append({'directory':directory,'pattern':pattern,'exitCode':r['exitCode'],'log':output[-500:]})
  write(self.w/'local-gate.json',{'passed':True,'results':results,'completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'remainingPlanSeconds':limit(self.budget,'plan'),'codeHashes':{str(p):sha(p) for directory in [HERE,CONTAINER/'lifecycle',CONTAINER/'single-policy-test'] for p in directory.iterdir() if p.is_file() and p.suffix in ['.py','.mjs','.toml']}})
 def enter_preparation(self):
  gate=read(self.w/'local-gate.json');assert gate['passed'];limit(self.budget,'plan')
  assert all(sha(p)==h for p,h in gate['codeHashes'].items()),'code-changed-since-local-gate'
  assert 'environment' not in self.budget['deadlines'],'environment-already-entered'
  now=datetime.datetime.now(datetime.timezone.utc);mono=time.monotonic();utc=min(now+datetime.timedelta(minutes=20),datetime.datetime.fromisoformat(self.budget['deadlines']['preparation']['utc']));end=min(mono+1200,self.budget['deadlines']['preparation']['monotonic'])
  self.budget['deadlines']['environment']={'utc':utc.isoformat(),'monotonic':end};self.budget['environmentEntered']={'utc':now.isoformat(),'mono':mono};write(self.w/'budget.json',self.budget)
 def prepare(self):
  gate=read(self.w/'local-gate.json');assert gate['passed'];limit(self.budget,'plan')
  assert all(sha(p)==h for p,h in gate['codeHashes'].items()),'code-changed-since-local-gate'
  self.phase='environment';end=self.budget['deadlines']['environment']['monotonic'];mono=self.budget['environmentEntered']['mono'];limit(self.budget,'environment')
  assert not self.root.exists(),'owned-root-already-exists';write(self.w/'ownership.json',{'root':str(self.root),'vmName':self.plan['vmName'],'store':self.plan['store'],'storeExistedBefore':pathlib.Path(self.plan['store']).exists(),'ownedRootPlannedBeforeCreation':True,'vmRegistrations':0});self.root.mkdir(mode=0o700)
  store=Store(self.plan['store'],owner_tag=self.plan['round']);requests=[{'name':'lima-2.3.0-Darwin-arm64','url':'https://github.com/lima-vm/lima/releases/download/v2.3.0/lima-2.3.0-Darwin-arm64.tar.gz','sha256':'b7af444bd8f91d3c307477e562f2cf3bd7595d62b9429185e4fa841563578cfc','maximumBytes':55000000,'version':'2.3.0','platform':'darwin/arm64','buildInputHashes':{}},{'name':'ubuntu-26.04-20261016-arm64','url':'https://cloud-images.ubuntu.com/releases/resolute/release-20261016/ubuntu-26.04-server-cloudimg-arm64.img','sha256':'8eb876c2ccc4b6ff89e4a65d511815923b285e04503ba465809bf587f763da24','bytes':940373504,'version':'26.04-20261016','platform':'linux/arm64','buildInputHashes':{}},{'name':'nerdctl-full-2.4.2-linux-arm64','url':'https://github.com/containerd/nerdctl/releases/download/v2.4.2/nerdctl-full-2.4.2-linux-arm64.tar.gz','sha256':'fe0ef0e9840ee8932640e6058f84b7fa98050f9726e44af44883a5b804ae830e','bytes':270513423,'version':'2.4.2','platform':'linux/arm64','buildInputHashes':{}}]
  records=[]
  for req in requests:
   start=time.monotonic();record=store.acquire(req,download(req,end),end);record['firstUseSeconds']=time.monotonic()-start;records.append(record);write(self.w/'artifact-acquisitions.json',records)
  second=[]
  for req in requests:
   start=time.monotonic();r=store.lookup(req,end);assert r;second.append({**r,'reuseSeconds':time.monotonic()-start,'downloads':0,'builds':0})
  write(self.w/'artifact-reuse.json',second)
  prefix=self.root/'prefix';prefix.mkdir()
  self.cmd([sys.executable,'-c','import tarfile,sys;tarfile.open(sys.argv[1]).extractall(sys.argv[2],filter="data")',records[0]['path'],str(prefix)])
  text=(CONTAINER/'lima.yaml').read_text().replace(requests[1]['url'],records[1]['path'])
  text=text.replace('  system: true','  archives:\n    - location: '+records[2]['path']+'\n      arch: aarch64\n      digest: sha256:'+requests[2]['sha256']+'\n  system: true');config=self.root/'lima.yaml';config.write_text(text);write(self.w/'vm-config.json',{'text':text,'sha256':sha(config),'noUserCacheMutation':True})
  ownership=read(self.w/'ownership.json');ownership['vmRegistrations']=1;write(self.w/'ownership.json',ownership)
  self.cmd([self.lima,'start','--yes','--name='+self.plan['vmName'],'--timeout='+str(int(limit(self.budget,'environment')))+'s',str(config)])
  clock_start=datetime.datetime.now(datetime.timezone.utc);clock_mono=time.monotonic()
  _,clock_text=self.guest(['python3','-c','import datetime,time,json;print(json.dumps({"utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"guestMonotonic":time.monotonic()}))'],timeout=3)
  clock= json.loads(clock_text);clock_end=datetime.datetime.now(datetime.timezone.utc);guest_utc=datetime.datetime.fromisoformat(clock['utc'])
  assert clock_start-datetime.timedelta(seconds=1)<=guest_utc<=clock_end+datetime.timedelta(seconds=1),'guest-clock-offset'
  write(self.w/'clock-calibration.json',{'hostBeforeUtc':clock_start.isoformat(),'hostAfterUtc':clock_end.isoformat(),'hostRoundTripSeconds':time.monotonic()-clock_mono,'guest':clock,'registrationTransportReserveSeconds':6,'maximumRegistrationCommandSeconds':5,'monotonicClocksCompared':False})
  # Exact old build recipe; package/binary outputs still have to match before policy start.
  docker=(CONTAINER/'Dockerfile').read_text()+'\nUSER 0:0\nRUN apt-get update && apt-get install -y --no-install-recommends strace && dpkg-query -W strace > /opt/namespace-package.txt && rm -rf /var/lib/apt/lists/*\nUSER 1000:1000\n'
  (self.w/'Dockerfile').write_text(docker)
  inputs={name:sha(p) for name,p in [('probe',CONTAINER/'single-policy-test/retry-probe.mjs'),('fixture',HERE/'fixture.mjs'),('policy',CONTAINER/'cli-feasibility/policy.toml'),('recipe',self.w/'Dockerfile')]};write(self.w/'inputs.json',inputs)
  files=[(p,'execution-lifecycle/'+p.name) for p in HERE.glob('*.py') if not p.name.startswith(('test_','fixture_'))]+[(p,'lifecycle/'+p.name) for p in (CONTAINER/'lifecycle').glob('*.py')]+[(self.w/'Dockerfile','build/Dockerfile'),(CONTAINER/'single-policy-test/retry-probe.mjs','probe/probe.mjs'),(HERE/'fixture.mjs','probe/fixture.mjs'),(CONTAINER/'cli-feasibility/policy.toml','policy.toml')]+[(self.w/n,n) for n in ['budget.json','prior-pair.json','inputs.json']]
  with tarfile.open(self.w/'inputs.tar.gz','w:gz') as t:
   for p,name in files:t.add(p,arcname=name)
  write(self.w/'input-transfer.json',{'archiveSha256':sha(self.w/'inputs.tar.gz'),'members':{n:sha(p) for p,n in files}})
  self.cmd([self.lima,'copy',str(self.w/'inputs.tar.gz'),self.plan['vmName']+':/tmp/execution-inputs.tar.gz'])
  self.guest(['mkdir','-p','/opt/ontosary-execution']);self.guest(['tar','-xzf','/tmp/execution-inputs.tar.gz','-C','/opt/ontosary-execution'])
  self.guest(['python3','/opt/ontosary-execution/execution-lifecycle/guest.py','prepare'])
  _,output=self.guest(['cat','/opt/ontosary-execution/image-export.json']);export= json.loads(output)
  image_request={'name':'ontosary-fixed-trace-image','url':'local-build:fixed-public-inputs','version':'codex-0.167.0-alpha.3.2-node-22.19.0-strace','platform':'linux/arm64','bytes':export['bytes'],'sha256':export['sha256'],'image':export['image'],'buildInputHashes':{**inputs,'baseImage':'sha256:4a4884e8a44826194dff92ba316264f392056cbe243dcc9fd3551e71cea02b90'}}
  def producer(sink):
   args=self.shell+['cat','/opt/ontosary-execution/image.tar'];p=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,env=self.env)
   try:
    while True:
     b=p.stdout.read(1024*1024)
     if not b:break
     sink(b)
    if p.wait(timeout=max(.01,end-time.monotonic())):raise RuntimeError('image-copy-failed')
   finally:
    if p.poll() is None:p.kill();p.wait()
  start=time.monotonic();first=store.acquire(image_request,producer,end);verified=verify_image_archive(first['path'],export['image'],end);second_image=store.lookup(image_request,end)
  write(self.w/'image-artifact.json',{'first':first,'archiveVerification':verified,'second':second_image,'secondDownloads':0,'secondBuilds':0,'seconds':time.monotonic()-start})
  self.cmd([self.lima,'copy',second_image['path'],self.plan['vmName']+':/tmp/reused-image.tar']);self.guest(['mv','/tmp/reused-image.tar','/opt/ontosary-execution/reused-image.tar']);self.guest(['python3','/opt/ontosary-execution/execution-lifecycle/guest.py','import'])
  write(self.w/'preparation-complete.json',{'seconds':time.monotonic()-mono,'storeBytes':store.usage(),'actualImage':export['image'],'vmRegistrations':1,'workUnits':0,'environmentRemainingSeconds':limit(self.budget,'environment')})
 def engine(self,args,timeout=3):
  _,out=self.guest(['python3','/opt/ontosary-execution/execution-lifecycle/engine.py',*args],timeout=timeout);return json.loads(out) if out.strip() else None
 def unit(self,mode):
  assert limit(self.budget,'exploration')>=120
  registry=read(self.w/'units.json') if (self.w/'units.json').exists() else []
  assert mode not in [x['mode'] for x in registry] and len(registry)<9
  row={'mode':mode,'requestAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hostStartedMono':time.monotonic()};registry.append(row);write(self.w/'units.json',registry)
  log=(self.w/(mode+'-driver.log')).open('x');driver=subprocess.Popen([sys.executable,str(HERE/'driver.py'),str(self.w),mode],stdout=log,stderr=subprocess.STDOUT);row['wrapperPid']=driver.pid;write(self.w/'units.json',registry);injected=False;rid=None;state=None
  try:
   while time.monotonic()-row['hostStartedMono']<120:
    registration=self.w/(mode+'-registration.json')
    if registration.exists():
     rid=read(registration)['runId'];row['runId']=rid
     state=self.engine(['status',rid]);write(self.w/(mode+'-observed.json'),state)
     if state.get('ready') and 'readyObservedHostMono' not in row:row['readyObservedHostMono']=time.monotonic()
     if state.get('ready') and not injected and mode in ['wrapper-death','supervisor-death']:
      row['faultRequestedAtMono']=time.monotonic();write(self.w/'units.json',registry)
      if mode=='wrapper-death':driver.kill();driver.wait(timeout=2)
      else:self.guest(['systemctl','kill','--kill-whom=main','--signal=SIGKILL',state['service']],timeout=3)
      injected=True
     if state.get('serviceInactiveConfirmed') or state.get('discardVM'):break
    elif driver.poll() is not None:raise RuntimeError('wrapper-failed-before-registration')
    time.sleep(.2)
   else:raise RuntimeError('unit-120-second-deadline')
   assert state and state.get('serviceInactiveConfirmed') and state.get('removalConfirmed') and state.get('terminationConfirmed') and not any(state.get(k) for k in ['createPending','startPending','execPending']),state
   expected={'normal-1':'exit','precheck-rejection':'precheck-rejected','start-failure':'start-failed','timeout':'timeout','wrapper-death':'wrapper-death','supervisor-death':'supervisor-death','normal-2':'exit','baseline':'exit','candidate':'exit'}[mode]
   assert state['outcome']==expected,(mode,state)
   if mode in ['normal-1','normal-2','baseline','candidate']:assert state['exitCode']==0
   if mode=='precheck-rejection':assert state['starts']==0
   if mode=='supervisor-death':assert state['collectionStatus']=='suppressed';assert not read(self.w/(mode+'-observed.json')).get('result')
   if mode in ['timeout','wrapper-death','supervisor-death']:
    # Cross the worker's advertised 20s late-write timer; no sleep-based fault injection.
    assert state.get('ready') and 'readyObservedHostMono' in row,'ready-signal-missing'
    wait=max(0,row['readyObservedHostMono']+22-time.monotonic())
    if wait:time.sleep(min(wait,22))
    _,late=self.guest(['python3','-c',"import pathlib,sys,json;p=pathlib.Path('/opt/ontosary-fixture/runs')/sys.argv[1];print(json.dumps({'lateExists':(p/'source/late-write.txt').exists(),'lastWrite':(p/'auxiliary/writes.jsonl').stat().st_mtime_ns if (p/'auxiliary/writes.jsonl').exists() else None}))",rid],timeout=3);assert not json.loads(late)['lateExists'];row['lateWriteCheck']=json.loads(late);assert row['lateWriteCheck']['lastWrite']==state.get('lastWriteMtimeNs'),'writes-after-removal'
   if mode in ['normal-1','normal-2','timeout','wrapper-death']:
    _,raw=self.guest(['cat','/opt/ontosary-fixture/runs/'+rid+'/result/auxiliary/fixture-observations.json'],timeout=3);observed=json.loads(raw)
    assert all(observed['positive'].values()) and all(observed['isolation'].values()) and observed['uid']==1000 and observed['gid']==1000
    assert 'NoNewPrivs:\t1' in observed['status'] and 'CapEff:\t0000000000000000' in observed['status'] and 'nerdctl-default (enforce)' in observed['apparmor']
    assert observed['nodeVersion']=='v22.19.0' and observed['binaries']=={'codex':'e7f91e14eab4ba3a0f65047c1757b593409d4ce791ccb6ac65c67c970dfed76f','bwrap':'0f543a7356ab343b4827222f910461d4196778f328b28acd6c126ef18e9557ab'}
    if mode=='normal-2':assert observed['priorPathCount']>=24
    row['workerObservations']=observed
   if state['recoveryRequired']:self.engine(['recover',rid]);row['explicitRecovery']=True
   row.update(passed=True,outcome=state['outcome'],state=state,seconds=time.monotonic()-row['hostStartedMono'],faultInjected=injected);assert row['seconds']<120;write(self.w/'units.json',registry)
   return rid
  except Exception as exc:row.update(passed=False,error=str(exc),seconds=time.monotonic()-row['hostStartedMono']);write(self.w/'units.json',registry);raise
  finally:
   if driver.poll() is None:
    try:driver.wait(timeout=3)
    except subprocess.TimeoutExpired:driver.kill();driver.wait(timeout=2)
   log.close()
 def fixtures(self):
  self.phase='exploration';assert (self.w/'preparation-complete.json').exists()
  for mode in self.plan['fixtures']:self.unit(mode)
  write(self.w/'fixtures-complete.json',{'passed':True,'requiredUnits':7,'optionalRuntimeFailureFixture':False})
 def pair(self):
  self.phase='exploration';assert read(self.w/'fixtures-complete.json')['passed']
  rid=self.unit('baseline');_,raw=self.guest(['cat','/opt/ontosary-fixture/runs/'+rid+'/result/auxiliary/result.json']);baseline=json.loads(raw);write(self.w/'baseline-observation.json',baseline)
  assert all(baseline['parent'].values()) and not baseline['nativePayloadStarted'] and baseline['nodeVersion']=='v22.19.0'
  assert baseline['calls'][0]['stdout']=='codex-cli 0.167.0-alpha.3.2\n'
  assert baseline['binaries']['codex']['sha256']=='e7f91e14eab4ba3a0f65047c1757b593409d4ce791ccb6ac65c67c970dfed76f' and baseline['binaries']['bwrap']['sha256']=='0f543a7356ab343b4827222f910461d4196778f328b28acd6c126ef18e9557ab'
  assert baseline['calls'][-1]['stderr'].count('clone(child_stack=NULL, flags=CLONE_NEWNS|CLONE_NEWIPC|CLONE_NEWUSER|CLONE_NEWPID|CLONE_NEWNET|SIGCHLD) = -1 EPERM')==2
  self.guest(['python3','-c',"import sys,pathlib,json,os;sys.path.insert(0,'/opt/ontosary-execution/execution-lifecycle');from identity import RULE;p=pathlib.Path('/opt/ontosary-execution');s=json.loads((p/'baseline-native.json').read_text())['Spec']['linux']['seccomp'];s['syscalls'].append(RULE);f=p/'candidate.json';f.write_text(json.dumps(s));os.chmod(f,0o400)"])
  rid=self.unit('candidate');_,raw=self.guest(['cat','/opt/ontosary-fixture/runs/'+rid+'/result/auxiliary/result.json']);write(self.w/'candidate-observation.json',json.loads(raw))
 def cleanup(self):
  self.phase='finish'
  if not (self.w/'ownership.json').exists():write(self.w/'cleanup.json',{'vmCreated':False,'rootAbsent':not self.root.exists(),'storeRetained':False});return
  owner=read(self.w/'ownership.json');assert owner['root']==str(self.root) and self.root.name=='ontosary-s2-execution-lifecycle-20261114'
  if pathlib.Path(self.lima).exists():
   if owner['vmRegistrations'] and (self.root/'lima'/self.plan['vmName']).exists():
    self.guest(['python3','/opt/ontosary-execution/execution-lifecycle/guest.py','export'],timeout=10,check=False)
    self.cmd([self.lima,'copy',self.plan['vmName']+':/tmp/s2-execution-evidence.tar.gz',str(self.w/'guest-evidence.tar.gz')],timeout=15,check=False)
    self.cmd([self.lima,'stop','--force',self.plan['vmName']],timeout=30,check=False)
    self.cmd([self.lima,'delete','--force',self.plan['vmName']],timeout=30)
   _,listing=self.cmd([sys.executable,'-c','import subprocess,sys,json;p=subprocess.run([sys.argv[1],"list","--json"],capture_output=True,text=True,timeout=8);print(json.dumps({"exitCode":p.returncode,"stdout":p.stdout,"stderr":p.stderr}))',self.lima],timeout=10)
   listing= json.loads(listing);write(self.w/'lima-final-listing.json',listing)
   assert listing['exitCode']==0 and not listing['stdout'].strip() and not (self.root/'lima'/self.plan['vmName']).exists()
   processes=subprocess.check_output(['ps','-axo','pid=,ppid=,command='],text=True);remaining=[x for x in processes.splitlines() if str(self.root/'prefix') in x or str(self.root/'lima') in x];assert not remaining,remaining
  shutil.rmtree(self.root)
  store=Store(self.plan['store'],owner_tag=self.plan['round']);pending_removed=store.cleanup_pending(time.monotonic()+10);write(self.w/'cleanup.json',{'vmCreated':bool(owner['vmRegistrations']),'vmAbsent':True,'rootAbsent':not self.root.exists(),'dedicatedStore':self.plan['store'],'ownedTemporaryRemoved':pending_removed,'retainedBytes':store.usage(),'retainedEntries':[p.name for p in store.root.iterdir() if not p.name.startswith('.')],'temporaryEntries':[p.name for p in store.root.iterdir() if p.name.startswith('.pending-')],'existingUserCacheModified':False,'vmDisposalIsNotUnitTerminationProof':True})
 def validate(self):
  self.phase='finish';result={}
  for name,args in [('pnpm-check',['pnpm','check']),('examples-build',['pnpm','example:build']),('production-live-refusal',['pnpm','exec','vitest','run','tests/s2-lifecycle.test.ts']),('saved-evidence-replay',[sys.executable,str(HERE/'verify_saved.py'),'--work',str(self.w)]),('new-tests',[sys.executable,'-m','unittest','discover','-s',str(HERE),'-p','test_*.py','-v']),('lifecycle-tests',[sys.executable,'-m','unittest','discover','-s',str(CONTAINER/'lifecycle'),'-p','test_*.py','-v']),('audit-tests',[sys.executable,'-m','unittest','discover','-s',str(CONTAINER/'single-policy-test'),'-p','test_retry*.py','-v'])]:
   r,output=self.cmd(args,180,False);result[name]={'exitCode':r['exitCode'],'tail':output[-600:]}
  initial=read(self.w/'start-inventory.json');changed=[];unchanged=0
  # Initial inventory supports both flat hash rows and {sha256,bytes} rows.
  for name,expected in initial.items():
   p=pathlib.Path(name);wanted=expected.get('sha256') if isinstance(expected,dict) else expected
   if not p.exists() or sha(p)!=wanted:
    if not any(name==a or (a.endswith('/') and name.startswith(a)) for a in self.plan['mutableScope']):raise RuntimeError('immutable-input-changed:'+name)
    changed.append(name)
   else:unchanged+=1
  write(self.w/'validation.json',{'checks':result,'unchangedTrackedFiles':unchanged,'intentionalChangedFiles':changed,'priorCacheRestored':False})
 def seal(self):
  self.phase='finish';registered_scope(self.w);assert (self.w/'cleanup.json').exists() and (self.w/'validation.json').exists()
  now=datetime.datetime.now(datetime.timezone.utc);mono=time.monotonic();seconds=mono-self.budget['monotonic'];assert limit(self.budget,'finish')>10
  units=read(self.w/'units.json') if (self.w/'units.json').exists() else []
  cost={'status':'closed','startedUtc':self.budget['utc'],'measuredUntilUtc':now.isoformat(),'roundMeasuredSeconds':seconds,'previousMeasuredSeconds':self.budget['previousMeasuredSeconds'],'cumulativeMeasuredSeconds':self.budget['previousMeasuredSeconds']+seconds,'previousSerializationUpperBoundSeconds':10,'currentSerializationUpperBoundSeconds':10,'cumulativeUpperBoundSeconds':self.budget['previousMeasuredSeconds']+seconds+20,'newPaidCost':0,'gitDeliveryIncluded':False,'actualUnits':len(units),'passedUnits':sum(x.get('passed',False) for x in units),'runtimeRetries':0}
  write(self.w/'cost.json',cost)
  report=pathlib.Path('docs/reviews/2026-11-14-s2-execution-lifecycle.md');report.write_text(report.read_text().replace('ROUND_SECONDS',f'{seconds:.3f}').replace('CUMULATIVE_SECONDS',f'{cost["cumulativeMeasuredSeconds"]:.3f}'))
  result=package(self.w,self.plan['output']);from verify_saved import verify as verify_semantics;verify_semantics(pathlib.Path(self.plan['output'])/'host')
  index=read(pathlib.Path(self.plan['output'])/'index.json');report.write_text(report.read_text().replace('EVIDENCE_FILES',str(len(index['files']))).replace('ARCHIVES',str(len(index['archives']))).replace('ARCHIVE_MEMBERS',str(sum(len(x) for x in index['archives'].values()))))
  import re,urllib.parse
  links=0
  for path in [pathlib.Path(n) for n in ['docs/PROGRESS.md','docs/ARCHITECTURE.md','docs/ROADMAP.md','docs/DECISIONS.md','docs/reviews/REVIEW_CONTEXT.md']]+[report,HERE/'README.md',CONTAINER/'single-policy-test/README.md']:
   for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
    if target.startswith(('https:','http:','#','mailto:')):continue
    target=urllib.parse.unquote(target.split('#')[0]);assert (path.parent/target).exists(),(str(path),target);links+=1
  print(json.dumps({'index':result,'verification':verify_index(pathlib.Path(self.plan['output'])),'localLinks':links,'serializationActualSeconds':time.monotonic()-mono}));assert time.monotonic()-mono<10

def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['local','enter-preparation','prepare','fixtures','pair','cleanup','validate','seal']);p.add_argument('--work',required=True);a=p.parse_args();r=Round(a.work);r.action=a.action
 if a.action in ['local','enter-preparation','prepare','fixtures','pair'] and (r.w/'analysis-scope.json').exists():raise RuntimeError('analysis-frozen')
 if a.action=='seal':snapshot(r.w,['python3',str(HERE/'round.py'),'seal','--work',str(r.w)],'finish','closing')
 getattr(r,a.action.replace('-','_'))()
if __name__=='__main__':main()
