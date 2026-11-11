// Fixed PID1 calibration entrypoint. Output existence never authorizes collection.
import fs from 'node:fs';import {spawn} from 'node:child_process';
import {openEnvironment,evaluateSubmission} from './build/evaluation/evaluate.js';
import {readSubmission,deltaSubmission,manifest} from './build/evaluation/submission.js';
import {publicCheck} from './build/trial/public-check.js';
import {hash,stable} from './build/lib/analysis-session.js';
const [name,inputMode,publicFlag]=process.argv.slice(2);
if(!['baseline','reference','helper-type-error','wrong-modal-order','timeout','control'].includes(name)||!['complete-root','explicit-baseline-delta'].includes(inputMode)||!['public','private'].includes(publicFlag))throw Error('Unknown fixed calibration job');
if(process.pid!==1)throw Error('Evaluation entrypoint must be PID1');
const out=(name,value)=>fs.writeFileSync('/output/'+name+'.json',JSON.stringify(value,null,2)+'\n');
const readonly={};
for(const [key,file] of Object.entries({environment:'/environment/package.json',source:'/source/package.json',tools:'/tools/readonly-proof.txt'})) {
 try {const fd=fs.openSync(file,'r+');fs.closeSync(fd);throw Error('Read-only input opened writable: '+key);}catch(e){if(e.code!=='EROFS')throw e;readonly[key]=e.code;}
}
const audit={kind:'known-submission-calibration',fixtureOnly:true,validSubmission:false,trialAuthorized:false,readyForTrial:false,results:null,pid:process.pid,uid:process.getuid(),gid:process.getgid(),readonly,mountinfo:fs.readFileSync('/proc/self/mountinfo','utf8'),status:fs.readFileSync('/proc/self/status','utf8'),cgroup:fs.readFileSync('/proc/self/cgroup','utf8'),node:process.version,name,inputMode};
out('audit',audit);
if(name==='timeout'||name==='control') {
 const writer=spawn(process.execPath,['-e',"setTimeout(()=>{require('node:fs').writeFileSync('/output/late-writer.txt','finite delayed writer\\n')},5000)"],{detached:true,stdio:'ignore'});
 out('writer',{pid:writer.pid,delayMs:5000,started:performance.now()});
 await new Promise(resolve=>setTimeout(resolve,6500));
 out('control',{wrote:fs.existsSync('/output/late-writer.txt')});
} else {
 const env=openEnvironment('/environment','/tools/repo');
 const input=JSON.parse(fs.readFileSync('/input.json','utf8'));
 const sources=inputMode==='complete-root'?readSubmission('/source'):deltaSubmission(env.baseline,input.delta);
 if(hash(stable(manifest(sources)))!==input.submissionId)throw Error('Manager submission identity mismatch');
 const report=await evaluateSubmission(env,sources,inputMode);out('evaluation',report);
 if(publicFlag==='public')out('public',publicCheck('/source','/environment',manifest(env.baseline)));
 env.assertUnchanged();out('unchanged',{fingerprints:hash(stable(env.fingerprints)),submissionId:report.typecheck.submissionId});
}
