"""Guest evidence export and removal of this round's recorded resources only."""
import gzip,hashlib,json,os,pathlib,shutil,stat,subprocess,sys,tarfile,time
BASE=pathlib.Path('/opt/ontosary-linux-evaluation');FIXTURE=pathlib.Path('/opt/ontosary-fixture');OUT=pathlib.Path('/tmp/s2-linux-export');OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(FIXTURE/'code'))
from fingerprint import inputs_fingerprint
from common import NERD,CTR,command,write
start=time.monotonic();fingerprint=inputs_fingerprint(BASE);expected=json.loads((BASE/'setup/inputs-summary.json').read_text());assert fingerprint['sha256']==expected['sha256']
(OUT/'final-inputs-fingerprint.json.gz').write_bytes(gzip.compress((json.dumps(fingerprint,sort_keys=True)+'\n').encode(),mtime=0));write(OUT/'final-inputs-summary.json',{'sha256':fingerprint['sha256'],'fileCount':fingerprint['fileCount'],'seconds':time.monotonic()-start})
# Old removal routine checks every recorded cgroup/task/pending state before removing its unit.
if not (FIXTURE/'removal/cleanup.json').exists():
 subprocess.run(['python3',str(FIXTURE/'code/remove.py')],check=True,timeout=90)
else:
 assert json.loads((FIXTURE/'removal/cleanup.json').read_text())['status']=='guest-cleanup-passed'
cleanup=FIXTURE/'removal';image=json.loads((FIXTURE/'image.json').read_text())
code,out,err=command(cleanup,NERD+['image','inspect','--mode=native',image['name']],check=False);listing=command(cleanup,NERD+['images','--format','{{.Repository}}:{{.Tag}}'])[1];assert not listing.strip() and not out.strip()
containers=command(cleanup,NERD+['ps','-a','--format','{{.ID}} {{.Names}}'])[1];tasks=command(cleanup,CTR+['tasks','list'])[1];volumes=command(cleanup,NERD+['volume','ls'])[1]
assert not containers.strip() and len(tasks.strip().splitlines())==1
write(cleanup/'linux-absence.json',{'containers':containers,'tasks':tasks,'volumes':volumes,'imageAbsent':True,'imageListing':listing,'inspectExitCode':code,'inspectStdout':out,'inspectStderr':err,'image':image,'remainingBuildCache':'Owned VM only; removed with VM, not a collected-unit termination substitute'})
for name in ['preparation','setup','output']:shutil.copytree(BASE/name,OUT/name)
shutil.copytree(BASE/'tools',OUT/'tools',ignore=shutil.ignore_patterns('node_modules'))
shutil.copytree(FIXTURE/'code',OUT/'code',ignore=shutil.ignore_patterns('__pycache__'))
shutil.copytree(cleanup,OUT/'removal')
for name in ['image.json','gate.json']:shutil.copyfile(FIXTURE/name,OUT/name)
(OUT/'assembled').mkdir()
for f in (BASE/'assembled').glob('*.json'):shutil.copyfile(f,OUT/'assembled'/f.name)
rows=[]
for run in sorted((FIXTURE/'runs').iterdir()):
 dest=OUT/'runs'/run.name;dest.mkdir(parents=True);state=json.loads((run/'state.json').read_text());rows.append({'runId':run.name,'mode':state['mode'],'job':state.get('job'),'state':state['state'],'cleanupDone':state['cleanupDone']})
 (dest/'service-journal-final.log').write_text(command(run,['journalctl','-u',state['service'],'--no-pager'])[1])
 for f in run.iterdir():
  if f.is_file() and f.name!='operation.lock':shutil.copyfile(f,dest/f.name)
  elif f.is_dir() and f.name in ['result','quarantined-result']:shutil.copytree(f,dest/f.name)
 metadata={}
 for folder in ['source','auxiliary']:
  for f in (run/folder).rglob('*'):
   s=f.lstat();relative=f.relative_to(run).as_posix()
   assert stat.S_ISDIR(s.st_mode) or stat.S_ISREG(s.st_mode) and s.st_nlink==1
   if f.is_file():
    metadata[relative]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':s.st_size}
    if s.st_size<=65536:
     target=dest/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,target)
 write(dest/'source-metadata.json',metadata)
write(OUT/'export.json',{'fixtureOnly':True,'validSubmission':False,'rows':rows,'runs':len(rows),'sourcePayloadPolicy':'Full collected/quarantined outputs; manager records and <=64KiB ordinary source diagnostics. Large source report bytes also retained in collected results. No dependencies or VM payloads.'})
(OUT/'executed-preparation').mkdir()
for source in ['/tmp/s2-linux-prepare.py','/tmp/s2-job-code/setup.py','/tmp/s2-linux-finish.py','/tmp/s2-linux-finish-v1.py']:
 shutil.copyfile(source,OUT/'executed-preparation'/pathlib.Path(source).name)
with tarfile.open('/tmp/s2-linux-export.tar.gz','w:gz') as t:t.add(OUT,arcname='linux-evaluation')
print(json.dumps({'export':'/tmp/s2-linux-export.tar.gz','registeredUnits':len(rows),'guestCleanup':'passed','immutableInputs':'matched'}))
