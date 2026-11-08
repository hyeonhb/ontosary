import { BaselineSession } from './analysis-session.js';
import { Model, references, Evidence, string, object, array, integer } from './model.js';
export function validate(m: Model, session: BaselineSession) {
    references(m);
    const evidence = new Map<string, ReturnType<BaselineSession['verifyEvidence']>>();
    for (const f of m.facts)
        for (const e of f.evidence)
            evidence.set(e.id, session.verifyEvidence(e));
    // Member declarations and attribute target definitions are part of the packaged closure.
    const extra: Evidence[] = [];
    for (const o of m.objects) {
        const e = object(o.evidence, 'object/evidence');
        extra.push(toEvidence(e, `object:${string(o.id, 'object/id')}`));
    }
    for (const a of m.attributes)
        for (const [i, x] of array(a.declarations, 'attribute/declarations').entries())
            extra.push(toEvidence(object(x, 'declaration'), `attribute:${string(a.id, 'attribute/id')}:${i}`));
    for (const e of extra)
        evidence.set(e.id, session.verifyEvidence(e));
    return evidence;
}
function toEvidence(e: ReturnType<typeof object>, id: string): Evidence { const offset = integer(e.offset, id), anchor = string(e.anchor, id); return { id, file: string(e.file, id), symbol: string(e.symbol, id), offset, end: e.end === undefined ? offset + anchor.length : integer(e.end, id), line: integer(e.line, id), anchor, sha256: string(e.sha256, id) }; }
