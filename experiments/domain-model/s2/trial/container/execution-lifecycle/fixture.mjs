// Synthetic fixture only. No provider, authentication or model calls.
import fs from 'node:fs';
import {spawn} from 'node:child_process';
import crypto from 'node:crypto';
const mode=process.argv[2];
const at=()=>({utc:new Date().toISOString(),monoNs:process.hrtime.bigint().toString()});
if(mode==='writer') {
  fs.writeFileSync('/output/child-ready.json',JSON.stringify({pid:process.pid,...at()}));
  setInterval(()=>fs.appendFileSync('/output/writes.jsonl',JSON.stringify(at())+'\n'),50);
  setTimeout(()=>fs.writeFileSync('/source/late-write.txt','late'),20000);
} else {
  const deniedRead=p=>{try{fs.readFileSync(p);return false}catch(e){return ['ENOENT','EACCES','EPERM'].includes(e.code)}};
  const deniedWrite=p=>{try{fs.writeFileSync(p,'forbidden');return false}catch(e){return ['ENOENT','EACCES','EPERM','EROFS'].includes(e.code)}};
  const positive={source:fs.readFileSync('/source/input.txt','utf8')==='source input\n',materials:fs.readFileSync('/materials/input.txt','utf8')==='material input\n'};
  for(const p of ['/source/new.txt','/output/new.txt','/home/worker/new.txt','/home/runner/cli-state/new.txt','/scratch/new.txt'])fs.writeFileSync(p,'own-write');
  const isolation={managerRead:deniedRead('/opt/ontosary-fixture/gate.json'),managerWrite:deniedWrite('/opt/ontosary-fixture/gate.json'),hostStoreRead:deniedRead('/Users/hyeon/Library/Caches/ontosary/s2-prepared-v1/.lock'),materialWrite:deniedWrite('/materials/input.txt'),rootWrite:deniedWrite('/root/forbidden'),runtimeRead:deniedRead('/run/containerd/containerd.sock'),priorSource:deniedRead('/source/prior-canary'),priorHome:deniedRead('/home/worker/prior-canary'),priorCli:deniedRead('/home/runner/cli-state/prior-canary'),priorScratch:deniedRead('/scratch/prior-canary')};
  for(const p of ['/source','/home/worker','/home/runner/cli-state','/scratch'])fs.writeFileSync(p+'/prior-canary',mode);
  const priorPaths=JSON.parse(fs.readFileSync('/source/prior-paths.json','utf8'));isolation.priorAbsolutePaths=priorPaths.every(deniedRead);
  const native='/usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-arm64/vendor/aarch64-unknown-linux-musl';const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
  const result={mode,positive,isolation,priorPathCount:priorPaths.length,nodeVersion:process.version,binaries:{codex:sha(native+'/bin/codex'),bwrap:sha(native+'/codex-resources/bwrap')},uid:process.getuid(),gid:process.getgid(),status:fs.readFileSync('/proc/self/status','utf8'),cgroup:fs.readFileSync('/proc/self/cgroup','utf8'),apparmor:fs.readFileSync('/proc/self/attr/current','utf8'),...at()};
  fs.writeFileSync('/output/fixture-observations.json',JSON.stringify(result));
  if(!Object.values(positive).every(Boolean)||!Object.values(isolation).every(Boolean))process.exit(3);
  if(['timeout','wrapper-death','supervisor-death'].includes(mode)){
    const child=spawn(process.execPath,['/probe/fixture.mjs','writer'],{detached:true,stdio:'ignore'});child.unref();
    const timer=setInterval(()=>{if(fs.existsSync('/output/child-ready.json')){clearInterval(timer);fs.writeFileSync('/output/ready.json',JSON.stringify({pid:process.pid,child:child.pid,...at()}));}},20);
    setInterval(()=>{},1000);
  } else fs.writeFileSync('/output/ready.json',JSON.stringify({pid:process.pid,...at()}));
}
