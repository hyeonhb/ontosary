import fs from 'node:fs';
import path from 'node:path';
import { performance } from 'node:perf_hooks';
import { vendure, json } from './vendure-baseline.js';
import { openBaselineSession, hash } from './lib/analysis-session.js';
import { parseModel, Failure } from './lib/model.js';
import { validate } from './lib/validate.js';
import { bundle, limits, checkLimits, publish } from './lib/bundle.js';
const [root, out, repoArg] = process.argv.slice(2), repo = path.resolve(repoArg ?? '.');
if (!root || !out)
    throw new Error('Usage: prepare <prepared-vendure-root> <new-output> [repo]');
const start = performance.now();
let session: ReturnType<typeof openBaselineSession> | undefined;
try {
    const { spec, artifacts } = vendure(path.resolve(root), repo), l = limits(json(path.join(repo, 'experiments/domain-model/s2/limits.json')));
    const m = parseModel(...artifacts as [
        unknown,
        unknown,
        unknown,
        unknown
    ]);
    checkLimits(m, l);
    session = openBaselineSession(spec);
    const stages: Record<string, number> = {};
    let t = performance.now();
    session.inspectInputs();
    stages.inspectMs = performance.now() - t;
    t = performance.now();
    const ev = validate(m, session);
    stages.evidenceMs = performance.now() - t;
    t = performance.now();
    const baseline = session.seal();
    stages.sealMs = performance.now() - t;
    t = performance.now();
    const licenseDir = path.join(repo, 'experiments/public-app/results/2026-11-08/vendure/licenses');
    const licenseText = fs.readdirSync(licenseDir).filter(f => fs.statSync(path.join(licenseDir, f)).isFile()).sort().map(f => '\n' + f + '\n' + fs.readFileSync(path.join(licenseDir, f), 'utf8')).join('\n');
    const notice = fs.readFileSync(path.join(repo, 'experiments/public-app/results/2026-11-08/vendure/source-notice.json'), 'utf8') + '\n' + fs.readFileSync(path.join(repo, 'experiments/domain-model/SOURCE-NOTICE.md'), 'utf8') + licenseText;
    const b = bundle(m, ev, baseline, l, notice);
    stages.viewsMs = performance.now() - t;
    // Evaluator metadata lives outside A/B/C allowlisted data. No executable code/symlinks/imports in agent views.
    const parityGroups=new Map<string,unknown[]>();
    for(const unit of b.parity as {view:string}[]) {const key=unit.view.split('/').at(-1)!;parityGroups.set(key,[...(parityGroups.get(key)??[]),unit]);}
    for(const [name,units] of parityGroups)b.files.set('evaluator/parity/'+name,JSON.stringify(units,null,2)+'\n');
    b.files.set('evaluator/information-parity.json', JSON.stringify({ units: b.parity.length, views:[...parityGroups].map(([name,units])=>({file:'evaluator/parity/'+name,units:units.length,sha256:hash(b.files.get('evaluator/parity/'+name)!)})), humanParityReview: 'pending', semanticReview:'pending', developerReview:'see dated external review record', automaticCoverage:'bidirectional leaf inventory and document integrity, not proof of natural-language equivalence', tokenizer: null, tokens: null, reason: 'Exact model tokenizer unavailable; bytes measured, no fabricated token estimate', BBytes: [...b.files].filter(([f]) => f.startsWith('B/')).reduce((n, [, t]) => n + Buffer.byteLength(t), 0), CBytes: [...b.files].filter(([f]) => f.startsWith('C/')).reduce((n, [, t]) => n + Buffer.byteLength(t), 0) }, null, 2) + '\n');
    const plan = JSON.parse(fs.readFileSync(path.join(repo, 'experiments/domain-model/s2/evaluation/run-plan.json'), 'utf8')) as Record<string, unknown>;
    b.files.set('evaluator/run-plan.json', JSON.stringify({ ...plan, baselineId: b.baselineId, modelId: b.modelId, bundleId: b.bundleId, providedFiles: JSON.parse(b.files.get('bundle-manifest.json')!).files, sourceFingerprint: baseline.baselineId, node: process.version }, null, 2) + '\n');
    b.files.set('evaluator/selection.json', JSON.stringify(b.selection, null, 2) + '\n');
    b.files.set('evaluator/readiness.json', JSON.stringify({ implementation: 'prepared-for-review', baseline: 'verified', BCautomaticCoverage: 'leaf inventory and C text integrity; semantic review separate', humanParityReview: 'pending', semanticReview: 'pending', oracleFidelityReview: 'pending', isolation: 'not established by packaging; see separate execution evidence', runConditions: 'preparation-only', trialAuthorized:false, results:null, readyForTrial: false, agentUtility: null }, null, 2) + '\n');
    const audit = { ...session.metrics, stages, wallTimeMs: performance.now() - start, rssBytes: process.memoryUsage().rss, memoryScope: 'Process RSS at end; not peak', inputEntries: spec.inputs.length, originalInventoryEntries: 4735, programEntries: spec.program?.length, artifactHashes: spec.artifacts, ids: { baselineId: b.baselineId, modelId: b.modelId, bundleId: b.bundleId }, node: process.version };
    // Paths/absolute roots are excluded from published metadata.
    b.files.set('evaluator/timing.json', JSON.stringify({ ...audit, artifactHashes: spec.artifacts.map(f => ({ name: path.basename(f.file), sha256: f.sha256 })) }, null, 2) + '\n');
    publish(out, b.files, l);
    console.log(JSON.stringify({ status: 'prepared', ...audit.ids, programs: session.metrics.programs, readyForTrial: false }));
}
catch (e) {
    console.error(JSON.stringify({ status: 'rejected', code: e instanceof Failure ? e.code : 'Preparation', field: e instanceof Failure ? e.field : 'input', message: e instanceof Error ? e.message : String(e) }));
    process.exitCode = 1;
}
finally {
    session?.dispose();
}
