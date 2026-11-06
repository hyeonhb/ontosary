import ts from 'typescript';
import type { Comparison, Logic, Normalization, Reference, Value, Variable } from './model.js';

export type FunctionNode = ts.FunctionDeclaration | ts.FunctionExpression | ts.ArrowFunction | ts.MethodDeclaration | ts.GetAccessorDeclaration | ts.SetAccessorDeclaration | ts.ConstructorDeclaration;
const unsupported = (reason: string): Normalization => ({ status: 'unsupported', reason });
const unwrap = (node: ts.Expression): ts.Expression => ts.isParenthesizedExpression(node) ? unwrap(node.expression) : node;

/** Resolve the declared input type, never a control-flow-narrowed occurrence. */
export function normalize(expression: ts.Expression, fn: FunctionNode, checker: ts.TypeChecker,
  reference: (symbol: ts.Symbol) => Reference | undefined): Normalization {
  // TS erases this parameter; AST positions would not be runtime argN positions.
  // Apply the same conservative policy to full predicates and branch conditions.
  if (fn.parameters.some(p => ts.isIdentifier(p.name) && p.name.text === 'this'))
    return unsupported('Explicit this parameters are unsupported: this is type-only and is not a positional runtime argument.');
  const variables = new Map<string, Variable>();
  function variable(raw: ts.Expression): Variable {
    const node = unwrap(raw);
    const root = ts.isPropertyAccessExpression(node) ? unwrap(node.expression) : node;
    if (!ts.isIdentifier(root) || (ts.isPropertyAccessExpression(node) && node.questionDotToken))
      throw new Error('Only direct parameters and one-level, non-optional parameter properties are supported');
    const index = fn.parameters.findIndex(p => ts.isIdentifier(p.name) && checker.getSymbolAtLocation(p.name) === checker.getSymbolAtLocation(root));
    const parameter = fn.parameters[index];
    if (!parameter || parameter.dotDotDotToken || parameter.questionToken || parameter.initializer)
      throw new Error('Input must be a required parameter without a default or rest binding');
    let type = checker.getTypeAtLocation(parameter);
    // Cartesian enumeration cannot preserve correlations inside discriminated unions.
    if (ts.isPropertyAccessExpression(node) && type.isUnion()) throw new Error('Union object inputs require relational constraints');
    let symbol = checker.getSymbolAtLocation(parameter.name);
    if (ts.isPropertyAccessExpression(node)) {
      symbol = type.getProperty(node.name.text);
      if (!symbol || (symbol.flags & ts.SymbolFlags.Optional) || symbol.declarations?.some(d => ts.isGetAccessor(d) || ts.isSetAccessor(d)))
        throw new Error('Optional, unresolved, or accessor properties are unsupported');
      type = checker.getTypeOfSymbolAtLocation(symbol, symbol.valueDeclaration ?? symbol.declarations![0]!);
    }
    const parts = type.isUnion() ? type.types : [type];
    const domain: Value[] = [];
    for (const part of parts) {
      if (part.isStringLiteral()) domain.push(part.value);
      else if ((part.flags & ts.TypeFlags.EnumLiteral) && part.isNumberLiteral()) domain.push(part.value);
      else throw new Error('Input domain must be a finite string-literal union or constant enum');
    }
    const declaration = symbol && reference(symbol);
    if (!declaration || !domain.length) throw new Error('Missing input declaration or finite domain');
    const key = `arg${index}${ts.isPropertyAccessExpression(node) ? `.${node.name.text}` : ''}`;
    const result: Variable = { key, sourceName: node.getText(), domain: [...new Set(domain)].sort((a, b) => String(a).localeCompare(String(b))), declaration };
    variables.set(key, result);
    return result;
  }
  function literal(raw: ts.Expression): Value | undefined {
    const node = unwrap(raw);
    if (ts.isStringLiteral(node)) return node.text;
    if (ts.isPropertyAccessExpression(node)) {
      const symbol = checker.getSymbolAtLocation(node.name);
      if (symbol?.flags && (symbol.flags & ts.SymbolFlags.EnumMember)) {
        // A member's type does not make its receiver a constant: getEnum().A,
        // e?.A and (e as typeof E).A still evaluate user expressions at runtime.
        const receiver = unwrap(node.expression);
        if (node.questionDotToken || !ts.isIdentifier(receiver))
          throw new Error('Enum constants require a direct, non-optional enum identifier receiver.');
        const receiverSymbol = checker.getSymbolAtLocation(receiver);
        const target = receiverSymbol && (receiverSymbol.flags & ts.SymbolFlags.Alias
          ? checker.getAliasedSymbol(receiverSymbol) : receiverSymbol);
        if (!target?.declarations?.some(ts.isEnumDeclaration))
          throw new Error('Enum receiver must resolve to an enum declaration, not an enum-typed value.');
        const declaration = symbol.valueDeclaration;
        if (declaration && ts.isEnumMember(declaration)) return checker.getConstantValue(declaration);
      }
    }
    return undefined;
  }
  function visit(raw: ts.Expression): Logic {
    const node = unwrap(raw);
    if (node.kind === ts.SyntaxKind.TrueKeyword || node.kind === ts.SyntaxKind.FalseKeyword)
      return { op: 'constant', value: node.kind === ts.SyntaxKind.TrueKeyword };
    if (ts.isPrefixUnaryExpression(node) && node.operator === ts.SyntaxKind.ExclamationToken)
      return { op: 'not', operand: visit(node.operand) };
    if (ts.isBinaryExpression(node)) {
      const operator = node.operatorToken.kind;
      if (operator === ts.SyntaxKind.AmpersandAmpersandToken || operator === ts.SyntaxKind.BarBarToken)
        return { op: operator === ts.SyntaxKind.AmpersandAmpersandToken ? 'and' : 'or', left: visit(node.left), right: visit(node.right) };
      if (operator === ts.SyntaxKind.EqualsEqualsEqualsToken || operator === ts.SyntaxKind.ExclamationEqualsEqualsToken) {
        const right = literal(node.right), left = literal(node.left);
        if (right !== undefined && left !== undefined)
          return { op: 'constant', value: operator === ts.SyntaxKind.EqualsEqualsEqualsToken ? left === right : left !== right };
        const value = right ?? left;
        if (value === undefined) throw new Error('Equality requires a string literal or constant enum member');
        const input = variable(right !== undefined ? node.left : node.right);
        return { op: operator === ts.SyntaxKind.EqualsEqualsEqualsToken ? 'eq' : 'neq', variable: input.key, value };
      }
    }
    throw new Error(`Unsupported expression: ${ts.SyntaxKind[node.kind]}`);
  }
  try {
    const logic = visit(expression);
    return { status: 'supported', logic, variables: [...variables.values()].sort((a, b) => a.key.localeCompare(b.key)), assumptions: [
      'Inputs obey their declared TypeScript finite domains at runtime.',
      'Properties are stable plain data: no getters, proxies, mutation, or other side effects during evaluation.',
      'Enumerated input fields are independent; no additional business constraints are assumed.',
      'This expression is evaluated in isolation; surrounding control flow is not modeled.',
    ] };
  } catch (error) { return unsupported(error instanceof Error ? error.message : String(error)); }
}

export function predicateExpression(fn: FunctionNode): ts.Expression | undefined {
  if (fn.modifiers?.some(m => m.kind === ts.SyntaxKind.AsyncKeyword) || ('asteriskToken' in fn && fn.asteriskToken)) return;
  if (fn.parameters.some(p => p.initializer || p.dotDotDotToken || !ts.isIdentifier(p.name))) return;
  if (!fn.body) return;
  if (!ts.isBlock(fn.body)) return fn.body;
  if (fn.body.statements.length !== 1) return;
  const statement = fn.body.statements[0]!;
  return ts.isReturnStatement(statement) ? statement.expression : undefined;
}
export function evaluate(logic: Logic, input: Record<string, Value>): boolean {
  switch (logic.op) {
    case 'constant': return logic.value;
    case 'eq': return input[logic.variable] === logic.value;
    case 'neq': return input[logic.variable] !== logic.value;
    case 'and': return evaluate(logic.left, input) && evaluate(logic.right, input);
    case 'or': return evaluate(logic.left, input) || evaluate(logic.right, input);
    case 'not': return !evaluate(logic.operand, input);
  }
}

/** sameInput is an explicit caller assertion, never inferred from spelling or type shape. */
export function compare(left: Normalization, right: Normalization,
  options: { sameInput?: boolean; maxAssignments?: number } = {}): Comparison {
  const base = { evaluatedAssignments: 0, assumptions: [] as string[] };
  if (left.status !== 'supported' || right.status !== 'supported')
    return { ...base, status: 'Unsupported', reason: [left, right].filter(x => x.status === 'unsupported').map(x => x.reason).join('; ') };
  if (!options.sameInput) return { ...base, status: 'Unknown', reason: 'Explicit same-input assertion required: positional arguments and property paths must identify the same input.' };
  const assumptions = [...new Set([...left.assumptions, ...right.assumptions]),
    'Caller asserts identical positional inputs and property paths on both sides; this does not assert a shared business policy.'];
  const variables = new Map<string, Variable>();
  for (const v of [...left.variables, ...right.variables]) {
    const previous = variables.get(v.key);
    if (previous && JSON.stringify(previous.domain) !== JSON.stringify(v.domain))
      return { ...base, assumptions, status: 'Unknown', reason: `Incompatible finite domains for ${v.key}` };
    variables.set(v.key, v);
  }
  const ordered = [...variables.values()].sort((a, b) => a.key.localeCompare(b.key));
  const max = options.maxAssignments ?? 4096;
  if (!Number.isSafeInteger(max) || max < 1) throw new Error('maxAssignments must be a positive safe integer');
  const size = ordered.reduce((n, v) => n * v.domain.length, 1);
  if (!Number.isSafeInteger(size) || size > max) return { ...base, assumptions, status: 'Unknown', reason: `Enumeration limit exceeded (${size} > ${max})` };
  const leftLogic = left.logic, rightLogic = right.logic;
  let leftOnly: Record<string, Value> | undefined, rightOnly: Record<string, Value> | undefined;
  let evaluatedAssignments = 0;
  function enumerate(index: number, input: Record<string, Value>): void {
    const v = ordered[index];
    if (v) { for (const value of v.domain) enumerate(index + 1, { ...input, [v.key]: value }); return; }
    evaluatedAssignments++;
    const a = evaluate(leftLogic, input), b = evaluate(rightLogic, input);
    if (a && !b && !leftOnly) leftOnly = input;
    if (!a && b && !rightOnly) rightOnly = input;
  }
  enumerate(0, {});
  const equivalent = !leftOnly && !rightOnly;
  return { status: equivalent ? 'Equivalent' : !leftOnly || !rightOnly ? 'Implies' : 'Different', equivalent,
    leftImpliesRight: !leftOnly, rightImpliesLeft: !rightOnly,
    ...(!equivalent && (!leftOnly || !rightOnly) ? { direction: !leftOnly ? 'left-to-right' as const : 'right-to-left' as const } : {}),
    ...(leftOnly || rightOnly ? { counterexample: leftOnly ?? rightOnly } : {}),
    ...(leftOnly ? { leftOnly } : {}), ...(rightOnly ? { rightOnly } : {}), evaluatedAssignments, assumptions };
}
