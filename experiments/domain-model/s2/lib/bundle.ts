import fs from 'node:fs';
import path from 'node:path';
import { hash, stable, Baseline, verified } from './analysis-session.js';
import { Model, Failure, integer, object, string } from './model.js';
import { indexBundle } from './query.js';
export interface Limits {
    items: number;
    edges: number;
    facts: number;
    candidates: number;
    evidence: number;
    viewBytes: number;
    totalBytes: number;
    inputBytes: number;
}
export function limits(raw: unknown): Limits { const v = object(raw, 'limits'); return { items: integer(v.items, 'limits/items'), edges: integer(v.edges, 'limits/edges'), facts: integer(v.facts, 'limits/facts'), candidates: integer(v.candidates, 'limits/candidates'), evidence: integer(v.evidence, 'limits/evidence'), viewBytes: integer(v.viewBytes, 'limits/viewBytes'), totalBytes: integer(v.totalBytes, 'limits/totalBytes'), inputBytes: integer(v.inputBytes, 'limits/inputBytes') }; }
export function checkLimits(m: Model, l: Limits) { for (const [k, n] of Object.entries({ items: m.items.length, edges: m.links.length, facts: m.facts.length, candidates: m.candidates.length, evidence: m.facts.reduce((n, f) => n + f.evidence.length, 0) }))
    if (n > l[k as keyof Limits])
        throw new Failure('Limit', k, 'Record bound exceeded'); if (Buffer.byteLength(stable(m)) > l.inputBytes)
    throw new Failure('Limit', 'inputBytes', 'Input too large'); }
export function closure(m: Model) {
    const facts = new Set<string>(), cs = new Set<string>(), objects = new Set<string>(), attrs = new Set<string>(), queue = m.items.flatMap(i => [...i.factRefs, ...i.candidateRefs]), seen = new Set<string>();
    while (queue.length) {
        const id = queue.shift()!;
        if (seen.has(id))
            continue;
        seen.add(id);
        const f = m.facts.find(f => f.id === id), c = m.candidates.find(c => c.id === id);
        if (f)
            facts.add(id);
        else if (c) {
            cs.add(id);
            queue.push(...c.factRefs);
            c.extent.forEach(id => objects.add(id));
            c.intent.forEach(id => attrs.add(id));
        }
        else
            throw new Failure('Reference', id, 'Closure missing');
    }
    return { ...m, facts: m.facts.filter(f => facts.has(f.id)), candidates: m.candidates.filter(c => cs.has(c.id)), objects: m.objects.filter(o => objects.has(string(o.id, 'object/id'))).map(o => ({ id: o.id!, class: o.class!, name: o.name!, evidence: o.evidence! })), attributes: m.attributes.filter(a => attrs.has(string(a.id, 'attribute/id'))) };
}
export function publish(out: string, files: Map<string, string>, l: Limits) {
    if (fs.existsSync(out))
        throw new Failure('OutputExists', out, 'Never overwrite');
    let bytes = 0;
    for (const [name, text] of files) {
        if (!/^[A-Za-z0-9_./-]+$/.test(name) || name.split('/').some(x => !x || x === '.' || x === '..') || path.isAbsolute(name))
            throw new Failure('Path', name, 'Unsafe output name');
        const b = Buffer.byteLength(text);
        if (b > l.viewBytes)
            throw new Failure('Limit', name, 'View too large');
        bytes += b;
    }
    if (bytes > l.totalBytes)
        throw new Failure('Limit', 'totalBytes', 'Package too large');
    fs.mkdirSync(path.dirname(out), { recursive: true });
    const staging = fs.mkdtempSync(path.join(path.dirname(out), '.s2-staging-'));
    try {
        for (const [name, text] of files) {
            const dest = path.join(staging, name);
            fs.mkdirSync(path.dirname(dest), { recursive: true });
            fs.writeFileSync(dest, text, { flag: 'wx' });
        }
        fs.renameSync(staging, out);
    }
    catch (e) {
        fs.rmSync(staging, { recursive: true, force: true });
        throw e;
    }
    return bytes;
}
export function bundle(m: Model, evidence: Map<string, unknown>, baseline: Baseline, l: Limits, notice: string) {
    if (!verified(baseline))
        throw new Failure('State', 'baseline', 'External verified flags are not trusted');
    if (m.revision !== baseline.revision)
        throw new Failure('BaselineMismatch', 'revision', 'Model and baseline differ');
    checkLimits(m, l);
    const selected = closure(m), selectedEvidence = new Map<string, unknown>();
    for (const f of selected.facts)
        for (const e of f.evidence)
            selectedEvidence.set(e.id, evidence.get(e.id));
    for (const o of selected.objects) {
        const id = `object:${string(o.id, 'object')}`;
        selectedEvidence.set(id, evidence.get(id));
    }
    for (const a of selected.attributes) {
        const prefix = `attribute:${string(a.id, 'attribute')}:`;
        for (const [id, e] of evidence)
            if (id.startsWith(prefix))
                selectedEvidence.set(id, e);
    }
    for (const [id, e] of selectedEvidence)
        if (!e)
            throw new Failure('Evidence', id, 'Closure evidence missing');
    const modelId = hash(stable({ baselineId: baseline.baselineId, model: selected, evidence: [...selectedEvidence] })), query = indexBundle(selected, selectedEvidence), files = new Map<string, string>(), parity: unknown[] = [];
    const status = { integrity: 'verified', baselineEvidence: 'verified', semanticReview: 'pending', sourceVersion: 'baseline', currentWorkspaceAssessment: 'not-performed', coverage: 'Purposeful S1 client model; partial app coverage; no complete impact/runtime/server policy guarantee' };
    const add = (unit: string, data: unknown) => {
        const b = `B/views/${unit}.json`, c = `C/views/${unit}.md`, body = stable(data);
        files.set(b, JSON.stringify(data, null, 2) + '\n');
        // C contains the same semantic values rendered as labelled prose/list paragraphs, not abbreviated hints.
        const prose = (v: unknown, depth = 0): string => Array.isArray(v) ? v.map((x, i) => `${' '.repeat(depth)}항목 ${i + 1}:\n${prose(x, depth + 1)}`).join('\n') : v && typeof v === 'object' ? Object.entries(v).map(([k, x]) => `${' '.repeat(depth)}${k}: ${x && typeof x === 'object' ? '\n' + prose(x, depth + 1) : JSON.stringify(x)}`).join('\n') : JSON.stringify(v);
        const cText = `# ${unit}\n\n${prose(data).split('\n').map(line => line.trimEnd()).join('\n')}\n`;
        files.set(c, cText);
        parity.push({ unit, B: { file: b, startLine: 1, endLine: files.get(b)!.split('\n').length }, C: { file: c, startLine: 1, endLine: cText.split('\n').length }, semanticHash: hash(body), automaticCoverage: 'same source value tree; human prose equivalence pending', evidenceIds: [...selectedEvidence.keys()], semanticReview: 'pending' });
    };
    add('status', { ...status, baseline, modelId });
    add('index', query.listItems().map(i => ({ id: i.id, label: i.source.label })));
    selected.items.forEach((i, n) => add(`item-${n}`, { item: query.getItem(i.id), neighbors: query.neighbors(i.id) }));
    selected.facts.forEach((f, n) => add(`fact-${n}`, query.getFact(f.id)));
    selected.candidates.forEach((c, n) => add(`candidate-${n}`, { candidate: query.getCandidate(c.id), objects: selected.objects, attributes: selected.attributes }));
    [...selectedEvidence.keys()].forEach((id, n) => add(`evidence-${n}`, query.getEvidence(id)));
    for (const condition of ['A', 'B', 'C'])
        files.set(`${condition}/SOURCE-NOTICE.txt`, notice);
    const common = '검토용 가상 과업: 주문 취소 요청의 사유를 전송 전에 앞뒤 공백을 제거한 비어 있지 않은 문자열로 제한하되 기존 취소/환불/닫기 동작을 보존하세요. 미확정 실패 처리와 실행 조건은 본 실행 전에 별도 동결해야 합니다.\n';
    for (const c of ['A', 'B', 'C'])
        files.set(`${c}/TASK.txt`, common);
    const deployment = [...files].map(([file, text]) => ({ file, sha256: hash(text), bytes: Buffer.byteLength(text) }));
    const bundleId = hash(stable({ version: 1, baselineId: baseline.baselineId, modelId, files: deployment }));
    files.set('bundle-manifest.json', JSON.stringify({ version: 1, baselineId: baseline.baselineId, modelId, bundleId, files: deployment, status }, null, 2) + '\n');
    return { files, parity, baselineId: baseline.baselineId, modelId, bundleId, selection: { objectProjection: 'Member identity/declaration retained; unrelated cell references omitted, candidate shared-role facts retained', selectedFacts: selected.facts.map(f => f.id), excludedFacts: m.facts.filter(f => !selected.facts.includes(f)).map(f => ({ id: f.id, reason: 'Outside twelve-item reference closure' })), selectedCandidates: selected.candidates.map(c => c.id) }, bytes: deployment.reduce((n, f) => n + f.bytes, 0) };
}
