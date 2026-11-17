"""Offline pair replay; an absent candidate never establishes policy effect."""
import argparse,copy,hashlib,json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'single-policy-test'),str(HERE.parent/'lifecycle')]
from policy_pair import authorize,trace_observation,recovered_unit
from verify_recovery import contents
from identity import RULE,compare,expected_legacy,RUNTIME_ENV
from scope import verify_index,registered_scope
from image_cache import key

def read(p):return json.loads(pathlib.Path(p).read_text())
def verify(host):
 host=pathlib.Path(host);plan=read(host/'plan.json');authorize(plan);units=read(host/'units.json') if (host/'units.json').exists() else []
 assert [u['mode'] for u in units]==['baseline','candidate'][:len(units)] and len(units)<=2
 assert not (host/'fixtures-complete.json').exists()
 recovered={};specs=[];seals=[];observations={};identities={};natives={}
 for path in host.glob('recovery-*.tar.gz'):
  files=contents(path);status=json.loads(files['export-status.json']);receipt=read(path.with_suffix('').with_suffix('.json'));assert receipt['evidenceStatus']==status['status'];assert hashlib.sha256(path.read_bytes()).hexdigest()==receipt['archiveSha256'];recovered[path.name]=files
  for rid,value in status['runs'].items():
   if not value['exportedResult']:assert not any(n.startswith('runs/'+rid+'/result/') for n in files)
 if (host/'image-artifact.json').exists():
  cache=read(host/'image-artifact.json');assert cache['builds']==cache['downloads']==0 and cache['importAttempts']==1 and key(cache['binding']['inputs'])==cache['binding']['key']
 if 'recovery-preparation.tar.gz' in recovered:
  files=recovered['recovery-preparation.tar.gz'];tools=json.loads(files['preparation/runtime-tools.json']);assert tools['environment']==RUNTIME_ENV and tools['deliveredInputHashes']==read(host/'input-transfer.json')['members']
  publications=json.loads(files['metadata-publication.json']);assert {x['name'] for x in publications}=={'image-export.json','input-members.json'} and all(x['managerUid']==0 and x['sourceUid']!=0 and x['mode']=='0o600' for x in publications)
  assert json.loads(files['import-verified.json'])['actualImage']==cache['binding']['image']
 prior=read(host/'prior-pair.json')['pairs']['baseline']
 for row in units:
  mode=row['mode'];files=recovered.get('recovery-unit-'+mode+'.tar.gz');prefix='runs/'+str(row.get('runId'))+'/'
  if not files or prefix+'state.json' not in files:assert not row.get('passed');continue
  state=json.loads(files[prefix+'state.json'])
  if prefix+'native.json' in files and prefix+'baseline-policy-verification.json' in files:
   n=json.loads(files[prefix+'native.json']);ident=json.loads(files[prefix+'identity.json']);natives[mode]=n;identities[mode]=ident
   expected,eid,migration=expected_legacy(prior['native'],prior['identity'],state['image']);eid['inputHashes']=ident['inputHashes'];expected['Spec']['process']['args']=['node','/probe/probe.mjs']
   actual=compare(n,expected,ident,eid,mode=='candidate');saved=json.loads(files[prefix+'baseline-policy-verification.json']);assert actual==saved['comparison'] and migration==saved['explicitLegacyMigration'];specs.append({'mode':mode,'accepted':actual['accepted']})
   if mode=='candidate':
    if prefix+'policy-verification.json' in files:assert compare(n,natives['baseline'],ident,identities['baseline'],True)==json.loads(files[prefix+'policy-verification.json'])
    else:assert not row.get('passed')
  if row.get('passed'):
   assert all(state.get(k) for k in ['serviceInactiveConfirmed','removalConfirmed','terminationConfirmed','unitFilesRemoved','cleanupDone']);assert not any(state.get(k) for k in ['createPending','startPending','execPending','discardVM']);assert row['secondsIncludingRecovery']<120
   seal=json.loads(files[prefix+'seal-receipt.json']);ref=json.loads(files[prefix+'reference.json']);raw=[json.loads(x) for x in files[prefix+'service-raw.jsonl'].splitlines()]
   assert seal['raw'] in raw and ref['phase']=='released' and seal['invocationId']==state['invocationId'];assert state['finalizedAt']['mono']<=seal['inactiveAtMono']<=seal['raw']['observed']['mono']<=ref['released']['mono']<=state['sealedAt']['mono']<=state['deadlines']['finish'];assert ref['acquired']['mono']<=state['invocationObserved']['mono'];seals.append(mode)
   fixture=json.loads(files[prefix+'result/fixture.json']);assert fixture['termination']==json.loads(files[prefix+'termination.json']);assert fixture['snapshot']['files']=={n[len(prefix+'result/'):]:{'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)} for n,b in files.items() if n.startswith(prefix+'result/') and n!=prefix+'result/fixture.json'}
   result=json.loads(files[prefix+'result/auxiliary/result.json']);observations[mode]=trace_observation(result)
   if (host/(mode+'-trace-analysis.json')).exists():assert read(host/(mode+'-trace-analysis.json'))==observations[mode] and read(host/(mode+'-observation.json'))==result
 if len(units)>1:
  assert observations['baseline']['status']=='clone-still-denied';profile=copy.deepcopy(natives['baseline']['Spec']['linux']['seccomp']);profile['syscalls'].append(RULE);assert profile==read(host/'candidate-profile.json');assert read(host/'candidate-profile-publication.json')['sha256']==hashlib.sha256(json.dumps(profile,sort_keys=True).encode()).hexdigest()
  assert units[0]['runId']!=units[1]['runId']
  if 'candidate' in observations:
   a=read(host/'baseline-observation.json');b=read(host/'candidate-observation.json');assert [(x['file'],x['args']) for x in a['calls']]==[(x['file'],x['args']) for x in b['calls']]
 status='inconclusive'
 if (host/'pair-complete.json').exists():
  done=read(host/'pair-complete.json');assert len(units)==2 and all(u.get('passed') for u in units) and len(seals)==2;status=observations['candidate']['status'];assert done['status']==status
 if (host/'cleanup.json').exists():
  cleanup=read(host/'cleanup.json')
  if cleanup['cleanupStatus']=='complete':assert cleanup['vmAbsent'] and cleanup['rootAbsent']
 return {'status':status,'baselineUnits':sum(x['mode']=='baseline' for x in units),'candidateUnits':sum(x['mode']=='candidate' for x in units),'candidateStarts':sum(x.get('state',{}).get('starts',0) for x in units if x['mode']=='candidate'),'passedUnits':sum(x.get('passed',False) for x in units),'wholeSpecsReplayed':specs,'sealsVerified':seals,'observations':observations,'recoveryArchives':len(recovered),'runtimeReexecuted':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--work');p.add_argument('--root');a=p.parse_args()
 if a.root:root=pathlib.Path(a.root);result={'index':verify_index(root),'semantic':verify(root/'host')}
 else:registered_scope(pathlib.Path(a.work));result=verify(a.work)
 print(json.dumps(result,indent=2))
