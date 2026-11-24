import React, { createRef } from 'react';
import { createRoot } from 'react-dom/client';
import { flushSync } from 'react-dom';
import { RefundOrderDialog } from 'control-dialog';

function line(id, placed, quantity) {
    return { id, orderPlacedQuantity: placed, quantity, proratedUnitPriceWithTax: 100,
        featuredAsset: null, productVariant: { name: id, sku: id + '-sku' } };
}

function observe({ name, placed, current, refunded, payments, increased, added, inputs }) {
    const target = line('target', placed, current);
    const order = { state: 'PaymentSettled', currencyCode: 'USD', shippingLines: [],
        lines: added ? [line('existing', 1, 1), target] : [target],
        payments: payments.map((amount, i) => ({ id: 'p' + i, state: 'Settled', amount, method: 'manual',
            refunds: refunded && i === 0 ? [{ state: 'Settled', total: refunded * 100,
                lines: [{ orderLineId: target.id, quantity: refunded }] }] : [] })),
        modifications: increased || added ? [{ isSettled: true }] : [] };
    const root = createRoot(document.getElementById('mount')), ref = createRef();
    flushSync(() => root.render(<RefundOrderDialog ref={ref} order={order}/>));
    flushSync(() => ref.current.open());
    const dialog = document.querySelector('[role=dialog]');
    const rows = Array.from(dialog.querySelectorAll('tbody tr'));
    const row = rows.find(r => r.cells[1]?.textContent.includes('target-sku'));
    const field = row?.querySelector('input[type=number]');
    const quantityCell = row?.cells[3];
    const quantityShown = quantityCell ? Array.from(quantityCell.childNodes)
        .filter(n => n.nodeType === Node.TEXT_NODE).map(n => n.textContent).join('').trim() : null;
    const observed = { name, quantityShown, rows: rows.map(r => r.cells[1].textContent), displayed: row?.cells[3].textContent.trim() ?? null,
        selectable: Boolean(field && !field.disabled && !field.readOnly), max: field?.getAttribute('max') ?? null,
        attempts: [] };
    if (observed.selectable) {
        const setValue = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
        for (const requested of inputs) {
            flushSync(() => {
                setValue.call(field, String(requested));
                field.dispatchEvent(new Event('input', { bubbles: true }));
            });
            // Re-render from hook state so a value set only on the DOM cannot count as accepted.
            flushSync(() => root.render(<RefundOrderDialog ref={ref} order={order}/>));
            observed.attempts.push({ requested, retained: row.querySelector('input[type=number]').value });
        }
    }
    flushSync(() => root.unmount());
    return observed;
}

try {
    const results = [
        { name: 'increase', placed: 1, current: 2, refunded: 0, increased: true, payments: [100,100], inputs: [2,3] },
        { name: 'add', placed: 0, current: 1, refunded: 0, added: true, payments: [100,100], inputs: [1,2] },
        { name: 'partial', placed: 3, current: 1, refunded: 2, payments: [300], inputs: [1,2] },
        { name: 'exhausted', placed: 2, current: 0, refunded: 2, payments: [200], inputs: [1] },
    ].map(observe);
    document.querySelector('#result').textContent = JSON.stringify(results);
} catch (e) {
    document.querySelector('#result').textContent = JSON.stringify({ error: String(e), stack: e.stack });
}
