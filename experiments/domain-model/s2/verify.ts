import fs from 'node:fs';
import path from 'node:path';
import { hash } from './lib/analysis-session.js';
import { object, array, string, Failure } from './lib/model.js';
const [a, b, out] = process.argv.slice(2);
if (!a || !b || !out)
    throw Error('Usage: verify <first> <repeat> <new-report>');
const files = (dir: string, prefix = ''): string[] => fs.readdirSync(path.join(dir, prefix)).sort().flatMap(f => { const rel = path.join(prefix, f), s = fs.lstatSync(path.join(dir, rel)); if (s.isSymbolicLink())
    throw new Failure('Integrity', rel, 'Symlink not allowed'); return s.isDirectory() ? files(dir, rel) : [rel]; });
const left = files(a).filter(f => f !== 'evaluator/timing.json'), right = files(b).filter(f => f !== 'evaluator/timing.json');
if (JSON.stringify(left) !== JSON.stringify(right))
    throw Error('File lists differ');
const hashes: Record<string, string> = {};
for (const f of left) {
    const x = hash(fs.readFileSync(path.join(a, f))), y = hash(fs.readFileSync(path.join(b, f)));
    if (x !== y)
        throw Error('Mismatch: ' + f);
    hashes[f] = x;
}
for (const dir of [a, b]) {
    const m = object(JSON.parse(fs.readFileSync(path.join(dir, 'bundle-manifest.json'), 'utf8')), 'manifest');
    for (const x of array(m.files, 'files')) {
        const e = object(x, 'file'), f = string(e.file, 'file');
        if (f.split('/').includes('..') || path.isAbsolute(f))
            throw Error('Unsafe manifest');
        if (hash(fs.readFileSync(path.join(dir, f))) !== e.sha256)
            throw Error('Manifest hash mismatch');
    }
}
fs.writeFileSync(out, JSON.stringify({ equivalent: true, nonTimeFiles: left.length, excluded: ['evaluator/timing.json: timings and process memory only'], hashes }, null, 2) + '\n', { flag: 'wx' });
console.log(left.length);
