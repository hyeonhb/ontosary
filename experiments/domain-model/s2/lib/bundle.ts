import fs from 'node:fs';
import path from 'node:path';
import { hash, stable, Baseline, verified } from './analysis-session.js';
import { Model, Failure, integer, object, string } from './model.js';
import { indexBundle } from './query.js';
import { proseViews, auditProse } from './prose.js';
import { task, guide } from '../trial/task.js';
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
    const views=new Map<string,unknown>();
    const add = (unit: string, data: unknown) => {
        views.set(unit,data);
        files.set(`B/views/${unit}.json`,JSON.stringify(data,null,2)+'\n');
    };
    add('status', { ...status, baseline, modelId });
    add('index', query.listItems().map(i => ({ id: i.id, label: i.source.label })));
    selected.items.forEach((i, n) => add(`item-${n}`, { item: query.getItem(i.id), neighbors: query.neighbors(i.id) }));
    selected.facts.forEach((f, n) => add(`fact-${n}`, query.getFact(f.id)));
    selected.candidates.forEach((c, n) => add(`candidate-${n}`, { candidate: query.getCandidate(c.id), objects: selected.objects, attributes: selected.attributes }));
    [...selectedEvidence.keys()].forEach((id, n) => add(`evidence-${n}`, query.getEvidence(id)));
    for (const condition of ['A', 'B', 'C'])
        files.set(`${condition}/SOURCE-NOTICE.txt`, notice);
    const prose=proseViews(views);
    for(const [file,text] of prose.files)files.set(file,text);
    parity.push(...prose.units);
    const parityAudit=auditProse(views,prose.files,prose.units);
    if(!parityAudit.pass)throw new Failure('Parity','C','Generated mapping failed integrity audit');
    for(const condition of ['A','B','C']) {
        files.set(`${condition}/TASK.txt`,task);
        files.set(`${condition}/RUN.md`,guide);
        files.set(`${condition}/START.md`, '# 자료 시작\n\nTASK.txt의 요구와 RUN.md의 실행 범위를 읽고 source/에서 원문을 확인한다. 자료는 변경 전 snapshot이며 현재 변경의 정확성을 대신하지 않는다.\n\n'+
            (condition==='A'?'공통 원문과 upstream 문서를 사용한다.\n':condition==='B'?'views/index.json에서 항목 ID를 찾는다. views/status.json의 검토 상태와 한계를 먼저 확인하고 item-, fact-, candidate-, evidence- 파일의 참조를 따른다.\n':'guide.md에서 개념과 흐름을 찾는다. observations.md의 관찰·한계, roles.md의 역할 후보, evidence.md의 원문·메타데이터를 함께 확인한다.\n'));
    }
    const deployment = [...files].map(([file, text]) => ({ file, sha256: hash(text), bytes: Buffer.byteLength(text) }));
    const bundleId = hash(stable({ version: 2, baselineId: baseline.baselineId, modelId, files: deployment }));
    files.set('bundle-manifest.json', JSON.stringify({ version: 2, baselineId: baseline.baselineId, modelId, bundleId, files: deployment, status }, null, 2) + '\n');
    return { files, parity, baselineId: baseline.baselineId, modelId, bundleId, selection: { objectProjection: 'Member identity/declaration retained; unrelated cell references omitted, candidate shared-role facts retained', selectedFacts: selected.facts.map(f => f.id), excludedFacts: m.facts.filter(f => !selected.facts.includes(f)).map(f => ({ id: f.id, reason: 'Outside twelve-item reference closure' })), selectedCandidates: selected.candidates.map(c => c.id) }, bytes: deployment.reduce((n, f) => n + f.bytes, 0) };
}
