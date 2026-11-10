import { it, expect } from 'vitest';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { proseViews, auditProse } from '../experiments/domain-model/s2/lib/prose.js';
import { Ledger, collectUsage, schedule, refuseTrial } from '../experiments/domain-model/s2/trial/telemetry.js';
import { checkedSnapshot } from '../experiments/domain-model/s2/trial/snapshot-gate.js';
import { tree, snapshot } from '../experiments/domain-model/s2/trial/runtime.js';
import { hash } from '../experiments/domain-model/s2/lib/analysis-session.js';
import { Failure } from '../experiments/domain-model/s2/lib/model.js';
import { observeStream, emptyCompletion } from '../experiments/domain-model/s2/evaluation/stream.js';
const views=new Map(fs.readdirSync('experiments/domain-model/s2/results/2026-11-09-modal-fix/B/views').sort().map(f=>[f.slice(0,-5),JSON.parse(fs.readFileSync('experiments/domain-model/s2/results/2026-11-09-modal-fix/B/views/'+f,'utf8'))]));
it('covers every B leaf bidirectionally without claiming semantic approval',()=>{const p=proseViews(views),r=auditProse(views,p.files,p.units);expect(r.pass).toBe(true);expect(r.views).toBe(68);expect(r.meaningProven).toBe(false);expect(r.humanParityReview).toBe('pending');});
it.each(['negation','direction','approval','evidence','extra-solution','missing-unit','duplicate-unit'])('C drift requires review: %s',kind=>{
    const p=proseViews(views);const file=kind==='evidence'?'C/evidence.md':'C/guide.md';let t=p.files.get(file)!;
    if(kind==='negation')t=t.replace('참여한다','참여하지 않는다');
    if(kind==='direction')t=t.replace('에서 "order"로','에서 "line"으로');
    if(kind==='approval')t=t.replace('pending-review','approved');
    if(kind==='evidence')t=t.replace(/sha256/g,'lost-evidence');
    if(kind==='extra-solution')t+='\n서비스에 guard를 넣으면 정답이다.\n';
    if(kind==='missing-unit')p.units.pop();if(kind==='duplicate-unit')p.units.push(p.units[0]!);
    p.files.set(file,t);expect(auditProse(views,p.files,p.units).pass).toBe(false);
});
it('usage includes cache and reasoning only once; identical events are deduplicated',()=>{const l=new Ledger();const e={id:'x',input:99999,output:5,cachedInput:80000,reasoningOutput:2};l.add(e);l.add(e);expect(l.summary()).toMatchObject({total:100004,overReference:4,hardCap:false,complete:true});l.add({...e,output:6});expect(l.summary().complete).toBe(false);});
it('missing and invalid usage are not zero-cost success',()=>{expect(collectUsage(['{"type":"turn.started"}']).summary().complete).toBe(false);const l=new Ledger();l.add({id:'x',input:1,output:1,cachedInput:2,reasoningOutput:null});expect(l.summary().complete).toBe(false);});
it('assignment balances all conditions in every block and position',()=>{const s=schedule('s2-20261110-v1');expect(s).toEqual(schedule('s2-20261110-v1'));for(const field of ['block','position'] as const)for(const n of [1,2,3])expect(s.filter(x=>x[field]===n).map(x=>x.condition).sort()).toEqual(['A','B','C']);expect(()=>refuseTrial()).toThrow('not authorized');});
it('snapshot preserves additions/deletions and separates auxiliary; never restores baseline',()=>{const root=fs.mkdtempSync(path.join(os.tmpdir(),'s2-snapshot-'));try{const src=path.join(root,'src'),aux=path.join(root,'aux');fs.mkdirSync(src);fs.mkdirSync(aux);fs.writeFileSync(path.join(src,'a.ts'),'one');fs.writeFileSync(path.join(src,'c.ts'),'old');const base=tree(src);fs.writeFileSync(path.join(src,'c.ts'),'new');fs.unlinkSync(path.join(src,'a.ts'));fs.writeFileSync(path.join(src,'b.ts'),'two');fs.writeFileSync(path.join(aux,'note.md'),'notes');const s=snapshot(src,aux,path.join(root,'out'),base);expect(s.delta.map(x=>x.kind)).toEqual(['deleted','added','modified']);expect(Object.keys(s.source)).toEqual(['b.ts','c.ts']);expect(Object.keys(s.auxiliary)).toEqual(['note.md']);fs.symlinkSync('/tmp',path.join(src,'escape'));expect(()=>tree(src)).toThrow('Nonregular');}finally{fs.rmSync(root,{recursive:true,force:true});}});
it.each(['value','never','error','throw'])('invalid service must complete without values/errors: %s',kind=>{const o=observeStream(()=>{if(kind==='throw')throw Error('bad');return {subscribe(s:any){if(kind==='value'){s.next(undefined);s.complete();}if(kind==='error')s.error('bad');}};});expect(emptyCompletion(o)).toBe(false);});
it('empty synchronous completion passes',()=>expect(emptyCompletion(observeStream(()=>({subscribe(s:any){s.complete();}})))).toBe(true));

it('unsupported execution stays unsupported rather than policy failure',()=>{expect(()=>observeStream(()=>{throw new Failure('UnsupportedEvaluation','operator','unreviewed');})).toThrow('unreviewed');expect(()=>observeStream(()=>42)).toThrow('Non-observable');});

it('every correspondence points to the exact rendered line interval',()=>{
    const p=proseViews(views);
    for(const u of p.units)expect(hash(p.files.get(u.C.file)!.split('\n').slice(u.C.startLine-1,u.C.endLine).join('\n'))).toBe(u.C.sha256);
});

it('non-policy calls keep unexpected exceptions and stream errors unsupported',()=>{
    expect(()=>observeStream(()=>{throw Error('valid input failure');},false)).toThrow('valid input failure');
    expect(()=>observeStream(()=>({subscribe(s:any){s.next('response');s.error('later failure');}}),false)).toThrow('Unexpected service stream error');
});

it('snapshot gate rejects omitted production directories without discarding their evidence',()=>{
    const root=fs.mkdtempSync(path.join(os.tmpdir(),'s2-full-snapshot-'));
    try {const src=path.join(root,'src'),aux=path.join(root,'aux');fs.mkdirSync(src);fs.mkdirSync(aux);fs.mkdirSync(path.join(src,'node_modules'));fs.writeFileSync(path.join(src,'node_modules/hidden.ts'),'export const x=1;');const out=path.join(root,'out');snapshot(src,aux,out,{});expect(()=>checkedSnapshot(out)).toThrow('would be omitted');expect(fs.existsSync(path.join(out,'source/node_modules/hidden.ts'))).toBe(true);}finally{fs.rmSync(root,{recursive:true,force:true});}
});
it('snapshot gate accepts all captured source and detects later modification',()=>{
    const root=fs.mkdtempSync(path.join(os.tmpdir(),'s2-frozen-source-'));
    try {const src=path.join(root,'src'),aux=path.join(root,'aux');fs.mkdirSync(src);fs.mkdirSync(aux);fs.writeFileSync(path.join(src,'input.ts'),'export const x=1;');const out=path.join(root,'out');snapshot(src,aux,out,{});expect(checkedSnapshot(out).size).toBe(1);fs.chmodSync(path.join(out,'source/input.ts'),0o644);fs.writeFileSync(path.join(out,'source/input.ts'),'changed');expect(()=>checkedSnapshot(out)).toThrow('integrity mismatch');}finally{fs.rmSync(root,{recursive:true,force:true});}
});
