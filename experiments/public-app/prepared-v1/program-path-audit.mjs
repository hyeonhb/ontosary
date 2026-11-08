// Post-preparation provenance check. No scan, context, install or build is run.
// macOS realpaths /tmp to /private/tmp; preserve the original observation files.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import ts from 'typescript';
import { createHash } from 'node:crypto';
import { gunzipSync } from 'node:zlib';
const [rootArg, resultsArg] = process.argv.slice(2);
const root = path.resolve(rootArg), realRoot = fs.realpathSync(root);
const lib = fs.realpathSync(path.dirname(ts.getDefaultLibFilePath({})));
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const observations = {};
for (const scope of ['original', 'scoped']) {
  const previous = JSON.parse(gunzipSync(fs.readFileSync(path.join(resultsArg, scope, 'program.json.gz'))));
  const savedConfig = JSON.parse(fs.readFileSync(path.join(resultsArg, scope, 'config.json')));
  const config = path.join(root, savedConfig.config);
  const loaded = ts.readConfigFile(config, ts.sys.readFile);
  assert.equal(loaded.error, undefined);
  const parsed = ts.parseJsonConfigFileContent(loaded.config, ts.sys, path.dirname(config), { noEmit: true }, config);
  const program = ts.createProgram({ rootNames: parsed.fileNames, options: parsed.options, projectReferences: parsed.projectReferences });
  const files = program.getSourceFiles().map((sf, i) => {
    const actual = fs.realpathSync(sf.fileName);
    assert.ok(actual.startsWith(realRoot + path.sep) || actual.startsWith(lib + path.sep), `Unexpected source outside cache/TS lib: ${actual}`);
    const oldPath = sf.fileName.startsWith(root + path.sep) ? path.relative(root, sf.fileName) : sf.fileName.startsWith(path.dirname(ts.getDefaultLibFilePath({})) + path.sep) ? `<typescript-lib>/${path.relative(path.dirname(ts.getDefaultLibFilePath({})), sf.fileName)}` : '<external>/' + path.basename(sf.fileName);
    const fingerprint = { path: oldPath, sha256: sha(fs.readFileSync(actual)), declaration: sf.isDeclarationFile, externalLibrary: program.isSourceFileFromExternalLibrary(sf) };
    assert.deepEqual(fingerprint, previous.files[i], `${scope} Program file ${i}`);
    return { ...fingerprint, path: actual.startsWith(realRoot + path.sep) ? path.relative(realRoot, actual) : `<typescript-lib>/${path.relative(lib, actual)}`, observedPath: oldPath };
  });
  assert.equal(files.length, previous.files.length);
  observations[scope] = { fileCount: files.length, recoveredPaths: files.filter(f => f.observedPath.startsWith('<external>/')).length, unexpectedExternalFiles: 0, files };
}
console.log(JSON.stringify({ phase: 'Post-preparation reporting/provenance verification; no scan or preparation retry', observedUtc: new Date().toISOString(), explanation: 'On macOS /tmp resolves to /private/tmp. Original recorder used lexical /tmp root; dependency realpaths were abbreviated. All original Program file fingerprints/order match; paths below use canonical root.', observations }, null, 2));
