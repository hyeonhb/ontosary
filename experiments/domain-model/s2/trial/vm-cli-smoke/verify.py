"""Offline cross-check of this smoke's small indexed host diagnostics. No VM commands."""
import hashlib,json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'container/single-policy-test')]
from scope import inventory
from run import verdict

def verify(root):
    root=pathlib.Path(root).resolve();files=list(root.rglob('*'))
    assert len(files)<=160 and all(not p.is_symlink() for p in files),'evidence kind/count'
    regular=[p for p in files if p.is_file()]
    assert all(p.stat().st_nlink==1 for p in regular),'hardlinked evidence'
    assert sum(p.stat().st_size for p in regular)<=4*1024**2,'round diagnostics bound'
    assert inventory(root)==json.loads((root/'index.json').read_text()),'index mismatch'
    read=lambda name:json.loads((root/name).read_text())
    w=read('prepared/worker.json');outer=read('prepared/outer.json');result=read('prepared/result.json')
    freeze=read('prepared/freeze.json');plan=read('prepared/worker-plan.json');prepared=read('prepared/guest-preparation.json')
    for path,h in freeze['codeHashes'].items():
        assert hashlib.sha256((HERE/pathlib.Path(path).name).read_bytes()).hexdigest()==h,'runtime code changed'
    for name,h in freeze['inputHashes'].items():
        assert hashlib.sha256((root/'prepared'/name).read_bytes()).hexdigest()==h,'input changed'
    assert w['native']['args']==plan['argv']==prepared['plan']['argv']==read('prepared/native-command.json')['cliArgs'],'actual argv'
    assert w['binaries']==plan['binaries'] and w['configHash']==plan['configHash'] and w['payloadHash']==plan['payloadHash'],'actual hash'
    assert hashlib.sha256(prepared['config'].encode()).hexdigest()==plan['configHash'],'effective config'
    assert w['uid']==w['gid']==22002 and w['groups']==[22002],'worker identity'
    assert all(x in w['status'] for x in ['CapEff:\t0000000000000000','CapBnd:\t0000000000000000','NoNewPrivs:\t1']),'worker privilege'
    assert w['limits']=={'cpu.max':'200000 100000','memory.max':'4294967296','pids.max':'256'},'actual cgroup limits'
    network=w['network'];assert network['namespace']!=network['managerNamespace'] and [x['ifname'] for x in network['links']]==['lo'] and network['routes4']==network['routes6']==[],'network boundary'
    assert w['native']['processObservation']['pid']==w['native']['pid'] and w['native']['processObservation']['cgroup']=='0::'+w['cgroup']+'\n','CLI PID/service link'
    assert w['calls'][0]['stdout']=='v22.19.0\n' and w['calls'][1]['stdout']=='codex-cli 0.167.0-alpha.3.2\n','versions'
    assert len(w['calls'])==3 and all(x['exitCode']==0 and not x['truncated'] and not x['timedOut'] for x in w['calls']),'discovery'
    assert w['sandboxAttempts']==result['sandboxAttempts']==1 and result['cliDiscoveryCalls']==2,'native count'
    assert outer['seconds']<120 and w['native']['seconds']<15,'observed time limits'
    assert verdict(w,outer)==result['observation']=='blocked-before-payload','observation changed'
    assert w['native']['stdout']=='' and w['native']['exitCode']==1 and w['outputContent'] is None,'payload did not complete'
    assert w['native']['stderr']=='error building bubblewrap command: Read-only file system (os error 30)\n','raw blocker'
    cleanup=read('prepared/cleanup.json');post=read('post-cleanup.json')
    assert cleanup['cleanupStatus']=='complete' and cleanup['vmAbsent'] and cleanup['rootAbsent'] and cleanup['errors']==[],'VM cleanup'
    assert post['watchdogAlive'] is False and post['rootExists'] is False,'post-cleanup'
    commands=[json.loads(p.read_text()) for p in (root/'prepared').glob('command-*.json')]
    starts=[x for x in commands if x['args'][1:2]==['start']];assert len(starts)==1 and starts[0]['exitCode']==0,'VM count'
    for action in ['stop','delete','list']:
        rows=[x for x in commands if x['args'][1:2]==[action]]
        assert len(rows)==1 and rows[0]['exitCode']==0 and not rows[0]['truncated'] and not rows[0]['timedOut'],'VM cleanup command'
    assert read('initial-preparation/ownership.json')['vmRegistered'] is False,'initial preparation created a VM'
    assert read('preparation-correction.json')['budgetRestarted'] is False,'budget restart'
    assert all(result[k] is False for k in ['validSubmission','trialAuthorized','readyForTrial']) and result['fixtureOnly'] is True and result['results'] is None,'submission promotion'
    return {'observation':result['observation'],'vmStarts':1,'sandboxAttempts':1,'cliDiscoveryCalls':2,'payloadStarted':False,'cleanupStatus':'complete','indexedFiles':len(regular)-1,'diagnosticBytes':sum(p.stat().st_size for p in regular),'fullIsolationVerified':False}

if __name__=='__main__':print(json.dumps(verify(sys.argv[1]),indent=2))
