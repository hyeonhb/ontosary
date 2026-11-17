"""Offline replay of per-stage diagnostics, exact Specs, service seals and cleanup."""
import argparse,hashlib,io,json,pathlib,sys,tarfile
HERE=pathlib.Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'single-policy-test'),str(HERE.parent/'lifecycle')]
from scope import registered_scope,verify_index
from identity import compare,expected_legacy,RUNTIME_ENV
from image_cache import key

def read(p):return json.loads(pathlib.Path(p).read_text())
def contents(path):
 with tarfile.open(path) as t:
  outer={m.name:t.extractfile(m).read() for m in t if m.isfile()}
 assert set(outer)=={'evidence.tar.gz','index.json'}
 with tarfile.open(fileobj=io.BytesIO(outer['evidence.tar.gz'])) as t:files={m.name:t.extractfile(m).read() for m in t if m.isfile()}
 index=json.loads(outer['index.json']);assert {n:{'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)} for n,b in files.items()}==index
 assert len(files)+1<=1024 and sum(len(x) for x in files.values())+len(outer['index.json'])<=16*1024*1024-8192
 return files

def verify(host):
 host=pathlib.Path(host);plan=read(host/'plan.json');units=read(host/'units.json') if (host/'units.json').exists() else [];replayed=[];seals=[];recovered={}
 assert plan['maximumUnits']==7 and plan['maximumImageBuilds']==0 and plan['cacheOnly']
 assert len(units)<=7 and [r['mode'] for r in units]==plan['fixtures'][:len(units)]
 for path in host.glob('recovery-*.tar.gz'):
  files=contents(path);status=json.loads(files['export-status.json']);receipt=read(path.with_suffix('').with_suffix('.json'));assert receipt['evidenceStatus']==status['status'];recovered[path.stem]=files
  assert status['workerOriginalsRead'] is False
  for rid,state in status['runs'].items():
   if not state['exportedResult']:assert not any(n.startswith('runs/'+rid+'/result/') for n in files)
 if (host/'image-artifact.json').exists():
  cached=read(host/'image-artifact.json');assert cached['builds']==cached['downloads']==0 and cached['importAttempts']==1;assert key(cached['binding']['inputs'])==cached['binding']['key']
 if (host/'recovery-preparation.tar.gz').exists():
  files=contents(host/'recovery-preparation.tar.gz');tools=json.loads(files['preparation/runtime-tools.json']);assert tools['environment']==RUNTIME_ENV;assert tools['deliveredInputHashes']==read(host/'input-transfer.json')['members']
  published=json.loads(files['metadata-publication.json']);assert {r['name'] for r in published}=={'image-export.json','input-members.json'}
  assert all(r['managerUid']==0 and r['sourceUid']!=r['managerUid'] and r['mode']=='0o600' for r in published)
  assert json.loads(files['import-verified.json'])['actualImage']==read(host/'image-artifact.json')['binding']['image']
 prior=read(host/'prior-pair.json')['pairs']['baseline']
 for row in units:
  path=host/('recovery-unit-'+row['mode']+'.tar.gz')
  if not path.exists():assert not row.get('passed');continue
  files=contents(path);rid=row.get('runId');prefix='runs/'+str(rid)+'/'
  if prefix+'state.json' not in files:assert not row.get('passed');continue
  state=json.loads(files[prefix+'state.json'])
  if prefix+'baseline-policy-verification.json' in files:
   native=json.loads(files[prefix+'native.json']);identity=json.loads(files[prefix+'identity.json']);expected,eid,migration=expected_legacy(prior['native'],prior['identity'],state['image']);eid['inputHashes']=identity['inputHashes'];expected['Spec']['process']['args']=['/missing-fixture-entrypoint' if row['mode']=='start-failure' else 'node','/probe/fixture.mjs',row['mode']]
   actual=compare(native,expected,identity,eid);saved=json.loads(files[prefix+'baseline-policy-verification.json']);assert actual==saved['comparison'] and migration==saved['explicitLegacyMigration'];replayed.append({'mode':row['mode'],'accepted':actual['accepted']})
  if row.get('passed'):
   assert state['serviceInactiveConfirmed'] and state['removalConfirmed'] and state['terminationConfirmed'] and state['unitFilesRemoved'] and state['cleanupDone']
   assert not any(state.get(k) for k in ['createPending','startPending','execPending']);assert row['secondsIncludingRecovery']<120
   seal=json.loads(files[prefix+'seal-receipt.json']);reference=json.loads(files[prefix+'reference.json']);raw=[json.loads(x) for x in files[prefix+'service-raw.jsonl'].splitlines()]
   assert reference['phase']=='released' and seal['invocationId']==state['invocationId'];assert seal['raw'] in raw
   assert state['finalizedAt']['mono']<=seal['inactiveAtMono']<=seal['raw']['observed']['mono']<=reference['released']['mono']<=state['sealedAt']['mono']<=state['deadlines']['finish'];assert reference['acquired']['mono']<=state['invocationObserved']['mono'];seals.append(row['mode'])
   if state['collectionStatus']=='collected':
    fixture=json.loads(files[prefix+'result/fixture.json']);assert fixture['termination']==json.loads(files[prefix+'termination.json'])
    assert {n[len(prefix+'result/'):]:{'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)} for n,b in files.items() if n.startswith(prefix+'result/') and n!=prefix+'result/fixture.json'}==fixture['snapshot']['files']
 if (host/'cleanup.json').exists():
  cleanup=read(host/'cleanup.json')
  if cleanup['cleanupStatus']=='complete':assert cleanup['vmAbsent'] and cleanup['rootAbsent']
 return {'actualUnits':len(units),'passed':sum(r.get('passed',False) for r in units),'wholeSpecsReplayed':replayed,'sealsVerified':seals,'recoveryArchives':len(recovered),'runtimeReexecuted':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--work');p.add_argument('--root');a=p.parse_args()
 if a.root:root=pathlib.Path(a.root);out={'index':verify_index(root),'semantic':verify(root/'host')}
 else:registered_scope(pathlib.Path(a.work));out=verify(a.work)
 print(json.dumps(out,indent=2))
