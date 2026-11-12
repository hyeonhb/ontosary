"""Verify this pair's termination/removal and remove only its image/profile/units."""
import sys,pathlib,json
sys.path.insert(0,'/opt/ontosary-fixture/code')
from common import *
HERE=pathlib.Path('/opt/ontosary-policy-retry');log=HERE/'removal';log.mkdir();rows=[]
for mode in ['baseline','candidate']:
 p=HERE/(mode+'-run.json')
 if not p.exists():continue
 run=runpath(read(p)['runId']);s=read(run/'state.json')
 assert s['cleanupDone'] and s['terminationConfirmed'] and not any(s.get(k) for k in ['createPending','startPending','execPending'])
 command(log,['journalctl','-u',s['service'],'--no-pager','-n','100'],check=False)
 cid=s['containerId'];code,out,err=command(log,NERD+['inspect',cid],check=False)
 if code==0:
  n=json.loads(out)[0];assert not n['State']['Running'] and n['State']['Pid']==0
  command(log,NERD+['rm',cid]);code,out,err=command(log,NERD+['inspect',cid],check=False)
 assert code and 'no such' in err.lower()
 cg=pathlib.Path(s['cgroup'])
 if cg.exists():
  assert cgroup_snapshot(run)['events']['populated']=='0';command(log,['systemctl','stop',s['slice']]);assert not cg.exists()
 command(log,['systemctl','reset-failed',s['service']],check=False)
 for name in [s['slice'],s['service']]:
  unit=pathlib.Path('/run/systemd/system')/name
  if unit.exists():unit.unlink()
 rows.append({'mode':mode,'containerId':cid,'containerAbsent':True,'cgroupAbsent':True,'terminationConfirmed':True,'removedAt':stamp(),'secondsSinceCreate':stamp()['mono']-s['workStarted']['mono'],'runtimeWasStarted':(run/'start-authorized.json').exists()})
parent=pathlib.Path('/sys/fs/cgroup/ontosary.slice')
if parent.exists():
 assert dict(x.split() for x in (parent/'cgroup.events').read_text().splitlines())['populated']=='0'
 command(log,['systemctl','stop','ontosary.slice']);assert not parent.exists()
command(log,['systemctl','daemon-reload'])
containers=command(log,NERD+['ps','-a','--format','{{.ID}} {{.Names}}'])[1];assert not containers.strip()
tasks=command(log,CTR+['tasks','list'])[1];assert len(tasks.strip().splitlines())==1
volumes=command(log,NERD+['volume','ls','--quiet'])[1];assert not volumes.strip()
image=read(HERE/'image.json');command(log,NERD+['rmi',image['name']]);images=command(log,NERD+['images','--format','{{.Repository}}:{{.Tag}}'])[1];assert not images.strip()
profile=HERE/'candidate.json'
if profile.exists():profile.unlink()
units=command(log,['systemctl','list-units','--all','--no-legend','ontosary*'])[1];assert not units.strip()
write(log/'cleanup.json',{'status':'guest-cleanup-passed','rows':rows,'containers':containers,'tasks':tasks,'volumes':volumes,'images':images,'units':units,'profileAbsent':not profile.exists(),'fixtureOnly':True,'validSubmission':False,'R11':'unresolved'})
