"""Read-only reuse of a verified OCI archive; no rootfs extraction or install."""
import hashlib,json,pathlib,tarfile,time,sys
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'container/execution-lifecycle'))
from artifacts import verify_image_archive
VENDOR='usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-arm64/vendor/aarch64-unknown-linux-musl/'
SELECTED={
 'usr/local/bin/node','usr/local/LICENSE','usr/local/CHANGELOG.md',
 'usr/local/lib/node_modules/@openai/codex/package.json',
 'usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-arm64/package.json',
 VENDOR+'bin/codex',VENDOR+'codex-resources/bwrap',VENDOR+'codex-path/rg',VENDOR+'codex-package.json'}
EXPECTED={VENDOR+'bin/codex':'e7f91e14eab4ba3a0f65047c1757b593409d4ce791ccb6ac65c67c970dfed76f',VENDOR+'codex-resources/bwrap':'0f543a7356ab343b4827222f910461d4196778f328b28acd6c126ef18e9557ab'}
MAX_BYTES=512*1024*1024

def safe_name(name):
 p=pathlib.PurePosixPath(name)
 if p.is_absolute() or '..' in p.parts or not p.parts:raise ValueError('unsafe-archive-path')
 return p.as_posix()

def extract(record,dest,end):
 dest=pathlib.Path(dest)
 if dest.exists():raise ValueError('extraction-destination-exists')
 verified=verify_image_archive(record['path'],record['request']['image'],end)
 dest.mkdir(mode=0o700);files={};total=0
 with tarfile.open(record['path']) as outer:
  manifest=json.load(outer.extractfile('blobs/'+record['request']['image']['target'].replace(':','/')))
  for layer in manifest['layers']:
   if layer['mediaType']!='application/vnd.oci.image.layer.v1.tar+gzip':raise ValueError('unsupported-layer-format')
   with tarfile.open(fileobj=outer.extractfile('blobs/'+layer['digest'].replace(':','/')),mode='r|gz') as archive:
    for member in archive:
     if time.monotonic()>=end:raise TimeoutError('extraction-deadline')
     name=safe_name(member.name)
     if (member.issym() or member.islnk()) and any(p==name or p.startswith(name+'/') for p in SELECTED):raise ValueError('selected-ancestor-link')
     # No whiteout may silently invalidate a selected file or its ancestor.
     if '/.wh.' in name or name.startswith('.wh.'):
      parent=pathlib.PurePosixPath(name).parent;leaf=pathlib.PurePosixPath(name).name
      target=str(parent/(leaf[4:]))
      if any(p==target or p.startswith(target+'/') or (leaf=='.wh..wh..opq' and (str(parent)=='.' or p.startswith(str(parent)+'/'))) for p in SELECTED):raise ValueError('selected-whiteout')
     if name not in SELECTED:continue
     if not member.isfile() or member.issym() or member.islnk() or member.mode&0o6000:raise ValueError('selected-file-kind-or-setid')
     if name in files:raise ValueError('selected-file-replaced')
     total+=member.size
     if total>MAX_BYTES:raise ValueError('selected-byte-limit')
     path=dest/name;path.parent.mkdir(parents=True,exist_ok=True)
     h=hashlib.sha256();size=0
     with archive.extractfile(member) as source,path.open('xb') as out:
      while data:=source.read(1024*1024):
       if time.monotonic()>=end:raise TimeoutError('extraction-deadline')
       out.write(data);h.update(data);size+=len(data)
     if size!=member.size:raise ValueError('partial-member')
     mode=0o555 if name in [VENDOR+'bin/codex',VENDOR+'codex-resources/bwrap',VENDOR+'codex-path/rg','usr/local/bin/node'] else 0o444
     path.chmod(mode);files[name]={'sha256':h.hexdigest(),'bytes':size,'mode':oct(mode),'layer':layer['digest']}
 if set(files)!=SELECTED:raise ValueError('missing-selected-public-file')
 if any(files[n]['sha256']!=h for n,h in EXPECTED.items()):raise ValueError('pinned-binary-hash')
 return {'archive':record['actual'],'image':record['request']['image'],'verifiedOCI':verified,'files':files,'bytes':total,'rootfsInstalled':False,'linksExtracted':0,'downloads':0,'builds':0}
