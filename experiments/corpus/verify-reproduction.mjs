import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { digest } from './common.mjs';
const [left, right] = process.argv.slice(2);
if (!left || !right) throw new Error('Usage: node experiments/corpus/verify-reproduction.mjs <first-run> <second-run>');
const files = dir => fs.readdirSync(dir).filter(f => f !== 'timings.json').sort();
assert.deepEqual(files(left), files(right), 'Evidence file inventory changed');
const hashes = {};
for (const name of files(left)) {
  const a = fs.readFileSync(path.join(left, name)), b = fs.readFileSync(path.join(right, name));
  assert.deepEqual(a, b, `Non-timing evidence changed: ${name}`);
  hashes[name] = digest(a);
}
console.log(JSON.stringify({ equivalent: true, comparedFiles: Object.keys(hashes).length, hashes,
  excluded: ['timings.json: measured wall time and preparation cache state'],
  scope: 'Two fresh scanner runs in the same workspace/dependency layout; not a portability or performance claim.' }, null, 2));
