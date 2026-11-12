"""Package explicit analysis/closing scopes plus the complete archive inventory."""
import pathlib,json,shutil,tarfile,io
from scope import rows,classify,inventory,verify_index
work=pathlib.Path('work/s2-single-policy-test');out=pathlib.Path('experiments/domain-model/s2/verification/2026-11-12-single-policy-test');out.mkdir(exist_ok=True)
analysis=json.loads((work/'analysis-scope.json').read_text());known={r['id'] for r in analysis};closing=rows(work/'snapshots',sorted(p.stem for p in (work/'snapshots').glob('*.json') if p.stem not in known))
# This command explicitly classifies post-audit snapshots as closing evidence.
classify(work/'snapshots',analysis,closing)
(out/'snapshot-scope.json').write_text(json.dumps({'analysis':analysis,'closing':closing,'closingMeaning':'post-analysis verification, packaging or round close; not included in analysis audit'},indent=2)+'\n')
for p in work.iterdir():
 if p.is_file() and (p.suffix in ['.json','.jsonl','.log','.go'] or p.name.endswith('.tar.gz')):
  dest=out/'host'/p.name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(p,dest)
shutil.copytree(work/'snapshots',out/'snapshots',dirs_exist_ok=True)
base=pathlib.Path('experiments/domain-model/s2/trial/container/single-policy-test')
with tarfile.open(out/'final-source.tar.gz','w:gz') as t:
 for p in sorted(base.iterdir()):
  if p.is_file():
   b=p.read_bytes();info=tarfile.TarInfo(p.as_posix());info.size=len(b);info.mode=0o644;t.addfile(info,io.BytesIO(b))
(out/'index.json').write_text(json.dumps(inventory(out),indent=2)+'\n');print(json.dumps(verify_index(out)))
