"""Bounded regular-file fixture collector. Caller must hold termination authority."""
import datetime,hashlib,json,os,pathlib,shutil,stat,time
class Rejected(Exception):pass

def open_directory(path):
    """Walk every ancestor by FD. No parent symlink is followed."""
    path=pathlib.Path(path)
    if not path.is_absolute() or '..' in path.parts:raise Rejected('absolute-directory-required')
    fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY)
    try:
        for part in path.parts[1:]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
            os.close(fd);fd=child
        return fd
    except BaseException:os.close(fd);raise

def read_regular(fd,name,before,end,target=None,owner=None,sealed=False):
    """Shared collector/export body reader; caller checks quota before this open."""
    if not stat.S_ISREG(before.st_mode):raise Rejected('nonregular:'+name)
    if before.st_nlink!=1:raise Rejected('hardlink:'+name)
    if owner is not None and before.st_uid!=owner:raise Rejected('file-owner:'+name)
    if sealed and before.st_mode&0o222:raise Rejected('unsealed-file:'+name)
    source=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd)
    def identity(st):return (st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns,st.st_nlink,st.st_uid,st.st_mode)
    try:
        if identity(os.fstat(source))!=identity(before):raise Rejected('file-changed:'+name)
        h=hashlib.sha256();n=0;dest=target.open('xb') if target else None
        try:
            while True:
                if time.monotonic()>=end:raise Rejected('collection-time-limit')
                chunk=os.read(source,65536)
                if not chunk:break
                n+=len(chunk)
                if n>before.st_size:raise Rejected('file-grew:'+name)
                h.update(chunk)
                if dest:dest.write(chunk)
            if n!=before.st_size or identity(os.fstat(source))!=identity(before) or identity(os.stat(name,dir_fd=fd,follow_symlinks=False))!=identity(before):raise Rejected('file-changed:'+name)
        finally:
            if dest:dest.close()
        return {'sha256':h.hexdigest(),'bytes':n}
    finally:os.close(source)

class SafeFiles:
    """One cumulative export budget, including generated metadata."""
    def __init__(self,staging,deadline,max_files=1024,max_bytes=16*1024*1024):
        self.staging=pathlib.Path(staging);self.deadline=deadline;self.max_files=max_files;self.max_bytes=max_bytes;self.members={};self.bytes=0
    def reserve(self,name,size):
        if time.monotonic()>=self.deadline:raise Rejected('collection-time-limit')
        parts=pathlib.PurePosixPath(name).parts
        if not parts or len(parts)>16 or name.startswith('/') or '..' in parts or name in self.members:raise Rejected('export-name')
        if len(self.members)+1>self.max_files:raise Rejected('file-count-limit')
        if self.bytes+size>self.max_bytes:raise Rejected('byte-limit')
        self.bytes+=size
        target=self.staging/name;target.parent.mkdir(parents=True,exist_ok=True,mode=0o700);return target
    def copy(self,path,name,sealed=False):
        path=pathlib.Path(path);fd=open_directory(path.parent)
        try:
            before=os.stat(path.name,dir_fd=fd,follow_symlinks=False)
            target=self.reserve(name,before.st_size)
            row=read_regular(fd,path.name,before,self.deadline,target,os.getuid(),sealed)
            self.members[name]=row;return target
        finally:os.close(fd)
    def metadata(self,name,value):
        data=(json.dumps(value,sort_keys=True,indent=2)+'\n').encode();target=self.reserve(name,len(data));target.write_bytes(data);self.members[name]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)};return target

def inventory(roots, destination=None, fail_after=None, deadline=None):
    end=deadline if deadline is not None else time.monotonic()+10
    manifest={};directories=[];count=0;total=0
    def visit(fd, prefix, depth):
        nonlocal count,total
        if time.monotonic()>=end:raise Rejected('collection-time-limit')
        if depth>16:raise Rejected('path-depth-limit:'+prefix)
        # scandir avoids following entries; all opens below are descriptor relative.
        names=[]
        with os.scandir(fd) as entries:
            for entry in entries:
                if time.monotonic()>=end:raise Rejected('collection-time-limit')
                names.append(entry.name)
        for name in sorted(names):
            if time.monotonic()>=end:raise Rejected('collection-time-limit')
            rel=prefix+'/'+name
            if depth+1>16:raise Rejected('path-depth-limit:'+rel)
            before=os.stat(name,dir_fd=fd,follow_symlinks=False)
            if stat.S_ISDIR(before.st_mode):
                directories.append(rel)
                if destination:(destination/rel).mkdir(mode=0o700,parents=True,exist_ok=True)
                child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
                try:visit(child,rel,depth+1)
                finally:os.close(child)
            elif stat.S_ISREG(before.st_mode):
                if before.st_nlink!=1:raise Rejected('hardlink:'+rel)
                count+=1;total+=before.st_size
                if count>128:raise Rejected('file-count-limit')
                if total>16*1024*1024:raise Rejected('byte-limit')
                target=destination/rel if destination else None
                if target:target.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
                manifest[rel]=read_regular(fd,name,before,end,target)
                if fail_after is not None and count>=fail_after:raise Rejected('injected-copy-failure')
            else:raise Rejected('nonregular:'+rel+':'+str(stat.S_IFMT(before.st_mode)))
    for name,root in sorted(roots.items()):
        fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:
            if destination:(destination/name).mkdir(mode=0o700,parents=True,exist_ok=True)
            visit(fd,name,0)
        finally:os.close(fd)
    return {'files':manifest,'directories':sorted(directories),'fileCount':count,'bytes':total}

def collect(run, baseline, termination, fail_after=None, deadline=None):
    if termination.get('state')!='stopped-confirmed' or not termination.get('admissionClosed') or not termination.get('confirmed'):raise Rejected('termination-not-confirmed')
    current=json.loads((run/'state.json').read_text())
    if current['state']!='collecting' or not current.get('terminationConfirmed') or current.get('createPending') or current.get('startPending') or current.get('execPending'):raise Rejected('manager-state-not-collectible')
    for key in ['runId','containerId','image','cgroup','cgroupInode']:
        if termination.get(key)!=current.get(key):raise Rejected('termination-binding:'+key)
    if termination.get('source')!=str(run/'source') or termination.get('auxiliary')!=str(run/'auxiliary'):raise Rejected('termination-path-binding')
    collection_started={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mono':time.monotonic()}
    staging=run/'staging';final=run/'result'
    if staging.exists() or final.exists():raise Rejected('output-exists')
    staging.mkdir(mode=0o700);end=min(time.monotonic()+10,deadline) if deadline is not None else time.monotonic()+10
    roots={n:run/n for n in ['source','auxiliary']}
    try:
        snapshot=inventory(roots,staging,fail_after,end)
        if snapshot!=inventory(roots,deadline=end):raise Rejected('source-changed-during-copy')
        copied=inventory({n:staging/n for n in roots},deadline=end)
        if copied!=snapshot:raise Rejected('copy-manifest-mismatch')
        old=baseline['files'];new=snapshot['files']
        delta={'added':sorted(new.keys()-old.keys()),'deleted':sorted(old.keys()-new.keys()),'modified':sorted(k for k in new.keys()&old.keys() if new[k]!=old[k])}
        record={'schema':'s2-lifecycle-fixture-v1','fixtureOnly':True,'validSubmission':False,'classification':'normal-fixture' if termination['reason']=='exit' and termination['exitCode']==0 else 'diagnostic','termination':termination,'baselineHash':hashlib.sha256(json.dumps(baseline,sort_keys=True).encode()).hexdigest(),'snapshot':snapshot,'delta':delta,'collection':{'started':collection_started,'verified':{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mono':time.monotonic()},'limitSeconds':10}}
        (staging/'fixture.json').write_text(json.dumps(record,sort_keys=True,indent=2)+'\n')
        for p in staging.rglob('*'):os.chmod(p,0o555 if p.is_dir() else 0o444)
        os.chmod(staging,0o555)
        if time.monotonic()>=end:raise Rejected('collection-time-limit')
        os.rename(staging,final)
        return record
    except Exception:
        shutil.rmtree(staging);raise
