// Narrow diagnosis after discovery failed; no model, auth parser or network request.
import fs from 'node:fs';
import {spawnSync} from 'node:child_process';
const env={PATH:'/usr/local/bin:/usr/bin:/bin',HOME:'/home/runner',CODEX_HOME:'/home/runner/cli-state',TMPDIR:'/scratch',LANG:'C.UTF-8'};
const calls=[];
function call(executable,args){const r=spawnSync(executable,args,{env,cwd:'/source',encoding:'utf8',timeout:6000,maxBuffer:1024*1024});const row={executable,args,exitCode:r.status,signal:r.signal,error:r.error?.code??null,stdout:r.stdout,stderr:r.stderr};calls.push(row);return row;}
fs.writeFileSync('/source/parent-write.txt','parent allowed operation\n');
const parent={sourceRead:fs.readFileSync('/source/input.txt','utf8')==='source input\n',sourceWrite:fs.existsSync('/source/parent-write.txt'),materialRead:fs.readFileSync('/materials/input.txt','utf8')==='material input\n',syntheticAuthReadable:fs.readFileSync(env.CODEX_HOME+'/auth.json','utf8').includes('syntheticOnly')};
call('codex',['--strict-config','features','list']);
call('codex',['sandbox','-P','missing-fixture-profile','-C','/source','--','/usr/local/bin/node','-e','process.exit(99)']);
// A successful command must read/write the allowed paths; failure is never a deny pass.
call('codex',['sandbox','-P','fixture','-C','/source','--','/usr/local/bin/node','-e',"const fs=require('fs');if(fs.readFileSync('/source/input.txt','utf8')!=='source input\\n'||fs.readFileSync('/materials/input.txt','utf8')!=='material input\\n')process.exit(3);fs.writeFileSync('/source/native-write.txt','native allowed operation\\n');console.log(JSON.stringify({nativeAllowed:true}));"]);
call('/usr/bin/unshare',['--user','--map-root-user','--','/bin/true']);
const read=p=>{try{return fs.readFileSync(p,'utf8')}catch(e){return {errno:e.code}}};
const result={kind:'preparation-blocker-diagnosis',fixtureOnly:true,validSubmission:false,parent,calls,nonModelCLICalls:3,nativeAllowedWriteExists:fs.existsSync('/source/native-write.txt'),status:read('/proc/self/status'),mountinfo:read('/proc/self/mountinfo'),cgroup:read('/proc/self/cgroup'),routes:read('/proc/net/route'),namespaces:Object.fromEntries(['user','mnt','net','pid','cgroup'].map(k=>[k,fs.readlinkSync('/proc/self/ns/'+k)])),sysctls:Object.fromEntries(['/proc/sys/kernel/unprivileged_userns_clone','/proc/sys/user/max_user_namespaces','/proc/sys/kernel/apparmor_restrict_unprivileged_userns'].map(k=>[k,read(k)])),cliStateEntries:fs.readdirSync(env.CODEX_HOME),credentialTransfers:0,logins:0,refreshes:0,providerRequests:0,modelCalls:0,trialRuns:0,actualTurnTools:'unverified'};
fs.writeFileSync('/output/diagnosis.json',JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({kind:result.kind,nonModelCLICalls:3,parent,nativeAllowedWriteExists:result.nativeAllowedWriteExists}));
