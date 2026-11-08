export type Json = null | boolean | number | string | Json[] | {
    [key: string]: Json;
};
export type RecordData = {
    [key: string]: Json;
};
export class Failure extends Error {
    constructor(public code: string, public field: string, message: string) { super(message); }
}
export function object(x: unknown, at: string): RecordData { if (!x || typeof x !== 'object' || Array.isArray(x))
    throw new Failure('Schema', at, 'Expected object'); return x as RecordData; }
export function array(x: unknown, at: string): unknown[] { if (!Array.isArray(x))
    throw new Failure('Schema', at, 'Expected array'); return x; }
export function string(x: unknown, at: string): string { if (typeof x !== 'string' || !x.length)
    throw new Failure('Schema', at, 'Expected nonempty string'); return x; }
export function strings(x: unknown, at: string): string[] { return array(x, at).map((v, i) => string(v, `${at}/${i}`)); }
export function integer(x: unknown, at: string): number { if (typeof x !== 'number' || !Number.isSafeInteger(x) || x < 0)
    throw new Failure('Schema', at, 'Expected nonnegative integer'); return x; }
export function choice(x: unknown, values: string[], at: string): string { const v = string(x, at); if (!values.includes(v))
    throw new Failure('Schema', at, 'Invalid enum'); return v; }
export interface Evidence {
    id: string;
    file: string;
    symbol: string;
    offset: number;
    end: number;
    line: number;
    anchor: string;
    sha256: string;
}
export interface Item {
    id: string;
    kind: string;
    factRefs: string[];
    candidateRefs: string[];
    source: RecordData;
}
export interface Fact {
    id: string;
    evidence: Evidence[];
    source: RecordData;
}
export interface Candidate {
    id: string;
    factRefs: string[];
    extent: string[];
    intent: string[];
    source: RecordData;
}
export interface Link {
    from: string;
    to: string;
    kind: 'related-item';
    provenance: string;
}
export interface Model {
    revision: string;
    items: Item[];
    links: Link[];
    facts: Fact[];
    candidates: Candidate[];
    objects: RecordData[];
    attributes: RecordData[];
    approvedKnowledge: Json[];
    source: RecordData;
}
export function parseModel(raw: unknown, rawFacts: unknown, rawFca: unknown, rawObservation: unknown): Model {
    const m = object(raw, 'model');
    if (m.schemaVersion !== 1)
        throw new Failure('Schema', 'model/schemaVersion', 'Unsupported version');
    string(m.scope, 'model/scope');
    string(m.author, 'model/author');
    string(m.useContract, 'model/useContract');
    const links: Link[] = [];
    const items = array(m.items, 'items').map((x, i) => {
        const v = object(x, `items/${i}`), id = string(v.id, `items/${i}/id`);
        for (const k of ['label', 'interpretation', 'author'])
            string(v[k], `${id}/${k}`);
        choice(v.kind, ['concept-candidate', 'relationship-candidate', 'observed-behavior-candidate'], `${id}/kind`);
        choice(v.status, ['pending-review'], `${id}/status`);
        strings(v.unverified, `${id}/unverified`);
        if (!Object.hasOwn(v, 'intendedPolicy') || v.intendedPolicy !== null)
            throw new Failure('Approval', id, 'This adapter preserves pending S1 policies only');
        strings(v.relatedItems, `${id}/relatedItems`).forEach(to => links.push({ from: id, to, kind: 'related-item', provenance: `S1.items/${i}/relatedItems` }));
        return { id, kind: string(v.kind, id), factRefs: strings(v.factRefs, id), candidateRefs: strings(v.candidateRefs, id), source: v };
    });
    const facts = array(rawFacts, 'facts').map((x, i) => {
        const v = object(x, `facts/${i}`), id = string(v.id, `facts/${i}/id`);
        for (const k of ['author', 'method', 'scope', 'support', 'claim'])
            string(v[k], `${id}/${k}`);
        choice(v.kind, ['observed-in-source'], `${id}/kind`);
        if (v.value !== undefined)
            choice(v.value, ['yes', 'no', 'unknown'], `${id}/value`);
        const evidence = (Array.isArray(v.evidence) ? v.evidence : [v.evidence]).map((x, j) => {
            const e = object(x, `${id}/evidence/${j}`);
            const offset = integer(e.offset, id), anchor = string(e.anchor, id), end = e.end === undefined ? offset + anchor.length : integer(e.end, id), hash = string(e.sha256, id);
            if (end < offset + anchor.length || !/^[a-f0-9]{64}$/.test(hash))
                throw new Failure('Evidence', id, 'Invalid range/hash');
            return { id: `${id}/e${j}`, file: string(e.file, id), symbol: string(e.symbol, id), offset, end, line: integer(e.line, id), anchor, sha256: hash };
        });
        if (!evidence.length)
            throw new Failure('Evidence', id, 'No source evidence');
        return { id, evidence, source: v };
    });
    const candidates = array(object(rawFca, 'fca').candidates, 'candidates').map((x, i) => { const v = object(x, `candidates/${i}`); choice(v.status, ['pending-review'], 'candidate/status'); return { id: string(v.id, 'candidate/id'), factRefs: strings(v.factRefs, 'candidate/facts'), extent: strings(v.extent, 'candidate/extent'), intent: strings(v.intent, 'candidate/intent'), source: v }; });
    const obs = object(rawObservation, 'observation');
    const objects = array(obs.objects, 'objects').map(x => object(x, 'object'));
    const attributes = array(obs.targets, 'targets').map(x => object(x, 'target'));
    const approved = array(m.approvedKnowledge, 'approvedKnowledge');
    if (approved.length)
        throw new Failure('Approval', 'approvedKnowledge', 'S1 has no verified human decisions; approval ingestion unsupported');
    return { revision: string(m.revision, 'revision'), items, links, facts, candidates, objects, attributes, approvedKnowledge: [], source: m };
}
export function references(m: Model): void {
    const seen = new Set<string>();
    for (const row of [...m.items, ...m.facts, ...m.candidates]) {
        if (seen.has(row.id))
            throw new Failure('Duplicate', row.id, 'Duplicate ID');
        seen.add(row.id);
    }
    const ids = (rows: {
        id: string;
    }[]) => new Set(rows.map(r => r.id)), items = ids(m.items), facts = ids(m.facts), cs = ids(m.candidates);
    const need = (set: Set<string>, id: string, at: string) => { if (!set.has(id))
        throw new Failure('Reference', at, `Wrong kind or absent ${id}`); };
    for (const i of m.items) {
        for (const f of i.factRefs)
            need(facts, f, i.id);
        for (const c of i.candidateRefs)
            need(cs, c, i.id);
    }
    for (const l of m.links) {
        need(items, l.from, 'link/from');
        need(items, l.to, 'link/to');
    }
    const objects = new Set(m.objects.map(o => string(o.id, 'object/id'))), attrs = new Set(m.attributes.map(o => string(o.id, 'attribute/id')));
    if (objects.size !== m.objects.length || attrs.size !== m.attributes.length)
        throw new Failure('Duplicate', 'objects/attributes', 'Duplicate support ID');
    for (const c of m.candidates) {
        c.factRefs.forEach(f => need(facts, f, c.id));
        c.extent.forEach(o => need(objects, o, c.id));
        c.intent.forEach(a => need(attrs, a, c.id));
    }
}
