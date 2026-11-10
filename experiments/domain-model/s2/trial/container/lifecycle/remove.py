"""Remove only recorded fixture containers and temporary units, retaining evidence."""
import json,pathlib,sys
from common import *
log=ROOT/'removal';log.mkdir(mode=0o700);rows=[]
for run in sorted((ROOT/'runs').iterdir()):
    s=read(run/'state.json');assert s.get('cleanupDone') and not any(s.get(k) for k in ['createPending','startPending','execPending'])
    snap=cgroup_snapshot(run);assert snap['events']['populated']=='0' and not snap['members']
    cid=s.get('containerId')
    if cid:
        inspect=json.loads(command(log,NERD+['inspect',cid])[1])[0];assert not inspect['State']['Running']
        command(log,NERD+['rm',cid])
        code,out,err=command(log,NERD+['inspect',cid],check=False);assert code and 'no such object' in err.lower()
    command(log,['systemctl','stop',s['service']],check=False)
    command(log,['systemctl','reset-failed',s['service']],check=False)
    command(log,['systemctl','stop',s['slice']])
    for unit in [s['service'],s['slice']]:(pathlib.Path('/run/systemd/system')/unit).unlink()
    assert not pathlib.Path(s['cgroup']).exists()
    rows.append({'runId':run.name,'containerId':cid,'cgroupAbsent':True,'unitsAbsent':True})
command(log,['systemctl','stop','ontosary.slice'])
command(log,['systemctl','daemon-reload'])
listing=command(log,NERD+['ps','-a','--format','{{.ID}} {{.Names}}'])[1];assert 'ontosary-' not in listing
units=command(log,['systemctl','list-units','--all','--no-pager','ontosary*'])[1];assert 'ontosary-' not in units
assert not any(pathlib.Path('/run/systemd/system').glob('ontosary-*'))
image=read(ROOT/'image.json');command(log,NERD+['rmi',image['name']])
remaining_images=command(log,NERD+['images','--format','{{.Repository}}:{{.Tag}}'])[1];assert 'ontosary-s2-lifecycle' not in remaining_images
write(log/'cleanup.json',{'status':'guest-cleanup-passed','rows':rows,'containers':listing,'units':units,**stamp()})
print(json.dumps(read(log/'cleanup.json')))
