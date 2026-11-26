import assert from 'node:assert/strict';

function checkoutFixture(product, test, guard) {
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
        channels:[guard({id:'channel', pricesIncludeTax:test.taxIncluded}, 'channel')], lines:[guard(item, 'orderLine')], shippingLines:[guard(shipping, 'shippingLine')], surcharges:[],
        payments:[{id:'payment', state:settled ? 'Settled' : 'Authorized', amount:1400, refunds:[]}],
    });
    return guard(order, 'order');
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
    const orderSaves = [];
    const savedShippingLines = new Set();
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
            return {save(entity) {
                if (type === product.Order) {
                    assert.equal(entity.id, order.id, 'Unexpected order in repository fixture');
                    orderSaves.push(money(entity));
                } else {
                    savedShippingLines.add(entity.id);
                }
            }};
        },
    };
    modifier.stockMovementService = {createCancellationsForOrderLines() {}, createReleasesForOrderLines() {}};
    modifier.eventBus = {publish() {}};
    modifier.historyService = {createHistoryEntryForOrder() {}};
    modifier.orderCalculator = new product.OrderCalculator();
    modifier.orderCalculator.configService = {taxOptions:{orderTaxCalculationStrategy:new product.DefaultOrderTaxCalculationStrategy()}};
    return {modifier, orderSaves, savedShippingLines};
}

const money = order => [order.shipping, order.shippingWithTax, order.total, order.totalWithTax];

export async function observe(product, test, guard = value => value) {
    const order = checkoutFixture(product, test, guard);
    const {modifier, orderSaves, savedShippingLines} = cancellationServices(product, order);
    modifier.orderCalculator.calculateOrderTotals(order);
    const before = money(order);
    assert.deepEqual(before, [1000,1200,1200,1400]);
    const {cancel, refunds} = submitDialog(product, order, test);
    assert.equal(cancel.cancelShipping, test.cancelShipping);
    const cancelledQuantity = test.cancelShipping ? 2 : 1;
    assert.deepEqual(cancel.lines, [{orderLineId:'item', quantity:cancelledQuantity}]);
    const refundAmounts = refunds.map(refund => refund.amount);
    assert.deepEqual(refundAmounts, test.path === 'direct' ? [] : [test.cancelShipping ? 1400 : 100]);

    const expectedRemaining = order.lines[0].quantity - cancelledQuantity;
    const ctx = guard({channelId:'channel', channel:order.channels[0]}, 'context');
    const allCancelled = await modifier.cancelOrderByOrderLines(ctx, guard(cancel, 'input'), cancel.lines);
    const remainingItems = order.lines[0].quantity;
    const after = money(order);
    assert.equal(savedShippingLines.has(order.shippingLines[0].id), test.cancelShipping,
        'Unexpected shipping repository interaction');
    // Only compare completed, interpretable observations. Fixture/runtime errors go
    // back to the caller as ungradable, without treating their message as a verdict.
    if (typeof allCancelled !== 'boolean' || !Number.isFinite(remainingItems)) {
        throw Error('Uninterpretable cancellation result or quantity; origin not established');
    }

    const mismatches = [];
    function compare(field, expected, actual) {
        const matches = Array.isArray(expected)
            ? Array.isArray(actual) && actual.length === expected.length && expected.every((value, i) => actual[i] === value)
            : expected === actual;
        if (!matches) mismatches.push({field, expected, actual});
    }
    compare('allCancelled', expectedRemaining === 0, allCancelled);
    compare('remainingItems', expectedRemaining, remainingItems);
    compare('moneyAtOrderSave', test.expected, orderSaves.at(-1) ?? null);
    compare('moneyAtReturn', test.expected, after);
    return {...test, before, cancel, refundAmounts, remainingItems, after,
        orderSaves, allCancelled, mismatches, passed:mismatches.length === 0};
}
