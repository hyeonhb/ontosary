import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { canonical, mappings } from '../../../evaluation/behavior.js';
import { openEnvironment } from '../../../evaluation/evaluate.js';
import { executor, type Runtime } from '../../../evaluation/execute.js';
import { readSubmission, checkSubmission, sourceView, overallStatus } from '../../../evaluation/submission.js';
import { hash, stable } from '../../../lib/analysis-session.js';
import { Control, allocation, quantity, type Observe } from './dialogs.js';
import { refresh, type Rx } from './refresh.js';

const [source, rootArg, out, repo, task] = process.argv.slice(2);
if (!source || !rootArg || !out || !repo || !task || !['allocation','quantity','refresh'].includes(task) || fs.existsSync(out))
    throw Error('Expected source, environment, new output, repository and task');
const root = path.resolve(rootArg), version = 's2-complex-v1';
const modules = ['run','dialogs','refresh'].map(n=>'./'+n+'.js').concat(
    ['behavior','execute','submission','modal','evaluate','stream'].map(n=>'../../../evaluation/'+n+'.js'),
    ['../../../vendure-baseline.js','../../../lib/analysis-session.js','../../../lib/model.js']);
const fingerprint = Object.fromEntries(modules.map(n=>[n,hash(fs.readFileSync(fileURLToPath(new URL(n,import.meta.url))))]));
const evaluatorId = hash(stable({version,task,fingerprint}));
try {
    const env = openEnvironment(root,repo), sources = readSubmission(source);
    const checked = checkSubmission({root,config:env.config,baseline:env.baseline,sources,
        allowedChange:f=>f.startsWith('packages/admin-ui/src/') && f.endsWith('.ts')});
    const executed: Record<string,string> = {};
    const view = sourceView(sources,(file, sha)=>{executed[file]=sha;});
    const bindings = {marker:(s:string)=>s, gql:()=>'', ORDER_DETAIL_FRAGMENT:'', _:(s:string)=>s,
        CANCEL_ORDER:'cancel', REFUND_ORDER:'refund', FormControl:Control, Validators:{min:()=>null,max:()=>null},
        summate:(rows:Runtime[],key:string)=>rows.reduce((sum,r)=>sum+Number(r[key]),0)};
    const engine = executor(root,mappings,bindings,root,view);
    const req = createRequire(path.join(root,'package.json')), rx = req('rxjs') as Rx;
    // Both publicly supported RxJS entry points belong to the same runtime, whichever spelling a submission imports.
    req('rxjs/operators');
    const cases: {name:string;group:string;expected:unknown;actual?:unknown;status:string;error?:string}[] = [];
    const observe: Observe = (name,group,expected,fn) => {
        try {
            const actual = canonical(fn());
            const pass = JSON.stringify(actual) === JSON.stringify(canonical(expected));
            cases.push({name,group,expected,actual,status:pass?'passed':'failed'});
        } catch(e) { cases.push({name,group,expected,status:'unsupported',error:String(e)}); }
    };
    const unhandled: string[] = [];
    if (checked.status==='passed') {
        rx.config.onUnhandledError = e=>unhandled.push(String(e));
        if (task==='refresh') refresh(engine,rx,observe);
        else (task==='quantity'?quantity:allocation)(engine,observe);
        await new Promise(resolve=>setTimeout(resolve,15));
    }
    const behavior = checked.status!=='passed'?'not-run':unhandled.length || cases.some(c=>c.status==='unsupported')?'unsupported':
        cases.length && cases.every(c=>c.status==='passed')?'passed':'failed';
    const binding = checked.status==='passed' && Object.keys(executed).length>0 && Object.entries(executed).every(([file,sha])=>
        checked.submittedManifest[file]===sha && checked.checkedFiles.some(f=>f.file===file && f.sha256===sha));
    env.assertUnchanged();
    const runtime = Object.fromEntries(Object.keys(req.cache).filter(f=>f.startsWith(root+path.sep)).sort()
        .map(f=>[path.relative(root,f),hash(fs.readFileSync(f))]));
    const result = {contractVersion:version,task,evaluatorId,fingerprint,inputMode:'complete-root',environmentId:hash(stable(env.fingerprints)),
        runtimeId:hash(stable(runtime)),typecheck:{status:checked.status,submissionId:checked.submissionId,changedFiles:checked.changedFiles,
        diagnostics:checked.diagnostics,unsupported:checked.unsupported,programFiles:checked.cost.programFiles},behavior:{status:behavior,cases,unhandled},
        executed,sourceBinding:binding,overall:overallStatus(checked.status,behavior,binding)};
    fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
} catch(error) {
    fs.writeFileSync(out,JSON.stringify({overall:'environment-error',error:String(error)},null,2)+'\n',{flag:'wx'});
    process.exitCode=1;
}
