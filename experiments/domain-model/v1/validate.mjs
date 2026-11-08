import { sha } from './observe.mjs';
export function validateModel(model, facts, candidates, readSource) {
  if (!model || !Array.isArray(model.items) || !Array.isArray(model.approvedKnowledge) || !Array.isArray(facts) || !Array.isArray(candidates)) return { valid: false, semanticApproval: 'not-assessed', errors: [{code:'invalid-schema',id:'model',detail:'Record collections must be arrays'}], staleFacts: [], staleItems: [], requiresReview: true };
  const errors = [], staleFacts = new Set(), ids = new Set();
  const error = (code, id, detail) => errors.push({ code, id, detail });
  for (const row of [...facts, ...candidates, ...model.items, ...model.approvedKnowledge]) {
    if (!row.id || ids.has(row.id)) error('duplicate-or-missing-id', row.id, 'IDs must be unique across all records');
    ids.add(row.id);
  }
  const factIds = new Set(facts.map(f => f.id)), candidateIds = new Set(candidates.map(c => c.id)), itemIds = new Set(model.items.map(i => i.id));
  if (!model.revision || !model.scope || !model.author || !model.useContract) error('missing-provenance', 'model', 'revision/scope/author/useContract required');
  for (const f of facts) {
    if (!f.kind || !f.author || !f.method || !f.scope || !f.support || !f.claim) error('missing-provenance', f.id, 'kind/author/method/scope/support/claim required');
    const evidence = Array.isArray(f.evidence) ? f.evidence : [f.evidence];
    if (!evidence.length) error('missing-evidence', f.id, 'At least one source anchor required');
    for (const e of evidence) {
      if (!e?.file || !e.symbol || !e.anchor || !/^[a-f0-9]{64}$/.test(e.sha256 ?? '') || !Number.isInteger(e.offset) || e.offset < 0 || !Number.isInteger(e.line)) {
        error('missing-provenance', f.id, 'file/symbol/hash/anchor/offset/line required'); continue;
      }
      let source; try { source = readSource(e.file); } catch { /* unavailable input is stale */ }
      if (typeof source !== 'string' || sha(source) !== e.sha256 || source.slice(e.offset, e.offset + e.anchor.length) !== e.anchor || source.slice(0,e.offset).split('\n').length !== e.line) {
        staleFacts.add(f.id); error('stale-evidence', f.id, e.file);
      }
    }
  }
  for (const c of candidates) {
    if (!c.factRefs?.length) error('missing-evidence', c.id, 'Candidate requires cell fact references');
    for (const id of c.factRefs ?? []) if (!factIds.has(id)) error('broken-fact-ref', c.id, id);
  }
  for (const item of model.items) {
    if (!item.label || !item.kind || !item.author || !item.interpretation || !item.unverified?.length || !item.factRefs?.length || !Array.isArray(item.candidateRefs) || !Array.isArray(item.relatedItems) || !Object.hasOwn(item,'intendedPolicy')) error('missing-model-provenance', item.id, 'Draft interpretation, source refs and open questions required');
    if (!['pending-review','approved'].includes(item.status)) error('invalid-status',item.id,item.status);
    for (const id of item.factRefs ?? []) if (!factIds.has(id)) error('broken-fact-ref', item.id, id);
    for (const id of item.candidateRefs ?? []) if (!candidateIds.has(id)) error('broken-candidate-ref', item.id, id);
    for (const id of item.relatedItems ?? []) if (!itemIds.has(id)) error('broken-model-ref', item.id, id);
    if (item.status === 'approved' && !model.approvedKnowledge.some(a => a.itemRef === item.id)) error('missing-approval',item.id,'Actual human decision record required');
  }
  for (const a of model.approvedKnowledge) {
    const d = a.decision;
    if (!itemIds.has(a.itemRef) || !d?.actor || d.actorKind !== 'human' || !d.rationale || !d.evidenceRefs?.length || !d.at || !Number.isFinite(Date.parse(d.at))) error('invalid-approval', a.id, 'Human decision actor/rationale/evidence/timestamp required; syntax does not authenticate review');
    for (const id of d?.evidenceRefs ?? []) if (!factIds.has(id)) error('broken-fact-ref',a.id,id);
  }
  const staleCandidates = new Set(candidates.filter(c => c.factRefs?.some(f => staleFacts.has(f))).map(c => c.id));
  const staleItems = new Set(model.items.filter(i => i.factRefs?.some(f => staleFacts.has(f)) || i.candidateRefs?.some(c => staleCandidates.has(c))).map(i => i.id));
  let changed = true;
  while (changed) { changed = false; for (const i of model.items) if (!staleItems.has(i.id) && i.relatedItems?.some(id => staleItems.has(id))) { staleItems.add(i.id); changed = true; } }
  return { valid: errors.length === 0, semanticApproval: 'not-assessed; formal records cannot authenticate human review', errors, staleFacts: [...staleFacts].sort(), staleItems: [...staleItems].sort(), requiresReview: errors.length > 0 };
}
