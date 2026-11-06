import { beforeAll, describe, expect, it } from 'vitest';
import { scan, selectFunction, compare, discoverConcepts, evaluate } from '../src/core/index.js';
import type { ScanResult } from '../src/core/model.js';
import { canConsultFromCard, canConsultFromDetail, canConfirmRequest } from '../examples/react-vite/src/rules';
import type { Listing } from '../examples/react-vite/src/domain';
let example: ScanResult, fixture: ScanResult;
beforeAll(() => { example = scan('examples/react-vite'); fixture = scan('tests/fixtures'); });
const predicate = (name: string) => selectFunction(fixture, name).predicate;
const cmp = (a: string, b: string) => compare(predicate(a), predicate(b), { sameInput: true });

describe('TypeScript facts and identity', () => {
  it('loads a real React project with no diagnostics', () => {
    expect(example.diagnostics).toEqual([]);
    expect(fixture.diagnostics).toEqual([]);
    expect(example.files).toContain('src/App.tsx');
    expect(example.types.find(t => t.name === 'Listing')?.fields.map(f => f.name)).toEqual(['id', 'vehicle', 'status', 'price']);
    const fn = selectFunction(example, 'canConsultFromCard');
    expect(fn.parameters[0]?.type).toBe('Listing');
    expect(fn.returnType).toBe('boolean');
    expect(fn.properties.map(p => p.name)).toContain('status');
    expect(fn.referencedTypes.map(t => t.name)).toContain('Listing');
    expect(fn.predicateEvidence?.start.line).toBe(5);
  });
  it('keeps structurally identical User and Customer separate', () => {
    const [a, b] = ['User', 'Customer'].map(n => example.types.find(t => t.name === n)!);
    expect(a!.fields.map(f => [f.name, f.type])).toEqual(b!.fields.map(f => [f.name, f.type]));
    expect(a!.id).not.toBe(b!.id);
  });
  it('separates same-named declarations and resolves import aliases', () => {
    const checks = fixture.functions.filter(f => f.name === 'check');
    expect(new Set(checks.map(f => f.id)).size).toBe(2);
    expect(checks[0]!.properties[0]!.id).not.toBe(checks[1]!.properties[0]!.id);
    expect(() => selectFunction(fixture, 'check')).toThrow('Ambiguous');
    const imported = selectFunction(fixture, 'usesAlias');
    expect(imported.references.find(r => r.target.name === 'check')?.target.evidence.file).toBe('a.ts');
    expect(imported.referencedTypes.find(t => t.name === 'Item')?.evidence.file).toBe('a.ts');
  });
  it('does not absorb nested callback properties/references into an outer function', () => {
    const shadow = selectFunction(fixture, 'shadow');
    expect(shadow.conditions).toHaveLength(1);
    expect(fixture.functions.some(f => f.name === '<anonymous>' && f.predicate.status === 'unsupported')).toBe(true);
  });
  it('reports unsupported computed accesses and classes', () => {
    expect(fixture.omissions.some(o => o.reason.includes('Computed'))).toBe(true);
    expect(fixture.omissions.some(o => o.reason.includes('Class'))).toBe(true);
  });
  it('uses the full declared domain inside narrowed branches', () => {
    const conditions = selectFunction(fixture, 'narrowed').conditions;
    for (const c of conditions) {
      expect(c.normalization.status).toBe('supported');
      if (c.normalization.status === 'supported') expect(c.normalization.variables[0]?.domain).toEqual(['available', 'reserved', 'sold']);
    }
    expect(predicate('narrowed').status).toBe('unsupported');
  });
  it('does not publish primitive string methods as domain fields', () => {
    expect(example.types.find(t => t.name === 'ListingStatus')?.fields).toEqual([]);
    expect(example.types.find(t => t.name === 'ListingStatus')?.type).toContain('reserved');
  });
});

describe('finite logical comparisons', () => {
  it('finds reserved counterexample with directional implication', () => {
    const a = selectFunction(example, 'canConsultFromCard').predicate, b = selectFunction(example, 'canConsultFromDetail').predicate;
    expect(compare(a, b, { sameInput: true })).toMatchObject({ status: 'Implies', equivalent: false, leftImpliesRight: true, rightImpliesLeft: false, direction: 'left-to-right', counterexample: { 'arg0.status': 'reserved' }, evaluatedAssignments: 3 });
    expect(compare(b, a, { sameInput: true }).direction).toBe('right-to-left');
    expect(compare(a, b).status).toBe('Unknown');
  });
  it.each([['primitive', 'reversed'], ['wide', 'deMorgan'], ['enumOnline', 'enumPhone'], ['numericEnum', 'numericEnumEquivalent']])('proves %s equivalent to %s', (a, b) => {
    expect(cmp(a, b)).toMatchObject({ status: 'Equivalent', equivalent: true });
  });
  it('finds disagreement in both directions', () => {
    expect(cmp('primitive', 'complement')).toMatchObject({ status: 'Different', leftImpliesRight: false, rightImpliesLeft: false, leftOnly: { arg0: 'available' }, rightOnly: { arg0: 'reserved' } });
  });
  it('refuses incompatible domains', () => { expect(cmp('primitive', 'outside').status).toBe('Unknown'); });
  it.each(['unbounded', 'loose', 'call', 'optional', 'optionalChain', 'destructured', 'asyncPredicate', 'mutation', 'computed', 'correlated', 'accessor', 'defaults'])('reports %s as unsupported', name => {
    expect(predicate(name).status).toBe('unsupported');
    expect(cmp(name, 'primitive').status).toBe('Unsupported');
  });
  it('bounds enumeration before evaluating any assignments', () => {
    expect(compare(predicate('twoVariables'), predicate('twoVariables'), { sameInput: true, maxAssignments: 8 })).toMatchObject({ status: 'Unknown', evaluatedAssignments: 0 });
    expect(cmp('twoVariables', 'twoVariables').evaluatedAssignments).toBe(9);
    expect(() => compare(predicate('primitive'), predicate('primitive'), { sameInput: true, maxAssignments: -1 })).toThrow();
  });
  it('handles constants and vacuous implication explicitly', () => {
    expect(cmp('none', 'all')).toMatchObject({ status: 'Implies', leftImpliesRight: true, rightImpliesLeft: false, counterexample: {} });
  });
  it('matches executable example behavior on every declared input', () => {
    const predicateA = selectFunction(example, 'canConsultFromCard').predicate;
    const predicateB = selectFunction(example, 'canConsultFromDetail').predicate;
    if (predicateA.status !== 'supported' || predicateB.status !== 'supported') throw new Error('Unsupported example');
    for (const status of ['available', 'reserved', 'sold'] as const) {
      const listing: Listing = { id: 'l', vehicle: { id: 'v', model: 'test', fuel: 'electric' }, price: 1, status };
      expect(evaluate(predicateA.logic, { 'arg0.status': status })).toBe(canConsultFromCard(listing));
      expect(evaluate(predicateB.logic, { 'arg0.status': status })).toBe(canConsultFromDetail(listing));
    }
    expect(canConfirmRequest({ id: 'r', listingId: 'l', state: 'pending', channel: 'online' })).toBe(true);
    expect(canConfirmRequest({ id: 'r', listingId: 'l', state: 'confirmed', channel: 'online' })).toBe(false);
  });
  it('discovers shared listing rules without merging unrelated vehicle rules', () => {
    const discovered = discoverConcepts(example);
    const card = selectFunction(example, 'canConsultFromCard'), detail = selectFunction(example, 'canConsultFromDetail'), electric = selectFunction(example, 'isElectric');
    const group = discovered.candidates.find(c => c.extent.includes(card.id) && c.extent.includes(detail.id) && c.intent.some(a => a.startsWith('condition:')))!;
    expect(group).toBeDefined();
    expect(group.extent).not.toContain(electric.id);
    expect(discovered.approvedKnowledge).toEqual([]);
    expect(discovered.truncated).toBe(false);
    for (const edge of discovered.relations) {
      const general = discovered.candidates.find(c => c.id === edge.general)!;
      const specific = discovered.candidates.find(c => c.id === edge.specific)!;
      expect(general.intent.every(a => specific.intent.includes(a))).toBe(true);
      expect(specific.extent.every(o => general.extent.includes(o))).toBe(true);
    }
  });
});
