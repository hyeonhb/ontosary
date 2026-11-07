// Controlled fixtures and in-memory mutations; no original corpus code is executed.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import assert from 'node:assert/strict';
import { gunzipSync } from 'node:zlib';
import { scan } from '../../../dist/core/index.js';
import { evaluateLabel as v1 } from '../evaluate-labels.mjs';
import { evaluateLabel as v2 } from './evaluate-labels.mjs';
import { cacheRoot, inputRoot, readJson, manifest, verifySources } from '../common.mjs';
for (const corpus of manifest.corpora) verifySources(corpus);
const oldLabels = readJson(path.join(inputRoot, 'labels.json')).labels;
const newLabels = readJson(path.join(inputRoot, 'v2/labels.json')).labels;
const mutations = [];
for (const [id, file, change] of [
  ['date-fns-10', 'date-fns-weekday', f => { f.types.find(t => t.name === 'DateArg').type = 'never'; }],
  ['p-queue-02', 'p-queue-priority-queue', f => { f.functions.find(f => f.name === 'lowerBound').parameters.find(p => p.name === 'array').type = 'number'; }],
]) {
  const facts = JSON.parse(gunzipSync(fs.readFileSync(path.join(inputRoot, `results/2026-11-07/${file}-scan.json.gz`))));
  assert.deepEqual(facts.diagnostics, []);
  const before = oldLabels.find(l => l.id === id), after = newLabels.find(l => l.id === id);
  const options = { readSource: file => fs.readFileSync(path.join(cacheRoot, after.corpus, file), 'utf8') };
  const original = v2(after, facts, options);
  assert.equal(original.status, 'correct');
  change(facts);
  const oldResult = v1(before, facts), newResult = v2(after, facts, options);
  assert.equal(oldResult.status, 'correct');
  assert.equal(newResult.status, 'mismatch');
  mutations.push({ id, original, oldResult, newResult });
}
const source = 'export function unused() { return true; }\nexport function recursive(): boolean { return recursive(); }\n';
const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ontosary-contract-probe-'));
const sourceLocation = anchor => {
  const offset = source.indexOf(anchor);
  assert.ok(offset >= 0 && source.indexOf(anchor, offset + 1) < 0);
  return { file: 'input.ts', anchor, offset, line: source.slice(0, offset).split('\n').length };
};
try {
  fs.writeFileSync(path.join(root, 'input.ts'), source);
  fs.writeFileSync(path.join(root, 'tsconfig.json'), JSON.stringify({ compilerOptions: { strict: true, types: [] }, files: ['input.ts'] }));
  const facts = scan(root);
  assert.deepEqual(facts.diagnostics, []);
  const usages = ['unused', 'recursive'].map(name => {
    const declaration = sourceLocation(`export function ${name}(`);
    const old = { id: name, kind: 'reference', name, source: declaration, target: declaration };
    const next = { ...old, contractVersion: 2, use: sourceLocation(name === 'unused' ? 'unused() {' : 'recursive();'), usageKind: 'call', unverified: [] };
    const oldResult = v1(old, facts), newResult = v2(next, facts, { readSource: () => source });
    assert.equal(oldResult.status, 'correct');
    assert.equal(newResult.status, name === 'unused' ? 'mismatch' : 'correct');
    return { name, references: facts.functions.find(f => f.name === name).references, oldResult, newResult };
  });
  console.log(JSON.stringify({ evaluatorVersion: 2, diagnostics: facts.diagnostics, mutations, usages,
    interpretation: 'Old evaluator false positives reproduced; V2 rejects mutated types and declaration-name use while preserving actual recursion. No human review implied.' }, null, 2));
} finally { fs.rmSync(root, { recursive: true, force: true }); }
