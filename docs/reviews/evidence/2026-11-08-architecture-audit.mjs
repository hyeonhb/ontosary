// Read-only audit of existing implementation; writes only to a new output directory.
// pnpm build && node docs/reviews/evidence/2026-11-08-architecture-audit.mjs <prepared-vendure> <new-output>
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import { gunzipSync, gzipSync } from 'node:zlib';
import ts from 'typescript';
import { scan } from '../../../dist/core/analyzer.js';
import { formalConcepts, buildContext } from '../../../dist/core/fca.js';
import { compare } from '../../../dist/core/logic.js';
import { observeRoles, binaryContext, sha } from '../../../experiments/domain-model/v1/observe.mjs';
import { validateModel } from '../../../experiments/domain-model/v1/validate.mjs';
import { checkAnalysisInputs } from '../../../experiments/domain-model/v2/inputs.mjs';
const self=fileURLToPath(import.meta.url), repo=path.resolve(path.dirname(self),'../../..');
const [rootArg,outArg,mode]=process.argv.slice(2), root=fs.realpathSync(rootArg);
const config=path.join(root,'packages/admin-ui/ontosary.scope.json');
const load=p=>JSON.parse(fs.readFileSync(path.join(repo,p),'utf8'));
const timed=fn=>{const start=performance.now(),value=fn();return {ms:performance.now()-start,value};};
const summary=values=>({samples:values,median:[...values].sort((a,b)=>a-b)[Math.floor(values.length/2)]});
if(mode){
 let result;
 if(mode==='core'){
  ts.performance.enable();
  const run=timed(()=>scan(config)), json=JSON.stringify(run.value), ctx=buildContext(run.value);
  const compiler={};ts.performance.forEachMeasure((name,ms)=>compiler[name]=ms);
  result={wallMs:run.ms,compilerMeasuresMs:compiler,files:run.value.files.length,functions:run.value.functions.length,
   diagnostics:run.value.diagnostics.length,context:[ctx.objects.length,ctx.attributes.length],jsonBytes:Buffer.byteLength(json),gzipBytes:gzipSync(json).length,
   references:run.value.functions.reduce((n,f)=>n+f.references.length,0),rssHighWaterKiB:process.resourceUsage().maxRSS};
 }else if(mode==='roles'){
  const spec=load('experiments/domain-model/v1/manifest.json');
  const parsed=ts.parseJsonConfigFileContent(ts.readConfigFile(config,ts.sys.readFile).config,ts.sys,path.dirname(config),{noEmit:true},config);
  const construction=timed(()=>ts.createProgram({rootNames:parsed.fileNames,options:parsed.options,projectReferences:parsed.projectReferences}));
  const diagnostics=timed(()=>ts.getPreEmitDiagnostics(construction.value));
  const roles=timed(()=>observeRoles(construction.value,spec,root,diagnostics.value));
  const binary=timed(()=>binaryContext(roles.value,spec.attributes));
  const fca=timed(()=>formalConcepts(binary.value.context));
  result={programMs:construction.ms,diagnosticsMs:diagnostics.ms,rolesMs:roles.ms,binaryMs:binary.ms,fcaMs:fca.ms,
   diagnostics:diagnostics.value.length,objects:roles.value.objects.length,concepts:fca.value.concepts.length,rssHighWaterKiB:process.resourceUsage().maxRSS};
 }else if(mode==='guard'){
  const run=timed(()=>checkAnalysisInputs(root));result={wallMs:run.ms,result:run.value,rssHighWaterKiB:process.resourceUsage().maxRSS};
 }else throw new Error('Unknown audit mode');
 console.log(JSON.stringify(result));
}else{
 const out=path.resolve(outArg);if(fs.existsSync(out))throw new Error('Preserve previous evidence: output exists');fs.mkdirSync(out,{recursive:true});
 const worker=mode=>JSON.parse(execFileSync(process.execPath,[self,root,out,mode],{cwd:repo,encoding:'utf8'}));
 const results={revision:execFileSync('git',['rev-parse','HEAD'],{cwd:repo,encoding:'utf8'}).trim(),scriptSha256:sha(fs.readFileSync(self)),
  environment:{node:process.version,typescript:ts.version,platform:process.platform,arch:process.arch,cpu:os.cpus()[0].model},
  method:'Serial processes; existing prepared cache; OS cache not flushed; 3 observations, not a performance guarantee. Compiler timers overlap; do not sum/subtract. RSS is per worker, not aggregate V2 parent+child.',v2:[]};
 for(let i=0;i<3;i++){
  const dest=path.join(out,`v2-${i}`);
  const run=timed(()=>execFileSync(process.execPath,['experiments/domain-model/v2/run.mjs',root,dest],{cwd:repo,encoding:'utf8'}));
  results.v2.push({wallMs:run.ms,v1InnerReportedMs:JSON.parse(fs.readFileSync(path.join(dest,'timing.json'),'utf8')).wallTimeMs});
 }
 results.core=[worker('core'),worker('core'),worker('core')];
 results.roles=[worker('roles'),worker('roles'),worker('roles')];
 results.guard=[worker('guard'),worker('guard'),worker('guard')];
 const base=path.join(out,'v2-2'),read=p=>JSON.parse(fs.readFileSync(path.join(base,p),'utf8'));
 const facts=JSON.parse(gunzipSync(fs.readFileSync(path.join(base,'facts.json.gz')))),model=read('model-after.json'),candidates=read('fca.json').candidates;
 let readCalls=0,bytes=0;const fileCounts=new Map();
 const anchors=timed(()=>validateModel(model,facts,candidates,f=>{const text=fs.readFileSync(path.join(root,f),'utf8');readCalls++;bytes+=Buffer.byteLength(text);fileCounts.set(f,(fileCounts.get(f)??0)+1);return text;}));
 results.anchors={wallMs:anchors.ms,valid:anchors.value.valid,readCalls,bytes,uniqueFiles:fileCounts.size,
  uniqueBytes:[...fileCounts.keys()].reduce((n,f)=>n+fs.statSync(path.join(root,f)).size,0),readsPerFile:Object.fromEntries(fileCounts)};
 results.payload={facts: facts.length,evidenceOccurrences:facts.reduce((n,f)=>n+(Array.isArray(f.evidence)?f.evidence.length:1),0),factsJsonBytes:Buffer.byteLength(JSON.stringify(facts)),factsGzipBytes:fs.statSync(path.join(base,'facts.json.gz')).size};
 const make=(g,m,has)=>{const objects=Array.from({length:g},(_,i)=>`o${i}`),attributes=Array.from({length:m},(_,i)=>`a${i}`);return {objects,attributes,incidence:Object.fromEntries(objects.map((o,i)=>[o,attributes.filter((a,j)=>has(i,j))]))};};
 const contexts={s1:read('context.json').context,dense128x64:make(128,64,()=>true),sparse128x64:make(128,64,(i,j)=>((i*73+j*37+i*j*13)%101)<12),contranominal12:make(12,12,(i,j)=>i!==j),contranominal64:make(64,64,(i,j)=>i!==j)};
 results.fca={};
 for(const [name,context]of Object.entries(contexts)){formalConcepts(context);const runs=Array.from({length:3},()=>timed(()=>formalConcepts(context)));results.fca[name]={shape:[context.objects.length,context.attributes.length],...summary(runs.map(r=>r.ms)),concepts:runs[0].value.concepts.length,truncated:runs[0].value.truncated};}
 const variables=Array.from({length:12},(_,i)=>({key:`arg${i}`,sourceName:`x${i}`,domain:['a','b'],declaration:{id:`d${i}`}}));
 const normalization={status:'supported',variables,assumptions:[],logic:variables.map(v=>({op:'eq',variable:v.key,value:'a'})).reduce((left,right)=>({op:'or',left,right}))};
 compare(normalization,normalization,{sameInput:true});const runs=Array.from({length:3},()=>timed(()=>compare(normalization,normalization,{sameInput:true})));
 results.logic={shape:'12 independent binary inputs; identical OR expression',...summary(runs.map(r=>r.ms)),status:runs[0].value.status,assignments:runs[0].value.evaluatedAssignments};
 const prior=path.join(repo,'experiments/domain-model/results/2026-11-08-v2');
 results.reproduction=fs.readdirSync(prior).filter(f=>f!=='timing.json').map(file=>({file,same:fs.readFileSync(path.join(prior,file)).equals(fs.readFileSync(path.join(base,file)))}));
 fs.writeFileSync(path.join(out,'audit.json'),JSON.stringify(results,null,2)+'\n');console.log(JSON.stringify(results,null,2));
}
