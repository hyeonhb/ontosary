"""Guest-only preparation; bounded install and unchanged historical input gate."""
import gzip,hashlib,json,os,pathlib,subprocess,sys,time
ROOT=pathlib.Path('/opt/ontosary-linux-evaluation');LOG=ROOT/'preparation';LOG.mkdir(parents=True,exist_ok=True)
NERD=['nerdctl','--address','/run/containerd/containerd.sock','--namespace','default']
def write(name,value): (LOG/name).write_text(json.dumps(value,indent=2)+'\n')
def command(name,args,timeout=30,check=True):
 start=time.monotonic()
 with (LOG/(name+'.log')).open('xb') as out:
  try:p=subprocess.run(args,stdout=out,stderr=subprocess.STDOUT,timeout=timeout);code=p.returncode
  except subprocess.TimeoutExpired:code=124
 write(name+'.command.json',{'command':args,'seconds':time.monotonic()-start,'exitCode':code})
 if check and code:raise RuntimeError(name+': '+str(code))
 return code

def fingerprint(name):
 inv=json.loads(gzip.decompress((ROOT/'tools/repo/experiments/public-app/results/2026-11-08/vendure/inventory.json.gz').read_bytes()))
 records={i['path']:hashlib.sha256((ROOT/'environment'/i['path']).read_bytes()).hexdigest() for i in inv}
 write(name+'.json',records)
 assert all(records[i['path']]==i['sha256'] for i in inv)
 return records

def run(name,args,timeout):
 # Preparatory containers are not calibration receipts. Their native identity and exit remain explicit.
 command(name+'-create',NERD+['create','--pull=never','--name','s2-linux-'+name,*args])
 cid=(LOG/(name+'-create.log')).read_text().strip()
 command(name+'-inspect-before',NERD+['inspect',cid])
 try:
  command(name+'-start',NERD+['start',cid])
  code=command(name+'-wait',NERD+['wait',cid],timeout,False)
  if code==124:command(name+'-kill',NERD+['kill','--signal','SIGKILL',cid],10,False)
  command(name+'-inspect-after',NERD+['inspect',cid])
  command(name+'-logs',NERD+['logs',cid],30)
  state=json.loads((LOG/(name+'-inspect-after.log')).read_text())[0]['State']
  assert not state['Running'] and state['Pid']==0
  write(name+'-result.json',{'cid':cid,'state':state,'waitCommandExitCode':code,'calibration':False})
  return state['ExitCode'] if code!=124 else 124
 finally:
  command(name+'-remove',NERD+['rm','--force',cid],15,False)
  command(name+'-absence',NERD+['inspect',cid],10,False)

command('versions',['sh','-c','uname -a; systemctl --version; nerdctl --version; containerd --version'])
command('build',NERD+['build','--build-arg','BASE_IMAGE=docker.io/library/node@sha256:4a4884e8a44826194dff92ba316264f392056cbe243dcc9fd3551e71cea02b90','-t','ontosary-s2-linux-evaluation:20261111',str(ROOT/'build')],300)
sys.path.insert(0,str(ROOT/'lifecycle'))
from image import identify
image=identify(LOG,'ontosary-s2-linux-evaluation:20261111');write('image.json',image)
command('minimal',NERD+['run','--rm','--pull=never','--name','s2-linux-minimal','--user','1000:1000','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','--read-only',image['target'],'sh','-c','id; node --version; npm --version'],30)
fingerprint('source-before')
command('ownership',['chown','-R','1000:1000',str(ROOT/'environment')])
code=run('install',['--user','1000:1000','--cap-drop','ALL','--security-opt','no-new-privileges','--cpus','2','--memory','4g','--pids-limit','256','--mount',f'type=bind,src={ROOT}/environment,dst=/environment,readonly=false','--mount',f'type=bind,src={ROOT}/tools,dst=/tools,readonly=true',image['target'],'sh','/tools/prepare-vendure.sh'],900)
fingerprint('source-after')
if code:raise RuntimeError('Linux installation/common build failed: '+str(code))
# Resolve ESM TypeScript in this image, with immutable tools and no host node_modules.
(ROOT/'tools/node_modules').mkdir();os.symlink('/opt/s2-tools/node_modules/typescript',ROOT/'tools/node_modules/typescript')
output=ROOT/'output';output.mkdir();os.chown(output,1000,1000)
code=run('open',['--user','1000:1000','--cap-drop','ALL','--security-opt','no-new-privileges','--network','none','--cpus','2','--memory','4g','--pids-limit','256','--read-only','--tmpfs','/tmp:rw,nosuid,nodev,size=64m','--mount',f'type=bind,src={ROOT}/environment,dst=/environment,readonly=true','--mount',f'type=bind,src={ROOT}/tools,dst=/tools,readonly=true','--mount',f'type=bind,src={output},dst=/output,readonly=false',image['target'],'node','/tools/open.mjs'],180)
fingerprint('source-final')
write('gate.json',{'openExitCode':code,'status':'opened' if code==0 else 'blocked','trialAuthorized':False,'readyForTrial':False})
print(json.dumps({'status':'opened' if code==0 else 'blocked','openExitCode':code}))
raise SystemExit(code)
