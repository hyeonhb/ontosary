const fs = require('node:fs');
const ts = require('./ontosary/node_modules/typescript');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const root = 'vendure/packages/admin-ui/src/lib/order/src/components/';
function fromSource(component, className, methodNames, bindings = {}) {
    const file = root + component + '/' + component + '.component.ts';
    const fileAst = ts.createSourceFile(file, fs.readFileSync(file, 'utf8'), ts.ScriptTarget.Latest, true);
    const classAst = fileAst.statements.find(node => ts.isClassDeclaration(node) && node.name?.text === className);
    const methods = methodNames.map(name => classAst.members.find(member => ts.isMethodDeclaration(member) && member.name.getText() === name).getText());
    const {outputText} = ts.transpileModule('new (class { ' + methods.join('\n') + ' })()', {compilerOptions:{target: ts.ScriptTarget.ES2022}});
    return vm.runInNewContext(outputText, bindings);
}
const detail = fromSource('order-detail', 'OrderDetailComponent', ['canAddFulfillment', 'hasUnsettledModifications', 'outstandingPaymentAmount'], {
    summate: (rows, key) => rows.reduce((sum, row) => sum + row[key], 0),
});
const dialog = fromSource('fulfill-order-dialog', 'FulfillOrderDialogComponent', ['getFulfillableCount', 'getUnfulfilledCount', 'canSubmit'], {
    GlobalFlag: {INHERIT: 'INHERIT', TRUE: 'TRUE', FALSE: 'FALSE'},
    configurableOperationValueIsValid: () => true,
});
const line = (id, quantity, trackInventory, stockOnHand) => ({id, quantity, productVariant: {trackInventory, stockOnHand}});
const order = {
    state: 'PartiallyShipped', type: 'Regular',
    nextStates: ['Shipped', 'PartiallyDelivered', 'Cancelled', 'Modifying'],
    lines: [line('A', 5, 'INHERIT', 1), line('B', 3, 'FALSE', 0)],
    fulfillments: [
        {state: 'Shipped', lines: [{orderLineId: 'A', quantity: 2}, {orderLineId: 'B', quantity: 1}]},
        {state: 'Pending', lines: [{orderLineId: 'A', quantity: 1}]},
        {state: 'Cancelled', lines: [{orderLineId: 'A', quantity: 1}]},
    ],
    totalWithTax: 10000, payments: [{state: 'Settled', amount: 10000, refunds: []}], modifications: [],
};
dialog.order = order;
dialog.fulfillmentHandlerControl = {valid: true};
const setMax = () => {
    dialog.fulfillmentQuantities = Object.fromEntries(order.lines.map(entry => {
        const count = dialog.getFulfillableCount(entry, true);
        return [entry.id, {fulfillCount: count, max: count}];
    }));
};
assert.equal(detail.canAddFulfillment(order), true);
assert.deepEqual(order.lines.map(entry => dialog.getUnfulfilledCount(entry)), [2, 2]);
setMax();
assert.deepEqual(Object.values(dialog.fulfillmentQuantities).map(entry => entry.max), [1, 2]);
assert.equal(dialog.canSubmit(), true);
dialog.fulfillmentQuantities.A.fulfillCount = 2;
assert.equal(dialog.canSubmit(), false);
order.payments[0].amount -= 1000;
assert.equal(detail.canAddFulfillment(order), false);
order.payments[0].amount += 1000;
order.lines[0].productVariant.stockOnHand = 0;
order.lines[1].productVariant.trackInventory = 'TRUE';
assert.equal(detail.canAddFulfillment(order), true);
setMax();
assert.deepEqual(Object.values(dialog.fulfillmentQuantities).map(entry => entry.max), [0, 0]);
assert.equal(dialog.canSubmit(), false);
console.log('Passed 9 assertions using Admin UI methods extracted from TypeScript, with payment sum and valid handler fixtures.');
