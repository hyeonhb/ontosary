import { beforeAll, describe, expect, it } from 'vitest';
import { spawnSync } from 'node:child_process';
import { scan, selectFunction, compare, evaluate } from '../src/core/index.js';
import type { ScanResult } from '../src/core/model.js';
import * as runtime from './fixtures/soundness/input';
import { importedEnum } from './fixtures/soundness/imported';

const project = 'tests/fixtures/soundness';
let facts: ScanResult;
beforeAll(() => {
  facts = scan(project);
  // These failures must not be masked by the global compiler-error refusal.
  expect(facts.diagnostics).toEqual([]);
});
const fn = (name: string) => selectFunction(facts, name);
const cmp = (a: string, b: string) => compare(fn(a).predicate, fn(b).predicate, { sameInput: true });
const rejectedReceivers = [
  'optionalEnum', 'callEnum', 'reversedCall', 'wrappedCall', 'assertedEnum', 'nonNullEnum',
  'parameterEnum', 'nestedEnum', 'nestedOptional', 'optionalParent', 'assertedDirect',
  'computedEnum', 'optionalDirect', 'aliasedObject', 'shadowedEnum', 'underAnd', 'underNot',
  'underConstant', 'accessorEnum', 'namespacedEnum',
];

describe('R1: enum-member symbols do not erase receiver evaluation', () => {
  it('reproduces distinct runtime outcomes on valid inputs', () => {
    expect(runtime.optionalEnum(undefined)).toBe(false);
    expect(runtime.always(undefined)).toBe(true);
    expect(() => runtime.callEnum()).toThrow('not total');
    expect(() => runtime.accessorEnum(new runtime.Holder())).toThrow('getter evaluated');
  });
  it.each(rejectedReceivers)('refuses %s in both the predicate and its condition', name => {
    const fact = fn(name);
    expect(fact.predicate).toMatchObject({ status: 'unsupported', reason: expect.any(String) });
    expect(fact.conditions).toHaveLength(1);
    expect(fact.conditions[0]!.normalization).toEqual(fact.predicate);
    expect(cmp(name, 'always')).toMatchObject({ status: 'Unsupported', evaluatedAssignments: 0 });
    expect(cmp(name, 'always')).not.toHaveProperty('equivalent');
  });
});

describe('R2: explicit this must not become a positional runtime argument', () => {
  it('shows both the false equivalent and false different cases in runtime terms', () => {
    for (const a of ['a', 'b'] as const) for (const b of ['a', 'b'] as const) {
      expect(runtime.withThis(a, b)).toBe(runtime.first(a, b));
    }
    expect(runtime.withThis('a', 'b')).not.toBe(runtime.second('a', 'b'));
    expect(cmp('withThis', 'first')).toMatchObject({ status: 'Unsupported', evaluatedAssignments: 0 });
    expect(cmp('withThis', 'second')).toMatchObject({ status: 'Unsupported', evaluatedAssignments: 0 });
  });
  it.each(['withThis', 'withThisConstant', 'withThisMethod', 'thisBranch'])('refuses all conditions of %s with a specific reason', name => {
    const fact = fn(name);
    expect(fact.predicate.status).toBe('unsupported');
    expect(fact.parameters[0]?.name).toBe('this'); // source signature, not runtime arg0
    expect(fact.conditions.length).toBeGreaterThan(0);
    for (const condition of fact.conditions) expect(condition.normalization).toMatchObject({ status: 'unsupported', reason: expect.stringContaining('this') });
    if (name !== 'thisBranch') expect(fact.predicate).toMatchObject({ reason: expect.stringContaining('this') });
  });
});

describe('accepted expression semantics and executable comparison witnesses', () => {
  const functions = {
    first: runtime.first, second: runtime.second, directEnum: runtime.directEnum,
    reverseEnum: runtime.reverseEnum, directConstant: runtime.directConstant,
    parenthesizedEnum: runtime.parenthesizedEnum, negated: runtime.negated,
    nestedLogic: runtime.nestedLogic, nestedEquivalent: runtime.nestedEquivalent,
  };
  const inputs = ['a', 'b'] as const;
  it('matches every accepted expression to runtime over the full controlled domain', () => {
    for (const [name, execute] of Object.entries(functions)) {
      const predicate = fn(name).predicate;
      expect(predicate.status).toBe('supported');
      if (predicate.status !== 'supported') throw new Error(name);
      for (const a of inputs) for (const b of inputs)
        expect(evaluate(predicate.logic, { arg0: a, arg1: b })).toBe(execute(a, b));
      expect(fn(name).conditions[0]!.normalization).toEqual(predicate);
    }
  });
  it('compares all 81 ordered pairs against runtime truth tables and replays witnesses', () => {
    let replayed = 0;
    for (const [aName, a] of Object.entries(functions)) for (const [bName, b] of Object.entries(functions)) {
      const result = cmp(aName, bName);
      const evaluations = inputs.flatMap(x => inputs.map(y => [a(x, y), b(x, y)]));
      const leftOnly = evaluations.some(([x, y]) => x && !y), rightOnly = evaluations.some(([x, y]) => !x && y);
      expect(result).toMatchObject({ equivalent: !leftOnly && !rightOnly, leftImpliesRight: !leftOnly, rightImpliesLeft: !rightOnly,
        status: !leftOnly && !rightOnly ? 'Equivalent' : !leftOnly || !rightOnly ? 'Implies' : 'Different' });
      for (const side of ['leftOnly', 'rightOnly'] as const) {
        const witness = result[side];
        if (!witness) continue;
        const x = (witness.arg0 ?? 'a') as runtime.S, y = (witness.arg1 ?? 'a') as runtime.S;
        expect([a(x, y), b(x, y)]).toEqual(side === 'leftOnly' ? [true, false] : [false, true]);
        replayed++;
      }
    }
    expect(replayed).toBeGreaterThan(0);
  });
  it('preserves direct string/numeric enum members and named import aliases', () => {
    for (const [name, values, execute] of [
      ['enumParameter', [runtime.E.A, runtime.E.B], runtime.enumParameter],
      ['numericEnum', [runtime.N.A, runtime.N.B], runtime.numericEnum],
      ['importedEnum', inputs, importedEnum],
    ] as const) {
      const predicate = fn(name).predicate;
      expect(predicate.status).toBe('supported');
      if (predicate.status !== 'supported') throw new Error(name);
      for (const value of values) expect(evaluate(predicate.logic, { arg0: value })).toBe((execute as (input: string | number) => boolean)(value));
    }
    expect(cmp('numericEnum', 'numericComplement').status).toBe('Equivalent');
  });
});

describe('core/CLI contract', () => {
  it('preserves the default 4096-assignment boundary before enumeration', () => {
    expect(cmp('boundary12', 'boundary12')).toMatchObject({ status: 'Equivalent', evaluatedAssignments: 4096 });
    expect(cmp('boundary13', 'boundary13')).toMatchObject({ status: 'Unknown', evaluatedAssignments: 0 });
  });
  it.each([
    ['optionalEnum', 'always'], ['callEnum', 'always'], ['underAnd', 'always'],
    ['withThis', 'first'], ['withThis', 'second'],
  ])('returns Unsupported/exit 2/zero evaluations for %s vs %s', (left, right) => {
    const result = spawnSync(process.execPath, ['dist/cli/index.js', 'compare', project, left, right, '--assume-same-input', '--json'], { encoding: 'utf8' });
    expect(result.stderr).toBe('');
    expect(result.status).toBe(2);
    const json = JSON.parse(result.stdout);
    expect(json).toMatchObject(cmp(left, right));
    expect(json).toMatchObject({ status: 'Unsupported', reason: expect.any(String), evaluatedAssignments: 0 });
    expect(json).not.toHaveProperty('equivalent');
  });
});
