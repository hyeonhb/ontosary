"""Offline reproduction of this stopped round; never starts a VM or runtime unit."""
import argparse,hashlib,json,pathlib,sys,tarfile,time
HERE=pathlib.Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'single-policy-test')]
from identity import compare,expected_legacy,normalize
from scope import registered_scope,verify_index
sha=lambda data:hashlib.sha256(data).hexdigest()
def read(p):return json.loads(pathlib.Path(p).read_text())
def archive(path):
 result={}
 with tarfile.open(path) as t:
  for m in t:
   if m.isdir():continue
   assert m.isfile() and m.name not in result and not pathlib.PurePosixPath(m.name).is_absolute() and '..' not in pathlib.PurePosixPath(m.name).parts,'archive-entry'
   result[m.name]=t.extractfile(m).read()
 return result

def verify(host):
 host=pathlib.Path(host);files=archive(host/'guest-evidence.tar.gz');inputs=archive(host/'inputs.tar.gz');transfer=read(host/'input-transfer.json')
 assert sha((host/'inputs.tar.gz').read_bytes())==transfer['archiveSha256']
 assert {n:sha(b) for n,b in inputs.items()}==transfer['members'],'input-transfer-members'
 linked=read(host/'execution-source-link.json');assert all(transfer['members'][n]==h for n,h in linked['helpers'].items())
 state_names=[n for n in files if n.startswith('runs/') and n.endswith('/state.json')];assert len(state_names)==1
 state=json.loads(files[state_names[0]]);prefix='runs/'+state['runId']+'/'
 get=lambda n:json.loads(files[prefix+n])
 native=get('native.json');identity=get('identity.json');term=get('termination.json');removed=get('removed.json');saved=get('baseline-policy-verification.json')
 prior=read(host/'prior-pair.json')['pairs']['baseline'];expected,expected_id,migration=expected_legacy(prior['native'],prior['identity'],state['image']);expected_id['inputHashes']=identity['inputHashes'];expected['Spec']['process']['args']=['node','/probe/fixture.mjs','normal-1']
 actual=compare(native,expected,identity,expected_id,False)
 assert actual==saved['comparison'] and migration==saved['explicitLegacyMigration'],'full-spec-replay'
 assert not actual['accepted'] and state['error']=='baseline-full-spec-difference'
 assert 'apparmorProfile' not in native['Spec']['process'] and prior['native']['Spec']['process']['apparmorProfile']=='nerdctl-default'
 changed=[]
 for dest in ['/materials','/probe','/home/runner/cli-state/config.toml']:
  new=next(m for m in native['Spec']['mounts'] if m['destination']==dest);old=next(m for m in prior['native']['Spec']['mounts'] if m['destination']==dest)
  assert 'rro' in old['options'] and 'rro' not in new['options'] and 'ro' in new['options'];changed.append(dest)
 assert state['starts']==0 and len(state['runtimeRequests'])==1 and state['runtimeRequests'][0]['kind']=='create'
 assert state['terminationConfirmed'] and state['removalConfirmed'] and state['serviceInactiveConfirmed'] and state['unitFilesRemoved'] and state['cleanupDone']
 assert not any(state.get(k) for k in ['createPending','startPending','execPending'])
 assert term['confirmed'] and term['kernel']['events']['populated']=='0' and not term['kernel']['members']
 assert term['containerId']==state['containerId']==native['ID'] and removed['containerAbsent'] and removed['taskAbsent'] and not removed['pending']
 assert state['registeredAt']['mono']<=term['stopRequested']['mono']<=term['confirmedAt']['mono']<=removed['confirmedAt']['mono']<=state['inactiveAtMono']<=state['sealedAt']['mono']<=state['deadlines']['finish']
 assert state['collectionStatus']=='suppressed' and state['recoveryRequired'] and not json.loads(files['gate.json'])['allowNext']
 assert not any(n.startswith(prefix+'result/') or n.startswith(prefix+'staging/') or n.endswith('start-authorized.json') for n in files)
 events=[json.loads(x) for x in files[prefix+'events.jsonl'].splitlines()]
 assert any(x.get('kind')=='command' and x['command'][-2:]==['rm',state['containerId']] and x['exitCode']==0 for x in events)
 assert any(x.get('kind')=='command' and x['command'][-3:]==['containers','list','-q'] and x['exitCode']==0 and not x['stdout'].strip() and x['start']['mono']>=term['confirmedAt']['mono'] for x in events)
 for folder in ['preparation','import']:
  manifest=files[folder+'/manifest.oci'];config=files[folder+'/config.oci'];assert 'sha256:'+sha(manifest)==state['image']['target'];assert 'sha256:'+sha(config)==state['image']['config'];cfg=json.loads(config);chain=cfg['rootfs']['diff_ids'][0]
  for layer in cfg['rootfs']['diff_ids'][1:]:chain='sha256:'+sha((chain+' '+layer).encode())
  assert chain==state['image']['chain']
 result=read(host/'analysis-result.json');assert result['registeredUnits']==1 and result['expectedOutcomesPassed']==0 and result['containerStarts']==0 and result['candidateStarts']==0
 return {'actualUnits':1,'startedUnits':0,'expectedOutcomesPassed':0,'requiredUnits':7,'guestArchiveFiles':len(files),'inputArchiveFiles':len(inputs),'transferredHelperHashes':len(linked['helpers']),'wholeSpecDiffReproduced':True,'missingAppArmor':True,'recursiveReadOnlyChanged':changed,'containerRemovedSeconds':state['removedAt']['mono']-state['registeredAt']['mono'],'unitSealedSeconds':state['sealedAt']['mono']-state['registeredAt']['mono'],'resultSuppressed':True,'nextBlocked':True,'actualBinaryIdentityVerified':False,'runtimeReexecuted':False}

def main():
 p=argparse.ArgumentParser();p.add_argument('--work');p.add_argument('--root');a=p.parse_args()
 if a.root:
  root=pathlib.Path(a.root);result={'index':verify_index(root),'semantic':verify(root/'host')}
 else:
  work=pathlib.Path(a.work);registered_scope(work);result=verify(work)
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
