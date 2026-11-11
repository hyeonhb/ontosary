"""At most two preparation containers, unchanged security policy; no lifecycle claims."""
import datetime,hashlib,json,os,pathlib,subprocess,sys,time
ROOT=pathlib.Path('/opt/ontosary-namespace-diagnosis');sys.path.insert(0,str(ROOT/'lifecycle'))
from common import NERD,CTR,command,write
from image import identify
LOG=ROOT/'preparation';LOG.mkdir();BASE='docker.io/library/node@sha256:4a4884e8a44826194dff92ba316264f392056cbe243dcc9fd3551e71cea02b90'
command(LOG,['sh','-c','uname -a; systemctl --version; nerdctl --version; containerd --version; runc --version'])
command(LOG,NERD+['build','--build-arg','BASE_IMAGE='+BASE,'-t','ontosary-s2-namespace:base',str(ROOT/'build')],timeout=300)
base=identify(LOG,'ontosary-s2-namespace:base');write(ROOT/'base-image.json',base)
def unit(mode,image):
 run=ROOT/mode;run.mkdir();log=run/'audit';log.mkdir()
 for name in ['source','output','state','shell-home','scratch','materials']:
  p=run/name;p.mkdir(mode=0o700);os.chown(p,1000,1000)
 for name,value in [('source/input.txt','source input\n'),('materials/input.txt','material input\n')]:
  p=run/name;p.write_text(value);os.chown(p,1000,1000)
 args=NERD+['create','--pull=never','--name','s2-namespace-'+mode,'--entrypoint','node','--user','1000:1000','--cap-drop','ALL','--security-opt','no-new-privileges','--network','none','--cpus','2','--memory','4g','--pids-limit','256','--read-only','--tmpfs','/tmp:rw,noexec,nosuid,nodev,size=64m','--cgroupns','private']
 for src,dst,ro in [(run/'source','/source',False),(run/'output','/output',False),(run/'state','/home/runner/cli-state',False),(run/'shell-home','/home/worker',False),(run/'scratch','/scratch',False),(run/'materials','/materials',True),(ROOT/'probe','/probe',True),(ROOT/'policy.toml','/home/runner/cli-state/config.toml',True)]:args+=['--mount',f'type=bind,src={src},dst={dst},readonly={str(ro).lower()}']
 args+=[image['target'],'/probe/probe.mjs',mode]
 write(log/'pre-execution.json',{'mode':mode,'command':args,'policySha256':hashlib.sha256((ROOT/'policy.toml').read_bytes()).hexdigest(),'probeSha256':hashlib.sha256((ROOT/'probe/probe.mjs').read_bytes()).hexdigest(),'expected':'namespace failure; traced unit may instead expose ptrace denial','payloadMaxSeconds':15,'outerMaxSeconds':120,'image':image,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 started=time.monotonic();since=datetime.datetime.now(datetime.timezone.utc).isoformat();deadline=started+120
 def bounded(args,timeout=3,check=True):return command(log,args,timeout=min(timeout,max(.1,deadline-time.monotonic())),check=check)
 cid=bounded(args)[1].strip();native=json.loads(bounded(NERD+['inspect','--mode=native',cid])[1])[0];write(log/'native.json',native)
 assert native['Labels']['nerdctl/image-digest']==image['target'] and native['SnapshotInfo']['Parent']==image['chain']
 bounded(NERD+['start',cid]);wait=bounded(NERD+['wait',cid],15,False)
 if wait[0]:bounded(NERD+['kill','--signal','KILL',cid],5);bounded(NERD+['wait',cid],5)
 exited=json.loads(bounded(NERD+['inspect',cid])[1])[0];write(log/'exited.json',exited);bounded(NERD+['logs',cid])
 assert not exited['State']['Running'] and exited['State']['Pid']==0
 bounded(NERD+['rm',cid]);code,out,err=bounded(NERD+['inspect',cid],check=False);assert code and 'no such' in err.lower()
 paths=[str(p) for p in pathlib.Path('/sys/fs/cgroup').rglob('*') if cid in str(p)];assert not paths
 # Read only narrowly matching existing kernel records within this unit's time window.
 until=datetime.datetime.now(datetime.timezone.utc).isoformat()
 logquery=['journalctl','--kernel','--since',since,'--until',until,'--no-pager','--output=short-iso','--grep=apparmor=.*(DENIED|ALLOWED).*(comm="(bwrap|codex|strace)"|profile="nerdctl-default")']
 bounded(logquery,5,False)
 result=json.loads((run/'output/result.json').read_text()) if (run/'output/result.json').exists() else None
 write(log/'complete.json',{'cid':cid,'waitExitCode':wait[0],'containerExitCode':exited['State']['ExitCode'],'stoppedPid':0,'removed':True,'cgroupPathsRemaining':paths,'seconds':time.monotonic()-started,'payloadDeadlineSeconds':15,'outerDeadlineSeconds':120,'resultPresent':result is not None})
 assert wait[0]==0 and exited['State']['ExitCode']==0 and result is not None
 if result['nativePayloadStarted']:raise RuntimeError('unexpected-baseline-success-stop-exploration')
 return result
unit('baseline',base)
tracebuild=ROOT/'trace-build';tracebuild.mkdir();original=(ROOT/'build/Dockerfile').read_text()
(tracebuild/'Dockerfile').write_text(original+'\nUSER 0:0\nRUN apt-get update && apt-get install -y --no-install-recommends strace && dpkg-query -W strace > /opt/namespace-package.txt && rm -rf /var/lib/apt/lists/*\nUSER 1000:1000\n')
write(LOG/'diagnostic-image-input.json',{'dockerfile':(tracebuild/'Dockerfile').read_text(),'sha256':hashlib.sha256((tracebuild/'Dockerfile').read_bytes()).hexdigest(),'policyUnchanged':True,'purpose':'strace tooling only, not original execution image'})
command(LOG,NERD+['build','--build-arg','BASE_IMAGE='+BASE,'-t','ontosary-s2-namespace:trace',str(tracebuild)],timeout=180)
trace_log=ROOT/'trace-image';trace_log.mkdir();diagnostic=identify(trace_log,'ontosary-s2-namespace:trace');write(ROOT/'trace-image.json',diagnostic)
unit('traced',diagnostic)
print(json.dumps({'completedPreparationContainers':2,'policyChangesApplied':False}))
