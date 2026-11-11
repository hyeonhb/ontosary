// Preparation gate only. Never refreeze or replace historical input hashes.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import ts from 'typescript';
import { openEnvironment, contractVersion } from './build/evaluation/evaluate.js';
import { vendure } from './build/vendure-baseline.js';
import { hash, stable } from './build/lib/analysis-session.js';
const root='/environment', repo='/tools/repo', output='/output';
const modules=['submission.js','evaluate.js','behavior.js','execute.js','modal.js','stream.js'];
const evaluatorHashes=Object.fromEntries(modules.map(f=>[f,hash(fs.readFileSync('/tools/build/evaluation/'+f))]));
const result={kind:'linux-environment-preparation',trialAuthorized:false,readyForTrial:false,results:null,versions:{node:process.version,typescript:ts.version,platform:process.platform,arch:process.arch},evaluatorHashes,evaluatorId:hash(stable({contractVersion,evaluatorHashes})),status:'blocked'};
const req=createRequire(root+'/package.json');
result.resolution={typescript:import.meta.resolve('typescript'),rxjs:req.resolve('rxjs')};
result.versions.rxjs=req('rxjs/package.json').version;
try {
 const env=openEnvironment(root,repo); // Original function, before any diagnostic decomposition.
 env.assertUnchanged();result.status='opened';result.baselineTypecheck=env.checked;result.fingerprints=env.fingerprints;result.cost=env.cost;
} catch(error) {
 result.error={name:error.name,message:error.message,stack:error.stack};
 const {spec}=vendure(root,repo);
 result.inputs=[...spec.inputs,...spec.artifacts].map(input=>{
  const relative=path.relative(root,input.file);
  const category=input.file.includes('/typescript/lib/')?'typescript-library':relative.startsWith('packages/common/lib/')?'common-build':relative.startsWith('node_modules/')?'dependency':input.file.startsWith(repo+'/')?'repository-artifact':'source-or-config';
  try {
   const actual=input.symlink!==undefined?fs.readlinkSync(input.file):hash(fs.readFileSync(input.file));
   const expected=input.symlink??input.sha256;
   return {file:input.file,category,expected,actual,status:actual===expected?'matched':'mismatched'};
  } catch(e) {return {file:input.file,category,expected:input.symlink??input.sha256,status:'missing',error:e.code};}
 });
 result.differences=result.inputs.filter(i=>i.status!=='matched');
}
fs.writeFileSync(output+'/open-environment.json',JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({status:result.status,evaluatorId:result.evaluatorId,versions:result.versions,differences:result.differences?.length,error:result.error?.message}));
if(result.status!=='opened')process.exitCode=1;
