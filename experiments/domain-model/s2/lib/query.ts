import type { Model } from './model.js';
export type Lookup<T> = {
    status: 'Found';
    value: T;
} | {
    status: 'NotFound';
    id: string;
};
export function indexBundle(model: Model, evidence: ReadonlyMap<string, unknown>) {
    const m = structuredClone(model), items = new Map(m.items.map(i => [i.id, i])), facts = new Map(m.facts.map(f => [f.id, f])), candidates = new Map(m.candidates.map(c => [c.id, c]));
    const incoming = new Map<string, typeof m.links>(), outgoing = new Map<string, typeof m.links>();
    for (const l of m.links) {
        incoming.set(l.to, [...(incoming.get(l.to) ?? []), l]);
        outgoing.set(l.from, [...(outgoing.get(l.from) ?? []), l]);
    }
    const ev = new Map([...evidence].map(([id, e]) => [id, structuredClone(e)]));
    const get = <T>(map: Map<string, T>, id: string): Lookup<T> => map.has(id) ? { status: 'Found', value: structuredClone(map.get(id)!) } : { status: 'NotFound', id };
    return Object.freeze({ listItems: () => structuredClone(m.items), getItem: (id: string) => get(items, id), getEvidence: (id: string) => get(ev, id), getFact: (id: string) => get(facts, id), getCandidate: (id: string) => get(candidates, id), neighbors: (id: string): Lookup<unknown> => items.has(id) ? { status: 'Found', value: structuredClone([...(outgoing.get(id) ?? []).map(l => ({ ...l, direction: 'outgoing' })), ...(incoming.get(id) ?? []).map(l => ({ ...l, direction: 'incoming' }))]) } : { status: 'NotFound', id } });
}
