"""Guest root-only admission, lease receipt, and independent systemd cleanup."""
import argparse,json,os,pathlib,stat,sys,time,uuid
from common import *
from collector import inventory
MODES={'simple','nonzero','normal','timeout','wrapper','supervisor','kill-error','query-error','control','race','symlink','hardlink','fifo','socket','device','files','bytes','depth','copy-failure','logs','consume','publish-supervisor'}
def prepare(mode,consume=None):
    if mode not in MODES:raise ValueError('unknown finite fixture')
    with lock(ROOT/'gate.lock'):
        if (ROOT/'gate.json').exists() and not read(ROOT/'gate.json')['allowNext']:raise RuntimeError('next-run-denied')
        rid=uuid.uuid4().hex[:12];run=runpath(rid);run.mkdir(parents=True,mode=0o700)
        write(ROOT/'gate.json',{'runId':rid,'allowNext':False,'reason':'prepared',**stamp()})
        for n in ['source','auxiliary']:(run/n).mkdir(mode=0o700);os.chown(run/n,1000,1000)
        for n in ['original.txt','delete.txt']:
            p=run/'source'/n;p.write_text('baseline\n');os.chown(p,1000,1000)
        baseline=inventory({n:run/n for n in ['source','auxiliary']});write(run/'baseline.json',baseline)
        # Real manager-side canaries; their exact paths are passed to the probe.
        control=ROOT/'control';control.mkdir(exist_ok=True,mode=0o700);(control/'package.json').write_text('{"managerCanary":true}\n')
        previous=ROOT/'previous';previous.mkdir(exist_ok=True,mode=0o700)
        for n in ['source','result']:(previous/n).mkdir(exist_ok=True,mode=0o700)
        (previous/'source'/'package.json').write_text('previous source canary\n');(previous/'result'/'fixture.json').write_text('previous result canary\n')
        canaries=[control/'package.json',previous/'source'/'package.json',previous/'result'/'fixture.json',pathlib.Path('/run/containerd/containerd.sock')]
        write(run/'canaries.json',[{'path':str(p),'mode':p.stat().st_mode,'inode':p.stat().st_ino,'isSocket':stat.S_ISSOCK(p.stat().st_mode)} for p in canaries])
        slice_name='ontosary-'+rid+'.slice';service='ontosary-fixture-'+rid+'.service'
        unit_dir=pathlib.Path('/run/systemd/system')
        slice_text='[Unit]\nDescription=Finite Ontosary worker parent\n[Slice]\nCPUQuota=200%\nMemoryMax=4G\nTasksMax=256\n'
        service_text=f'[Unit]\nDescription=Finite Ontosary fixture supervisor\n[Service]\nType=simple\nExecStart=/usr/bin/python3 {CODE}/supervisor.py {rid}\nExecStopPost=/usr/bin/python3 {CODE}/manager.py cleanup {rid}\nRestart=no\nRuntimeMaxSec=40\nTimeoutStartSec=5\nTimeoutStopSec=12\nKillMode=control-group\nKillSignal=SIGKILL\n'
        (unit_dir/slice_name).write_text(slice_text);(unit_dir/service).write_text(service_text)
        (run/'slice.unit').write_text(slice_text);(run/'service.unit').write_text(service_text)
        command(run,['systemctl','daemon-reload']);command(run,['systemctl','start',slice_name])
        cg=command(run,['systemctl','show',slice_name,'-p','ControlGroup','--value'])[1].strip();path=pathlib.Path('/sys/fs/cgroup'+cg)
        snapshot=None
        if consume:
            old=runpath(consume);prior=read(old/'state.json')
            if prior['state']!='finalized' or not prior.get('cleanupDone'):raise RuntimeError('consumer-source-not-finalized')
            snapshot=str(old/'result')
        initial={'runId':rid,'mode':mode,'state':'prepared','admissionClosed':False,'createPending':False,'startPending':False,'containerId':None,'image':read(ROOT/'image.json'),'cgroup':str(path),'cgroupInode':path.stat().st_ino,'service':service,'slice':slice_name,'prepared':stamp(),'taskSeconds':5 if mode=='timeout' else 10,'snapshot':snapshot,'cleanupDone':False}
        write(run/'state.json',initial);event(run,'registered',state=initial)
        if mode=='device':os.mknod(run/'source'/'bad',stat.S_IFCHR|0o600,os.makedev(1,3))
        command(run,['systemctl','start',service]);return initial

def heartbeat(run):
    if not (run/'supervisor-ready.json').exists():raise RuntimeError('supervisor-not-ready')
    s=read(run/'state.json')
    if s['state'] not in ['prepared','running']:return s
    lease={**stamp(),'runId':run.name};write(run/'lease.json',lease);event(run,'heartbeat',receipt=lease);return lease

def recover(run):
    s=read(run/'state.json')
    if s['state']!='blocked' or not s.get('cleanupDone') or s.get('createPending') or s.get('startPending') or s.get('execPending'):raise RuntimeError('recovery-refused')
    with lock(run/'operation.lock'):
        stop_confirm(run);gate(run,True,'explicit-manager-recovery');event(run,'recovered')
    return read(run/'state.json')
if __name__=='__main__':
    action=sys.argv[1]
    if action=='prepare':result=prepare(sys.argv[2],sys.argv[3] if len(sys.argv)>3 else None)
    else:
        run=runpath(sys.argv[2])
        if action=='heartbeat':result=heartbeat(run)
        elif action=='query':result={**read(run/'state.json'),'workerReady':(run/'worker-ready.json').exists()}
        elif action=='cleanup':cleanup(run);result=read(run/'state.json')
        elif action=='recover':result=recover(run)
        else:raise ValueError('unknown action')
    print(json.dumps(result,sort_keys=True))
