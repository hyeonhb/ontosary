"""Freeze or verify this round's allowlisted evidence, never an auth/state directory."""
import hashlib,io,json,pathlib,shutil,sys,tarfile
sha=lambda b:hashlib.sha256(b).hexdigest()
def inventory(root):
 files={};archives={}
 for p in sorted(root.rglob('*')):
  if not p.is_file() or p.name=='index.json':continue
  name=p.relative_to(root).as_posix();files[name]={'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size}
  if name.endswith('.tar.gz'):
   rows={}
   with tarfile.open(p) as t:
    for m in t.getmembers():
     assert not pathlib.PurePosixPath(m.name).is_absolute() and '..' not in pathlib.PurePosixPath(m.name).parts
     assert m.isdir() or m.isfile(),m.name
     if m.isfile():assert m.name not in rows;rows[m.name]={'sha256':sha(t.extractfile(m).read()),'bytes':m.size}
   archives[name]=rows
 return {'files':files,'archives':archives}
if len(sys.argv)>1 and sys.argv[1]=='--verify':
 root=pathlib.Path(sys.argv[2]);assert inventory(root)==json.loads((root/'index.json').read_text());print(json.dumps({'files':len(inventory(root)['files']),'archives':len(inventory(root)['archives']),'verified':True}));raise SystemExit
work=pathlib.Path('work/s2-namespace-diagnosis');out=pathlib.Path('experiments/domain-model/s2/verification/2026-11-11-namespace-diagnosis');out.mkdir(exist_ok=True)
marker=out/'round.json';started=json.loads((work/'budget.json').read_text())['utc']
if marker.exists():assert json.loads(marker.read_text())['startedUtc']==started
else:marker.write_text(json.dumps({'startedUtc':started,'status':'proposal-ready-unapplied','fixtureOnly':True,'validSubmission':False},indent=2)+'\n')
for p in work.iterdir():
 if p.is_file() and (p.suffix in ['.json','.jsonl','.log'] or p.name.endswith('.tar.gz')):
  dest=out/'host'/p.name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(p,dest)
shutil.copytree(work/'snapshots',out/'snapshots',dirs_exist_ok=True)
base=pathlib.Path('experiments/domain-model/s2/trial/container/namespace-diagnosis')
with tarfile.open(out/'final-source.tar.gz','w:gz') as t:
 for p in sorted(base.iterdir()):
  if p.is_file():
   b=p.read_bytes();info=tarfile.TarInfo(p.as_posix());info.size=len(b);info.mode=0o644;t.addfile(info,io.BytesIO(b))
for name in ['cost.json','audit.json','host-cleanup.json','stop.json']:
 if (work/name).exists():shutil.copyfile(work/name,out/name)
shutil.copyfile(base.parent/'cli-feasibility/policy.toml',out/'observed-unchanged-policy.toml')
(out/'index.json').write_text(json.dumps(inventory(out),indent=2)+'\n')
print(json.dumps({'files':len(inventory(out)['files']),'archives':len(inventory(out)['archives']),'output':str(out)}))
