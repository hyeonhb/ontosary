"""Reproduce only frozen analysis; closing cleanup and complete index are separate evidence."""
import argparse,hashlib,json,pathlib,re,tarfile
from scope import verify as verify_scope,classify
from runtime_policy import verify,baseline_verify,normalize
from policy import RULE
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads(p.read_text())
FLAGS='CLONE_NEWNS|CLONE_NEWIPC|CLONE_NEWUSER|CLONE_NEWPID|CLONE_NEWNET|SIGCHLD'
def clones(trace):
 pending=set();rows=[]
 for line in trace.splitlines():
  pid=re.match(r'\[pid\s+(\d+)\]',line);pid=pid.group(1) if pid else 'main'
  if 'clone(child_stack=NULL, flags='+FLAGS+')' in line:
   if '<unfinished ...>' in line:pending.add(pid)
   rows.append({'parent':pid,'line':line,'child':int(m.group(1)) if (m:=re.search(r'= (\d+)\s*$',line)) else None})
  elif pid in pending and '<... clone resumed>' in line:
   pending.remove(pid);rows.append({'parent':pid,'line':line,'child':int(m.group(1)) if (m:=re.search(r'= (\d+)\s*$',line)) else None})
 return rows

def audit(work):
 work=pathlib.Path(work);historical=[]
 for item in read(work/'historical-scopes.json'):
  root=pathlib.Path(item['root'])/'snapshots';classify(root,item['analysis'],item['closing']);historical.append({'root':item['root'],'analysis':verify_scope(root,item['analysis']),'closing':len(item['closing'])})
 unchanged=read(work/'start-input-hashes.json')
 for name,digest in unchanged.items():assert sha(pathlib.Path(name).read_bytes())==digest,name
 snapshots=verify_scope(work/'snapshots',read(work/'analysis-scope.json'))
 units=[];diff=None;outcome='inconclusive';blocked=[];root=work/'guest';candidate_starts=0;applications=0
 if (work/'inputs.tar.gz').exists():
  manifest=read(work/'inputs.json');assert sha((work/'inputs.tar.gz').read_bytes())==manifest['archiveSha256']
  with tarfile.open(work/'inputs.tar.gz') as t:assert {m.name:sha(t.extractfile(m).read()) for m in t.getmembers() if m.isfile()}==manifest['members']
 for mode in ['baseline','candidate']:
  if not (root/mode/'state.json').exists():continue
  state=read(root/mode/'state.json');native=read(root/mode/'native.json') if (root/mode/'native.json').exists() else None
  started=(root/mode/'start-authorized.json').exists();candidate_starts+=int(mode=='candidate' and started)
  applications+=int(mode=='candidate' and native is not None and started)
  row={'mode':mode,'containerId':state.get('containerId'),'started':started,'state':state['state'],'cleanupDone':state.get('cleanupDone'),'terminationConfirmed':state.get('terminationConfirmed')}
  if native:
   pre=read(root/mode/'pre-execution.json');image=pre['image'];assert native['SnapshotInfo']['Parent']==image['chain'] and native['Labels']['nerdctl/image-digest']==image['target']
   for name in ['probe/probe.mjs','policy.toml']:assert pre['inputs']['/opt/ontosary-policy-retry/'+name]==sha((root/name).read_bytes())
   row.update(image=image,inputs=pre['inputs'])
  if (root/(mode+'-result.json')).exists():
   result=read(root/(mode+'-result.json'));term=read(root/mode/'termination.json');removed=read(root/mode/'removed.json')
   assert term['confirmed'] and term['kernel']['events']['populated']=='0' and not term['kernel']['members'] and term['runtimeState']['Pid']==0 and not term['runtimeState']['Running']
   assert all(removed[k] for k in ['containerAbsent','runtimeTaskAbsent','noPendingRequests','terminationBeforeCollection']) and removed['seconds']<120
   assert not any(state.get(k) for k in ['createPending','startPending','execPending']) and state['cleanupDone'] and state['state']=='finalized'
   assert all(result['parent'].values()) and result['nodeVersion']=='v22.19.0' and result['calls'][0]['stdout']=='codex-cli 0.167.0-alpha.3.2\n'
   assert all(result[k]==0 for k in ['credentialTransfers','logins','refreshes','providerRequests','modelCalls','trialRuns'])
   trace=result['calls'][-1]['stderr'];row.update(parent=result['parent'],seconds=removed['seconds'],payloadStarted=result['nativePayloadStarted'],cliExit=result['calls'][-1]['exitCode'],clones=clones(trace),bwrapExecLines=[l for l in trace.splitlines() if 'execve(' in l and ('/proc/self/fd/' in l or 'bwrap' in l)],traceArgs=result['calls'][-1]['args'])
  else:blocked.append(mode+':no-collected-result:'+str(state.get('blockReason')))
  units.append(row)
 if (root/'candidate/native.json').exists():
  b=read(root/'baseline/native.json');c=read(root/'candidate/native.json');bi=read(root/'baseline-identity.json');cs=read(root/'candidate/state.json');ci={'run':'/opt/ontosary-fixture/runs/'+cs['runId'],'shared':'/opt/ontosary-policy-retry','slice_name':cs['slice']}
  baseline_verify(b,read(work/'prior-native.json'),**bi);expected=json.loads(json.dumps(b['Spec']['linux']['seccomp']));expected['syscalls'].append(RULE);assert c['Spec']['linux']['seccomp']==expected==read(root/'candidate.json')
  left=normalize(b,**bi);right=normalize(c,**ci);left['linux']['seccomp']['syscalls'].append(RULE);differences=[]
  def compare(a,b,path=''):
   if type(a)!=type(b):differences.append({'path':path,'baseline':a,'candidate':b})
   elif isinstance(a,dict):
    for k in sorted(a.keys()|b.keys()):compare(a.get(k),b.get(k),path+'/'+k)
   elif isinstance(a,list):
    if len(a)!=len(b):differences.append({'path':path,'baselineLength':len(a),'candidateLength':len(b)})
    for i,(x,y) in enumerate(zip(a,b)):compare(x,y,path+'/'+str(i))
   elif a!=b:differences.append({'path':path,'baseline':a,'candidate':b})
  compare(left,right);diff={'exactSeccompAddedRule':RULE,'remainingSpecDifferences':differences,'candidateIdentity':ci,'baselineIdentity':bi,'preStartGatePassed':not differences}
  if differences:blocked.append('candidate-prestart-unlisted-hook-environment-path')
 if len(units)==2 and all('clones' in u for u in units):
  b=read(root/'baseline/native.json');c=read(root/'candidate/native.json');bi=read(root/'baseline-identity.json');ci=read(root/'candidate/policy-verification.json')['candidateIdentity']
  baseline_verify(b,read(work/'prior-native.json'),**bi);diff=verify(c,b,ci,bi);assert c['Spec']['linux']['seccomp']==read(root/'candidate.json')
  assert units[0]['image']==units[1]['image'] and units[0]['traceArgs']==units[1]['traceArgs']
  assert sum('EPERM' in r['line'] for r in units[0]['clones'])==2
  assert not units[0]['payloadStarted']
  positives=[r for r in units[1]['clones'] if r['child'] and r['child']>0]
  outcome='synthetic-payload-completed' if units[1]['payloadStarted'] and units[1]['cliExit']==0 else 'first-clone-passed-next-blocked' if positives else 'clone-still-denied' if any('EPERM' in r['line'] for r in units[1]['clones']) else 'inconclusive'
  authorization=read(work/'candidate-host-authorization.json');assert authorization['remainingSeconds']>0
  assert read(root/'candidate/policy-verification.json')['mono']<read(root/'candidate/start-authorized.json')['mono']
 else:blocked.append('pair-not-completed')
 cleanup=read(work/'removal/removal/cleanup.json') if (work/'removal/removal/cleanup.json').exists() else None
 if cleanup:
  for row in cleanup['rows']:
   if row['mode']=='candidate' and row['secondsSinceCreate']>120:blocked.append('candidate-container-removal-after-120-second-outer-bound')
 return {'outcome':outcome,'blockedReasons':blocked,'units':units,'actualPolicyDiff':diff,'candidateApplications':applications,'candidateSpecAssignments':int((root/'candidate/native.json').exists()),'postRunCleanup':cleanup,'candidateStarts':candidate_starts,'containers':len(units),'newVMs':1 if (work/'ownership.json').exists() else 0,'historical':historical,'snapshots':snapshots,'originalInputsUnchanged':len(unchanged),'fixtureOnly':True,'validSubmission':False,'trialAuthorized':False,'readyForTrial':False,'results':None,'R11':'unresolved','R12':'prior scope unchanged','credentialProviderModelTrial':0}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--work',required=True);a=p.parse_args();work=pathlib.Path(a.work);result=audit(work);(work/'audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
