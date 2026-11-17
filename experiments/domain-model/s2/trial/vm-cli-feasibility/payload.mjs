throw new Error("unexecuted draft: preparation gate missed; payload disabled");
// Only synthetic, local operations; no provider endpoint or real credential.
import fs from 'node:fs';
import net from 'node:net';
import {spawn} from 'node:child_process';
const p=JSON.parse(process.argv[2]);
const read=path=>{try{fs.readFileSync(path);return {accessible:true};}catch(e){return {accessible:false,errno:e.code};}};
const write=path=>{try{fs.writeFileSync(path,'synthetic write\n');return {accessible:true};}catch(e){return {accessible:false,errno:e.code};}};
const connect=options=>new Promise(resolve=>{const s=net.createConnection(options);let done=false;const end=r=>{if(done)return;done=true;s.destroy();resolve(r);};s.once('connect',()=>end({accessible:true}));s.once('error',e=>end({accessible:false,errno:e.code}));s.setTimeout(700,()=>end({accessible:false,errno:'TIMEOUT'}));});
const result={kind:'actual-cli-sandbox-payload',pid:process.pid,ppid:process.ppid,uid:process.getuid(),gid:process.getgid(),nodeVersion:process.version,started:true,mode:p.mode,
 environmentKeys:Object.keys(process.env).sort(),status:fs.readFileSync('/proc/self/status','utf8'),cgroup:fs.readFileSync('/proc/self/cgroup','utf8'),positive:{},denied:{},fixtureOnly:true,validSubmission:false};
result.positive.sourceRead=read(p.source+'/input.txt').accessible;
result.positive.sourceWrite=write(p.source+'/native.txt').accessible;
result.positive.materialRead=read(p.materials+'/input.txt').accessible;
result.positive.scratchWrite=write(p.scratch+'/native.txt').accessible;
result.positive.homeWrite=write(p.home+'/native.txt').accessible;
for(const [id,path] of Object.entries(p.readTargets))result.denied[id]=read(path);
result.denied.materialWrite=write(p.materials+'/input.txt');
result.denied.outsideWrite=write(p.outside+'/attempt.txt');
result.denied.fakeEnvironment={accessible:Object.hasOwn(process.env,'S2_FAKE_AUTH')};
result.denied.inheritedFd=read('/proc/self/fd/'+p.fd);
for(const [id,options] of Object.entries(p.servers))result.denied[id]=await connect(options);
result.completed=true;
fs.writeFileSync(p.source+'/payload.json',JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({kind:result.kind,started:true,completed:true}));
if(p.mode==='timeout'||p.mode==='wrapper-death'){
 const child=spawn(process.execPath,['-e',`const {spawn}=require('child_process');const p=spawn(process.execPath,['-e',${JSON.stringify("setTimeout(()=>require('fs').writeFileSync("+JSON.stringify(p.source+'/late.txt')+",'late'),20000)")}],{detached:true,stdio:'ignore'});p.unref();`],{detached:true,stdio:'ignore'});child.unref();
 fs.writeFileSync(p.source+'/late-ready.json',JSON.stringify({pid:process.pid,childPid:child.pid,lateAfterMs:20000}));
 await new Promise(resolve=>setTimeout(resolve,60000));
}
