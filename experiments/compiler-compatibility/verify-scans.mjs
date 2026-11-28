// Compare public CLI output with the previously frozen Excalidraw evidence.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import path from 'node:path';

const [source, results] = process.argv.slice(2);
if (!source || !results) throw new Error('Usage: node verify-scans.mjs <Excalidraw root> <directory with scan-<version>.json>');
const read = file => JSON.parse(readFileSync(file, 'utf8'));
const previous = new URL('../first-use/excalidraw-eraser/', import.meta.url);
const frozen = read(new URL('source-check.json', previous));
const baseline = read(new URL('installed-cli.json', previous));
const inputs = { ...frozen.sourceSha256, 'yarn.lock': '033a69ccfaea9b182a18502b98899d361587e7cf8b100b6395cf1c5a24d286f6' };
for (const [file, sha] of Object.entries(inputs)) {
  assert.equal(createHash('sha256').update(readFileSync(path.join(source, file))).digest('hex'), sha, file);
}
assert.equal(read(path.join(source, 'node_modules/typescript/package.json')).version, '4.9.4');
for (const version of ['4.9.4', '5.9.3']) {
  const scan = read(path.join(results, `scan-${version}.json`));
  assert.deepEqual(scan.compiler, { requested: version, used: version });
  assert.deepEqual(scan.diagnostics, version === '4.9.4' ? [] : baseline.diagnostics);
  for (const field of ['files', 'types', 'functions', 'omissions']) {
    assert.equal(scan[field].length, frozen.scanCounts[field], field);
  }
  for (const location of frozen.locations) {
    const matches = scan.functions.filter(fn => fn.name === location.symbol);
    assert.deepEqual(matches.map(fn => fn.evidence), [location]);
    const code = readFileSync(path.resolve(source, 'packages/excalidraw', location.file), 'utf8');
    const prefix = code.slice(0, location.start.offset);
    assert.ok(prefix.endsWith('const ' + location.symbol + ' = '));
    assert.equal(code[location.start.offset], '(');
    console.log(version, matches[0].id, location.start.line, location.start.column);
  }
  console.log(version, scan.files.length, 'files,', scan.functions.length, 'functions,', scan.diagnostics.length, 'diagnostics');
}
