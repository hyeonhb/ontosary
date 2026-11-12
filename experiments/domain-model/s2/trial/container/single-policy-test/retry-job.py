"""Two fixed synthetic observations; unchanged common termination authority."""
import sys,pathlib,json,time,hashlib,datetime
sys.path.insert(0,'/opt/ontosary-fixture/code')
from common import *
from runtime_policy import verify,baseline_verify
ROOT_JOB=pathlib.Path('/opt/ontosary-policy-retry')
def execute(run):
 with lock(run/'operation.lock'):
  s=read(run/'state.json');started=stamp();deadline=started['mono']+90
  supervisor=(pathlib.Path('/proc/self/cgroup')).read_text();assert s['cgroup'].removeprefix('/sys/fs/cgroup') not in supervisor
  write(run/'supervisor.json',{'pid':os.getpid(),'cgroup':supervisor,**stamp()})
  state(run,workStarted=started,deadlineMono=deadline,createPending=True)
  def bounded(args,timeout=3,check=True):
   remaining=deadline-time.monotonic()
   if remaining<=0:raise RuntimeError('unit-deadline')
   return command(run,args,timeout=min(timeout,remaining),check=check)
  args=NERD+['create','--pull=never','--name','ontosary-'+run.name,'--entrypoint','node','--user','1000:1000','--cap-drop','ALL','--security-opt','no-new-privileges','--network','none','--cpus','2','--memory','4g','--pids-limit','256','--read-only','--tmpfs','/tmp:rw,noexec,nosuid,nodev,size=64m','--cgroupns','private','--cgroup-parent',s['slice']]
  if s['mode']=='candidate':
   profile=ROOT_JOB/'candidate.json';assert profile.stat().st_uid==0 and profile.stat().st_mode & 0o777==0o400
   write(run/'profile-input.json',{'sha256':hashlib.sha256(profile.read_bytes()).hexdigest(),'uid':0,'mode':'0400','format':'OCI LinuxSeccomp identity'})
   args+=['--security-opt','seccomp='+str(profile)]
  mounts=[(run/'source','/source',False),(run/'auxiliary','/output',False),(run/'cli-state','/home/runner/cli-state',False),(run/'shell-home','/home/worker',False),(run/'scratch','/scratch',False),(run/'materials','/materials',True),(ROOT_JOB/'probe','/probe',True),(ROOT_JOB/'policy.toml','/home/runner/cli-state/config.toml',True)]
  for src,dst,ro in mounts:args+=['--mount',f'type=bind,src={src},dst={dst},readonly={str(ro).lower()}']
  args+=[s['image']['target'],'/probe/probe.mjs']
  write(run/'pre-execution.json',{'command':args,'mountRoles':[{'source':str(a),'destination':b,'readonly':c} for a,b,c in mounts],'inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT_JOB/'probe/probe.mjs',ROOT_JOB/'policy.toml',run/'source/input.txt',run/'materials/input.txt']},'image':s['image'],'mode':s['mode'],'expected':'original clone EPERM; candidate exact clone observation once','payloadSeconds':15,'outerSeconds':120,**stamp()})
  cid=bounded(args)[1].strip();assert len(cid)==64
  state(run,containerId=cid,createPending=False)
  native=json.loads(bounded(NERD+['inspect','--mode=native',cid])[1])[0];write(run/'native.json',native)
  for src,dst,ro in mounts:
   observed=[m for m in native['Spec']['mounts'] if m['destination']==dst];assert len(observed)==1 and observed[0]['source']==str(src)
  assert native['Labels']['nerdctl/image-digest']==s['image']['target'] and native['SnapshotInfo']['Parent']==s['image']['chain']
  if s['mode']=='baseline':baseline_verify(native,read(ROOT_JOB/'prior-native.json'),str(run),str(ROOT_JOB),s['slice']);write(ROOT_JOB/'baseline-native.json',native);write(ROOT_JOB/'baseline-identity.json',{'run':str(run),'shared':str(ROOT_JOB),'slice_name':s['slice']})
  else:
   identity={'run':str(run),'shared':str(ROOT_JOB),'slice_name':s['slice']};actual=verify(native,read(ROOT_JOB/'baseline-native.json'),identity,read(ROOT_JOB/'baseline-identity.json'));assert native['Spec']['linux']['seccomp']==read(ROOT_JOB/'candidate.json')
   write(run/'policy-verification.json',{**actual,**stamp()});write(ROOT_JOB/'candidate-prepared.json',{'runId':run.name,**stamp()})
   while not (ROOT_JOB/'candidate-authorized.json').exists():
    if time.monotonic()>=deadline:raise RuntimeError('host-authorization-missing')
    time.sleep(.05)
   assert read(ROOT_JOB/'candidate-authorized.json')['runId']==run.name
  # Host's 20-minute boundary is transferred as a fixed UTC timestamp.
  assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(read(ROOT_JOB/'budget.json')['deadlines']['environment']['utc']),'environment-deadline'
  write(run/'start-authorized.json',stamp());state(run,startPending=True,state='running');bounded(NERD+['start',cid]);state(run,startPending=False)
  inspected=json.loads(bounded(NERD+['inspect',cid])[1])[0];pid=inspected['State']['Pid']
  if pid:
   proc=pathlib.Path('/proc')/str(pid);placement=(proc/'cgroup').read_text();assert s['cgroup'].removeprefix('/sys/fs/cgroup')+'/' in placement
   write(run/'placement.json',{'pid':pid,'procCgroup':placement,'parent':cgroup_snapshot(run)})
  wait=bounded(NERD+['wait',cid],25,False)
  state(run,reason='exit' if wait[0]==0 else 'timeout',exitCode=wait[1].strip(),stopTrigger=stamp())
  stop_confirm(run)
  bounded(NERD+['logs',cid],3,False)
  state(run,state='finalized',fixtureOnly=True,validSubmission=False)
if __name__=='__main__':execute(runpath(sys.argv[1]))
