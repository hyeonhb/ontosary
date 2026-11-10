#!/usr/bin/env python3
"""Four finite model-free probes in one dedicated guest. No R11 receipt."""
import argparse, datetime, hashlib, json, pathlib, subprocess, time
p=argparse.ArgumentParser();p.add_argument('--image',required=True);p.add_argument('--deadline',required=True);p.add_argument('--out',required=True);p.add_argument('--payload',required=True);a=p.parse_args()
out=pathlib.Path(a.out);out.mkdir(exist_ok=False);records=[];units=[]
deadline=datetime.datetime.fromisoformat(a.deadline).timestamp();mono_deadline=time.monotonic()+deadline-time.time()
manager=['nerdctl','--address','/run/containerd/containerd.sock','--namespace','default']
ctr=['ctr','--address','/run/containerd/containerd.sock','--namespace','default']
def call(label,args,seconds=30):
 remaining=min(deadline-time.time(),mono_deadline-time.monotonic(),seconds)
 if remaining<=0:raise RuntimeError('Exploration deadline; no new command')
 start=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
 try:
  r=subprocess.run(args,capture_output=True,timeout=remaining);code=r.returncode;stdout=r.stdout;stderr=r.stderr
 except subprocess.TimeoutExpired as e:
  code=124;stdout=e.stdout or b'';stderr=e.stderr or b''
 row={'label':label,'command':args,'utcStart':utc,'monotonicStart':start,'seconds':time.monotonic()-start,'timeoutSeconds':remaining,'exitCode':code}
 (out/(label+'.stdout')).write_bytes(stdout);(out/(label+'.stderr')).write_bytes(stderr);records.append(row);(out/'commands.json').write_text(json.dumps(records,indent=2)+'\n')
 if code!=0:raise RuntimeError(f'{label}: manager command exit {code}; see raw logs')
 return stdout.decode()
def doc(label,args,seconds=30):return json.loads(call(label,args,seconds))
def chain_id(layers):
 value=layers[0]
 for layer in layers[1:]:value='sha256:'+hashlib.sha256((value+' '+layer).encode()).hexdigest()
 return value
call('manager-version',manager+['version']);call('manager-info',manager+['info']);call('native-images',manager+['images','--digests','--no-trunc']);call('endpoint',ctr+['version'])
image=doc('image-native',manager+['image','inspect','--mode=native',a.image])[0]
compat=doc('image-dockercompat',manager+['image','inspect',a.image])[0]
# Native Target is intentionally distinct from Docker-compatible Id/config.
target=image['Image']['Target']['digest'];manifest_bytes=call('image-manifest',ctr+['content','get',target]).encode()
assert 'sha256:'+hashlib.sha256(manifest_bytes).hexdigest()==target
manifest=json.loads(manifest_bytes);assert 'config' in manifest,'Expected built single-platform manifest, not an unresolved index'
config_digest=manifest['config']['digest'];config_bytes=call('image-config',ctr+['content','get',config_digest]).encode()
assert 'sha256:'+hashlib.sha256(config_bytes).hexdigest()==config_digest
config=json.loads(config_bytes);assert config_digest==compat['Id'];assert (config['os'],config['architecture'])==('linux','arm64')
chain=chain_id(config['rootfs']['diff_ids']);assert compat['RootFS']['Layers']==config['rootfs']['diff_ids']
assert 'NODE_VERSION=22.19.0' in config['config']['Env']
identity={'name':image['Image']['Name'],'target':target,'config':config_digest,'platform':'linux/arm64','rootfsChainId':chain,'reference':target,'endpoint':'/run/containerd/containerd.sock','namespace':'default'}
(out/'identity.json').write_text(json.dumps(identity,indent=2)+'\n')
payload=pathlib.Path(a.payload).read_text()
for index,mode in enumerate(['basic','exit7','basic','cli']):
 label=f'{index+1}-{mode}';probe_deadline=min(mono_deadline,time.monotonic()+60)
 def probe(label,args):return call(label,args,max(0,probe_deadline-time.monotonic()))
 before=json.loads(probe(label+'-image-before',manager+['image','inspect','--mode=native',a.image]));assert before[0]['Image']['Target']['digest']==target
 name='s2-smoke-'+label
 args=manager+['create','--pull=never','--name',name,'--user','1000:1000','--cap-drop','ALL','--security-opt','no-new-privileges','--network','none','--cpus','2','--memory','4g','--pids-limit','256','--read-only','--tmpfs','/tmp:rw,nosuid,nodev,size=64m','--env','HOME=/tmp/smoke-home','--env','CODEX_HOME=/tmp/smoke-home/codex',target,'sh','-c',payload,'smoke',mode]
 cid=probe(label+'-create',args).strip();assert len(cid)==64 and all(c in '0123456789abcdef' for c in cid)
 units.append({'id':cid,'name':name,'mode':mode,'removed':False});(out/'units.json').write_text(json.dumps(units,indent=2)+'\n')
 native=json.loads(probe(label+'-native',manager+['inspect','--mode=native',cid]))[0]
 docker=json.loads(probe(label+'-inspect-before',manager+['inspect',cid]))[0]
 snapshot=json.loads(probe(label+'-snapshot',ctr+['snapshots','--snapshotter','overlayfs','info',native['SnapshotKey']]))
 assert snapshot['Parent']==chain,'Container rootfs is not the selected image chain'
 spec=native['Spec'];assert spec['process']['user']['uid']==1000 and spec['process']['user']['gid']==1000
 assert spec['process']['noNewPrivileges'] is True
 assert all(not values for values in spec['process']['capabilities'].values())
 resources=spec['linux']['resources'];assert resources['memory']['limit']==4294967296 and resources['pids']['limit']==256
 assert resources['cpu']['quota']/resources['cpu']['period']==2
 namespaces={n['type']:n for n in spec['linux']['namespaces']};assert 'pid' in namespaces and not namespaces['pid'].get('path');assert 'network' in namespaces
 assert docker['HostConfig']['NetworkMode']=='none'
 assert all(m['Type']=='tmpfs' and m['Destination']=='/tmp' for m in docker.get('Mounts',[])),'Unexpected mount'
 assert spec['root']['readonly'] is True
 probe(label+'-start',manager+['start',cid]);exit_code=int(probe(label+'-wait',manager+['wait',cid]).strip())
 logs=probe(label+'-logs',manager+['logs',cid]);after=json.loads(probe(label+'-inspect-after',manager+['inspect',cid]))[0]
 assert after['State']['Running'] is False and after['State']['ExitCode']==exit_code
 expected=7 if mode=='exit7' else 0;assert exit_code==expected
 marker={'basic':'S2_SMOKE_STARTED','exit7':'S2_EXIT7_STARTED','cli':'S2_CLI_STARTED'}[mode];assert marker in logs
 if mode=='basic':assert '"node":"v22.19.0","uid":1000,"gid":1000' in logs and 'CapEff:\t0000000000000000' in logs and 'NoNewPrivs:\t1' in logs
 if mode=='cli':assert 'codex-cli 0.167.0-alpha.3.2' in logs and 'Usage:' in logs and '/codex' in logs
 after_image=json.loads(probe(label+'-image-after',manager+['image','inspect','--mode=native',a.image]));assert after_image[0]['Image']['Target']['digest']==target
 units[-1].update({'target':target,'config':config_digest,'snapshotParent':snapshot['Parent'],'exitCode':exit_code,'passed':True})
 probe(label+'-remove',manager+['rm',cid]);units[-1]['removed']=True;(out/'units.json').write_text(json.dumps(units,indent=2)+'\n')
assert len(set(u['id'] for u in units))==4
call('containers-final',manager+['ps','-a','--no-trunc'])
(out/'result.json').write_text(json.dumps({'status':'probes-passed-cleanup-pending','identity':identity,'units':units,'trialAuthorized':False,'readyForTrial':False,'results':None,'providerCalls':0,'trialRuns':0},indent=2)+'\n')
print('Four model-free probes passed; VM cleanup still required')
