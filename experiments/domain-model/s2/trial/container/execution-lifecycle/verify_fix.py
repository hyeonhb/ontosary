"""Offline replay of the correction round, including blocked/partial outcomes."""
import argparse,hashlib,json,pathlib,sys,tarfile
HERE=pathlib.Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'single-policy-test'),str(HERE.parent/'lifecycle')]
from scope import registered_scope,verify_index
from verify_saved import archive
from identity import compare,expected_legacy,RUNTIME_ENV
from image_cache import key
from exporter import DIAGNOSTICS
sha=lambda b:hashlib.sha256(b).hexdigest()
def read(p):return json.loads(pathlib.Path(p).read_text())
def verify(host):
 host=pathlib.Path(host);plan=read(host/'plan.json');result=read(host/'analysis-result.json');assert plan['maximumUnits']==7 and plan['conditionalPair']==[]
 assert all(plan[k] is False for k in ['validSubmission','trialAuthorized','readyForTrial']) and plan['fixtureOnly'] and plan['results'] is None
 units=read(host/'units.json') if (host/'units.json').exists() else [];assert len(units)<=7 and len({r['mode'] for r in units})==len(units)
 assert [r['mode'] for r in units]==plan['fixtures'][:len(units)]
 assert result['registeredUnits']==len(units) and result['expectedOutcomesPassed']==sum(r.get('passed',False) for r in units)
 if (host/'image-artifact.json').exists():
  cached=read(host/'image-artifact.json');binding=cached['binding'];assert key(binding['inputs'])==binding['key'] and binding['output']==cached['artifact']['actual']
  assert cached['builds']<=1 and cached['downloads']==0 and cached['importAttempts']==1
  if binding['provenance']['kind']=='validated-legacy-link':assert cached['builds']==0
 if not (host/'guest-evidence.tar.gz').exists():
  assert not (host/'fixtures-complete.json').exists();return {'actualUnits':len(units),'passed':0,'runtimeReexecuted':False,'guestEvidenceAvailable':False}
 files=archive(host/'guest-evidence.tar.gz');index=read(host/'guest-export-index.json');assert {n:{'sha256':sha(b),'bytes':len(b)} for n,b in files.items()}==index
 export= json.loads(read(host/'export-result.json')['output']);assert len(index)+1<=1024 and sum(len(b) for b in files.values())+(host/'guest-export-index.json').stat().st_size<=16*1024*1024
 assert export['sha256']==sha((host/'guest-evidence.tar.gz').read_bytes())
 status=json.loads(files['export-status.json']);assert status['workerOriginalsRead'] is False
 inputs=archive(host/'inputs.tar.gz');transfer=read(host/'input-transfer.json');assert {n:sha(b) for n,b in inputs.items()}==transfer['members'] and sha((host/'inputs.tar.gz').read_bytes())==transfer['archiveSha256']
 prior=read(host/'prior-pair.json')['pairs']['baseline'];replayed=0
 for row in units:
  if not row.get('runId'):continue
  prefix='runs/'+row['runId']+'/';state=json.loads(files[prefix+'state.json'])
  assert state['runId']==row['runId']
  for name in files:
   if not name.startswith(prefix):continue
   rel=name[len(prefix):];assert rel.split('/')[0] in DIAGNOSTICS or rel.startswith('result/')
  if not status['runs'][row['runId']]['exportedResult']:assert not any(n.startswith(prefix+'result/') for n in files)
  else:
   fixture=json.loads(files[prefix+'result/fixture.json']);assert fixture['termination']==json.loads(files[prefix+'termination.json'])
   assert {n[len(prefix+'result/'):]:index[n] for n in files if n.startswith(prefix+'result/') and n!=prefix+'result/fixture.json'}==fixture['snapshot']['files']
  if prefix+'baseline-policy-verification.json' in files:
   native=json.loads(files[prefix+'native.json']);ident=json.loads(files[prefix+'identity.json']);expected,eid,migration=expected_legacy(prior['native'],prior['identity'],state['image']);eid['inputHashes']=ident['inputHashes'];expected['Spec']['process']['args']=['/missing-fixture-entrypoint' if row['mode']=='start-failure' else 'node','/probe/fixture.mjs',row['mode']]
   actual=compare(native,expected,ident,eid);saved=json.loads(files[prefix+'baseline-policy-verification.json']);assert actual==saved['comparison'] and migration==saved['explicitLegacyMigration'];replayed+=1
   if row.get('passed'):assert actual['accepted'] and native['Spec']['process']['apparmorProfile']=='nerdctl-default'
  if row.get('passed'):
   assert all(state[k] for k in ['terminationConfirmed','removalConfirmed','cleanupDone','serviceInactiveConfirmed','unitFilesRemoved']) and not any(state.get(k) for k in ['createPending','startPending','execPending'])
   assert state['sealedAt']['mono']<=state['deadlines']['finish'] and row['seconds']<120
 if units and units[0].get('passed'):
  tools=json.loads(files['preparation/runtime-tools.json']);assert tools['environment']==RUNTIME_ENV and tools['beforeContainerCreate'] and tools['deliveredInputHashes']==transfer['members']
  imported=json.loads(files['import-verified.json']);assert imported['actualImage']==read(host/'image-artifact.json')['binding']['image']
 return {'actualUnits':len(units),'passed':sum(r.get('passed',False) for r in units),'fullSpecsReplayed':replayed,'exportMembers':len(files),'runtimeReexecuted':False,'guestEvidenceAvailable':True}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--work');p.add_argument('--root');a=p.parse_args()
 if a.root:
  root=pathlib.Path(a.root);out={'index':verify_index(root),'semantic':verify(root/'host')}
 else:registered_scope(pathlib.Path(a.work));out=verify(a.work)
 print(json.dumps(out,indent=2))
