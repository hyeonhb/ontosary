"""Verify stopped owned units before image/VM removal; no new runtime unit."""
import json,pathlib,sys
ROOT=pathlib.Path('/opt/ontosary-namespace-diagnosis');sys.path.insert(0,str(ROOT/'lifecycle'))
from common import NERD,CTR,command,write
log=ROOT/'removal';log.mkdir();rows=[]
for mode in ['baseline','traced']:
 run=ROOT/mode;done=json.loads((run/'audit/complete.json').read_text());cid=done['cid'];assert done['removed'] and done['stoppedPid']==0
 code,out,err=command(log,NERD+['inspect',cid],check=False);assert code and 'no such' in err.lower()
 paths=[str(p) for p in pathlib.Path('/sys/fs/cgroup').rglob('*') if cid in str(p)];assert not paths
 rows.append({'mode':mode,'cid':cid,'containerAbsent':True,'cgroupAbsent':True})
containers=command(log,NERD+['ps','-a','--format','{{.ID}} {{.Names}}'])[1];assert not containers.strip()
tasks=command(log,CTR+['tasks','list'])[1];assert len(tasks.strip().splitlines())==1
volumes=command(log,NERD+['volume','ls','--quiet'])[1];assert not volumes.strip()
for name in ['trace','base']:
 image=json.loads((ROOT/(name+'-image.json')).read_text());command(log,NERD+['rmi',image['name']])
 code,out,err=command(log,NERD+['image','inspect','--mode=native',image['name']],check=False);assert not out.strip()
images=command(log,NERD+['images','--format','{{.Repository}}:{{.Tag}}'])[1];assert not images.strip()
units=command(log,['systemctl','list-units','--all','--no-legend','ontosary*'])[1];assert not units.strip()
write(log/'cleanup.json',{'status':'guest-cleanup-passed','rows':rows,'containers':containers,'tasks':tasks,'volumes':volumes,'images':images,'units':units,'newPolicyApplied':False,'newAuditOrTraceKernelFacility':False,'note':'Preparation units only; no CLI lifecycle/timeout authority claimed.'})
print(json.dumps({'status':'guest-cleanup-passed','unitsRemoved':2,'imagesRemoved':2}))
