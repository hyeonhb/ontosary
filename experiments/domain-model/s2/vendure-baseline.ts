import fs from 'node:fs';
import path from 'node:path';
import { gunzipSync } from 'node:zlib';
import ts from 'typescript';
import { BaselineSpec, hash } from './lib/analysis-session.js';
import { array, object, string, Failure } from './lib/model.js';
export const json = (f: string): unknown => JSON.parse(f.endsWith('.gz') ? gunzipSync(fs.readFileSync(f), { maxOutputLength: 16777216 }).toString() : fs.readFileSync(f, 'utf8'));
export function vendure(root: string, repo: string): {
    spec: BaselineSpec;
    artifacts: unknown[];
} {
    const s2 = path.join(repo, 'experiments/domain-model/s2'), provenance = object(json(path.join(s2, 'provenance.json')), 'provenance'), manifest = object(json(path.join(repo, 'experiments/domain-model/v1/manifest.json')), 'manifest');
    const artifacts = Object.entries(object(provenance.S1Artifacts, 'S1Artifacts')).map(([f, h]) => ({ file: path.join(repo, 'experiments/domain-model/results/2026-11-08-v2', f), sha256: string(h, f) }));
    for (const f of artifacts)
        if (hash(fs.readFileSync(f.file)) !== f.sha256)
            throw new Failure('InputChanged', f.file, 'S1 artifact changed');
    const inventory = array(json(path.join(repo, 'experiments/public-app/results/2026-11-08/vendure/inventory.json.gz')), 'inventory').map(x => { const e = object(x, 'inventory'); return { file: path.join(root, string(e.path, 'path')), ...(e.symlink !== undefined ? { symlink: string(e.symlink, 'symlink') } : { sha256: string(e.sha256, 'hash') }) }; });
    const prior = object(json(path.join(repo, 'experiments/public-app/results/2026-11-08-prepared/program-path-audit.json.gz')), 'audit');
    const files = array(object(object(prior.observations, 'observations').scoped, 'scoped').files, 'files');
    const program = files.map(x => { const e = object(x, 'file'), p = string(e.path, 'path'); return { file: p.startsWith('<typescript-lib>/') ? path.join(path.dirname(ts.getDefaultLibFilePath({})), p.slice(17)) : path.join(root, p), sha256: string(e.sha256, 'hash') }; });
    const explicit = Object.entries(object(manifest.inputHashes, 'inputHashes')).map(([f, h]) => ({ file: path.join(root, f), sha256: string(h, f) }));
    const repository = Object.entries(object(manifest.repositoryInputs, 'repositoryInputs')).map(([f, h]) => ({ file: path.resolve(repo, 'experiments/domain-model/v1', f), sha256: string(h, f) }));
    return { spec: { root: fs.realpathSync(root), config: path.resolve(root, string(manifest.config, 'config')), revision: string(manifest.revision, 'revision'), policy: 'S2-v1', inputs: [...inventory, ...explicit, ...program], program, artifacts: [...artifacts, ...repository] }, artifacts: artifacts.map(f => json(f.file)) };
}
