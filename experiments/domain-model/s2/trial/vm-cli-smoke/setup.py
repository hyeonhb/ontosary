"""Fixed root setup inside the disposable guest; no package installation."""
import hashlib,json,os,pathlib,pwd,shutil,subprocess,sys
BASE=pathlib.Path('/opt/s2-smoke');UID=22002
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        while b:=f.read(1024*1024):h.update(b)
    return h.hexdigest()
def main():
    manager=sys.argv[1];assert os.getuid()==0 and manager.replace('_','').replace('-','').isalnum()
    manager_home=pwd.getpwnam(manager).pw_dir
    subprocess.run(['useradd','--uid',str(UID),'--user-group','--no-create-home','--shell','/usr/sbin/nologin','s2smoke'],check=True,timeout=5)
    for name in ['/source','/scratch','/home/worker','/home/runner/cli-state']:
        p=pathlib.Path(name);p.mkdir(parents=True,exist_ok=False,mode=0o700);os.chown(p,UID,UID)
    pathlib.Path('/materials').mkdir(mode=0o755)
    for name,body in [('/source/input.txt','smoke source\n'),('/materials/input.txt','smoke material\n')]:
        pathlib.Path(name).write_text(body);os.chmod(name,0o444)
    shutil.copyfile(BASE/'payload.mjs','/source/payload.mjs');os.chmod('/source/payload.mjs',0o444)
    shutil.copyfile(BASE/'config.toml','/home/runner/cli-state/config.toml');os.chmod('/home/runner/cli-state/config.toml',0o444)
    plan=json.loads((BASE/'plan.json').read_text());plan['managerNamespace']=os.readlink('/proc/self/ns/net');(BASE/'plan.json').write_text(json.dumps(plan))
    dependencies=subprocess.run(['ldd',str(BASE/'public/usr/local/bin/node')],capture_output=True,text=True,timeout=3)
    if dependencies.returncode or 'not found' in dependencies.stdout:raise RuntimeError('required-node-library-missing:'+dependencies.stdout+dependencies.stderr)
    text=f'''[Service]
Type=exec
User=s2smoke
Group=s2smoke
ExecStart=/usr/bin/env -i PATH=/usr/sbin:/usr/bin:/sbin:/bin LANG=C.UTF-8 HOME=/home/worker /usr/bin/python3 /opt/s2-smoke/worker.py
WorkingDirectory=/source
NoNewPrivileges=yes
CapabilityBoundingSet=
AmbientCapabilities=
PrivateNetwork=yes
ProtectSystem=strict
ProtectControlGroups=yes
RestrictSUIDSGID=yes
Delegate=no
InaccessiblePaths=-/run/user -/run/dbus -/run/systemd/private -/run/containerd -/run/docker.sock -/root -{manager_home}/.ssh
ReadWritePaths=/source /scratch /home/worker /home/runner/cli-state
ReadOnlyPaths=/home/runner/cli-state/config.toml
CPUQuota=200%
MemoryMax=4G
TasksMax=256
RuntimeMaxSec=25
TimeoutStopSec=3
KillMode=control-group
StandardOutput=journal
StandardError=journal
'''
    # systemd-run --pipe receives the same service properties; save exact unit for review.
    (BASE/'worker.service').write_text(text)
    print(json.dumps({'guestPython':sys.version,'worker':pwd.getpwnam('s2smoke').pw_uid,'managerNamespace':plan['managerNamespace'],'nodeDependencies':dependencies.stdout,'unit':text,'config':pathlib.Path('/home/runner/cli-state/config.toml').read_text(),'plan':plan,'bootId':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()}))
if __name__=='__main__':main()
