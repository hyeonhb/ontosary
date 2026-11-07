import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
export const repoRoot = fileURLToPath(new URL('../../', import.meta.url));
export const inputRoot = fileURLToPath(new URL('./', import.meta.url));
export const cacheRoot = path.join(repoRoot, 'work/corpora');
export const readJson = file => JSON.parse(fs.readFileSync(file, 'utf8'));
export const digest = bytes => createHash('sha256').update(bytes).digest('hex');
export const manifest = readJson(path.join(inputRoot, 'manifest.json'));
export function verifySources(corpus) {
  const root = path.join(cacheRoot, corpus.id);
  for (const file of corpus.files) {
    const bytes = fs.readFileSync(path.join(root, file.path));
    if (digest(bytes) !== file.sha256 || bytes.length !== file.bytes) throw new Error(`Source hash mismatch: ${corpus.id}/${file.path}`);
  }
  return root;
}
export function locate(root, source) {
  const text = fs.readFileSync(path.join(root, source.file), 'utf8');
  const offset = text.indexOf(source.anchor);
  if (offset < 0 || text.indexOf(source.anchor, offset + 1) >= 0 || offset !== source.offset || text.slice(0, offset).split('\n').length !== source.line) {
    throw new Error(`Label anchor mismatch: ${source.file}:${source.line}`);
  }
}
// TypeChecker-rendered import types can contain absolute workspace paths. Redact only
// this known prefix in the serialized observation; offsets and local source stay intact.
export const serializeObservation = (value, indent = 2) => JSON.stringify(value, null, indent).replaceAll(repoRoot, '<workspace>/') + '\n';
