"""Validate transport bytes once by FD, then publish manager-owned control metadata."""
import hashlib,json,os,pathlib,re,stat,tempfile,time
from collector import open_directory,read_regular,Rejected
import common as c

def validate(value,name,binding=None):
 if name=='input-members.json':
  if not isinstance(value,dict) or not 1<=len(value)<=128:raise Rejected('metadata-members')
  for path,digest in value.items():
   if path.startswith('/') or '..' in pathlib.PurePosixPath(path).parts or not re.fullmatch('[0-9a-f]{64}',digest):raise Rejected('metadata-member-binding')
 elif name=='image-export.json':
  if set(value)!={'bytes','sha256','image','buildKey'} or value['buildKey']!=binding or not isinstance(value['bytes'],int) or not 0<value['bytes']<=6*1024**3 or not re.fullmatch('[0-9a-f]{64}',value['sha256']):raise Rejected('metadata-image-binding')
  image=value['image']
  if set(image)!={'name','target','config','chain','platform'} or image['platform']!='linux/arm64' or any(not re.fullmatch('sha256:[0-9a-f]{64}',image[k]) for k in ['target','config','chain']):raise Rejected('metadata-image-identity')
 else:raise Rejected('metadata-name')

def publish(shared,source,name,expected_hash,transfer_uid,deadline,binding=None,manager_uid=None):
 shared=pathlib.Path(shared);source=pathlib.Path(source);manager_uid=os.getuid() if manager_uid is None else manager_uid
 if shared.stat().st_uid!=manager_uid or shared.stat().st_mode&0o022:raise Rejected('metadata-manager-directory')
 fd=open_directory(source.parent);temp=None
 try:
  parent=os.fstat(fd)
  if parent.st_uid!=transfer_uid or parent.st_mode&0o077:raise Rejected('metadata-transfer-directory')
  before=os.stat(source.name,dir_fd=fd,follow_symlinks=False)
  if before.st_uid!=transfer_uid or before.st_mode&0o022 or before.st_size>1024*1024:raise Rejected('metadata-transfer-owner-mode-bound')
  n,path=tempfile.mkstemp(prefix='.metadata-',dir=shared);os.close(n);temp=pathlib.Path(path);temp.unlink()
  row=read_regular(fd,source.name,before,deadline,temp,owner=transfer_uid)
  if row['sha256']!=expected_hash:raise Rejected('metadata-hash')
  value=json.loads(temp.read_text());validate(value,name,binding)
  os.chmod(temp,0o600)
  if temp.stat().st_uid!=manager_uid:raise Rejected('metadata-published-owner')
  target=shared/name
  if target.exists():raise Rejected('metadata-already-published')
  if time.monotonic()>=deadline:raise Rejected('metadata-deadline')
  os.rename(temp,target);temp=None
  with target.open('rb') as f:after=hashlib.file_digest(f,'sha256').hexdigest()
  st=target.stat()
  if st.st_uid!=manager_uid or stat.S_IMODE(st.st_mode)!=0o600 or after!=expected_hash:raise Rejected('metadata-published-verification')
  receipt={'name':name,'sourceUid':before.st_uid,'managerUid':st.st_uid,'mode':oct(stat.S_IMODE(st.st_mode)),'sha256':after,'bytes':st.st_size,'binding':binding,'atomic':True}
  receipts=c.read(shared/'metadata-publication.json') if (shared/'metadata-publication.json').exists() else [];receipts.append(receipt);c.write(shared/'metadata-publication.json',receipts);return receipt
 finally:
  os.close(fd)
  if temp is not None and temp.exists():temp.unlink()

# This fixed bootstrap is sent as a python -c argument, not executed from transport.
BOOTSTRAP=r'''import os,sys,stat,hashlib,pathlib,tarfile,tempfile
source=pathlib.Path(sys.argv[1]);expected=sys.argv[2];owner=int(sys.argv[3]);shared=pathlib.Path('/opt/ontosary-execution')
fd=os.open(source.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);parent=os.fstat(fd)
assert parent.st_uid==owner and not parent.st_mode&0o077
f=os.open(source.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd);before=os.fstat(f)
assert stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_uid==owner and not before.st_mode&0o022 and before.st_size<=8*1024*1024
shared.mkdir(mode=0o700);n,path=tempfile.mkstemp(dir=shared);h=hashlib.sha256();size=0
with os.fdopen(n,'wb') as out:
 while True:
  b=os.read(f,65536)
  if not b:break
  size+=len(b);assert size<=before.st_size;h.update(b);out.write(b)
after=os.fstat(f);assert size==before.st_size and (after.st_size,after.st_mtime_ns,after.st_ctime_ns)==(before.st_size,before.st_mtime_ns,before.st_ctime_ns) and h.hexdigest()==expected
os.close(f);os.close(fd)
with tarfile.open(path) as t:
 for m in t:
  assert (m.isfile() or m.isdir()) and not m.name.startswith('/') and '..' not in pathlib.PurePosixPath(m.name).parts
 t.extractall(shared,filter='data')
os.unlink(path)
for p in shared.rglob('*'):
 assert not p.is_symlink();os.chown(p,0,0);os.chmod(p,0o755 if p.is_dir() else 0o644)
os.chmod(shared,0o755)
print('verified-manager-input-archive')'''
