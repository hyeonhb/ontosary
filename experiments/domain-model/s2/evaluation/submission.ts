import fs from 'node:fs';
import path from 'node:path';
import ts from 'typescript';
import { performance } from 'node:perf_hooks';
import { hash, stable } from '../lib/analysis-session.js';
import { Failure } from '../lib/model.js';

export type Sources = ReadonlyMap<string, Buffer>;
export type Delta = Record<string, string | null>;
export function deltaSubmission(baseline: Sources, changes: Delta): Sources {
    const result = new Map(baseline);
    for (const [file, text] of Object.entries(changes)) {
        if (path.isAbsolute(file) || file.split('/').some(p => !p || p === '..' || p === '.'))
            throw new Failure('SubmissionPath', file, 'Unsafe delta path');
        if (text === null) result.delete(file); else result.set(file, Buffer.from(text));
    }
    return result;
}
export function readSubmission(root: string): Sources {
    const result = new Map<string, Buffer>();
    function walk(relative: string) {
        for (const entry of fs.readdirSync(path.join(root, relative), { withFileTypes: true })) {
            if (['node_modules', '.git'].includes(entry.name)) continue;
            const file = path.posix.join(relative, entry.name);
            if (entry.isSymbolicLink()) throw new Failure('SubmissionPath', file, 'Submitted symlinks unsupported');
            if (entry.isDirectory()) walk(file);
            else if (entry.isFile()) result.set(file, fs.readFileSync(path.join(root, file)));
            else throw new Failure('SubmissionPath', file, 'Nonregular submission');
        }
    }
    walk('');
    return result;
}
export const manifest = (sources: Sources) => Object.fromEntries([...sources].sort(([a], [b]) => a.localeCompare(b)).map(([f, b]) => [f, hash(b)]));
export function sourceView(sources: Sources, onRead?: (file: string, digest: string) => void) {
    return {
        has: (file: string) => sources.has(file),
        read: (file: string) => {
            const bytes = sources.get(file);
            if (!bytes) throw new Failure('UnsupportedEvaluation', file, 'Submitted file missing');
            onRead?.(file, hash(bytes));
            return bytes.toString('utf8');
        },
    };
}
export interface CheckOptions { root: string; config: string; baseline: Sources; sources: Sources; allowedChange?: (file: string) => boolean; }
/** Full original modules/callers; source paths shadow the fixed environment, including absence. */
export function checkSubmission({ root, config, baseline, sources, allowedChange = f => f.endsWith('.ts') }: CheckOptions) {
    const start = performance.now(), changed = [...new Set([...baseline.keys(), ...sources.keys()])].filter(f => !baseline.has(f) || !sources.has(f) || !baseline.get(f)!.equals(sources.get(f)!));
    const unsupported: { file: string; reason: string }[] = [];
    for (const file of changed) {
        if (!sources.has(file)) unsupported.push({ file, reason: 'Deletion requires broader evaluation coverage' });
        else if (!allowedChange(file)) unsupported.push({ file, reason: 'Changed file outside supported TypeScript scope; HTML/UI requires manual review' });
    }
    const rootPath = path.resolve(root), toRelative = (file: string) => path.relative(rootPath, path.resolve(file)).split(path.sep).join('/');
    const reads = new Map<string, string>();
    const host = ts.createCompilerHost({});
    const originalRead = host.readFile.bind(host), originalExists = host.fileExists.bind(host);
    const names = new Set([...baseline.keys(), ...sources.keys()]);
    const read = (file: string): string | undefined => {
        const relative = toRelative(file);
        const bytes = relative.endsWith('.json') ? baseline.get(relative) : names.has(relative) ? sources.get(relative) : undefined;
        const text = relative.endsWith('.json') ? bytes?.toString('utf8') ?? originalRead(file) : names.has(relative) ? bytes?.toString('utf8') : originalRead(file);
        if (text !== undefined) reads.set(relative.startsWith('../') ? '<typescript>/' + path.basename(file) : relative, bytes ? hash(bytes) : hash(text));
        return text;
    };
    const exists = (file: string) => names.has(toRelative(file)) ? sources.has(toRelative(file)) : originalExists(file);
    const parseHost: ts.ParseConfigHost = { ...ts.sys, readFile: read, fileExists: exists };
    const raw = ts.readConfigFile(path.join(rootPath, config), read);
    const parsed = ts.parseJsonConfigFileContent(raw.config ?? {}, parseHost, path.dirname(path.join(rootPath, config)), { noEmit: true });
    const options = parsed.options;
    if ((!options.strict && !options.strictNullChecks) || options.strictNullChecks === false)
        unsupported.push({ file: config, reason: 'Strict null checking required; configuration not relaxed' });
    const compilerHost = ts.createCompilerHost(options);
    compilerHost.readFile = read;
    compilerHost.fileExists = exists;
    const sourceDirectories = new Set<string>();
    for (const file of sources.keys()) { let dir=path.posix.dirname(file); while(dir!=='.') {sourceDirectories.add(dir);dir=path.posix.dirname(dir);} }
    const originalDir = compilerHost.directoryExists?.bind(compilerHost);
    compilerHost.directoryExists = dir => sourceDirectories.has(toRelative(dir)) || originalDir?.(dir) === true;
    // Preserve fixed config roots. Newly imported helpers resolve through this host, not baseline fallbacks.
    const program = ts.createProgram({ rootNames: parsed.fileNames, options, projectReferences: parsed.projectReferences, host: compilerHost });
    const checked = new Map(program.getSourceFiles().map(sf => [toRelative(sf.fileName), sf]));
    const included = changed.map(file => ({ file, included: checked.has(file), sha256: sources.has(file) ? hash(sources.get(file)!) : null }));
    for (const item of included) if (!item.included && sources.has(item.file)) unsupported.push({ file: item.file, reason: 'Changed source absent from actual Program' });
    const diagnostics = [...(raw.error ? [raw.error] : []), ...parsed.errors, ...ts.getPreEmitDiagnostics(program)].map(d => ({
        code: d.code, category: ts.DiagnosticCategory[d.category], file: d.file ? toRelative(d.file.fileName) : null,
        line: d.file && d.start !== undefined ? d.file.getLineAndCharacterOfPosition(d.start).line + 1 : null,
        column: d.file && d.start !== undefined ? d.file.getLineAndCharacterOfPosition(d.start).character + 1 : null,
        message: ts.flattenDiagnosticMessageText(d.messageText, '\n').split(rootPath).join('<environment>'),
    }));
    const submittedManifest = manifest(sources);
    return {
        status: diagnostics.length ? 'failed' as const : unsupported.length ? 'unsupported' as const : 'passed' as const,
        diagnostics, unsupported, changedFiles: included,
        checkedFiles: [...checked].map(([file, sf]) => ({ file: file.startsWith('../') ? '<typescript>/' + path.basename(file) : file, sha256: hash(sf.text) })).sort((a,b) => a.file.localeCompare(b.file)),
        submissionId: hash(stable(submittedManifest)), submittedManifest,
        inputHashes: Object.fromEntries([...reads].sort(([a],[b]) => a.localeCompare(b))),
        configuration: { file: config, options: JSON.parse(JSON.stringify(options).split(rootPath).join('<environment>')) as unknown, typescript: ts.version, node: process.version },
        cost: { programs: 1, wallTimeMs: performance.now() - start, programFiles: program.getSourceFiles().length },
    };
}

export function overallStatus(typecheck: string, behavior: string, sourceBinding: boolean | null): 'passed' | 'failed' | 'unsupported' {
    if (typecheck === 'passed' && behavior === 'passed' && sourceBinding === true) return 'passed';
    return typecheck === 'unsupported' || behavior === 'unsupported' ? 'unsupported' : 'failed';
}
