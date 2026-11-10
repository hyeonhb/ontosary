import fs from 'node:fs';
import path from 'node:path';
import { gunzipSync } from 'node:zlib';
import { array, object, string, choice, Failure } from './lib/model.js';
import { hash } from './lib/analysis-session.js';
const [bundleArg, sourceArg, conditionArg, outArg, repoArg, environmentArg] = process.argv.slice(2);
if (!bundleArg || !sourceArg || !conditionArg || !outArg)
    throw Error('Usage: workspace <bundle-dir> <baseline-root> <A|B|C> <new-workspace> [repo] [isolated-environment]');
const condition = choice(conditionArg, ['A', 'B', 'C'], 'condition'), bundle = path.resolve(bundleArg), source = path.resolve(sourceArg), out = path.resolve(outArg), repo = path.resolve(repoArg ?? '.');
if (fs.existsSync(out))
    throw new Failure('OutputExists', out, 'No overwrite');
fs.mkdirSync(path.dirname(out), { recursive: true });
const stage = fs.mkdtempSync(path.join(path.dirname(out), '.s2-workspace-'));
const safe = (base: string, relative: string) => { if (path.isAbsolute(relative) || relative.split('/').some(s => s === '..' || s === ''))
    throw new Failure('Path', relative, 'Unsafe path'); return path.join(base, relative); };
try {
    const manifest = object(JSON.parse(fs.readFileSync(path.join(bundle, 'bundle-manifest.json'), 'utf8')), 'manifest');
    for (const x of array(manifest.files, 'files')) {
        const e = object(x, 'file'), name = string(e.file, 'file');
        if (!name.startsWith(condition + '/'))
            continue;
        const input = safe(bundle, name);
        if (!fs.lstatSync(input).isFile())
            throw new Failure('Packaging', name, 'Symlink or special file');
        const bytes = fs.readFileSync(input);
        if (hash(bytes) !== e.sha256)
            throw new Failure('Integrity', name, 'Bundle file changed');
        const dest = safe(path.join(stage, 'materials'), name.slice(condition.length + 1));
        fs.mkdirSync(path.dirname(dest), { recursive: true });
        fs.writeFileSync(dest, bytes, { flag: 'wx' });
    }
    const inv = array(JSON.parse(gunzipSync(fs.readFileSync(path.join(repo, 'experiments/public-app/results/2026-11-08/vendure/inventory.json.gz'))).toString()), 'inventory');
    for (const x of inv) {
        const e = object(x, 'entry'), file = string(e.path, 'path'), input = safe(source, file);
        if (e.symlink !== undefined || !fs.lstatSync(input).isFile())
            throw new Failure('Packaging', file, 'Source symlink requires explicit safe materialization policy');
        const bytes = fs.readFileSync(input);
        if (hash(bytes) !== e.sha256)
            throw new Failure('Integrity', file, 'Baseline source changed');
        const dest = safe(path.join(stage, 'source'), file);
        fs.mkdirSync(path.dirname(dest), { recursive: true });
        fs.writeFileSync(dest, bytes, { flag: 'wx' });
    }
    if(environmentArg) {
        const tools=fs.realpathSync(path.join(path.resolve(environmentArg),'tools'));
        for(const name of ['public-check','public-check.js','baseline-manifest.json'])if(!fs.statSync(path.join(tools,name)).isFile())throw new Failure('Packaging',name,'Public tool missing');
        fs.symlinkSync(tools,path.join(stage,'tools'));
    }
    fs.renameSync(stage, out);
    console.log(JSON.stringify({ condition, sourceFiles: inv.length, isolation: 'unverified', dependencies: 'not copied; runtime mount/permissions must be fixed before trial', evaluationFilesCopied: 0 }));
}
catch (e) {
    fs.rmSync(stage, { recursive: true, force: true });
    throw e;
}
