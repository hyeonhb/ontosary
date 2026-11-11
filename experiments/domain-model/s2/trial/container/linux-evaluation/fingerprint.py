"""Manager-only complete Linux environment fingerprint, including dependency symlink confinement."""
import hashlib,json,os,pathlib,stat

def fingerprint(root):
    root=pathlib.Path(root).resolve();records={}
    for parent,dirs,files in os.walk(root,followlinks=False):
        for name in sorted(dirs+files):
            f=pathlib.Path(parent)/name;relative=f.relative_to(root).as_posix();s=f.lstat()
            if stat.S_ISLNK(s.st_mode):
                immutable_tool_link=(str(root)=='/opt/ontosary-linux-evaluation/tools' and relative=='node_modules/typescript' and os.readlink(f)=='/opt/s2-tools/node_modules/typescript')
                if not immutable_tool_link and not f.resolve(strict=True).is_relative_to(root):raise RuntimeError('dependency-symlink-outside-environment:'+relative)
                records[relative]={'symlink':os.readlink(f)}
            elif stat.S_ISREG(s.st_mode):
                h=hashlib.sha256()
                with f.open('rb') as stream:
                    for b in iter(lambda:stream.read(1024*1024),b''):h.update(b)
                records[relative]={'sha256':h.hexdigest(),'bytes':s.st_size}
            elif not stat.S_ISDIR(s.st_mode):raise RuntimeError('environment-nonregular:'+relative)
    digest=hashlib.sha256(json.dumps(records,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {'sha256':digest,'fileCount':len(records),'records':records}
def inputs_fingerprint(root):
    root=pathlib.Path(root);parts={name:fingerprint(root/name) for name in ['environment','tools','assembled']}
    digest=hashlib.sha256(json.dumps({name:value['sha256'] for name,value in parts.items()},sort_keys=True).encode()).hexdigest()
    return {'sha256':digest,'fileCount':sum(v['fileCount'] for v in parts.values()),'parts':parts}

if __name__=='__main__':
    import sys,time,gzip
    started=time.monotonic();result=inputs_fingerprint(sys.argv[1]) if len(sys.argv)>3 and sys.argv[3]=='inputs' else fingerprint(sys.argv[1]);result['seconds']=time.monotonic()-started
    output=pathlib.Path(sys.argv[2]);output.write_bytes(gzip.compress((json.dumps(result,sort_keys=True)+'\n').encode(),mtime=0))
    print(json.dumps({k:v for k,v in result.items() if k not in ['records','parts']}))
