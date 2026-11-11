"""End-of-round immutable source, deployment, model and evaluator identity verification."""
import gzip,hashlib,json,pathlib
repo=pathlib.Path.cwd();work=repo/'work/s2-linux-evaluation';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
start=json.loads((work/'start-input-hashes.json').read_text())
allowed={'experiments/domain-model/s2/trial/container/lifecycle/'+f for f in ['manager.py','supervisor.py','host_driver.py','README.md']}|{'experiments/domain-model/s2/README.md','experiments/domain-model/s2/trial/container/README.md'}
changed={f:{'before':h,'after':sha(repo/f)} for f,h in start.items() if sha(repo/f)!=h};assert set(changed)<=allowed,changed
source=pathlib.Path('/tmp/ontosary-vendure-preparation-20261108/vendure');inventory=json.loads(gzip.decompress((repo/'experiments/public-app/results/2026-11-08/vendure/inventory.json.gz').read_bytes()))
for row in inventory:assert sha(source/row['path'])==row['sha256']
manifest=json.loads((repo/'experiments/domain-model/v1/manifest.json').read_text())
for f,h in manifest['inputHashes'].items():assert sha(source/f)==h
bundle=repo/'experiments/domain-model/s2/results/2026-11-10-trial-preparation';m=json.loads((bundle/'bundle-manifest.json').read_text());assert len(m['files'])==84
for row in m['files']:assert sha(bundle/row['file'])==row['sha256']
model=json.loads((repo/'experiments/domain-model/results/2026-11-08-v2/model-after.json').read_text());assert len(model['items'])==12 and sum(len(i['relatedItems']) for i in model['items'])==16 and not model['approvedKnowledge']
execution=json.loads((repo/'experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix/execution/execution-manifest.json').read_text());assert all(m[k]==execution[k] for k in ['baselineId','modelId','bundleId']);assert execution['trialAuthorized'] is False and execution['readyForTrial'] is False and execution['results'] is None
oracle=json.loads(gzip.decompress((repo/'experiments/domain-model/s2/verification/2026-11-10-trial-preparation/oracle/baseline.json.gz').read_bytes()))
for f,h in oracle['evaluatorHashes'].items():assert sha(repo/'work/s2-build/evaluation'/f)==h
result={'status':'passed','trackedOriginalInputs':len(start),'allowedImplementationOrReadmeChanges':changed,'originalInventoryFiles':len(inventory),'originalCacheUnchanged':True,'deploymentFiles':84,'modelItems':12,'modelLinks':16,'approvedKnowledge':0,'baselineId':m['baselineId'],'modelId':m['modelId'],'bundleId':m['bundleId'],'evaluatorId':oracle['evaluatorId'],'evaluatorHashes':oracle['evaluatorHashes'],'trialAuthorized':False,'readyForTrial':False,'results':None}
(work/'static-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['allowedImplementationOrReadmeChanges','evaluatorHashes']}))
