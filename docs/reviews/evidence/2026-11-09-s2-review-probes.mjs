// Independent review probes. Run after `pnpm s2:build`; never writes the Vendure cache.
// node <this-file> <prepared-vendure-root> <new-output-dir>
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { gunzipSync } from 'node:zlib';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import ts from 'typescript';

const [rootArg, outArg] = process.argv.slice(2);
if (!rootArg || !outArg) throw Error('Expected prepared root and new output directory');
const root = fs.realpathSync(rootArg), out = path.resolve(outArg), repo = process.cwd();
if (fs.existsSync(out)) throw Error('Output exists');
fs.mkdirSync(out, { recursive: true });
const hash = text => createHash('sha256').update(text).digest('hex');
const patches = JSON.parse(gunzipSync(fs.readFileSync('experiments/domain-model/s2/verification/2026-11-08/reference-patches.json.gz')));
const baseline = Object.fromEntries(patches.map(p => [p.file, fs.readFileSync(path.join(root, p.file), 'utf8')]));
const reference = Object.fromEntries(patches.map(p => [p.file, p.patch.after]));
for (const p of patches) if (hash(baseline[p.file]) !== p.baselineHash) throw Error('Baseline mismatch');
const service = patches.find(p => p.file.endsWith('order-data.service.ts')).file;
const replace = (s, a, b) => { if (s.split(a).length !== 2) throw Error('Nonunique patch anchor'); return s.replace(a, b); };
const runner = path.resolve('work/s2-build/evaluation/run.js');
const probeRunner = path.join(path.dirname(runner), 'independent-refund-only-review.js');
if (fs.existsSync(probeRunner)) throw Error('Probe runner exists');
fs.writeFileSync(probeRunner, replace(fs.readFileSync(runner, 'utf8'), "scenario('refund-only', 'normal', 'refund-only', 'preservation');", "scenario('refund-only', 'normal', 'refund-only', 'preservation');\nscenario('refund-only-whitespace', '   ', 'refund-only', 'preservation');"));
const summaries = [];
try {
    for (const variant of ['baseline', 'reference', 'wrong-order-id', 'wrong-refund-payment-amount']) {
        const texts = { ...(variant === 'baseline' ? baseline : reference) };
        if (variant === 'wrong-order-id') texts[service] = replace(texts[service], 'input = { ...input, reason: input.reason.trim() };', "input = { ...input, reason: input.reason.trim(), orderId: 'wrong-order' };");
        if (variant === 'wrong-refund-payment-amount') texts[service] = replace(texts[service], 'refundOrder(input: Codegen.RefundOrderInput) {', "refundOrder(input: Codegen.RefundOrderInput) {\n        input = { ...input, paymentId: 'wrong-payment', amount: 999999 };");
        const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'ontosary-s2-independent-'));
        try {
            for (const [file, text] of Object.entries(texts)) {
                fs.mkdirSync(path.dirname(path.join(tmp, file)), { recursive: true });
                fs.writeFileSync(path.join(tmp, file), text);
            }
            for (const [name, executable] of [['original', runner], ['refund-only-extension', probeRunner]]) {
                const file = path.join(out, `${variant}-${name}.json`);
                execFileSync(process.execPath, [executable, tmp, root, file], { stdio: 'pipe' });
                const r = JSON.parse(fs.readFileSync(file));
                summaries.push({ variant, evaluator: name, preservation: `${r.preservationPassed}/${r.preservationTotal}`, draft: `${r.draftPassed}/${r.draftTotal}`, failedCases: r.cases.filter(c => !c.pass).map(c => c.name), observedCancel: r.cases.find(c => c.name === 'direct-reason-0')?.calls, observedRefund: r.cases.find(c => c.name === 'refund-only')?.calls });
            }
        } finally { fs.rmSync(tmp, { recursive: true, force: true }); }
    }
} finally { fs.unlinkSync(probeRunner); }

// Use the same prepared scoped Program, with read-only in-memory source overrides.
const config = path.join(root, 'packages/admin-ui/ontosary.scope.json');
const raw = ts.readConfigFile(config, ts.sys.readFile);
const parsed = ts.parseJsonConfigFileContent(raw.config, ts.sys, path.dirname(config), { noEmit: true });
if (raw.error || parsed.errors.length) throw Error('Config failed');
const diagnostics = [];
for (const [variant, texts] of [['baseline', baseline], ['reference', reference]]) {
    const overrides = new Map(Object.entries(texts).map(([p, text]) => [fs.realpathSync(path.join(root, p)), text]));
    const host = ts.createCompilerHost(parsed.options), originalRead = host.readFile.bind(host);
    host.readFile = file => { let key = file; try { key = fs.realpathSync(file); } catch {} return overrides.get(key) ?? originalRead(file); };
    const program = ts.createProgram({ rootNames: parsed.fileNames, options: parsed.options, projectReferences: parsed.projectReferences, host });
    const ds = ts.getPreEmitDiagnostics(program).map(d => ({ code: d.code, file: d.file ? path.relative(root, d.file.fileName) : null, line: d.file && d.start !== undefined ? d.file.getLineAndCharacterOfPosition(d.start).line + 1 : null, message: ts.flattenDiagnosticMessageText(d.messageText, '\n') }));
    diagnostics.push({ variant, programFiles: program.getSourceFiles().length, overridesVerified: [...overrides].every(([file, text]) => program.getSourceFile(file)?.text === text), diagnosticCount: ds.length, diagnostics: ds });
}
const result = { reviewedCommit: execFileSync('git', ['rev-parse', 'HEAD'], { cwd: repo, encoding: 'utf8' }).trim(), node: process.version, typescript: ts.version, scope: 'Independent oracle counterexamples and read-only submitted-reference type checking; no agent trial', summaries, diagnostics };
fs.writeFileSync(path.join(out, 'summary.json'), JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify(result, null, 2));
