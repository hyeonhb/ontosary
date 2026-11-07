import { beforeAll, afterAll, describe, it, expect } from 'vitest';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { scan } from '../src/core/index.js';
import { evaluateLabel } from '../experiments/corpus/v3/evaluate-labels.mjs';
import { texts, cases } from '../experiments/corpus/v3/role-cases.mjs';
let root: string, facts: ReturnType<typeof scan>;
beforeAll(() => {
  root = fs.mkdtempSync(path.join(os.tmpdir(), 'ontosary-type-context-'));
  for (const [file, text] of Object.entries(texts)) fs.writeFileSync(path.join(root, file), text as string);
  fs.writeFileSync(path.join(root, 'tsconfig.json'), JSON.stringify({ compilerOptions: { strict: true, types: [] }, include: ['*.ts'] }));
  facts = scan(root);
  expect(facts.diagnostics).toEqual([]);
});
afterAll(() => fs.rmSync(root, { recursive: true, force: true }));
describe('R5 type-declaration context, actual scan', () => {
  for (const { id, expected, label } of cases) it(id, () => {
    const fn = facts.functions.find(f => f.name === label.name)!;
    const edges = fn.references.filter(r => r.evidence.file === label.use.file && r.evidence.start.offset === label.use.offset);
    expect(edges).toHaveLength(1);
    if (id !== 'shadow-wrong-target') {
      expect(edges[0].target.evidence.file).toBe(label.target.file);
      expect(edges[0].target.evidence.start.offset).toBe(label.target.offset);
    }
    const result = evaluateLabel(label, facts, { readSource: (file: string) => texts[file] });
    if (expected === 'correct') {
      expect(result.status).toBe('correct');
      expect(result.useEvidence.start.offset).toBe(label.use.offset);
      expect(result.targetEvidence.start.offset).toBe(label.target.offset);
    } else {
      expect(result.status).not.toBe('correct');
      expect(result.reason).toBeTruthy();
    }
  });
});
