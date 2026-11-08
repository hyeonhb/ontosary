// Verify observations of the same prepared cache; does not reinstall dependencies.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { gunzipSync } from 'node:zlib';
const [first, repeat] = process.argv.slice(2);
if (!first || !repeat) throw new Error('Usage: node experiments/public-app/prepared-v1/verify.mjs <results> <repeat>');
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const hashes = {}, observations = {};
for (const scope of ['original', 'scoped']) {
  const dir = path.join(first, scope), other = path.join(repeat, scope);
  const files = fs.readdirSync(dir).sort();
  assert.deepEqual(files, fs.readdirSync(other).sort());
  for (const f of files) {
    const key = `${scope}/${f}`; hashes[key] = sha(fs.readFileSync(path.join(dir, f)));
    assert.equal(hashes[key], sha(fs.readFileSync(path.join(other, f))), key);
  }
  const facts = JSON.parse(gunzipSync(fs.readFileSync(path.join(dir, 'scan.json.gz'))));
  const result = JSON.parse(fs.readFileSync(path.join(dir, 'outcome.json')));
  assert.equal(result.errorCount, facts.diagnostics.filter(d => d.category === 'Error').length);
  assert.equal(result.functions, facts.functions.length); assert.equal(result.analyzedFiles, facts.files.length);
  assert.ok(!fs.existsSync(path.join(dir, 'concepts.json'))); assert.ok(!fs.existsSync(path.join(dir, 'simple-groups.json')));
  if (scope === 'original') {
    assert.ok(result.errorCount > 0); assert.equal(result.context, null);
    assert.ok(facts.functions.every(f => f.predicate.status === 'unsupported'));
    assert.ok(facts.diagnostics.every(d => d.evidence?.file.endsWith('.spec.ts')));
  } else {
    assert.equal(result.errorCount, 0); assert.deepEqual(facts.diagnostics, []);
    assert.equal(result.context.objects, facts.functions.length);
    assert.equal(Object.values(result.entryFunctions).reduce((a,b) => a+b, 0), 129);
    assert.ok(result.context.objects > result.context.limits.maxObjects);
    assert.ok(result.context.attributes > result.context.limits.maxAttributes);
    assert.equal(result.context.fits, false);
  }
  observations[scope] = { status: result.status, errorCount: result.errorCount, functions: result.functions, context: result.context };
}
console.log(JSON.stringify({ equivalent: true, comparedFiles: Object.keys(hashes).length, observations, hashes,
  scope: 'Same installed cache and absolute path, two new scan outputs. Dependency installation/build was not independently reproduced; cross-path type-display limitations remain.' }, null, 2));
