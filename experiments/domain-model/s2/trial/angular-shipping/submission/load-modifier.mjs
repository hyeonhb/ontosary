// The unobserved application is not loaded. Compare its declarations to the parent
// before linking the submitted module to the dependencies exercised by the six cases.
import ts from 'typescript';
import { posix as path } from 'node:path';
import { modifierPath } from '../load-controls.mjs';

function parse(name, source) {
    const file = ts.createSourceFile(name, source, ts.ScriptTarget.Latest, true);
    if (file.parseDiagnostics.length) throw Error('TypeScript parse: ' + file.parseDiagnostics[0].messageText);
    return file;
}

const isFunction = node => ts.isFunctionDeclaration(node) && node.name && node.body;
const isMethod = node => ts.isMethodDeclaration(node) && ts.isIdentifier(node.name) && node.body;
const nameOf = node => node.name?.text;
const isModifier = node => ts.isClassDeclaration(node) && nameOf(node) === 'OrderModifier';

export function submittedModifier(source, base, additions, changedLines, read, bindings, calls) {
    const original = parse(modifierPath, base);
    const submitted = parse(modifierPath, source);
    const originalClass = original.statements.find(isModifier);
    const originalMethods = new Set(originalClass.members.map(nameOf));
    const originalFunctions = new Set(original.statements.filter(isFunction).map(nameOf));
    const knownImports = new Map();
    for (const imp of original.statements.filter(ts.isImportDeclaration)) {
        const names = imp.importClause?.namedBindings?.elements ?? [];
        knownImports.set(imp.moduleSpecifier.text, new Set(names.map(n => (n.propertyName ?? n.name).text)));
    }

    const entry = 'cancelOrderByOrderLines';
    const tracked = new Set();
    const modules = new Map();
    const helpers = new Set(additions);
    const helperFile = (from, spec) => path.normalize(path.join(path.dirname(from), spec)) + '.ts';
    const isHelperImport = (from, node) => ts.isImportDeclaration(node) &&
        node.moduleSpecifier.text.startsWith('.') && helpers.has(helperFile(from, node.moduleSpecifier.text));

    // Mask the exercised method body and the added callable helpers. All other
    // declarations, including constructor, decorators and original imports, must agree.
    const printer = ts.createPrinter({removeComments:true});
    function unobserved(file) {
        const project = context => root => {
            function visit(node) {
                if (isHelperImport(modifierPath, node)) return undefined;
                if (isFunction(node) && node.parent === file && !originalFunctions.has(nameOf(node))) return undefined;
                if (isMethod(node) && isModifier(node.parent)) {
                    if (!originalMethods.has(nameOf(node)) && !ts.getDecorators(node)?.length) return undefined;
                    if (nameOf(node) === entry) {
                        return ts.factory.updateMethodDeclaration(node, node.modifiers, node.asteriskToken,
                            node.name, node.questionToken, node.typeParameters, node.parameters, node.type,
                            ts.factory.createBlock([]));
                    }
                }
                return ts.visitEachChild(node, visit, context);
            }
            return ts.visitNode(root, visit);
        };
        const transform = ts.transform(file, [project]);
        try { return printer.printFile(transform.transformed[0]); }
        finally { transform.dispose(); }
    }
    if (unobserved(original) !== unobserved(submitted)) {
        throw Error('Unobserved declaration changed in ' + modifierPath);
    }

    function compile(file) {
        const helper = file.fileName !== modifierPath;
        if (helper && !file.statements.every(n => isFunction(n) || ts.isInterfaceDeclaration(n) ||
            ts.isTypeAliasDeclaration(n) || (ts.isImportDeclaration(n) &&
            (n.importClause?.isTypeOnly || isHelperImport(file.fileName, n))))) {
            throw Error('Unsupported declaration in submitted helper: ' + file.fileName);
        }
        const instrument = context => root => {
            function hit(id) {
                tracked.add(id);
                return ts.factory.createCallExpression(ts.factory.createIdentifier('__recordShippingCall'),
                    undefined, [ts.factory.createStringLiteral(id)]);
            }
            function visit(node) {
                if (ts.isDecorator(node)) return undefined;
                // Count changed statement expressions even if their enclosing method ran.
                // The comma expression preserves the value and receiver of the original call.
                const parent = node.parent;
                const isValue = parent && ((ts.isReturnStatement(parent) || ts.isThrowStatement(parent) ||
                    ts.isExpressionStatement(parent)) && parent.expression === node ||
                    ts.isVariableDeclaration(parent) && parent.initializer === node);
                if (isValue) {
                    const start = file.getLineAndCharacterOfPosition(node.getStart()).line + 1;
                    const end = file.getLineAndCharacterOfPosition(node.end).line + 1;
                    if (helper || changedLines.some(line => start <= line && line <= end)) {
                        const id = file.fileName + '@' + start + '.' + node.getStart();
                        return ts.factory.createParenthesizedExpression(ts.factory.createComma(
                            hit(id), ts.visitEachChild(node, visit, context)));
                    }
                }
                const method = isMethod(node) && isModifier(node.parent);
                if ((method && (nameOf(node) === entry || !originalMethods.has(nameOf(node)))) ||
                    (isFunction(node) && node.parent === root && (helper || !originalFunctions.has(nameOf(node))))) {
                    const id = file.fileName + '#' + nameOf(node);
                    const statements = ts.visitNodes(node.body.statements, visit);
                    const body = ts.factory.updateBlock(node.body, [ts.factory.createExpressionStatement(hit(id)), ...statements]);
                    if (method) return ts.factory.updateMethodDeclaration(node, node.modifiers, node.asteriskToken,
                        node.name, node.questionToken, node.typeParameters, node.parameters, node.type, body);
                    return ts.factory.updateFunctionDeclaration(node, node.modifiers, node.asteriskToken, node.name,
                        node.typeParameters, node.parameters, node.type, body);
                }
                return ts.visitEachChild(node, visit, context);
            }
            return ts.visitNode(root, visit);
        };
        const {outputText} = ts.transpileModule(file.text, {
            fileName:file.fileName, compilerOptions:{target:ts.ScriptTarget.ES2022, module:ts.ModuleKind.CommonJS},
            transformers:{before:[instrument]},
        });
        const exports = {};
        modules.set(file.fileName, exports);
        function require(spec) {
            const target = helperFile(file.fileName, spec);
            if (spec.startsWith('.') && helpers.has(target)) {
                return modules.get(target) ?? compile(parse(target, read(target)));
            }
            if (!helper && knownImports.has(spec)) {
                return new Proxy({}, {get(_, key) {
                    if (knownImports.get(spec).has(key) && Object.hasOwn(bindings, key)) return bindings[key];
                    throw Error('Unobserved dependency: ' + spec + '.' + String(key));
                }});
            }
            throw Error('Unobserved import: ' + spec);
        }
        Function('exports', 'require', '__recordShippingCall', outputText)(exports, require, id => {
            calls.set(id, (calls.get(id) ?? 0) + 1);
        });
        return exports;
    }
    const {OrderModifier} = compile(submitted);
    for (const name of additions) {
        if (!modules.has(name)) throw Error('Added source was not loaded: ' + name);
    }
    return {OrderModifier, tracked};
}
