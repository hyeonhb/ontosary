"""Bounded regular-file fixture collector. Caller must hold termination authority."""
import datetime,hashlib,json,os,pathlib,shutil,stat,time
class Rejected(Exception):pass

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
                source=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd)
                try:
                    current=os.fstat(source)
                    if not stat.S_ISREG(current.st_mode) or current.st_nlink!=1:raise Rejected('file-kind-changed:'+rel)
                    if (current.st_dev,current.st_ino,current.st_size,current.st_mtime_ns)!=(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns):raise Rejected('file-changed:'+rel)
                    h=hashlib.sha256();n=0;dest=None
                    if destination:
                        target=destination/rel;target.parent.mkdir(mode=0o700,parents=True,exist_ok=True);dest=target.open('xb')
                    try:
                        while True:
                            if time.monotonic()>=end:raise Rejected('collection-time-limit')
                            chunk=os.read(source,65536)
                            if not chunk:break
                            n+=len(chunk)
                            if n>before.st_size:raise Rejected('file-grew:'+rel)
                            h.update(chunk)
                            if dest:dest.write(chunk)
                        after=os.fstat(source)
                        if n!=before.st_size or after.st_mtime_ns!=before.st_mtime_ns:raise Rejected('file-changed:'+rel)
                    finally:
                        if dest:dest.close()
                    manifest[rel]={'sha256':h.hexdigest(),'bytes':n}
                    if fail_after is not None and count>=fail_after:raise Rejected('injected-copy-failure')
                finally:os.close(source)
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
