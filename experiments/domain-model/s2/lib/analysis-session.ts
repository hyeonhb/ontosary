import fs from 'node:fs';
import path from 'node:path';
import ts from 'typescript';
import { createHash } from 'node:crypto';
import { Evidence, Failure } from './model.js';
export const hash = (b: string | Buffer) => createHash('sha256').update(b).digest('hex');
export function stable(x: unknown): string { if (Array.isArray(x))
    return '[' + x.map(stable).join(',') + ']'; if (x !== null && typeof x === 'object')
    return '{' + Object.entries(x).sort(([a], [b]) => a.localeCompare(b)).map(([k, v]) => JSON.stringify(k) + ':' + stable(v)).join(',') + '}'; return JSON.stringify(x); }
function lineStarts(text: string) { const starts = [0]; for (let i = 0; i < text.length; i++) {
    const c = text.charCodeAt(i);
    if (c === 13) {
        if (text.charCodeAt(i + 1) === 10)
            i++;
        starts.push(i + 1);
    }
    else if (c === 10 || c === 0x2028 || c === 0x2029)
        starts.push(i + 1);
} return starts; }
function position(lines: number[], offset: number) { let line = 0; while (line + 1 < lines.length && lines[line + 1]! <= offset)
    line++; return { line, character: offset - lines[line]! }; }
export interface Input {
    file: string;
    sha256?: string;
    symlink?: string;
}
export interface BaselineSpec {
    root: string;
    config: string;
    revision: string;
    policy: string;
    inputs: Input[];
    program?: Input[];
    artifacts: Input[];
}
export interface Baseline {
    baselineId: string;
    revision: string;
    inputs: number;
    programFiles: number;
    sourceVersion: 'baseline';
    currentWorkspaceAssessment: 'not-performed';
}
const tokens = new WeakSet<object>();
export function verified(b: Baseline) { return tokens.has(b); }
export class BaselineSession {
    state: 'open' | 'sealed' | 'rejected' | 'disposed' = 'open';
    private program: ts.Program | undefined;
    private snapshot = new Map<string, string>();
    private texts = new Map<string, {
        text: string;
        lines: number[];
    }>();
    private inspected = false;
    private lookups = new Map<string, boolean>();
    metrics = { programs: 0, hostReads: 0, explicitReads: 0, hashes: 0, sealReads: 0 };
    constructor(private spec: BaselineSpec) { }
    private open() { if (this.state !== 'open')
        throw new Failure('State', 'session', this.state); }
    private read(file: string, retain = false) {
        const canonical = fs.realpathSync(file);
        let entry = this.texts.get(canonical);
        if (entry)
            return entry;
        const bytes = fs.readFileSync(file);
        this.metrics.explicitReads++;
        this.metrics.hashes++;
        const digest = hash(bytes);
        this.snapshot.set(canonical, digest);
        const text = bytes.toString('utf8');
        const lines = lineStarts(text);
        entry = { text, lines };
        if (retain)
            this.texts.set(canonical, entry);
        return entry;
    }
    private reject(e: unknown): never { this.state = 'rejected'; throw e; }
    inspectInputs() {
        this.open();
        if (this.inspected)
            return this.metrics;
        try {
            for (const input of [...this.spec.inputs, ...this.spec.artifacts]) {
                if (input.symlink !== undefined) {
                    if (fs.readlinkSync(input.file) !== input.symlink)
                        throw new Failure('InputChanged', input.file, 'Symlink differs');
                    continue;
                }
                if (!this.snapshot.has(fs.realpathSync(input.file)))
                    this.read(input.file);
                if (input.sha256 && this.snapshot.get(fs.realpathSync(input.file)) !== input.sha256)
                    throw new Failure('InputChanged', input.file, 'Hash differs');
            }
            const configHost: ts.ParseConfigHost = { ...ts.sys, readFile: f => { try {
                    return this.read(f, true).text;
                }
                catch {
                    return undefined;
                } } };
            const config = ts.readConfigFile(this.spec.config, configHost.readFile);
            if (config.error)
                throw new Failure('Diagnostic', 'config', 'Cannot read config');
            const parsed = ts.parseJsonConfigFileContent(config.config, configHost, path.dirname(this.spec.config), { noEmit: true });
            if (parsed.errors.length || (!parsed.options.strict && !parsed.options.strictNullChecks) || parsed.options.strictNullChecks === false)
                throw new Failure('Diagnostic', 'config', 'Invalid strict config');
            const host = ts.createCompilerHost(parsed.options), exists = host.fileExists.bind(host), directory = host.directoryExists?.bind(host);
            if (directory)
                host.directoryExists = f => { const found = directory(f); this.lookups.set('d:' + f, found); return found; };
            host.fileExists = f => { const found = exists(f); this.lookups.set('f:' + f, found); return found; };
            const read = host.readFile.bind(host);
            host.readFile = f => { this.metrics.hostReads++; const text = read(f); if (text !== undefined && fs.existsSync(f)) {
                this.snapshot.set(fs.realpathSync(f), hash(Buffer.from(text)));
                this.metrics.hashes++;
            } return text; };
            this.program = ts.createProgram({ rootNames: parsed.fileNames, options: parsed.options, projectReferences: parsed.projectReferences, host });
            this.metrics.programs++;
            const actual = this.program.getSourceFiles().map(sf => { const canonical = fs.realpathSync(sf.fileName); this.texts.set(canonical, { text: sf.text, lines: lineStarts(sf.text) }); const digest = hash(Buffer.from(sf.text)); this.snapshot.set(canonical, digest); return { file: canonical, sha256: digest }; }).sort((a, b) => a.file.localeCompare(b.file));
            if (this.spec.program) {
                const expected = this.spec.program.map(p => ({ file: fs.realpathSync(p.file), sha256: p.sha256 })).sort((a, b) => a.file.localeCompare(b.file));
                if (stable(actual) !== stable(expected))
                    throw new Failure('InputChanged', 'Program', 'Membership/hash differs');
            }
            if (ts.getPreEmitDiagnostics(this.program).length)
                throw new Failure('Diagnostic', 'Program', 'Compiler diagnostics');
            this.inspected = true;
            return this.metrics;
        }
        catch (e) {
            return this.reject(e);
        }
    }
    verifyEvidence(e: Evidence) {
        this.open();
        if (!this.inspected)
            throw new Failure('State', 'session', 'inspect first');
        try {
            if (!Number.isSafeInteger(e.offset) || e.offset < 0 || !Number.isSafeInteger(e.end) || e.end < e.offset + e.anchor.length || !Number.isSafeInteger(e.line) || e.line < 1)
                throw new Failure('Evidence', e.id, 'Invalid UTF16 interval/line');
            const file = path.resolve(this.spec.root, e.file);
            if (!file.startsWith(path.resolve(this.spec.root) + path.sep))
                throw new Failure('Evidence', e.id, 'Outside root');
            const { text, lines } = this.read(file, true);
            const sf = this.program?.getSourceFile(file);
            if (sf && sf.text !== text)
                throw new Failure('Evidence', e.id, 'Program text mismatch');
            if (this.snapshot.get(fs.realpathSync(file)) !== e.sha256 || text.slice(e.offset, e.offset + e.anchor.length) !== e.anchor || e.end > text.length || position(lines, e.offset).line + 1 !== e.line)
                throw new Failure('Evidence', e.id, 'Hash/anchor/UTF16 coordinate mismatch');
            return { ...e, text: text.slice(e.offset, e.end), column: position(lines, e.offset).character + 1, sourceVersion: 'baseline' as const };
        }
        catch (x) {
            return this.reject(x);
        }
    }
    seal(): Baseline {
        this.open();
        if (!this.inspected)
            throw new Failure('State', 'session', 'inspect first');
        try {
            for (const i of [...this.spec.inputs, ...this.spec.artifacts])
                if (i.symlink !== undefined && fs.readlinkSync(i.file) !== i.symlink)
                    throw new Failure('InputChanged', i.file, 'Symlink changed before seal');
            for (const [key, exists] of this.lookups) {
                let current = false;
                try {
                    const stat = fs.statSync(key.slice(2));
                    current = key.startsWith('d:') ? stat.isDirectory() : stat.isFile();
                }
                catch { }
                if (current !== exists)
                    throw new Failure('InputChanged', 'resolution', 'Resolution lookup changed');
            }
            for (const [file, h] of this.snapshot) {
                this.metrics.sealReads++;
                if (hash(fs.readFileSync(file)) !== h)
                    throw new Failure('InputChanged', file, 'Changed before seal');
            }
            // Reparse root membership without a second Program.
            const cfg = ts.readConfigFile(this.spec.config, ts.sys.readFile), p = ts.parseJsonConfigFileContent(cfg.config, ts.sys, path.dirname(this.spec.config), { noEmit: true });
            if (stable([...p.fileNames].sort()) !== stable([...(this.program?.getRootFileNames() ?? [])].sort()))
                throw new Failure('InputChanged', 'roots', 'Input list changed');
            const root = fs.realpathSync(this.spec.root);
            const names = [...this.snapshot].map(([f, h]) => [f.startsWith(root + path.sep) ? path.relative(root, f) : f.includes('/typescript/lib/') ? 'typescript/' + path.basename(f) : 'artifact/' + path.basename(f), h]).sort(([a], [b]) => a!.localeCompare(b!));
            const b: Baseline = { baselineId: hash(stable({ revision: this.spec.revision, policy: this.spec.policy, ts: ts.version, node: process.version, files: names })), revision: this.spec.revision, inputs: this.spec.inputs.length, programFiles: this.program!.getSourceFiles().length, sourceVersion: 'baseline', currentWorkspaceAssessment: 'not-performed' };
            tokens.add(b);
            this.state = 'sealed';
            return Object.freeze(b);
        }
        catch (e) {
            return this.reject(e);
        }
    }
    dispose() { this.program = undefined; this.texts.clear(); this.snapshot.clear(); this.lookups.clear(); this.state = 'disposed'; }
}
export const openBaselineSession = (spec: BaselineSpec) => new BaselineSession(spec);
