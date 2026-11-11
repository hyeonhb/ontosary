"""Export only predetermined diagnostic records, never a CLI state or host directory."""
import pathlib,tarfile
root=pathlib.Path('/opt/ontosary-namespace-diagnosis')
names=['preparation','trace-image','base-image.json','trace-image.json','trace-build/Dockerfile','policy.toml','probe/probe.mjs']
for mode in ['baseline','traced']:names += [mode+'/audit',mode+'/output',mode+'/source',mode+'/materials']
with tarfile.open('/tmp/s2-namespace-evidence.tar.gz','w:gz') as t:
 for name in names:
  p=root/name
  if p.exists():t.add(p,arcname=name)
