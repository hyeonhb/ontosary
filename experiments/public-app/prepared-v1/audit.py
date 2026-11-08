"""Snapshot immutable upstream files and generated/install artifacts separately."""
import datetime, gzip, hashlib, json, os, pathlib, sys
here = pathlib.Path(__file__).resolve().parent
repo = here.parents[2]
m = json.loads((here/'manifest.json').read_text())
root = pathlib.Path(m['cache'])/'vendure'
out = pathlib.Path(sys.argv[1]).resolve()
if out.exists(): raise SystemExit('Use a new audit output')
out.mkdir(parents=True)
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def write(name, value):
    b=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
    (out/name).write_bytes(gzip.compress(b,mtime=0) if name.endswith('.gz') else b)
inv=json.loads(gzip.decompress((root.parent/'vendure-inventory.json.gz').read_bytes()))
changed=[]
for e in inv:
    p=root/e['path']
    if 'symlink' in e:
        if not p.is_symlink() or str(p.readlink())!=e['symlink']:changed.append(e['path'])
    elif not p.is_file() or sha(p)!=e['sha256']:changed.append(e['path'])
known={e['path'] for e in inv}
dependency_files=[]; generated=[]; links=[]
for directory,dirs,files in os.walk(root,followlinks=False):
    for name in list(dirs):
        p=pathlib.Path(directory)/name
        if p.is_symlink(): links.append(dict(path=str(p.relative_to(root)),target=os.readlink(p)))
    for name in files:
        p=pathlib.Path(directory)/name;rel=str(p.relative_to(root))
        if rel in known:continue
        if p.is_symlink():links.append(dict(path=rel,target=os.readlink(p)));continue
        item=dict(path=rel,bytes=p.stat().st_size,sha256=sha(p))
        (dependency_files if 'node_modules' in p.relative_to(root).parts else generated).append(item)
lock=json.loads((root/'package-lock.json').read_text());packages=[]
for loc,entry in lock['packages'].items():
    if not loc or 'node_modules' not in pathlib.Path(loc).parts:continue
    p=root/loc/'package.json'
    if not p.is_file():continue
    data=json.loads(p.read_text());licenses=[]
    for f in sorted(p.parent.iterdir()):
        if f.is_file() and f.name.lower().startswith(('license','licence','copying','notice')):
            licenses.append(dict(file=str(f.relative_to(root)),sha256=sha(f),bytes=f.stat().st_size))
    packages.append(dict(path=loc,name=data.get('name'),version=data.get('version'),license=data.get('license',data.get('licenses')),packageJsonSha256=sha(p),resolved=entry.get('resolved'),integrity=entry.get('integrity'),workspaceLink=entry.get('link',False),licenseFiles=licenses))
write('dependency-files.json.gz',sorted(dependency_files,key=lambda x:x['path']))
write('packages.json.gz',packages)
write('generated-files.json',sorted(generated,key=lambda x:x['path']))
write('links.json',sorted(links,key=lambda x:x['path']))
write('summary.json',dict(originalEntries=len(inv),changedOriginalFiles=changed,dependencyFiles=len(dependency_files),dependencyBytes=sum(f['bytes'] for f in dependency_files),installedPackageEntries=len(packages),generatedFiles=len(generated),generatedBytes=sum(f['bytes'] for f in generated),lockfileSha256=sha(root/'package-lock.json'),originalInventorySha256=sha(root.parent/'vendure-inventory.json.gz'),artifacts={name:sha(out/name) for name in ['dependency-files.json.gz','packages.json.gz','generated-files.json','links.json']},note='Package license declarations/file hashes and lockfile integrity are provenance, not a complete dependency license/legal audit. No installed dependencies or generated lib files are redistributed. Common build outputs are separate from pinned original generated source.'))
assert not changed,changed
print(json.dumps(dict(originalEntries=len(inv),changedOriginalFiles=changed,dependencyFiles=len(dependency_files),dependencyBytes=sum(f['bytes'] for f in dependency_files),installedPackageEntries=len(packages),generatedFiles=len(generated))))
