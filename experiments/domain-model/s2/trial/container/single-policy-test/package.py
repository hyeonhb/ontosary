"""Validate explicit registration before staging; publish once, never overwrite history."""
import argparse,pathlib,json,shutil,tarfile,io,tempfile,os
from scope import registered_scope,inventory,verify_index
def package(work,out):
 work=pathlib.Path(work);out=pathlib.Path(out);plan=json.loads((work/'plan.json').read_text())
 assert out.resolve()==pathlib.Path(plan['output']).resolve(),'output-not-planned'
 assert not out.exists(),'output-exists-history-protected'
 scope=registered_scope(work)  # No mkdir or public output before validation.
 out.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='.policy-package-',dir=out.parent) as tmp:
  stage=pathlib.Path(tmp)/'evidence';stage.mkdir();(stage/'snapshot-scope.json').write_text(json.dumps(scope,indent=2)+'\n')
  for p in work.iterdir():
   if p.is_file() and (p.suffix in ['.json','.jsonl','.log','.go'] or p.name.endswith('.tar.gz')):
    dest=stage/'host'/p.name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(p,dest)
  shutil.copytree(work/'snapshots',stage/'snapshots')
  base=pathlib.Path(plan['source'])
  with tarfile.open(stage/'final-source.tar.gz','w:gz') as t:
   for directory in plan.get('sourceDirs',[str(base)]):
    directory=pathlib.Path(directory)
    for p in sorted(directory.iterdir()):
     if p.is_file():
      b=p.read_bytes();info=tarfile.TarInfo(directory.name+'/'+p.name);info.size=len(b);info.mode=0o644;t.addfile(info,io.BytesIO(b))
  (stage/'index.json').write_text(json.dumps(inventory(stage),indent=2)+'\n');result=verify_index(stage)
  assert not out.exists(),'output-created-concurrently';os.rename(stage,out)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--work',required=True);p.add_argument('--out',required=True);a=p.parse_args();print(json.dumps(package(a.work,a.out)))
