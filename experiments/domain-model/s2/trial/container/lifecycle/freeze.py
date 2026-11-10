#!/usr/bin/env python3
"""Package/verify the completed fixture round. Never starts a runtime."""
import argparse,gzip,hashlib,io,json,pathlib,re,shutil,tarfile

def sha(data):return hashlib.sha256(data).hexdigest()
def members(archive):
    records={}
    with tarfile.open(archive) as t:
        for item in t.getmembers():
            name=pathlib.PurePosixPath(item.name)
            assert not name.is_absolute() and '..' not in name.parts and (item.isfile() or item.isdir())
            if item.isfile():
                raw=t.extractfile(item).read();records[name.as_posix()]={'sha256':sha(raw),'bytes':len(raw)}
    return records

def verify(out):
    manifest=json.loads((out/'manifest.json').read_text());repo=pathlib.Path(__file__).resolve().parents[6]
    for name,digest in manifest['evidence'].items():assert sha((out/name).read_bytes())==digest,name
    for name,files in manifest['archives'].items():assert members(out/name)==files,name
    for name,digest in manifest['implementation'].items():assert sha((repo/name).read_bytes())==digest,name
    for archive in ['guest-initial.tar.gz','guest-final.tar.gz']:
        with tarfile.open(out/archive) as t:
            entries={pathlib.PurePosixPath(i.name).as_posix():i for i in t.getmembers() if i.isfile()}
            image=json.loads(t.extractfile(entries['image.json']).read())
            for name,key in [('environment/manifest.oci','target'),('environment/config.oci','config')]:assert 'sha256:'+sha(t.extractfile(entries[name]).read())==image[key]
            if archive=='guest-final.tar.gz':
                selected=json.loads((out/'selected.json').read_text());audit=json.loads(t.extractfile(entries['audit.json']).read())
                assert len(audit['rows'])==len(selected)==25
                assert {r['runId'] for r in selected}=={r['runId'] for r in audit['rows']}
                for row in selected:
                    prefix='runs/'+row['runId']+'/'
                    state=json.loads(t.extractfile(entries[prefix+'state.json']).read())
                    assert state['cleanupDone'] and state['terminationConfirmed'] and state['image']==image
                    if state['state']=='blocked':
                        assert not any(n.startswith(prefix+'result/') for n in entries)
                        if state['mode']=='publish-supervisor':assert prefix+'quarantined-result/fixture.json' in entries
                    else:
                        result=json.loads(t.extractfile(entries[prefix+'result/fixture.json']).read())
                        assert result['fixtureOnly'] and result['validSubmission'] is False
                        assert result['termination']['containerId']==state['containerId']
                        for name,item in result['snapshot']['files'].items():
                            raw=t.extractfile(entries[prefix+'result/'+name]).read();assert sha(raw)==item['sha256'] and len(raw)==item['bytes']
    assert manifest['fixtureOnly'] and not manifest['trialAuthorized'] and manifest['R11']=='unresolved'
    print(json.dumps({'status':manifest['status'],'evidenceFiles':len(manifest['evidence']),'archiveFiles':sum(len(x) for x in manifest['archives'].values()),'implementationFiles':len(manifest['implementation'])}))

def create(work,out):
    assert not out.exists();out.mkdir(parents=True)
    repo=pathlib.Path(__file__).resolve().parents[6]
    for src,dest in [('guest.tar.gz','guest-initial.tar.gz'),('guest-final.tar.gz','guest-final.tar.gz')]:shutil.copyfile(work/src,out/dest)
    normalizations={};rawdir=out/'raw';rawdir.mkdir()
    sources=[p for p in work.iterdir() if p.is_file() and p.suffix in ['.log','.json'] and p.name not in ['selected.json','metrics.json','cost.json']]
    sources += [p for folder in work.glob('probes-*') for p in folder.rglob('*') if p.is_file()]
    for source in sorted(sources):
        original=source.read_bytes();text=original.decode()
        for before,after in [(str(repo),'<repo>'),(str(pathlib.Path.home())+'/Library/Caches','<host-cache>'),(str(pathlib.Path.home()),'<host-home>'),('/home/hyeon.guest','<guest-home>'),('황보현','<host-display-name>'),('hyeon','<host-user>')]:text=text.replace(before,after)
        text=re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]','',text)
        text='\n'.join(line.rstrip() for line in text.splitlines()).rstrip()+'\n' if text else ''
        relative=source.relative_to(work);destination=rawdir/relative;data=text.encode()
        if source.suffix=='.jsonl' or len(data)>65536:destination=destination.with_name(destination.name+'.gz');encoded=gzip.compress(data,mtime=0)
        else:encoded=data
        destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(encoded)
        normalizations[destination.relative_to(out).as_posix()]={'originalSha256':sha(original),'normalizedSha256':sha(data),'encoding':'gzip' if destination.suffix=='.gz' else 'utf8'}
    for name in ['selected.json','metrics.json','cost.json']:shutil.copyfile(work/name,out/name)
    code={}
    for p in (work/'versions').rglob('*'):
        if p.is_file():code['versions/'+p.relative_to(work/'versions').as_posix()]=p
    for p in sorted(work.glob('*.py')):code['host-tools/'+p.name]=p
    for name in ['Dockerfile','lima.yaml']:code['inputs/'+name]=pathlib.Path(__file__).parent.parent/name
    for p in pathlib.Path(__file__).parent.iterdir():
        if p.is_file():code['final-tools/'+p.name]=p
    with tarfile.open(out/'executed-code.tar.gz','w:gz') as t:
        for name,p in sorted(code.items()):
            raw=p.read_bytes();item=tarfile.TarInfo(name);item.size=len(raw);item.mode=0o644;item.mtime=0;t.addfile(item,io.BytesIO(raw))
    archives={name:members(out/name) for name in ['guest-initial.tar.gz','guest-final.tar.gz','executed-code.tar.gz']}
    selected=json.loads((out/'selected.json').read_text());assert len(selected)==25
    assert json.loads((work/'cleanup-final.json').read_text())['status']=='cleanup-passed'
    assert '304 passed (304)' in (work/'60-final-host-check.log').read_text()
    assert 'Ran 13 tests' in (work/'36-python-tests.log').read_text() and 'Ran 3 tests' in (work/'48-cleanup-regressions.log').read_text()
    implementation_files=[p for p in pathlib.Path(__file__).parent.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    implementation_files += [pathlib.Path(__file__).parent.parent/name for name in ['Dockerfile','lima.yaml']]
    implementation_files += [repo/'tests/s2-lifecycle.test.ts']
    implementation={p.resolve().relative_to(repo).as_posix():sha(p.read_bytes()) for p in implementation_files}
    manifest={'status':'fixture-boundary-passed','baseCommit':'25c2d310f86a2275dae6746e01a44732deb7ffe0','fixtureOnly':True,'selectedFinalRuns':25,'requiredRuns':24,'additionalPublicationDeathRuns':1,'hostTests':304,'pythonTests':16,'R11':'unresolved','R12':'existing scope unchanged','trialAuthorized':False,'readyForTrial':False,'results':None,'providerCalls':0,'trialRuns':0,'implementation':implementation,'archives':archives,'exports':normalizations,'evidence':{p.relative_to(out).as_posix():sha(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file()},'normalization':'Guest and executed-code archives preserve exact bytes; no credentials/host homes were present. Host logs redact local identities/paths and ANSI/trailing whitespace. Large logs are losslessly gzip encoded after normalization. Archive members are individually hashed.'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n');verify(out)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--verify',type=pathlib.Path);parser.add_argument('--work',type=pathlib.Path);parser.add_argument('--out',type=pathlib.Path);args=parser.parse_args()
    if args.verify:verify(args.verify)
    else:
        if not args.work or not args.out:parser.error('--work and --out are required for creation')
        create(args.work,args.out)
