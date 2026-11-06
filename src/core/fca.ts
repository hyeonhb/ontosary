import type { Concept, FormalContext, ScanResult } from './model.js';
const subset = (a: string[], b: string[]) => a.every(x => b.includes(x));

export function buildContext(scan: ScanResult): FormalContext {
  const incidence: Record<string, string[]> = Object.create(null);
  for (const fn of scan.functions) {
    incidence[fn.id] = [...new Set([
      ...fn.referencedTypes.map(t => `type:${t.id}`),
      ...fn.properties.map(p => `property:${p.id}`),
      `returns:${fn.returnType}`,
      ...fn.conditions.flatMap(c => c.normalization.status === 'supported' ? c.normalization.variables.map(v => `condition:${v.declaration.id}`) : []),
    ])].sort();
  }
  return { objects: Object.keys(incidence).sort(), attributes: [...new Set(Object.values(incidence).flat())].sort(), incidence };
}

/** Ganter's NextClosure enumerates closed intents, with bounded input and output. */
export function formalConcepts(context: FormalContext, options: { maxConcepts?: number; maxObjects?: number; maxAttributes?: number } = {}) {
  const { objects, attributes, incidence } = context;
  const limits = { maxConcepts: options.maxConcepts ?? 256, maxObjects: options.maxObjects ?? 128, maxAttributes: options.maxAttributes ?? 64 };
  for (const [key, value] of Object.entries(limits)) if (!Number.isSafeInteger(value) || value < 1) throw new Error(`${key} must be a positive safe integer`);
  if (objects.length > limits.maxObjects || attributes.length > limits.maxAttributes) throw new Error(`Formal context exceeds limits: ${objects.length} objects / ${attributes.length} attributes (limits ${limits.maxObjects}/${limits.maxAttributes})`);
  if (new Set(objects).size !== objects.length || new Set(attributes).size !== attributes.length) throw new Error('Formal context has duplicate objects or attributes');
  if (objects.some(o => !Object.hasOwn(incidence, o) || incidence[o]!.some(a => !attributes.includes(a))) || Object.keys(incidence).some(o => !objects.includes(o))) throw new Error('Invalid incidence relation');
  const extent = (intent: string[]) => objects.filter(o => subset(intent, incidence[o]!));
  const closure = (intent: string[]) => { const members = extent(intent); return attributes.filter(a => members.every(o => incidence[o]!.includes(a))); };
  const concepts: Concept[] = [];
  let intent = closure([]), truncated = false;
  while (true) {
    concepts.push({ id: `formal-${concepts.length}`, extent: extent(intent), intent });
    let next: string[] | undefined;
    for (let i = attributes.length - 1; i >= 0; i--) {
      const attribute = attributes[i]!;
      if (intent.includes(attribute)) continue;
      const candidate = closure([...intent.filter(a => attributes.indexOf(a) < i), attribute]);
      if (attributes.slice(0, i).every(a => candidate.includes(a) === intent.includes(a))) { next = candidate; break; }
    }
    if (!next) break;
    if (concepts.length >= limits.maxConcepts) { truncated = true; break; }
    intent = next;
  }
  return { concepts, truncated, limits };
}
export function discoverConcepts(scan: ScanResult) {
  const context = buildContext(scan), formal = formalConcepts(context);
  const candidates = formal.concepts.filter(c => c.extent.length >= 2 && c.intent.some(a => !a.startsWith('returns:'))).map(c => ({ ...c,
    category: 'discovered-candidate' as const, reviewStatus: 'unreviewed' as const,
    evidence: c.extent.map(id => scan.functions.find(f => f.id === id)!.evidence) }));
  const relations = candidates.flatMap(general => candidates.filter(specific => specific.id !== general.id && subset(general.intent, specific.intent)).map(specific => ({ general: general.id, specific: specific.id, kind: 'strict-generalization' as const })));
  return { schemaVersion: 1, category: 'discovered-candidates', context, ...formal, candidates, relations,
    relationScope: 'All strict order relations among emitted candidates; not Hasse cover edges.',
    filter: 'At least two functions and at least one shared type, property, or condition-field attribute. Return type alone is insufficient.',
    approvedKnowledge: [], limitations: ['Formal groups are not confirmed business concepts.', 'Truncated output is an incomplete prefix, not a complete lattice.', 'High-frequency utility attributes may still form unhelpful groups.'] };
}
