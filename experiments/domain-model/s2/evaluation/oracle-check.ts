import fs from 'node:fs';
import path from 'node:path';
import { gzipSync } from 'node:zlib';
import { performance } from 'node:perf_hooks';
import { hash, stable } from '../lib/analysis-session.js';
import { openEnvironment, evaluateSubmission, contractVersion } from './evaluate.js';
import { deltaSubmission } from './submission.js';
import { variants, variantDelta } from './variants.js';
const [rootArg,outArg,filter]=process.argv.slice(2);
if(!rootArg||!outArg)throw Error('Usage: oracle-check <prepared-root> <new-evidence-dir> [comma-separated-variants]');
const root=fs.realpathSync(rootArg),out=path.resolve(outArg),repo=process.cwd();
if(fs.existsSync(out))throw Error('Output exists');
fs.mkdirSync(out,{recursive:true});
const start=performance.now(),env=openEnvironment(root,repo),summaries:unknown[]=[];
const selected=filter?filter.split(','):variants;
for(const name of selected) {
    if(!variants.includes(name))throw Error('Unknown variant: '+name);
    const delta=variantDelta(name,env.baseline,repo),sources=deltaSubmission(env.baseline,delta);
    const result=await evaluateSubmission(env,sources,'explicit-baseline-delta');
    fs.writeFileSync(path.join(out,name+'.json.gz'),gzipSync(JSON.stringify(result,null,2)+'\n'));
    fs.writeFileSync(path.join(out,name+'-patches.json.gz'),gzipSync(JSON.stringify(Object.entries(delta).map(([file,after])=>({file,baselineHash:env.baseline.has(file)?hash(env.baseline.get(file)!):null,submittedHash:after===null?null:hash(after),before:env.baseline.get(file)?.toString('utf8')??null,after})),null,2)+'\n'));
    const cases=result.behavior.cases;
    const summary={variant:name,typecheck:result.typecheck.status,diagnostics:result.typecheck.diagnostics.map(d=>d.code),behavior:result.behavior.status,overall:result.overall,
        preservation:result.behavior.status==='not-run'?null:cases.filter(c=>c.category==='preservation'&&c.status==='passed').length,preservationTotal:result.behavior.status==='not-run'?null:cases.filter(c=>c.category==='preservation').length,
        draft:result.behavior.status==='not-run'?null:cases.filter(c=>c.category==='draft-requirement'&&c.status==='passed').length,draftTotal:result.behavior.status==='not-run'?null:cases.filter(c=>c.category==='draft-requirement').length,
        failedCases:cases.filter(c=>c.status!=='passed').map(c=>({name:c.name,status:c.status})),submissionId:result.typecheck.submissionId,programFiles:result.typecheck.cost.programFiles,sourceBinding:result.sourceBinding};
    summaries.push(summary);console.log(JSON.stringify(summary));
    if(['reference','helper'].includes(name)&&result.overall!=='passed')throw Error('Valid reference/alternative rejected: '+name);
    if(name==='baseline'&&(result.typecheck.status!=='passed'||summary.preservation!==summary.preservationTotal||summary.draft===summary.draftTotal))throw Error('Baseline calibration failed');
    if(['historical-reference','helper-type-error','helper-syntax-error','missing-helper','deleted-module','out-of-scope'].includes(name)) {
        if(result.typecheck.status==='passed'||result.behavior.status!=='not-run'||result.overall==='passed')throw Error('Invalid submission accepted: '+name);
    } else if(!['reference','helper','baseline'].includes(name)) {
        if(result.typecheck.status!=='passed'||result.behavior.status!=='failed'||!summary.failedCases.length)throw Error('Behavior mutant not independently detected: '+name);
    }
}
env.assertUnchanged();
fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify({contractVersion,baselineEnvironment:env.cost,wallTimeMs:performance.now()-start,summaries,readyForTrial:false},null,2)+'\n');
// Timing is the only exclusion. Paths are normalized by the producer, diagnostics/calls/hashes are retained.
function normalized(value:unknown):unknown {
    if(Array.isArray(value))return value.map(normalized);
    if(value&&typeof value==='object')return Object.fromEntries(Object.entries(value).filter(([k])=>k!=='wallTimeMs').map(([k,v])=>[k,normalized(v)]));
    return value;
}
fs.writeFileSync(path.join(out,'decisions.json'),stable(normalized(JSON.parse(fs.readFileSync(path.join(out,'summary.json'),'utf8'))))+'\n');
