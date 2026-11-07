// Compare frozen V2 with V3 using unchanged independent-review source/labels and
// adjacent source-authored fixtures. No fixture or corpus code is executed.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import { scan } from '../../../dist/core/index.js';
import { evaluateLabel as v2 } from '../v2/evaluate-labels.mjs';
import { evaluateLabel as v3 } from './evaluate-labels.mjs';
import { source, texts, cases } from './role-cases.mjs';
import { repoRoot, digest } from '../common.mjs';
const reviewPath = 'docs/reviews/evidence/2026-11-08-contract-independent-results.json';
const review = JSON.parse(fs.readFileSync(path.join(repoRoot, reviewPath), 'utf8'));
function observe(name, sources, items) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ontosary-role-comparison-'));
  try {
    for (const [file, text] of Object.entries(sources)) fs.writeFileSync(path.join(root, file), text);
    fs.writeFileSync(path.join(root, 'tsconfig.json'), JSON.stringify({ compilerOptions: { strict: true, types: [] }, include: ['*.ts'] }));
    const facts = scan(root);
    assert.deepEqual(facts.diagnostics, []);
    const observations = items.map(({ id, label, expected, result: archived }) => {
      const options = { readSource: file => sources[file] };
      const before = v2(label, facts, options), after = v3(label, facts, options);
      if (archived) assert.deepEqual(before, archived, `V2 independent observation changed: ${id}`);
      const matches = result => expected === 'reject' ? result.status !== 'correct' : result.status === expected;
      assert.ok(matches(after), `V3 did not satisfy ${id}`);
      if (expected === 'reject') assert.ok(after.reason);
      return { id, expected, label, beforeMatchesExpectation: matches(before), matchesExpectation: matches(after), before, after };
    });
    return { name, diagnostics: facts.diagnostics, source: sources, total: observations.length,
      beforeMatched: observations.filter(o => o.beforeMatchesExpectation).length,
      afterMatched: observations.filter(o => o.matchesExpectation).length, observations };
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
}
const groups = [observe('unchanged-independent-probe', { 'input.ts': review.source }, review.observations), observe('adjacent-type-context-and-runtime-uses', texts, cases)];
assert.equal(source, texts['input.ts']);
const files = [reviewPath, 'experiments/corpus/v2/evaluate-labels.mjs', 'experiments/corpus/v3/evaluate-labels.mjs', 'experiments/corpus/v3/role-cases.mjs', 'experiments/corpus/v3/check-roles.mjs'];
console.log(JSON.stringify({ evaluatorVersion: 3, labelContractVersion: 2,
  fingerprints: Object.fromEntries(files.map(f => [f, digest(fs.readFileSync(path.join(repoRoot, f)))])), groups,
  interpretation: 'Actual scan with zero diagnostics; all V3 expectations asserted. This is evaluation-role correctness evidence, not human approval or product utility.' }, null, 2));
