import { executor, invoke, type Runtime } from '../../../evaluation/execute.js';

export type Engine = ReturnType<typeof executor>;
export type Observe = (name: string, group: 'change' | 'preserve', expected: unknown, observe: () => unknown) => void;

// Small synchronous Angular form seam. All selection, pricing and payload methods come from the submission.
export class Control {
    constructor(public value: number) {}
    setValue(value: number) { this.value = value; }
}
const reason = '  requested  ';
const line = (orderLineId: string, quantity: number) => ({ orderLineId, quantity });
const item = (id: string, quantity: number, orderPlacedQuantity: number, proratedUnitPriceWithTax: number) =>
    ({ id, quantity, orderPlacedQuantity, proratedUnitPriceWithTax });
const refund = (state: string, total: number, lines: ReturnType<typeof line>[]) => ({ state, total, lines });
const payment = (id: string, amount: number, refunds: ReturnType<typeof refund>[] = [], state = 'Settled') =>
    ({ id, amount, refunds, state });
const ship = [{ id: 'ship', discountedPriceWithTax: 5 }];
interface PaymentControl { id: string; selected: boolean; refundableAmount: number; amountToRefundControl: Control }
function dialog(engine: Engine, lines: ReturnType<typeof item>[], payments: ReturnType<typeof payment>[]) {
    const dialog = engine.instance('RefundOrderDialogComponent');
    Object.assign(dialog, { order: { id: 'order', lines, payments, shippingLines: ship }, reason,
        refundShippingLineIds: [], manuallySetRefundTotal: false, refundTotal: 0 });
    invoke(dialog, 'ngOnInit');
    return { dialog, payments: dialog.refundablePayments as PaymentControl[] };
}
function submit(dialog: Runtime) {
    const submissions: unknown[] = [];
    dialog.resolveWith = (value: unknown) => submissions.push(value);
    invoke(dialog, 'select');
    return submissions;
}
function payload(refundLines: ReturnType<typeof line>[], cancelLines: ReturnType<typeof line>[],
                 amounts: [string, number][], cancelShipping: boolean) {
    return [{ refunds: amounts.map(([paymentId, amount]) =>
        ({ paymentId, amount, lines: refundLines, reason, shipping: 0, adjustment: 0 })),
        cancel: { orderId: 'order', lines: cancelLines, reason, cancelShipping } }];
}

export function allocation(engine: Engine, observe: Observe) {
    // Display capacities 70,20,20. Historical Failed money and non-settled payments must not participate.
    function scenario(selected: string[], manual: number | null, withShipping: boolean) {
        const { dialog: d, payments } = dialog(engine, [item('x', 2, 2, 12)], [
            payment('big', 100, [refund('Settled', 30, []), refund('Failed', 60, [])]),
            payment('excluded', 6, [], 'Authorized'), payment('first', 20),
            payment('second', 55, [refund('Pending', 35, [])]),
        ]);
        for (const p of payments) p.selected = selected.includes(p.id);
        Object.assign(d, { lineQuantities: { x: { quantity: 2, cancel: true } }, manuallySetRefundTotal: manual !== null,
            refundTotal: manual ?? 0, refundShippingLineIds: withShipping ? ['ship'] : [] });
        invoke(d, 'updateRefundTotal');
        return { total: d.refundTotal, controls: payments.map(p => [p.id, p.amountToRefundControl.value]),
            display: (d.refundablePayments as PaymentControl[]).map(p => p.id), submissions: submit(d) };
    }
    function check(name: string, group: 'change'|'preserve', selected: string[], manual: number|null,
                   shipping: boolean, total: number, amounts: [number, number, number]) {
        const ids = ['big', 'first', 'second'];
        const values: [string, number][] = ids.map((id, i) => [id, amounts[i]!]);
        observe(name, group, { total, controls: values, display: ids,
            submissions: payload([line('x', 2)], [line('x', 2)], values.filter(([, n]) => n > 0), shipping) },
            () => scenario(selected, manual, shipping));
    }
    check('effective-capacity-and-tie', 'change', ['big','first','second'], null, true, 29, [0,20,9]);
    check('manual-total-and-payload-order', 'change', ['big','second'], 38, false, 38, [18,0,20]);
    check('only-selected', 'preserve', ['big'], null, false, 24, [24,0,0]);
    check('equal-capacity-order', 'preserve', ['first','second'], 11, false, 11, [0,11,0]);
    check('insufficient-capacity', 'preserve', ['big','first','second'], 135, false, 135, [70,20,20]);
}

export function quantity(engine: Engine, observe: Observe) {
    // A historical refund belongs to a line even if it was processed under another payment.
    function scenario(prior: number, requested: number, keepRefundOnly: boolean, includeY: boolean) {
        const { dialog: d } = dialog(engine, [item('x', 1, 6, 10), item('y', 2, 2, 3)], [
            payment('pay', 500, [refund('Settled', 9, [line('x', prior), line('y', 1)]),
                refund('Failed', 30, [line('x', 5)])]), payment('other', 100, [refund('Pending', 8, [line('x',1)])]),
        ]);
        d.refundShippingLineIds = ['ship'];
        if (includeY) invoke(d, 'onRefundQuantityChange', 'y', 1);
        if (keepRefundOnly || requested === 0) invoke(d, 'onRefundQuantityChange', 'x', 1);
        if (keepRefundOnly) {
            (d.lineQuantities as Record<string,{cancel: boolean}>).x!.cancel = false;
        }
        invoke(d, 'onRefundQuantityChange', 'x', requested);
        type State = Record<string, {quantity: number; cancel: boolean}>;
        const state = (d.lineQuantities as State).x!;
        return { quantity: state.quantity, cancel: state.cancel, total: d.refundTotal, submissions: submit(d) };
    }
    function check(name: string, group: 'change'|'preserve', prior: number, requested: number, keep: boolean,
                   count: number, cancel: boolean, includeY = true) {
        const x = count ? [line('x', count)] : [], y = includeY ? [line('y', 1)] : [];
        const total = 5 + 3 * Number(includeY) + 10 * count;
        observe(name, group, {quantity: count, cancel, total,
            submissions: payload([...x,...y], [...(cancel ? x : []),...y], [['pay',total]], true)},
            () => scenario(prior, requested, keep, includeY));
    }
    // Both template controls use this same predicate. Exercise it on the actual initialized dialog.
    const available = item('available', 1, 4, 10), exhausted = item('exhausted', 2, 3, 5);
    for (const [target, visible] of [[available,true],[exhausted,false]] as const) {
        const expected = visible ? {visible:true, cancelEnabledBeforeEdit:false, cancelEnabledAfterEdit:true}
            : {visible:false};
        observe('quantity-and-cancel-controls/'+target.id, 'preserve', expected, () => {
            const {dialog: d} = dialog(engine,[available,exhausted],[
                payment('first',60,[refund('Settled',10,[line('available',2),line('exhausted',2)])]),
                payment('second',50,[refund('Pending',5,[line('exhausted',1)]),refund('Failed',20,[line('available',2)])]),
            ]);
            const displayed = invoke(d,'lineCanBeRefundedOrCancelled',target);
            if (!displayed) return {visible:displayed};
            const quantities = d.lineQuantities as Record<string,{quantity:number}>;
            const cancelEnabled = () => quantities[target.id]!.quantity !== 0;
            const before = cancelEnabled();
            invoke(d,'onRefundQuantityChange',target.id,1);
            return {visible:displayed, cancelEnabledBeforeEdit:before, cancelEnabledAfterEdit:cancelEnabled()};
        });
    }
    check('aggregate-other-payment-and-failed-history', 'change', 2, 5, false, 3, true);
    check('over-refunded-line-keeps-other-line-and-shipping', 'change', 7, 1, false, 0, false);
    check('capped-edit-retains-refund-only-choice', 'change', 3, 6, true, 2, false);
    check('placed-not-current-and-other-line-history', 'preserve', 1, 4, false, 4, true);
    check('manual-refund-only-under-cap', 'preserve', 1, 2, true, 2, false, false);
    check('zero-clears-cancel', 'preserve', 1, 0, false, 0, false);
}
