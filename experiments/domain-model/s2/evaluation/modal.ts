import { Failure } from '../lib/model.js';
import { invoke, Mapping, Runtime } from './execute.js';

export interface Observer { next(value: unknown): void; complete(): void; }
export interface DialogRegistration {
    component: Function;
    declaration: Mapping;
    create(): Runtime;
    userState(): Runtime;
}
export interface ModalTrace {
    call: number;
    identity: (Mapping & { basis: string }) | null;
    options: unknown;
    action: 'select' | 'cancel';
    subscriptions: number;
    resolveCount: number;
    resolved: boolean;
    resolutions: unknown[];
    delivered: unknown[];
    events: string[];
    failure: string | null;
}
/** JSON-safe trace encoding. Undefined is distinct from null and from no resolve event. */
export function traceValue(value: unknown, seen = new Set<object>()): unknown {
    if (value === undefined) return { $type: 'undefined' };
    if (value === null || typeof value === 'string' || typeof value === 'boolean') return value;
    if (typeof value === 'number' && Number.isFinite(value)) return value;
    if (typeof value !== 'object' || seen.has(value)) throw Error('Non-data or cyclic modal value');
    seen.add(value);
    const result = Array.isArray(value) ? value.map(v => traceValue(v, seen)) : Object.fromEntries(Object.entries(value).map(([k,v]) => [k,traceValue(v,seen)]));
    seen.delete(value);
    return result;
}
function record(value: unknown, field: string): Runtime {
    if (!value || typeof value !== 'object' || Array.isArray(value)) throw Error(field + ' must be an object');
    return value as Runtime;
}
export function orderLocals(value: unknown): Runtime {
    const locals = record(value, 'locals');
    if (Object.keys(locals).length !== 1 || !Object.hasOwn(locals,'order')) throw Error('Only locals.order is supported');
    const order = record(locals.order, 'locals.order');
    if (typeof order.id !== 'string' || !order.id || typeof order.active !== 'boolean' || !Array.isArray(order.lines)) throw Error('Invalid order id/active/lines shape');
    for (const value of order.lines) {
        const line = record(value,'order line');
        if (typeof line.id !== 'string' || !line.id || typeof line.quantity !== 'number' || !Number.isFinite(line.quantity) || typeof line.orderPlacedQuantity !== 'number' || !Number.isFinite(line.orderPlacedQuantity)) throw Error('Invalid order line shape');
    }
    // Preserve the actual objects and business values; validation does not repair them.
    return locals;
}
/** Bounded synchronous UI seam. Production uses the pinned RxJS Observable constructor. */
export function createModal<T>(settings: {
    registrations: DialogRegistration[];
    observable(subscribe: (observer: Observer) => void): T;
    action: 'select' | 'cancel';
    validateLocals(value: unknown): Runtime;
    maxCalls?: number;
}) {
    const traces: ModalTrace[] = [];
    const registry = new Map(settings.registrations.map(r => [r.component,r]));
    function fail(trace: ModalTrace, message: string): never {
        trace.failure = message;
        trace.events.push('unsupported');
        throw new Failure('UnsupportedEvaluation', 'modal/' + trace.call, message);
    }
    function fromComponent(component: unknown, options: unknown): T {
        const trace: ModalTrace = {call:traces.length,identity:null,options:null,action:settings.action,subscriptions:0,resolveCount:0,resolved:false,resolutions:[],delivered:[],events:['fromComponent'],failure:null};
        traces.push(trace);
        try {
            trace.options = traceValue(options);
            if (traces.length > (settings.maxCalls ?? 1)) fail(trace,'Additional modal call exceeds scenario bound');
            const registration = registry.get(component as Function);
            if (!registration) fail(trace,'Unknown component identity; names are not identities');
            trace.identity = {...registration.declaration,basis:'Strict reference equality with executor-loaded submitted constructor'};
            const config = record(options,'options');
            if (Object.keys(config).some(k=>!['locals','size'].includes(k)) || (config.size !== undefined && config.size !== 'xl')) fail(trace,'Unsupported modal options');
            const locals = settings.validateLocals(config.locals);
            return settings.observable(observer => {
                trace.subscriptions++;
                trace.events.push('subscribe');
                try {
                    if (trace.subscriptions !== 1) fail(trace,'Repeated subscription unsupported');
                    const dialog = registration.create(), userState = registration.userState();
                    if (Object.keys(userState).some(k => Object.hasOwn(locals,k) || k==='resolveWith')) fail(trace,'User state may not overwrite locals or resolver');
                    Object.assign(dialog,locals,userState);
                    dialog.resolveWith = (value: unknown) => {
                        trace.resolveCount++;
                        trace.events.push('resolve');
                        trace.resolutions.push(traceValue(value));
                        if (trace.resolveCount !== 1) fail(trace,'Multiple resolves unsupported');
                        trace.resolved = true;
                        trace.delivered.push(traceValue(value));
                        trace.events.push('next');
                        observer.next(value);
                        trace.events.push('complete');
                        observer.complete();
                    };
                    trace.events.push(settings.action);
                    invoke(dialog,settings.action);
                    trace.events.push('action-returned');
                    if (!trace.resolved) fail(trace,'Dialog did not resolve synchronously');
                } catch (error) {
                    if (!trace.failure) trace.failure=String(error);
                    // No fabricated undefined result. assertComplete reports this call as unsupported.
                    observer.complete();
                }
            });
        } catch (error) {
            if (!trace.failure) trace.failure=String(error);
            throw error;
        }
    }
    return {fromComponent,traces,assertComplete(expectedCalls = 1) {
        if (traces.length !== expectedCalls) throw new Failure('UnsupportedEvaluation','modal','Unexpected modal call count');
        for (const trace of traces) if (trace.failure || trace.subscriptions!==1 || trace.resolveCount!==1) {
            if (!trace.failure) trace.failure='Modal was not subscribed/resolved exactly once';
            throw new Failure('UnsupportedEvaluation','modal/'+trace.call,trace.failure);
        }
    }};
}
