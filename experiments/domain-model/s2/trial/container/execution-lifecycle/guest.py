"""Owned round preparation/export; all worker units go through engine.py."""
import datetime,hashlib,io,json,os,pathlib,sys,tarfile,time
HERE=pathlib.Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'lifecycle')]
import common as c
import image
from engine import SHARED,MANAGER_ENV

def prep():
 log=SHARED/'preparation';log.mkdir(mode=0o700)
 budget=c.read(SHARED/'budget.json');end=time.monotonic()+(datetime.datetime.fromisoformat(budget['deadlines']['environment']['utc'])-datetime.datetime.now(datetime.timezone.utc)).total_seconds()
 def cmd(args,timeout=3):return c.command(log,args,timeout=timeout,env=MANAGER_ENV,deadline=end)
 versions=cmd(['sh','-c','uname -a; systemctl --version; nerdctl --version; containerd --version; runc --version'])[1]
 if not all(x in versions for x in ['7.0.0-38-generic','nerdctl version 2.4.2','b7a25261e029d68978bbf290df0a62fc819b3c51']):raise RuntimeError('runtime-version-mismatch')
 target='ontosary-s2-execution:trace'
 cmd(c.NERD+['build','--build-arg','BASE_IMAGE=docker.io/library/node@sha256:4a4884e8a44826194dff92ba316264f392056cbe243dcc9fd3551e71cea02b90','-t',target,str(SHARED/'build')],max(.01,end-time.monotonic()))
 found=image.identify(log,target);c.write(SHARED/'image.json',found)
 cmd(c.NERD+['save','--output',str(SHARED/'image.tar'),target],max(.01,end-time.monotonic()))
 c.write(SHARED/'image-export.json',{'image':found,'bytes':(SHARED/'image.tar').stat().st_size,'sha256':hashlib.file_digest((SHARED/'image.tar').open('rb'),'sha256').hexdigest()})
 print(json.dumps(c.read(SHARED/'image-export.json')))

def imported():
 log=SHARED/'import';log.mkdir(mode=0o700);budget=c.read(SHARED/'budget.json');end=time.monotonic()+(datetime.datetime.fromisoformat(budget['deadlines']['environment']['utc'])-datetime.datetime.now(datetime.timezone.utc)).total_seconds()
 expected=c.read(SHARED/'image-export.json');p=SHARED/'reused-image.tar'
 if p.stat().st_size!=expected['bytes'] or hashlib.file_digest(p.open('rb'),'sha256').hexdigest()!=expected['sha256']:raise RuntimeError('import-archive-bytes')
 c.command(log,c.NERD+['load','--input',str(p)],timeout=max(.01,end-time.monotonic()),env=MANAGER_ENV,deadline=end)
 actual=image.identify(log,expected['image']['name'])
 if actual!=expected['image']:raise RuntimeError('import-image-identity')
 c.write(SHARED/'import-verified.json',{'archive':expected,'actualImage':actual,'secondUseBuilds':0,'secondUseDownloads':0})
 # Root-owned working directory and runtime hook bundle parents cannot be worker-written.
 for parent in [SHARED,pathlib.Path('/var/lib/nerdctl')]:
  info=parent.stat()
  if info.st_uid!=0 or info.st_mode&0o022:raise RuntimeError('runtime-working-directory-owner')
 unit=pathlib.Path('/run/systemd/system/ontosary-execution-seal.service')
 unit.write_text(f'[Service]\nType=simple\nWorkingDirectory={SHARED}\nExecStart=/usr/bin/python3 {HERE}/engine.py reap\nRestart=no\nRuntimeMaxSec=3h\nTimeoutStopSec=2\nKillMode=control-group\n')
 c.command(log,['systemctl','daemon-reload'],env=MANAGER_ENV,deadline=end);c.command(log,['systemctl','start',unit.name],env=MANAGER_ENV,deadline=end)
 print(json.dumps(c.read(SHARED/'import-verified.json')))

def export():
 target=pathlib.Path('/tmp/s2-execution-evidence.tar.gz');members={};total=0
 with tarfile.open(target,'w:gz') as tar:
  for base,prefix in [(c.ROOT/'runs','runs'),(SHARED/'preparation','preparation'),(SHARED/'import','import')]:
   if not base.exists():continue
   for p in sorted(base.rglob('*')):
    if not p.is_file() or p.is_symlink():continue
    if base==c.ROOT/'runs':
     relative=p.relative_to(base);run=base/relative.parts[0];state=c.read(run/'state.json')
     if len(relative.parts)>2 and not(state.get('terminationConfirmed') and state.get('removalConfirmed')):continue
    data=p.read_bytes();total+=len(data)
    if total>16*1024*1024 or len(members)>=1024:raise RuntimeError('export-bound')
    name=prefix+'/'+p.relative_to(base).as_posix();item=tarfile.TarInfo(name);item.size=len(data);item.mode=0o644;tar.addfile(item,io.BytesIO(data));members[name]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
  for p in [SHARED/'image.json',SHARED/'image-export.json',SHARED/'import-verified.json',c.ROOT/'gate.json']:
   if p.exists():
    data=p.read_bytes();item=tarfile.TarInfo(p.name);item.size=len(data);item.mode=0o644;tar.addfile(item,io.BytesIO(data));members[p.name]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
 c.write(SHARED/'export-index.json',members);print(json.dumps({'bytes':target.stat().st_size,'files':len(members),'sha256':hashlib.file_digest(target.open('rb'),'sha256').hexdigest()}))
if __name__=='__main__':{'prepare':prep,'import':imported,'export':export}[sys.argv[1]]()
