import fs from 'node:fs';
import assert from 'node:assert/strict';
import { scan, selectFunction, compare, discoverConcepts } from '../dist/core/index.js';
const cases = JSON.parse(fs.readFileSync(new URL('./cases.json', import.meta.url), 'utf8'));
const facts = scan(cases.project);
assert.equal(facts.diagnostics.length, 0, 'Example must typecheck before experiment');
const groups = discoverConcepts(facts);
const comparisons = cases.comparisons.map(({ left, right, expected }) => {
  const a = selectFunction(facts, left), b = selectFunction(facts, right);
  const actual = compare(a.predicate, b.predicate, { sameInput: true });
  for (const [key, value] of Object.entries(expected)) assert.deepEqual(actual[key], value, `${left}/${right}: ${key}`);
  return { left: { id: a.id, evidence: a.predicateEvidence ?? a.evidence }, right: { id: b.id, evidence: b.predicateEvidence ?? b.evidence }, expected, actual };
});
const summary = {
  dataset: 'Synthetic vehicle/listing/consultation example; no real-world ground truth',
  files: facts.files.length, types: facts.types.length, functions: facts.functions.length,
  supportedPredicates: facts.functions.filter(f => f.predicate.status === 'supported').length,
  unsupportedPredicates: facts.functions.filter(f => f.predicate.status === 'unsupported').length,
  context: { objects: groups.context.objects.length, attributes: groups.context.attributes.length },
  formalConcepts: groups.concepts.length, candidates: groups.candidates.length,
  relations: groups.relations.length, truncated: groups.truncated,
  comparisonCases: comparisons.length, comparisonCasesPassed: comparisons.length,
  interpretation: 'Implementation feasibility demonstrated on this fixture; business concept accuracy, developer value, and superiority over LLM baselines remain untested.'
};
const output = new URL('./results/', import.meta.url);
fs.mkdirSync(output, { recursive: true });
for (const [name, value] of Object.entries({ scan: facts, concepts: groups, comparisons, summary })) fs.writeFileSync(new URL(`${name}.json`, output), JSON.stringify(value, null, 2) + '\n');
console.log(JSON.stringify(summary, null, 2));
