// A real collected fixture must still be refused by every existing live entry.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
const root = path.resolve(process.argv[2]);
const receipt = JSON.parse(fs.readFileSync(path.join(root, 'fixture.json'), 'utf8'));
assert.equal(receipt.fixtureOnly, true);
assert.equal(receipt.validSubmission, false);
const runtime = await import(pathToFileURL(path.resolve('work/s2-build/trial/runtime.js')));
const gate = await import(pathToFileURL(path.resolve('work/s2-build/trial/snapshot-gate.js')));
assert.throws(() => runtime.snapshot(receipt), /production collection blocked/);
assert.throws(() => gate.checkedSnapshot(root), /production evaluation blocked/);
for (const [entry, args, message] of [
    ['evaluate-snapshot.js', [root], 'production evaluation blocked'],
    ['freeze.js', ['run'], 'not authorized'],
]) {
    const result = spawnSync(process.execPath, ['work/s2-build/trial/' + entry, ...args], { encoding: 'utf8', timeout: 5000 });
    assert.notEqual(result.status, 0);
    assert.equal(result.error, undefined);
    assert.ok(result.stderr.includes(message));
    console.log(JSON.stringify({ entry, exitCode: result.status, stdout: result.stdout, stderr: result.stderr }));
}
console.log(JSON.stringify({ fixtureRun: receipt.termination.runId, collection: 'refused', productionEvaluation: 'refused', liveDispatch: 'refused', R11: 'unresolved', providerCalls: 0, trialRuns: 0 }));
