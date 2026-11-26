import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { observe } from './observe.mjs';
import { fix, parent, loadControls } from './load-controls.mjs';

const repository = process.argv[2];
assert.ok(repository, 'pass the path to the upstream Vendure git repository');
assert.equal(execFileSync('git', ['-C', repository, 'rev-parse', fix + '^'], {encoding:'utf8'}).trim(), parent);
const cases = JSON.parse(readFileSync(new URL('cases.json', import.meta.url)));

const expected = {
    original:[false,true,false,true,true,true],
    'always-gross':[true,false,true,false,true,true],
    upstream:[true,true,true,true,true,true],
};
const controls = {};
for (const [variant, pass] of Object.entries(expected)) {
    const product = loadControls(repository, variant);
    // Keep the published candidate-selection record in its original format.
    controls[variant] = await Promise.all(cases.map(async test => {
        const {orderSaves, shippingSaveObserved, allCancelled, mismatches, ...row} = await observe(product, test);
        return row;
    }));
    assert.deepEqual(controls[variant].map(row => row.passed), pass);
}
process.stdout.write(JSON.stringify({parent,fix,participantCalls:0,controls}, null, 2) + '\n');
