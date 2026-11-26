import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { loadProduct, modifierPath } from '../load-controls.mjs';
import { observe } from '../observe.mjs';
import { submittedModifier } from './load-modifier.mjs';

const [root, manifest] = process.argv.slice(2);
const {changes, baseModifier, changedLines, deletedOnly} = JSON.parse(readFileSync(manifest));
const cases = JSON.parse(readFileSync(new URL('../cases.json', import.meta.url)));
const sources = {};
function read(path) {
    const bytes = readFileSync(join(root, path));
    sources[path] = createHash('sha256').update(bytes).digest('hex');
    return new TextDecoder('utf-8', {fatal:true}).decode(bytes);
}

const calls = new Map();
let tracked;
const rows = [];
try {
    if (deletedOnly.length) {
        throw Error('Removed lines have no submitted execution site: ' + JSON.stringify(deletedOnly));
    }
    const additions = [];
    for (const {path, status, mode} of changes) {
        if (mode === '100644' && status === 'A' && path.endsWith('.ts')) additions.push(path);
        else if (!(mode === '100644' && status === 'M' && path === modifierPath)) {
            throw Error('Unobserved change: ' + status + ' ' + path);
        }
    }
    const product = loadProduct(read, (source, bindings) => {
        const loaded = submittedModifier(source, baseModifier, additions, changedLines, read, bindings, calls);
        tracked = loaded.tracked;
        return loaded.OrderModifier;
    });
    for (const test of cases) {
        calls.clear();
        try {
            const result = await observe(product, test, checkedFixture);
            if (!result.after.every(Number.isFinite)) {
                const observed = result.after.map(value => Number.isFinite(value) ? value : String(value));
                rows.push({...test, after:observed, status:'ungradable', stage:'runtime',
                    reason:'Non-finite or missing money value; origin not established', calls:Object.fromEntries(calls)});
                continue;
            }
            rows.push({...result, status:result.passed ? 'pass' : 'fail', calls:Object.fromEntries(calls)});
        } catch (error) {
            rows.push({...test, status:'ungradable', stage:'runtime', reason:String(error.message), calls:Object.fromEntries(calls)});
        }
    }
    const skipped = [...tracked].filter(id => !rows.some(row => row.calls[id]));
    if (skipped.length) {
        for (const row of rows) {
            if (row.status === 'ungradable') continue;
            delete row.passed;
            Object.assign(row, {status:'ungradable', stage:'coverage', reason:'Unobserved code: ' + skipped.join(', ')});
        }
    }
} catch (error) {
    rows.splice(0, rows.length, ...cases.map(test => ({...test, status:'ungradable', stage:'load', reason:String(error.message)})));
}
process.stdout.write(JSON.stringify({sources, rows}));

// Report reads outside the fixture explicitly. Await probes the optional "then" property.
function checkedFixture(value, label) {
    return new Proxy(value, {get(target, key, receiver) {
        if (typeof key === 'string' && key !== 'then' && !(key in target)) {
            throw Error('Unobserved fixture field: ' + label + '.' + key);
        }
        return Reflect.get(target, key, receiver);
    }});
}
