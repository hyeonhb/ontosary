import { afterEach, expect, it } from 'vitest';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { checkSubmission, deltaSubmission, readSubmission, sourceView, overallStatus } from '../experiments/domain-model/s2/evaluation/submission.js';
import { canonical, compareCalls } from '../experiments/domain-model/s2/evaluation/behavior.js';
import { executor, invoke } from '../experiments/domain-model/s2/evaluation/execute.js';
const dirs:string[]=[];
afterEach(()=>dirs.splice(0).forEach(d=>fs.rmSync(d,{recursive:true,force:true})));
function fixture() {
    const root=fs.mkdtempSync(path.join(os.tmpdir(),'s2-contract-'));dirs.push(root);
    const files={'tsconfig.json':JSON.stringify({compilerOptions:{strict:true,target:'ES2022',moduleResolution:'node',types:[],skipLibCheck:true},files:['caller.ts']}),
        'caller.ts':"import { Submit } from './input'; export const result:string = new Submit().run('x');",
        'input.ts':'export class Submit { run(reason:string):string {return reason;} }'};
    for(const [file,text] of Object.entries(files))fs.writeFileSync(path.join(root,file),text);
    return {root,config:'tsconfig.json',baseline:readSubmission(root)};
}
it('checks original callers rather than reconstructed bodies',()=>{
    const f=fixture();expect(checkSubmission({...f,sources:f.baseline}).status).toBe('passed');
    const r=checkSubmission({...f,sources:deltaSubmission(f.baseline,{'input.ts':'export class Submit {run(reason:string):number {return 42;} }'})});
    expect(r.status).toBe('failed');expect(r.diagnostics.some(d=>d.file==='caller.ts'&&d.code===2322)).toBe(true);
});
it('checks and executes the identical new nested helper snapshot',()=>{
    const f=fixture(),sources=deltaSubmission(f.baseline,{'input.ts':"import {clean} from './new/helper';export class Submit {run(reason:string):string {return clean(reason);}}",'new/helper.ts':'export function clean(s:string):string {return s.trim();}'});
    const r=checkSubmission({...f,sources});expect(r.status).toBe('passed');expect(r.changedFiles.every(f=>f.included)).toBe(true);
    const executed:Record<string,string>={};const e=executor(f.root,[{file:'input.ts',className:'Submit'}],{},f.root,sourceView(sources,(f,h)=>{executed[f]=h;}));
    expect(invoke(e.instance('Submit'),'run',' x ')).toBe('x');
    for(const [file,h] of Object.entries(executed))expect(r.checkedFiles.find(f=>f.file===file)?.sha256).toBe(h);
});
it.each(['type','syntax','missing'])('rejects %s helper before behavior eligibility',kind=>{
    const f=fixture(),delta:Record<string,string>={'input.ts':"import {clean} from './helper';export class Submit {run(s:string):string{return clean(s);}}"};
    if(kind!=='missing')delta['helper.ts']=kind==='type'?'export function clean(s:string):string {return 5;}':'export function clean(s:string):string {return ( ;}';
    const r=checkSubmission({...f,sources:deltaSubmission(f.baseline,delta)});expect(r.status).toBe('failed');expect(r.diagnostics.length).toBeGreaterThan(0);
});
it('does not restore a deleted source from baseline disk',()=>{
    const f=fixture(),r=checkSubmission({...f,sources:deltaSubmission(f.baseline,{'input.ts':null})});
    expect(r.status).not.toBe('passed');expect(r.diagnostics.some(d=>d.code===2307)).toBe(true);expect(r.unsupported.some(d=>d.file==='input.ts')).toBe(true);
    const withEmpty=new Map(f.baseline);withEmpty.set('empty.ts',Buffer.alloc(0));
    const removed=checkSubmission({...f,baseline:withEmpty,sources:f.baseline});
    expect(removed.status).toBe('unsupported');expect(removed.changedFiles.some(f=>f.file==='empty.ts')).toBe(true);
});
it('complete submissions with missing files and unreferenced changes cannot pass',()=>{
    const f=fixture();expect(checkSubmission({...f,sources:new Map([['caller.ts',f.baseline.get('caller.ts')!]])}).status).not.toBe('passed');
    const r=checkSubmission({...f,sources:deltaSubmission(f.baseline,{'unused.ts':'export const x=1;'})});
    expect(r.status).toBe('unsupported');expect(r.changedFiles[0]?.included).toBe(false);
});
it('uses the pinned strict config even when submission tries to relax it',()=>{
    const f=fixture(),r=checkSubmission({...f,sources:deltaSubmission(f.baseline,{'tsconfig.json':JSON.stringify({compilerOptions:{strict:false},files:['caller.ts']}),'input.ts':'export class Submit {run(s:string):string {return undefined;}}'})});
    expect(r.status).toBe('failed');expect(r.diagnostics.some(d=>d.code===2322)).toBe(true);
});
it('does not reuse source files or diagnostics across submissions',()=>{
    const f=fixture();const bad=checkSubmission({...f,sources:deltaSubmission(f.baseline,{'input.ts':'export class Submit {run(s:string):number{return 1;}}'})});
    const good=checkSubmission({...f,sources:f.baseline});expect(bad.status).toBe('failed');expect(good.status).toBe('passed');expect(bad.submissionId).not.toBe(good.submissionId);
});
it('payload comparison ignores key/line order and absent undefined but preserves duplicates and values',()=>{
    const expected=[{kind:'cancel',input:{orderId:'o',lines:[{orderLineId:'a',quantity:2},{orderLineId:'b',quantity:3}]}}];
    expect(compareCalls([{kind:'cancel',input:{unused:undefined,lines:[{quantity:3,orderLineId:'b'},{quantity:2,orderLineId:'a'}],orderId:'o'}}],expected).pass).toBe(true);
    for(const input of [{orderId:'wrong',lines:expected[0]!.input.lines},{orderId:'o',lines:[{orderLineId:'a',quantity:2},{orderLineId:'a',quantity:2}]},{orderId:'o',lines:[{orderLineId:'a',quantity:3},{orderLineId:'b',quantity:3}]}])expect(compareCalls([{kind:'cancel',input}],expected).pass).toBe(false);
    expect(compareCalls([...expected,...expected],expected).pass).toBe(false);
});
it.each(['paymentId','amount','reason','shipping','adjustment'])('compares refund %s',key=>{
    const input={paymentId:'p',amount:75,reason:'  original  ',shipping:0,adjustment:0,lines:[{orderLineId:'l',quantity:3}]};
    expect(compareCalls([{kind:'refund',input:{...input,[key]:'wrong'}}],[{kind:'refund',input}]).pass).toBe(false);
});
it('copied observations preserve call-time payload and call order',()=>{
    const payload={orderId:'o'},calls=[structuredClone({kind:'cancel',input:payload}),{kind:'refund',input:{paymentId:'p'}}];payload.orderId='changed';
    expect((canonical(calls) as typeof calls)[0]!.input.orderId).toBe('o');expect(compareCalls([...calls].reverse(),calls).pass).toBe(false);
});

it('overall rejects incomplete/unsupported checks even when behavior assertions pass',()=>{
    for(const status of ['failed','unsupported','not-run'])expect(overallStatus(status,'passed',true)).not.toBe('passed');
    for(const status of ['failed','unsupported','not-run'])expect(overallStatus('passed',status,true)).not.toBe('passed');
    expect(overallStatus('passed','passed',false)).toBe('failed');
    expect(overallStatus('passed','passed',null)).toBe('failed');
    expect(overallStatus('passed','passed',true)).toBe('passed');
});
it('compares cancellation flags independently of reason and lines',()=>{
    const expected=[{kind:'cancel',input:{orderId:'o',reason:'r',cancelShipping:true}}];
    expect(compareCalls([{kind:'cancel',input:{orderId:'o',reason:'r',cancelShipping:false}}],expected).pass).toBe(false);
});
