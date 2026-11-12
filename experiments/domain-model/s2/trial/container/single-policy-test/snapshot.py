"""Capture each experimental helper version BEFORE execution; never inspect user auth/config."""
import datetime,hashlib,io,json,pathlib,tarfile,time
ROOT=pathlib.Path('experiments/domain-model/s2/trial/container')
def snapshot(work,command,phase=None,category="analysis"):
 work=pathlib.Path(work)
 if (work/"analysis-scope.json").exists() and category!="closing":raise ValueError("analysis-frozen")
 if category=="closing":
  plan=json.loads((work/"plan.json").read_text());assert {"phase":phase,"command":command} in plan["closingAllowed"],"closing-command-not-allowed"
 else:assert category=="analysis"
 folder=pathlib.Path(work)/'snapshots';folder.mkdir(exist_ok=True);identity=str(time.time_ns());archive=folder/(identity+'.tar.gz');files={}
 paths=[*ROOT.glob('*.yaml'),ROOT/'Dockerfile']
 for directory in ['single-policy-test','cli-feasibility','lifecycle']:
  paths += [p for p in (ROOT/directory).iterdir() if p.is_file() and p.suffix in ['.py','.mjs','.js','.json','.toml']]
 paths += [p for p in pathlib.Path(work).glob('*.py')]
 paths += [pathlib.Path(work)/n for n in ['plan.json','budget.json','start-input-hashes.json','Dockerfile','prior-native.json','seccomp-loader.go','prior-snapshot-scope.json'] if (pathlib.Path(work)/n).exists()]
 with tarfile.open(archive,'w:gz') as t:
  for p in sorted(paths):
   b=p.read_bytes();name=('round-inputs/'+p.relative_to(work).as_posix()) if p.is_absolute() else p.as_posix();files[name]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)};info=tarfile.TarInfo(name);info.size=len(b);info.mode=0o644;t.addfile(info,io.BytesIO(b))
 metadata={'id':identity,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hostMonotonic':time.monotonic(),'command':command,'phase':phase,'category':category,'archiveSha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':files}
 manifest=folder/(identity+'.json');manifest.write_text(json.dumps(metadata,indent=2)+'\n')
 if category=='closing':
  registry=work/'closing-registry.json';registered=json.loads(registry.read_text());registered.append({'id':identity,'manifestSha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'archiveSha256':metadata['archiveSha256'],'phase':phase,'command':command});tmp=registry.with_suffix('.tmp');tmp.write_text(json.dumps(registered,indent=2)+'\n');tmp.replace(registry)
 return identity
