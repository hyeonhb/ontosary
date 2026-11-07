/** Match source-authored claims by file + exact declaration offset, never by name alone. */
const at = (evidence, source) => evidence?.file === source.file && evidence?.start.offset === source.offset;
export function evaluateLabel(label, facts) {
  const out = (status, evidence = [], reason) => ({ id: label.id, status, evidence, ...(reason ? { reason } : {}) });
  if (!facts || facts.diagnostics.some(d => d.category === 'Error')) return out('indeterminate', [], 'Scan failed or compiler errors prevent reliable label adjudication.');
  const typeKind = ['type', 'field', 'distinct-types'].includes(label.kind);
  const pool = typeKind ? facts.types : facts.functions;
  const matches = pool.filter(f => at(f.evidence, label.source));
  if (matches.length > 1) return out('indeterminate', matches.map(f => f.evidence), 'Multiple facts at the labeled declaration.');
  if (matches.length === 0) {
    const omissions = facts.omissions.filter(o => at(o.evidence, label.source));
    return omissions.length ? out('unsupported', omissions.map(o => o.evidence), omissions.map(o => o.reason).join('; ')) : out('missing', [], 'No fact at the source-authored declaration.');
  }
  const fact = matches[0];
  if (fact.name !== label.name) return out('mislinked', [fact.evidence], 'Declaration name disagrees at the labeled location.');
  if (label.kind === 'function' || label.kind === 'type') return out('correct', [fact.evidence]);
  if (label.kind === 'parameter') {
    const p = fact.parameters.find(p => p.name === label.parameter);
    return p ? out('correct', [p.evidence]) : out('missing');
  }
  if (label.kind === 'field') {
    const field = fact.fields.find(f => f.name === label.field);
    return !field ? out('missing') : out(field.type === label.fieldType ? 'correct' : 'mislinked', [field.declaration.evidence]);
  }
  if (label.kind === 'condition') {
    const condition = fact.conditions.find(c => c.text === label.text && c.kind === label.conditionKind);
    // This label is extraction coverage. Normalization support is reported separately.
    return condition ? out('correct', [condition.evidence], `Normalization: ${condition.normalization.status}`) : out('missing');
  }
  if (label.kind === 'distinct-types') {
    const other = facts.types.filter(t => at(t.evidence, label.other));
    return other.length !== 1 ? out('missing') : out(other[0].name === label.otherName && other[0].id !== fact.id ? 'correct' : 'mislinked', [fact.evidence, other[0].evidence]);
  }
  if (label.kind === 'reference' || label.kind === 'property') {
    const refs = label.kind === 'reference' ? fact.references.filter(r => r.evidence.file !== r.target.evidence.file || r.evidence.start.offset !== r.target.evidence.start.offset).map(r => r.target) : fact.properties;
    const target = refs.find(r => at(r.evidence, label.target));
    if (target) return out('correct', [fact.evidence, target.evidence]);
    // Absence of the expected edge does not itself prove a wrong edge. Report any same-name edge separately for review.
    return out('missing', [fact.evidence], 'Expected declaration edge not extracted; inspect raw references for other targets.');
  }
  throw new Error(`Unknown label kind: ${label.kind}`);
}
