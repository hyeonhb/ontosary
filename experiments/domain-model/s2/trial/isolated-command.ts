import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { createRequire } from 'node:module';
import { configuration, runTool, Layout } from './runtime.js';
// Evaluator-only, known calibration inputs. No model dispatch or broad host-home read capability.
const [codex,repoArg,cacheArg,outArg,...command]=process.argv.slice(2);
if(!codex||!repoArg||!cacheArg||!outArg||!command.length)throw Error('Usage: isolated-command <codex> <repo> <cache> <new-dir> <node-script> [args]');
const entries=['work/s2-build/evaluation/oracle-check.js','work/s2-build/trial/evaluate-calibration-snapshot.js','work/s2-build/trial/evaluate-snapshot.js'];
if(!entries.includes(command[0]!.replaceAll('\\','/')))throw Error('Only explicit private calibration or refusal entries are allowed');
const repo=fs.realpathSync(repoArg),cache=fs.realpathSync(cacheArg),out=path.resolve(outArg);
if(fs.existsSync(out))throw Error('Output exists');fs.mkdirSync(out,{recursive:true});
const control=fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(),'s2-evaluator-'))),privateRepo=path.join(control,'repository'),results=path.join(control,'results'),node=path.join(control,'node');
const copied=[
    'work/s2-build','experiments/domain-model/s2/provenance.json','experiments/domain-model/v1/manifest.json',
    'experiments/domain-model/results/2026-11-08-v2','experiments/public-app/results/2026-11-08/vendure/inventory.json.gz',
    'experiments/public-app/results/2026-11-08-prepared/program-path-audit.json.gz','experiments/public-app/results/2026-11-08-prepared/scoped/scan.json.gz',
    'experiments/public-app/v1/vendure-task.json','experiments/domain-model/s2/verification/2026-11-08/reference-patches.json.gz',
];
for(const relative of copied){const dest=path.join(privateRepo,relative);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.cpSync(path.join(repo,relative),dest,{recursive:true});}
fs.writeFileSync(path.join(privateRepo,'package.json'),'{"type":"module"}\n');
const require=createRequire(import.meta.url),tsRoot=path.dirname(require.resolve('typescript/package.json'));
fs.mkdirSync(path.join(privateRepo,'node_modules'),{recursive:true});fs.cpSync(tsRoot,path.join(privateRepo,'node_modules/typescript'),{recursive:true});
fs.copyFileSync(fs.realpathSync(process.execPath),node);fs.chmodSync(node,0o555);fs.mkdirSync(results);
const args=command.map((arg,i)=>{
    const full=path.resolve(repo,arg);
    if(full===out||full.startsWith(out+path.sep))return path.join(results,path.relative(out,full));
    if(i===0)return path.join(privateRepo,path.relative(repo,full));
    if(full===cache)return cache;
    if(fs.existsSync(full)&&fs.statSync(full).isDirectory()) {
        const target=path.join(control,'input-'+i);fs.cpSync(full,target,{recursive:true});return target;
    }
    return arg;
});
const inputs=args.filter(a=>a.startsWith(control+'/input-'));
const l:Layout={root:results,source:privateRepo,sourceReadOnly:true,materials:privateRepo,auxiliary:path.join(results,'auxiliary'),scratch:results,home:path.join(control,'home'),control,readOnly:[cache,node,...inputs],denied:['/Users',repo,path.join(control,'config.toml')]};
fs.mkdirSync(l.home);fs.mkdirSync(l.auxiliary);fs.writeFileSync(path.join(control,'config.toml'),configuration(l));
try {
    const denied=await runTool(codex,l,[node,'-e',`try{require('node:fs').readFileSync(${JSON.stringify(path.join(repo,'package.json'))});console.log('READ');}catch(e){console.log(e.code);}`],5000);
    if(!['EPERM','EACCES'].includes(denied.stdout.trim()))throw Error('Evaluator host package.json read not denied');
    const r=await runTool(codex,l,[node,...args],1800000);
    const clean=(s:string)=>s.split(repo).join('<repository>').split(cache).join('<cache>').split(control).join('<control>');
    fs.cpSync(results,out,{recursive:true});
    fs.writeFileSync(path.join(out,'execution.json'),JSON.stringify({...r,stdout:clean(r.stdout),stderr:clean(r.stderr),profile:clean(configuration(l)),hostPackageReadDenied:true,copiedEvaluatorPaths:copied,validTrialSubmission:false,scope:'Known calibration/complete-root in copied read-only evaluator, explicit host-home deny, network denied; detached process gate remains open'},null,2)+'\n');
    console.log(JSON.stringify({code:r.code,reason:r.reason,output:out,stderr:clean(r.stderr).slice(0,1000)}));process.exitCode=r.code===0?0:1;
}finally{fs.rmSync(control,{recursive:true,force:true});}
