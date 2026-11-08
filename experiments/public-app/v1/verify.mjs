// Byte-level reproduction check, plus failure/result invariants for this frozen screen.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { gunzipSync } from 'node:zlib';
const [first, second] = process.argv.slice(2);
if (!first || !second) throw new Error('Usage: node experiments/public-app/v1/verify.mjs <first-output> <second-output>');
const sha = b => createHash('sha256').update(b).digest('hex');
const read = (root, f) => JSON.parse(fs.readFileSync(path.join(root, f), 'utf8'));
function names(root) {
  const all = [];
  function walk(dir) { for (const f of fs.readdirSync(dir).sort()) {
    const full = path.join(dir, f);
    if (fs.statSync(full).isDirectory()) walk(full); else all.push(path.relative(root, full));
  } } walk(root); return all.filter(f => !['timings.json', 'preparation.json'].includes(f));
}
const files = names(first); assert.deepEqual(files, names(second));
for (const f of files) assert.equal(sha(fs.readFileSync(path.join(first, f))), sha(fs.readFileSync(path.join(second, f))), `Mismatch: ${f}`);
const outcomes = {};
for (const variant of ['original', 'scoped']) {
  const processResult = read(first, `${variant}/process.json`);
  assert.equal(processResult.exitCode, 0); assert.equal(processResult.signal, null); assert.equal(processResult.error, null);
  const result = read(first, `${variant}/outcome.json`);
  outcomes[variant] = result.status;
  if (result.status === 'compiler-errors') {
    const scan = JSON.parse(gunzipSync(fs.readFileSync(path.join(first, variant, 'scan.json.gz'))));
    assert.ok(result.errorCount > 0);
    assert.equal(result.errorCount, scan.diagnostics.filter(d => d.category === 'Error').length);
    assert.equal(result.analyzedFiles, scan.files.length); assert.equal(result.functions, scan.functions.length);
    assert.ok(scan.functions.every(f => f.predicate.status === 'unsupported'));
    assert.equal(result.groups, 'not-run: compiler errors'); assert.equal(result.fca, 'not-run: compiler errors');
    assert.ok(!fs.existsSync(path.join(first, variant, 'concepts.json')));
  } else {
    assert.equal(result.status, 'rejected-before-program'); assert.match(result.error, /strictNullChecks/);
    assert.ok(!fs.existsSync(path.join(first, variant, 'scan.json.gz')));
  }
}
console.log(JSON.stringify({ equivalent: true, comparedFiles: files.length, outcomes,
  hashes: Object.fromEntries(files.map(f => [f, sha(fs.readFileSync(path.join(first, f)))])),
  excluded: ['timings.json', 'preparation.json'],
  scope: 'Reproduced failure observations at the same absolute cache path in this Node/TypeScript environment; not a successful application analysis or upstream build verdict.' }, null, 2));
