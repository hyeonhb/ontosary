"""Owned round preparation/export; all worker units go through engine.py."""
import datetime,hashlib,io,json,os,pathlib,sys,tarfile,time
HERE=pathlib.Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'lifecycle')]
import common as c
import image
from engine import SHARED,MANAGER_ENV
from identity import RUNTIME_ENV

def digest(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def preparation_deadline():
 budget=c.read(SHARED/'budget.json')
 return time.monotonic()+(datetime.datetime.fromisoformat(budget['deadlines']['environment']['utc'])-datetime.datetime.now(datetime.timezone.utc)).total_seconds()
def prep():
 from runtime_env import verify_tools
 log=SHARED/'preparation';log.mkdir(mode=0o700)
 end=preparation_deadline()
 def cmd(args):return c.command(log,args,env=RUNTIME_ENV,deadline=end)
 expected=c.read(SHARED/'input-members.json');actual={}
 for name,wanted in expected.items():
  if name.startswith('/') or '..' in pathlib.PurePosixPath(name).parts:raise RuntimeError('input-member-path')
  if time.monotonic()>=end:raise RuntimeError('preparation-deadline')
  with (SHARED/name).open('rb') as f:actual[name]=hashlib.file_digest(f,'sha256').hexdigest()
  if actual[name]!=wanted:raise RuntimeError('delivered-input-hash:'+name)
 c.write(log/'runtime-tools.json',{**verify_tools(cmd),'deliveredInputHashes':actual})
 kernel=cmd(['uname','-r'])[1].strip()
 if kernel!='7.0.0-38-generic':raise RuntimeError('kernel-version-mismatch')
 print(json.dumps({'toolsVerified':True,'kernel':kernel,'builds':0}))
def build():
 log=SHARED/'preparation';end=preparation_deadline()
 def cmd(args,timeout=3):return c.command(log,args,timeout=timeout,env=RUNTIME_ENV,deadline=end)
 target='ontosary-s2-execution:trace'
 cmd(c.NERD+['build','--build-arg','BASE_IMAGE=docker.io/library/node@sha256:4a4884e8a44826194dff92ba316264f392056cbe243dcc9fd3551e71cea02b90','-t',target,str(SHARED/'build')],max(.01,end-time.monotonic()))
 found=image.identify(log,target,env=RUNTIME_ENV,deadline=end);c.write(SHARED/'image.json',found)
 cmd(c.NERD+['save','--output',str(SHARED/'image.tar'),target],max(.01,end-time.monotonic()))
 c.write(SHARED/'image-export.json',{'image':found,'bytes':(SHARED/'image.tar').stat().st_size,'sha256':digest(SHARED/'image.tar')})
 print(json.dumps(c.read(SHARED/'image-export.json')))

def imported(source=None,transfer_uid=None):
 log=SHARED/'import';log.mkdir(mode=0o700);budget=c.read(SHARED/'budget.json');end=time.monotonic()+(datetime.datetime.fromisoformat(budget['deadlines']['environment']['utc'])-datetime.datetime.now(datetime.timezone.utc)).total_seconds()
 expected=c.read(SHARED/'image-export.json');p=SHARED/'reused-image.tar'
 if source is not None:
  from collector import open_directory,read_regular,Rejected
  source=pathlib.Path(source);fd=open_directory(source.parent);tmp=SHARED/'.image-transfer'
  try:
   parent=os.fstat(fd);before=os.stat(source.name,dir_fd=fd,follow_symlinks=False)
   if parent.st_uid!=transfer_uid or parent.st_mode&0o077 or before.st_uid!=transfer_uid or before.st_size!=expected['bytes'] or before.st_mode&0o022:raise Rejected('image-transfer-binding')
   row=read_regular(fd,source.name,before,end,tmp,owner=transfer_uid)
   if row!={'sha256':expected['sha256'],'bytes':expected['bytes']}:raise Rejected('image-transfer-hash')
   os.chmod(tmp,0o400);os.rename(tmp,p)
  finally:
   os.close(fd)
   if tmp.exists():tmp.unlink()
 if p.stat().st_size!=expected['bytes'] or digest(p)!=expected['sha256']:raise RuntimeError('import-archive-bytes')
 c.command(log,c.NERD+['load','--input',str(p)],timeout=max(.01,end-time.monotonic()),env=RUNTIME_ENV,deadline=end)
 actual=image.identify(log,expected['image']['name'],env=RUNTIME_ENV,deadline=end)
 if actual!=expected['image']:raise RuntimeError('import-image-identity')
 c.write(SHARED/'image.json',actual)
 c.write(SHARED/'import-verified.json',{'archive':expected,'actualImage':actual,'secondUseBuilds':0,'secondUseDownloads':0})
 activate_observer(log,end)
 print(json.dumps(c.read(SHARED/'import-verified.json')))

def activate_observer(log,end):
 # Root-owned working directory and runtime hook bundle parents cannot be worker-written.
 for parent in [SHARED,pathlib.Path('/var/lib/nerdctl')]:
  info=parent.stat()
  if info.st_uid!=0 or info.st_mode&0o022:raise RuntimeError('runtime-working-directory-owner')
 unit=pathlib.Path('/run/systemd/system/ontosary-execution-seal.service')
 unit.write_text(f'[Service]\nType=simple\nWorkingDirectory={SHARED}\nExecStart=/usr/bin/python3 {HERE}/engine.py reap\nExecStopPost=/usr/bin/python3 {HERE}/engine.py reaper-failed\nRestart=no\nRuntimeMaxSec=3h\nTimeoutStopSec=2\nKillMode=control-group\n')
 c.command(log,['systemctl','daemon-reload'],env=RUNTIME_ENV,deadline=end);c.command(log,['systemctl','start',unit.name],env=RUNTIME_ENV,deadline=end)

def export(target=None,deadline=None,**limits):
 from exporter import export as safe_export
 if deadline is None:
  budget=c.read(SHARED/'budget.json');deadline=time.monotonic()+max(0,(datetime.datetime.fromisoformat(budget['deadlines']['finish']['utc'])-datetime.datetime.now(datetime.timezone.utc)).total_seconds())
 result=safe_export(c.ROOT,SHARED,target or pathlib.Path('/tmp/s2-execution-export'),deadline,**limits)
 print(json.dumps(result));return result
if __name__=='__main__':
 action=sys.argv[1]
 if action=='publish':
  from metadata import publish
  print(json.dumps(publish(SHARED,pathlib.Path(sys.argv[2]),sys.argv[3],sys.argv[4],int(sys.argv[5]),preparation_deadline(),None if sys.argv[6]=='-' else sys.argv[6])))
 elif action=='import':imported(pathlib.Path(sys.argv[2]),int(sys.argv[3])) if len(sys.argv)>2 else imported()
 elif action=='export':
  scope=sys.argv[2];rid=None if sys.argv[3]=='-' else sys.argv[3];end=time.monotonic()+max(0,(datetime.datetime.fromisoformat(sys.argv[4])-datetime.datetime.now(datetime.timezone.utc)).total_seconds())
  export(target=pathlib.Path('/tmp/s2-execution-export-'+scope),deadline=end,run_id=rid,max_bytes=16*1024*1024-8192)
 else:{'prepare':prep,'build':build}[action]()
