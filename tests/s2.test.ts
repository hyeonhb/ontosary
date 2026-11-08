import { it, expect, afterEach, describe } from 'vitest';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { gunzipSync } from 'node:zlib';
import { openBaselineSession, hash, stable } from '../experiments/domain-model/s2/lib/analysis-session.js';
import { parseModel, references } from '../experiments/domain-model/s2/lib/model.js';
import { indexBundle } from '../experiments/domain-model/s2/lib/query.js';
import { publish, checkLimits, limits, closure, bundle } from '../experiments/domain-model/s2/lib/bundle.js';
import { executor, invoke } from '../experiments/domain-model/s2/evaluation/execute.js';
const dirs: string[] = [];
const temp = () => { const p = fs.mkdtempSync(path.join(os.tmpdir(), 'ontosary-s2-')); dirs.push(p); return p; };
afterEach(() => dirs.splice(0).forEach(d => fs.rmSync(d, { recursive: true, force: true })));
function fixture() { const root = temp(); fs.cpSync('tests/fixtures/domain-model-s2', root, { recursive: true }); const inputs = fs.readdirSync(root).map(f => ({ file: path.join(root, f), sha256: hash(fs.readFileSync(path.join(root, f))) })); return { root, config: path.join(root, 'tsconfig.json'), revision: 'owned-fixture', policy: 'test', inputs, artifacts: [] }; }
const r = 'experiments/domain-model/results/2026-11-08-v2';
const read = (f: string) => JSON.parse(f.endsWith('.gz') ? gunzipSync(fs.readFileSync(`${r}/${f}`)).toString() : fs.readFileSync(`${r}/${f}`, 'utf8'));
const raw = () => [read('model-after.json'), read('facts.json.gz'), read('fca.json'), read('observation.json.gz')] as [
    unknown,
    unknown,
    unknown,
    unknown
];
const model = () => parseModel(...raw());
const l = limits(JSON.parse(fs.readFileSync('experiments/domain-model/s2/limits.json', 'utf8')));
it('one Program, stable baseline across paths, disposed access fails', () => { const ids = []; for (let i = 0; i < 2; i++) {
    const s = openBaselineSession(fixture());
    try {
        s.inspectInputs();
        s.inspectInputs();
        expect(s.metrics.programs).toBe(1);
        ids.push(s.seal().baselineId);
        expect(() => s.inspectInputs()).toThrow();
    }
    finally {
        s.dispose();
    }
    expect(() => s.seal()).toThrow();
} expect(ids[0]).toBe(ids[1]); });
it.each(['target.ts', 'client.ts', 'tsconfig.json'])('rejects changed pinned %s', (file) => { const spec = fixture(); fs.appendFileSync(path.join(spec.root, file), ' '); const s = openBaselineSession(spec); try {
    expect(() => s.inspectInputs()).toThrow();
    expect(s.state).toBe('rejected');
}
finally {
    s.dispose();
} });
it('rejects missing input and diagnostics', () => { for (const mode of ['missing', 'diagnostic']) {
    const spec = fixture();
    if (mode === 'missing')
        fs.unlinkSync(path.join(spec.root, 'target.ts'));
    else {
        fs.writeFileSync(path.join(spec.root, 'client.ts'), 'const x: string = 1;');
        spec.inputs = spec.inputs.filter(i => !i.file.endsWith('client.ts'));
    }
    const s = openBaselineSession(spec);
    try {
        expect(() => s.inspectInputs()).toThrow();
    }
    finally {
        s.dispose();
    }
} });
it('seal rereads content and root membership', () => { for (const edit of ['edit', 'add']) {
    const spec = fixture(), s = openBaselineSession(spec);
    try {
        s.inspectInputs();
        if (edit === 'edit')
            fs.appendFileSync(path.join(spec.root, 'target.ts'), ' ');
        else
            fs.writeFileSync(path.join(spec.root, 'extra.ts'), 'export const x=1;');
        expect(() => s.seal()).toThrow();
    }
    finally {
        s.dispose();
    }
} });
it('UTF16 and CRLF evidence uses baseline text', () => { const spec = fixture(), file = path.join(spec.root, 'client.ts'), text = '// 😀\r\nexport const x = "한글";\r\n'; fs.writeFileSync(file, text); spec.inputs = spec.inputs.map(i => i.file === file ? { ...i, sha256: hash(text) } : i); const s = openBaselineSession(spec); try {
    s.inspectInputs();
    const offset = text.indexOf('export'), e = { id: 'e', file: 'client.ts', symbol: 'x', offset, end: text.length - 2, line: 2, anchor: 'export', sha256: hash(text) };
    expect(s.verifyEvidence(e).column).toBe(1);
    expect(() => s.verifyEvidence({ ...e, line: 1 })).toThrow();
}
finally {
    s.dispose();
} });
it('malformed model inputs and false approvals are structured failures', () => { for (const mutate of [(x: unknown[]) => x[0] = [], (x: unknown[]) => { (x[0] as {
        items: unknown;
    }).items = 'wrong'; }, (x: unknown[]) => { (x[0] as {
        approvedKnowledge: unknown[];
    }).approvedKnowledge = [{ verified: true }]; }]) {
    const x = raw();
    mutate(x);
    expect(() => parseModel(...x)).toThrow();
} });
it('duplicates, wrong reference kinds and broken references rejected', () => { for (const change of ['duplicate', 'kind', 'broken']) {
    const m = model();
    if (change === 'duplicate')
        m.items.push(m.items[0]!);
    else
        m.items[0]!.factRefs = [change === 'kind' ? m.items[0]!.id : 'missing'];
    expect(() => references(m)).toThrow();
} });
it('query preserves 12 IDs, R6 paths and ownership', () => { const m = model(); references(m); const q = indexBundle(m, new Map()); expect(q.listItems()).toHaveLength(12); for (const id of m.items.map(i => i.id))
    expect(q.getItem(id).status).toBe('Found'); const n = q.neighbors('cancel-request'); expect(JSON.stringify(n)).toContain('refund-also-cancels'); expect(JSON.stringify(q.neighbors('order'))).not.toContain('refund-transport'); expect(q.getItem('absent').status).toBe('NotFound'); const i = q.listItems(); i[0]!.source.label = 'mutated'; expect(q.listItems()[0]!.source.label).not.toBe('mutated'); });
it('closure retains candidate support, members and attribute declarations', () => { const m = closure(model()); expect(m.items).toHaveLength(12); expect(m.facts).toHaveLength(22); expect(m.candidates).toHaveLength(2); expect(m.objects.length).toBeGreaterThan(0); expect(m.attributes.length).toBeGreaterThan(0); });
it('limit/path/output failures do not leave completed outputs', () => { const root = temp(), out = path.join(root, 'out'); expect(() => checkLimits(model(), { ...l, items: 1 })).toThrow(); expect(() => publish(out, new Map([['../escape', 'x']]), l)).toThrow(); expect(fs.existsSync(out)).toBe(false); expect(() => publish(out, new Map([['ok', '123']]), { ...l, totalBytes: 1 })).toThrow(); publish(out, new Map([['ok', 'x']]), l); expect(() => publish(out, new Map(), l)).toThrow(); });
it('interpretation affects model identity, ordered arrays are not reordered', () => { const m = model(), before = hash(stable(m)); m.items[0]!.source.interpretation = 'changed'; expect(hash(stable(m))).not.toBe(before); expect(stable(['b', 'a'])).not.toBe(stable(['a', 'b'])); });
it('oracle executes submitted changes and newly imported helpers', () => { const root = temp(), file = path.join(root, 'input.ts'); fs.writeFileSync(file, 'export class Submit { run(x:string){return x;} }'); let e = executor(root, [{ file: 'input.ts', className: 'Submit' }], {}); expect(invoke(e.instance('Submit'), 'run', ' x ')).toBe(' x '); fs.writeFileSync(path.join(root, 'helper.ts'), 'export const clean=(x:string)=>x.trim();'); fs.writeFileSync(file, "import {clean} from './helper'; export class Submit { run(x:string){return clean(x);} }"); e = executor(root, [{ file: 'input.ts', className: 'Submit' }], {}); expect(invoke(e.instance('Submit'), 'run', ' x ')).toBe('x'); });
it('mid-write directory collision leaves no completed bundle', () => { const root = temp(), out = path.join(root, 'out'); expect(() => publish(out, new Map([['a', 'file'], ['a/b', 'nested']]), l)).toThrow(); expect(fs.existsSync(out)).toBe(false); expect(fs.readdirSync(root)).toEqual([]); });
it('semantic enum and interval errors fail before packaging', () => { const inputs = raw(); const m = inputs[0] as {
    items: {
        kind: string;
    }[];
}; m.items[0]!.kind = 'approved-policy'; expect(() => parseModel(...inputs)).toThrow(); const second = raw(); const facts = second[1] as {
    evidence: {
        offset: number;
    };
}[]; facts[0]!.evidence.offset = -1; expect(() => parseModel(...second)).toThrow(); });
it('frozen query evidence survives external mutation and does not inspect edited workspace', () => { const ev = new Map([['e', { text: 'baseline', sourceVersion: 'baseline' }]]); const q = indexBundle(model(), ev); ev.set('e', { text: 'edited', sourceVersion: 'current' }); expect(q.getEvidence('e')).toEqual({ status: 'Found', value: { text: 'baseline', sourceVersion: 'baseline' } }); });
it('external verified flag and wrong baseline cannot grant model validity', () => { const fake = { baselineId: 'fake', revision: 'x', inputs: 0, programFiles: 0, sourceVersion: 'baseline' as const, currentWorkspaceAssessment: 'not-performed' as const }; expect(() => bundle(model(), new Map(), fake, l, 'notice')).toThrow('External verified'); const s = openBaselineSession(fixture()); try {
    s.inspectInputs();
    const b = s.seal();
    expect(() => bundle(model(), new Map(), b, l, 'notice')).toThrow('Model and baseline differ');
}
finally {
    s.dispose();
} });
it('unsupported submitted field changes are explicitly rejected by executor', () => { const source = temp(), env = temp(); const text = 'export class Submit { field=1; run(){return this.field;} }'; fs.writeFileSync(path.join(env, 'input.ts'), text); fs.writeFileSync(path.join(source, 'input.ts'), text.replace('field=1', 'field=2')); expect(() => executor(source, [{ file: 'input.ts', className: 'Submit' }], {}, env).instance('Submit')).toThrow('excluded constructor'); });
it('deferred submission execution is unsupported rather than premature success', () => { const root = temp(); fs.writeFileSync(path.join(root, 'input.ts'), 'export class Submit { async run(){ await Promise.resolve(); return 1; } }'); expect(() => executor(root, [{ file: 'input.ts', className: 'Submit' }], {}).instance('Submit')).toThrow('Deferred'); });

it('support declarations reject duplicate object and attribute IDs', () => {
    for (const key of ['objects', 'attributes'] as const) {
        const m = model();
        m[key].push(structuredClone(m[key][0]!));
        expect(() => references(m)).toThrow('Duplicate support ID');
    }
});
it('evidence verification rejects reversed declaration intervals', () => {
    const spec = fixture(), s = openBaselineSession(spec);
    try {
        s.inspectInputs();
        expect(() => s.verifyEvidence({ id: 'bad', file: 'client.ts', symbol: 'x', offset: 2, end: 1, line: 1, anchor: 'x', sha256: '0'.repeat(64) })).toThrow('Invalid UTF16 interval');
    } finally { s.dispose(); }
});
