"""Guest pinned image build and finite local CLI discovery; no Vendure install or credentials."""
import json,os,pathlib,subprocess,sys,time
ROOT=pathlib.Path('/opt/ontosary-cli-feasibility');LOG=ROOT/'preparation';LOG.mkdir()
sys.path.insert(0,str(ROOT/'lifecycle'))
from common import NERD,CTR,command,write
from image import identify
command(LOG,['sh','-c','uname -a; systemctl --version; nerdctl --version; containerd --version'])
command(LOG,NERD+['build','--build-arg','BASE_IMAGE=docker.io/library/node@sha256:4a4884e8a44826194dff92ba316264f392056cbe243dcc9fd3551e71cea02b90','-t','ontosary-s2-cli-feasibility:20261111',str(ROOT/'build')],timeout=300)
image=identify(LOG,'ontosary-s2-cli-feasibility:20261111');write(ROOT/'image.json',image)
for name in ['source','auxiliary','cli-state','shell-home','scratch']:
 p=ROOT/name;p.mkdir(mode=0o700);os.chown(p,1000,1000)
args=NERD+['create','--pull=never','--name','s2-cli-discovery','--entrypoint','node','--user','1000:1000','--cap-drop','ALL','--security-opt','no-new-privileges','--network','none','--cpus','2','--memory','4g','--pids-limit','256','--read-only','--tmpfs','/tmp:rw,noexec,nosuid,nodev,size=64m','--cgroupns','private']
for src,dst,ro in [(ROOT/'source','/source',False),(ROOT/'auxiliary','/output',False),(ROOT/'cli-state','/home/runner/cli-state',False),(ROOT/'shell-home','/home/worker',False),(ROOT/'scratch','/scratch',False),(ROOT/'probe','/probe',True)]:args+=['--mount',f'type=bind,src={src},dst={dst},readonly={str(ro).lower()}']
args+=[image['target'],'/probe/discover.mjs']
cid=command(LOG,args)[1].strip();write(LOG/'container-native.json',json.loads(command(LOG,NERD+['inspect','--mode=native',cid])[1])[0])
native=json.loads((LOG/'container-native.json').read_text());assert native['Labels']['nerdctl/image-digest']==image['target'] and native['SnapshotInfo']['Parent']==image['chain']
command(LOG,NERD+['start',cid]);command(LOG,NERD+['wait',cid],timeout=60);write(LOG/'container-exited.json',json.loads(command(LOG,NERD+['inspect',cid])[1])[0]);command(LOG,NERD+['logs',cid]);state=json.loads((LOG/'container-exited.json').read_text())['State'];assert not state['Running'] and state['Pid']==0 and state['ExitCode']==0
command(LOG,NERD+['rm',cid]);code,out,err=command(LOG,NERD+['inspect',cid],check=False);assert code and 'no such' in err.lower()
write(LOG/'gate.json',{'status':'discovery-complete','cid':cid,'exitCode':state['ExitCode'],'containerAbsent':True,'image':image,'productionReceipt':False});print(json.dumps(json.loads((ROOT/'auxiliary/discovery.json').read_text())['calls']))
