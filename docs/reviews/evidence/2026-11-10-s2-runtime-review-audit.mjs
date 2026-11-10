// Independent, model-free audit. Run after pnpm s2:build from the repository root.
// node docs/reviews/evidence/2026-11-10-s2-runtime-review-audit.mjs <new-output.json>
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { gunzipSync } from 'node:zlib';
import { collectUsage } from '../../../work/s2-build/trial/telemetry.js';
import { snapshot } from '../../../work/s2-build/trial/runtime.js';
import { checkedSnapshot } from '../../../work/s2-build/trial/snapshot-gate.js';
import { hash, stable } from '../../../work/s2-build/lib/analysis-session.js';
const out=process.argv[2];
if(!out||fs.existsSync(out))throw Error('New output path required');
const evidence='experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix';
const bundle='experiments/domain-model/s2/results/2026-11-10-trial-preparation';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const fixture={termination:'fixture',reason:'completed',code:0,normalEOF:true,outputTruncated:false,readErrors:[]};
const s={type:'turn.started'},d={type:'turn.completed',usage:{input_tokens:10,output_tokens:2}},f={type:'turn.failed',error:{message:'fixture'}};
const report=(events,end=fixture)=>collectUsage(events.map(e=>JSON.stringify(e)),end).summary();
const languageFailures=[];let languageCases=0;
function enumerate(prefix,n){
  if(prefix.length){
    languageCases++;
    const expected=/^(sd)+$/.test(prefix),events=[...prefix].map(c=>({s,d,f}[c])),r=report(events);
    if(r.complete!==expected||r.total!==(expected?prefix.length/2*12:null))languageFailures.push({prefix,expected,actual:r});
  }
  if(n)for(const c of 'sdf')enumerate(prefix+c,n-1);
}
enumerate('',7);assert.deepEqual(languageFailures,[]);
const a={...d,id:'a'},b={...d,id:'b'},startId={...s,id:'s'};
const cases=[
  ['valid',[s,d],fixture,true,12,12],
  ['unfinished',[s,d,s],fixture,false,null,12],
  ['missing-start',[d],fixture,false,null,null],
  ['duplicate-mask',[s,a,b,s],fixture,false,null,null],
  ['null',[null],fixture,false,null,null],
  ['same-values-distinct-turns',[s,d,s,d],fixture,true,24,24],
  ['same-id-replay',[startId,startId,a,a],fixture,true,12,12],
  ['late-conflict-retracts-old-turn',[s,a,s,b,{...a,usage:{input_tokens:20,output_tokens:2}}],fixture,false,null,12],
  ['active-cross-turn-replay',[s,a,s,a,d],fixture,false,null,null],
  ['ambiguous-no-id-completion',[s,d,d],fixture,false,null,null],
  ['additional-failure-retracts',[s,d,f],fixture,false,null,null],
  ['failed-then-success',[s,f,s,d],fixture,false,null,12],
  ['unknown-event',[s,{type:'item.completed',item:{id:'x'}},d],fixture,true,12,12],
  ['unsupported-concurrency',[s,{...d,turn_id:'x'}],fixture,false,null,null],
  ['invalid-identity-retracts',[s,a,{...a,id:22}],fixture,false,null,null],
  ['unverified-end',[s,d],{...fixture,termination:'unverified'},false,null,12],
  ['timeout',[s,d],{...fixture,reason:'timeout'},false,null,12],
  ['cut-log',[s,d],{...fixture,outputTruncated:true},false,null,12],
  ['error-after-complete',[s,d,{type:'error',message:'fixture'}],fixture,false,null,12],
  ['error-during-active',[s,{type:'error',message:'fixture'},d],fixture,false,null,null],
];
const rows=cases.map(([name,events,end,complete,total,subtotal])=>{
  const actual=report(events,end);
  assert.equal(actual.complete,complete,name);assert.equal(actual.total,total,name);assert.equal(actual.subtotal.total,subtotal,name);
  return {name,raw:events.map(e=>JSON.stringify(e)),end,actual};
});
const recorded=read(path.join(evidence,'accounting-fixtures.json'));
for(const r of recorded.rows)assert.deepEqual(collectUsage(r.raw,r.end).summary(),r.actual,r.name);
const implementation=read(path.join(evidence,'implementation.json'));
let implementationFiles=0;
for(const [p,h] of Object.entries({...implementation.sourceHashes,...implementation.testsHashes})){
  assert.equal(hash(fs.readFileSync(p)),h,p);implementationFiles++;
}
const index=read(path.join(evidence,'runtime-accounting.json'));
for(const e of index.files)assert.equal(hash(fs.readFileSync(path.resolve(evidence,e.path))),e.sha256,e.path);
const {executionId,...manifest}=read(path.join(evidence,'execution/execution-manifest.json'));
assert.equal(hash(stable(manifest)),executionId);
for(const [p,h] of Object.entries(manifest.implementationHashes))assert.equal(hash(fs.readFileSync(path.join('experiments/domain-model/s2',p))),h,p);
assert.equal(manifest.runtimeAccountingBinding.indexHash,hash(fs.readFileSync(path.join(evidence,'runtime-accounting.json'))));
assert.deepEqual(manifest.runtimeAccountingBinding.files,index.files);
assert.equal(manifest.trialAuthorized,false);assert.equal(manifest.readyForTrial,false);assert.equal(manifest.results,null);
assert.equal(manifest.runtimeContract.R11,'unresolved');assert.equal(manifest.assignment.length,9);
assert.ok(manifest.assignment.every(r=>r.status==='not-run'&&r.attempts.length===0));
const distribution=read(path.join(bundle,'bundle-manifest.json'));
for(const e of distribution.files)assert.equal(hash(fs.readFileSync(path.join(bundle,e.file))),e.sha256,e.file);
const preserved=read(path.join(evidence,'preservation-and-reuse.json'));
for(const e of preserved.agentFiles){
  const p=path.join(bundle,e.file);
  assert.equal(hash(fs.readFileSync(p)),e.sha256,p);
  assert.equal(hash(execFileSync('git',['show','ef60bc9:'+p])),e.sha256,p);
}
assert.equal(manifest.bundleId,distribution.bundleId);assert.equal(manifest.baselineId,distribution.baselineId);assert.equal(manifest.modelId,distribution.modelId);
assert.throws(()=>snapshot({collectionAllowed:true}),/R11 unresolved/);
assert.throws(()=>checkedSnapshot('/missing-independent-fixture'),/production evaluation blocked/);
const refusals=[];
for(const args of [['work/s2-build/trial/freeze.js','run'],['work/s2-build/trial/evaluate-snapshot.js','/missing-independent-fixture']]){
  const r=spawnSync(process.execPath,args,{encoding:'utf8'});
  assert.equal(r.status,1);assert.match(r.stderr,/not authorized|production evaluation blocked/);
  refusals.push({args,code:r.status,reason:r.stderr.match(/Error: ([^\n]+)/)?.[1]});
}
const work=path.dirname(out),runtime=read(path.join(work,'runtime-probe.json'));
assert.equal(runtime.rows.length,22);assert.deepEqual(runtime.failures,[]);
for(const r of runtime.rows){
  assert.equal(r.nextCanary,'NONSECRET');assert.ok(r.productionRejected&&r.evaluationRejected&&r.receiptMismatch);
  assert.ok(Object.values(r.readOnly).every(v=>['EPERM','EACCES'].includes(v)));
  assert.equal(r.usage.complete,false);assert.equal(r.usage.total,null);assert.equal(r.run.lifecycle.collectionAllowed,false);
  if(['normal-child','detached','grandchild','open-handle'].includes(r.name)){
    assert.equal(r.lateText,'late');assert.ok(['EPERM','EACCES'].includes(r.crossResult));
  }
}
const normalize=x=>Array.isArray(x)?x.map(normalize):x&&typeof x==='object'?Object.fromEntries(Object.entries(x).filter(([k])=>k!=='wallTimeMs').map(([k,v])=>[k,normalize(v)])):x;
const reference=read(path.join(work,'reference-check/result.json'));
const oldReference=JSON.parse(gunzipSync(fs.readFileSync(path.join(evidence,'reference-calibration.json.gz'))));
assert.deepEqual(normalize(reference),normalize(oldReference));
assert.equal(reference.validTrialSubmission,false);assert.equal(reference.evaluation.overall,'passed');
const delta=JSON.parse(gunzipSync(fs.readFileSync(path.join(work,'calibration/oracle/reference.json.gz'))));
assert.deepEqual(normalize(reference.evaluation.behavior),normalize(delta.behavior));
assert.equal(reference.evaluation.typecheck.submissionId,delta.typecheck.submissionId);
assert.equal(reference.evaluation.sourceBinding,true);
const evaluation=read(path.join(work,'evaluation-reproduction.json'));
assert.equal(evaluation.equivalent,true);assert.equal(evaluation.files,60);
assert.equal(fs.readFileSync(path.join(work,'execution/execution-manifest.json'),'utf8'),fs.readFileSync(path.join(evidence,'execution/execution-manifest.json'),'utf8'));
const output={kind:'independent-synthetic-and-artifact-audit',providerCalls:0,languageCases,languageFailures,additionalCases:rows.length,rows,
  recordedFixturesReplayed:recorded.rows.length,implementationFiles,evidenceFiles:index.files.length,agentFiles:preserved.agentFiles.length,
  executionId,executionManifestVerified:true,executionManifestReproduced:true,productionAndLiveRefusals:refusals,
  runtime:{executions:runtime.rows.length,failures:runtime.failures,lateWrites:runtime.rows.filter(r=>r.lateText==='late').length,allProductionBlocked:true,allWholeTotalsNull:true,allReadOnlyChecksDenied:true},
  reference:{sameAsCommittedExceptWallTimeMs:true,sameAsDeltaBehavior:true,submissionId:delta.typecheck.submissionId,passedCases:delta.behavior.cases.filter(c=>c.status==='passed').length,validTrialSubmission:false},
  calibration:{files:60,equivalent:true,variants:read(path.join(work,'calibration/oracle/summary.json')).summaries.length}};
fs.writeFileSync(out,JSON.stringify(output,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({languageCases,additionalCases:rows.length,recordedFixturesReplayed:recorded.rows.length,implementationFiles,evidenceFiles:index.files.length,agentFiles:preserved.agentFiles.length}));
