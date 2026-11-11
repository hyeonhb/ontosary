"""Reconcile finite preparation evidence. A blocked command is never a boundary pass."""
import hashlib,json,pathlib,sys,tarfile
WORK=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else 'work/s2-cli-feasibility')
def read(name):return json.loads((WORK/name).read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
discovery=read('preparation/auxiliary/discovery.json');diagnosis=read('diagnosis/diagnostic-input/auxiliary/diagnosis.json')
assert discovery['calls'][0]['stdout']=='codex-cli 0.167.0-alpha.3.2\n'
assert discovery['versions']['node']=='v22.19.0'
calls=discovery['calls']+[c for c in diagnosis['calls'] if c['executable']=='codex'];assert len(calls)==10
assert sum(c['exitCode']==0 for c in calls)==6
assert all(diagnosis['parent'].values()) and not diagnosis['nativeAllowedWriteExists']
assert 'undefined profile' in diagnosis['calls'][1]['stderr']
assert 'No permissions to create a new namespace' in diagnosis['calls'][2]['stderr']
assert 'Operation not permitted' in diagnosis['calls'][3]['stderr']
assert diagnosis['calls'][2]['exitCode']==diagnosis['calls'][3]['exitCode']==1
assert '--strict-config` is not supported' in diagnosis['calls'][0]['stderr']
for x in [discovery,diagnosis]:
 for key in ['credentialTransfers','logins','refreshes','providerRequests','modelCalls','trialRuns']:assert x[key]==0
image=read('preparation/image.json');rows=[]
for directory in ['preparation/preparation','diagnosis/diagnosis']:
 native=read(directory+'/container-native.json');exited=read(directory+'/container-exited.json');gate=read(directory+'/gate.json');spec=native['Spec']
 assert native['Labels']['nerdctl/image-digest']==image['target'] and native['SnapshotInfo']['Parent']==image['chain']
 assert spec['process']['user']['uid']==spec['process']['user']['gid']==1000
 assert spec['process']['noNewPrivileges'] and spec['root']['readonly']
 assert not any(spec['process']['capabilities'].values())
 seccomp=spec['linux']['seccomp'];assert seccomp['defaultAction']=='SCMP_ACT_ERRNO'
 assert not any('unshare' in s['names'] and s['action']=='SCMP_ACT_ALLOW' for s in seccomp['syscalls'])
 assert exited['State']['Pid']==0 and not exited['State']['Running'] and gate['containerAbsent']
 rows.append({'id':native['ID'],'imageTarget':image['target'],'seccompDefault':seccomp['defaultAction'],'unshareAllowed':False,'apparmorProfile':spec['process'].get('apparmorProfile'),'stoppedAndRemoved':True})
manifest=(WORK/'preparation/preparation/manifest.oci').read_bytes();config=(WORK/'preparation/preparation/config.oci').read_bytes()
assert 'sha256:'+sha(manifest)==image['target'] and 'sha256:'+sha(config)==image['config']
layers=json.loads(config)['rootfs']['diff_ids'];chain=layers[0]
for layer in layers[1:]:chain='sha256:'+sha((chain+' '+layer).encode())
assert chain==image['chain']
snapshots=[];members=0
for p in sorted((WORK/'snapshots').glob('*.json')):
 meta=json.loads(p.read_text());archive=p.with_suffix('.tar.gz');assert sha(archive.read_bytes())==meta['archiveSha256']
 with tarfile.open(archive) as t:
  actual={m.name:sha(t.extractfile(m).read()) for m in t.getmembers() if m.isfile()}
 assert actual=={k:v['sha256'] for k,v in meta['files'].items()};members+=len(actual);snapshots.append(meta['id'])
for e in read('budget.json')['events']:
 meta=read('snapshots/'+e['snapshot']+'.json');assert meta['command']==e['command']
 # Wrapper timestamp is before snapshot; subprocess starts only after snapshot returns.
 assert e['monotonic']<=meta['hostMonotonic']<=e['monotonic']+e['seconds']
unchanged=0;documentation=[]
for name,digest in read('start-input-hashes.json').items():
 if sha(pathlib.Path(name).read_bytes())!=digest:
  assert name.endswith('/README.md'),name;documentation.append(name)
 else:unchanged+=1
assert read('removal/removal/cleanup.json')['status']=='guest-cleanup-passed'
assert read('host-cleanup.json')['rootAbsent']
result={'verdict':'blocked','nonModelCLICalls':len(calls),'successfulLocalCLICommands':6,'failedLocalCLICommands':4,'nativeSandboxEntryAttempts':2,'nativeSandboxPayloadsStarted':0,'parentPositiveBatches':1,'normalBoundaryRuns':0,'timeoutControls':0,'networkProbePairs':0,'registeredLifecycleUnits':0,'preparationContainers':rows,'snapshotsVerified':len(snapshots),'snapshotMembersVerified':members,'originalInputsUnchanged':unchanged,'documentationOnlyChanges':documentation,'trialAuthorized':False,'readyForTrial':False,'results':None,'R11':'unresolved'}
(WORK/'audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
