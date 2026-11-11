// Finite local CLI discovery only: no exec/turn/login/status/provider commands.
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';
const out='/output';const env={PATH:'/usr/local/bin:/usr/bin:/bin',HOME:'/home/runner',CODEX_HOME:'/home/runner/cli-state',TMPDIR:'/scratch',LANG:'C.UTF-8'};
const calls=[];
for(const args of [['--version'],['--help'],['sandbox','--help'],['sandbox','linux','--help'],['debug','--help'],['features','--help'],['features','list']]) {
 const start=performance.now();const r=spawnSync('codex',args,{env,cwd:'/source',encoding:'utf8',timeout:6000,maxBuffer:1024*1024});calls.push({args,exitCode:r.status,signal:r.signal,error:r.error?.code??null,stdout:r.stdout,stderr:r.stderr,milliseconds:performance.now()-start});
}
const sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const launcher=fs.realpathSync('/usr/local/bin/codex');const binaries=[];
function walk(dir,depth=0){if(depth>9)return;for(const e of fs.readdirSync(dir,{withFileTypes:true})){const f=path.join(dir,e.name);if(e.isDirectory())walk(f,depth+1);else if(e.isFile()&&['codex','bwrap','codex-linux-sandbox'].includes(e.name))binaries.push({file:f,bytes:fs.statSync(f).size,sha256:sha(f),mode:fs.statSync(f).mode});}}
walk('/usr/local/lib/node_modules/@openai');
const files=[];function metadata(dir,depth=0){if(depth>6)return;for(const e of fs.readdirSync(dir,{withFileTypes:true})){const f=path.join(dir,e.name);const s=fs.lstatSync(f);files.push({path:path.relative(env.CODEX_HOME,f),mode:s.mode,bytes:s.size,symlink:e.isSymbolicLink()});if(e.isDirectory())metadata(f,depth+1);}}
metadata(env.CODEX_HOME);
const result={kind:'non-model-cli-discovery',fixtureOnly:true,validSubmission:false,versions:{node:process.version},uid:process.getuid(),gid:process.getgid(),pid:process.pid,allowlistedEnvironmentKeys:Object.keys(env),calls,nonModelCLICalls:calls.length,launcher:{path:launcher,sha256:sha(launcher)},binaries,cliHomeMetadata:files,procStatus:fs.readFileSync('/proc/self/status','utf8'),mountinfo:fs.readFileSync('/proc/self/mountinfo','utf8'),routes:fs.readFileSync('/proc/net/route','utf8'),credentialTransfers:0,logins:0,refreshes:0,providerRequests:0,modelCalls:0,trialRuns:0,actualTurnTools:'unverified'};
fs.writeFileSync(out+'/discovery.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({nonModelCLICalls:calls.length,status:'discovery-recorded',version:calls[0].stdout}));
