import ts from 'typescript';
import path from 'node:path';
import fs from 'node:fs';
import { normalize, predicateExpression, type FunctionNode } from './logic.js';
import type { Evidence, FunctionFact, Reference, ScanResult, TypeFact } from './model.js';

function isFunction(node: ts.Node): node is FunctionNode {
  return ts.isFunctionDeclaration(node) || ts.isFunctionExpression(node) || ts.isArrowFunction(node) ||
    ts.isMethodDeclaration(node) || ts.isGetAccessor(node) || ts.isSetAccessor(node) || ts.isConstructorDeclaration(node);
}
export function scan(projectPath: string): ScanResult {
  const requested = path.resolve(projectPath);
  const configPath = fs.existsSync(requested) && fs.statSync(requested).isDirectory() ? path.join(requested, 'tsconfig.json') : requested;
  if (!fs.existsSync(configPath)) throw new Error(`TypeScript config not found: ${configPath}`);
  const root = path.dirname(configPath);
  const slash = (file: string) => file.replaceAll(path.sep, '/');
  const relative = (file: string) => slash(path.relative(root, file));
  const loaded = ts.readConfigFile(configPath, ts.sys.readFile);
  if (loaded.error) throw new Error(ts.flattenDiagnosticMessageText(loaded.error.messageText, '\n'));
  const parsed = ts.parseJsonConfigFileContent(loaded.config, ts.sys, root, { noEmit: true }, configPath);
  if (parsed.errors.length) throw new Error(parsed.errors.map(d => ts.flattenDiagnosticMessageText(d.messageText, '\n')).join('\n'));
  if (!parsed.options.strictNullChecks && !parsed.options.strict)
    throw new Error('Sound finite-domain analysis requires strictNullChecks (or strict) in tsconfig.json');
  if (parsed.options.strictNullChecks === false) throw new Error('strictNullChecks must not be disabled');
  const program = ts.createProgram({ rootNames: parsed.fileNames, options: parsed.options, projectReferences: parsed.projectReferences });
  const checker = program.getTypeChecker();
  function evidence(node: ts.Node, symbol = ''): Evidence {
    const sf = node.getSourceFile();
    const start = node.getStart(sf), end = node.getEnd();
    const a = sf.getLineAndCharacterOfPosition(start), b = sf.getLineAndCharacterOfPosition(end);
    return { file: relative(sf.fileName), symbol, start: { line: a.line + 1, column: a.character + 1, offset: start }, end: { line: b.line + 1, column: b.character + 1, offset: end } };
  }
  function refNode(node: ts.Node, name: string): Reference {
    const location = evidence(node, name);
    return { id: `${location.file}:${location.start.offset}:${name}`, name, evidence: location };
  }
  function resolve(symbol: ts.Symbol): ts.Symbol {
    return symbol.flags & ts.SymbolFlags.Alias ? checker.getAliasedSymbol(symbol) : symbol;
  }
  function reference(symbol: ts.Symbol): Reference | undefined {
    symbol = resolve(symbol);
    const declaration = symbol.declarations?.[0];
    return declaration ? refNode(declaration, symbol.name) : undefined;
  }
  const sourceFiles = program.getSourceFiles().filter(sf => !sf.isDeclarationFile && !program.isSourceFileFromExternalLibrary(sf)).sort((a, b) => a.fileName.localeCompare(b.fileName));
  const files: ts.SourceFile[] = [], skippedFiles: ts.SourceFile[] = [];
  for (const sf of sourceFiles) {
    if (/\.tsx?$/.test(sf.fileName) || /\.[cm]ts$/.test(sf.fileName)) files.push(sf);
    else skippedFiles.push(sf);
  }
  const result: ScanResult = { schemaVersion: 1, category: 'code-facts', project: relative(configPath), files: files.map(f => relative(f.fileName)), types: [], functions: [], diagnostics: [], omissions: [], limitations: [
    'files lists analyzed TS/TSX/MTS/CTS implementation files only; declaration files and external libraries are not enumerated.',
    'No interprocedural control flow, runtime values, dynamic access, business interpretation, or whole-program verification.',
    'References resolve declaration identity; type references cover explicit syntax and parameter/return type symbols, not all transitive types.',
    'Function predicates require one direct return expression; extracted branch conditions describe expressions only.',
    'Source-coordinate IDs are snapshot-specific and change when source text moves.',
    'Only function-local conditions are extracted; top-level executable conditions are outside this PoC.',
    'Primitive/union aliases retain their type expression but their fields are not expanded.',
  ] };
  if (parsed.projectReferences?.length) result.omissions.push({ reason: 'Project references are not recursively scanned; scan each referenced tsconfig separately.' });
  for (const sf of skippedFiles) result.omissions.push({
    reason: 'Unsupported source file extension: only TS/TSX/MTS/CTS implementation files are analyzed.',
    evidence: evidence(sf),
  });
  for (const diagnostic of ts.getPreEmitDiagnostics(program)) {
    const sf = diagnostic.file;
    let location: Evidence | undefined;
    if (sf && diagnostic.start !== undefined) {
      const a = sf.getLineAndCharacterOfPosition(diagnostic.start);
      const end = diagnostic.start + (diagnostic.length ?? 0), b = sf.getLineAndCharacterOfPosition(end);
      location = { file: relative(sf.fileName), symbol: '', start: { line: a.line + 1, column: a.character + 1, offset: diagnostic.start }, end: { line: b.line + 1, column: b.character + 1, offset: end } };
    }
    result.diagnostics.push({ category: ts.DiagnosticCategory[diagnostic.category]!, code: diagnostic.code, message: ts.flattenDiagnosticMessageText(diagnostic.messageText, '\n'), ...(location ? { evidence: location } : {}) });
  }
  function typeFact(node: ts.InterfaceDeclaration | ts.TypeAliasDeclaration | ts.EnumDeclaration): TypeFact {
    const type = checker.getTypeAtLocation(node);
    // Primitive aliases expose library methods through getProperties(); those are not domain fields.
    const objectType = !!(type.flags & ts.TypeFlags.Object);
    const fields = objectType ? checker.getPropertiesOfType(type).flatMap(symbol => {
      const declaration = reference(symbol);
      return declaration ? [{ name: symbol.name, type: checker.typeToString(checker.getTypeOfSymbolAtLocation(symbol, symbol.valueDeclaration ?? node)), declaration }] : [];
    }) : ts.isEnumDeclaration(node) ? node.members.map(member => ({ name: member.name.getText(), type: String(checker.getConstantValue(member) ?? 'computed/unknown'), declaration: refNode(member, member.name.getText()) })) : [];
    return { ...refNode(node, node.name.text), kind: ts.isInterfaceDeclaration(node) ? 'interface' : ts.isEnumDeclaration(node) ? 'enum' : 'alias', type: checker.typeToString(type, node, ts.TypeFormatFlags.InTypeAlias), fields };
  }
  function functionFact(node: FunctionNode): FunctionFact {
    const parent = node.parent;
    const name = ('name' in node && node.name ? node.name.getText() : ts.isVariableDeclaration(parent) ? parent.name.getText() : '<anonymous>');
    const types = new Map<string, Reference>(), properties = new Map<string, Reference>();
    const references: FunctionFact['references'] = [], conditions: FunctionFact['conditions'] = [];
    const signature = checker.getSignatureFromDeclaration(node);
    const returnType = signature ? checker.getReturnTypeOfSignature(signature) : undefined;
    function addType(type: ts.Type) {
      const symbol = type.aliasSymbol ?? type.getSymbol();
      const ref = symbol && reference(symbol);
      if (ref && symbol?.declarations?.some(d => ts.isInterfaceDeclaration(d) || ts.isTypeAliasDeclaration(d) || ts.isEnumDeclaration(d) || ts.isClassDeclaration(d))) types.set(ref.id, ref);
    }
    node.parameters.forEach(p => addType(checker.getTypeAtLocation(p)));
    if (returnType) addType(returnType);
    function condition(expression: ts.Expression, kind: FunctionFact['conditions'][number]['kind']) {
      const ref = refNode(expression, name);
      conditions.push({ id: ref.id, kind, text: expression.getText(), evidence: ref.evidence, normalization: normalize(expression, node, checker, reference) });
    }
    function visit(child: ts.Node) {
      if (child !== node && isFunction(child)) return;
      if (ts.isIdentifier(child)) {
        const symbol = checker.getSymbolAtLocation(child);
        const ref = symbol && reference(symbol);
        if (ref) {
          references.push({ target: ref, evidence: evidence(child, name) });
          if (resolve(symbol!).declarations?.some(d => ts.isTypeAliasDeclaration(d) || ts.isInterfaceDeclaration(d) || ts.isEnumDeclaration(d))) types.set(ref.id, ref);
        }
      }
      if (ts.isPropertyAccessExpression(child)) {
        const symbol = checker.getSymbolAtLocation(child.name), ref = symbol && reference(symbol);
        if (ref) properties.set(ref.id, ref);
        addType(checker.getTypeAtLocation(child.expression));
      }
      if (ts.isElementAccessExpression(child)) result.omissions.push({ reason: 'Computed property access is not included in property facts or logical normalization.', evidence: evidence(child, name) });
      if (ts.isIfStatement(child) || ts.isConditionalExpression(child)) condition(ts.isIfStatement(child) ? child.expression : child.condition, ts.isIfStatement(child) ? 'if' : 'conditional');
      if (ts.isWhileStatement(child) || ts.isDoStatement(child)) condition(child.expression, 'loop');
      if (ts.isForStatement(child) && child.condition) condition(child.condition, 'loop');
      if (ts.isReturnStatement(child) && child.expression) condition(child.expression, 'return');
      ts.forEachChild(child, visit);
    }
    visit(node);
    if (node.body && !ts.isBlock(node.body)) condition(node.body, 'return');
    const expression = predicateExpression(node);
    const predicate = expression ? normalize(expression, node, checker, reference) : { status: 'unsupported' as const, reason: 'Predicate requires a synchronous, non-generator function with exactly one return expression and no other statements.' };
    return { ...refNode(node, name), parameters: node.parameters.map(p => ({ name: p.name.getText(), type: checker.typeToString(checker.getTypeAtLocation(p)), evidence: evidence(p, name) })),
      returnType: returnType ? checker.typeToString(returnType) : 'unknown', referencedTypes: [...types.values()].sort((a, b) => a.id.localeCompare(b.id)),
      properties: [...properties.values()].sort((a, b) => a.id.localeCompare(b.id)), references, conditions, predicate,
      ...(expression ? { predicateEvidence: evidence(expression, name) } : {}) };
  }
  for (const sf of files) {
    function visit(node: ts.Node) {
      if (ts.isInterfaceDeclaration(node) || ts.isTypeAliasDeclaration(node) || ts.isEnumDeclaration(node)) result.types.push(typeFact(node));
      if (ts.isClassDeclaration(node)) result.omissions.push({ reason: 'Class type/field modeling is not implemented; method functions are still scanned.', evidence: evidence(node, node.name?.text) });
      if (ts.isSwitchStatement(node)) result.omissions.push({ reason: 'Switch control flow is not normalized.', evidence: evidence(node) });
      if (isFunction(node)) result.functions.push(functionFact(node));
      ts.forEachChild(node, visit);
    }
    visit(sf);
  }
  if (result.diagnostics.some(d => d.category === 'Error')) {
    const invalid = { status: 'unsupported' as const, reason: 'Compiler errors invalidate finite-domain assumptions; fix project diagnostics first.' };
    for (const fn of result.functions) {
      fn.predicate = invalid;
      for (const c of fn.conditions) c.normalization = invalid;
    }
  }
  return result;
}

export function selectFunction(result: ScanResult, selector: string): FunctionFact {
  const matches = result.functions.filter(f => f.id === selector || f.name === selector);
  if (matches.length !== 1) throw new Error(matches.length ? `Ambiguous function '${selector}'; use a full ID: ${matches.map(f => f.id).join(', ')}` : `Function not found: ${selector}`);
  return matches[0]!;
}
