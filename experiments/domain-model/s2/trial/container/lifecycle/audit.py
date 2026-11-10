"""Guest independent evidence audit, after probes; never grants submission rights."""
import hashlib,json,os,pathlib,stat,sys
from common import *

def scan(root):
    files={};directories=[]
    for parent,dirs,names in os.walk(root):
        dirs.sort();names.sort()
        for d in dirs:directories.append((pathlib.Path(parent)/d).relative_to(root).as_posix())
        for name in names:
            p=pathlib.Path(parent)/name;st=p.lstat()
            assert stat.S_ISREG(st.st_mode) and st.st_nlink==1
            files[p.relative_to(root).as_posix()]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':st.st_size}
    return files,sorted(directories)

def audit(rid):
    run=runpath(rid);s=read(run/'state.json');events=[json.loads(l) for l in (run/'events.jsonl').read_text().splitlines()];mode=s['mode']
    assert s['cleanupDone'] and s['terminationConfirmed'] and s['admissionClosed']
    snap=cgroup_snapshot(run);assert snap['events']['populated']=='0' and not snap['members']
    group=pathlib.Path(s['cgroup']);limits={n:(group/n).read_text() for n in ['cpu.max','memory.max','pids.max']}
    assert limits['cpu.max'].strip()=='200000 100000' and limits['memory.max'].strip()==str(4*1024**3) and limits['pids.max'].strip()=='256'
    native=read(run/'container-native.json');spec=native['Spec'];process=spec['process']
    assert process['user']['uid']==process['user']['gid']==1000 and process['noNewPrivileges']
    assert all(not caps for caps in process['capabilities'].values()) and spec['root']['readonly']
    assert any(n['type']=='cgroup' for n in spec['linux']['namespaces'])
    mounts=spec['mounts'];binds={m['destination']:m['source'] for m in mounts if m['destination'] in ['/source','/auxiliary','/snapshot']}
    assert binds['/source']==str(run/'source') and binds['/auxiliary']==str(run/'auxiliary')
    forbidden=['/opt/ontosary-fixture/control','/opt/ontosary-fixture/previous','/run/containerd/containerd.sock']
    assert not any(any(m['source'].startswith(p) for p in forbidden) for m in mounts)
    assert native['Labels']['nerdctl/networks']=='["none"]'
    cgmount=[m for m in mounts if m['destination']=='/sys/fs/cgroup'][0];assert 'ro' in cgmount['options']
    access=read(run/'source'/'access.json');checks=access['checks'];assert checks[0]['name']=='self-read' and checks[0]['success']
    assert all(not c['success'] for c in checks[1:]);assert '0::/\n'==access['cgroup']
    for key in ['CapInh','CapPrm','CapEff','CapBnd','CapAmb']:assert key+':\t0000000000000000' in access['status']
    assert 'NoNewPrivs:\t1' in access['status']
    for key in ['Uid','Gid']:assert key+':\t1000\t1000\t1000\t1000' in access['status']
    canaries=read(run/'canaries.json');assert len(canaries)==4 and canaries[-1]['isSocket']
    for c in canaries:assert pathlib.Path(c['path']).stat().st_ino==c['inode']
    ready=read(run/'worker-ready.json');assert ready['kernel']['events']['populated']=='1'
    if mode in ['normal','timeout','wrapper','supervisor','kill-error','query-error','control','race']:
        assert ready['writers'] and ready['writerBytes']>0
        statuses=[dict(line.split(':',1) for line in m['status'].splitlines() if ':' in line) for m in ready['kernel']['members']]
        for writer in ready['writers'].values():
            matched=[(member,st) for member,st in zip(ready['kernel']['members'],statuses) if int(st['NSpid'].split()[-1])==writer['pid']]
            assert len(matched)==1
            member,st=matched[0]
            assert int(st['NSpgid'].split()[-1])==int(st['NSsid'].split()[-1])==writer['pid']
            if 'fds' in member:
                assert any(fd['target']=='/source/writer.log' for fd in member['fds'].values())
                assert member['namespaces']['cgroup']!=read(run/'supervisor-ready.json')['cgroupNamespace']
                if mode=='timeout':assert stat.S_ISFIFO(member['fds']['1']['mode'])
            else:raise AssertionError('writer FD evidence missing')
        assert all(m['procCgroup'].strip().removeprefix('0::').startswith(s['cgroup'].removeprefix('/sys/fs/cgroup')+'/') for m in ready['kernel']['members'])
    assert s['cgroup'].removeprefix('/sys/fs/cgroup') not in read(run/'supervisor-ready.json')['cgroup']
    terms=[e['termination'] for e in events if e['kind']=='stopped-confirmed'];term=terms[0]
    stop_seconds=term['confirmedAt']['mono']-term['stopRequested']['mono'];assert 0<=stop_seconds<=10
    if mode=='timeout':assert 0<=term['stopRequested']['mono']-s['deadlineMono']<.5
    if mode=='wrapper':
        lease=read(run/'lease.json');assert 5<=term['stopRequested']['mono']-lease['mono']<5.5;assert term['stopRequested']['mono']<s['deadlineMono']
        receipts=[e for e in events if e['kind']=='heartbeat'];assert max(e['receipt']['mono'] for e in receipts)==lease['mono']
    if mode=='control':assert 'LATE' in (run/'source/writer.log').read_text() and list((run/'source').glob('late-*'))
    if mode=='race':assert sum(e['kind']=='cleanup-enter' for e in events)>=3
    if s['state']=='finalized':
        result=read(run/'result/fixture.json');assert result['fixtureOnly'] and result['validSubmission'] is False
        assert result['termination']['runId']==rid and result['termination']['containerId']==s['containerId'] and result['termination']['image']==s['image']
        expected={};dirs=[]
        for n in ['source','auxiliary']:
            files,subdirs=scan(run/n);expected.update({n+'/'+k:v for k,v in files.items()});dirs += [n+'/'+d for d in subdirs]
            assert (files,subdirs)==scan(run/'result'/n)
        assert expected==result['snapshot']['files'] and sorted(dirs)==result['snapshot']['directories']
        assert result['snapshot']['fileCount']==len(expected) and result['snapshot']['bytes']==sum(f['bytes'] for f in expected.values())
        assert (run/'result/source/original.txt').read_bytes()==b'modified\0bytes'
        assert (run/'result/source/added.bin').read_bytes()==bytes([0,1,2,255])
        assert (run/'result/auxiliary/note.txt').read_bytes()==b'auxiliary'
        baseline=read(run/'baseline.json')['files'];assert result['delta']=={'added':sorted(expected.keys()-baseline.keys()),'deleted':['source/delete.txt'],'modified':['source/original.txt']}
        assert len([e for e in events if e['kind']=='finalized'])==1
        assert result['classification']==('normal-fixture' if s['reason']=='exit' and s['exitCode']==0 else 'diagnostic')
        assert s['collectionFinished']['mono']-s['collectionStarted']['mono']<=10
        for item in [run/'result',*(run/'result').rglob('*')]:assert item.stat().st_uid==0 and item.stat().st_mode&0o222==0
        if mode=='consume':
            consumed=read(run/'source/consume.json');assert next(c for c in consumed if c['name']=='snapshot-read')['value'] is True
            assert not next(c for c in consumed if c['name']=='snapshot-write')['success']
            assert set(next(m for m in mounts if m['destination']=='/snapshot')['options']) & {'ro','rro'}
            assert any(line.split()[4]=='/snapshot' and 'ro' in line.split()[5].split(',') for line in access['mountinfo'].splitlines())
            prior=pathlib.Path(s['snapshot']);expected_prior=read(prior/'fixture.json')['snapshot']['files'];actual_prior={}
            for name in ['source','auxiliary']:actual_prior.update({name+'/'+k:v for k,v in scan(prior/name)[0].items()})
            assert expected_prior==actual_prior
    else:
        assert s['state']=='blocked' and not (run/'result').exists() and not (run/'staging').exists()
        expected_error={'publish-supervisor':'supervisor-failed-after-publication','supervisor':'supervisor-failed','kill-error':'injected-kill-command-failure','query-error':'injected-state-query-failure','symlink':'nonregular','hardlink':'hardlink','fifo':'nonregular','socket':'nonregular','device':'nonregular','files':'file-count-limit','bytes':'byte-limit','depth':'path-depth-limit','copy-failure':'injected-copy-failure','logs':'workload-log-limit'}[mode]
        assert expected_error in s['blockReason'],s['blockReason']
    journal=command(run,['journalctl','-u',s['service'],'--no-pager'])[1];(run/'service-journal.log').write_text(journal)
    properties=command(run,['systemctl','show',s['service'],'-p','Result','-p','ExecMainStatus','-p','KillMode','-p','KillSignal','-p','Restart','-p','RuntimeMaxUSec','-p','TimeoutStopUSec'])[1];(run/'service-properties.txt').write_text(properties)
    assert 'KillSignal=9' in properties and 'Restart=no' in properties and 'RuntimeMaxUSec=40s' in properties
    row={'runId':rid,'mode':mode,'state':s['state'],'reason':s.get('reason'),'exitCode':s.get('exitCode'),'classification':s.get('classification'),'stopConfirmationSeconds':stop_seconds,'limits':limits,'independentChecks':'passed'}
    write(run/'audit.json',row);return row
if __name__=='__main__':
    rows=[audit(rid) for rid in sys.argv[1:]];write(ROOT/'audit.json',{'fixtureOnly':True,'rows':rows});print(json.dumps(rows,indent=2))
