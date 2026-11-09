// Independent S2 v2 review. Does not modify the pinned Vendure environment.
// After pnpm s2:build: node <this-file> <prepared-root> <new-output-dir>
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import { gzipSync } from 'node:zlib';
import { openEnvironment, evaluateSubmission } from '../../../work/s2-build/evaluation/evaluate.js';
import { deltaSubmission, sourceView } from '../../../work/s2-build/evaluation/submission.js';
import { variantDelta, patch } from '../../../work/s2-build/evaluation/variants.js';
import { executor, invoke } from '../../../work/s2-build/evaluation/execute.js';
import { mappings, compareCalls } from '../../../work/s2-build/evaluation/behavior.js';
import { hash } from '../../../work/s2-build/lib/analysis-session.js';

const [rootArg, outArg] = process.argv.slice(2);
if (!rootArg || !outArg) throw Error('Expected prepared root and new output directory');
const root = fs.realpathSync(rootArg), out = path.resolve(outArg), repo = process.cwd();
if (fs.existsSync(out)) throw Error('Output exists');
fs.mkdirSync(out, { recursive: true });
const env = openEnvironment(root, repo), require = createRequire(path.join(root, 'package.json')), rx = require('rxjs');
const bindings = { marker: x => x, _: x => x, gql: () => '', ORDER_DETAIL_FRAGMENT: '', CANCEL_ORDER: 'cancel', REFUND_ORDER: 'refund', summate: (rows, k) => rows.reduce((s, r) => s + r[k], 0) };
const summaries = [];
let referenceSources, referenceId;
for (const variant of ['reference', 'wrong-modal-order', 'wrong-modal-active']) {
    const delta = variantDelta('reference', env.baseline, repo);
    if (variant !== 'reference') {
        const file = mappings[0].file, text = env.baseline.get(file).toString();
        const start = text.indexOf('    private cancelOrder(order: OrderDetailFragment) {');
        const end = text.indexOf('    private refundOrder(', start);
        if (start < 0 || end < start) throw Error('Missing parent method');
        const changedLocal = variant === 'wrong-modal-order' ? "order: { ...order, id: 'wrong-modal-order' }," : 'order: { ...order, active: true },';
        delta[file] = text.slice(0, start) + patch(text.slice(start, end), '                    order,', '                    ' + changedLocal) + text.slice(end);
    }
    const sources = deltaSubmission(env.baseline, delta), result = await evaluateSubmission(env, sources, 'explicit-baseline-delta');
    fs.writeFileSync(path.join(out, variant + '.json.gz'), gzipSync(JSON.stringify(result, null, 2) + '\n'));
    if (variant === 'reference') { referenceSources = sources; referenceId = result.typecheck.submissionId; }

    // Execute the same submitted methods, forwarding actual fromComponent locals.
    // Only UI construction/user action and external service effects are supplied here.
    const executed = {}, engine = executor(root, mappings, bindings, root, sourceView(sources, (file, h) => { executed[file] = h; }));
    const calls = [], modalCalls = [], service = engine.instance('OrderDataService');
    service.baseDataService = { mutate: (kind, args) => { calls.push(structuredClone({ kind, input: args.input })); return rx.of({ cancelOrder: { __typename: 'Order' } }); } };
    service.getOrder = () => ({ single$: rx.of(undefined) });
    const parent = engine.instance('OrderDetailComponent');
    Object.assign(parent, {
        id: 'o-one', dataService: { order: service }, notificationService: { success: () => {}, error: () => {} }, fetchHistory: { next: () => {} },
        modalService: { fromComponent: (component, options) => {
            modalCalls.push({ className: component.name, locals: structuredClone(options.locals) });
            const dialog = Object.create(component.prototype); let returned;
            Object.assign(dialog, { ...options.locals, reason: 'normal', cancelAll: true, lineQuantities: { 'l-one': 1, 'l-extra': 2, excluded: 0, negative: -1 }, resolveWith: v => { returned = v; } });
            invoke(dialog, 'select');
            return rx.of(returned);
        } },
    });
    invoke(parent, 'cancelOrRefund', { id: 'o-one', active: false, payments: [], state: 'PaymentSettled', lines: [{ id: 'l-one', quantity: 2, orderPlacedQuantity: 2 }, { id: 'l-extra', quantity: 2, orderPlacedQuantity: 2 }] });
    const expected = [{ kind: 'cancel', input: { orderId: 'o-one', reason: 'normal', lines: [{ orderLineId: 'l-one', quantity: 1 }, { orderLineId: 'l-extra', quantity: 2 }], cancelShipping: true } }];
    const connected = compareCalls(calls, expected);
    summaries.push({ variant, typecheck: result.typecheck.status, diagnosticCount: result.typecheck.diagnostics.length, behavior: result.behavior.status, sourceBinding: result.sourceBinding, overall: result.overall, preservation: result.behavior.preservation, draft: result.behavior.draft, submissionId: result.typecheck.submissionId, modalCalls, connected, connectedExecutedFiles: executed, sourceHashesMatch: Object.entries(executed).every(([f, h]) => result.typecheck.checkedFiles.some(row => row.file === f && row.sha256 === h)), originalOracleDirect: result.behavior.cases.find(c => c.name === 'o-one/direct-reason-0'), mutation: variant === 'reference' ? null : { file: mappings[0].file, before: 'locals: { order }', after: variant === 'wrong-modal-order' ? "locals: { order: { ...order, id: 'wrong-modal-order' } }" : 'locals: { order: { ...order, active: true } }', baselineHash: hash(env.baseline.get(mappings[0].file)), submittedHash: hash(sources.get(mappings[0].file)) } });
}

// Exercise the documented complete-root CLI, including its logical /tmp path input.
const complete = path.join(out, 'complete-source');
try {
    for (const [file, bytes] of referenceSources) { const dest = path.join(complete, file); fs.mkdirSync(path.dirname(dest), { recursive: true }); fs.writeFileSync(dest, bytes); }
    execFileSync(process.execPath, ['work/s2-build/evaluation/run.js', complete, rootArg, path.join(out, 'complete-cli.json')], { stdio: 'pipe' });
} finally { fs.rmSync(complete, { recursive: true, force: true }); }
const cli = JSON.parse(fs.readFileSync(path.join(out, 'complete-cli.json')));
env.assertUnchanged();
const summary = { reviewedCommit: execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim(), scope: 'Actual submitted methods with actual modal component/locals forwarding; no Angular rendering, network or agent trial', summaries, completeCLI: { overall: cli.overall, typecheck: cli.typecheck.status, behavior: cli.behavior.status, sourceBinding: cli.sourceBinding, sameSubmissionAsDelta: cli.typecheck.submissionId === referenceId }, environmentRecheck: 'passed' };
fs.writeFileSync(path.join(out, 'summary.json'), JSON.stringify(summary, null, 2) + '\n');
console.log(JSON.stringify(summary, null, 2));
