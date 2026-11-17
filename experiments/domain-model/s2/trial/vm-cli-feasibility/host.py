"""Bounded one-shot direct VM experiment. Run only the explicit frozen plan."""
# Unexecuted draft: this round missed its preparation gate. No runtime entry is authorized.
if __name__ == "__main__":
 raise SystemExit("inconclusive: preparation gate missed; runtime draft disabled")
import argparse,datetime,hashlib,json,os,pathlib,shutil,signal,subprocess,sys,tarfile,time,uuid
HERE=pathlib.Path(__file__).resolve().parent;CONTAINER=HERE.parent/'container'
sys.path[:0]=[str(HERE),str(CONTAINER/'single-policy-test'),str(CONTAINER/'execution-lifecycle')]
from deadline import run as bounded_run,limit
from artifacts import Store
from recovery import verify_pair
from materialize import extract
from checks import check
def read(p):return json.loads(pathlib.Path(p).read_text())
def write(p,v):pathlib.Path(p).write_text(json.dumps(v,indent=2)+'\n')
def sha(p):
 with pathlib.Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
class Blocked(RuntimeError):pass

def finish_despite_failure(work,cleanup):
 """Evidence failure must never suppress the independent disposal attempt."""
 errors=[];value=None
 try:value=work()
 except Exception as e:errors.append({'phase':'work','error':str(e)})
 finally:
  try:cleanup()
  except Exception as e:errors.append({'phase':'cleanup','error':str(e)})
 return value,errors

class Runner:
 def __init__(self,w,index=1):
  self.w=pathlib.Path(w).resolve();self.plan=read(self.w/'plan.json');self.budget=read(self.w/'budget.json');self.index=index;self.root=pathlib.Path(self.plan['rootPrefix']+'-'+str(index));self.name='ontosary-vm-cli-'+str(index);self.lima=str(self.root/'prefix/bin/limactl');self.phase='prepare';self.env={'PATH':os.environ['PATH'],'HOME':str(self.root/'host-home'),'LIMA_HOME':str(self.root/'lima'),'LANG':'C.UTF-8'};self.guard=None
 def cmd(self,args,timeout=30,check=True):
  path=self.w/('vm'+str(self.index)+'-'+uuid.uuid4().hex[:10]+'.log')
  with path.open('x') as out:r=bounded_run(args,self.budget,self.phase,self.w/'commands.jsonl',timeout,out,self.env)
  text=path.read_text();r['log']=path.name
  with (self.w/'command-outputs.jsonl').open('a') as out:out.write(json.dumps(r)+'\n')
  if check and r['exitCode']:raise Blocked('command-failed:'+str(args)+':'+text[-1500:])
  return r,text
 def guest(self,args,**kw):return self.cmd([self.lima,'shell','--workdir=/tmp',self.name,'sudo','-n',*args],**kw)
 def action(self,*args,**kw):
  _,text=self.guest(['python3','/opt/ontosary-vm/code/guest.py',*args],**kw);return json.loads(text)
 def prepare(self):
  self.phase='prepare' if self.index==1 else 'repeat';limit(self.budget,self.phase)
  if self.root.exists():raise Blocked('owned-root-already-exists')
  write(self.w/f'ownership-{self.index}.json',{'root':str(self.root),'name':self.name,'registered':False});self.root.mkdir(mode=0o700);(self.root/'host-home').mkdir(mode=0o700)
  cache=read(self.w/'public-cache.json')['records'];rows={r['request']['name']:r for r in cache};store=Store(self.plan['store'])
  for r in cache:
   actual=store.lookup(r['request'],time.monotonic()+min(60,limit(self.budget,self.phase)))
   if not actual or actual['actual']!=r['actual']:raise Blocked('cache-missing-or-changed')
  lima=rows['lima-2.3.0-Darwin-arm64'];ubuntu=rows['ubuntu-26.04-20261016-arm64'];nerdctl=rows['nerdctl-full-2.4.2-linux-arm64']
  (self.root/'prefix').mkdir();self.cmd([sys.executable,'-c','import tarfile,sys;tarfile.open(sys.argv[1]).extractall(sys.argv[2],filter="data")',lima['path'],str(self.root/'prefix')])
  config=(CONTAINER/'lima.yaml').read_text().replace(ubuntu['request']['url'],ubuntu['path']).replace('  system: true','  archives:\n    - location: '+nerdctl['path']+'\n      arch: aarch64\n      digest: sha256:'+nerdctl['actual']['sha256']+'\n  system: true')
  (self.root/'vm.yaml').write_text(config);write(self.w/f'vm-config-{self.index}.json',{'text':config,'sha256':sha(self.root/'vm.yaml'),'sourceSha256':sha(CONTAINER/'lima.yaml'),'resourceSettingsUnchanged':True})
  write(self.w/f'ownership-{self.index}.json',{'root':str(self.root),'name':self.name,'registered':True})
  self.guard=subprocess.Popen([sys.executable,str(HERE/'host.py'),'watchdog','--work',str(self.w),'--index',str(self.index),'--parent',str(os.getpid())],start_new_session=True,stdout=(self.w/f'watchdog-{self.index}.log').open('w'),stderr=subprocess.STDOUT)
  self.cmd([self.lima,'start','--yes','--name='+self.name,'--timeout='+str(int(limit(self.budget,self.phase)))+'s',str(self.root/'vm.yaml')],min(600,limit(self.budget,self.phase)))
  _,text=self.cmd([self.lima,'shell','--workdir=/tmp',self.name,'id','-un']);manager_user=text.strip()
  if not manager_user.replace('-','').replace('_','').isalnum():raise Blocked('manager-name')
  self.cmd([self.lima,'copy',str(self.w/'inputs.tar.gz'),self.name+':/tmp/ontosary-vm-inputs.tar.gz'],60)
  installer="import tarfile,pathlib,sys,hashlib,json,os; p=pathlib.Path('/tmp/ontosary-vm-inputs.tar.gz'); assert hashlib.sha256(p.read_bytes()).hexdigest()==sys.argv[1]; b=pathlib.Path('/opt/ontosary-vm'); assert not b.exists(); b.mkdir(mode=0o755); t=tarfile.open(p); assert all(m.isfile() and not m.name.startswith('/') and '..' not in pathlib.PurePosixPath(m.name).parts for m in t.getmembers()); t.extractall(b,filter='data'); manifest=json.loads((b/'input-manifest.json').read_text()); assert all(hashlib.sha256((b/n).read_bytes()).hexdigest()==v['sha256'] for n,v in manifest.items()); p.unlink()"
  self.guest(['python3','-c',installer,sha(self.w/'inputs.tar.gz')],timeout=60)
  prep=self.action('prepare',manager_user,timeout=15);write(self.w/f'preparation-{self.index}.json',prep)
  if not prep['priorFixturePathsAbsent']:raise Blocked('inherited-fixture-path')
  if self.index==2 and prep['bootId']==read(self.w/'preparation-1.json')['bootId']:raise Blocked('reused-vm-identity')
 def recover(self,scope):
  start=time.monotonic();available=min(30,limit(self.budget,'finish')-90,limit(self.budget,self.phase))
  if available<=0:raise Blocked('recovery-reserve')
  data=self.action('export',scope,timeout=min(20,available));archive=self.w/f'vm{self.index}-{scope}.tar.gz';index=self.w/f'vm{self.index}-{scope}.index.json'
  for remote,local in [(data['archive'],archive),(data['index'],index)]:self.cmd([self.lima,'copy',self.name+':'+remote,str(local)],max(.1,available-(time.monotonic()-start)))
  verified=verify_pair(archive,index)
  if sha(archive)!=data['archiveSha256']:raise Blocked('recovery-hash')
  write(self.w/f'recovery-{self.index}-{scope}.json',{'evidenceStatus':'complete','archive':archive.name,'index':index.name,'sha256':sha(archive),'verified':verified,'seconds':time.monotonic()-start});return archive
 def unit(self,mode):
  self.phase='prepare' if mode=='normal-1' else ('boundaries' if mode.startswith('normal') and self.index==1 else 'repeat' if self.index==2 else 'failures')
  if min(limit(self.budget,self.phase),limit(self.budget,'finish')-90)<120:raise Blocked('insufficient-unit-budget')
  began=time.monotonic();rid=uuid.uuid4().hex[:12];row={'mode':mode,'runId':rid,'vm':self.index,'registeredHostMono':began,'externalLimitSeconds':120};units=read(self.w/'units.json') if (self.w/'units.json').exists() else []
  if len(units)>=4 or mode in [u['mode'] for u in units]:raise Blocked('unit-count-or-repeat')
  units.append(row);write(self.w/'units.json',units);state=self.action('register',rid,mode,'114',timeout=5);row['registration']=state;write(self.w/'units.json',units)
  wrapper=subprocess.Popen([sys.executable,str(HERE/'host.py'),'wrapper','--work',str(self.w),'--index',str(self.index),'--rid',rid],stdout=(self.w/(mode+'-wrapper.log')).open('w'),stderr=subprocess.STDOUT);row['wrapperPid']=wrapper.pid;injected=False
  try:
   while time.monotonic()-began<80:
    state=self.action('status',rid,timeout=4)
    if state.get('lateReady') and mode=='wrapper-death' and not injected:
     wrapper.kill();wrapper.wait(timeout=3);injected=True;row['wrapperKill']={'signal':'SIGKILL','returnCode':wrapper.returncode,'atHostMono':time.monotonic()}
    if state.get('finalizedAt') and state['supervisorObservation']['fields']['ActiveState'] in ['inactive','failed']:break
    time.sleep(.2)
   else:raise Blocked('unit-finalization-timeout')
   row['state']=state;write(self.w/'units.json',units)
   if mode in ['timeout','wrapper-death']:
    wait=max(0,began+28-time.monotonic());time.sleep(min(wait,28));state=self.action('status',rid);row['lateObservation']=state
    if state['lateExists'] or not state['lateReady']:raise Blocked('late-write-or-missing-positive-schedule')
    if state.get('outcome')!=mode:raise Blocked('failure-path-outcome')
   archive=self.recover(mode)
   with tarfile.open(archive) as t:
    names=t.getnames();prefix='runs/'+rid+'/collected/';name=prefix+'output/result.json'
    result=json.load(t.extractfile(name if name in names else prefix+'output/preflight.json'))
    if not mode.startswith('normal'):
     result['payload']=json.load(t.extractfile(prefix+'source/payload.json'));result['nativePayloadStarted']=True;row['resultFrom']='terminated-preflight-and-payload'
   verdict=check(result,state,mode);row.update(verdict=verdict,passed=verdict['passed'],seconds=time.monotonic()-began,wrapperKilled=injected);write(self.w/'units.json',units)
   if row['seconds']>=120:raise Blocked('unit-120-second-cap')
   if not verdict['passed']:raise Blocked('fixture-boundary:'+','.join(verdict['reasons']))
   return row
  finally:
   if wrapper.poll() is None:wrapper.terminate();wrapper.wait(timeout=3)
 def dispose(self):
  self.phase='finish';result={'cleanupStatus':'unconfirmed','vmAbsent':False,'rootAbsent':not self.root.exists(),'errors':[],'vmDisposalIsNotUnitTermination':True}
  owner=self.w/f'ownership-{self.index}.json'
  if not owner.exists():result.update(cleanupStatus='not-created',vmAbsent=True);write(self.w/f'cleanup-{self.index}.json',result);return result
  record=read(owner)
  if record['root']!=str(self.root) or record['name']!=self.name or self.root.is_symlink():raise RuntimeError('cleanup-ownership')
  def cleanup_call(args):
   try:return self.cmd(args,30,False)
   except Exception:
    # Only safety disposal is permitted beyond the experiment deadline.
    p=subprocess.run(args,env=self.env,capture_output=True,text=True,timeout=30);return {'exitCode':p.returncode},p.stdout+p.stderr
  try:
   if pathlib.Path(self.lima).exists() and record['registered']:
    for action in ['stop','delete']:
     try:r,out=cleanup_call([self.lima,action,'--force',self.name]);result[action]={'exitCode':r['exitCode'],'output':out[-2000:]}
     except Exception as e:result['errors'].append(str(e))
    r,out=cleanup_call([self.lima,'list','--json']);result['listing']={'exitCode':r['exitCode'],'output':out}
    if r['exitCode'] or any(json.loads(line).get('name')==self.name for line in out.splitlines() if line.strip()) or (self.root/'lima'/self.name).exists():raise RuntimeError('vm-absence-unconfirmed')
   elif record['registered']:raise RuntimeError('registered-vm-tool-missing')
   result['vmAbsent']=True
   processes=subprocess.check_output(['ps','-axo','pid=,command='],text=True)
   if any(str(self.root/'prefix') in line or str(self.root/'lima') in line for line in processes.splitlines()):raise RuntimeError('owned-process-remains')
   if self.root.exists():shutil.rmtree(self.root)
   result.update(rootAbsent=True,cleanupStatus='complete');(self.w/f'disposed-{self.index}').touch()
  except Exception as e:result['errors'].append(str(e))
  write(self.w/f'cleanup-{self.index}.json',result)
  if self.guard:self.guard.wait(timeout=3)
  return result

def execute(w):
 raise Blocked("preparation gate missed; runtime draft disabled")
 w=pathlib.Path(w).resolve();plan=read(w/'plan.json');gate=read(w/'local-gate.json')
 if not gate['passed'] or any(sha(p)!=h for p,h in gate['codeHashes'].items()):raise Blocked('local-code-gate')
 if (w/'execution-started.json').exists():raise Blocked('round-already-attempted')
 write(w/'execution-started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'planSha256':sha(w/'plan.json'),'codeHashes':gate['codeHashes']});verdict={'status':'inconclusive','fixtureOnly':True,'validSubmission':False,'trialAuthorized':False,'readyForTrial':False,'results':None,'errors':[]}
 for index,modes in [(1,['normal-1','timeout','wrapper-death']),(2,['normal-2'])]:
  r=Runner(w,index)
  def work():
   r.prepare()
   for mode in modes:r.unit(mode)
  def cleanup():
   try:
    if (w/f'preparation-{index}.json').exists():r.recover('final')
   except Exception as e:verdict['errors'].append({'phase':'recovery','error':str(e)})
   finally:
    receipt=r.dispose()
    if receipt['cleanupStatus']!='complete':raise RuntimeError('cleanup-incomplete')
  _,errors=finish_despite_failure(work,cleanup);verdict['errors']+=errors
  if errors:verdict['status']='blocked';break
 else:verdict['status']='feasible-for-next-integration'
 write(w/'outcome.json',verdict);print(json.dumps(verdict));return verdict

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['execute','wrapper','watchdog']);p.add_argument('--work',required=True);p.add_argument('--index',type=int,default=1);p.add_argument('--rid');p.add_argument('--parent',type=int);a=p.parse_args()
 if a.action=='execute':execute(a.work)
 elif a.action=='wrapper':
  r=Runner(a.work,a.index);r.phase='repeat' if a.index==2 else 'failures';end=time.monotonic()+110
  while time.monotonic()<end:r.guest(['python3','/opt/ontosary-vm/code/guest.py','heartbeat',a.rid],timeout=3);time.sleep(.5)
 else:
  r=Runner(a.work,a.index)
  while not (r.w/f'disposed-{a.index}').exists():
   try:os.kill(a.parent,0);alive=True
   except ProcessLookupError:alive=False
   if not alive or limit(r.budget,'finish')<90:r.dispose();break
   time.sleep(.5)
