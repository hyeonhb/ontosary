import ts from 'typescript';

export const evaluatorVersion = 2;
const at = (evidence, source) => evidence?.file === source?.file && evidence?.start.offset === source?.offset;
const compact = text => typeof text === 'string' ? text.trim().replace(/\s+/g, ' ') : undefined;
const isFunction = node => ts.isFunctionDeclaration(node) || ts.isFunctionExpression(node) || ts.isArrowFunction(node) ||
  ts.isMethodDeclaration(node) || ts.isGetAccessor(node) || ts.isSetAccessor(node) || ts.isConstructorDeclaration(node);

// These are deliberately syntactic type-text contracts, not structural assignability.
function typeMatches(actual, expected) {
  if (!expected || Object.keys(expected).length !== 1) throw new Error('Expected exactly one type matcher');
  if (typeof expected.exact === 'string') return compact(actual) === compact(expected.exact);
  if (Array.isArray(expected.unionMembers) && expected.unionMembers.length > 1 &&
      expected.unionMembers.every(x => typeof x === 'string' && /^[A-Za-z_$][\w$]*$/.test(x)) &&
      new Set(expected.unionMembers).size === expected.unionMembers.length) {
    const members = typeof actual === 'string' ? actual.split('|').map(x => x.trim()) : [];
    return JSON.stringify(members.sort()) === JSON.stringify([...expected.unionMembers].sort());
  }
  throw new Error('Unsupported type matcher; use exact text or distinct identifier/keyword union members');
}
function verifyAnchor(location, readSource) {
  if (!location || !Number.isSafeInteger(location.offset) || location.offset < 0 ||
      typeof location.anchor !== 'string' || !location.anchor.length) throw new Error('Missing source/target/use anchor');
  const text = readSource(location.file);
  if (typeof text !== 'string' || text.indexOf(location.anchor) !== location.offset ||
      text.indexOf(location.anchor, location.offset + 1) >= 0 ||
      text.slice(0, location.offset).split('\n').length !== location.line) throw new Error(`Anchor mismatch: ${location.file}:${location.line}`);
  return text;
}
function sourceUse(label, readSource) {
  const text = readSource(label.source.file);
  const sf = ts.createSourceFile(label.source.file, text, ts.ScriptTarget.Latest, true);
  if (sf.parseDiagnostics.length) throw new Error('Cannot adjudicate use in syntactically invalid source');
  let owner, token;
  function visit(node) {
    if (isFunction(node) && node.getStart(sf) === label.source.offset) owner = node;
    if ((ts.isIdentifier(node) || ts.isPrivateIdentifier(node)) && node.getStart(sf) === label.use.offset) token = node;
    ts.forEachChild(node, visit);
  }
  visit(sf);
  if (!owner || !token || label.use.file !== label.source.file) return 'Use must be an identifier in the labeled function';
  // Names in the function header, including parameters, are not body references.
  if (!owner.body || token.getStart(sf) < owner.body.getStart(sf) || token.getEnd() > owner.body.getEnd()) return 'Declaration/header names are not body uses';
  for (let node = token; node && node !== owner; node = node.parent) {
    if (node !== token && isFunction(node)) return 'Use belongs to a nested function';
    if (ts.isTypeNode(node)) return 'Type syntax is outside the runtime-expression reference contract';
  }
  const parent = token.parent;
  const declarationName = parent.name === token && (
    ts.isVariableDeclaration(parent) || ts.isBindingElement(parent) || ts.isParameter(parent) ||
    isFunction(parent) || ts.isClassDeclaration(parent) || ts.isClassExpression(parent) ||
    ts.isTypeAliasDeclaration(parent) || ts.isInterfaceDeclaration(parent) || ts.isEnumDeclaration(parent) ||
    ts.isEnumMember(parent) || ts.isPropertyDeclaration(parent) || ts.isPropertyAssignment(parent));
  if (declarationName) return 'Declaration/property-key names are not runtime-expression uses';
  if (label.usageKind === 'call') {
    let callee = token;
    if (ts.isPropertyAccessExpression(callee.parent) && callee.parent.name === callee) callee = callee.parent;
    while (ts.isParenthesizedExpression(callee.parent)) callee = callee.parent;
    if (!ts.isCallExpression(callee.parent) || callee.parent.expression !== callee) return 'The specified use is a reference, not a call callee';
  } else if (label.usageKind !== 'reference') throw new Error('usageKind must be call or reference');
  return undefined;
}

/** V2 evaluates only explicit contracts; free-text context remains unverified. */
export function evaluateLabel(label, facts, { readSource } = {}) {
  const checks = [], unverified = label.unverified ?? [];
  const out = (status, evidence = [], reason, extra = {}) => ({ id: label.id, evaluatorVersion, status, checks, unverified,
    evidence, ...(reason ? { reason } : {}), ...extra });
  const check = (field, expected, actual, passed = actual === expected) => {
    checks.push({ field, expected, actual, passed });
    return passed;
  };
  if (label.contractVersion !== 2 || typeof readSource !== 'function') return out('indeterminate', [], 'V2 contract and source reader are required');
  if (!facts || facts.diagnostics.some(d => d.category === 'Error')) return out('indeterminate', [], 'Scan missing or compiler errors');
  try {
    for (const location of [label.source, label.target, label.use, label.other, label.parameterSource, label.conditionSource].filter(Boolean)) verifyAnchor(location, readSource);
    if (['reference', 'property'].includes(label.kind) && (!label.use || !label.target)) throw new Error('Explicit use and target anchors are required');
    if (['type', 'field', 'distinct-types'].includes(label.kind) && !label.expectedKind) throw new Error('Explicit expectedKind is required');
    if (label.kind === 'parameter' && !label.expectedType) throw new Error('Explicit expectedType is required');
    if (label.expectedType) typeMatches('', label.expectedType); // Validate the matcher even when the fact is missing.
  } catch (error) { return out('indeterminate', [], error.message); }
  const typeKind = ['type', 'field', 'distinct-types'].includes(label.kind);
  const matches = (typeKind ? facts.types : facts.functions).filter(f => at(f.evidence, label.source));
  if (matches.length > 1) return out('indeterminate', matches.map(f => f.evidence), 'Ambiguous declaration');
  if (!matches.length) {
    const omissions = facts.omissions.filter(o => at(o.evidence, label.source));
    return omissions.length ? out('unsupported', omissions.map(o => o.evidence), omissions.map(o => o.reason).join('; ')) : out('missing', [], 'No fact at the labeled declaration');
  }
  const fact = matches[0];
  check('declaration.file+offset', label.source, fact.evidence, true);
  if (!check('name', label.name, fact.name)) return out('mislinked', [fact.evidence], 'Wrong declaration name');
  if (label.expectedKind && !check('kind', label.expectedKind, fact.kind)) return out('mismatch', [fact.evidence], 'Wrong type declaration kind');
  if (label.kind === 'function') return out('correct', [fact.evidence]);
  if (label.kind === 'type') {
    if (label.expectedType && !check('type', label.expectedType, fact.type, typeMatches(fact.type, label.expectedType))) return out('mismatch', [fact.evidence], 'Type text violates the label contract');
    return out('correct', [fact.evidence]);
  }
  if (label.kind === 'parameter') {
    const ps = fact.parameters.filter(p => p.name === label.parameter && (!label.parameterSource || at(p.evidence, label.parameterSource)));
    if (ps.length !== 1) return out(ps.length ? 'indeterminate' : 'missing', [], 'Parameter not uniquely located');
    return out(check('parameter.type', label.expectedType, ps[0].type, typeMatches(ps[0].type, label.expectedType)) ? 'correct' : 'mismatch', [ps[0].evidence]);
  }
  if (label.kind === 'field') {
    const field = fact.fields.find(f => f.name === label.field);
    return !field ? out('missing') : out(check('field.type', label.fieldType, field.type) ? 'correct' : 'mismatch', [field.declaration.evidence]);
  }
  if (label.kind === 'condition') {
    const condition = fact.conditions.find(c => c.text === label.text && c.kind === label.conditionKind && (!label.conditionSource || at(c.evidence, label.conditionSource)));
    if (!condition) return out('missing', [], 'No condition with the exact kind/text/location');
    check('condition.kind+text', { kind: label.conditionKind, text: label.text }, { kind: condition.kind, text: condition.text }, true);
    return out('correct', [condition.evidence], `Extraction only; normalization: ${condition.normalization.status}`);
  }
  if (label.kind === 'distinct-types') {
    const other = facts.types.filter(t => at(t.evidence, label.other));
    if (other.length !== 1) return out(other.length ? 'indeterminate' : 'missing');
    const valid = check('other.name', label.otherName, other[0].name) &&
      check('other.kind', label.expectedKind, other[0].kind) && check('distinct IDs', true, other[0].id !== fact.id);
    return out(valid ? 'correct' : 'mismatch', [fact.evidence, other[0].evidence]);
  }
  if (['reference', 'property'].includes(label.kind)) {
    let invalid;
    try { invalid = sourceUse(label, readSource); }
    catch (error) { return out('indeterminate', [], error.message); }
    if (!check('source use role', label.usageKind, invalid ?? label.usageKind, !invalid)) return out('mismatch', [fact.evidence], invalid);
    const edges = fact.references.filter(r => at(r.evidence, label.use));
    if (!edges.length) return out('missing', [fact.evidence], 'No reference at the exact use location');
    if (edges.length !== 1) return out('indeterminate', edges.map(r => r.evidence), 'Ambiguous use evidence');
    const edge = edges[0], evidence = [fact.evidence, edge.evidence, edge.target.evidence];
    const details = { useEvidence: edge.evidence, targetEvidence: edge.target.evidence };
    if (!check('target.file+offset', label.target, edge.target.evidence, at(edge.target.evidence, label.target))) return out('mislinked', evidence, 'Use resolves to a different declaration', details);
    if (label.kind === 'property' && !fact.properties.some(p => at(p.evidence, label.target))) return out('missing', evidence, 'Expected property fact absent', details);
    return out('correct', evidence, 'Syntactic source use and fact edge; not a runtime execution or call-graph proof', details);
  }
  return out('indeterminate', [], `Unknown label kind: ${label.kind}`);
}
