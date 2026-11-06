import { describe, expect, it } from 'vitest';
import { formalConcepts } from '../src/core/fca.js';
import type { FormalContext } from '../src/core/model.js';
const context: FormalContext = { objects: ['a', 'b', 'c'], attributes: ['x', 'y'], incidence: { a: ['x'], b: ['x', 'y'], c: ['y'] } };
const key = (intent: string[]) => [...intent].sort().join(',');

describe('FCA closure and bounded enumeration', () => {
  it('computes the known four-element diamond', () => {
    expect(formalConcepts(context).concepts.map(c => [c.extent, c.intent])).toEqual([
      [['a', 'b', 'c'], []], [['b', 'c'], ['y']], [['a', 'b'], ['x']], [['b'], ['x', 'y']],
    ]);
  });
  it('agrees with an independent exhaustive oracle for every 3×3 incidence matrix', () => {
    const objects = ['a', 'b', 'c'], attributes = ['x', 'y', 'z'];
    for (let matrix = 0; matrix < 512; matrix++) {
      const incidence = Object.fromEntries(objects.map((o, i) => [o, attributes.filter((_, j) => matrix & (1 << (i * 3 + j)))]));
      const expected = new Set<string>();
      for (let mask = 0; mask < 8; mask++) {
        const intent = attributes.filter((_, j) => mask & (1 << j));
        const extent = objects.filter(o => intent.every(a => incidence[o]!.includes(a)));
        expected.add(key(attributes.filter(a => extent.every(o => incidence[o]!.includes(a)))));
      }
      const output = formalConcepts({ objects, attributes, incidence });
      expect(output.truncated).toBe(false);
      expect(output.concepts).toHaveLength(expected.size);
      expect(new Set(output.concepts.map(c => key(c.intent)))).toEqual(expected);
      for (const c of output.concepts) {
        expect(c.extent).toEqual(objects.filter(o => c.intent.every(a => incidence[o]!.includes(a))));
        expect(c.intent).toEqual(attributes.filter(a => c.extent.every(o => incidence[o]!.includes(a))));
      }
    }
  });
  it('supports empty contexts and vacuous closure', () => {
    expect(formalConcepts({ objects: [], attributes: ['x'], incidence: {} }).concepts[0]).toMatchObject({ extent: [], intent: ['x'] });
    expect(formalConcepts({ objects: ['a'], attributes: [], incidence: { a: [] } }).concepts[0]).toMatchObject({ extent: ['a'], intent: [] });
  });
  it('reports truncation accurately, including exact limit boundary', () => {
    expect(formalConcepts(context, { maxConcepts: 3 })).toMatchObject({ truncated: true });
    expect(formalConcepts(context, { maxConcepts: 4 })).toMatchObject({ truncated: false });
  });
  it('rejects oversized or malformed contexts', () => {
    expect(() => formalConcepts(context, { maxObjects: 2 })).toThrow('exceeds');
    expect(() => formalConcepts(context, { maxAttributes: 1 })).toThrow('exceeds');
    expect(() => formalConcepts(context, { maxConcepts: 0 })).toThrow('positive');
    expect(() => formalConcepts({ ...context, objects: ['a', 'a'] })).toThrow('duplicate');
    expect(() => formalConcepts({ ...context, incidence: { a: ['unknown'] } })).toThrow('Invalid');
  });
});
