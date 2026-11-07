import { describe, it, expect } from 'vitest';
import { repoRoot, serializeObservation } from '../experiments/corpus/common.mjs';
import type { FunctionFact } from '../src/core/model.js';
import { evaluateLabel } from '../experiments/corpus/evaluate-labels.mjs';
const evidence = (file: string, offset: number) => ({ file, symbol: '', start: { offset, line: 1, column: offset + 1 }, end: { offset: offset + 1, line: 1, column: offset + 2 } });
const label = { id: 'source-authored', kind: 'function', name: 'rule', source: { file: 'a.ts', offset: 10 } };
const fn: FunctionFact = { id: 'a.ts:10:rule', name: 'rule', evidence: evidence('a.ts', 10), parameters: [], conditions: [], properties: [], references: [], referencedTypes: [], returnType: 'boolean', predicate: { status: 'unsupported', reason: 'test' } };
const facts = (functions: FunctionFact[] = [fn], extra: Record<string, unknown> = {}) => ({ functions, types: [], omissions: [], diagnostics: [], ...extra });
describe('corpus source-label adjudication', () => {
  it('redacts only the workspace prefix in observations without altering source coordinates', () => {
    const input = { type: `import("${repoRoot}work/corpora/a/source").Options`, relative: 'source/input.ts', offset: 42 };
    expect(JSON.parse(serializeObservation(input))).toEqual({ type: 'import("<workspace>/work/corpora/a/source").Options', relative: input.relative, offset: 42 });
    expect(input.type).toContain(repoRoot);
  });
  it('uses declaration coordinates, not coincidentally matching names', () => {
    expect(evaluateLabel(label, facts()).status).toBe('correct');
    expect(evaluateLabel(label, facts([{ ...fn, evidence: evidence('b.ts', 10) }])).status).toBe('missing');
    expect(evaluateLabel(label, facts([{ ...fn, name: 'other' }])).status).toBe('mislinked');
  });
  it('keeps compiler failures and ambiguous facts indeterminate', () => {
    expect(evaluateLabel(label, facts([], { diagnostics: [{ category: 'Error' }] })).status).toBe('indeterminate');
    expect(evaluateLabel(label, facts([fn, fn])).status).toBe('indeterminate');
    expect(evaluateLabel(label, undefined).status).toBe('indeterminate');
  });
  it('distinguishes explicit omissions at the source from unexplained missing facts', () => {
    const l = { ...label, kind: 'type' };
    expect(evaluateLabel(l, facts([], { omissions: [{ evidence: evidence('a.ts', 10), reason: 'class unsupported' }] })).status).toBe('unsupported');
    expect(evaluateLabel(l, facts([], { omissions: [{ evidence: evidence('b.ts', 10), reason: 'class unsupported' }] })).status).toBe('missing');
  });
  it('counts extracted condition text separately from logical support', () => {
    const l = { ...label, kind: 'condition', text: 'n > 0', conditionKind: 'if' };
    const c = { text: 'n > 0', kind: 'if', evidence: evidence('a.ts', 20), normalization: { status: 'unsupported' } };
    const result = evaluateLabel(l, facts([{ ...fn, conditions: [{ ...c, id: 'condition', kind: 'if', normalization: { status: 'unsupported', reason: 'test' } }] }]));
    expect(result.status).toBe('correct');
    expect(result.reason).toContain('unsupported');
    expect(evaluateLabel({ ...l, text: 'n >= 0' }, facts([{ ...fn, conditions: [{ ...c, id: 'condition', kind: 'if', normalization: { status: 'unsupported', reason: 'test' } }] }])).status).toBe('missing');
  });
  it('requires a use edge to the expected declaration, not its self-reference or a name collision', () => {
    const l = { ...label, kind: 'reference', target: { file: 'a.ts', offset: 14 } };
    const target = { id: 'a.ts:14:input', name: 'input', evidence: evidence('a.ts', 14) };
    const self = { target, evidence: target.evidence };
    expect(evaluateLabel(l, facts([{ ...fn, references: [self] }])).status).toBe('missing');
    const wrong = { target: { ...target, evidence: evidence('b.ts', 14) }, evidence: evidence('a.ts', 30) };
    expect(evaluateLabel(l, facts([{ ...fn, references: [self, wrong] }])).status).toBe('missing');
    expect(evaluateLabel(l, facts([{ ...fn, references: [self, { target, evidence: evidence('a.ts', 30) }] }])).status).toBe('correct');
  });
  it('keeps structurally similar types separate by declaration identity', () => {
    const l = { ...label, kind: 'distinct-types', otherName: 'other', other: { file: 'b.ts', offset: 20 } };
    const other = { id: 'b.ts:20:other', name: 'other', evidence: evidence('b.ts', 20) };
    expect(evaluateLabel(l, facts([], { types: [fn, other] })).status).toBe('correct');
    expect(evaluateLabel(l, facts([], { types: [fn, { ...other, id: fn.id }] })).status).toBe('mislinked');
  });
});
