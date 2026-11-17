"""Pinned runtime environment and guest-only tool discovery, before any create."""
import os,pathlib,shutil,stat,time
from identity import RUNTIME_ENV,SYSTEM_PATH
TOOLS=('nerdctl','ctr','runc','containerd','apparmor_parser','aa-exec','true')
def validate_env(env):
 if env!=RUNTIME_ENV or any(not x.startswith('/') or x in ['','.'] for x in env.get('PATH','').split(':')):raise RuntimeError('runtime-environment-contract')
def verify_tools(command):
 validate_env(RUNTIME_ENV);paths={}
 def owned(p):
  p=pathlib.Path(p).resolve(strict=True)
  for item in [p,*p.parents]:
   s=item.stat()
   if s.st_uid!=0 or s.st_mode&0o022:raise RuntimeError('runtime-tool-owner:'+str(item))
  return str(p)
 for folder in SYSTEM_PATH.split(':'):owned(folder)
 for name in TOOLS:
  found=shutil.which(name,path=SYSTEM_PATH)
  if not found:raise RuntimeError('runtime-tool-missing:'+name)
  paths[name]={'resolved':owned(found),'lookup':found}
 probes={}
 for name,args in [('nerdctl',['nerdctl','--version']),('containerd',['containerd','--version']),('runc',['runc','--version']),('runcFeatures',['runc','features']),('apparmorParser',['apparmor_parser','--version']),('apparmorPackage',['dpkg-query','-W','apparmor']),('apparmorExec',['aa-exec','--help']),('apparmorEnabled',['cat','/sys/module/apparmor/parameters/enabled']),('apparmorTrue',['aa-exec','true'])]:
  probes[name]=command(args)
 if 'runc version 1.5.2' not in probes['runc'][1] or 'nerdctl version 2.4.2' not in probes['nerdctl'][1] or 'b7a25261e029d68978bbf290df0a62fc819b3c51' not in probes['containerd'][1]:raise RuntimeError('runtime-version-mismatch')
 if probes['apparmorEnabled'][1].strip()!='Y':raise RuntimeError('apparmor-disabled')
 return {'environment':RUNTIME_ENV,'paths':paths,'probes':probes,'beforeContainerCreate':True}
