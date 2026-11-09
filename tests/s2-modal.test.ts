import { afterEach, expect, it } from 'vitest';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { executor, invoke, Runtime } from '../experiments/domain-model/s2/evaluation/execute.js';
import { createModal, orderLocals, Observer } from '../experiments/domain-model/s2/evaluation/modal.js';
const dirs: string[]=[];
afterEach(()=>dirs.splice(0).forEach(d=>fs.rmSync(d,{recursive:true,force:true})));
function fixture(action: 'select'|'cancel'='select', method?: string, state: Runtime={choice:'user-choice'}, maxCalls=1) {
    const root=fs.mkdtempSync(path.join(os.tmpdir(),'s2-modal-'));dirs.push(root);
    fs.cpSync('tests/fixtures/s2-modal',root,{recursive:true});
    if(method) {
        const file=path.join(root,'first.ts'), text=fs.readFileSync(file,'utf8');
        fs.writeFileSync(file,text.replace(/select\(\) \{[^\n]+\}/,method));
    }
    const mappings=[{file:'parent.ts',className:'Parent'},{file:'first.ts',className:'FirstDialog'},{file:'second.ts',className:'SecondDialog'}];
    const engine=executor(root,mappings,{});
    const observable=(subscribe:(observer:Observer)=>void)=>({subscribe(next:(value:unknown)=>void){subscribe({next,complete:()=>undefined});}});
    const modal=createModal({registrations:mappings.slice(1).map(declaration=>({declaration,component:engine.component(declaration.className),create:()=>engine.instance(declaration.className),userState:()=>state})),observable,action,validateLocals:orderLocals,maxCalls});
    const requests:unknown[]=[];
    const parent=engine.instance('Parent');Object.assign(parent,{modal,values:[],client:{send:(value:unknown)=>requests.push(structuredClone(value))}});
    return {engine,modal,parent,requests};
}
const firstOrder={id:'first-order',active:false,lines:[{id:'first-line',quantity:2,orderPlacedQuantity:3}]};
const secondOrder={id:'other-order',active:true,lines:[{id:'other-line',quantity:4,orderPlacedQuantity:5}]};
it('actual parent locals propagate through two call-owned subscriptions without repaired values',()=>{
    const {engine,modal,parent,requests}=fixture('select',undefined,undefined,2);
    invoke(parent,'run',engine.component('FirstDialog'),firstOrder);
    invoke(parent,'run',engine.component('FirstDialog'),secondOrder);
    modal.assertComplete(2);
    expect(parent.values).toEqual([
        {id:'first-order',active:false,line:'first-line',choice:'user-choice',kind:'first'},
        {id:'other-order',active:true,line:'other-line',choice:'user-choice',kind:'first'},
    ]);
    expect(requests).toEqual([
        {id:'first-order',active:false,line:'first-line',choice:'user-choice',kind:'first'},
        {id:'other-order',active:true,line:'other-line',choice:'user-choice',kind:'first'},
    ]);
    expect(modal.traces.map(t=>t.resolveCount)).toEqual([1,1]);
    expect(modal.traces[0]!.events).toEqual(['fromComponent','subscribe','select','resolve','next','complete','action-returned']);
});
it('actual constructor identity chooses different components with the same result interface',()=>{
    const {engine,modal,parent}=fixture('select',undefined,undefined,2);
    invoke(parent,'run',engine.component('FirstDialog'),firstOrder);
    invoke(parent,'run',engine.component('SecondDialog'),firstOrder);
    modal.assertComplete(2);
    expect((parent.values as Runtime[]).map(v=>v.kind)).toEqual(['first','second']);
    expect(modal.traces.map(t=>t.identity?.file)).toEqual(['first.ts','second.ts']);
});
it('dismiss executes cancel and delivers actual undefined, distinct from unresolved',()=>{
    const {engine,modal,parent,requests}=fixture('cancel');invoke(parent,'run',engine.component('FirstDialog'),firstOrder);modal.assertComplete();
    expect(requests).toEqual([]);
    expect(parent.values).toEqual([undefined]);expect(modal.traces[0]).toMatchObject({resolved:true,resolveCount:1,resolutions:[{$type:'undefined'}],delivered:[{$type:'undefined'}]});
});
it('unknown same-name component does not get substituted with the known component',()=>{
    const {modal}=fixture();const fake=Object.defineProperty(function(){},'name',{value:'FirstDialog'});
    expect(()=>modal.fromComponent(fake,{locals:{order:firstOrder}})).toThrow('Unknown component identity');
    expect(modal.traces[0]!.identity).toBeNull();
});
it.each([undefined,{}, {order:null},{order:{...firstOrder,id:3}},{order:{...firstOrder,active:'true'}},{order:{...firstOrder,lines:'wrong'}}])('malformed locals are unsupported without fixture fallback: %j',locals=>{
    const {engine,modal}=fixture();expect(()=>modal.fromComponent(engine.component('FirstDialog'),{locals})).toThrow();expect(modal.traces[0]!.failure).not.toBeNull();
});
it('locals cannot be overwritten by fixture state or its resolver',()=>{
    for(const state of [{order:secondOrder},{resolveWith:()=>undefined}]) {
        const {engine,modal,parent}=fixture('select',undefined,state);
        invoke(parent,'run',engine.component('FirstDialog'),firstOrder);
        expect(()=>modal.assertComplete()).toThrow('overwrite');expect(parent.values).toEqual([]);
    }
});
it('no resolve is unsupported and never fabricates a dismiss',()=>{
    const {engine,modal,parent}=fixture('select','select() {}');invoke(parent,'run',engine.component('FirstDialog'),firstOrder);
    expect(()=>modal.assertComplete()).toThrow('did not resolve');expect(parent.values).toEqual([]);
    expect(modal.traces[0]).toMatchObject({resolved:false,resolveCount:0,delivered:[]});
});
it('multiple resolves are unsupported without delivering the second value',()=>{
    const {engine,modal,parent}=fixture('select','select() { this.resolveWith("one"); this.resolveWith("two"); }');invoke(parent,'run',engine.component('FirstDialog'),firstOrder);
    expect(()=>modal.assertComplete()).toThrow('Multiple resolves');expect(parent.values).toEqual(['one']);expect(modal.traces[0]!.resolveCount).toBe(2);
});
it('unsubscribed or repeated subscriptions cannot pass or rerun user action',()=>{
    const {engine,modal}=fixture();const stream=modal.fromComponent(engine.component('FirstDialog'),{locals:{order:firstOrder}});
    expect(()=>modal.assertComplete()).toThrow();
    const next=fixture();const calls:unknown[]=[];const subscribed=next.modal.fromComponent(next.engine.component('FirstDialog'),{locals:{order:firstOrder}});
    subscribed.subscribe(v=>calls.push(v));subscribed.subscribe(v=>calls.push(v));
    expect(calls).toHaveLength(1);expect(()=>next.modal.assertComplete()).toThrow('Repeated subscription');
    expect(next.modal.traces[0]!.events.filter(e=>e==='select')).toHaveLength(1);
    void stream;
});
it('production one-modal bound rejects extra calls without reusing prior result',()=>{
    const {engine,modal,parent}=fixture();invoke(parent,'run',engine.component('FirstDialog'),firstOrder);
    expect(()=>invoke(parent,'run',engine.component('FirstDialog'),secondOrder)).toThrow('Additional modal');
    expect(parent.values).toHaveLength(1);expect(modal.traces[1]!.resolutions).toEqual([]);
});
it('trace values are captured before later mutations and cannot serialize functions',()=>{
    const {engine,modal,parent}=fixture();const order=structuredClone(firstOrder);invoke(parent,'run',engine.component('FirstDialog'),order);order.id='later';modal.assertComplete();
    expect(modal.traces[0]!.options).toEqual({locals:{order:firstOrder}});
    const other=fixture();expect(()=>other.modal.fromComponent(other.engine.component('FirstDialog'),{locals:{order:firstOrder},callback:()=>1})).toThrow('Non-data');
});
