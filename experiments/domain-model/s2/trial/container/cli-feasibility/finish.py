"""Verify both preparation containers are gone, then remove the owned image."""
import json,pathlib,sys
ROOT=pathlib.Path('/opt/ontosary-cli-feasibility');sys.path.insert(0,str(ROOT/'lifecycle'))
from common import NERD,CTR,command,write
log=ROOT/'removal';log.mkdir();rows=[]
for name in ['preparation','diagnosis']:
 gate=json.loads((ROOT/name/'gate.json').read_text());native=json.loads((ROOT/name/'container-native.json').read_text());exited=json.loads((ROOT/name/'container-exited.json').read_text())
 assert gate['containerAbsent'] and exited['State']['Pid']==0 and not exited['State']['Running'] and exited['State']['ExitCode']==0
 code,out,err=command(log,NERD+['inspect',gate['cid']],check=False);assert code and 'no such' in err.lower()
 rows.append({'phase':name,'containerId':gate['cid'],'containerAbsent':True,'nativeCgroupsPath':native['Spec']['linux']['cgroupsPath'],'observedStoppedPid':exited['State']['Pid']})
containers=command(log,NERD+['ps','-a','--format','{{.ID}} {{.Names}}'])[1];assert not containers.strip()
tasks=command(log,CTR+['tasks','list'])[1];assert len(tasks.strip().splitlines())==1
volumes=command(log,NERD+['volume','ls','--quiet'])[1];assert not volumes.strip()
units=command(log,['systemctl','list-units','--all','--no-legend','ontosary*'])[1];assert not units.strip()
cgpaths=[str(p) for p in pathlib.Path('/sys/fs/cgroup').rglob('*') if any(r['containerId'] in str(p) for r in rows)];assert not cgpaths
image=json.loads((ROOT/'image.json').read_text());command(log,NERD+['rmi',image['name']])
code,out,err=command(log,NERD+['image','inspect','--mode=native',image['name']],check=False)
images=command(log,NERD+['images','--format','{{.Repository}}:{{.Tag}}'])[1];assert not images.strip() and not out.strip()
write(log/'cleanup.json',{'status':'guest-cleanup-passed','containers':containers,'tasks':tasks,'volumes':volumes,'units':units,'cgroupPathsRemaining':cgpaths,'rows':rows,'image':image,'imageAbsent':True,'imageListing':images,'nativeMissingImageExitCode':code,'nativeMissingImageStderr':err,'runtimeTestsRegistered':0,'testServersCreated':0,'customNetworkRulesCreated':0,'note':'Natural preparation exits/removal verified; no lifecycle termination receipt or new timeout guarantee is claimed.'})
print(json.dumps({'status':'guest-cleanup-passed','containersRemoved':len(rows)}))
