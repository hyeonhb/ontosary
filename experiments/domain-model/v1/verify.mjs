import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { sha } from './observe.mjs';
const [first, second] = process.argv.slice(2);
const files = dir => fs.readdirSync(dir).filter(f => f!=='timing.json').sort();
assert.deepEqual(files(first),files(second));
const hashes = {};
for (const file of files(first)) {
  hashes[file]=sha(fs.readFileSync(path.join(first,file)));
  assert.equal(hashes[file],sha(fs.readFileSync(path.join(second,file))),file);
}
console.log(JSON.stringify({equivalent:true,comparedFiles:Object.keys(hashes).length,excluded:{'timing.json':'Wall time only; not an analysis result'},scope:'Same pinned prepared cache, two new output paths; no independent installation reproduction',hashes},null,2));
