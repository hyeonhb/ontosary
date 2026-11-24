import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { fix, parent, loadControls } from './load-controls.mjs';

const repository = process.argv[2];
assert.ok(repository, 'pass the path to the upstream Vendure git repository');
assert.equal(execFileSync('git', ['-C', repository, 'rev-parse', fix + '^'], {encoding:'utf8'}).trim(), parent);
const cases = JSON.parse(readFileSync(new URL('cases.json', import.meta.url)));

function checkoutFixture(product, test) {
    const shipping = Object.assign(new product.ShippingLine(), {
        id:'shipment', listPrice:test.taxIncluded ? 1200 : 1000,
        listPriceIncludesTax:test.taxIncluded, taxLines:[{taxRate:20}], adjustments:[],
    });
    const settled = test.path === 'with-refund';
    const item = {
        id:'item', quantity:2, orderPlacedQuantity:2, proratedUnitPriceWithTax:100,
        get proratedLinePrice() { return this.quantity * 100; },
        get proratedLinePriceWithTax() { return this.quantity * 100; },
    };
    const order = Object.assign(new product.Order(), {
        id:'order', active:false, state:settled ? 'PaymentSettled' : 'PaymentAuthorized',
        channels:[{id:'channel'}], lines:[item], shippingLines:[shipping],
        payments:[{id:'payment', state:settled ? 'Settled' : 'Authorized', amount:1400, refunds:[]}],
    });
    return order;
}

function submitDialog(product, order, test) {
    const detail = new product.OrderDetailComponent();
    let path, dialog, submission;
    detail.cancelOrder = () => { path = 'direct'; dialog = new product.CancelOrderDialogComponent(); };
    detail.refundOrder = () => { path = 'with-refund'; dialog = new product.RefundOrderDialogComponent(); };
    detail.cancelOrRefund(order);
    assert.equal(path, test.path);
    Object.assign(dialog, {order, reason:'customer request', resolveWith: value => { submission = value; }});
    dialog.ngOnInit();
    if (path === 'direct') {
        if (!test.cancelShipping) {
            dialog.cancelAll = false;
            dialog.radioChanged();
            dialog.lineQuantities.item = 1;
            dialog.checkIfAllSelected();
        }
        assert.ok(dialog.reason && dialog.selectionCount > 0);
    } else {
        assert.ok(dialog.lineCanBeRefundedOrCancelled(order.lines[0]));
        dialog.onRefundQuantityChange('item', test.cancelShipping ? 2 : 1);
        if (test.cancelShipping) dialog.toggleShippingRefund('shipment');
        assert.ok(dialog.canSubmit());
    }
    dialog.select();
    return path === 'direct' ? {cancel:submission, refunds:[]} : submission;
}

function cancellationServices(product, order) {
    const item = order.lines[0];
    const stockQueries = new Set(['Allocation','Sale','Release','FulfillmentLine','Cancellation']);
    const saves = [];
    const modifier = new product.OrderModifier();
    modifier.connection = {
        getEntityOrThrow(_ctx, type, id) {
            assert.equal(type, product.Order);
            assert.equal(id, order.id);
            return order;
        },
        getRepository(_ctx, type) {
            if (stockQueries.has(type)) return {
                createQueryBuilder: () => ({
                    leftJoinAndSelect() { return this; }, where() { return this; }, getMany: () => [],
                }),
            };
            if (type === 'OrderLine') return {
                find: ({where}) => where.id.includes(item.id) ? [{...item, order}] : [],
                update(id, values) { assert.equal(id, item.id); Object.assign(item, values); },
            };
            assert.ok(type === product.Order || type === product.ShippingLine);
            return {save(entity) { saves.push(entity); }};
        },
    };
    modifier.stockMovementService = {createCancellationsForOrderLines() {}, createReleasesForOrderLines() {}};
    modifier.eventBus = {publish() {}};
    modifier.historyService = {createHistoryEntryForOrder() {}};
    modifier.orderCalculator = new product.OrderCalculator();
    modifier.orderCalculator.configService = {taxOptions:{orderTaxCalculationStrategy:new product.DefaultOrderTaxCalculationStrategy()}};
    return {modifier, saves};
}

const money = order => [order.shipping, order.shippingWithTax, order.total, order.totalWithTax];

async function observe(product, test) {
    const order = checkoutFixture(product, test);
    const {modifier, saves} = cancellationServices(product, order);
    modifier.orderCalculator.calculateOrderTotals(order);
    const before = money(order);
    assert.deepEqual(before, [1000,1200,1200,1400]);
    const {cancel, refunds} = submitDialog(product, order, test);
    assert.equal(cancel.cancelShipping, test.cancelShipping);
    const cancelledQuantity = test.cancelShipping ? 2 : 1;
    assert.deepEqual(cancel.lines, [{orderLineId:'item', quantity:cancelledQuantity}]);
    const refundAmounts = refunds.map(refund => refund.amount);
    assert.deepEqual(refundAmounts, test.path === 'direct' ? [] : [test.cancelShipping ? 1400 : 100]);

    const allCancelled = await modifier.cancelOrderByOrderLines({channelId:'channel'}, cancel, cancel.lines);
    assert.equal(allCancelled, test.cancelShipping);
    assert.equal(order.lines[0].quantity, 2 - cancelledQuantity);
    assert.equal(saves.at(-1), order);
    assert.equal(saves.includes(order.shippingLines[0]), test.cancelShipping);
    const after = money(order);
    return {...test, before, cancel, refundAmounts, remainingItems:order.lines[0].quantity,
        after, passed:after.every((value, i) => value === test.expected[i])};
}

const expected = {
    original:[false,true,false,true,true,true],
    'always-gross':[true,false,true,false,true,true],
    upstream:[true,true,true,true,true,true],
};
const controls = {};
for (const [variant, pass] of Object.entries(expected)) {
    const product = loadControls(repository, variant);
    controls[variant] = await Promise.all(cases.map(test => observe(product, test)));
    assert.deepEqual(controls[variant].map(row => row.passed), pass);
}
process.stdout.write(JSON.stringify({parent,fix,participantCalls:0,controls}, null, 2) + '\n');
