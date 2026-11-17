import copy,hashlib,json,pathlib,sys,tarfile
root=pathlib.Path.cwd();code=root/'experiments/domain-model/s2/trial/container';sys.path[:0]=[str(code/'execution-lifecycle'),str(code/'single-policy-test'),str(code/'lifecycle')]
from verify_recovery import contents
from policy_pair import trace_observation,RULE
h=root/'experiments/domain-model/s2/verification/2026-11-17-policy-pair/host';ev=h.parent
read=lambda p:json.loads(p.read_text())
def digest(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
s={'reviewedHead':'7a5eb53','runtimeExecutions':0}
with tarfile.open(ev/'final-source.tar.gz') as t:
 rows=[m for m in t if m.isfile()];assert all((code/m.name).read_bytes()==t.extractfile(m).read() for m in rows);s['finalSourceFilesMatched']=len(rows)
transfer=read(h/'input-transfer.json');assert digest(h/'inputs.tar.gz')==transfer['archiveSha256']
with tarfile.open(h/'inputs.tar.gz') as t:
 entries={m.name:t.extractfile(m).read() for m in t if m.isfile()};assert {n:hashlib.sha256(b).hexdigest() for n,b in entries.items()}==transfer['members'];assert all((code/n).read_bytes()==b for n,b in entries.items() if (code/n).is_file());s['inputMembersMatched']=len(entries)
initial=read(h/'start-inventory.json');changed=[n for n,v in initial.items() if not (root/n).exists() or digest(root/n)!=(v.get('sha256') if isinstance(v,dict) else v)];final=read(h/'final-input-verification.json');assert sorted(changed)==sorted(final['intentionalChangedFiles']);s.update(initialFiles=len(initial),unchangedFiles=len(initial)-len(changed),changedFiles=changed)
plan=read(h/'plan.json');saved=read(h/'image-artifact.json');s['retainedArtifacts']=[]
for r in [*read(h/'artifact-acquisitions.json'),saved['artifact']]:
 p=pathlib.Path(r['path']);actual={'sha256':digest(p),'bytes':p.stat().st_size};assert actual==r['actual'];s['retainedArtifacts'].append(actual)
assert read(pathlib.Path(plan['store'])/('.image-key-'+saved['binding']['key']+'.json'))==saved['binding'];s['imageBindingMatched']=True
natives={};observations={};unitrows=[]
for unit in read(h/'units.json'):
 mode=unit['mode'];files=contents(h/('recovery-unit-'+mode+'.tar.gz'));prefix='runs/'+unit['runId']+'/';natives[mode]=json.loads(files[prefix+'native.json']);observations[mode]=json.loads(files[prefix+'result/auxiliary/result.json']);assert observations[mode]==read(h/(mode+'-observation.json'))
 state=json.loads(files[prefix+'state.json']);unitrows.append({'mode':mode,'starts':state['starts'],'probeExitCode':state['exitCode'],'sandboxExitCode':observations[mode]['calls'][-1]['exitCode'],'payloadStarted':observations[mode]['nativePayloadStarted'],'seconds':unit['secondsIncludingRecovery'],'sealed':state['serviceInactiveConfirmed']})
a=copy.deepcopy(natives['baseline']['Spec']['linux']['seccomp']);a['syscalls'].append(RULE);assert a==natives['candidate']['Spec']['linux']['seccomp'];s['exactOneAddedRule']=True
trace=observations['candidate']['calls'][-1]['stderr'];lines=trace.splitlines();manual=read(h/'trace-review.json');assert hashlib.sha256(trace.encode()).hexdigest()==manual['traceSha256'];assert all(lines[e['line']-1]==e['raw'] for e in manual['excerpts'])
assert '[pid    41] clone(' in lines[63] and lines[63].endswith('/usr/bin/strace: Process 42 attached') and lines[64]==') = 42';assert '[pid    42] mount(' in lines[109] and '= -1 EPERM' in lines[109]
assert '[pid    43] clone(' in lines[131] and lines[131].endswith(') = 44');assert '[pid    44] mount(' in lines[177] and '= -1 EPERM' in lines[177]
assert trace_observation(observations['baseline'])['status']=='clone-still-denied';assert trace_observation(observations['candidate'])['status']=='inconclusive'
derived=copy.deepcopy(observations['candidate']);needle='/usr/bin/strace: Process 42 attached\n';assert trace.count(needle)==1;derived['calls'][-1]['stderr']=trace.replace(needle,'');derived_status=trace_observation(derived)['status'];assert derived_status=='first-clone-passed-next-blocked'
s.update(units=unitrows,traceHash=manual['traceSha256'],manualExcerptsMatched=len(manual['excerpts']),automaticStatus='inconclusive',independentRawObservation='first-clone-passed-next-blocked',temporaryDerivedStringStatus=derived_status,originalTraceUnchanged=True,lsmCauseConfirmed=False)
s['cleanup']=read(h/'cleanup.json');s['cost']=read(h/'cost.json');print(json.dumps(s,indent=2))
