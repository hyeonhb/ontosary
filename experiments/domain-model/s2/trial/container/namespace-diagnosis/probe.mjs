// Fixed non-model namespace observation. No attach, auth discovery or network request.
import fs from 'node:fs';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';
const mode=process.argv[2];if(!['baseline','traced'].includes(mode))throw Error('unknown fixed diagnostic unit');
const env={PATH:'/usr/local/bin:/usr/bin:/bin',HOME:'/home/runner',CODEX_HOME:'/home/runner/cli-state',TMPDIR:'/scratch',LANG:'C.UTF-8'};
const native='/usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-arm64/vendor/aarch64-unknown-linux-musl';
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');const calls=[];
function call(file,args,timeout=2000){const start=performance.now();const r=spawnSync(file,args,{env,cwd:'/source',encoding:'utf8',timeout,maxBuffer:1024*1024});const row={file,args,exitCode:r.status,signal:r.signal,error:r.error?.code??null,stdout:r.stdout,stderr:r.stderr,milliseconds:performance.now()-start};calls.push(row);return row;}
fs.writeFileSync('/source/parent.txt','parent write\n');
const parent={read:fs.readFileSync('/source/input.txt','utf8')==='source input\n',write:fs.existsSync('/source/parent.txt'),materialRead:fs.readFileSync('/materials/input.txt','utf8')==='material input\n'};
call('codex',['--version']);call(native+'/codex-resources/bwrap',['--version']);
const args=['sandbox','-P','fixture','-C','/source','--','/usr/local/bin/node','-e',"const fs=require('fs');fs.readFileSync('/source/input.txt');fs.readFileSync('/materials/input.txt');fs.writeFileSync('/source/native.txt','started');console.log('NATIVE_PAYLOAD_STARTED');"];
if(mode==='baseline')call('codex',args,5000);
else {call('/usr/bin/strace',['--version']);call('/usr/bin/strace',['-f','-s','128','-e','trace=clone,clone3,unshare,setns,execve,wait4,exit_group','--','/usr/local/bin/codex',...args],5000);}
const read=p=>{try{return fs.readFileSync(p,'utf8')}catch(e){return {errno:e.code}}};
const result={mode,fixtureOnly:true,validSubmission:false,parent,calls,nonModelCLICalls:2,nativePayloadStarted:fs.existsSync('/source/native.txt'),nodeVersion:process.version,binaries:{codex:{path:native+'/bin/codex',sha256:sha(native+'/bin/codex')},bwrap:{path:native+'/codex-resources/bwrap',sha256:sha(native+'/codex-resources/bwrap')}},procStatus:read('/proc/self/status'),mountinfo:read('/proc/self/mountinfo'),cgroup:read('/proc/self/cgroup'),apparmor:read('/proc/self/attr/current'),sysctls:Object.fromEntries(['/proc/sys/kernel/unprivileged_userns_clone','/proc/sys/user/max_user_namespaces','/proc/sys/kernel/apparmor_restrict_unprivileged_userns'].map(p=>[p,read(p)])),credentialTransfers:0,logins:0,refreshes:0,providerRequests:0,modelCalls:0,trialRuns:0};
if(mode==='traced'){result.strace={sha256:sha('/usr/bin/strace'),package:read('/opt/namespace-package.txt'),license:read('/usr/share/doc/strace/copyright')};}
fs.writeFileSync('/output/result.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({mode,parent,nativePayloadStarted:result.nativePayloadStarted,nonModelCLICalls:2}));
