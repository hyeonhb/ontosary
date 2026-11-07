import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { scan } from '../src/core/index.js';
import { evaluateLabel } from '../experiments/corpus/v2/evaluate-labels.mjs';

const source = `export type DateArg<DateType extends Date> = DateType | number | string;
export function unused() { return true; }
export function recursive(): boolean { return recursive(); }
export function arrayRule(array: readonly string[]) { return array.length; }
export function parameterOnly(value: string) { return true; }
export function localDeclaration() { const item = 1; return true; }
export function importedCall() { return imported(); }
export function referenceOnly() { return imported; }
export function shadow(imported: () => boolean) { return imported(); }
export function enclosing() { function nested() { return imported(); } return nested; }
export interface Config { flag: boolean }
export function propertyUse(config: Config) { return config.flag; }
export class State { value = 1; }
import { external as imported } from './external.js';
`;
const external = 'export function external() { return true; }\n';
const texts: Record<string, string> = { 'input.ts': source, 'external.ts': external };
const readSource = (file: string) => texts[file];
function loc(anchor: string, file = 'input.ts') {
  const text = texts[file], offset = text.indexOf(anchor);
  if (offset < 0 || text.indexOf(anchor, offset + 1) >= 0) throw new Error(`Non-unique test anchor: ${anchor}`);
  return { file, anchor, offset, line: text.slice(0, offset).split('\n').length };
}
function label(name: string, kind: string, extra: Record<string, unknown> = {}) {
  return { contractVersion: 2, id: name, name, kind, source: loc(`export function ${name}(`), unverified: [], ...extra };
}
const usage = (name: string, use: string, target: ReturnType<typeof loc>, usageKind = 'call') => label(name, 'reference', { use: loc(use), target, usageKind });
let root: string, facts: ReturnType<typeof scan>;
beforeAll(() => {
  root = fs.mkdtempSync(path.join(os.tmpdir(), 'ontosary-corpus-contract-'));
  for (const [file, text] of Object.entries(texts)) fs.writeFileSync(path.join(root, file), text);
  fs.writeFileSync(path.join(root, 'tsconfig.json'), JSON.stringify({ compilerOptions: { strict: true, types: [] }, include: ['*.ts'] }));
  facts = scan(root);
  expect(facts.diagnostics).toEqual([]);
});
afterAll(() => fs.rmSync(root, { recursive: true, force: true }));
const evaluate = (l: object, f = facts) => evaluateLabel(l, f, { readSource });

describe('version 2 corpus claim contract (actual compiler scan)', () => {
  it('R4 rejects a mutated DateArg union and type kind', () => {
    const l = { contractVersion: 2, id: 'DateArg', name: 'DateArg', kind: 'type', source: loc('export type DateArg'), expectedKind: 'alias', expectedType: { unionMembers: ['DateType', 'number', 'string'] } };
    expect(evaluate(l).status).toBe('correct');
    const changed = structuredClone(facts);
    changed.types.find(t => t.name === 'DateArg')!.type = 'never';
    expect(evaluate(l, changed).status).not.toBe('correct');
    const changedKind = structuredClone(facts);
    changedKind.types.find(t => t.name === 'DateArg')!.kind = 'interface';
    expect(evaluate(l, changedKind).status).not.toBe('correct');
  });
  it('R4 rejects a mutated array parameter type', () => {
    const l = label('arrayRule', 'parameter', { parameter: 'array', expectedType: { exact: 'readonly string[]' } });
    expect(evaluate(l).status).toBe('correct');
    const changed = structuredClone(facts);
    changed.functions.find(f => f.name === 'arrayRule')!.parameters[0].type = 'number';
    expect(evaluate(l, changed).status).not.toBe('correct');
  });
  it('R5 rejects declaration-name references with real unequal name/declaration offsets', () => {
    const fn = facts.functions.find(f => f.name === 'unused')!;
    expect(fn.references).toHaveLength(1);
    expect(fn.references[0].evidence.start.offset).not.toBe(fn.references[0].target.evidence.start.offset);
    const l = usage('unused', 'unused() {', loc('export function unused('), 'reference');
    expect(evaluate(l).status).not.toBe('correct');
  });
  it('rejects parameter and local declaration names as body uses', () => {
    const p = usage('parameterOnly', 'value: string', loc('value: string'), 'reference');
    const v = usage('localDeclaration', 'item = 1', loc('item = 1'), 'reference');
    expect(evaluate(p).status).not.toBe('correct');
    expect(evaluate(v).status).not.toBe('correct');
  });
  it('accepts actual recursion and reports both use and declaration evidence', () => {
    const l = usage('recursive', 'recursive();', loc('export function recursive('));
    const result = evaluate(l);
    expect(result.status).toBe('correct');
    expect(result.useEvidence.start.offset).toBe(l.use.offset);
    expect(result.targetEvidence.start.offset).toBe(l.target.offset);
    const removed = structuredClone(facts);
    const fn = removed.functions.find(f => f.name === 'recursive')!;
    fn.references = fn.references.filter(r => r.evidence.start.offset !== l.use.offset);
    expect(evaluate(l, removed).status).toBe('missing');
  });
  it('distinguishes imported uses, calls, and same-name parameter targets', () => {
    const target = loc('export function external(', 'external.ts');
    expect(evaluate(usage('importedCall', 'imported(); }\nexport function referenceOnly', target)).status).toBe('correct');
    const ref = usage('referenceOnly', 'imported; }', target, 'reference');
    expect(evaluate(ref).status).toBe('correct');
    expect(evaluate({ ...ref, usageKind: 'call' }).status).not.toBe('correct');
    const wrong = usage('shadow', 'imported(); }\nexport function enclosing', target);
    expect(evaluate(wrong).status).not.toBe('correct');
    expect(evaluate({ ...wrong, target: loc('imported: () => boolean') }).status).toBe('correct');
  });
  it('does not attribute nested-function uses to the enclosing function', () => {
    const l = usage('enclosing', 'imported(); } return nested', loc('export function external(', 'external.ts'));
    expect(evaluate(l).status).not.toBe('correct');
  });
  it('does not guess when use evidence, anchors, or diagnostic validity are missing', () => {
    const l = usage('recursive', 'recursive();', loc('export function recursive('));
    expect(evaluate({ ...l, use: undefined }).status).toBe('indeterminate');
    expect(evaluate({ ...l, use: { ...l.use, anchor: 'wrong' } }).status).toBe('indeterminate');
    expect(evaluate({ ...l, source: { ...l.source, anchor: 'wrong declaration' } }).status).toBe('indeterminate');
    expect(evaluate({ ...l, target: { ...l.target, offset: 999 } }).status).toBe('indeterminate');
    const invalid = structuredClone(facts);
    invalid.diagnostics.push({ category: 'Error', code: 1, message: 'test diagnostic' });
    expect(evaluate(l, invalid).status).toBe('indeterminate');
  });
  it('matches property use coordinates and target instead of accepting only a deduplicated property', () => {
    const l = { ...usage('propertyUse', 'flag; }', loc('flag: boolean'), 'reference'), kind: 'property' };
    expect(evaluate(l).status).toBe('correct');
    const changed = structuredClone(facts);
    const fn = changed.functions.find(f => f.name === 'propertyUse')!;
    fn.references = fn.references.filter(r => r.evidence.start.offset !== l.use.offset);
    expect(evaluate(l, changed).status).toBe('missing');
  });
  it('keeps omissions, missing facts, mismatched contracts and unverified context distinct', () => {
    const l = { contractVersion: 2, id: 'State', name: 'State', kind: 'type', source: loc('export class State'), expectedKind: 'class' };
    expect(evaluate(l).status).toBe('unsupported');
    expect(evaluate(l, { ...facts, omissions: [] }).status).toBe('missing');
    expect(evaluate(label('arrayRule', 'parameter', { parameter: 'array' })).status).toBe('indeterminate');
    const unverified = ['FunctionFact does not verify generic parameters.'];
    expect(evaluate(label('arrayRule', 'function', { unverified })).unverified).toEqual(unverified);
  });

});
