import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { gzipSync } from 'node:zlib';
import { performance } from 'node:perf_hooks';
import ts from 'typescript';
import { scan, buildContext, discoverConcepts, selectFunction, compare } from '../../../dist/core/index.js';
import { manifest, repoRoot, inputRoot, cacheRoot, readJson, digest, verifySources, locate, serializeObservation } from '../common.mjs';
import { evaluateLabel, evaluatorVersion } from './evaluate-labels.mjs';
const outputArg = process.argv[2];
if (!outputArg) throw new Error('Usage: node experiments/corpus/v3/run.mjs <new-output-directory>; existing evidence is never overwritten.');
const output = path.resolve(outputArg);
if (fs.existsSync(output)) throw new Error(`Output already exists: ${output}`);
const labels = readJson(path.join(inputRoot, 'v2/labels.json'));
const tasks = readJson(path.join(inputRoot, 'tasks.json'));
const fingerprintFiles = ['src/core/analyzer.ts', 'src/core/logic.ts', 'src/core/fca.ts', 'src/core/model.ts', 'src/core/index.ts', 'pnpm-lock.yaml'];
const pinned = readJson(path.join(inputRoot, 'analyzer-fingerprints.json'));
for (const file of fingerprintFiles) assert.equal(digest(fs.readFileSync(path.join(repoRoot, file))), pinned[file], `Analyzer changed: ${file}; create a new versioned experiment.`);
assert.equal(labels.schemaVersion, 2);
assert.equal(labels.evaluatorVersion, 2);
assert.ok(labels.labels.every(l => l.contractVersion === 2));
assert.equal(labels.labels.length, 24);
assert.equal(new Set(labels.labels.map(l => l.id)).size, 24);
// Audit V2 anchors against unchanged source before this run; V1 results were already known.
for (const corpus of manifest.corpora) {
  const root = verifySources(corpus);
  for (const scope of corpus.scopes) if (scope.content) assert.equal(fs.readFileSync(path.join(root, scope.config), 'utf8'), JSON.stringify(scope.content, null, 2) + '\n');
  for (const label of labels.labels.filter(l => l.corpus === corpus.id)) {
    for (const location of [label.source, label.target, label.use, label.other, label.parameterSource, label.conditionSource].filter(Boolean)) locate(root, location);
  }
}
fs.mkdirSync(output, { recursive: true });
const write = (name, value, compressed = false) => fs.writeFileSync(path.join(output, name), compressed ? gzipSync(serializeObservation(value, 0)) : serializeObservation(value), { flag: 'wx' });
const counts = values => Object.fromEntries([...new Set(values)].sort().map(key => [key, values.filter(v => v === key).length]));
const scans = new Map(), summary = [], timings = [];
for (const corpus of manifest.corpora) {
  const root = path.join(cacheRoot, corpus.id);
  for (const scope of corpus.scopes) {
    const key = `${corpus.id}/${scope.id}`, prefix = `${corpus.id}-${scope.id}`;
    let facts;
    const start = performance.now();
    try { facts = scan(path.join(root, scope.config)); }
    catch (error) {
      const failure = { status: 'scan-failed', message: error.message };
      write(`${prefix}-failure.json`, failure);
      summary.push({ corpus: corpus.id, scope: scope.id, ...failure });
      timings.push({ key, scanMs: Math.round(performance.now() - start), fcaMs: null });
      continue;
    }
    const scanMs = Math.round(performance.now() - start);
    scans.set(key, facts);
    write(`${prefix}-scan.json.gz`, facts, true);
    const errors = facts.diagnostics.filter(d => d.category === 'Error');
    const supported = facts.functions.filter(f => f.predicate.status === 'supported').length;
    const conditions = facts.functions.flatMap(f => f.conditions);
    const row = { corpus: corpus.id, scope: scope.id, status: errors.length ? 'compiler-errors' : 'scanned',
      analyzedFiles: facts.files, analyzedFileCount: facts.files.length, types: facts.types.length,
      predicates: { supported, totalFunctions: facts.functions.length },
      conditions: { supported: conditions.filter(c => c.normalization.status === 'supported').length, totalExtracted: conditions.length },
      diagnosticsByCategory: counts(facts.diagnostics.map(d => d.category)),
      omissions: { records: facts.omissions.length, byReason: counts(facts.omissions.map(o => o.reason)) },
      unsupportedPredicatesByReason: counts(facts.functions.filter(f => f.predicate.status === 'unsupported').map(f => f.predicate.reason)) };
    let fcaMs = null;
    if (errors.length) {
      row.fca = { status: 'skipped-compiler-errors' };
      row.simpleGroups = { status: 'skipped-compiler-errors' };
    } else {
      const context = buildContext(facts);
      const attributes = new Map();
      for (const fn of facts.functions) for (const attr of new Set([...fn.referencedTypes.map(t => `type:${t.id}`), ...fn.properties.map(p => `property:${p.id}`)])) {
        if (!attributes.has(attr)) attributes.set(attr, []);
        attributes.get(attr).push(fn.id);
      }
      const simpleGroups = [...attributes].filter(([, extent]) => extent.length >= 2).sort(([a], [b]) => a.localeCompare(b)).map(([attribute, extent]) => ({ attribute, extent: extent.sort(), reviewStatus: 'unreviewed', evidence: extent.map(id => facts.functions.find(f => f.id === id).evidence) }));
      write(`${prefix}-simple-groups.json.gz`, simpleGroups, true);
      row.simpleGroups = { count: simpleGroups.length, method: 'One shared type/property per group, >=2 functions; no ranking or semantic quality score.' };
      const fcaStart = performance.now();
      try {
        const result = discoverConcepts(facts);
        write(`${prefix}-concepts.json.gz`, result, true);
        row.fca = { status: 'computed', objects: context.objects.length, attributes: context.attributes.length,
          limits: result.limits, concepts: result.concepts.length, candidates: result.candidates.length, relations: result.relations.length, truncated: result.truncated };
      } catch (error) {
        if (!error.message.startsWith('Formal context exceeds limits:')) throw error;
        row.fca = { status: 'limit-exceeded', objects: context.objects.length, attributes: context.attributes.length, message: error.message };
        write(`${prefix}-concepts-failure.json`, row.fca);
      }
      fcaMs = Math.round(performance.now() - fcaStart);
    }
    summary.push(row);
    timings.push({ key, scanMs, fcaMs });
  }
}
const adjudications = labels.labels.map(label => {
  const corpus = manifest.corpora.find(c => c.id === label.corpus);
  const facts = scans.get(`${corpus.id}/${corpus.labelScope}`);
  return { ...label, sourceUrl: `${corpus.repository}/blob/${corpus.revision}/${label.source.file}#L${label.source.line}`,
    scope: corpus.labelScope, result: evaluateLabel(label, facts, { readSource: file => fs.readFileSync(path.join(cacheRoot, corpus.id, file), 'utf8') }) };
});
const comparisons = tasks.comparisons.map(task => {
  const facts = scans.get(`${task.corpus}/${task.scope}`);
  if (!facts || facts.diagnostics.some(d => d.category === 'Error')) return { ...task, status: 'indeterminate', reason: 'Scan failed or compiler errors.' };
  const a = selectFunction(facts, task.left), b = selectFunction(facts, task.right);
  return { ...task, leftEvidence: a.evidence, rightEvidence: b.evidence, result: compare(a.predicate, b.predicate, { sameInput: task.sameInput }) };
});
const report = { schemaVersion: 2, evaluatorVersion, labelVersion: labels.schemaVersion, evaluationBaseRevision: 'c5676e42ff98c0f1b6b29e1521695d9c503e676a', analyzerBaseRevision: manifest.analyzerBaseRevision,
  environment: { node: process.version, typescript: ts.version, nodeTypes: readJson(path.join(repoRoot, 'node_modules/@types/node/package.json')).version },
  fingerprints: { ...pinned, ...Object.fromEntries(['manifest.json', 'labels.json', 'tasks.json', 'run.mjs', 'evaluate-labels.mjs', 'common.mjs', 'prepare.mjs', 'v2/labels.json', 'v2/run.mjs', 'v2/evaluate-labels.mjs', 'v2/check-mutations.mjs', 'v3/run.mjs', 'v3/evaluate-labels.mjs', 'v3/role-cases.mjs', 'v3/check-roles.mjs'].map(f => [f, digest(fs.readFileSync(path.join(inputRoot, f)))])), ...Object.fromEntries(['analyzer.js', 'logic.js', 'fca.js'].map(f => [`dist/core/${f}`, digest(fs.readFileSync(path.join(repoRoot, 'dist/core', f)))])) },
  scopes: summary, labels: { total: adjudications.length, byOutcome: counts(adjudications.map(a => a.result.status)), humanReviewed: 0 },
  preselectedComparisons: { supported: comparisons.filter(c => ['Equivalent', 'Implies', 'Different'].includes(c.result?.status)).length, totalPairs: comparisons.length },
  interpretation: 'Source facts and support observations only. No business meaning approval, human timing or search/LSP superiority measured. No upstream code executed.',
  approvedKnowledge: [], humanReviewTimeMs: null };
write('comparisons.json', { comparisons, skipped: tasks.skippedComparisons });
const legacyRoot = path.join(inputRoot, 'results/2026-11-08-v2');
const previousLabels = readJson(path.join(legacyRoot, 'labels.json'));
const transitions = adjudications.map(a => {
  const previous = previousLabels.find(p => p.id === a.id);
  assert.ok(previous, `Missing predecessor ${a.id}`);
  return { id: a.id, before: { evaluatorVersion: 2, claim: previous.claim, status: previous.result.status },
    after: { evaluatorVersion, claim: a.claim, status: a.result.status, checks: a.result.checks, unverified: a.result.unverified },
    changeReason: 'Unchanged V2 claim/anchors/expectations. V3 corrects type-only source-use classification.', comparableAsAccuracyDelta: false };
});
write('label-changes.json', { previousLabelsSha256: digest(fs.readFileSync(path.join(legacyRoot, 'labels.json'))),
  note: 'Label contracts are unchanged. Equal corpus totals do not erase the reproduced V2 role errors; this is not a product accuracy score.', transitions });
const unchanged = fs.readdirSync(legacyRoot).filter(f => !['summary.json', 'labels.json', 'review.md', 'timings.json', 'analysis-unchanged.json', 'label-changes.json'].includes(f)).sort();
for (const file of unchanged) assert.deepEqual(fs.readFileSync(path.join(output, file)), fs.readFileSync(path.join(legacyRoot, file)), `Core observation changed: ${file}`);
write('analysis-unchanged.json', { comparedFiles: unchanged.length, hashes: Object.fromEntries(unchanged.map(f => [f, digest(fs.readFileSync(path.join(output, f)))])),
  note: 'Core scan/FCA/simple groups/comparisons/failures unchanged from V2. This is not a semantic utility evaluation.' });
write('summary.json', report);
write('labels.json', adjudications);
const review = [
  '# Corpus V3 review worksheet — 2026-11-08', '',
  'Unchanged agent-authored V2 label contracts, evaluated by V3 after the type-context review. Correct applies only to the explicit claim; unverified context and human decisions remain pending.', '',
  '| Label | Source / use / target | Checked claim | Observation | Unverified context | Human decision |',
  '| --- | --- | --- | --- | --- | --- |',
  ...adjudications.map(a => {
    const corpus = manifest.corpora.find(c => c.id === a.corpus);
    const link = (name, loc) => `[${name}:${loc.line}](${corpus.repository}/blob/${corpus.revision}/${loc.file}#L${loc.line})`;
    const locations = [link('source', a.source), ...(a.use ? [link('use', a.use), link('target', a.target)] : [])].join(' · ');
    const escape = value => value.replaceAll('|', '\\|');
    return `| ${a.id} | ${locations} | ${escape(a.claim)} | ${a.result.status} | ${escape(a.unverified.join(' ')) || 'none'} | pending |`;
  }), '',
  'Review the unchanged source first, then linked evidence in labels.json. Correct an agent label separately from an extraction defect; keep original observations.', '',
  '## User tasks (not yet performed)', '',
  '1. Independently review these code-fact contracts against source. This measurement-quality review is not the product value experiment.',
  '2. Separately prepare one real business-application concept-finding task with fixed ground-truth evidence, participants, order/learning controls and human timing; compare search/LSP and simple groups with FCA.',
  '3. The two library comparisons remain Unsupported. No human trial or exploration-time improvement is claimed here.', '',
  'Decode *-concepts.json.gz and *-simple-groups.json.gz using the README command. All candidates remain unreviewed; do not interpret RunFunction, Date or Array sharing as business identity.', '',
  'Human reviewer: pending. Human elapsed time: not measured. Approved knowledge: none.', ''
].join('\n');
fs.writeFileSync(path.join(output, 'review.md'), review, { flag: 'wx' });
write('timings.json', { scopes: timings, preparation: readJson(path.join(cacheRoot, 'preparation.json')), humanReviewTimeMs: null, note: 'Wall times are single local observations, not benchmarks. Author preparation effort unmeasured.' });
console.log(JSON.stringify({ scopes: summary, labels: report.labels, comparisons: report.preselectedComparisons }, null, 2));
