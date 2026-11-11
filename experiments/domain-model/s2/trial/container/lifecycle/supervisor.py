"""Independent finite guest supervisor; worker belongs to a different slice."""
import json,os,pathlib,selectors,signal,subprocess,sys,time
from common import *
from collector import collect
from image import identify

def capture_ready(run):
    if (run/'source'/'ready.json').exists() and not (run/'worker-ready.json').exists():
        ready=json.loads((run/'source'/'ready.json').read_text());writers={p.name:json.loads(p.read_text()) for p in (run/'source').glob('writer-*.json')}
        state(run,execPending=False)
        write(run/'worker-ready.json',{'ready':ready,'writers':writers,'writerBytes':(run/'source'/'writer.log').stat().st_size if (run/'source'/'writer.log').exists() else 0,'kernel':cgroup_snapshot(run),**stamp()})

def supervise(run):
    if read(run/'state.json')['mode']=='linux-evaluation':
        from linux_job import supervise_job
        return supervise_job(run)
    with lock(run/'operation.lock'):
        s=read(run/'state.json');mode=s['mode'];start=stamp()
        write(run/'supervisor-ready.json',{'pid':os.getpid(),'cgroup':pathlib.Path('/proc/self/cgroup').read_text(),'cgroupNamespace':os.readlink('/proc/self/ns/cgroup'),**start})
        if s['cgroup'].removeprefix('/sys/fs/cgroup') in pathlib.Path('/proc/self/cgroup').read_text():raise RuntimeError('supervisor-inside-worker-group')
        end=time.monotonic()+5
        while not (run/'lease.json').exists():
            if time.monotonic()>=end:raise RuntimeError('first-heartbeat-missing')
            time.sleep(.02)
        if time.monotonic()-read(run/'lease.json')['mono']>5:raise RuntimeError('first-heartbeat-expired')
        state(run,createPending=True)
        args=NERD+['create','--pull=never','--name','ontosary-'+run.name,'--user','1000:1000','--cap-drop','ALL','--security-opt','no-new-privileges','--network','none','--cpus','2','--memory','4g','--pids-limit','256','--read-only','--tmpfs','/tmp:rw,noexec,nosuid,size=64m','--cgroupns','private','--cgroup-parent',s['slice']]
        for n in ['source','auxiliary']:args+=['--mount',f'type=bind,src={run/n},dst=/{n},readonly=false']
        if s['snapshot']:args+=['--mount',f'type=bind,src={s["snapshot"]},dst=/snapshot,readonly=true']
        args+=[s['image']['target'],'node','-e','setInterval(()=>{},1000)']
        created=command(run,args,timeout=3,check=False)
        if created[0]:
            # A timeout remains pending. A known parser rejection never dispatched.
            if created[0]!=124 and "invalid field" in created[2]:state(run,createPending=False)
            raise RuntimeError('create-failed:'+str(created[0]))
        cid=created[1].strip();state(run,containerId=cid,createPending=False)
        native=json.loads(command(run,NERD+['inspect','--mode=native',cid])[1])[0];write(run/'container-native.json',native)
        actual_image=identify(run,native['Image'])
        if actual_image!=s['image'] or native['Labels']['nerdctl/image-digest']!=s['image']['target'] or native['SnapshotInfo']['Parent']!=s['image']['chain']:raise RuntimeError('container-image-mismatch')
        started=stamp();state(run,state='running',startPending=True,workStarted=started,deadlineMono=started['mono']+s['taskSeconds'])
        command(run,NERD+['start',cid],timeout=3);state(run,startPending=False)
        inspected=json.loads(command(run,NERD+['inspect',cid])[1])[0];write(run/'container-started.json',inspected)
        pid=inspected['State']['Pid'];actual=pathlib.Path('/proc')/str(pid)/'cgroup'
        if not pid or s['cgroup'].removeprefix('/sys/fs/cgroup')+'/' not in actual.read_text():raise RuntimeError('worker-outside-parent')
        write(run/'placement.json',{'pid':pid,'procCgroup':actual.read_text(),'supervisor':read(run/'supervisor-ready.json'),'parent':cgroup_snapshot(run)})
        code=(CODE/'fixture.js').read_text()
        state(run,execPending=True)
        worker=subprocess.Popen(CTR+['tasks','exec','--exec-id','fixture-'+run.name,cid,'env','FIXTURE_CODE='+code,'node','-e',code,mode],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        sel=selectors.DefaultSelector();sel.register(worker.stdout,selectors.EVENT_READ);os.set_blocking(worker.stdout.fileno(),False)
        count=0;reason=None;exitcode=None;log_overflow=False
        with (run/'workload.log').open('xb') as log:
            while True:
                capture_ready(run)
                for key,_ in sel.select(.01):
                    chunk=os.read(key.fileobj.fileno(),65536)
                    if not chunk:sel.unregister(key.fileobj)
                    else:
                        count+=len(chunk);log.write(chunk[:max(0,1024*1024-(count-len(chunk)))])
                        if count>1024*1024:log_overflow=True
                now=time.monotonic()
                if mode in ['kill-error','query-error'] and (run/'worker-ready.json').exists():reason='management-failure';break
                if log_overflow:reason='log-limit';break
                if now-read(run/'lease.json')['mono']>=5:reason='wrapper-lost';break
                if now>=started['mono']+s['taskSeconds']:reason='timeout';break
                code_exit=worker.poll()
                if code_exit is not None:
                    capture_ready(run);state(run,execPending=False);reason='exit';exitcode=code_exit;break
        sel.close();state(run,reason=reason,exitCode=exitcode,workloadLogBytesObserved=count,stopTrigger=stamp())
        inject=mode if mode in ['kill-error','query-error'] else None
        termination=stop_confirm(run,inject)
        try:worker.wait(timeout=2)
        except subprocess.TimeoutExpired:raise RuntimeError('exec-client-did-not-settle')
        # Drain only after whole-cgroup stop: inherited pipes cannot hold collection open.
        with (run/'workload.log').open('ab') as log:
            while True:
                chunk=os.read(worker.stdout.fileno(),65536)
                if not chunk:break
                count+=len(chunk);log.write(chunk[:max(0,1024*1024-(count-len(chunk)))])
                if count>1024*1024:log_overflow=True
        worker.stdout.close()
        state(run,execClientExit=worker.returncode,workloadLogBytesObserved=count)
        if log_overflow:raise RuntimeError('workload-log-limit')
        state(run,state='collecting',collectionStarted=stamp())
        result=collect(run,read(run/'baseline.json'),termination,1 if mode=='copy-failure' else None)
        state(run,state='finalized',collectionFinished=stamp(),classification=result['classification'])
        event(run,'finalized',result='result/fixture.json')
        if mode=='publish-supervisor':
            event(run,'fault-injection',stage='after-publication-before-service-success',signal='SIGKILL');os.kill(os.getpid(),signal.SIGKILL)
if __name__=='__main__':
    run=runpath(sys.argv[1])
    try:supervise(run)
    except Exception as e:
        state(run,state='blocked',blockReason=str(e),recoveryRequired=True);gate(run,False,'supervisor-error');event(run,'supervisor-error',error=str(e));raise
