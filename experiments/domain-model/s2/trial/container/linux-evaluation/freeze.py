"""Freeze this round's evidence and verify every archive member; no runtime execution."""
import gzip,hashlib,json,pathlib,shutil,tarfile,io
REPO=pathlib.Path.cwd();WORK=REPO/'work/s2-linux-evaluation';OUT=REPO/'experiments/domain-model/s2/verification/2026-11-11-linux-evaluation'
OUT.mkdir(exist_ok=True);budget=json.loads((WORK/'budget.json').read_text());marker=OUT/'round.json'
if marker.exists():assert json.loads(marker.read_text())['startedUtc']==budget['utc']
else:marker.write_text(json.dumps({'startedUtc':budget['utc'],'closedRoundEvidence':True},indent=2)+'\n')
sha=lambda b:hashlib.sha256(b).hexdigest()
origins={}
def copy(source,destination):
 destination.parent.mkdir(parents=True,exist_ok=True);data=source.read_bytes()
 if len(data)>128*1024 and source.suffix in ['.json','.jsonl','.log']:
  destination=destination.with_name(destination.name+'.gz');destination.write_bytes(gzip.compress(data,mtime=0))
 else:destination.write_bytes(data)
 origins[str(destination.relative_to(OUT))]={'source':str(source.relative_to(REPO)),'originalSha256':sha(data),'originalBytes':len(data)}
for f in WORK.iterdir():
 if f.is_file() and f.suffix in ['.json','.jsonl','.log']:copy(f,OUT/'host'/f.name)
for name in ['guest-records.tar.gz','preparation-evidence.tar.gz','job-code.tar.gz']:copy(WORK/name,OUT/name)
for category in ['units','prevalidation-units','validation-units','job-probes','lifecycle-regressions']:
 for case in sorted((WORK/category).iterdir()):
  for f in case.iterdir():
   if f.is_file():copy(f,OUT/category/case.name/f.name)
for name in ['seven-comparison.json','core-comparison-v2.json','job-probes-summary.json','static-verification.json','host-cleanup.json','version-provenance.json']:
 copy(WORK/name,OUT/name)
for name in ['comparison-policy.json']:
 copy(REPO/'experiments/domain-model/s2/trial/container/linux-evaluation'/name,OUT/name)
if (WORK/'cost.json').exists():copy(WORK/'cost.json',OUT/'cost.json')
# Current source + original host commands. Guest archives independently preserve what actually executed.
files=[p for p in (REPO/'experiments/domain-model/s2/trial/container/linux-evaluation').iterdir() if p.is_file()]
files += [p for p in WORK.glob('*.py')]
with tarfile.open(OUT/'host-code.tar.gz','w:gz') as archive:
 for f in sorted(files):
  data=f.read_bytes();name=str(f.relative_to(REPO));info=tarfile.TarInfo(name);info.mode=0o644;info.size=len(data);archive.addfile(info,io.BytesIO(data))
archives={}
for archive in sorted(OUT.rglob('*.tar.gz')):
 members={}
 with tarfile.open(archive,'r:gz') as t:
  for m in t:
   assert not pathlib.PurePosixPath(m.name).is_absolute() and '..' not in pathlib.PurePosixPath(m.name).parts
   if m.isfile():
    b=t.extractfile(m).read();assert len(b)==m.size;members[m.name]={'sha256':sha(b),'bytes':len(b)}
   else:assert m.isdir(),(archive,m.name)
 archives[str(archive.relative_to(OUT))]=members
(OUT/'archive-members.json.gz').write_bytes(gzip.compress((json.dumps(archives,sort_keys=True,indent=2)+'\n').encode(),mtime=0))
(OUT/'origins.json').write_text(json.dumps(origins,indent=2)+'\n')
files={str(f.relative_to(OUT)):{'sha256':sha(f.read_bytes()),'bytes':f.stat().st_size} for f in sorted(OUT.rglob('*')) if f.is_file() and f.name!='evidence-index.json'}
index={'schema':'s2-linux-evaluation-evidence-v1','status':'linux-evaluation-reproduced','trialAuthorized':False,'readyForTrial':False,'results':None,'files':files,'archiveCount':len(archives),'archiveMembers':sum(len(m) for m in archives.values()),'exclusions':['host node_modules','VM/prefix/private keys','full public source transport archive (all members/hash retained in host evidence)']}
(OUT/'evidence-index.json').write_text(json.dumps(index,indent=2)+'\n')
for f,metadata in files.items():assert sha((OUT/f).read_bytes())==metadata['sha256']
print(json.dumps({'status':'verified','files':len(files),'archives':len(archives),'archiveMembers':index['archiveMembers'],'bytes':sum(m['bytes'] for m in files.values())}))
