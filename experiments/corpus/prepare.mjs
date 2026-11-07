import fs from 'node:fs';
import path from 'node:path';
import { performance } from 'node:perf_hooks';
import { manifest, cacheRoot, digest, verifySources } from './common.mjs';
const start = performance.now();
let downloadedFiles = 0, cachedFiles = 0;
for (const corpus of manifest.corpora) {
  const root = path.join(cacheRoot, corpus.id);
  for (const file of corpus.files) {
    const target = path.join(root, file.path);
    if (fs.existsSync(target)) { cachedFiles++; continue; }
    const response = await fetch(corpus.acquisition.replace('{path}', file.path), { signal: AbortSignal.timeout(30000) });
    if (!response.ok) throw new Error(`Download failed: ${response.status} ${corpus.id}/${file.path}`);
    const bytes = Buffer.from(await response.arrayBuffer());
    if (digest(bytes) !== file.sha256 || bytes.length !== file.bytes) throw new Error(`Download integrity failure: ${file.path}`);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, bytes, { flag: 'wx' });
    downloadedFiles++;
  }
  verifySources(corpus);
  for (const scope of corpus.scopes) if (scope.content) {
    fs.writeFileSync(path.join(root, scope.config), JSON.stringify(scope.content, null, 2) + '\n');
  }
}
const result = { downloadedFiles, cachedFiles, wallTimeMs: Math.round(performance.now() - start),
  method: 'SHA-256 verified immutable raw files; no package installation, upstream scripts or source execution.',
  authorPreparationTimeMs: null, humanReviewTimeMs: null };
fs.writeFileSync(path.join(cacheRoot, 'preparation.json'), JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify(result));
