"""Export bounded fixture evidence, without opening rejected input kinds."""
import gzip,hashlib,json,os,pathlib,shutil,stat,sys
from common import *
out=pathlib.Path(sys.argv[1]);out.mkdir(mode=0o700)
for name in ['image.json','audit.json','gate.json']:shutil.copyfile(ROOT/name,out/name)
shutil.copytree(ROOT/'environment',out/'environment')
for run in sorted((ROOT/'runs').iterdir()):
    dest=out/'runs'/run.name;dest.mkdir(parents=True)
    s=read(run/'state.json')
    (run/'service-journal-final.log').write_text(command(run,['journalctl','-u',s['service'],'--no-pager'])[1])
    for item in run.iterdir():
        if item.is_file() and item.name not in ['operation.lock']:
            if item.name=='workload.log':
                with gzip.GzipFile(filename=str(dest/'workload.log.gz'),mode='wb',mtime=0) as stream:stream.write(item.read_bytes())
            else:shutil.copyfile(item,dest/item.name)
    metadata={}
    for name in ['source','auxiliary']:
        for parent,dirs,files in os.walk(run/name,followlinks=False):
            for n in sorted(dirs+files):
                path=pathlib.Path(parent)/n;st=path.lstat();rel=path.relative_to(run).as_posix();row={'mode':st.st_mode,'bytes':st.st_size,'links':st.st_nlink,'uid':st.st_uid,'gid':st.st_gid}
                if stat.S_ISLNK(st.st_mode):row['target']=os.readlink(path)
                if stat.S_ISREG(st.st_mode) and st.st_nlink==1 and st.st_size<=65536:
                    row['sha256']=hashlib.sha256(path.read_bytes()).hexdigest();target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
                elif not stat.S_ISDIR(st.st_mode):row['payloadOmitted']='rejected kind, hardlink or >64KiB evidence payload; not a collected submission'
                metadata[rel]=row
    write(dest/'source-metadata.json',metadata)
    for name in ['result','quarantined-result']:
        if (run/name).exists():shutil.copytree(run/name,dest/name)
write(out/'export.json',{'fixtureOnly':True,'runs':len(list((ROOT/'runs').iterdir())),'note':'All manager records, full published fixture results, small ordinary inputs, no rejected-kind reads; workload logs losslessly gzip encoded.',**stamp()})
print(json.dumps(read(out/'export.json')))
