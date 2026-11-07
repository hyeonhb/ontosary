// Review observation only: exit 0 is not a correctness gate. Inspect matchesExpectation.
// Run from the repository root after pnpm build. Only temporary fixture files are created.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import assert from 'node:assert/strict';
const repo = process.cwd();
const { scan } = await import(pathToFileURL(path.join(repo, 'dist/core/index.js')));
const { evaluateLabel } = await import(pathToFileURL(path.join(repo, 'experiments/corpus/v2/evaluate-labels.mjs')));
const source = `export function localTypes() {
  type Box<TypeParam> = { value: TypeParam };
  interface Local { member: string }
  return true;
}
export function unused() { return true; }
export function recursive(): boolean { return recursive(); }
export function direct(value: string) { return value; }
export function nested() { const inner = () => recursive(); return inner; }
export function localValue() { const item = true; return item; }
export function typeQuery() { type Result = ReturnType<typeof recursive>; return true; }
`;
const loc = anchor => {
  const offset = source.indexOf(anchor);
  assert.ok(offset >= 0 && source.indexOf(anchor, offset + 1) === -1);
  return { file: 'input.ts', anchor, offset, line: source.slice(0, offset).split('\n').length };
};
const cases = [
  ['local-type-parameter-name', 'localTypes', 'TypeParam> =', 'TypeParam> =', 'reference', 'reject'],
  ['local-interface-property-name', 'localTypes', 'member: string', 'member: string', 'reference', 'reject'],
  ['unused-name', 'unused', 'unused() {', 'export function unused()', 'reference', 'reject'],
  ['recursive-call', 'recursive', 'recursive(); }', 'export function recursive()', 'call', 'correct'],
  ['parameter-read', 'direct', 'value; }', 'value: string', 'reference', 'correct'],
  ['nested-call', 'nested', 'recursive(); return inner;', 'export function recursive()', 'call', 'reject'],
  ['local-variable-declaration', 'localValue', 'item = true', 'item = true', 'reference', 'reject'],
  ['local-variable-read', 'localValue', 'item; }', 'item = true', 'reference', 'correct'],
  ['type-query', 'typeQuery', 'recursive>; return', 'export function recursive()', 'reference', 'reject'],
];
const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ontosary-review-v2-'));
try {
  fs.writeFileSync(path.join(root, 'input.ts'), source);
  fs.writeFileSync(path.join(root, 'tsconfig.json'), JSON.stringify({ compilerOptions: { strict: true, types: [] }, files: ['input.ts'] }));
  const facts = scan(root);
  assert.deepEqual(facts.diagnostics, []);
  const observations = cases.map(([id, name, use, target, usageKind, expected]) => {
    const label = { id, name, contractVersion: 2, kind: 'reference', source: loc(`export function ${name}(`), use: loc(use), target: loc(target), usageKind, unverified: [] };
    const result = evaluateLabel(label, facts, { readSource: () => source });
    return { id, expected, matchesExpectation: expected === 'reject' ? result.status !== 'correct' : result.status === expected, label, result };
  });
  console.log(JSON.stringify({ implementationRevision: '76712363fa6304b9bb716b4f9f50fc2c0a3780a0', source, diagnostics: facts.diagnostics, observations }, null, 2));
} finally { fs.rmSync(root, { recursive: true, force: true }); }
