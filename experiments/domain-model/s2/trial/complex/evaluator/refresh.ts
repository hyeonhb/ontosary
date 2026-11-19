import { mappings } from '../../../evaluation/behavior.js';
import { invoke, type Runtime } from '../../../evaluation/execute.js';
import { createModal, orderLocals, type Observer } from '../../../evaluation/modal.js';
import type { Engine, Observe } from './dialogs.js';

export interface Rx {
    Subscriber: Function;
    Observable: new (subscribe: (observer: Observer) => void) => unknown;
    of(value: unknown): unknown;
    config: { onUnhandledError: ((error: unknown) => void) | null };
}
type Route = 'direct' | 'mixed' | 'refund-only';
type Outcome = 'ok' | 'reject' | 'failed';
interface Fixture { route: Route; dismiss?: boolean; cancelError?: boolean; refunds?: Outcome[] }
const reason = ' requested ';
const lines = [{ orderLineId: 'x', quantity: 2 }];
const cancel = { orderId: 'order', reason, lines, cancelShipping: true };
const refund = (i: number) => ({ paymentId: 'p'+i, reason, lines, amount: 10+i, adjustment: 0, shipping: 0 });

function scenario(engine: Engine, rx: Rx, fixture: Fixture) {
    const { route, dismiss, cancelError, refunds = [] } = fixture;
    const requests: unknown[] = [], notices: unknown[] = [], refreshes: string[] = [];
    const pending: (() => void)[] = [];
    let settled = 0;
    const service = engine.instance('OrderDataService');
    service.baseDataService = { mutate: (kind: string, args: Runtime) => new rx.Observable(observer => {
        const input = args.input as Runtime;
        requests.push({kind,input:structuredClone(input)});
        pending.push(() => {
            settled++;
            const outcome = refunds[Number(String(input.paymentId).slice(1))];
            const result = kind === 'cancel' ? {cancelOrder: cancelError ?
                {__typename:'OrderStateTransitionError',message:'cancel denied'} : {__typename:'Order',id:'order'}} :
                {refundOrder: outcome === 'reject' ? {__typename:'AlreadyRefundedError',message:'refund denied'} :
                    {__typename:'Refund',state: outcome === 'failed' ? 'Failed' : 'Settled'}};
            observer.next(result); observer.complete();
        });
    }) };
    service.getOrder = (id: string) => ({ single$: new rx.Observable(observer => {
        refreshes.push('order/'+id+'/'+settled);
        observer.next({order:{id}}); observer.complete();
    }) });
    const action = dismiss ? 'cancel' : 'select';
    const actionErrors: unknown[] = [];
    const modal = createModal({
        registrations: mappings.slice(1,3).map(declaration => ({
            declaration, component:engine.component(declaration.className), create:()=>{
                const dialog = engine.instance(declaration.className);
                const original = dialog[action];
                if (typeof original === 'function') dialog[action] = function(this: Runtime, ...args: unknown[]) {
                    try { return Reflect.apply(original,this,args); }
                    catch (error) { actionErrors.push(error); throw error; }
                };
                return dialog;
            },
            userState:()=>({ reason, cancelAll:true, refundShippingLineIds:['ship'],
                refundablePayments: refunds.map((_,i)=>({id:'p'+i,selected:true,amountToRefundControl:{value:10+i}})),
                lineQuantities: declaration.className==='CancelOrderDialogComponent' ? {x:2} :
                    {x:{quantity:2,cancel:route==='mixed'}} }),
        })),
        observable: subscribe => new rx.Observable(subscribe), action, validateLocals: orderLocals,
    });
    const detail = engine.instance('OrderDetailComponent');
    Object.assign(detail,{id:'order', dataService:{order:service}, modalService:{fromComponent:modal.fromComponent},
        fetchHistory:{next:()=>refreshes.push('history/'+settled)},
        notificationService:{success:(...args:unknown[])=>notices.push(['success',...args]),
                             error:(...args:unknown[])=>notices.push(['error',...args])}});
    invoke(detail,'cancelOrRefund',{id:'order',active:false,state:'PaymentSettled',
        payments:route==='direct'?[]:[{state:'Settled'}],lines:[{id:'x',quantity:2,orderPlacedQuantity:2}]});
    if (actionErrors.length) throw actionErrors[0]; // The modal seam otherwise serializes the exception.
    modal.assertComplete();
    // Reverse completion among concurrently requested payments; cap a faulty submission's repeated work.
    while (pending.length && settled < 10) pending.pop()!();
    if (pending.length) throw Error('Exceeded scenario mutation bound');
    return { requests, notices, refreshes:refreshes.sort() };
}

export function refresh(engine: Engine, rx: Rx, observe: Observe) {
    function check(name: string, f: Fixture) {
        const expectedRequests: unknown[] = [], notices: unknown[] = [];
        if (!f.dismiss) {
            if (f.route !== 'refund-only') {
                expectedRequests.push({kind:'cancel',input:cancel});
                if (f.cancelError) notices.push(['error','cancel denied']);
                else if (f.route==='direct') notices.push(['success','order.cancelled-order-success']);
                else notices.push(['success','order.cancelled-order-items-success',{count:2}]);
            }
            if (!f.cancelError) for (const [i,outcome] of (f.refunds??[]).entries()) {
                expectedRequests.push({kind:'refund',input:refund(i)});
                notices.push(outcome==='ok' ? ['success','order.refund-order-success'] :
                    ['error',outcome==='failed'?'order.refund-order-failed':'refund denied']);
            }
        }
        const n = expectedRequests.length;
        observe(name+'/sync','change',n ? ['history/'+n,'order/order/'+n] : [],
            ()=>scenario(engine,rx,f).refreshes);
        observe(name+'/requests','preserve',expectedRequests,()=>scenario(engine,rx,f).requests);
        observe(name+'/notices',f.route==='direct' && f.cancelError?'change':'preserve',notices,()=>scenario(engine,rx,f).notices);
    }
    check('dismiss-direct',{route:'direct',dismiss:true});
    check('dismiss-refund',{route:'mixed',dismiss:true,refunds:['ok']});
    check('direct-success',{route:'direct'});
    check('direct-error',{route:'direct',cancelError:true});
    check('mixed-success',{route:'mixed',refunds:['ok','ok']});
    check('mixed-cancel-rejected',{route:'mixed',cancelError:true,refunds:['ok']});
    check('mixed-partial-success',{route:'mixed',refunds:['reject','ok']});
    check('refund-only-failures',{route:'refund-only',refunds:['failed','reject']});
}
