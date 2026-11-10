#!/usr/bin/env python3
"""Verify collected smoke evidence and export it without starting a runtime."""
import argparse, hashlib, json, pathlib, re
p=argparse.ArgumentParser();p.add_argument('work',type=pathlib.Path);p.add_argument('output',type=pathlib.Path);a=p.parse_args()
repo=pathlib.Path(__file__).resolve().parents[5];guest=a.work/'guest/smoke-run-v2';result=json.loads((guest/'result.json').read_text());identity=result['identity']
assert len(result['units'])==4 and len({u['id'] for u in result['units']})==4
for index,unit in enumerate(result['units'],1):
 label=f"{index}-{unit['mode']}"
 before=json.loads((guest/(label+'-inspect-before.stdout')).read_text())[0]
 after=json.loads((guest/(label+'-inspect-after.stdout')).read_text())[0]
 native=json.loads((guest/(label+'-native.stdout')).read_text())[0]
 assert before['Id']==unit['id'] and before['Image']==identity['target']
 assert native['SnapshotInfo']['Parent']==identity['rootfsChainId']
 assert after['State']['Running'] is False and after['State']['ExitCode']==unit['exitCode']
 assert unit['passed'] and unit['removed']
 assert unit['exitCode']==(7 if unit['mode']=='exit7' else 0)
for name,key in [('image-manifest.stdout','target'),('image-config.stdout','config')]:
 assert 'sha256:'+hashlib.sha256((guest/name).read_bytes()).hexdigest()==identity[key]
commands=json.loads((guest/'commands.json').read_text());creates=[r for r in commands if r['label'].endswith('-create')]
assert len(creates)==4 and all('--pull=never' in r['command'] for r in creates)
cleanup=json.loads((a.work/'cleanup.json').read_text());assert cleanup['status']=='cleanup-passed' and cleanup['allRemovedPathsAbsent'] and cleanup['hostAgentAbsent']
assert '303 passed (303)' in (a.work/'14-host-check.log').read_text()
budget=json.loads((a.work/'budget.json').read_text());assert any(e['command']==['pnpm','check'] and e['exitCode']==0 for e in budget['events'])
a.output.mkdir(parents=True,exist_ok=True);exports={}
files=[f for f in a.work.iterdir() if f.name in ['budget.json','ownership.json','disk-downloads.json','cleanup.json'] or re.match(r'^\d\d-.*\.(json|log)$',f.name)]+[f for d in ['guest','implementation-at-execution'] for f in (a.work/d).rglob('*') if f.is_file()]
for f in sorted(files):
 relative=f.relative_to(a.work);original=f.read_bytes();text=original.decode()
 # OCI content bytes remain exact so target/config digest checks are repeatable.
 exact=f.name in ['image-manifest.stdout','image-config.stdout']
 if not exact:
  for old,new in [('/private/tmp/ontosary-s2-smoke-20261110','<task-root>'),('/tmp/ontosary-s2-smoke-20261110','<task-root>'),(str(repo),'<repo>'),(str(pathlib.Path.home())+'/Library/Caches','<host-cache>'),('/home/hyeon.guest','<guest-home>'),(str(pathlib.Path.home()),'<host-home>'),('황보현','<host-display-name>'),('hyeon','<host-user>')]:text=text.replace(old,new)
  text=re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]','',text)
  text='\n'.join(line.rstrip() for line in text.splitlines()).rstrip()+'\n' if text else ''
 dest=a.output/'raw'/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text)
 exports[str(relative)]={'originalSha256':hashlib.sha256(original).hexdigest(),'exportSha256':hashlib.sha256(text.encode()).hexdigest(),'exactOCIBytes':exact}
implementation={str(f.relative_to(repo)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(pathlib.Path(__file__).parent.rglob('*')) if f.is_file() and '__pycache__' not in f.parts}
evidence={str(f.relative_to(a.output)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(a.output.rglob('*')) if f.is_file() and f.name!='manifest.json'}
manifest={'status':'smoke-passed','baseCommit':'cb3c75df7075f03bf63acaf18da638d1c0b13c96','identity':identity,'implementation':implementation,'evidence':evidence,'exports':exports,'normalization':'Host paths/identities, ANSI, line endings/trailing whitespace; OCI content bytes preserved exactly. Initial/final executed scripts preserved under raw/implementation-at-execution.','hostTests':303,'skipped':0,'providerCalls':0,'trialRuns':0,'R11':'unresolved','trialAuthorized':False,'readyForTrial':False,'results':None}
(a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'status':manifest['status'],'implementationFiles':len(implementation),'evidenceFiles':len(evidence)}))
