import { performance } from 'node:perf_hooks';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import { hash } from '../lib/analysis-session.js';
const [rootArg, outArg] = process.argv.slice(2);
if (!rootArg || !outArg)
    throw Error('Usage: oracle-check <prepared-root> <new-evidence-dir>');
const root = path.resolve(rootArg), out = path.resolve(outArg);
if (fs.existsSync(out))
    throw Error('Existing output');
fs.mkdirSync(out, { recursive: true });
const base = 'packages/admin-ui/src/lib/', paths = { detail: base + 'order/src/components/order-detail/order-detail.component.ts', cancel: base + 'order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts', refund: base + 'order/src/components/refund-order-dialog/refund-order-dialog.component.ts', service: base + 'core/src/data/providers/order-data.service.ts' };
const originals = Object.fromEntries(Object.entries(paths).map(([k, f]) => [k, fs.readFileSync(path.join(root, f), 'utf8')]));
const replace = (s: string, from: string, to: string) => { if (s.split(from).length !== 2)
    throw Error('Nonunique patch anchor'); return s.replace(from, to); };
const summaries: unknown[] = [];
const started = performance.now();
for (const variant of ['baseline', 'reference', 'direct-only', 'no-trim', 'force-cancel', 'dismiss-request', 'continue-after-failure', 'omit-followup-refund']) {
    const caseStart = performance.now();
    const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'ontosary-oracle-'));
    try {
        const texts = { ...originals };
        if (variant !== 'baseline') {
            const guard = "\n        if (typeof this.reason !== 'string' || !this.reason.trim()) { this.resolveWith(); return; }\n        this.reason = this.reason.trim();";
            texts.cancel = replace(texts.cancel!, 'select() {', 'select() {' + guard);
            if (variant !== 'direct-only') {
                texts.refund = replace(texts.refund!, 'select() {', 'select() {' + guard);
                texts.service = "import { of } from 'rxjs';\n" + replace(texts.service!, 'cancelOrder(input: Codegen.CancelOrderInput) {', "cancelOrder(input: Codegen.CancelOrderInput) {\n        if (typeof input.reason !== 'string' || !input.reason.trim()) { return of(undefined); }\n        input = { ...input, reason: input.reason.trim() };");
            }
            if (variant === 'no-trim')
                for (const key of ['cancel', 'refund', 'service'])
                    texts[key] = texts[key]!.replaceAll('.reason.trim()', '.reason');
            if (variant === 'force-cancel')
                texts.detail = replace(texts.detail!, 'if (input.cancel.lines?.length) {', 'if (input.cancel) {');
            if (variant === 'dismiss-request')
                texts.cancel = replace(texts.cancel!, 'cancel() {\n        this.resolveWith();', 'cancel() {\n        this.select();');
            if (variant === 'omit-followup-refund')
                texts.detail = replace(texts.detail!, 'if (input.refunds.length) {', 'if (input.refunds.length && !input.cancel.lines?.length) {');
            if (variant === 'continue-after-failure')
                texts.detail = replace(texts.detail!, 'this.notificationService.error(result.message);\n                                        return undefined;', 'this.notificationService.error(result.message);\n                                        return input;');
        }
        for (const [key, file] of Object.entries(paths)) {
            const dest = path.join(tmp, file);
            fs.mkdirSync(path.dirname(dest), { recursive: true });
            fs.writeFileSync(dest, texts[key]!);
        }
        const report = path.join(out, variant + '.json');
        execFileSync(process.execPath, [fileURLToPath(new URL('./run.js', import.meta.url)), tmp, root, report], { stdio: 'pipe' });
        const parsed: unknown = JSON.parse(fs.readFileSync(report, 'utf8'));
        if (!parsed || typeof parsed !== 'object')
            throw Error('Report missing');
        const r = parsed as {
            preservationPassed: number;
            draftPassed: number;
            cases: {
                name: string;
                pass: boolean;
            }[];
        };
        if (variant === 'baseline' && (r.preservationPassed !== 6 || r.draftPassed === 18))
            throw Error('Baseline oracle failed its calibration');
        if (variant === 'reference' && (r.preservationPassed !== 6 || r.draftPassed !== 18))
            throw Error('Reference must pass all draft cases');
        if (!['baseline', 'reference'].includes(variant) && r.cases.every(c => c.pass))
            throw Error('Defect mutant escaped');
        summaries.push({ variant, wallTimeMs: performance.now() - caseStart, preservationPassed: r.preservationPassed, draftPassed: r.draftPassed, failedCases: r.cases.filter(c => !c.pass).map(c => c.name) });
        fs.writeFileSync(path.join(out, variant + '-patches.json'), JSON.stringify(Object.entries(paths).map(([key, file]) => ({ file, baselineHash: hash(originals[key]!), submittedHash: hash(texts[key]!), patch: variant === 'baseline' ? null : { before: originals[key], after: texts[key] } })), null, 2) + '\n');
    }
    finally {
        fs.rmSync(tmp, { recursive: true, force: true });
    }
}
fs.writeFileSync(path.join(out, 'summary.json'), JSON.stringify({ wallTimeMs: performance.now() - started, policyStatus: 'draft-not-approved', humanFidelityReview: 'pending', scope: 'Temporary submitted source clones; actual cache untouched; reference changes are evaluator-only, not agent trials', summaries }, null, 2) + '\n');
console.log(JSON.stringify(summaries));
