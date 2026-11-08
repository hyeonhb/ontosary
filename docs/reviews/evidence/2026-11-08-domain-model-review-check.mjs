// Independent checks of S1's frozen context and handoff contracts.
// Usage: node <this-file> <prepared Vendure root> [fresh S1 result directory]
// Upstream files are read only. The changed target below lives in a CompilerHost.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { gunzipSync } from 'node:zlib';
import assert from 'node:assert/strict';
import ts from 'typescript';
import { observeRoles } from '../../../experiments/domain-model/v1/observe.mjs';
import { validateModel } from '../../../experiments/domain-model/v1/validate.mjs';

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const root = fs.realpathSync(process.argv[2]);
const saved = path.join(repo, 'experiments/domain-model/results/2026-11-08');
const load = p => JSON.parse(p.endsWith('.gz') ? gunzipSync(fs.readFileSync(p)) : fs.readFileSync(p, 'utf8'));
const manifest = load(path.join(repo, 'experiments/domain-model/v1/manifest.json'));
const model = load(path.join(saved, 'model-after.json'));
const facts = load(path.join(saved, 'facts.json.gz'));
const fca = load(path.join(saved, 'fca.json'));
const context = load(path.join(saved, 'context.json')).context;
const readSource = file => fs.readFileSync(path.join(root, file), 'utf8');
assert.equal(validateModel(model, facts, fca.candidates, readSource).valid, true);

// Enumerate all 2^6 attribute subsets, independently of core NextClosure.
const key = a => [...a].sort().join('\n');
const closed = new Map();
for (let mask = 0; mask < 2 ** context.attributes.length; mask++) {
  const attrs = context.attributes.filter((_, i) => mask & (1 << i));
  const extent = context.objects.filter(o => attrs.every(a => context.incidence[o].includes(a)));
  const intent = context.attributes.filter(a => extent.every(o => context.incidence[o].includes(a)));
  closed.set(key(intent), { extent, intent });
}
assert.equal(closed.size, fca.formal.concepts.length);
for (const c of fca.formal.concepts) {
  const expected = closed.get(key(c.intent));
  assert.ok(expected);
  assert.equal(key(c.extent), key(expected.extent));
}
const simple = load(path.join(saved, 'simple-groups.json'));
for (const g of simple) {
  const extent = context.objects.filter(o => context.incidence[o].includes(g.attribute));
  assert.equal(key(g.extent), key(extent));
  assert.equal(key(g.intent), key(context.attributes.filter(a => extent.every(o => context.incidence[o].includes(a)))));
}
assert.ok(fca.candidates.every(c => simple.some(g => key(c.extent) === key(g.extent))));
const handoff = load(path.join(repo, 'experiments/domain-model/agent-input-manifest.json'));
const { sha } = await import('../../../experiments/domain-model/v1/observe.mjs');
for (const [file, hash] of Object.entries(handoff.providedFiles)) assert.equal(sha(fs.readFileSync(path.join(repo, 'experiments/domain-model', file))), hash);

// Follow precisely the outgoing relatedItems contract described in MODEL.md.
const byId = new Map(model.items.map(i => [i.id, i]));
const reachable = start => {
  const visited = new Set(), queue = [start];
  while (queue.length) {
    const id = queue.shift();
    if (visited.has(id)) continue;
    visited.add(id); queue.push(...byId.get(id).relatedItems);
  }
  return [...visited].sort();
};
const navigation = ['order', 'cancel-request', 'refund-request'].map(id => ({ start: id, reachable: reachable(id) }));
const expectedCancelTargets = ['dialog-submit', 'cancel-transport', 'refund-also-cancels'];
const unreachable = expectedCancelTargets.filter(id => !reachable('cancel-request').includes(id));
assert.equal(unreachable.length, expectedCancelTargets.length);

// A target declaration is an input premise of the recorded symbol-role facts.
// The handoff validator currently reads only occurrence/lexical evidence files.
const target = manifest.attributes.find(a => a.id === 'opens-modal').targets[0];
const original = readSource(target.file);
const modified = original.replace('    fromComponent<T extends Dialog<any>, R>(', '    renamedFromComponent<T extends Dialog<any>, R>(');
assert.notEqual(modified, original);
const readFiles = new Set();
const afterTargetEdit = validateModel(model, facts, fca.candidates, file => {
  readFiles.add(file);
  return file === target.file ? modified : readSource(file);
});
assert.equal(readFiles.has(target.file), false);
assert.equal(afterTargetEdit.valid, true);
const config = path.join(root, manifest.config);
const configFile = ts.readConfigFile(config, ts.sys.readFile);
const parsed = ts.parseJsonConfigFileContent(configFile.config, ts.sys, path.dirname(config), { noEmit: true }, config);
const host = ts.createCompilerHost(parsed.options);
const originalGetSourceFile = host.getSourceFile.bind(host);
host.getSourceFile = (file, languageVersion, ...rest) => path.resolve(file) === path.join(root, target.file)
  ? ts.createSourceFile(file, modified, languageVersion, true)
  : originalGetSourceFile(file, languageVersion, ...rest);
const program = ts.createProgram({ rootNames: parsed.fileNames, options: parsed.options, projectReferences: parsed.projectReferences, host });
const diagnostics = [...parsed.errors, ...ts.getPreEmitDiagnostics(program)];
// Ignore diagnostics for this narrow contrast: the observer independently detects
// that the pinned target no longer exists. The full runner is stricter still.
const changedObservation = observeRoles(program, manifest, root);
const changedRole = changedObservation.facts.filter(f => f.attribute === 'opens-modal');
assert.ok(changedRole.every(f => f.value === 'unknown'));
assert.equal(readSource(target.file), original);

let reproduction = null;
if (process.argv[3]) {
  const fresh = path.resolve(process.argv[3]);
  const files = fs.readdirSync(saved).filter(f => f !== 'timing.json').sort();
  assert.deepEqual(fs.readdirSync(fresh).filter(f => f !== 'timing.json').sort(), files);
  for (const file of files) assert.equal(sha(fs.readFileSync(path.join(saved, file))), sha(fs.readFileSync(path.join(fresh, file))), file);
  reproduction = { nonTimeFiles: files.length, byteIdentical: true, scope: 'Same prepared cache, fresh result directory; no installation reproduction' };
}

console.log(JSON.stringify({
  reviewedRevision: '4480438b462609971cac35aea61e4aa0a2a95d6f',
  reproduction,
  independentFca: { subsetsEnumerated: 2 ** context.attributes.length, formalConcepts: closed.size, candidates: fca.candidates.length, allCandidateExtentsInSimpleGroups: true },
  roleSupport: Object.fromEntries(context.attributes.map(a => [a, context.objects.filter(o => context.incidence[o].includes(a)).length])),
  handoffHashesVerified: Object.keys(handoff.providedFiles).length,
  navigation: { actual: navigation, expectedCancelTargets, unreachable, reverseLookupContract: 'Not specified by the model useContract/relatedItems traversal; consumers could manually scan inbound references.' },
  targetDependency: { file: target.file, mutation: 'Rename the pinned fromComponent declaration in memory only', validatorReadTarget: readFiles.has(target.file), validation: afterTargetEdit, freshRoleCounts: { unknown: changedRole.filter(f => f.value === 'unknown').length }, diagnostics: { count: diagnostics.length, codes: [...new Set(diagnostics.map(d => d.code))] }, originalUnchanged: true, limitation: 'Full run.mjs checks the complete prepared input and would reject this edit; validate-input.mjs does not.' },
}, null, 2));
