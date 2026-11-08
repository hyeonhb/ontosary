// Fetch immutable archives into an isolated cache; never execute upstream scripts.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { gzipSync } from 'node:zlib';
const here = path.dirname(fileURLToPath(import.meta.url));
const manifest = JSON.parse(fs.readFileSync(path.join(here, 'manifest.json')));
export const sha = b => createHash('sha256').update(b).digest('hex');
const cache = path.resolve(process.argv[2] ?? path.join(os.tmpdir(), 'ontosary-public-app-v1'));
const selected = process.argv[3];
for (let p = cache;; p = path.dirname(p)) {
  if (fs.existsSync(path.join(p, 'node_modules'))) throw new Error(`Cache must not inherit workspace dependencies: ${p}`);
  if (p === path.dirname(p)) break;
}
fs.mkdirSync(cache, { recursive: true });
for (const c of manifest.candidates.filter(c => !selected || c.id === selected)) {
  const start = performance.now(), root = path.join(cache, c.id), archive = path.join(cache, `${c.id}.tar.gz`);
  if (fs.existsSync(root)) throw new Error(`Use a new cache path; existing source is never overwritten: ${root}`);
  const res = await fetch(c.archiveUrl, { signal: AbortSignal.timeout(60000) });
  if (!res.ok) throw new Error(`Download failed: ${res.status}`);
  const bytes = Buffer.from(await res.arrayBuffer());
  if (sha(bytes) !== c.archiveSha256) throw new Error(`Archive integrity mismatch: ${c.id}`);
  fs.writeFileSync(archive, bytes, { flag: 'wx' });
  fs.mkdirSync(root);
  execFileSync('tar', ['-xzf', archive, '--strip-components=1', '-C', root]);
  const files = [];
  function walk(dir) { for (const name of fs.readdirSync(dir).sort()) {
    const f = path.join(dir, name), st = fs.lstatSync(f), rel = path.relative(root, f);
    if (st.isSymbolicLink()) files.push({ path: rel, symlink: fs.readlinkSync(f) });
    else if (st.isDirectory()) walk(f);
    else if (st.isFile()) files.push({ path: rel, bytes: st.size, sha256: sha(fs.readFileSync(f)) });
  } }
  walk(root);
  fs.writeFileSync(path.join(cache, `${c.id}-inventory.json.gz`), gzipSync(JSON.stringify(files, null, 2) + '\n'));
  fs.writeFileSync(path.join(cache, `${c.id}-preparation.json`), JSON.stringify({ archiveSha256: sha(bytes), archiveBytes: bytes.length,
    sourceFiles: files.length, sourceBytes: files.reduce((s, f) => s + (f.bytes ?? 0), 0), wallTimeMs: Math.round(performance.now() - start),
    method: 'Download, SHA-256 validation, tar extraction, file inventory; no dependency install, codegen, submodule checkout or source execution.',
    humanPreparationTimeMs: null, humanTaskTimeMs: null }, null, 2) + '\n');
  console.log(`${c.id}: ${files.length} files prepared`);
}
