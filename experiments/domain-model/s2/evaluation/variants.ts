import path from 'node:path';
import fs from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { Sources, Delta } from './submission.js';
import { mappings } from './behavior.js';
export const variants=['baseline','reference','historical-reference','helper','helper-type-error','helper-syntax-error','missing-helper','deleted-module','out-of-scope','direct-only','no-trim','force-cancel','dismiss-request','continue-after-failure','omit-followup-refund','wrong-order-id','wrong-payment-id','wrong-refund-amount','wrong-cancel-line-id','wrong-cancel-quantity','guard-refund-only','trim-refund-reason','wrong-modal-order','wrong-modal-active','invalid-service-value','invalid-service-never','invalid-service-error','invalid-service-throw','invalid-dialog-null'];
export function patch(source:string,from:string,to:string) {
    if(source.split(from).length!==2) throw Error('Nonunique patch anchor: '+from);
    return source.replace(from,to);
}
export function variantDelta(name:string,baseline:Sources,repo:string):Delta {
    const [detail,cancel,refund,service]=mappings.map(m=>m.file) as [string,string,string,string];
    const original=(f:string)=>baseline.get(f)!.toString('utf8');
    if(name==='baseline')return {};
    if(name==='historical-reference') {
        const records=JSON.parse(gunzipSync(fs.readFileSync(path.join(repo,'experiments/domain-model/s2/verification/2026-11-08/reference-patches.json.gz'))).toString()) as {file:string;patch:{after:string}}[];
        return Object.fromEntries(records.map(r=>[r.file,r.patch.after]));
    }
    const delta:Record<string,string>={};
    delta[cancel]=patch(original(cancel),'select() {',"select() {\n        if (typeof this.reason !== 'string' || !this.reason.trim()) { this.resolveWith(); return; }\n        this.reason = this.reason.trim();");
    if(name==='direct-only')return delta;
    delta[refund]=patch(original(refund),'const cancelLines = this.getOrderLineInput(line => line.cancel);',"const cancelLines = this.getOrderLineInput(line => line.cancel);\n        if (cancelLines.length && (typeof this.reason !== 'string' || !this.reason.trim())) { this.resolveWith(); return; }");
    delta[refund]=patch(delta[refund], 'orderId: this.order.id,\n                reason: this.reason,','orderId: this.order.id,\n                reason: cancelLines.length ? this.reason.trim() : this.reason,');
    delta[service]="import { EMPTY, Observable } from 'rxjs';\n"+patch(original(service),'cancelOrder(input: Codegen.CancelOrderInput) {',"cancelOrder(input: Codegen.CancelOrderInput): Observable<Codegen.CancelOrderMutation> {\n        if (typeof input.reason !== 'string' || !input.reason.trim()) { return EMPTY; }\n        input = { ...input, reason: input.reason.trim() };");
    if(['helper','helper-type-error','helper-syntax-error','missing-helper'].includes(name)) {
        const helper='packages/admin-ui/src/s2-reason.ts';
        for(const file of [cancel,refund,service]) {
            let relative=path.posix.relative(path.posix.dirname(file),helper).replace(/\.ts$/,'');if(!relative.startsWith('.'))relative='./'+relative;
            delta[file]=`import { cleanReason } from '${relative}';\n`+delta[file]!.replaceAll('this.reason.trim()','cleanReason(this.reason)').replaceAll('input.reason.trim()','cleanReason(input.reason)');
        }
        if(name!=='missing-helper')delta[helper]=name==='helper-type-error'?'export function cleanReason(reason:string):string { return 42; }':name==='helper-syntax-error'?'export function cleanReason(reason:string):string { return reason.trim( ; }':'export function cleanReason(reason:string):string { return reason.trim(); }';
    }
    if(name==='deleted-module')return {...delta,[cancel]:null};
    if(name==='out-of-scope')delta['packages/admin-ui/src/unreferenced-s2.ts']='export const unrelated = 1;';
    if(name==='no-trim')for(const file of [cancel,refund,service])delta[file]=delta[file]!.replaceAll('.reason.trim()', '.reason');
    if(name==='force-cancel')delta[detail]=patch(original(detail),'if (input.cancel.lines?.length) {','if (input.cancel) {');
    if(name==='dismiss-request')delta[cancel]=patch(delta[cancel], 'cancel() {\n        this.resolveWith();','cancel() {\n        this.select();');
    if(name==='continue-after-failure')delta[detail]=patch(original(detail),'this.notificationService.error(result.message);\n                                        return undefined;','this.notificationService.error(result.message);\n                                        return input;');
    if(name==='omit-followup-refund')delta[detail]=patch(original(detail),'if (input.refunds.length) {','if (input.refunds.length && !input.cancel.lines?.length) {');
    if(name==='wrong-order-id')delta[service]=patch(delta[service], 'input = { ...input, reason: input.reason.trim() };',"input = { ...input, reason: input.reason.trim(), orderId: 'wrong-order' };");
    if(name==='wrong-payment-id'||name==='wrong-refund-amount')delta[service]=patch(delta[service], 'refundOrder(input: Codegen.RefundOrderInput) {',`refundOrder(input: Codegen.RefundOrderInput) {\n        input = { ...input, ${name==='wrong-payment-id'?"paymentId: 'wrong-payment'":'amount: 999999'} };`);
    if(name==='wrong-cancel-line-id'||name==='wrong-cancel-quantity')delta[refund]=patch(delta[refund], 'lines: cancelLines,',`lines: cancelLines.map(line => ({ ...line, ${name==='wrong-cancel-line-id'?"orderLineId: 'wrong-line'":'quantity: line.quantity + 1'} })),`);
    if(name==='guard-refund-only')delta[refund]=patch(delta[refund],"if (cancelLines.length && (typeof this.reason !== 'string' || !this.reason.trim()))", "if (typeof this.reason !== 'string' || !this.reason.trim())");
    if(name==='trim-refund-reason')delta[refund]=patch(delta[refund], 'reason: this.reason,','reason: this.reason.trim(),');
    if (name==='wrong-modal-order' || name==='wrong-modal-active') {
        const source=original(detail), start=source.indexOf('    private cancelOrder(order: OrderDetailFragment) {'), end=source.indexOf('    private refundOrder(',start);
        if(start<0 || end<start) throw Error('Missing cancel modal method');
        const order=name==='wrong-modal-order'?"order: { ...order, id: 'wrong-modal-order' },":'order: { ...order, active: true },';
        delta[detail]=source.slice(0,start)+patch(source.slice(start,end),'                    order,','                    '+order)+source.slice(end);
    }
    const invalidReturns: Record<string,string> = {
        'invalid-service-value': 'return of(undefined as any);',
        'invalid-service-never': 'return new Observable<Codegen.CancelOrderMutation>(() => {});',
        'invalid-service-error': 'return new Observable<Codegen.CancelOrderMutation>(subscriber => subscriber.error(new Error("invalid")));',
        'invalid-service-throw': 'throw new Error("invalid");',
    };
    if(invalidReturns[name]) {
        delta[service]=patch(delta[service], 'return EMPTY;', invalidReturns[name]!);
        if(name==='invalid-service-value') delta[service]="import { of } from 'rxjs';\n"+delta[service];
    }
    if(name==='invalid-dialog-null') delta[cancel]=patch(delta[cancel], 'this.resolveWith(); return;', 'this.resolveWith(null as any); return;');
    return delta;
}
