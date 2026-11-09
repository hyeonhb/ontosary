import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import ts from 'typescript';
import { createRequire } from 'node:module';
import { Failure } from '../lib/model.js';
export type Runtime = Record<string, unknown>;
export function invoke(o: Runtime, key: string, ...args: unknown[]): unknown { const f = o[key]; if (typeof f !== 'function')
    throw new Failure('UnsupportedEvaluation', key, 'Not callable'); return Reflect.apply(f, o, args); }
export interface Mapping {
    file: string;
    className: string;
}
/** Executes submitted class method/accessor bodies. DI, field initialization, inheritance and decorators are explicit excluded seams. */
export function executor(root: string, mappings: Mapping[], bindings: Runtime, environmentRoot = root, view?: { has(file: string): boolean; read(file: string): string }) {
    const loaded = new Map<string, Runtime>(), req = createRequire(path.join(environmentRoot, 'package.json'));
    const resolve = (from: string, spec: string) => { const p = path.resolve(path.dirname(from), spec); for (const f of [p, p + '.ts', p + '.js', path.join(p, 'index.ts')])
        if (view ? view.has(path.relative(root, f)) : fs.existsSync(f) && fs.statSync(f).isFile())
            return f; throw new Failure('UnsupportedEvaluation', spec, 'Missing submitted helper'); };
    function load(file: string): Runtime {
        if (loaded.has(file))
            return loaded.get(file)!;
        if (!file.startsWith(path.resolve(root) + path.sep))
            throw new Failure('UnsupportedEvaluation', file, 'Helper outside submission');
        const source = view ? view.read(path.relative(root, file)) : fs.readFileSync(file, 'utf8'), sf = ts.createSourceFile(file, source, ts.ScriptTarget.Latest, true);
        const selected = mappings.find(m => path.resolve(root, m.file) === file);
        let code = source;
        if (selected) {
            const cls = sf.statements.find((n): n is ts.ClassDeclaration => ts.isClassDeclaration(n) && n.name?.text === selected.className);
            if (!cls)
                throw new Failure('UnsupportedEvaluation', file, 'Class missing');
            const baselineFile = path.resolve(environmentRoot, selected.file);
            if (fs.existsSync(baselineFile)) {
                const baselineText = fs.readFileSync(baselineFile, 'utf8'), baseFile = ts.createSourceFile(baselineFile, baselineText, ts.ScriptTarget.Latest, true), baseClass = baseFile.statements.find((n): n is ts.ClassDeclaration => ts.isClassDeclaration(n) && n.name?.text === selected.className);
                const excluded = (c: ts.ClassDeclaration, f: ts.SourceFile) => JSON.stringify({ members: c.members.filter(n => !ts.isMethodDeclaration(n) && !ts.isGetAccessorDeclaration(n) && !ts.isSetAccessorDeclaration(n)).map(n => n.getText(f)), heritage: c.heritageClauses?.map(n => n.getText(f)), decorators: ts.getDecorators(c)?.map(n => n.getText(f)) });
                if (!baseClass || excluded(cls, sf) !== excluded(baseClass, baseFile))
                    throw new Failure('UnsupportedEvaluation', file, 'Changes to excluded constructor/field/inheritance/decorator seam require a broader harness');
            }
            const members = cls.members.filter(n => ts.isMethodDeclaration(n) || ts.isGetAccessorDeclaration(n) || ts.isSetAccessorDeclaration(n)).map(n => n.getText(sf));
            const imports = sf.statements.filter(ts.isImportDeclaration).map(n => n.getText(sf));
            const helpers = sf.statements.filter(n => ts.isFunctionDeclaration(n) || ts.isVariableStatement(n) || ts.isEnumDeclaration(n)).map(n => n.getText(sf));
            code = [...imports, ...helpers, `export class ${selected.className} {${members.join('\n')}}`].join('\n');
        }
        const checked = ts.createSourceFile(file, code, ts.ScriptTarget.Latest, true);
        let deferred = false;
        const inspect = (n: ts.Node) => { if (n.kind === ts.SyntaxKind.AsyncKeyword || ts.isAwaitExpression(n) || (ts.isIdentifier(n) && n.text === 'Promise'))
            deferred = true; ts.forEachChild(n, inspect); };
        inspect(checked);
        if (deferred)
            throw new Failure('UnsupportedEvaluation', file, 'Deferred Promise/async execution requires a broader harness');
        const js = ts.transpileModule(code, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, esModuleInterop: true } }).outputText;
        const exports: Runtime = {};
        loaded.set(file, exports);
        const lazy = (specifier: string) => new Proxy({}, { get(_target, key) { if (key === '__esModule')
                return true; const name = String(key); if (Object.hasOwn(bindings, name))
                return bindings[name]; const target = mappings.find(m => m.className === name); if (target)
                return load(path.resolve(root, target.file))[name]; if (specifier.startsWith('.'))
                return load(resolve(file, specifier))[name]; if (specifier === 'rxjs' || specifier === 'rxjs/operators') {
                if (!['of', 'forkJoin', 'EMPTY', 'Observable', 'Subject', 'map', 'mapTo', 'startWith', 'switchMap', 'take'].includes(name))
                    throw new Failure('UnsupportedEvaluation', name, 'Unreviewed RxJS operator/scheduler');
                const mod: unknown = req(specifier);
                return (mod as Runtime)[name];
            } throw new Failure('UnsupportedEvaluation', specifier + ':' + name, 'Unsupported executed dependency: ' + specifier + ':' + name); } });
        const context = vm.createContext({ exports, require: lazy, console: { log: () => undefined }, ...bindings });
        try {
            new vm.Script(js, { filename: path.relative(root, file) }).runInContext(context, { timeout: 2000 });
            return exports;
        }
        catch (e) {
            loaded.delete(file);
            throw e;
        }
    }
    return { instance(className: string): Runtime { const m = mappings.find(m => m.className === className); if (!m)
            throw new Failure('UnsupportedEvaluation', className, 'Unknown class'); const cls = load(path.resolve(root, m.file))[className]; if (typeof cls !== 'function')
            throw new Failure('UnsupportedEvaluation', className, 'No constructor'); return Object.create(cls.prototype) as Runtime; } };
}
