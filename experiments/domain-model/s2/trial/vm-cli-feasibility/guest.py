"""Disposable-VM manager. Worker and supervisor are separate system services."""
# Unexecuted draft: this round missed its preparation gate. No runtime entry is authorized.
if __name__ == "__main__":
 raise SystemExit("inconclusive: preparation gate missed; runtime draft disabled")
import datetime,hashlib,json,os,pathlib,pwd,shutil,subprocess,sys,time,uuid
BASE=pathlib.Path('/opt/ontosary-vm');HERE=BASE/'code'
sys.path.insert(0,str(HERE/'lifecycle'))
from collector import inventory,open_directory,read_regular
UID=22001;USER='s2fixture';PROPS=['Id','LoadState','ActiveState','SubState','InvocationID','MainPID','ControlGroup','Result','ExecMainStatus','InactiveEnterTimestampMonotonic','User','Group','NoNewPrivileges','CapabilityBoundingSet','AmbientCapabilities','PrivateNetwork','CPUQuotaPerSecUSec','MemoryMax','TasksMax','ProtectControlGroups','Delegate','KillMode','RuntimeMaxUSec']
def stamp():return {'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mono':time.monotonic()}
def write(p,v):
 p=pathlib.Path(p);tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(v,indent=2)+'\n');os.replace(tmp,p)
def read(p):return json.loads(pathlib.Path(p).read_text())
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def command(args,timeout=5,check=True):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
 if check and p.returncode:raise RuntimeError('guest-command:'+str(args)+':'+p.stderr[-1000:])
 return {'args':args,'exitCode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'at':stamp()}
def show(unit):
 raw=command(['systemctl','show',unit,*['--property='+p for p in PROPS]])
 raw['fields']=dict(line.split('=',1) for line in raw['stdout'].splitlines() if '=' in line);return raw
def security(fields):
 return (fields.get('User')==USER and fields.get('Group')==USER and fields.get('NoNewPrivileges')=='yes'
  and fields.get('CapabilityBoundingSet')=='' and fields.get('AmbientCapabilities')=='' and fields.get('PrivateNetwork')=='yes'
  and fields.get('MemoryMax')==str(4*1024**3) and fields.get('TasksMax')=='256' and fields.get('CPUQuotaPerSecUSec')=='2s'
  and fields.get('ProtectControlGroups')=='yes' and fields.get('Delegate')=='no' and fields.get('KillMode')=='control-group')
def prepare(manager_user):
 if os.getuid()!=0:raise RuntimeError('manager-must-be-root')
 command(['useradd','--uid',str(UID),'--user-group','--no-create-home','--shell','/usr/sbin/nologin',USER])
 BASE.chmod(0o755);(BASE/'control').mkdir(mode=0o700);write(BASE/'control/state.json',{'private':True})
 (BASE/'runs').mkdir(mode=0o755);(BASE/'other-run').mkdir(mode=0o755);(BASE/'other-run/marker').write_text('synthetic other run\n')
 (pathlib.Path('/run/systemd/system/ontosary-vm-forbidden.service')).write_text('[Service]\nType=oneshot\nExecStart=/usr/bin/true\n')
 result={'bootId':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'managerUser':manager_user,'worker':{'uid':UID,'name':USER,'passwd':pwd.getpwnam(USER).pw_shell},'id':command(['id',USER]),'uname':command(['uname','-a']),'systemd':command(['systemctl','--version']),'sysctls':{},'container':'not-applicable','hostMounts':command(['findmnt','--json']), 'priorFixturePathsAbsent':not any(pathlib.Path('/home').glob('s2cli-*'))}
 for key in ['kernel/unprivileged_userns_clone','user/max_user_namespaces','kernel/apparmor_restrict_unprivileged_userns']:
  p=pathlib.Path('/proc/sys')/key;result['sysctls'][key]=p.read_text().strip() if p.exists() else 'not-exposed'
 for name in ['node']:
  result[name+'Dependencies']=command(['ldd',str(BASE/'public/usr/local/bin'/name)],check=False)
  if 'not found' in result[name+'Dependencies']['stdout']:raise RuntimeError('missing-public-binary-library')
 write(BASE/'preparation.json',result);print(json.dumps(result))
def unit_text(rid,mode,manager_user):
 run=BASE/'runs'/rid;cli=pathlib.Path('/home/s2cli-'+rid)/'state';home=pathlib.Path('/home/s2shell-'+rid)
 return f'''[Unit]
Description=Ontosary direct VM fixture {rid}
[Service]
Type=exec
User={USER}
Group={USER}
ExecStart=/usr/bin/python3 {HERE}/worker.py {rid} {mode}
WorkingDirectory={run}/source
Environment=PATH=/usr/bin:/bin LANG=C.UTF-8
EnvironmentFile={run}/environment
NoNewPrivileges=yes
CapabilityBoundingSet=
AmbientCapabilities=
PrivateNetwork=yes
ProtectSystem=strict
ProtectControlGroups=yes
RestrictSUIDSGID=yes
Delegate=no
InaccessiblePaths=-/run/user -/run/containerd -/run/docker.sock -/root -/home/{manager_user}/.ssh
ReadWritePaths={run}/source {run}/scratch {run}/output {cli} {home}
CPUQuota=200%
MemoryMax=4G
TasksMax=256
KillMode=control-group
TimeoutStopSec=3
RuntimeMaxSec=22
StandardOutput=append:{run}/worker.stdout
StandardError=append:{run}/worker.stderr
'''
def register(rid,mode,seconds):
 if mode not in ['normal-1','timeout','wrapper-death','normal-2'] or len(rid)!=12 or any(c not in '0123456789abcdef' for c in rid):raise ValueError('invalid-owned-unit')
 run=BASE/'runs'/rid;run.mkdir(mode=0o755);cli=pathlib.Path('/home/s2cli-'+rid)/'state';home=pathlib.Path('/home/s2shell-'+rid)
 cli.mkdir(parents=True,mode=0o755);home.mkdir(mode=0o700);os.chown(home,UID,UID)
 for name in ['source','scratch','output']:
  (run/name).mkdir(mode=0o700);os.chown(run/name,UID,UID)
 (run/'materials').mkdir(mode=0o755);(run/'materials/input.txt').write_text('material input\n');(run/'materials/input.txt').chmod(0o444)
 (run/'source/input.txt').write_text('source input\n');os.chown(run/'source/input.txt',UID,UID)
 shutil.copyfile(HERE/'payload.mjs',run/'source/payload.mjs')
 for name in ['tmp','log','logs','sessions','state']:
  (cli/name).mkdir(mode=0o700);os.chown(cli/name,UID,UID)
 (cli/'fake-token.txt').write_text('synthetic fixture marker '+rid+'\n');(cli/'fake-token.txt').chmod(0o444)
 (cli.parent/'control-canary').write_text('synthetic control marker\n');(cli.parent/'control-canary').chmod(0o444)
 text=(HERE/'policy.toml').read_text().replace('/home/runner/cli-state',str(cli)).replace('/home/worker',str(home)).replace('/source',str(run/'source')).replace('/scratch',str(run/'scratch')).replace('/materials',str(run/'materials'))
 text=text.replace('PATH = "/usr/local/bin:/usr/bin:/bin"','PATH = "'+str(BASE/'public/usr/local/bin')+':/usr/bin:/bin"').replace('[permissions.fixture.network]','"'+str(BASE/'public')+'" = "read"\n[permissions.fixture.network]')
 (cli/'config.toml').write_text(text);(cli/'config.toml').chmod(0o444);(run/'environment').write_text('S2_FAKE_AUTH=synthetic-'+rid+'\n');(run/'environment').chmod(0o600)
 prep=read(BASE/'preparation.json');service='ontosary-vm-worker-'+rid+'.service';supervisor='ontosary-vm-supervisor-'+rid+'.service'
 state={'runId':rid,'mode':mode,'service':service,'supervisor':supervisor,'registeredAt':stamp(),'finishMono':time.monotonic()+min(float(seconds),114),'container':'not-applicable','fixtureOnly':True,'validSubmission':False,'terminationConfirmed':False,'collectionStatus':'not-started'}
 write(run/'state.json',state);write(run/'public.json',{'cliHome':str(cli),'home':str(home),'managerUser':prep['managerUser'],'materialSha256':sha(run/'materials/input.txt')})
 (run/'heartbeat').touch();worker_text=unit_text(rid,mode,prep['managerUser']);(run/'worker-unit.txt').write_text(worker_text);pathlib.Path('/run/systemd/system',service).write_text(worker_text)
 text=f'[Unit]\nAfter={service}\n[Service]\nType=exec\nExecStart=/usr/bin/python3 {HERE}/guest.py supervise {rid}\nRuntimeMaxSec=110\nTimeoutStopSec=4\nKillMode=control-group\nStandardOutput=append:{run}/supervisor.stdout\nStandardError=append:{run}/supervisor.stderr\n';pathlib.Path('/run/systemd/system',supervisor).write_text(text)
 command(['systemctl','daemon-reload']);command(['systemctl','start',supervisor]);print(json.dumps(state))
def members(cgroup):
 found=[]
 for path in pathlib.Path('/proc').glob('[0-9]*/cgroup'):
  try:
   groups=[line.split(':',2)[2] for line in path.read_text().splitlines()]
   if any(g==cgroup or g.startswith(cgroup+'/') for g in groups):found.append(int(path.parent.name))
  except (FileNotFoundError,ProcessLookupError,PermissionError):pass
 return sorted(found)
def collect(run,state):
 if not state.get('terminationConfirmed') or state.get('pendingCommand'):raise RuntimeError('collection-without-termination')
 destination=run/'collected';destination.mkdir(mode=0o700);manifest={};end=min(time.monotonic()+10,state['finishMono'])
 allow=['source/input.txt','source/parent.txt','source/native.txt','source/payload.json','source/late-ready.json','output/ready.json','output/preflight.json','output/result.json']
 total=0
 for name in allow:
  path=run/name
  if not path.exists():continue
  fd=open_directory(path.parent)
  try:
   before=os.stat(path.name,dir_fd=fd,follow_symlinks=False);total+=before.st_size
   if total>16*1024*1024 or len(manifest)>=128:raise RuntimeError('collection-bound')
   target=destination/name;target.parent.mkdir(parents=True,exist_ok=True);manifest[name]=read_regular(fd,path.name,before,end,target)
  finally:os.close(fd)
 write(run/'collection.json',{'at':stamp(),'files':manifest,'bytes':total,'classification':'synthetic-diagnostic','fixtureOnly':True,'validSubmission':False,'termination':state['termination'],'allowlist':allow});return manifest
def supervise(rid):
 run=BASE/'runs'/rid;s=read(run/'state.json');service=s['service'];raw=[]
 try:
  cfg=read(run/'public.json');cfg['supervisorPid']=os.getpid();write(run/'public.json',cfg)
  s['supervisorPid']=os.getpid();s['supervisorCgroup']=pathlib.Path('/proc/self/cgroup').read_text();s['pendingCommand']=True;write(run/'state.json',s)
  command(['systemctl','start',service]);s['pendingCommand']=False
  deadline=time.monotonic()+5
  while not (run/'output/ready.json').exists():
   if time.monotonic()>deadline:raise RuntimeError('worker-ready-missing')
   time.sleep(.05)
  observed=show(service);raw.append(observed);fields=observed['fields'];cg=fields['ControlGroup'];s.update(invocationId=fields['InvocationID'],cgroup=cg,workerMainPID=int(fields['MainPID']),securityProperties=fields)
  if not security(fields) or len(s['invocationId'])!=32 or not cg.startswith('/system.slice/') or cg in s['supervisorCgroup']:raise RuntimeError('worker-service-security-or-identity')
  path=pathlib.Path('/sys/fs/cgroup'+cg);s['cgroupInode']=path.stat().st_ino;s['cgroupLimits']={name:(path/name).read_text().strip() for name in ['cpu.max','memory.max','pids.max']};s['workerMembersAtAdmission']=members(cg)
  ready=read(run/'output/ready.json')
  if 'CapEff:\t0000000000000000' not in ready['status'] or 'NoNewPrivs:\t1' not in ready['status']:raise RuntimeError('worker-proc-security')
  (run/'go').touch();s['admittedAt']=stamp();write(run/'state.json',s);work_end=time.monotonic()+15
  while True:
   observed=show(service);raw.append(observed)
   if observed['fields']['ActiveState'] in ['inactive','failed']:s['outcome']='exit';break
   if s['mode']=='wrapper-death' and time.time()-(run/'heartbeat').stat().st_mtime>5:s['outcome']='wrapper-death';break
   if time.monotonic()>=work_end:s['outcome']='timeout';break
   time.sleep(.2)
 except Exception as exc:s['error']=str(exc);s['outcome']='blocked'
 finally:
  try:
   command(['systemctl','stop',service],8);s['pendingCommand']=False
   observed=show(service);raw.append(observed);cg=s.get('cgroup')
   if not cg or observed['fields']['InvocationID']!=s.get('invocationId') or observed['fields']['ActiveState'] not in ['inactive','failed']:raise RuntimeError('termination-service-identity')
   remaining=members(cg);path=pathlib.Path('/sys/fs/cgroup'+cg);events=(path/'cgroup.events').read_text() if path.exists() else 'cgroup-removed';s['termination']={'at':stamp(),'service':observed,'cgroup':cg,'remainingPids':remaining,'cgroupEvents':events,'supervisorOutsideWorker':cg not in s['supervisorCgroup']}
   if remaining or (events!='cgroup-removed' and 'populated 0' not in events):raise RuntimeError('worker-cgroup-not-empty')
   s['terminationConfirmed']=True;s['terminationConfirmedAt']=stamp();write(run/'state.json',s)
   s['collectedFiles']=collect(run,s);s['collectionStatus']='collected'
  except Exception as exc:s['finalizeError']=str(exc);s['collectionStatus']='suppressed'
  s['finalizedAt']=stamp();write(run/'service-observations.json',raw);write(run/'state.json',s)
def status(rid):
 run=BASE/'runs'/rid;s=read(run/'state.json');s['lateReady']=(run/'source/late-ready.json').exists();s['lateExists']=(run/'source/late.txt').exists();s['supervisorObservation']=show(s['supervisor']);print(json.dumps(s))
def export(scope):
 import tarfile
 if not scope.replace('-','').isalnum():raise ValueError('export-scope')
 dest=BASE/('export-'+scope);dest.mkdir(mode=0o700);files={};total=0;end=time.monotonic()+20
 allow=['preparation.json','input-manifest.json']
 for run in sorted((BASE/'runs').iterdir()):
  allow += [str(p.relative_to(BASE)) for p in [run/n for n in ['state.json','public.json','worker-unit.txt','worker.stdout','worker.stderr','supervisor.stdout','supervisor.stderr','collection.json','service-observations.json']] if p.is_file()]
  if (run/'collected').exists():allow += [str(p.relative_to(BASE)) for p in (run/'collected').rglob('*') if p.is_file()]
 for name in allow:
  p=BASE/name
  if not p.exists():continue
  fd=open_directory(p.parent)
  try:
   st=os.stat(p.name,dir_fd=fd,follow_symlinks=False);total+=st.st_size
   if total>16*1024*1024 or len(files)>=128:raise RuntimeError('export-bound')
   target=dest/name;target.parent.mkdir(parents=True,exist_ok=True);files[name]=read_regular(fd,p.name,st,end,target,owner=0)
  finally:os.close(fd)
 index='/tmp/ontosary-vm-index-'+scope+'.json';archive='/tmp/ontosary-vm-evidence-'+scope+'.tar.gz';write(index,files)
 with tarfile.open(archive,'w:gz') as t:
  for name in files:t.add(dest/name,arcname=name,recursive=False)
 os.chmod(archive,0o644);os.chmod(index,0o644)
 print(json.dumps({'files':len(files),'bytes':total,'archive':archive,'index':index,'archiveSha256':sha(archive)}))
if __name__=='__main__':
 action,*args=sys.argv[1:]
 if action=='prepare':prepare(*args)
 elif action=='register':register(*args)
 elif action=='supervise':supervise(*args)
 elif action=='status':status(*args)
 elif action=='heartbeat':(BASE/'runs'/args[0]/'heartbeat').touch()
 elif action=='export':export(*args)
 else:raise ValueError('unknown-action')
