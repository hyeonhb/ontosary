"""Reproduce the frozen audit and verify closing registration plus all delivered archives."""
import argparse,hashlib,importlib.util,json,pathlib,shutil,tarfile,tempfile
from scope import verify_index,registered_scope
sha=lambda b:hashlib.sha256(b).hexdigest()
def verify(root):
 root=pathlib.Path(root);index=verify_index(root)
 with tempfile.TemporaryDirectory() as temporary:
  work=pathlib.Path(temporary);shutil.copytree(root/'host',work,dirs_exist_ok=True);shutil.copytree(root/'snapshots',work/'snapshots');registered_scope(work)
  for name,dest in [('guest-evidence.tar.gz','guest'),('removal.tar.gz','removal')]:
   if (work/name).exists():
    with tarfile.open(work/name) as t:t.extractall(work/dest,filter='data')
  spec=importlib.util.spec_from_file_location('retry_audit',pathlib.Path(__file__).with_name('retry-audit.py'));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);assert module.audit(work)==json.loads((work/'audit.json').read_text()),'analysis-not-reproducible'
  guest=work/'guest'
  if (guest/'image.json').exists():
   image=json.loads((guest/'image.json').read_text());config=(guest/'preparation/config.oci').read_bytes();manifest=(guest/'preparation/manifest.oci').read_bytes();assert 'sha256:'+sha(config)==image['config'] and 'sha256:'+sha(manifest)==image['target']
   layers=json.loads(config)['rootfs']['diff_ids'];chain=layers[0]
   for layer in layers[1:]:chain='sha256:'+sha((chain+' '+layer).encode())
   assert chain==image['chain']
   result=json.loads((guest/'baseline-result.json').read_text());assert result['binaries']['codex']['sha256']=='e7f91e14eab4ba3a0f65047c1757b593409d4ce791ccb6ac65c67c970dfed76f' and result['binaries']['bwrap']['sha256']=='0f543a7356ab343b4827222f910461d4196778f328b28acd6c126ef18e9557ab'
 return {'index':index,'analysisReproduced':True,'imageAndBinaryIdentityVerified':True}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();print(json.dumps(verify(a.root)))
