"""Allowlisted diagnostic export, after verified removal; no CLI state export."""
import pathlib,tarfile,json
root=pathlib.Path('/opt/ontosary-policy-retry')
names=['preparation','image.json','build/Dockerfile','policy.toml','probe/probe.mjs','prior-native.json','baseline-native.json','candidate.json','baseline-result.json','candidate-result.json','pair-complete.json','baseline-run.json','candidate-run.json','baseline-identity.json','candidate-prepared.json','candidate-authorized.json','metadata']
with tarfile.open('/tmp/s2-policy-retry-evidence.tar.gz','w:gz') as t:
 for name in names:
  p=root/name
  if p.exists():t.add(p,arcname=name)
 for mode in ['baseline','candidate']:
  if not (root/(mode+'-run.json')).exists():continue
  run=pathlib.Path('/opt/ontosary-fixture/runs')/json.loads((root/(mode+'-run.json')).read_text())['runId']
  for p in sorted(run.iterdir()):
   if p.is_file() and p.suffix in ['.json','.jsonl','.service','.slice']:t.add(p,arcname=mode+'/'+p.name)
  if (run/'removed.json').exists():
   for name in ['source','auxiliary','materials']:t.add(run/name,arcname=mode+'/'+name)
