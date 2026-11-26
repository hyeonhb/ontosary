// Evaluate the pinned product methods with explicit bindings for their local dependencies.
// Decorators, constructors and unrelated application modules are outside this observation.
import { execFileSync } from 'node:child_process';
import assert from 'node:assert/strict';
import ts from 'typescript';

export const parent = '8dbb6e4063248c3084e5768d613347a3453eda41';
export const fix = 'e30fd9e94214135de85c95631edc6f2fcedd0da1';
export const modifierPath = 'packages/core/src/service/helpers/order-modifier/order-modifier.ts';

export function loadControls(repository, variant) {
    return loadProduct(path => {
        const revision = path === modifierPath && variant === 'upstream' ? fix : parent;
        let source = execFileSync('git', ['-C', repository, 'show', revision + ':' + path], { encoding: 'utf8' });
        if (path === modifierPath && variant === 'always-gross') {
            const old = 'amount: -shippingLine.discountedPrice,';
            assert.equal(source.split(old).length, 2);
            source = source.replace(old, 'amount: -shippingLine.discountedPriceWithTax,');
        }
        return source;
    });
}

export function loadProduct(readSource, loadModifier) {
    const bindings = {};
    const core = 'packages/core/src/';
    const angular = 'packages/admin-ui/src/lib/order/src/';
    const component = name => angular + 'components/' + name + '/' + name + '.component.ts';

    function load(path, name, members) {
        const source = readSource(path);
        const file = ts.createSourceFile(path, source, ts.ScriptTarget.Latest, true);
        const node = file.statements.find(statement => statement.name?.text === name);
        assert.ok(node, name);
        let body;
        if (members) {
            const declarations = members.map(key => {
                const member = node.members.find(item => item.name?.getText(file) === key);
                assert.ok(member, name + '.' + key);
                const decorators = ts.getDecorators(member);
                const start = decorators?.at(-1)?.end ?? member.getStart(file);
                return source.slice(start, member.end);
            });
            body = 'class ' + name + ' {\n' + declarations.join('\n') + '\n}';
        } else {
            body = node.getText(file).replace(/^export /, '');
        }
        const js = ts.transpileModule(body, {compilerOptions: {target: ts.ScriptTarget.ES2022}}).outputText;
        bindings[name] = Function(...Object.keys(bindings), js + '\nreturn ' + name)(...Object.values(bindings));
    }

    // Only storage/infrastructure and form control surfaces are substituted.
    class FormControl {
        constructor(value) { this.value = value; }
        setValue(value) { this.value = value; }
    }
    Object.assign(bindings, {
        FormControl, Validators: { min: () => undefined, max: () => undefined },
        In: ids => ids, AdjustmentType: {OTHER:'OTHER'}, HistoryEntryType: {ORDER_CANCELLATION:'ORDER_CANCELLATION'},
        OrderLineEvent: class {},
    });
    for (const name of ['OrderLine','Allocation','Sale','Release','FulfillmentLine','Cancellation']) {
        bindings[name] = name;
    }
    load('packages/common/src/shared-utils.ts', 'summate');
    load(core + 'common/utils.ts', 'idsAreEqual');
    for (const fn of ['taxComponentOf', 'netPriceOf', 'taxPayableOn', 'grossPriceOf']) {
        load(core + 'common/tax-utils.ts', fn);
    }
    load(core + 'config/entity/default-money-strategy.ts', 'DefaultMoneyStrategy', ['round']);
    const rounding = new bindings.DefaultMoneyStrategy();
    bindings.roundMoney = rounding.round.bind(rounding);
    load(core + 'entity/order/order.entity.ts', 'Order', ['total','totalWithTax']);
    load(core + 'entity/shipping-line/shipping-line.entity.ts', 'ShippingLine',
        ['discountedPrice','discountedPriceWithTax','getAdjustmentsTotal','taxRate']);
    load(core + 'config/tax/default-order-tax-calculation-strategy.ts', 'DefaultOrderTaxCalculationStrategy',
        ['calculateOrderTotals']);
    load(core + 'service/helpers/order-calculator/order-calculator.ts', 'OrderCalculator', ['calculateOrderTotals']);
    const utils = core + 'service/helpers/utils/order-utils.ts';
    load(utils, 'getOrdersFromLines');
    load(utils, 'orderLinesAreAllCancelled');
    if (loadModifier) {
        bindings.OrderModifier = loadModifier(readSource(modifierPath), bindings);
    } else {
        load(modifierPath, 'OrderModifier', ['cancelOrderByOrderLines']);
    }
    load(angular + 'common/get-refundable-payments.ts', 'getRefundablePayments');
    load(component('order-detail'), 'OrderDetailComponent', ['cancelOrRefund','orderHasSettledPayments']);
    load(component('cancel-order-dialog'), 'CancelOrderDialogComponent',
        ['cancelAll','ngOnInit','radioChanged','checkIfAllSelected','selectionCount','getLineInputs','select']);
    load(component('refund-order-dialog'), 'RefundOrderDialogComponent',
        ['refundShippingLineIds','manuallySetRefundTotal','refundTotal','lineCanBeRefundedOrCancelled',
         'ngOnInit','updateRefundTotal','toggleShippingRefund','onRefundQuantityChange',
         'amountToRefundTotal','canSubmit','getOrderLineInput','select']);
    return bindings;
}
