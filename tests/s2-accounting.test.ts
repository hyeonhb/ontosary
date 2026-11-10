import { it, expect } from 'vitest';
import { collectUsage, UsageLedger, LogEnd } from '../experiments/domain-model/s2/trial/telemetry.js';
import { snapshot, collectDiagnostic, Layout, RunResult } from '../experiments/domain-model/s2/trial/runtime.js';
import { checkedSnapshot } from '../experiments/domain-model/s2/trial/snapshot-gate.js';
const end:LogEnd={termination:'fixture',reason:'completed',code:0,normalEOF:true,outputTruncated:false,readErrors:[]};
const start={type:'turn.started'};
const done=(id?:string,input=10,output=2)=>({type:'turn.completed',...(id?{id}:{}),usage:{input_tokens:input,output_tokens:output,cached_input_tokens:5,reasoning_output_tokens:1}});
const report=(events:unknown[],e:LogEnd=end)=>collectUsage(events.map(x=>JSON.stringify(x)),e).summary();
it.each([
 ['normal',[start,done()],true,12],['unfinished second',[start,done(),start],false,null],
 ['missing start',[done()],false,null],['two IDs mask unfinished',[start,done('a'),done('b'),start],false,null],['null',[null],false,null],
] as const)('review regression: %s',(_name,events,complete,total)=>expect(report([...events])).toMatchObject({complete,total}));
it('retracts contradictory turn instead of reporting doubled lower bound',()=>{const r=report([start,done('a'),done('b'),start]);expect(r.subtotal.total).toBeNull();expect(r.consumptionLowerBound).toBeNull();expect(r.turns[0]?.valid).toBe(false);});
it('counts equal numbers from distinct sequential turns',()=>expect(report([start,done(),start,done()])).toMatchObject({complete:true,total:24,subtotal:{turns:[1,2]}}));
it('deduplicates a stream identity within the same turn',()=>{const s={...start,id:'start'};expect(report([s,s,done('done'),done('done')])).toMatchObject({complete:true,total:12});});
it('conflicting replay retracts the original completed value',()=>{const r=report([start,done('a'),done('a',20)]);expect(r).toMatchObject({complete:false,total:null,subtotal:{total:null}});expect(r.rows.at(-1)?.line).toBe(3);});
it('does not treat replay ID as identity of a new active turn',()=>expect(report([start,done('a'),start,done('a')])).toMatchObject({complete:false,total:null,subtotal:{total:null}}));
it('ambiguous ID-less repeated completion is not silently added or deduplicated',()=>expect(report([start,done(),done()])).toMatchObject({complete:false,total:null,subtotal:{total:null}}));
it.each([
 [start,start,done()], [start,{type:'turn.failed',error:{message:'fixture'}}], [start,{type:'turn.completed'}],
 [start,{type:'error',message:'fixture'}], [start,{type:'turn.failed',error:null}],
 [start,{...done(),turn_id:'unsupported'}], [start,{...done(),id:22}],
])('rejects invalid lifecycle %#',(...events)=>expect(report(events).complete).toBe(false));
it.each([null,[],5,'text',{}, {type:0}].map(value=>[value]))('records structure errors without throwing %#',event=>{const r=report([event]);expect(r.total).toBeNull();expect(r.issues.some(i=>i.code==='invalid-event-structure')).toBe(true);});
it.each([-1,1.2,Number.MAX_SAFE_INTEGER+1,null,'10'])('rejects invalid usage number %#',value=>expect(report([start,{type:'turn.completed',usage:{input_tokens:value,output_tokens:2}}]).complete).toBe(false));
it('parsing failure preserves normal subtotal and raw-line identity',()=>{const r=collectUsage([JSON.stringify(start),JSON.stringify(done()),'{bad'],end).summary();expect(r).toMatchObject({complete:false,total:null,subtotal:{total:12}});expect(r.issues).toContainEqual({line:3,code:'malformed-json'});expect(r.rows[2]?.sha256).toHaveLength(64);});
it('detects accumulated safe integer overflow',()=>{const terminal={type:'turn.completed',usage:{input_tokens:Number.MAX_SAFE_INTEGER,output_tokens:0}};const r=report([start,terminal,start,terminal]);expect(r).toMatchObject({complete:false,total:null,subtotal:{input:null,total:null}});expect(r.issues.some(i=>i.code==='aggregate-overflow')).toBe(true);});
it.each([
 {...end,reason:'timeout' as const},{...end,normalEOF:false},{...end,outputTruncated:true},{...end,readErrors:['fixture']},{...end,code:1},
])('normal completed turn does not hide log or execution loss %#',e=>expect(report([start,done()],e)).toMatchObject({complete:false,total:null,subtotal:{total:12},reference:{wholeRunBelowReference:null}}));
it('unobserved details stay null and absent usage is not zero',()=>{expect(report([start,{type:'turn.completed',usage:{input_tokens:0,output_tokens:0}}])).toMatchObject({complete:true,total:0,subtotal:{cachedInput:null,reasoningOutput:null}});expect(report([])).toMatchObject({total:null,subtotal:{total:null}});});
it('requires explicit EOF and runtime end evidence',()=>expect(collectUsage([JSON.stringify(start),JSON.stringify(done())]).summary()).toMatchObject({complete:false,total:null}));
it('keeps unknown object events as non-accounting rows',()=>{const r=report([{type:'item.completed',item:{text:'fixture'}},start,done()]);expect(r.complete).toBe(true);expect(r.rows[0]?.disposition).toBe('non-accounting-event');});
it('bounds aggregation and does not call a cut log complete',()=>{const l=new UsageLedger();for(let i=0;i<10002;i++)l.accept('{"type":"unknown"}');const r=l.finish(end).summary();expect(r.aggregationTruncated).toBe(true);expect(r.rows).toHaveLength(10000);expect(r.complete).toBe(false);});
it('caps oversized line metadata without parsing it',()=>expect(collectUsage([' '.repeat(65537)],end).summary().issues[0]?.code).toBe('oversized-line'));
it('production collection and evaluation reject caller-authored success',()=>{expect(()=>snapshot({collectionAllowed:true})).toThrow('R11 unresolved');expect(()=>checkedSnapshot('/nonexistent')).toThrow('termination receipt');expect(()=>collectDiagnostic({} as RunResult,{} as Layout,'/nonexistent',{})).toThrow('receipt mismatch');});
it.each([{input_tokens:10,output_tokens:2,cached_input_tokens:11},{input_tokens:10,output_tokens:2,reasoning_output_tokens:3},[]].map(value=>[value]))('rejects impossible usage detail %#',usage=>expect(report([start,{type:'turn.completed',usage}]).complete).toBe(false));
it('stops consuming an unbounded iterable at the explicit aggregation cap',()=>{
    let read=0;function* lines(){while(true){read++;yield '{"type":"unknown"}';}}
    const r=collectUsage(lines(),end).summary();expect(read).toBe(10001);expect(r.complete).toBe(false);expect(r.aggregationTruncated).toBe(true);
});
it('an excessively nested replay identity cannot crash aggregation',()=>{
    const raw='{"type":"turn.completed","id":"deep","usage":{"input_tokens":10,"output_tokens":2},"extra":'+'['.repeat(11000)+'0'+']'.repeat(11000)+'}';
    const r=collectUsage([JSON.stringify(start),raw],end).summary();expect(r.complete).toBe(false);expect(r.issues.some(i=>i.code==='unrepresentable-event-identity')).toBe(true);
});

it('unverified runtime termination cannot certify whole-run usage after normal EOF',()=>expect(report([start,done()],{...end,termination:'unverified'})).toMatchObject({complete:false,total:null,subtotal:{total:12}}));
