import ts from 'typescript';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { executor, invoke, Runtime, Mapping } from './execute.js';
import { hash } from '../lib/analysis-session.js';
interface Stream {
    subscribe(next: (v: unknown) => void): void;
}
interface Rx {
    config: {
        onUnhandledError: (error: unknown) => void;
    };
    of: (...v: unknown[]) => Stream;
}
const [submissionArg, envArg, out] = process.argv.slice(2);
if (!submissionArg || !envArg || !out)
    throw new Error('Usage: evaluate <submitted-source-root> <prepared-environment-root> <new-result.json>');
const root = path.resolve(submissionArg), env = path.resolve(envArg), req = createRequire(path.join(env, 'package.json')), rx = req('rxjs') as Rx;
const base = 'packages/admin-ui/src/lib/';
const mappings: Mapping[] = [{ className: 'OrderDetailComponent', file: base + 'order/src/components/order-detail/order-detail.component.ts' }, { className: 'CancelOrderDialogComponent', file: base + 'order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts' }, { className: 'RefundOrderDialogComponent', file: base + 'order/src/components/refund-order-dialog/refund-order-dialog.component.ts' }, { className: 'OrderDataService', file: base + 'core/src/data/providers/order-data.service.ts' }];
const unhandled: unknown[] = [];
rx.config.onUnhandledError = e => unhandled.push(e instanceof Error ? e.message : String(e));
const result: {
    name: string;
    category: string;
    pass: boolean;
    calls: unknown[];
    details: unknown;
}[] = [];
const bindings: Runtime = { marker: (s: unknown) => s, gql: () => 'unused-document-seam', ORDER_DETAIL_FRAGMENT: 'unused-fragment-seam', _: (s: unknown) => s, CANCEL_ORDER: 'cancel', REFUND_ORDER: 'refund', summate: (rows: Runtime[], k: string) => rows.reduce((s, r) => s + Number(r[k]), 0) };
const engine = executor(root, mappings, bindings, env);
function scenario(name: string, reason: unknown, mode: 'direct' | 'refund' | 'refund-only' | 'dismiss-cancel' | 'dismiss-refund', category: string, failCancel = false, active = false) {
    const calls: Runtime[] = [];
    let returned: unknown;
    const service = engine.instance('OrderDataService');
    service.baseDataService = { mutate: (kind: unknown, args: Runtime) => { calls.push({ kind, input: args.input }); return rx.of(kind === 'cancel' ? { cancelOrder: { __typename: failCancel ? 'OrderStateTransitionError' : 'Order', message: 'failure' } } : { refundOrder: { __typename: 'Refund', state: 'Settled' } }); } };
    service.getOrder = () => ({ single$: rx.of(undefined) });
    const dialog = engine.instance(mode.includes('refund') ? 'RefundOrderDialogComponent' : 'CancelOrderDialogComponent');
    Object.assign(dialog, { order: { id: 'o', active, lines: [{ id: 'l', quantity: 2, orderPlacedQuantity: 2 }] }, reason, cancelAll: true, lineQuantities: mode.includes('refund') ? { l: { quantity: 1, cancel: mode !== 'refund-only' } } : { l: 1, zero: 0 }, refundShippingLineIds: [], refundablePayments: [{ id: 'p', selected: true, amountToRefundControl: { value: 10 } }], resolveWith: (v: unknown) => { returned = v; } });
    try {
        invoke(dialog, mode.startsWith('dismiss') ? 'cancel' : 'select');
        const detail = engine.instance('OrderDetailComponent');
        Object.assign(detail, { id: 'o', dataService: { order: service }, modalService: { fromComponent: () => rx.of(returned) }, notificationService: { success: () => undefined, error: () => undefined }, fetchHistory: { next: () => undefined } });
        // Dismiss still passes through the submitted parent flow; no request may appear.
        invoke(detail, 'cancelOrRefund', { id: 'o', active: mode.includes('refund') ? false : true, payments: mode.includes('refund') ? [{ state: 'Settled' }] : [], state: 'PaymentSettled' });
        const cancel = calls.filter(c => c.kind === 'cancel'), refund = calls.filter(c => c.kind === 'refund');
        const input = cancel[0]?.input as Runtime | undefined;
        let pass: boolean;
        if (mode.startsWith('dismiss'))
            pass = calls.length === 0;
        else if (mode === 'refund-only')
            pass = cancel.length === 0 && refund.length === 1;
        else if (failCancel)
            pass = cancel.length === 1 && refund.length === 0 && calls.length === 1;
        else if (category === 'preservation')
            pass = cancel.length === 1 && refund.length === 0 && (active ? input?.lines === undefined : Array.isArray(input?.lines) && JSON.stringify(input.lines) === JSON.stringify([{ orderLineId: 'l', quantity: 1 }]));
        else {
            const valid = typeof reason === 'string' && reason.trim().length > 0;
            pass = valid ? cancel.length === 1 && input?.reason === (reason as string).trim() && JSON.stringify(calls.map(c => c.kind)) === JSON.stringify(mode === 'refund' ? ['cancel', 'refund'] : ['cancel']) : calls.length === 0;
        }
        result.push({ name, category, pass, calls, details: { dialogReturned: returned ?? null } });
    }
    catch (e) {
        result.push({ name, category, pass: false, calls, details: { status: 'unsupported-or-failed', error: e instanceof Error ? e.message : String(e) } });
    }
}
for (const [i, reason] of ['normal', '  spaced  ', '', '   ', null, undefined].entries())
    for (const mode of ['direct', 'refund'] as const)
        scenario(`${mode}-reason-${i}`, reason, mode, 'draft-requirement');
scenario('refund-only', 'normal', 'refund-only', 'preservation');
scenario('dismiss-cancel', 'normal', 'dismiss-cancel', 'preservation');
scenario('dismiss-refund', 'normal', 'dismiss-refund', 'preservation');
scenario('cancel-failure-stops-refund', 'normal', 'refund', 'preservation', true);
scenario('active-lines-omitted', 'normal', 'direct', 'preservation', false, true);
scenario('positive-lines-only', 'normal', 'direct', 'preservation');
for (const [i, reason] of ['normal', '  spaced  ', '', '   ', null, undefined].entries()) {
    const calls: Runtime[] = [];
    const service = engine.instance('OrderDataService');
    service.baseDataService = { mutate: (kind: unknown, args: Runtime) => { calls.push({ kind, input: args.input }); return rx.of(undefined); } };
    let error: unknown = null;
    try {
        invoke(service, 'cancelOrder', { orderId: 'o', reason });
    }
    catch (e) {
        error = e instanceof Error ? e.message : String(e);
    }
    const valid = typeof reason === 'string' && reason.trim().length > 0;
    const pass = error === null && (valid ? calls.length === 1 && (calls[0]?.input as Runtime)?.reason === (reason as string).trim() : calls.length === 0);
    result.push({ name: `api-reason-${i}`, category: 'draft-requirement', pass, calls, details: { error } });
}
await new Promise(resolve => setTimeout(resolve, 10));
if (unhandled.length)
    for (const c of result) {
        c.pass = false;
        c.details = { status: 'unsupported-unhandled-error', errors: unhandled };
    }
const report = { scope: 'Submitted method bodies plus submitted relative helpers; real pinned RxJS; constructor/field/Angular/DI/server/UI excluded. No untrusted-code sandbox claim.', policy: 'Draft: invalid reason suppresses submission; requires review before trial.', sourceMapping: mappings.map(m => { const text = fs.readFileSync(path.join(root, m.file), 'utf8'), sf = ts.createSourceFile(m.file, text, ts.ScriptTarget.Latest, true), cls = sf.statements.find((n): n is ts.ClassDeclaration => ts.isClassDeclaration(n) && n.name?.text === m.className); return { ...m, submittedHash: hash(text), baselineHash: hash(fs.readFileSync(path.join(env, m.file))), methods: cls?.members.filter(n => ts.isMethodDeclaration(n) || ts.isGetAccessorDeclaration(n)).map(n => ({ name: n.name?.getText(sf), offset: n.getStart(sf), end: n.getEnd(), line: sf.getLineAndCharacterOfPosition(n.getStart(sf)).line + 1, anchor: n.getText(sf).split('\n')[0] })), testedCoverage: 'Only scenarios listed below; not every extracted method is executed' }; }), runtime: { typescript: ts.version, node: process.version, rxjsPackageHash: hash(fs.readFileSync(path.join(env, 'node_modules/rxjs/package.json'))) }, cases: result, preservationPassed: result.filter(r => r.category === 'preservation' && r.pass).length, preservationTotal: result.filter(r => r.category === 'preservation').length, draftPassed: result.filter(r => r.category === 'draft-requirement' && r.pass).length, draftTotal: 18 };
fs.writeFileSync(out, JSON.stringify(report, null, 2) + '\n', { flag: 'wx' });
if (unhandled.length)
    process.exitCode = 1;
console.log(JSON.stringify({ preservationPassed: report.preservationPassed, draftPassed: report.draftPassed }));
