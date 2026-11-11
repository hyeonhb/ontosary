"""Finite known-submission jobs, using the existing manager's termination and collector authority."""
import json,os,pathlib,selectors,subprocess,time
from common import *
from collector import collect
from image import identify
ENV=pathlib.Path('/opt/ontosary-linux-evaluation')
JOBS={
 'baseline':('baseline','complete-root','public'),
 'reference':('reference','complete-root','public'),
 'helper-type-error':('helper-type-error','complete-root','private'),
 'wrong-modal-order':('wrong-modal-order','complete-root','private'),
 'reference-delta':('reference','explicit-baseline-delta','private'),
 'timeout':('timeout','complete-root','private'),
 'control':('control','complete-root','private'),
}
def specification(name):
    if name not in JOBS:raise ValueError('unknown known-submission job')
    variant,mode,public=JOBS[name];source='baseline' if variant in ['timeout','control'] else variant
    return {'name':name,'variant':variant,'inputMode':mode,'public':public,'source':str(ENV/'assembled'/source),'input':str(ENV/'assembled'/(source+'.json')),'kind':'known-submission-calibration','fixtureOnly':True,'validSubmission':False}

def runtime_exit(inspected):
    s=inspected['State']
    if s.get('OOMKilled'):return ('oom',s.get('ExitCode'))
    if s['Running']:return None
    if s['Pid']!=0 or s.get('Status')!='exited' or not s.get('StartedAt') or s['StartedAt'].startswith('0001-'):raise RuntimeError('runtime-exit-unclear')
    return ('exit',s['ExitCode'])

def supervise_job(run):
    with lock(run/'operation.lock'):
        s=read(run/'state.json');job=s['job'];assert job==specification(job['name'])
        started_supervisor=stamp()
        write(run/'supervisor-ready.json',{'pid':os.getpid(),'cgroup':pathlib.Path('/proc/self/cgroup').read_text(),'cgroupNamespace':os.readlink('/proc/self/ns/cgroup'),**started_supervisor})
        if s['cgroup'].removeprefix('/sys/fs/cgroup') in pathlib.Path('/proc/self/cgroup').read_text():raise RuntimeError('supervisor-inside-worker-group')
        until=time.monotonic()+5
        while not (run/'lease.json').exists():
            if time.monotonic()>=until:raise RuntimeError('first-heartbeat-missing')
            time.sleep(.02)
        if time.monotonic()-read(run/'lease.json')['mono']>5:raise RuntimeError('first-heartbeat-expired')
        # Deadline includes the very first dispatched create, identity inspection and start.
        started=stamp();deadline=started['mono']+s['taskSeconds']
        state(run,createPending=True,workStarted=started,deadlineMono=deadline)
        def bounded(args,check=True):
            remaining=deadline-time.monotonic()
            if remaining<=0:raise RuntimeError('job-deadline-during-start')
            return command(run,args,timeout=min(3,remaining),check=check)
        args=NERD+['create','--pull=never','--name','ontosary-'+run.name,'--user','1000:1000','--cap-drop','ALL','--security-opt','no-new-privileges','--network','none','--cpus','2','--memory','4g','--pids-limit','256','--read-only','--tmpfs','/tmp:rw,noexec,nosuid,nodev,size=64m','--cgroupns','private','--cgroup-parent',s['slice']]
        mounts=[(ENV/'environment','/environment',True),(ENV/'tools','/tools',True),(job['source'],'/source',True),(job['input'],'/input.json',True),(run/'source','/output',False),(run/'auxiliary','/auxiliary',False)]
        for src,dst,ro in mounts:args+=['--mount',f'type=bind,src={src},dst={dst},readonly={str(ro).lower()}']
        args+=[s['image']['target'],'node','/tools/job.mjs',job['variant'],job['inputMode'],job['public']]
        created=bounded(args,False)
        if created[0]:raise RuntimeError('job-create-unsettled:'+str(created[0]))
        cid=created[1].strip()
        if len(cid)!=64 or any(c not in '0123456789abcdef' for c in cid):raise RuntimeError('job-create-identity-unclear')
        state(run,containerId=cid,createPending=False)
        native=json.loads(bounded(NERD+['inspect','--mode=native',cid])[1])[0];write(run/'container-native.json',native)
        actual_image=identify(run,native['Image'])
        if actual_image!=s['image'] or native['Labels']['nerdctl/image-digest']!=s['image']['target'] or native['SnapshotInfo']['Parent']!=s['image']['chain']:raise RuntimeError('container-image-mismatch')
        state(run,state='running',startPending=True)
        bounded(NERD+['start',cid]);state(run,startPending=False)
        inspected=json.loads(bounded(NERD+['inspect',cid])[1])[0];write(run/'container-started.json',inspected)
        pid=inspected['State']['Pid']
        if not pid:raise RuntimeError('job-start-placement-unobserved')
        proc=pathlib.Path('/proc')/str(pid)
        if s['cgroup'].removeprefix('/sys/fs/cgroup')+'/' not in (proc/'cgroup').read_text():raise RuntimeError('worker-outside-parent')
        write(run/'placement.json',{'pid':pid,'procCgroup':(proc/'cgroup').read_text(),'mountinfo':(proc/'mountinfo').read_text(),'supervisor':read(run/'supervisor-ready.json'),'parent':cgroup_snapshot(run)})
        logger=subprocess.Popen(NERD+['logs','--follow',cid],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        sel=selectors.DefaultSelector();sel.register(logger.stdout,selectors.EVENT_READ);os.set_blocking(logger.stdout.fileno(),False)
        count=0;overflow=False;reason=None;exitcode=None;next_inspect=0
        def drain(log,wait):
            nonlocal count,overflow
            for key,_ in sel.select(wait):
                chunk=os.read(key.fileobj.fileno(),65536)
                if not chunk:sel.unregister(key.fileobj)
                else:
                    prior=count;count+=len(chunk);log.write(chunk[:max(0,1024*1024-prior)]);overflow|=count>1024*1024
        try:
            with (run/'workload.log').open('xb') as log:
                while True:
                    drain(log,.02);now=time.monotonic()
                    if overflow:reason='log-limit';break
                    if now-read(run/'lease.json')['mono']>=5:reason='wrapper-lost';break
                    if now>=deadline:reason='timeout';break
                    if now>=next_inspect:
                        inspected=json.loads(command(run,NERD+['inspect',cid],timeout=min(2,deadline-now))[1])[0]
                        observed=runtime_exit(inspected);next_inspect=time.monotonic()+.2
                        if observed:
                            reason,exitcode=observed;write(run/'container-exited.json',inspected);break
                state(run,reason=reason,exitCode=exitcode,stopTrigger=stamp(),workloadLogBytesObserved=count)
                termination=stop_confirm(run)
                logger.wait(timeout=2)
                while sel.get_map():drain(log,.02)
            if logger.returncode or overflow:raise RuntimeError('job-log-failed-or-overflow')
        finally:
            sel.close()
            if logger.poll() is None:logger.kill();logger.wait(timeout=2)
            logger.stdout.close()
        state(run,workloadLogBytesObserved=count,state='collecting',collectionStarted=stamp())
        result=collect(run,read(run/'baseline.json'),termination)
        state(run,state='finalized',collectionFinished=stamp(),classification=result['classification'])
        event(run,'finalized',kindOfResult='known-submission-calibration',result='result/fixture.json')
