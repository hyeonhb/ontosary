import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { performance } from 'node:perf_hooks';
import ts from 'typescript';
import { vendure, json } from '../vendure-baseline.js';
import { hash, stable } from '../lib/analysis-session.js';
import { array, object, string, Failure } from '../lib/model.js';
import { Sources, checkSubmission, overallStatus } from './submission.js';
import { evaluateBehavior, mappings } from './behavior.js';
export const contractVersion = 's2-evaluation-v2-cancel-only';
export function openEnvironment(root: string, repo: string) {
    const start=performance.now(), {spec}=vendure(root,repo);
    const fingerprints: Record<string,string>={};
    for(const i of [...spec.inputs,...spec.artifacts]) {
        if(i.symlink!==undefined) { if(fs.readlinkSync(i.file)!==i.symlink) throw new Failure('Environment',i.file,'Symlink changed'); continue; }
        const digest=hash(fs.readFileSync(i.file));
        if(i.sha256&&digest!==i.sha256) throw new Failure('Environment',path.relative(root,i.file),'Pinned input differs');
        fingerprints[i.file.startsWith(root+path.sep)?path.relative(root,i.file):i.file.includes('/typescript/lib/')?'<typescript>/'+path.basename(i.file):'<repository>/'+path.relative(repo,i.file)]=digest;
    }
    const inventory=array(json(path.join(repo,'experiments/public-app/results/2026-11-08/vendure/inventory.json.gz')),'inventory');
    const baseline=new Map<string,Buffer>();
    for(const entry of inventory) {const f=string(object(entry,'inventory').path,'path');baseline.set(f,fs.readFileSync(path.join(root,f)));}
    const config=path.relative(root,spec.config);
    const checked=checkSubmission({root,config,baseline,sources:baseline});
    if(checked.status!=='passed') throw new Failure('Environment','baseline','Baseline type check failed');
    // Runtime and submission compilation may consume only this pinned, unchanged environment.
    function assertUnchanged() {
        for(const i of [...spec.inputs,...spec.artifacts]) if(i.sha256&&hash(fs.readFileSync(i.file))!==i.sha256) throw new Failure('Environment',i.file,'Environment changed during evaluation');
    }
    return {root,config,baseline,checked,fingerprints,assertUnchanged,cost:{wallTimeMs:performance.now()-start,programs:1,programFiles:checked.cost.programFiles}};
}
export type Environment=ReturnType<typeof openEnvironment>;
export async function evaluateSubmission(env: Environment,sources:Sources,inputMode:'complete-root'|'explicit-baseline-delta') {
    const typecheck=checkSubmission({root:env.root,config:env.config,baseline:env.baseline,sources,allowedChange:f=>f.startsWith('packages/admin-ui/src/')&&f.endsWith('.ts')});
    const behavior=typecheck.status==='passed'?await evaluateBehavior(env.root,sources):{status:'not-run',reason:'Submission typecheck '+typecheck.status,cases:[],executedFiles:{},cost:{wallTimeMs:0}};
    const sourceBinding=behavior.status==='not-run'?null:Object.entries(behavior.executedFiles).every(([file,h])=>typecheck.submittedManifest[file]===h&&typecheck.checkedFiles.some(f=>f.file===file&&f.sha256===h));
    const recheckStart=performance.now();
    env.assertUnchanged();
    const environmentRecheck={wallTimeMs:performance.now()-recheckStart};
    const moduleFiles=['submission.js','evaluate.js','behavior.js','execute.js'];
    const evaluatorHashes=Object.fromEntries(moduleFiles.map(f=>[f,hash(fs.readFileSync(fileURLToPath(new URL(f,import.meta.url))))]));
    return {contractVersion,evaluatorId:hash(stable({contractVersion,evaluatorHashes})),evaluatorHashes,inputMode,
        environment:{id:hash(stable(env.fingerprints)),inputHashes:env.fingerprints,baselineTypecheck:{status:env.checked.status,diagnostics:env.checked.diagnostics,programFiles:env.checked.cost.programFiles},cost:env.cost},
        environmentRecheck,typecheck,behavior,sourceBinding,overall:overallStatus(typecheck.status,behavior.status,sourceBinding),
        sourceMapping:mappings.map(m=>{const bytes=sources.get(m.file),text=bytes?.toString('utf8')??'',sf=ts.createSourceFile(m.file,text,ts.ScriptTarget.Latest,true),cls=sf.statements.find((n):n is ts.ClassDeclaration=>ts.isClassDeclaration(n)&&n.name?.text===m.className);return {...m,submittedHash:bytes?hash(bytes):null,baselineHash:hash(env.baseline.get(m.file)!),methods:cls?.members.filter(n=>ts.isMethodDeclaration(n)||ts.isGetAccessorDeclaration(n)).map(n=>({name:n.name?.getText(sf),offset:n.getStart(sf),end:n.getEnd(),line:sf.getLineAndCharacterOfPosition(n.getStart(sf)).line+1,anchor:n.getText(sf).split('\n')[0]}))};}),
        policy:'Draft (a): suppress invalid cancellation and chained refund; preserve refund-only and refund reasons. Human fidelity/policy review pending.',readyForTrial:false};
}
