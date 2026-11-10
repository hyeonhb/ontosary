"""Finite host fixture probe with ready handshakes and expected failure assertions."""
import argparse,datetime,hashlib,json,os,pathlib,signal,subprocess,sys,time
from host_driver import guest
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--output',required=True);p.add_argument('--modes',nargs='+',required=True);p.add_argument('--consume');p.add_argument('--budget',required=True);a=p.parse_args()
root=pathlib.Path(a.root);output=pathlib.Path(a.output);output.mkdir(parents=True,exist_ok=True);prefix=str(root/'prefix');home=str(root/'lima');limactl=str(root/'prefix/bin/limactl');code=pathlib.Path(__file__).parent

def shell(args,timeout=3):
    r=subprocess.run([limactl,'shell','--workdir=/tmp','s2-lifecycle','sudo',*args],env={**os.environ,'LIMA_HOME':home},capture_output=True,timeout=timeout)
    if r.returncode:raise RuntimeError(r.stderr.decode()+r.stdout.decode())
    return r.stdout.decode()
for mode in a.modes:
    budget=json.loads(pathlib.Path(a.budget).read_text());now=datetime.datetime.now(datetime.timezone.utc)
    remaining=min(150*60-(time.monotonic()-budget['startedMonotonic']),(datetime.datetime.fromisoformat(budget['explorationDeadline'])-now).total_seconds())
    if remaining<60:raise RuntimeError('no-time-for-next-fixture')
    started=time.monotonic();args=['prepare',mode]+([a.consume] if mode=='consume' else [])
    prepared=guest(prefix,home,args);rid=prepared['runId'];case=output/rid;case.mkdir();(case/'prepare.json').write_text(json.dumps(prepared,indent=2)+'\n');print(json.dumps({'event':'prepared','mode':mode,'runId':rid}),flush=True)
    driver=subprocess.Popen([sys.executable,str(code/'host_driver.py'),'--prefix',prefix,'--home',home,'--run',rid,'--log',str(case/'driver.jsonl')],stdout=(case/'driver.stdout').open('w'),stderr=(case/'driver.stderr').open('w'))
    injected=False;duplicates=[]
    while time.monotonic()-started<60:
        s=guest(prefix,home,['query',rid])
        if mode in ['wrapper','supervisor'] and not injected and s['workerReady']:
            ready=json.loads(shell(['cat',f'/opt/ontosary-fixture/runs/{rid}/worker-ready.json']))
            assert ready['writers'] and ready['writerBytes']>0
            if mode=='wrapper':os.kill(driver.pid,signal.SIGKILL)
            else:shell(['systemctl','kill','--kill-whom=main','--signal=KILL',s['service']])
            (case/'injection.json').write_text(json.dumps({'kind':mode,'hostMono':time.monotonic(),'hostUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ready':ready},indent=2)+'\n');injected=True
        if mode=='race' and not injected and s['workerReady']:
            for i in range(2):
                duplicates.append(subprocess.Popen([limactl,'shell','--workdir=/tmp','s2-lifecycle','sudo','python3','/opt/ontosary-fixture/code/manager.py','cleanup',rid],env={**os.environ,'LIMA_HOME':home},stdout=(case/('duplicate-'+str(i)+'.stdout')).open('w'),stderr=(case/('duplicate-'+str(i)+'.stderr')).open('w')))
            injected=True
        if s['state'] in ['finalized','blocked'] and s.get('cleanupDone'):break
        time.sleep(.1)
    else:
        driver.kill();raise RuntimeError('outer-timeout:'+rid)
    driver_code=driver.wait(timeout=3)
    (case/'driver-exit.json').write_text(json.dumps({'exitCode':driver_code,'signalInjected':mode=='wrapper'})+'\n')
    assert driver_code==(-signal.SIGKILL if mode=='wrapper' else 0)
    for duplicate in duplicates:assert duplicate.wait(timeout=12)==0
    (case/'terminal.json').write_text(json.dumps(s,indent=2)+'\n')
    if s['state']=='blocked':
        try:guest(prefix,home,['prepare','simple'])
        except RuntimeError as e:
            assert 'next-run-denied' in str(e);(case/'denied-next.txt').write_text(str(e))
        else:raise AssertionError('blocked-run-admitted-next')
    late_modes=['normal','timeout','wrapper','supervisor','kill-error','query-error','race']
    if mode in late_modes:
        # Observe beyond each writer's planned delayed write, in the guest clock domain.
        check_code="import pathlib,time,json,hashlib; p=pathlib.Path('/opt/ontosary-fixture/runs/"+rid+"'); paths=[p/'source',p/'result']; snap=lambda:{str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for r in paths if r.exists() for f in r.rglob('*') if f.is_file()}; before=snap(); ready=json.loads((p/'worker-ready.json').read_text()); time.sleep(max(0,ready['mono']+8-time.monotonic())); after=snap(); print(json.dumps({'same':before==after,'lateFiles':[str(f) for f in (p/'source').glob('late-*')],'observedMono':time.monotonic(),'readyMono':ready['mono'],'hashes':after})); assert before==after; assert not list((p/'source').glob('late-*'))"
        observed=json.loads(shell(['python3','-c',check_code],timeout=12));(case/'late-observation.json').write_text(json.dumps(observed,indent=2)+'\n')
    if s['state']=='blocked':
        assert shell(['test','!','-e',f'/opt/ontosary-fixture/runs/{rid}/result'])==''
        assert shell(['test','!','-e',f'/opt/ontosary-fixture/runs/{rid}/staging'])==''
        guest(prefix,home,['recover',rid])
    expected_block=mode in ['publish-supervisor','supervisor','kill-error','query-error','symlink','hardlink','fifo','socket','device','files','bytes','depth','copy-failure','logs']
    assert (s['state']=='blocked')==expected_block,(mode,s)
    if not expected_block:
        result=json.loads(shell(['cat',f'/opt/ontosary-fixture/runs/{rid}/result/fixture.json']));(case/'result.json').write_text(json.dumps(result,indent=2)+'\n')
        reason={'timeout':'timeout','wrapper':'wrapper-lost'}.get(mode,'exit');assert s['reason']==reason,(mode,s)
        assert s['exitCode']==(7 if mode=='nonzero' else 0 if reason=='exit' else None)
        assert result['classification']==('normal-fixture' if reason=='exit' and mode!='nonzero' else 'diagnostic')
        assert result['fixtureOnly'] and not result['validSubmission']
        assert 'source/delete.txt' in result['delta']['deleted'] and 'source/original.txt' in result['delta']['modified'] and 'auxiliary/note.txt' in result['delta']['added']
    summary={'mode':mode,'runId':rid,'state':s['state'],'reason':s.get('reason'),'blockReason':s.get('blockReason'),'seconds':time.monotonic()-started}
    (case/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)
