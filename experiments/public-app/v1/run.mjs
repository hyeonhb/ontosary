import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { gunzipSync } from 'node:zlib';
import { spawnSync } from 'node:child_process';
import ts from 'typescript';
const here = path.dirname(fileURLToPath(import.meta.url)), repo = path.resolve(here, '../../..');
const [id, cacheArg, outArg] = process.argv.slice(2);
if (!id || !cacheArg || !outArg) throw new Error('Usage: node experiments/public-app/v1/run.mjs <candidate> <isolated-cache> <new-output>');
const manifest = JSON.parse(fs.readFileSync(path.join(here, 'manifest.json'))), c = manifest.candidates.find(c => c.id === id);
if (!c) throw new Error('Unknown candidate');
const cache = path.resolve(cacheArg), root = path.join(cache, id), out = path.resolve(outArg);
const sha = b => createHash('sha256').update(b).digest('hex');
const taskBytes = fs.readFileSync(path.join(here, c.task));
if (sha(taskBytes) !== c.taskSha256) throw new Error('Pre-analysis task changed');
const inventory = JSON.parse(gunzipSync(fs.readFileSync(path.join(cache, `${id}-inventory.json.gz`))));
if (sha(fs.readFileSync(path.join(cache, `${id}.tar.gz`))) !== c.archiveSha256) throw new Error('Archive changed');
for (const f of inventory) {
  const actual = path.join(root, f.path);
  if (f.symlink ? fs.readlinkSync(actual) !== f.symlink : sha(fs.readFileSync(actual)) !== f.sha256) throw new Error(`Source changed: ${f.path}`);
}
for (let p = root;; p = path.dirname(p)) {
  if (fs.existsSync(path.join(p, 'node_modules'))) throw new Error('Unexpected application/ancestor node_modules; use isolated uninstalled cache');
  if (p === path.dirname(p)) break;
}
const task = JSON.parse(taskBytes);
for (const e of task.evidence) {
  const text = fs.readFileSync(path.join(root, e.file), 'utf8');
  if (sha(Buffer.from(text)) !== e.sha256 || text.indexOf(e.anchor) !== e.offsetUtf16 || text.indexOf(e.anchor, e.offsetUtf16 + 1) >= 0 || text.slice(0, e.offsetUtf16).split('\n').length !== e.line) throw new Error(`Task anchor changed: ${e.id}`);
}
if (fs.existsSync(out)) throw new Error('Output already exists; use a new path');
fs.mkdirSync(out, { recursive: true });
const write = (name, obj) => fs.writeFileSync(path.join(out, name), JSON.stringify(obj, null, 2) + '\n');
for (const name of ['inventory.json.gz', 'preparation.json']) fs.copyFileSync(path.join(cache, `${id}-${name}`), path.join(out, name));
const packageJson = JSON.parse(fs.readFileSync(path.join(root, 'package.json')));
const appPackage = JSON.parse(fs.readFileSync(path.join(root, c.appPackage ?? 'package.json')));
const fingerprintFiles = ['src/core/analyzer.ts', 'src/core/fca.ts', 'src/core/logic.ts', 'src/core/model.ts', 'pnpm-lock.yaml', 'dist/core/analyzer.js', 'dist/core/fca.js', 'dist/core/logic.js', 'experiments/public-app/v1/manifest.json', `experiments/public-app/v1/${c.task}`, 'experiments/public-app/v1/verify.mjs', 'experiments/public-app/v1/prepare.mjs', 'experiments/public-app/v1/observe.mjs', 'experiments/public-app/v1/run.mjs'];
write('input.json', { candidate: c, budget: manifest.budget, environment: { node: process.version, typescript: ts.version, platform: process.platform, arch: process.arch },
  upstream: { engines: packageJson.engines, packageManager: packageJson.packageManager, dependencies: Object.keys(packageJson.dependencies ?? {}).length, devDependencies: Object.keys(packageJson.devDependencies ?? {}).length },
  appPackage: { path: c.appPackage ?? 'package.json', engines: appPackage.engines, dependencies: Object.keys(appPackage.dependencies ?? {}).length, devDependencies: Object.keys(appPackage.devDependencies ?? {}).length },
  inventorySha256: sha(fs.readFileSync(path.join(cache, `${id}-inventory.json.gz`))), taskSha256: sha(taskBytes), fingerprints: Object.fromEntries(fingerprintFiles.map(f => [f, sha(fs.readFileSync(path.join(repo, f)))])),
  method: 'Isolated archive checkout; no app node_modules, source patches, generated stubs, submodule fetch or upstream execution. Missing dependencies are an environment failure, not proof upstream is invalid.' });
const metadata = [...new Set([...c.licenseFiles, ...c.metadataFiles])].map(file => {
  const bytes = fs.readFileSync(path.join(root, file));
  return { file, bytes: bytes.length, sha256: sha(bytes), sourceUrl: `https://github.com/${c.repository}/blob/${c.revision}/${file}` };
});
write('metadata.json', metadata);
fs.mkdirSync(path.join(out, 'licenses'));
for (const file of c.licenseFiles) fs.copyFileSync(path.join(root, file), path.join(out, 'licenses', path.basename(file)));
write('source-notice.json', { repository: c.repository, revision: c.revision, archiveUrl: c.archiveUrl, license: c.license, note: 'Upstream files remain in the isolated cache. Extracted source fragments in raw scan and task anchors retain upstream licensing; no upstream source is relicensed as Ontosary Apache-2.0.' });
const runs = [];
for (const [name, config] of [['original', c.originalConfig], ...(c.scopedConfig ? [['scoped', c.scopedConfigPath ?? 'ontosary.scope.json']] : [])]) {
  if (name === 'scoped') fs.writeFileSync(path.join(root, config), JSON.stringify(c.scopedConfig, null, 2) + '\n');
  const dir = path.join(out, name); fs.mkdirSync(dir);
  const start = performance.now();
  const result = spawnSync(process.execPath, [`--max-old-space-size=${manifest.budget.maxHeapMb}`, path.join(here, 'observe.mjs'), root, config, dir], { timeout: manifest.budget.perProcessTimeoutMs, encoding: 'utf8', maxBuffer: 8 * 1024 * 1024 });
  const clean = text => text?.replaceAll(root, '<app>').replaceAll(repo, '<workspace>');
  fs.writeFileSync(path.join(dir, 'process.json'), JSON.stringify({ exitCode: result.status, signal: result.signal, error: result.error?.code ?? null, stdout: clean(result.stdout), stderr: clean(result.stderr) }, null, 2) + '\n');
  runs.push({ name, wallTimeMs: Math.round(performance.now() - start) });
}
write('timings.json', { runs, humanPreparationTimeMs: null, humanTaskTimeMs: null, note: 'Machine wall time only; first observation may include cache effects. No human experiment.' });
console.log(out);
