"""Manager-owned finite original/candidate pair. No model, authentication or policy retry."""
import sys,pathlib,json,os,time,uuid,copy,datetime,hashlib
sys.path.insert(0,'/opt/ontosary-fixture/code')
from common import *
from image import identify
from policy import RULE
HERE=pathlib.Path('/opt/ontosary-policy-retry');LOG=HERE/'preparation'
BASE='docker.io/library/node@sha256:4a4884e8a44826194dff92ba316264f392056cbe243dcc9fd3551e71cea02b90'
if sys.argv[1]=='prepare':
 LOG.mkdir()
 versions=command(LOG,['sh','-c','uname -a; systemctl --version; nerdctl --version; containerd --version; runc --version'])[1]
 assert all(value in versions for value in ['7.0.0-38-generic','nerdctl version 2.4.2','containerd','b7a25261e029d68978bbf290df0a62fc819b3c51'])
 command(LOG,NERD+['build','--build-arg','BASE_IMAGE='+BASE,'-t','ontosary-s2-policy-retry:trace',str(HERE/'build')],timeout=max(.01,(datetime.datetime.fromisoformat(read(HERE/'budget.json')['deadlines']['environment']['utc'])-datetime.datetime.now(datetime.timezone.utc)).total_seconds()))
 image=identify(LOG,'ontosary-s2-policy-retry:trace');write(HERE/'image.json',image)
 ROOT.mkdir(exist_ok=True);(ROOT/'runs').mkdir(exist_ok=True)
def unit(mode):
 rid=uuid.uuid4().hex[:12];run=runpath(rid);run.mkdir(mode=0o700);started=stamp()
 write(ROOT/'gate.json',{'runId':rid,'allowNext':False})
 for name in ['source','auxiliary','cli-state','shell-home','scratch','materials']:
  p=run/name;p.mkdir(mode=0o700);os.chown(p,1000,1000)
 for name,value in [('source/input.txt','source input\n'),('materials/input.txt','material input\n')]:
  p=run/name;p.write_text(value);os.chown(p,1000,1000)
 slice_name='ontosary-'+rid+'.slice';service='ontosary-fixture-'+rid+'.service';units=pathlib.Path('/run/systemd/system')
 st='[Unit]\nDescription=Single policy owned worker parent\n[Slice]\nCPUQuota=200%\nMemoryMax=4G\nTasksMax=256\n'
 sv=f'[Unit]\nDescription=Single policy finite supervisor\n[Service]\nType=simple\nExecStart=/usr/bin/python3 {HERE}/retry-job.py {rid}\nExecStopPost=/usr/bin/python3 {CODE}/manager.py cleanup {rid}\nRestart=no\nRuntimeMaxSec=95\nTimeoutStartSec=5\nTimeoutStopSec=12\nKillMode=control-group\nKillSignal=SIGKILL\n'
 for name,txt in [(slice_name,st),(service,sv)]: (units/name).write_text(txt);(run/name).write_text(txt)
 command(run,['systemctl','daemon-reload']);command(run,['systemctl','start',slice_name]);cg=command(run,['systemctl','show',slice_name,'-p','ControlGroup','--value'])[1].strip();path=pathlib.Path('/sys/fs/cgroup'+cg)
 write(run/'state.json',{'runId':rid,'mode':mode,'state':'prepared','createPending':False,'startPending':False,'execPending':False,'containerId':None,'image':image,'cgroup':str(path),'cgroupInode':path.stat().st_ino,'slice':slice_name,'service':service,'cleanupDone':False})
 write(HERE/(mode+'-run.json'),{'runId':rid,'started':started})
 command(run,['systemctl','start',service])
 if mode=='candidate':
  while not (HERE/'candidate-prepared.json').exists():
   status=command(run,['systemctl','show',service,'-p','ActiveState','--value'])[1].strip()
   if status in ['inactive','failed']:raise RuntimeError('candidate-precheck-failed')
   if time.monotonic()-started['mono']>100:raise RuntimeError('candidate-precheck-timeout')
   time.sleep(.1)
  return {'prepared':True}
 return collect_unit(mode,run,started)
def collect_unit(mode,run,started):
 s=read(run/'state.json');service=s['service'];slice_name=s['slice'];path=pathlib.Path(s['cgroup']);units=pathlib.Path('/run/systemd/system')
 while True:
  status=command(run,['systemctl','show',service,'-p','ActiveState','--value'])[1].strip()
  if status in ['inactive','failed']:break
  if time.monotonic()-started['mono']>110:command(run,['systemctl','stop',service],timeout=15);raise RuntimeError('outer-timeout')
  time.sleep(.2)
 state_now=read(run/'state.json')
 command(run,['journalctl','-u',service,'--no-pager','-n','100'],check=False)
 assert state_now['state']=='finalized' and state_now['cleanupDone'] and state_now['terminationConfirmed'],state_now
 term=read(run/'termination.json');assert term['kernel']['events']['populated']=='0' and not term['kernel']['members']
 cid=state_now['containerId'];command(run,NERD+['rm',cid]);code,out,err=command(run,NERD+['inspect',cid],check=False);assert code and 'no such' in err.lower()
 tasks=command(run,CTR+['tasks','list'])[1];assert not any(x.split() and x.split()[0]==cid for x in tasks.splitlines()[1:])
 assert cgroup_snapshot(run)['events']['populated']=='0'
 write(run/'removed.json',{'containerAbsent':True,'runtimeTaskAbsent':True,'noPendingRequests':not any(state_now.get(k) for k in ['createPending','startPending','execPending']),'terminationBeforeCollection':True,'seconds':time.monotonic()-started['mono'],**stamp()})
 # Diagnostic result is read only after cgroup, task, pending and container checks.
 result=read(run/'auxiliary/result.json');write(HERE/(mode+'-result.json'),result)
 since=datetime.datetime.fromisoformat(started['utc']).strftime('%Y-%m-%d %H:%M:%S UTC');until=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S UTC')
 command(run,['journalctl','-k','--since',since,'--until',until,'--no-pager','--output=short-iso','--grep=apparmor=.*(DENIED|ALLOWED).*(comm="(bwrap|codex|strace)"|profile="nerdctl-default")'],timeout=5,check=False)
 assert time.monotonic()-started['mono']<120
 command(run,['systemctl','stop',slice_name]);assert not path.exists()
 for name in [service,slice_name]:(units/name).unlink()
 command(run,['systemctl','daemon-reload'])
 return result
if sys.argv[1]=='prepare':
 baseline=unit('baseline')
 flags='CLONE_NEWNS|CLONE_NEWIPC|CLONE_NEWUSER|CLONE_NEWPID|CLONE_NEWNET|SIGCHLD'
 assert all(baseline['parent'].values()) and not baseline['nativePayloadStarted']
 assert baseline['calls'][0]['stdout']=='codex-cli 0.167.0-alpha.3.2\n' and baseline['nodeVersion']=='v22.19.0'
 expected={'codex':'e7f91e14eab4ba3a0f65047c1757b593409d4ce791ccb6ac65c67c970dfed76f','bwrap':'0f543a7356ab343b4827222f910461d4196778f328b28acd6c126ef18e9557ab'}
 assert all(baseline['binaries'][k]['sha256']==v for k,v in expected.items())
 assert baseline['calls'][-1]['stderr'].count('clone(child_stack=NULL, flags='+flags+') = -1 EPERM')==2
 policy=copy.deepcopy(read(HERE/'baseline-native.json')['Spec']['linux']['seccomp']);policy['syscalls'].append(RULE);write(HERE/'candidate.json',policy);os.chmod(HERE/'candidate.json',0o400)
 assert (HERE/'candidate.json').stat().st_uid==0
 unit('candidate')
elif sys.argv[1]=='collect':
 info=read(HERE/'candidate-run.json');collect_unit('candidate',runpath(info['runId']),info['started']);write(HERE/'pair-complete.json',{'containers':2,'candidateStarts':1,'fixtureOnly':True,'validSubmission':False,'readyForTrial':False,'trialAuthorized':False,'results':None})
else:raise ValueError('unknown stage')
