"""Finite guest entrypoint: one independent service and one shared stop/remove/collect path."""
import argparse,datetime,json,os,pathlib,sys,time,uuid
HERE=pathlib.Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'lifecycle'),'/opt/ontosary-fixture/code']
import common as c
from collector import collect,inventory
from identity import RUNTIME_ENV,ROLES,normalize,compare,RULE,expected_legacy
c.NERD[0]='/usr/local/bin/nerdctl';c.CTR[0]='/usr/local/bin/ctr'
SHARED=pathlib.Path('/opt/ontosary-execution');UNITS=pathlib.Path('/run/systemd/system')
MANAGER_ENV={'PATH':'/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin','HOME':'/root','LANG':'C.UTF-8'}
PENDING=['createPending','startPending','execPending']
MODES=['normal-1','precheck-rejection','start-failure','timeout','wrapper-death','supervisor-death','normal-2','baseline','candidate']

def deadline(run,phase):return c.read(run/'state.json')['deadlines'][phase]
def command(run,args,phase='remove',timeout=3,check=True):
    runtime=args[0] in ['nerdctl','ctr','/usr/local/bin/nerdctl','/usr/local/bin/ctr']
    args=args.copy()
    if runtime:args[0]='/usr/local/bin/'+pathlib.Path(args[0]).name
    return c.command(run,args,timeout,check,env=RUNTIME_ENV if runtime else MANAGER_ENV,deadline=deadline(run,phase))
def gate(run,allow,reason):c.gate(run,allow,reason,deadline(run,'finish'))
def pending(s):return any(s.get(k) for k in PENDING)
def revoke(run):
    if (run/'result').exists():os.rename(run/'result',run/'quarantined-result');c.event(run,'result-revoked')
def blocked(run,error,discard=True):
    revoke(run);c.state(run,state='blocked',collectionStatus='suppressed',cleanupDone=False,recoveryRequired=True,discardVM=discard,error=str(error));gate(run,False,'discard-vm-required' if discard else 'recovery-required')
def native(run,name,phase='remove'):
    return json.loads(command(run,c.NERD+['inspect','--mode=native',name],phase)[1])[0]
def list_containers(run,phase='remove'):
    # Successful full namespace inventory, never an inspect error interpreted as absence.
    ids=command(run,c.CTR+['containers','list','-q'],phase)[1].split()
    return [native(run,i,phase) for i in ids]
def owned(run,n):
    s=c.read(run/'state.json');cid=s.get('containerId')
    if n['Spec']['annotations'].get('nerdctl/name')!=s['containerName']:raise RuntimeError('foreign-container-name')
    if cid and n['ID']!=cid:raise RuntimeError('container-id-replaced')
    if n['Spec']['linux']['cgroupsPath']!=s['slice']+':nerdctl:'+n['ID']:raise RuntimeError('foreign-cgroup')
    if n['Labels']['nerdctl/image-digest']!=s['image']['target'] or n['SnapshotInfo']['Parent']!=s['image']['chain']:raise RuntimeError('foreign-image')
    return n['ID']
def resolve_owned(run,phase='remove'):
    s=c.read(run/'state.json');rows=list_containers(run,phase);matches=[n for n in rows if n['ID']==s.get('containerId') or n['Spec']['annotations'].get('nerdctl/name')==s['containerName']]
    if len(matches)>1:raise RuntimeError('ambiguous-container')
    return owned(run,matches[0]) if matches else None

def identity(run):
    s=c.read(run/'state.json')
    return {'runId':run.name,'run':str(run),'shared':str(SHARED),'slice':s['slice'],'containerId':s['containerId'],'image':s['image'],'inputHashes':s['inputHashes']}

def register(mode,remaining,host_deadline):
    if mode not in MODES or remaining<=0 or remaining>114:raise RuntimeError('invalid-registration-budget')
    c.ROOT.mkdir(mode=0o700,exist_ok=True);(c.ROOT/'runs').mkdir(mode=0o700,exist_ok=True)
    now=c.stamp();finish=now['mono']+min(remaining,(datetime.datetime.fromisoformat(host_deadline)-datetime.datetime.now(datetime.timezone.utc)).total_seconds())
    if finish-now['mono']<110:raise RuntimeError('registration-transport-budget')
    with c.lock(c.ROOT/'gate.lock',finish):
        if (c.ROOT/'gate.json').exists() and not c.read(c.ROOT/'gate.json').get('allowNext'):raise RuntimeError('admission-closed')
        rid=uuid.uuid4().hex[:12];run=c.runpath(rid);run.mkdir(mode=0o700)
        service='ontosary-execution-'+rid+'.service';slice_name='ontosary-'+rid+'.slice'
        # Ownership and planned requests exist BEFORE unit files, cgroup, mounts or runtime resources.
        c.write(run/'state.json',{'runId':rid,'mode':mode,'registeredAt':now,'hostDeadlineUtc':host_deadline,'deadlines':{'work':finish-40,'remove':finish-10,'finish':finish},'service':service,'slice':slice_name,'cgroup':'/sys/fs/cgroup/ontosary.slice/'+slice_name,'cgroupInode':None,'containerName':'ontosary-'+rid,'containerId':None,'image':c.read(SHARED/'image.json'),'inputHashes':c.read(SHARED/'inputs.json'),'ownedPaths':[str(run/n) for n in [*ROLES.values()]],'createPending':False,'startPending':False,'execPending':False,'state':'registered','outcome':None,'terminationConfirmed':False,'removalConfirmed':False,'collectionStatus':'not-started','admissionClosed':True,'cleanupDone':False,'recoveryRequired':False,'starts':0,'runtimeRequests':[]})
        c.write(c.ROOT/'gate.json',{'runId':rid,'allowNext':False,'reason':'registered'})
    text=f'[Unit]\nDescription=Ontosary finite execution supervisor\n[Service]\nType=exec\nWorkingDirectory={SHARED}\nExecStart=/usr/bin/python3 {HERE}/engine.py supervise {rid}\nExecStopPost=/usr/bin/python3 {HERE}/engine.py finalize {rid}\nRestart=no\nRuntimeMaxSec={max(.1,finish-40-time.monotonic()):.3f}\nTimeoutStopSec=39\nKillMode=control-group\nKillSignal=SIGKILL\n'
    try:
        (UNITS/service).write_text(text);(run/service).write_text(text)
        command(run,['systemctl','daemon-reload'],'work');command(run,['systemctl','start',service],'work',5)
    except Exception as e:
        c.state(run,outcome='registration-failure',error=str(e));finalize(run)
        raise
    print(json.dumps({'runId':rid,'registeredAt':now,'deadlines':c.read(run/'state.json')['deadlines']}),flush=True)
    return rid

def prepare(run):
    s=c.read(run/'state.json');slice_text='[Unit]\nDescription=Ontosary owned worker parent\n[Slice]\nCPUQuota=200%\nMemoryMax=4G\nTasksMax=256\n'
    (UNITS/s['slice']).write_text(slice_text);(run/s['slice']).write_text(slice_text)
    command(run,['systemctl','daemon-reload'],'work');command(run,['systemctl','start',s['slice']],'work')
    cg=command(run,['systemctl','show',s['slice'],'-p','ControlGroup','--value'],'work')[1].strip();path=pathlib.Path('/sys/fs/cgroup'+cg)
    if str(path)!=s['cgroup']:raise RuntimeError('planned-cgroup-mismatch')
    c.state(run,cgroupInode=path.stat().st_ino)
    supervisor=pathlib.Path('/proc/self/cgroup').read_text()
    if cg in supervisor:raise RuntimeError('supervisor-in-worker-cgroup')
    c.write(run/'supervisor.json',{'pid':os.getpid(),'cgroup':supervisor,**c.stamp()})
    for name in ROLES.values():
        p=run/name;p.mkdir(mode=0o700);os.chown(p,1000,1000)
    for name,text in [('source/input.txt','source input\n'),('materials/input.txt','material input\n')]:
        p=run/name;p.write_text(text);os.chown(p,1000,1000)
    prior_paths=[str(p/role/'prior-canary') for p in (c.ROOT/'runs').iterdir() if p!=run for role in ['source','shell-home','cli-state','scratch']]
    (run/'source/prior-paths.json').write_text(json.dumps(prior_paths));os.chown(run/'source/prior-paths.json',1000,1000)
    c.write(run/'baseline.json',inventory({n:run/n for n in ['source','auxiliary']},deadline=deadline(run,'work')))

def create_args(run):
    s=c.read(run/'state.json');args=c.NERD+['create','--pull=never','--name',s['containerName'],'--entrypoint','/missing-fixture-entrypoint' if s['mode']=='start-failure' else 'node','--user','1000:1000','--cap-drop','ALL','--security-opt','no-new-privileges','--network','none','--cpus','2','--memory','4g','--pids-limit','256','--read-only','--tmpfs','/tmp:rw,noexec,nosuid,nodev,size=64m','--cgroupns','private','--cgroup-parent',s['slice']]
    if s['mode']=='candidate':args+=['--security-opt','seccomp='+str(SHARED/'candidate.json')]
    mounts=[(run/role,dst,role=='materials') for dst,role in ROLES.items()]+[(SHARED/'probe','/probe',True),(SHARED/'policy.toml','/home/runner/cli-state/config.toml',True)]
    for src,dst,ro in mounts:args+=['--mount',f'type=bind,src={src},dst={dst},readonly={str(ro).lower()}']
    args += [s['image']['target'],'/probe/probe.mjs'] if s['mode'] in ['baseline','candidate'] else [s['image']['target'],'/probe/fixture.mjs',s['mode']]
    return args

def request(run,kind,args,timeout=10):
    s=c.read(run/'state.json')
    if s.get('workClosed'):raise RuntimeError('request-admission-closed')
    c.state(run,**{kind+'Pending':True},runtimeRequests=s['runtimeRequests']+[{'kind':kind,'command':args,'requestedAt':c.stamp()}])
    result=command(run,args,'work',timeout,False)
    # Timeout/transport loss does NOT settle an asynchronous runtime mutation.
    if result[0]==124:raise RuntimeError('runtime-request-unsettled:'+kind)
    if kind=='create':
        cid=resolve_owned(run,'work')
        if cid:c.state(run,containerId=cid)
        if result[0]!=0:raise RuntimeError('create-error-settlement-unknown')
        if not cid or result[1].strip()!=cid:raise RuntimeError('create-response-binding')
    if kind=='start' and result[0]!=0:
        if '/missing-fixture-entrypoint' not in result[2] or 'no such file or directory' not in result[2]:raise RuntimeError('start-error-settlement-unknown')
        cid=resolve_owned(run,'work')
        if not cid:raise RuntimeError('start-error-resource-unknown')
        info=json.loads(command(run,c.NERD+['inspect',cid],'work')[1])[0]
        if info['State']['Running'] or info['State']['Pid']!=0:raise RuntimeError('start-error-task-unsettled')
    c.state(run,**{kind+'Pending':False});c.event(run,'request-settled',kindRequested=kind,exitCode=result[0])
    return result

def supervise(run):
    try:
        with c.lock(run/'operation.lock',deadline(run,'work')):
            prepare(run);s=c.read(run/'state.json')
            if resolve_owned(run,'work'):raise RuntimeError('planned-name-already-exists')
            created=request(run,'create',create_args(run),30)
            if created[0]:c.state(run,outcome='create-failure',reason='create-failure');return
            s=c.read(run/'state.json');n=native(run,s['containerId'],'work');c.write(run/'native.json',n);ident=identity(run);c.write(run/'identity.json',ident)
            normalized,proof=normalize(n,ident);c.write(run/'identity-proof.json',{'normalized':normalized,'substitutions':proof})
            prior=c.read(SHARED/'prior-pair.json')['pairs']['baseline']
            expected,expected_id,migration=expected_legacy(prior['native'],prior['identity'],s['image'])
            expected_id['inputHashes']=ident['inputHashes']
            expected['Spec']['process']['args']=create_args(run)[-2:] if s['mode'] in ['baseline','candidate'] else ['node','/probe/fixture.mjs',s['mode']]
            if s['mode']=='start-failure':expected['Spec']['process']['args'][0]='/missing-fixture-entrypoint'
            if s['mode'] in ['baseline','candidate']:expected['Spec']['process']['args']=['node','/probe/probe.mjs']
            comparison=compare(n,expected,ident,expected_id,s['mode']=='candidate')
            c.write(run/'baseline-policy-verification.json',{'comparison':comparison,'explicitLegacyMigration':migration})
            if not comparison['accepted']:raise RuntimeError('baseline-full-spec-difference')
            if s['mode']=='precheck-rejection':c.state(run,outcome='precheck-rejected',reason='precheck-rejected');return
            if s['mode']=='candidate':
                pair=compare(n,c.read(SHARED/'baseline-native.json'),ident,c.read(SHARED/'baseline-identity.json'),True);c.write(run/'policy-verification.json',pair)
                if not pair['accepted']:raise RuntimeError('candidate-full-spec-difference')
            if s['mode']=='baseline':c.write(SHARED/'baseline-native.json',n);c.write(SHARED/'baseline-identity.json',ident)
            start=c.stamp();payload_end=min(start['mono']+15,deadline(run,'work'))
            c.state(run,workStarted=start,deadlineMono=payload_end)
            started=request(run,'start',c.NERD+['start',s['containerId']],min(10,max(.01,payload_end-time.monotonic())))
            if started[0]:c.state(run,outcome='start-failed',reason='start-failed',exitCode=started[0]);return
            c.state(run,starts=1,state='running')
            ready_seen=False
            while True:
                now=time.monotonic();s=c.read(run/'state.json')
                if (run/'auxiliary/ready.json').exists() and not ready_seen:
                    ready_seen=True;placement=c.cgroup_snapshot(run)
                    if s['mode'] in ['timeout','wrapper-death','supervisor-death'] and len(placement['members'])<2:raise RuntimeError('detached-descendant-not-observed')
                    c.write(run/'ready.json',{'worker':c.read(run/'auxiliary/ready.json'),'observedAt':c.stamp(),'placement':placement});c.event(run,'worker-ready')
                if now>=s['deadlineMono']:
                    c.state(run,outcome='timeout',reason='timeout',stopTrigger=c.stamp());return
                if s['mode']=='wrapper-death' and ready_seen:
                    beat=c.read(run/'heartbeat.json') if (run/'heartbeat.json').exists() else start
                    if now-beat['mono']>3:c.state(run,outcome='wrapper-death',reason='wrapper-death',stopTrigger=c.stamp());return
                info=json.loads(command(run,c.NERD+['inspect',s['containerId']],'work')[1])[0]
                if not info['State']['Running'] and info['State']['Pid']==0:
                    code=info['State'].get('ExitCode');c.state(run,outcome='exit',reason='exit',exitCode=code,stopTrigger=c.stamp());return
                time.sleep(.1)
    except Exception as e:
        c.state(run,outcome='supervisor-error',reason='supervisor-error',error=str(e));raise
    finally:c.state(run,workClosed=True)

def finalize(run):
    if c.read(run/'state.json').get('serviceInactiveConfirmed'):return
    try:
        with c.lock(run/'operation.lock',deadline(run,'remove')):
            s=c.read(run/'state.json');c.event(run,'finalizer-enter',serviceResult=os.environ.get('SERVICE_RESULT'))
            gate(run,False,'stopping');c.state(run,workClosed=True,admissionClosed=True)
            abnormal=os.environ.get('SERVICE_RESULT') not in [None,'success'] or s['outcome'] is None
            if abnormal:c.state(run,outcome='supervisor-death',reason='supervisor-death',recoveryRequired=True)
            s=c.read(run/'state.json')
            if not s.get('removalConfirmed'):
                if s['cgroupInode'] is None:
                    # No worker parent was registered: establish actual absent runtime, not missing CID.
                    if pending(s) or resolve_owned(run):raise RuntimeError('unregistered-parent-resource')
                    c.state(run,terminationConfirmed=True)
                    term=None
                else:
                    # Reuse existing cgroup/PID/task proof with this unit's absolute reserve.
                    term=c.stop_confirm(run,deadline=deadline(run,'remove'),runtime_env=RUNTIME_ENV)
                if pending(c.read(run/'state.json')):raise RuntimeError('runtime-request-unsettled')
                cid=resolve_owned(run)
                if cid:command(run,c.NERD+['rm',cid],timeout=max(.01,deadline(run,'remove')-time.monotonic()))
                if resolve_owned(run):raise RuntimeError('container-still-present')
                tasks=command(run,c.CTR+['tasks','list'])[1]
                if s.get('containerId') and any(x.split() and x.split()[0]==s['containerId'] for x in tasks.splitlines()[1:]):raise RuntimeError('task-still-present')
                c.write(run/'removed.json',{'containerAbsent':True,'taskAbsent':True,'pending':False,'confirmedAt':c.stamp()});c.state(run,removalConfirmed=True,removedAt=c.stamp(),lastWriteMtimeNs=(run/'auxiliary/writes.jsonl').stat().st_mtime_ns if (run/'auxiliary/writes.jsonl').exists() else None)
            else:term=c.read(run/'termination.json') if (run/'termination.json').exists() else None
            s=c.read(run/'state.json')
            if not s.get('workerUnitRemoved'):
                # Finalizer executes outside the worker slice. Files removed before opening admission.
                if s['cgroupInode'] is not None:
                    command(run,['systemctl','stop',s['slice']],'finish')
                    if pathlib.Path(s['cgroup']).exists():raise RuntimeError('worker-parent-remains')
                for name in [s['slice']]:
                    p=UNITS/name
                    if p.exists():p.unlink()
                command(run,['systemctl','daemon-reload'],'finish');c.state(run,workerUnitRemoved=True)
            allowed=s['outcome'] in ['exit','timeout','wrapper-death'] and not abnormal
            if allowed and s['collectionStatus']=='not-started':
                c.state(run,state='collecting',collectionStatus='collecting',collectionStarted=c.stamp())
                result=collect(run,c.read(run/'baseline.json'),term,deadline=deadline(run,'finish'))
                c.state(run,collectionStatus='collected',collectionFinished=c.stamp(),classification=result['classification'])
            elif not allowed:revoke(run);c.state(run,collectionStatus='suppressed')
            s=c.read(run/'state.json');recovery=s['outcome']!='exit' or s.get('exitCode')!=0
            c.state(run,state='finalized',cleanupDone=True,recoveryRequired=recovery,finalizedAt=c.stamp())
            # The service has not left ExecStopPost yet; observer seals actual inactive timestamp.
            gate(run,False,'await-inactive-service-proof');c.event(run,'finalizer-complete')
    except Exception as e:
        blocked(run,e);c.event(run,'finalizer-failed',error=str(e));raise

def observe(run,recover=False):
    with c.lock(run/'operation.lock',deadline(run,'finish')):
        return seal(run,recover)

def seal(run,recover=False):
    s=c.read(run/'state.json')
    if s.get('serviceInactiveConfirmed'):
        if recover and s['recoveryRequired'] and not (run/'recovery.json').exists():
            if resolve_owned(run,'finish') or pending(s):raise RuntimeError('recovery-resource-present')
            c.write(run/'recovery.json',{'priorOutcome':s['outcome'],'confirmed':True,**c.stamp()});gate(run,True,'explicit-recovery')
        return s
    status=command(run,['systemctl','show',s['service'],'-p','ActiveState','-p','InactiveEnterTimestampMonotonic'],'finish')[1]
    fields=dict(line.split('=',1) for line in status.splitlines() if '=' in line)
    if fields.get('ActiveState') not in ['inactive','failed']:return s
    inactive=int(fields.get('InactiveEnterTimestampMonotonic','0'))/1000000
    if not s.get('cleanupDone') or not s.get('terminationConfirmed') or not s.get('removalConfirmed') or pending(s):raise RuntimeError('cleanup-unconfirmed')
    # Unloaded unit may lose timestamp after daemon-reload: preserve a prior systemd proof only.
    if inactive<=0 or inactive>s['deadlines']['finish']:raise RuntimeError('inactive-deadline-unconfirmed')
    if resolve_owned(run,'finish'):raise RuntimeError('late-container')
    if pathlib.Path(s['cgroup']).exists():raise RuntimeError('late-cgroup')
    if time.monotonic()>s['deadlines']['finish']:raise RuntimeError('external-observation-deadline')
    (UNITS/s['service']).unlink()
    command(run,['systemctl','daemon-reload'],'finish')
    c.state(run,serviceInactiveConfirmed=True,unitFilesRemoved=True,inactiveAtMono=inactive,sealedAt=c.stamp())
    if s['recoveryRequired'] and not recover:gate(run,False,'explicit-recovery-required')
    else:
        if recover:c.write(run/'recovery.json',{'priorOutcome':s['outcome'],'confirmed':True,**c.stamp()})
        gate(run,True,'explicit-recovery' if recover else 'normal-cleanup-confirmed')
    return c.read(run/'state.json')

def reap():
    # Independent manager observer: only seals successful ExecStopPost completion,
    # never substitutes VM disposal or a missing PID for termination proof.
    while not (SHARED/'reaper-stop').exists():
        if (c.ROOT/'runs').exists():
            for run in (c.ROOT/'runs').iterdir():
                if not (run/'state.json').exists():continue
                s=c.read(run/'state.json')
                if s.get('cleanupDone') and not s.get('serviceInactiveConfirmed') and not s.get('discardVM'):
                    try:observe(run)
                    except Exception as e:blocked(run,'seal:'+str(e))
        time.sleep(.1)

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['register','supervise','finalize','observe','recover','heartbeat','reap','status']);p.add_argument('value',nargs='?');p.add_argument('--remaining',type=float);p.add_argument('--host-deadline');a=p.parse_args()
    if a.action=='reap':reap();return
    if a.action=='register':register(a.value,a.remaining,a.host_deadline);return
    run=c.runpath(a.value)
    if a.action=='status':
        s=c.read(run/'state.json');s['ready']=(run/'ready.json').exists();print(json.dumps(s));return
    if a.action=='heartbeat':
        s=c.read(run/'state.json')
        if s.get('workClosed'):return
        c.write(run/'heartbeat.json',c.stamp())
    elif a.action in ['observe','recover']:print(json.dumps(observe(run,a.action=='recover')))
    else:globals()[a.action](run)
if __name__=='__main__':main()
