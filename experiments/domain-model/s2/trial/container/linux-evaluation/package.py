"""Package pinned inventory, explicit inputs and portable tools; never host dependencies."""
import argparse,gzip,hashlib,json,pathlib,subprocess,tarfile,io
p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('output');a=p.parse_args()
repo=pathlib.Path.cwd();source=pathlib.Path(a.source);out=pathlib.Path(a.output);out.mkdir(exist_ok=True)
hashbytes=lambda b:hashlib.sha256(b).hexdigest()
load=lambda p:json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
manifest=load(repo/'experiments/domain-model/v1/manifest.json')
inv=load(repo/'experiments/public-app/results/2026-11-08/vendure/inventory.json.gz')
assert len(inv)==4735
members={}
for item in inv:
 assert not item.get('symlink'), 'Inventory symlink needs explicit packaging policy'
 file=source/item['path'];assert not file.is_symlink();b=file.read_bytes();assert hashbytes(b)==item['sha256'],item['path'];members['environment/'+item['path']]=b
for f,h in manifest['inputHashes'].items():
 b=(source/f).read_bytes();assert hashbytes(b)==h,f;members['environment/'+f]=b
paths=['experiments/domain-model/s2/provenance.json','experiments/domain-model/v1/manifest.json','experiments/public-app/results/2026-11-08/vendure/inventory.json.gz','experiments/public-app/results/2026-11-08-prepared/program-path-audit.json.gz']
provenance=load(repo/paths[0])
paths += ['experiments/domain-model/results/2026-11-08-v2/'+f for f in provenance['S1Artifacts']]
paths += [str((repo/'experiments/domain-model/v1'/f).resolve().relative_to(repo)) for f in manifest['repositoryInputs']]
for f in paths:members['tools/repo/'+f]=(repo/f).read_bytes()
for f in (repo/'work/s2-build').rglob('*.js'):members['tools/build/'+str(f.relative_to(repo/'work/s2-build'))]=f.read_bytes()
members['tools/package.json']=b'{"type":"module"}\n'
for f in (repo/'experiments/domain-model/s2/trial/container/linux-evaluation').glob('*.mjs'):members['tools/'+f.name]=f.read_bytes()
for f in (repo/'experiments/domain-model/s2/trial/container/lifecycle').glob('*.py'):members['lifecycle/'+f.name]=f.read_bytes()
members['build/Dockerfile']=(repo/'experiments/domain-model/s2/trial/container/Dockerfile').read_bytes()
members['tools/prepare-vendure.sh']=(repo/'experiments/domain-model/s2/trial/container/prepare-vendure.sh').read_bytes()
with tarfile.open(out/'inputs.tar.gz','w:gz') as archive:
 for name,b in sorted(members.items()):
  info=tarfile.TarInfo(name);info.size=len(b);info.mode=0o644;archive.addfile(info,io.BytesIO(b))
(out/'archive-members.json').write_text(json.dumps({f:{'sha256':hashbytes(b),'bytes':len(b)} for f,b in sorted(members.items())},indent=2)+'\n')
tracked=subprocess.check_output(['git','ls-files','experiments/domain-model/s2','experiments/domain-model/v1','experiments/public-app/results/2026-11-08-prepared','experiments/public-app/results/2026-11-08/vendure/inventory.json.gz'],text=True).splitlines()
(out/'start-input-hashes.json').write_text(json.dumps({f:hashbytes((repo/f).read_bytes()) for f in tracked},indent=2)+'\n')
execution=load(repo/'experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix/execution/execution-manifest.json')
(out/'identity.json').write_text(json.dumps({'baseCommit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'sourceRevision':manifest['revision'],'ids':{k:v for k,v in execution.items() if k.endswith('Id')},'inventoryFiles':len(inv),'inventoryBytes':sum(i['bytes'] for i in inv),'archiveSha256':hashbytes((out/'inputs.tar.gz').read_bytes()),'repositoryFiles':paths},indent=2)+'\n')
print('Packaged',len(members),'files; inventory',len(inv))
