"""Offline comparison of actual archives/policies and observed syscall denial."""
import hashlib,json,pathlib,re,tarfile
sha=lambda b:hashlib.sha256(b).hexdigest()
PRIOR=pathlib.Path('experiments/domain-model/s2/verification/2026-11-11-cli-feasibility')
def read(root,name):return json.loads((root/name).read_text())
def member(archive,name):
 with tarfile.open(archive) as t:return t.extractfile(name).read()
def verify_inputs(archive,manifest):
 assert sha(archive.read_bytes())==manifest['archiveSha256'],'archive-hash-mismatch'
 with tarfile.open(archive) as t:actual={m.name:sha(t.extractfile(m).read()) for m in t.getmembers() if m.isfile()}
 assert actual==manifest['members'],'member-hash-mismatch'
def security(native):
 s=native['Spec'];p=s['process'];l=s['linux']
 return {'user':p['user'],'capabilities':p['capabilities'],'noNewPrivileges':p['noNewPrivileges'],'apparmorProfile':p.get('apparmorProfile'),'rootReadonly':s['root']['readonly'],'seccomp':l['seccomp'],'resources':l['resources'],'namespaceTypes':sorted(n['type'] for n in l['namespaces']),'cgroupMount':[m for m in s['mounts'] if m['destination']=='/sys/fs/cgroup']}
def verify_policy(native,prior):assert security(native)==security(prior),'policy-mismatch'
def verify(root):
 verify_inputs(root/'inputs.tar.gz',read(root,'inputs.json'))
 prior=json.loads(member(PRIOR/'host/diagnosis.tar.gz','diagnosis/container-native.json'))
 historical=json.loads(member(PRIOR/'host/preparation.tar.gz','auxiliary/discovery.json'))
 expected_binaries={p['file']:p['sha256'] for p in historical['binaries']}
 policy=pathlib.Path('experiments/domain-model/s2/trial/container/cli-feasibility/policy.toml').read_bytes()
 assert (root/'guest/policy.toml').read_bytes()==policy
 rows=[]
 for mode,image_dir in [('baseline','preparation'),('traced','trace-image')]:
  r=read(root,'guest/'+mode+'/output/result.json');native=read(root,'guest/'+mode+'/audit/native.json');done=read(root,'guest/'+mode+'/audit/complete.json');pre=read(root,'guest/'+mode+'/audit/pre-execution.json')
  verify_policy(native,prior)
  assert all(r['parent'].values()) and not r['nativePayloadStarted']
  assert r['calls'][0]['stdout']=='codex-cli 0.167.0-alpha.3.2\n' and r['nodeVersion']=='v22.19.0'
  assert all(expected_binaries[b['path']]==b['sha256'] for b in r['binaries'].values())
  assert pre['policySha256']==sha(policy) and pre['probeSha256']==sha((root/'guest/probe/probe.mjs').read_bytes())
  image=pre['image'];config=(root/'guest'/image_dir/'config.oci').read_bytes();manifest=(root/'guest'/image_dir/'manifest.oci').read_bytes()
  assert 'sha256:'+sha(config)==image['config'] and 'sha256:'+sha(manifest)==image['target']
  layers=json.loads(config)['rootfs']['diff_ids'];chain=layers[0]
  for layer in layers[1:]:chain='sha256:'+sha((chain+' '+layer).encode())
  assert chain==image['chain']==native['SnapshotInfo']['Parent'] and native['Labels']['nerdctl/image-digest']==image['target']
  assert done['removed'] and done['stoppedPid']==0 and done['seconds']<120 and done['waitExitCode']==0 and done['containerExitCode']==0
  assert r['calls'][-1]['exitCode']==1 and 'No permissions to create a new namespace' in r['calls'][-1]['stderr']
  for key in ['credentialTransfers','logins','refreshes','providerRequests','modelCalls','trialRuns']:assert r[key]==0
  rows.append({'mode':mode,'containerId':done['cid'],'seconds':done['seconds'],'image':image,'securitySha256':sha(json.dumps(security(native),sort_keys=True).encode()),'nonModelCLICalls':r['nonModelCLICalls']})
 base=read(root,'guest/preparation/config.oci')['rootfs']['diff_ids'];traceconfig=read(root,'guest/trace-image/config.oci')['rootfs']['diff_ids'];assert traceconfig[:-1]==base
 result=read(root,'guest/traced/output/result.json');trace=result['calls'][-1]['stderr'];flags='CLONE_NEWNS|CLONE_NEWIPC|CLONE_NEWUSER|CLONE_NEWPID|CLONE_NEWNET|SIGCHLD'
 calls=[l for l in trace.splitlines() if 'clone(child_stack=NULL, flags='+flags+') = -1 EPERM' in l];assert len(calls)==2
 assert not re.search(r'\b(clone3|unshare|setns)\(',trace)
 seccomp=prior['Spec']['linux']['seccomp'];clone=[r for r in seccomp['syscalls'] if 'clone' in r['names']];assert len(clone)==1 and clone[0]['action']=='SCMP_ACT_ALLOW'
 arg=clone[0]['args'][0];assert arg['index']==0 and arg['op']=='SCMP_CMP_MASKED_EQ' and arg['value']==0x7e020000 and arg.get('valueTwo',0)==0
 actual=0x78020011;assert actual & arg['value'] != arg.get('valueTwo',0)
 assert seccomp['defaultAction']=='SCMP_ACT_ERRNO'
 assert read(root,'kernel-log-correction.json')['mechanicalCorrection']==1
 for row in read(root,'kernel-log-correction.json')['rows']:assert row['stderr']=='' and row['stdout']=='-- No entries --\n'
 assert read(root,'removal/removal/cleanup.json')['status']=='guest-cleanup-passed'
 assert read(root,'host-cleanup.json')['rootAbsent']
 unchanged=0
 for name,digest in read(root,'start-input-hashes.json').items():
  assert sha(pathlib.Path(name).read_bytes())==digest,name;unchanged+=1
 snapshots=0
 for path in (root/'snapshots').glob('*.json'):
  meta=json.loads(path.read_text());verify_inputs(path.with_suffix('.tar.gz'),{'archiveSha256':meta['archiveSha256'],'members':{k:v['sha256'] for k,v in meta['files'].items()}});snapshots+=1
 return {'verdict':'proposal-ready','policyApplied':False,'units':rows,'preparationContainers':2,'nonModelCLICalls':4,'directBwrapVersionCalls':2,'tracerVersionCalls':1,'tracedCLIInvocations':1,'tracedNamespaceCloneFailures':calls,'observedFlagsHex':hex(actual),'observedFlagsDecimal':actual,'denyMaskHex':hex(arg['value']),'maskedFlagsHex':hex(actual & arg['value']),'traceHasClone3UnshareSetnsCalls':False,'kernelLSMDenialMatches':0,'lsmIndependentContribution':'unresolved','originalInputsUnchanged':unchanged,'snapshotsVerified':snapshots,'mechanicalCorrections':1,'runtimeRetries':0,'nativePayloadStarts':0,'trialAuthorized':False,'readyForTrial':False,'results':None}
if __name__=='__main__':
 root=pathlib.Path('work/s2-namespace-diagnosis');result=verify(root);(root/'audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
