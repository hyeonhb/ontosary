"""Unprivileged finite parent control plus exactly one real CLI sandbox call."""
# Unexecuted draft: this round missed its preparation gate. No runtime entry is authorized.
if __name__ == "__main__":
 raise SystemExit("inconclusive: preparation gate missed; runtime draft disabled")
import hashlib,json,os,pathlib,socket,subprocess,sys,threading,time
BASE=pathlib.Path('/opt/ontosary-vm');VENDOR=BASE/'public/usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-arm64/vendor/aarch64-unknown-linux-musl'
NODE=str(BASE/'public/usr/local/bin/node');CLI=str(VENDOR/'bin/codex')
def read(p):return pathlib.Path(p).read_text()
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def call(args,env,timeout=3,fd=(),on_start=None):
 start=time.monotonic()
 try:
  p=subprocess.Popen(args,env=env,cwd=run/'source',stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,pass_fds=fd)
  if on_start:on_start(p.pid)
  try:stdout,stderr=p.communicate(timeout=timeout)
  except subprocess.TimeoutExpired:p.kill();p.communicate(timeout=2);raise
  return {'args':args,'pid':p.pid,'exitCode':p.returncode,'stdout':stdout[:65536],'stderr':stderr[:65536],'truncated':len(stdout)>65536 or len(stderr)>65536,'seconds':time.monotonic()-start}
 except subprocess.TimeoutExpired as e:return {'args':args,'exitCode':124,'timeout':True,'stdout':(e.stdout or b'').decode()[:65536],'stderr':(e.stderr or b'').decode()[:65536],'seconds':time.monotonic()-start}
def serve(family,address):
 s=socket.socket(family,socket.SOCK_STREAM);s.bind(address);s.listen(4);s.settimeout(.3)
 def loop():
  until=time.monotonic()+30
  while time.monotonic()<until:
   try:c,_=s.accept();c.close()
   except socket.timeout:pass
   except OSError:break
 threading.Thread(target=loop,daemon=True).start();return s
def connect(family,address):
 with socket.socket(family,socket.SOCK_STREAM) as s:s.settimeout(1);s.connect(address);return True

if __name__=='__main__':
 rid,mode=sys.argv[1:];run=BASE/'runs'/rid;cfg=json.loads((run/'public.json').read_text());cli=pathlib.Path(cfg['cliHome']);home=pathlib.Path(cfg['home'])
 env={'PATH':str(BASE/'public/usr/local/bin')+':/usr/bin:/bin','HOME':str(cli.parent),'CODEX_HOME':str(cli),'TMPDIR':str(run/'scratch'),'LANG':'C.UTF-8','S2_FAKE_AUTH':os.environ['S2_FAKE_AUTH']}
 out={'fixtureOnly':True,'validSubmission':False,'pid':os.getpid(),'uid':os.getuid(),'gid':os.getgid(),'groups':os.getgroups(),'mode':mode,'status':read('/proc/self/status'),'cgroup':read('/proc/self/cgroup'),'apparmor':read('/proc/self/attr/current'),'environmentKeys':sorted(os.environ),'configSha256':sha(cli/'config.toml'),'binaries':{'node':sha(NODE),'codex':sha(CLI),'bwrap':sha(VENDOR/'codex-resources/bwrap')},'calls':[],'credentialTransfers':0,'logins':0,'refreshes':0,'providerRequests':0,'modelCalls':0,'trialRuns':0}
 (run/'output/ready.json').write_text(json.dumps({'pid':os.getpid(),'status':out['status'],'cgroup':out['cgroup']}))
 end=time.monotonic()+6
 while not (run/'go').exists():
  if time.monotonic()>end:raise RuntimeError('manager-admission-missing')
  time.sleep(.05)
 try:
  out['calls'] += [call([CLI,'--version'],env),call([CLI,'sandbox','--help'],env)] if mode.startswith('normal') else []
  out['nodeVersion']=call([NODE,'--version'],env)
  if mode.startswith('normal') and (out['calls'][0]['exitCode'] or out['calls'][0]['stdout']!='codex-cli 0.167.0-alpha.3.2\n' or out['calls'][1]['exitCode']):raise RuntimeError('pinned-cli-discovery-failed')
  if out['nodeVersion']['stdout']!='v22.19.0\n':raise RuntimeError('pinned-node-version')
  out['parent']={'sourceRead':bool(read(run/'source/input.txt')),'materialRead':bool(read(run/'materials/input.txt')),'fakeFileExists':bool(read(cli/'fake-token.txt')),'fakeEnvironmentPresent':'S2_FAKE_AUTH' in os.environ,'controlCanaryReadable':bool(read(cli.parent/'control-canary'))}
  (run/'source/parent.txt').write_text('parent write\n');out['parent']['sourceWrite']=True
  fd=os.open(cli/'fake-token.txt',os.O_RDONLY);os.set_inheritable(fd,True);out['parent']['fdOpen']=bool(os.fstat(fd).st_size)
  (run/'source/fake-link').symlink_to(cli/'fake-token.txt')
  sockets=[];servers={};positive={};unavailable={}
  for ident,family,address in [('ipv4',socket.AF_INET,('127.0.0.1',0)),('ipv6',socket.AF_INET6,('::1',0)),('unix',socket.AF_UNIX,str(cli/'fixture.sock'))]:
   try:
    s=serve(family,address);sockets.append(s);a=s.getsockname();positive[ident]=connect(family,a);servers[ident]={'path':a} if family==socket.AF_UNIX else {'host':a[0],'port':a[1]}
   except OSError as e:unavailable[ident]={'status':'not-applicable','errno':e.errno}
  if 'ipv4' not in servers or 'unix' not in servers:raise RuntimeError('required-local-positive-control-unavailable')
  out['networkPositive']=positive;out['networkNotApplicable']=unavailable
  targets={'fakeDirect':str(cli/'fake-token.txt'),'fakeSymlink':str(run/'source/fake-link'),'controlDirect':str(cli.parent/'control-canary'),'otherRun':str(BASE/'other-run/marker'),
    'parentProcRoot':f'/proc/{os.getpid()}/root'+str(cli/'fake-token.txt'),'parentProcEnvironment':f'/proc/{os.getpid()}/environ','parentProcFd':f'/proc/{os.getpid()}/fd/{fd}'}
  out['parent']['procRootReadable']=bool(read(targets['parentProcRoot']));out['parent']['procEnvironmentPresent']=b'S2_FAKE_AUTH=' in pathlib.Path(targets['parentProcEnvironment']).read_bytes();out['parent']['procFdReadable']=bool(read(targets['parentProcFd']))
  out['management']={}
  for key,args in [('sudo',['sudo','-n','true']),('serviceControl',['systemctl','--no-ask-password','start','ontosary-vm-forbidden.service'])]:
   try:out['management'][key]=call(args,env)
   except FileNotFoundError:out['management'][key]={'status':'not-exposed','exitCode':127}
  for key,path in [('cgroupMove','/sys/fs/cgroup/cgroup.procs'),('runtimeSocket','/run/containerd/containerd.sock'),('managerState',str(BASE/'control/state.json')),('managerSSH','/home/'+cfg['managerUser']+'/.ssh/authorized_keys')]:
   try:
    if key=='cgroupMove':pathlib.Path(path).write_text(str(os.getpid()))
    else:pathlib.Path(path).read_bytes()
    out['management'][key]={'accessible':True}
   except OSError as e:out['management'][key]={'accessible':False,'errno':e.errno}
  try:os.kill(cfg['supervisorPid'],0);out['management']['supervisorSignal']={'accessible':True}
  except OSError as e:out['management']['supervisorSignal']={'accessible':False,'errno':e.errno}
  out['routes']={n:read('/proc/net/'+n) for n in ['route','ipv6_route','dev']}
  p={'mode':mode,'source':str(run/'source'),'materials':str(run/'materials'),'scratch':str(run/'scratch'),'home':str(home),'outside':str(BASE/'other-run'),'readTargets':targets,'servers':servers,'fd':fd}
  args=[CLI,'sandbox','-P','fixture','-C',str(run/'source'),'--',NODE,str(run/'source/payload.mjs'),json.dumps(p,separators=(',',':'))]
  out['inheritedFdPassedToCLI']=fd
  def started(pid):
   out['sandboxInvocation']={'args':args,'pid':pid,'parentPid':os.getpid(),'atMono':time.monotonic()}
   try:out['sandboxInvocation']['procCmdline']=pathlib.Path(f'/proc/{pid}/cmdline').read_bytes().decode().split('\0')[:-1];out['sandboxInvocation']['cgroup']=read(f'/proc/{pid}/cgroup')
   except OSError:out['sandboxInvocation']['procUnavailable']=True
   out['configUnchanged']=sha(cli/'config.toml')==out['configSha256'];out['materialsUnchanged']=sha(run/'materials/input.txt')==cfg['materialSha256']
   (run/'output/preflight.json').write_text(json.dumps(out,indent=2)+'\n')
  out['calls'].append(call(args,env,15,(fd,),started));os.close(fd)
  payload=run/'source/payload.json';out['nativePayloadStarted']=payload.exists();out['payload']=json.loads(payload.read_text()) if payload.exists() else None
  out['configUnchanged']=sha(cli/'config.toml')==out['configSha256'];out['materialsUnchanged']=sha(run/'materials/input.txt')==cfg['materialSha256']
 except Exception as e:out['error']=str(e)
 finally:
  (run/'output/result.json').write_text(json.dumps(out,indent=2)+'\n')
  print(json.dumps({'resultRecorded':True,'payloadStarted':out.get('nativePayloadStarted',False)}),flush=True)
