"""Manager-only state and kernel/runtime checks for the finite fixture harness."""
import contextlib,datetime,fcntl,hashlib,json,os,pathlib,re,signal,subprocess,time
ROOT=pathlib.Path('/opt/ontosary-fixture')
CODE=ROOT/'code'
NERD=['nerdctl','--address','/run/containerd/containerd.sock','--namespace','default']
CTR=['ctr','--address','/run/containerd/containerd.sock','--namespace','default']

def stamp():return {'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mono':time.monotonic()}
def write(path,value):
    tmp=path.with_name(path.name+'.tmp.'+str(os.getpid()))
    with tmp.open('x') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.chmod(tmp,0o600);os.replace(tmp,path)
def read(path):return json.loads(path.read_text())
def runpath(runid):
    if not re.fullmatch('[0-9a-f]{12}',runid):raise ValueError('invalid manager run ID')
    return ROOT/'runs'/runid
@contextlib.contextmanager
def lock(path,deadline=None):
    with path.open('a') as f:
        if deadline is None:fcntl.flock(f,fcntl.LOCK_EX)
        else:
            while True:
                if time.monotonic()>=deadline:raise RuntimeError('lock-deadline')
                try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);break
                except BlockingIOError:time.sleep(.01)
        yield

def event(run,kind,**details):
    with (run/'events.jsonl').open('a') as f:f.write(json.dumps({'kind':kind,**stamp(),**details},sort_keys=True)+'\n')
def command(run,args,timeout=3,check=True,env=None,deadline=None):
    if deadline is not None:
        timeout=min(timeout,deadline-time.monotonic())
        if timeout<=0:raise RuntimeError("command-deadline")
    started=stamp()
    try:
        if deadline is None:
            p=subprocess.run(args,capture_output=True,timeout=timeout,env=env);rawout,rawerr=p.stdout,p.stderr
        else:
            p=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,start_new_session=True)
            try:rawout,rawerr=p.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                # Kill the owned CLI process group, not just a PID with inherited output pipes.
                try:os.killpg(p.pid,signal.SIGKILL)
                except ProcessLookupError:pass
                try:p.communicate(timeout=.2)
                except subprocess.TimeoutExpired:pass
                raise
        code=p.returncode;out=rawout.decode(errors='replace');err=rawerr.decode(errors='replace')
    except subprocess.TimeoutExpired as e:
        code=124;out=(e.stdout or b'').decode(errors='replace');err=(e.stderr or b'').decode(errors='replace')
    event(run,'command',command=args,start=started,seconds=time.monotonic()-started['mono'],exitCode=code,stdout=out,stderr=err)
    if check and code:raise RuntimeError('manager-command:'+str(code)+':'+args[0])
    return code,out,err

def state(run,**updates):
    s=read(run/'state.json');s.update(updates);write(run/'state.json',s);event(run,'state',state=s);return s

def gate(run,allow,reason,deadline=None):
    with lock(ROOT/'gate.lock',deadline):
        g=read(ROOT/'gate.json')
        if g['runId']==run.name:write(ROOT/'gate.json',{'runId':run.name,'allowNext':allow,'reason':reason,**stamp()})

def cgroup_snapshot(run):
    s=read(run/'state.json');cg=pathlib.Path(s['cgroup']);info=cg.stat()
    if info.st_ino!=s['cgroupInode']:raise RuntimeError('cgroup-identity-changed')
    events=dict(line.split() for line in (cg/'cgroup.events').read_text().splitlines())
    members=[]
    for procs in [cg/'cgroup.procs',*cg.rglob('cgroup.procs')]:
        try:pids=procs.read_text().split()
        except FileNotFoundError:continue  # runtime child scope may be removed; parent must remain.
        for pid in pids:
            try:
                actual=pathlib.Path('/proc')/pid
                fds={}
                for fd in (actual/'fd').iterdir():
                    try:fds[fd.name]={'target':os.readlink(fd),'mode':fd.stat().st_mode}
                    except FileNotFoundError:pass
                namespaces={n:os.readlink(actual/'ns'/n) for n in ['pid','cgroup','mnt','net']}
                members.append({'pid':int(pid),'group':str(procs.parent),'procCgroup':(actual/'cgroup').read_text(),'status':(actual/'status').read_text(),'fds':fds,'namespaces':namespaces})
            except FileNotFoundError:pass
    return {'path':str(cg),'inode':info.st_ino,'events':events,'members':members,**stamp()}

def stop_confirm(run,inject=None,deadline=None,runtime_env=None):
    previous=read(run/'state.json');preserve=previous['state']=='blocked'
    s=state(run,admissionClosed=True,**({} if preserve else {'state':'stopping'}),stopRequested=stamp())
    gate(run,False,'stopping',deadline)
    before=cgroup_snapshot(run);event(run,'before-kill',snapshot=before)
    if inject=='kill-error':raise RuntimeError('injected-kill-command-failure')
    (pathlib.Path(s['cgroup'])/'cgroup.kill').write_text('1')
    end=min(time.monotonic()+10,deadline) if deadline is not None else time.monotonic()+10
    while True:
        if inject=='query-error':raise RuntimeError('injected-state-query-failure')
        after=cgroup_snapshot(run)
        if after['events'].get('populated')=='0':break
        if time.monotonic()>=end:raise RuntimeError('termination-confirmation-timeout')
        time.sleep(.02)
    if after['members']:raise RuntimeError('empty-events-with-members')
    if s.get('createPending') or s.get('startPending') or s.get('execPending'):raise RuntimeError('runtime-request-unsettled')
    cid=s.get('containerId');runtime=None
    if cid:
        while True:
            runtime=json.loads(command(run,NERD+['inspect',cid],timeout=min(2,max(.01,end-time.monotonic())),deadline=end,env=runtime_env)[1])[0]
            if not runtime['State']['Running'] and runtime['State']['Pid']==0:break
            if time.monotonic()>=end:raise RuntimeError('runtime-task-still-active')
            time.sleep(.02)
        tasklist=command(run,CTR+['tasks','list'],timeout=min(2,max(.01,end-time.monotonic())),deadline=end,env=runtime_env)[1]
        matching=[line.split() for line in tasklist.splitlines()[1:] if line.split() and line.split()[0]==cid]
        if matching:
            if len(matching)!=1 or matching[0][-1]!='STOPPED':raise RuntimeError('runtime-task-not-stopped')
            command(run,CTR+['tasks','delete',cid],timeout=min(2,max(.01,end-time.monotonic())),deadline=end,env=runtime_env)
            remaining=command(run,CTR+['tasks','list'],timeout=min(2,max(.01,end-time.monotonic())),deadline=end,env=runtime_env)[1]
            if any(line.split() and line.split()[0]==cid for line in remaining.splitlines()[1:]):raise RuntimeError('runtime-task-present')
    after=cgroup_snapshot(run)
    if after['events'].get('populated')!='0':raise RuntimeError('cgroup-repopulated')
    record={'state':'stopped-confirmed','confirmed':True,'admissionClosed':True,'runId':run.name,'containerId':cid,'image':s['image'],'cgroup':s['cgroup'],'cgroupInode':s['cgroupInode'],'source':str(run/'source'),'auxiliary':str(run/'auxiliary'),'reason':s.get('reason'),'exitCode':s.get('exitCode'),'start':s.get('workStarted'),'deadlineMono':s.get('deadlineMono'),'stopRequested':s['stopRequested'],'confirmedAt':stamp(),'kernel':after,'runtimeState':runtime['State'] if runtime else None}
    write(run/'termination.json',record);state(run,**({} if preserve else {'state':'stopped-confirmed'}),terminationConfirmed=True);event(run,'stopped-confirmed',termination=record);return record

def cleanup(run):
    with lock(run/'operation.lock'):
        original=read(run/'state.json');event(run,'cleanup-enter',serviceResult=os.environ.get('SERVICE_RESULT'),supervisorState=original['state'])
        try:
            service_result=os.environ.get('SERVICE_RESULT')
            abnormal=service_result is not None and service_result!='success'
            if original['state']=='finalized' and not abnormal:
                # Re-check without rewinding the public state or issuing another result.
                snap=cgroup_snapshot(run)
                if snap['events'].get('populated')!='0':raise RuntimeError('finalized-cgroup-populated')
                runtime=json.loads(command(run,NERD+['inspect',original['containerId']])[1])[0]
                if runtime['State']['Running']:raise RuntimeError('finalized-runtime-running')
                if service_result is None and not original.get('cleanupDone'):
                    event(run,'cleanup-deferred',reason='await-systemd-service-result');return
                state(run,cleanupDone=True);gate(run,True,'finalized-cleanup-confirmed')
            else:
                if (run/'result').exists():
                    os.rename(run/'result',run/'quarantined-result')
                    event(run,'result-revoked',reason='supervisor-failed-after-publication')
                    original['blockReason']='supervisor-failed-after-publication'
                    state(run,state='blocked',classification=None,blockReason=original['blockReason'])
                state(run,reason='supervisor-failed' if abnormal else original.get('reason') or 'supervisor-failed',exitCode=original.get('exitCode'))
                term=stop_confirm(run)
                state(run,state='blocked',cleanupDone=True,recoveryRequired=True,terminationConfirmed=True,blockReason=original.get('blockReason') or 'supervisor-failed')
                gate(run,False,'recovery-required')
            event(run,'cleanup-complete')
        except Exception as e:
            state(run,state='blocked',cleanupDone=False,recoveryRequired=True,blockReason='cleanup-failed:'+str(e));gate(run,False,'discard-vm-required');event(run,'cleanup-failed',error=str(e));raise
