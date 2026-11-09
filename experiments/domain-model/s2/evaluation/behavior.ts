import { createRequire } from 'node:module';
import path from 'node:path';
import fs from 'node:fs';
import { hash } from '../lib/analysis-session.js';
import { performance } from 'node:perf_hooks';
import { executor, invoke, Runtime, Mapping } from './execute.js';
import { sourceView, Sources } from './submission.js';
import { createModal, orderLocals, Observer, ModalTrace } from './modal.js';

export const base = 'packages/admin-ui/src/lib/';
export const mappings: Mapping[] = [
    { className: 'OrderDetailComponent', file: base + 'order/src/components/order-detail/order-detail.component.ts' },
    { className: 'CancelOrderDialogComponent', file: base + 'order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts' },
    { className: 'RefundOrderDialogComponent', file: base + 'order/src/components/refund-order-dialog/refund-order-dialog.component.ts' },
    { className: 'OrderDataService', file: base + 'core/src/data/providers/order-data.service.ts' },
];
export interface Call { kind: string; input: unknown; }
// JSON transport omits undefined object fields; line order is immaterial, multiplicity is not.
export function canonical(value: unknown, key = ''): unknown {
    if (Array.isArray(value)) {
        const values = value.map(v => canonical(v));
        return key === 'lines' ? values.sort((a,b) => JSON.stringify(a).localeCompare(JSON.stringify(b))) : values;
    }
    if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).filter(([,v]) => v !== undefined).sort(([a],[b]) => a.localeCompare(b)).map(([k,v]) => [k,canonical(v,k)]));
    return value;
}
export function compareCalls(actual: Call[], expected: Call[]) {
    return { pass: JSON.stringify(canonical(actual)) === JSON.stringify(canonical(expected)), expected: canonical(expected), actual: canonical(actual) };
}
export interface CaseResult { name: string; category: 'preservation' | 'draft-requirement'; status: 'passed' | 'failed' | 'unsupported'; assertion: ReturnType<typeof compareCalls>; details: unknown; }
interface Fixture { order: string; line: string; extra: string; payment: string; quantity: number; extraQuantity: number; amount: number; shipping: boolean; }
const fixtures: Fixture[] = [
    { order: 'o-one', line: 'l-one', extra: 'l-extra', payment: 'p-one', quantity: 1, extraQuantity: 2, amount: 10, shipping: true },
    { order: 'o-two', line: 'l-two', extra: 'l-other', payment: 'p-two', quantity: 3, extraQuantity: 4, amount: 75, shipping: false },
];
interface Stream { subscribe(next: (v: unknown) => void): void; }
interface Rx { Observable: new (subscribe: (observer: Observer) => void) => Stream; config: { onUnhandledError: ((error: unknown) => void) | null }; of: (...v: unknown[]) => Stream; }
const bindings: Runtime = { marker: (s: unknown) => s, gql: () => 'unused-document-seam', ORDER_DETAIL_FRAGMENT: 'unused-fragment-seam', _: (s: unknown) => s, CANCEL_ORDER: 'cancel', REFUND_ORDER: 'refund', summate: (rows: Runtime[], k: string) => rows.reduce((s,r) => s + Number(r[k]), 0) };
export async function evaluateBehavior(root: string, sources: Sources) {
    const start = performance.now(), require = createRequire(path.join(root,'package.json')), rx = require('rxjs') as Rx;
    const unhandled: string[] = [], previous = rx.config.onUnhandledError;
    rx.config.onUnhandledError = e => unhandled.push(String(e));
    const executed: Record<string,string> = {}, cases: CaseResult[] = [];
    const engine = executor(root, mappings, bindings, root, sourceView(sources,(f,h) => { executed[f]=h; }));
    type Mode = 'direct' | 'refund' | 'refund-only' | 'dismiss-cancel' | 'dismiss-refund' | 'api';
    function scenario(f: Fixture, name: string, reason: unknown, mode: Mode, category: CaseResult['category'], failCancel=false, active=false) {
        const calls: Call[] = [], valid = typeof reason === 'string' && reason.trim().length > 0;
        const line = { orderLineId: f.line, quantity: f.quantity }, extra = { orderLineId: f.extra, quantity: f.extraQuantity };
        // Independently specified expected network requests; no submitted output feeds these values.
        const cancelInput = { orderId: f.order, reason: category === 'draft-requirement' && valid ? reason.trim() : reason, lines: active ? undefined : mode === 'direct' ? [line,extra] : [line], cancelShipping: f.shipping };
        const refundInput = { paymentId: f.payment, amount: f.amount, lines: [line,extra], reason, shipping: 0, adjustment: 0 };
        let expected: Call[];
        if (mode.startsWith('dismiss') || category === 'draft-requirement' && !valid) expected=[];
        else if (mode === 'refund-only') expected=[{kind:'refund',input:refundInput}];
        else if (mode === 'api') expected=[{kind:'cancel',input:{orderId:f.order,reason:valid ? reason.trim() : reason,lines:[line],cancelShipping:f.shipping}}];
        else expected=[{kind:'cancel',input:cancelInput}, ...(mode === 'refund' && !failCancel ? [{kind:'refund',input:refundInput}] : [])];
        let modalTraces: ModalTrace[] = [], error: string | null = null;
        try {
            const service = engine.instance('OrderDataService');
            service.baseDataService={mutate:(kind:string,args:Runtime) => {
                calls.push(structuredClone({kind,input:args.input}));
                return rx.of(kind==='cancel' ? {cancelOrder:{__typename:failCancel?'OrderStateTransitionError':'Order',message:'failure'}} : {refundOrder:{__typename:'Refund',state:'Settled'}});
            }};
            service.getOrder=()=>({single$:rx.of(undefined)});
            if (mode === 'api') {
                const stream=invoke(service,'cancelOrder',{orderId:f.order,reason,lines:[line],cancelShipping:f.shipping}) as Stream;
                if (!stream || typeof stream.subscribe!=='function') throw Error('Unsupported non-observable API result');
                stream.subscribe(()=>undefined);
            } else {
                const isRefund=mode.includes('refund');
                const userState = (refundDialog: boolean): Runtime => ({
                    reason, cancelAll:f.shipping,
                    lineQuantities:refundDialog ? {
                        [f.line]:{quantity:f.quantity,cancel:mode!=='refund-only'},
                        [f.extra]:{quantity:f.extraQuantity,cancel:false}, excluded:{quantity:0,cancel:true},
                    } : {[f.line]:f.quantity,[f.extra]:f.extraQuantity,excluded:0,negative:-1},
                    refundShippingLineIds:f.shipping?['shipping-line']:[],
                    refundablePayments:[{id:f.payment,selected:true,amountToRefundControl:{value:f.amount}},
                        {id:'unselected',selected:false,amountToRefundControl:{value:13}},
                        {id:'zero',selected:true,amountToRefundControl:{value:0}}],
                });
                const modal = createModal({
                    registrations:[mappings[1]!,mappings[2]!].map(declaration=>({
                        declaration, component:engine.component(declaration.className),
                        create:()=>engine.instance(declaration.className),
                        userState:()=>userState(declaration.className==='RefundOrderDialogComponent'),
                    })),
                    observable:subscribe=>new rx.Observable(subscribe),
                    action:mode.startsWith('dismiss')?'cancel':'select', validateLocals:orderLocals,
                });
                modalTraces=modal.traces;
                const detail=engine.instance('OrderDetailComponent');
                Object.assign(detail,{id:f.order,dataService:{order:service},modalService:{fromComponent:modal.fromComponent},notificationService:{success:()=>undefined,error:()=>undefined},fetchHistory:{next:()=>undefined}});
                invoke(detail,'cancelOrRefund',{
                    id:f.order,active,payments:isRefund?[{state:'Settled'}]:[],state:'PaymentSettled',
                    lines:[{id:f.line,quantity:f.quantity+1,orderPlacedQuantity:f.quantity+1},
                        {id:f.extra,quantity:f.extraQuantity,orderPlacedQuantity:f.extraQuantity}],
                });
                modal.assertComplete();
            }
        } catch(e) { error=String(e); }
        const assertion=compareCalls(calls,expected);
        cases.push({name:f.order+'/'+name,category,status:error?'unsupported':assertion.pass?'passed':'failed',assertion,details:{error,modalTraces,inputReason:reason??null,reasonInput:reason===undefined?'undefined':typeof reason,uiCoverage:typeof reason==='string'&&!!reason?'truthy reason; other template constraints not evaluated':'forced method input; original truthiness UI condition would reject'}});
    }
    try {
        for(const f of fixtures) {
            for(const [i,reason] of ['normal','  spaced  ','','   ',null,undefined].entries())
                for(const mode of ['direct','refund','api'] as const) scenario(f,mode+'-reason-'+i,reason,mode,'draft-requirement');
            for(const [i,reason] of ['normal','  spaced  ','   '].entries()) scenario(f,'refund-only-'+i,reason,'refund-only','preservation');
            scenario(f,'dismiss-cancel','normal','dismiss-cancel','preservation');
            scenario(f,'dismiss-refund','normal','dismiss-refund','preservation');
            scenario(f,'cancel-failure-stops-refund','normal','refund','preservation',true);
            scenario(f,'active-lines-omitted','normal','direct','preservation',false,true);
            scenario(f,'positive-lines-only','normal','direct','preservation');
        }
        await new Promise(resolve=>setTimeout(resolve,10));
        if(unhandled.length) for(const c of cases) {c.status='unsupported';c.details={unhandled};}
    } finally { rx.config.onUnhandledError=previous; }
    const count=(category:CaseResult['category'])=>({passed:cases.filter(c=>c.category===category&&c.status==='passed').length,total:cases.filter(c=>c.category===category).length});
    const runtimeHashes=Object.fromEntries(Object.keys(require.cache).filter(f=>f.startsWith(root+path.sep)).sort().map(f=>[path.relative(root,f),hash(fs.readFileSync(f))]));
    return {runtimeHashes,status:cases.some(c=>c.status==='unsupported')?'unsupported':cases.every(c=>c.status==='passed')?'passed':'failed',cases,preservation:count('preservation'),draft:count('draft-requirement'),executedFiles:executed,cost:{wallTimeMs:performance.now()-start},scope:'Submitted methods/helpers; fixed DI/UI/server seams; HTML and network scheduling unassessed'};
}
