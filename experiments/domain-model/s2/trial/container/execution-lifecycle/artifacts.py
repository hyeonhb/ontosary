"""One manager-owned, byte-verified public artifact set (not a runtime cache)."""
import contextlib,fcntl,hashlib,json,os,pathlib,shutil,stat,time,urllib.request,uuid
LIMIT=10*1024**3
class Rejected(RuntimeError):pass

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
def digest_file(path,deadline):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        before=os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1:raise Rejected('not-owned-regular-file')
        h=hashlib.sha256();n=0
        while True:
            if time.monotonic()>=deadline:raise Rejected('artifact-deadline')
            data=os.read(fd,1024*1024)
            if not data:break
            h.update(data);n+=len(data)
        after=os.fstat(fd)
        if (before.st_ino,before.st_size,before.st_mtime_ns)!=(after.st_ino,after.st_size,after.st_mtime_ns) or n!=before.st_size:raise Rejected('artifact-changed')
        return {'sha256':h.hexdigest(),'bytes':n}
    finally:os.close(fd)

class Store:
    def __init__(self,root,limit=LIMIT,owner_tag=None):
        self.root=pathlib.Path(root).absolute();self.limit=limit;self.owner_tag=owner_tag
        if self.root.resolve()!=self.root:raise Rejected('store-symlink')
        self.root.mkdir(mode=0o700,parents=True,exist_ok=True)
        st=self.root.lstat()
        if not stat.S_ISDIR(st.st_mode) or st.st_uid!=os.getuid() or st.st_mode&0o077:raise Rejected('store-owner-mode')
    @contextlib.contextmanager
    def lock(self,deadline):
        fd=os.open(self.root/'.lock',os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600)
        try:
            while True:
                if time.monotonic()>=deadline:raise Rejected('store-lock-deadline')
                try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);break
                except BlockingIOError:time.sleep(.01)
            yield
        finally:os.close(fd)
    def usage(self):
        total=0
        for p in self.root.rglob('*'):
            s=p.lstat()
            if s.st_uid!=os.getuid() or stat.S_ISLNK(s.st_mode) or not (stat.S_ISREG(s.st_mode) or stat.S_ISDIR(s.st_mode)):raise Rejected('unexpected-store-entry')
            if p.name!='.lock' and stat.S_ISREG(s.st_mode):total+=s.st_size
        if total>self.limit:raise Rejected('store-capacity')
        return total
    def _lookup(self,request,deadline):
        self.usage()
        for folder in self.root.iterdir():
            if folder.name.startswith('.'):continue
            meta=folder/'manifest.json'
            if not meta.is_file() or meta.is_symlink():raise Rejected('incomplete-registration')
            record=json.loads(meta.read_text())
            if record['request']['name']!=request['name']:continue
            if record['request']!=request:raise Rejected('input-manifest-mismatch')
            actual=digest_file(folder/'data',deadline)
            if actual!=record['actual'] or folder.name!=actual['sha256']:raise Rejected('corrupt-registered-artifact')
            return {**record,'path':str(folder/'data'),'cacheHit':True,'verifiedAtMono':time.monotonic()}
        return None
    def cleanup_pending(self,deadline):
        if self.owner_tag is None:raise Rejected('missing-owner-tag')
        removed=[]
        with self.lock(deadline):
            self.usage()
            for p in self.root.glob('.pending-*'):
                owner=p/'owner.json'
                if not owner.exists():continue
                record=json.loads(owner.read_text())
                if record.get('ownerTag')==self.owner_tag and record.get('uid')==os.getuid():
                    shutil.rmtree(p);removed.append(p.name)
        return removed
    def lookup(self,request,deadline):
        with self.lock(deadline):return self._lookup(request,deadline)
    def acquire(self,request,producer,deadline):
        """producer(sink) streams only public immutable bytes; sink enforces remaining quota."""
        with self.lock(deadline):
            hit=self._lookup(request,deadline)
            if hit:return hit
            maximum=request.get('bytes',request.get('maximumBytes'))
            if not isinstance(maximum,int) or maximum<=0:raise Rejected('missing-byte-bound')
            if self.usage()+maximum+65536>self.limit:raise Rejected('store-capacity-reserve')
            temp=self.root/('.pending-'+uuid.uuid4().hex);temp.mkdir(mode=0o700)
            (temp/'owner.json').write_bytes(canonical({'ownerTag':self.owner_tag,'uid':os.getuid(),'request':request})+b'\n')
            data=temp/'data';count=0;h=hashlib.sha256()
            try:
                with data.open('xb') as f:
                    def sink(chunk):
                        nonlocal count
                        if time.monotonic()>=deadline:raise Rejected('artifact-deadline')
                        count+=len(chunk)
                        if count>maximum:raise Rejected('artifact-byte-bound')
                        h.update(chunk);f.write(chunk)
                    producer(sink);f.flush();os.fsync(f.fileno())
                actual={'sha256':h.hexdigest(),'bytes':count}
                if request.get('sha256') and actual['sha256']!=request['sha256']:raise Rejected('artifact-sha256')
                if 'bytes' in request and count!=request['bytes']:raise Rejected('partial-artifact')
                if digest_file(data,deadline)!=actual:raise Rejected('postwrite-mismatch')
                record={'request':request,'actual':actual,'ownerUid':os.getuid(),'registeredAtMono':time.monotonic()}
                (temp/'manifest.json').write_bytes(canonical(record)+b'\n')
                os.chmod(data,0o400);os.chmod(temp/'manifest.json',0o400)
                target=self.root/actual['sha256']
                if target.exists():raise Rejected('digest-name-conflict')
                if self.usage()>self.limit:raise Rejected('store-capacity')
                (temp/'owner.json').unlink()
                os.rename(temp,target)
                fd=os.open(self.root,os.O_RDONLY);os.fsync(fd);os.close(fd)
                return {**record,'path':str(target/'data'),'cacheHit':False,'verifiedAtMono':time.monotonic()}
            finally:
                if temp.exists():shutil.rmtree(temp) # only the unique directory created by this call

def download(request,deadline):
    def produce(sink):
        with urllib.request.urlopen(request['url'],timeout=max(.01,min(30,deadline-time.monotonic()))) as response:
            while True:
                block=response.read(1024*1024)
                if not block:break
                sink(block)
    return produce

def copy_public(path):
    def produce(sink):
        fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):raise Rejected('nonregular-import')
            while True:
                b=os.read(fd,1024*1024)
                if not b:break
                sink(b)
        finally:os.close(fd)
    return produce

def verify_image_archive(path,image,deadline):
    """Validate OCI content bytes + manifest/config/diff-ID chain without unpacking layers."""
    import tarfile
    with tarfile.open(path) as archive:
        members={};total=0
        for member in archive:
            if time.monotonic()>=deadline:raise Rejected('archive-deadline')
            if member.name in members or member.issym() or member.islnk() or pathlib.PurePosixPath(member.name).is_absolute() or '..' in pathlib.PurePosixPath(member.name).parts:raise Rejected('archive-entry')
            if member.isdir():continue
            if not member.isfile():raise Rejected('archive-kind')
            members[member.name]=member;total+=member.size
            if total>LIMIT or len(members)>2048:raise Rejected('archive-bound')
            if member.name.startswith('blobs/sha256/'):
                h=hashlib.sha256()
                with archive.extractfile(member) as f:
                    while True:
                        if time.monotonic()>=deadline:raise Rejected('archive-deadline')
                        b=f.read(1024*1024)
                        if not b:break
                        h.update(b)
                if h.hexdigest()!=member.name.rsplit('/',1)[1]:raise Rejected('archive-blob-hash')
        def blob(digest):
            name='blobs/'+digest.replace(':','/')
            if name not in members or members[name].size>4*1024*1024:raise Rejected('archive-metadata')
            return json.load(archive.extractfile(members[name]))
        manifest=blob(image['target']);config=blob(manifest['config']['digest'])
        if manifest['config']['digest']!=image['config'] or (config['os'],config['architecture'])!=('linux','arm64'):raise Rejected('archive-config')
        ids=config['rootfs']['diff_ids'];chain=ids[0]
        for layer in ids[1:]:chain='sha256:'+hashlib.sha256((chain+' '+layer).encode()).hexdigest()
        if chain!=image['chain']:raise Rejected('archive-chain')
        if any('blobs/'+x['digest'].replace(':','/') not in members for x in manifest['layers']):raise Rejected('missing-layer')
        return {'manifest':image['target'],'config':image['config'],'rootfsChain':chain,'blobsVerified':sum(n.startswith('blobs/') for n in members),'uncompressedArchiveBytes':total}
