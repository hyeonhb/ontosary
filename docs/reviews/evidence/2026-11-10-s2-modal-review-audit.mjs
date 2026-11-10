// Independent audit; run after pnpm s2:build and the historical contract-review probe.
// node <this-file> <prepared-vendure-root> <review-output-root>
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { gunzipSync } from 'node:zlib';
import { createHash } from 'node:crypto';
import { createModal, orderLocals } from '../../../work/s2-build/evaluation/modal.js';
const [rootArg, outArg] = process.argv.slice(2);
const root = fs.realpathSync(rootArg), out = path.resolve(outArg);
const read = file => JSON.parse(fs.readFileSync(file));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const rx = createRequire(path.join(root, 'package.json'))('rxjs');
const checks = [];
for (const action of ['select', 'cancel', 'unresolved', 'twice', 'repeat-subscribe']) {
    const received = [], order = { id: 'actual-parent-order', active: false, lines: [] };
    class ActualDialog {
        select() {
            if (action === 'unresolved') return;
            this.resolveWith({ id: this.order.id, active: this.order.active });
            if (action === 'twice') this.resolveWith('second');
        }
        cancel() { this.resolveWith(undefined); }
    }
    const modal = createModal({ registrations: [{ component: ActualDialog,
        declaration: { file: 'review-owned-dialog.ts', className: 'ActualDialog' },
        create: () => Object.create(ActualDialog.prototype), userState: () => ({}) }],
        observable: subscribe => new rx.Observable(subscribe), action: action === 'cancel' ? 'cancel' : 'select', validateLocals: orderLocals });
    const stream = modal.fromComponent(ActualDialog, { locals: { order } });
    assert.equal(modal.traces[0].subscriptions, 0);
    stream.subscribe(value => received.push(value));
    if (action === 'repeat-subscribe') stream.subscribe(value => received.push(value));
    let status = 'supported';
    try { modal.assertComplete(); } catch { status = 'unsupported'; }
    assert.equal(status, ['select', 'cancel'].includes(action) ? 'supported' : 'unsupported');
    assert.deepEqual(received, action === 'cancel' ? [undefined] : action === 'unresolved' ? [] : [{ id: order.id, active: false }]);
    checks.push({ action, status, traces: modal.traces });
}
const original = 'experiments/domain-model/s2/results/2026-11-09';
const prepared = path.join(out, 'prepared'), manifest = read(path.join(prepared, 'bundle-manifest.json'));
assert.deepEqual(manifest, read(path.join(original, 'bundle-manifest.json')));
for (const entry of manifest.files) {
    assert.equal(hash(fs.readFileSync(path.join(prepared, entry.file))), entry.sha256);
    assert.equal(hash(fs.readFileSync(path.join(original, entry.file))), entry.sha256);
}
const delta = JSON.parse(gunzipSync(fs.readFileSync(path.join(out, 'independent/reference.json.gz'))));
const cli = read(path.join(out, 'independent/complete-cli.json'));
assert.equal(cli.typecheck.submissionId, delta.typecheck.submissionId);
assert.equal(cli.overall, delta.overall);
assert.equal(cli.sourceBinding, true);
assert.deepEqual(cli.behavior.cases, delta.behavior.cases);
const upstream = read('experiments/domain-model/s2/verification/2026-11-09-modal-fix/modal-upstream-source.json');
for (const entry of upstream.records) {
    const bytes = fs.readFileSync(path.join(root, entry.file));
    assert.equal(hash(bytes), entry.sha256);
    assert.equal(bytes.toString().slice(entry.offset), entry.source);
}
fs.writeFileSync(path.join(out, 'independent-audit.json'), JSON.stringify({
    actualPinnedRxJSChecks: checks, completeRootMatchesDelta: { submissionId: cli.typecheck.submissionId, allCasesRequestsAndModalTraces: true, sourceBinding: true },
    distribution: { agentFiles: manifest.files.length, manifestAndHashesUnchanged: true, baselineId: manifest.baselineId, modelId: manifest.modelId, bundleId: manifest.bundleId },
    upstreamSourceHashesAndExcerptsMatch: upstream.records.map(({file,sha256}) => ({file,sha256})),
    scope: 'Synchronous modal seam and data propagation only; no Angular lifecycle, OS isolation or agent trial',
}, null, 2) + '\n', { flag: 'wx' });
console.log('Independent RxJS / CLI / distribution / upstream checks passed');
