"""Only the explicitly approved, two-unit clone rule observation."""
import copy,hashlib,json,pathlib,re
from identity import RULE
from verify_recovery import contents,verify as historical_semantics
from scope import verify_index
PURPOSE='s2-clone-rule-pair-2026-11-17'
HISTORY=pathlib.Path('experiments/domain-model/s2/verification/2026-11-17-seal-recovery')
HISTORY_SHA='0a2a9693766d11f90d03822aea2a1b7b2cdff96ab7b30ebf93f20b0851f1f67c'
FLAGS='CLONE_NEWNS|CLONE_NEWIPC|CLONE_NEWUSER|CLONE_NEWPID|CLONE_NEWNET|SIGCHLD'
BINARY={'codex':'e7f91e14eab4ba3a0f65047c1757b593409d4ce791ccb6ac65c67c970dfed76f','bwrap':'0f543a7356ab343b4827222f910461d4196778f328b28acd6c126ef18e9557ab'}
def authorize(plan,history=True):
 if not (plan.get('purpose')==PURPOSE and plan.get('fixtures')==['baseline','candidate'] and plan.get('maximumUnits')==2 and plan.get('maximumVMs')==1 and plan.get('cacheOnly') is True and plan.get('maximumImageBuilds')==0 and plan.get('candidateRule')==RULE and plan.get('payloadSeconds')==15 and plan.get('phaseSeconds')=={'work':80,'remove':110,'finish':120}):raise RuntimeError('policy-pair-not-authorized')
 if any(plan.get(k) is not v for k,v in {'fixtureOnly':True,'validSubmission':False,'trialAuthorized':False,'readyForTrial':False,'results':None}.items()):raise RuntimeError('pair-trial-contract')
 expected={'path':str(HISTORY),'indexSha256':HISTORY_SHA,'requiredUnits':7,'passedUnits':7}
 if plan.get('historicalGate')!=expected:raise RuntimeError('pair-historical-binding')
 if history:
  if hashlib.sha256((HISTORY/'index.json').read_bytes()).hexdigest()!=HISTORY_SHA:raise RuntimeError('pair-historical-hash')
  verify_index(HISTORY);result=historical_semantics(HISTORY/'host')
  if result['passed']!=7 or len(result['sealsVerified'])!=7:raise RuntimeError('pair-historical-gate')
 return True

def trace_observation(result):
 if result.get('nodeVersion')!='v22.19.0' or {k:v['sha256'] for k,v in result.get('binaries',{}).items()}!=BINARY:raise RuntimeError('pair-binary-mismatch')
 if result.get('fixtureOnly') is not True or result.get('validSubmission') is not False or result.get('parent')!={'read':True,'write':True,'materialRead':True}:raise RuntimeError('pair-parent-or-contract')
 if any(result.get(k)!=0 for k in ['credentialTransfers','logins','refreshes','providerRequests','modelCalls','trialRuns']):raise RuntimeError('pair-forbidden-call')
 calls=result['calls']
 if len(calls)!=4 or calls[0]['stdout']!='codex-cli 0.167.0-alpha.3.2\n' or calls[-1]['file']!='/usr/bin/strace' or calls[-1].get('error') or calls[-1].get('signal'):raise RuntimeError('pair-command-observation')
 trace=calls[-1]['stderr'];pending={};executions={};clones=[];denied=[]
 for number,line in enumerate(trace.splitlines(),1):
  match=re.match(r'\[pid\s+(\d+)\]\s+(.*)',line)
  if not match:continue
  pid=int(match[1]);body=match[2]
  if 'execve(' in body and '["bwrap",' in body:executions[pid]={'pid':pid,'kind':'precheck' if '"/usr/bin/true"' in body else 'command-preparation','line':number,'raw':line}
  if 'clone(' in body and 'flags='+FLAGS in body:
   if '<unfinished ...>' in body:pending[pid]=(number,line);continue
   original=line;start=number
  elif '<... clone resumed>' in body and pid in pending:start,original=pending.pop(pid)
  else:
   if re.search(r'(mount|unshare|setns|pivot_root|chroot|setgroups|setresuid|setresgid)\(.*= -1 (EPERM|EACCES)',body):denied.append({'pid':pid,'line':number,'raw':line})
   continue
  ret=re.search(r'= (-?\d+)(?: (\w+))?',body)
  if ret:clones.append({'pid':pid,'line':start,'raw':original,'completion':line,'return':int(ret[1]),'errno':ret[2] if int(ret[1])<0 else None})
 for clone in clones:clone['kind']=executions.get(clone['pid'],{}).get('kind','unknown')
 children={x['return'] for x in clones if x['return']>0};next_denied=[x for x in denied if x['pid'] in children or x['pid'] in executions]
 known=len(clones)==2 and {x['kind'] for x in clones}=={'precheck','command-preparation'} and not pending
 status='inconclusive'
 if known and all(x['return']==-1 and x['errno']=='EPERM' for x in clones) and not result['nativePayloadStarted']:status='clone-still-denied'
 elif known and all(x['return']>0 for x in clones):
  if result['nativePayloadStarted'] and calls[-1]['exitCode']==0 and 'NATIVE_PAYLOAD_STARTED' in calls[-1]['stdout']:status='synthetic-payload-completed'
  elif next_denied and not result['nativePayloadStarted']:status='first-clone-passed-next-blocked'
 return {'status':status,'bwrapExecutions':list(executions.values()),'namespaceClones':clones,'nextDenied':next_denied,'pendingCloneObservations':list(pending),'traceSha256':hashlib.sha256(trace.encode()).hexdigest(),'commandExitCode':calls[-1]['exitCode'],'nativePayloadStarted':result['nativePayloadStarted'],'lsmCauseConfirmed':False}

def recovered_unit(r,mode,rid):
 receipt=json.loads((r.w/('recovery-unit-'+mode+'.json')).read_text())
 if receipt['evidenceStatus']!='complete':raise RuntimeError('pair-unit-recovery-incomplete')
 files=contents(r.w/receipt['artifact']);prefix='runs/'+rid+'/'
 state=json.loads(files[prefix+'state.json'])
 if state['mode']!=mode or state['runId']!=rid or not all(state.get(k) for k in ['serviceInactiveConfirmed','terminationConfirmed','removalConfirmed','unitFilesRemoved','cleanupDone']) or state['collectionStatus']!='collected':raise RuntimeError('pair-unit-not-sealed')
 result=json.loads(files[prefix+'result/auxiliary/result.json']);return files,prefix,result,trace_observation(result)

def execute(r):
 authorize(r.plan);r.phase='exploration'
 if not (r.w/'preparation-complete.json').exists():raise RuntimeError('pair-not-prepared')
 gate=json.loads((r.w/'local-gate.json').read_text())
 if not gate['passed'] or any(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()!=h for p,h in gate['codeHashes'].items()):raise RuntimeError('pair-code-changed-after-gate')
 if (r.w/'units.json').exists():raise RuntimeError('pair-already-attempted')
 rid=r.unit('baseline');files,prefix,result,observation=recovered_unit(r,'baseline',rid)
 rwrite=lambda name,value:(r.w/name).write_text(json.dumps(value,indent=2)+'\n')
 rwrite('baseline-observation.json',result);rwrite('baseline-trace-analysis.json',observation)
 if observation['status']!='clone-still-denied':raise RuntimeError('baseline-clone-mismatch')
 native=json.loads(files[prefix+'native.json']);profile=copy.deepcopy(native['Spec']['linux']['seccomp']);profile['syscalls'].append(copy.deepcopy(RULE));rwrite('candidate-profile.json',profile)
 data=json.dumps(profile,sort_keys=True);digest=hashlib.sha256(data.encode()).hexdigest()
 r.guest(['python3','-c',"import pathlib,sys,hashlib,os;p=pathlib.Path('/opt/ontosary-execution/candidate.json');assert not p.exists();b=sys.argv[1].encode();assert hashlib.sha256(b).hexdigest()==sys.argv[2];p.write_bytes(b);os.chmod(p,0o400)",data,digest])
 rwrite('candidate-profile-publication.json',{'sha256':digest,'derivedFromRun':rid,'rule':RULE})
 rid=r.unit('candidate');files,prefix,result,observation=recovered_unit(r,'candidate',rid)
 rwrite('candidate-observation.json',result);rwrite('candidate-trace-analysis.json',observation)
 rwrite('pair-complete.json',{'status':observation['status'],'baselineUnits':1,'candidateUnits':1,'runtimeRetries':0,'fixtureOnly':True,'validSubmission':False})
