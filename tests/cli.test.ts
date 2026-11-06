import { execFileSync, spawnSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { describe, expect, it } from 'vitest';
import { scan, selectFunction } from '../src/core/index.js';
const run = (...args: string[]) => spawnSync(process.execPath, ['dist/cli/index.js', ...args], { encoding: 'utf8' });

describe('CLI and project validation', () => {
  it('prints reproducible scan JSON', () => {
    const a = run('scan', 'examples/react-vite', '--json'), b = run('scan', 'examples/react-vite');
    expect(a.status).toBe(0);
    expect(a.stdout).toBe(b.stdout);
    expect(JSON.parse(a.stdout).category).toBe('code-facts');
  });
  it('prints concepts and comparison with evidence', () => {
    const groups = run('concepts', 'examples/react-vite');
    expect(groups.status).toBe(0);
    expect(JSON.parse(groups.stdout).candidates.length).toBeGreaterThan(0);
    const comparison = run('compare', 'examples/react-vite', 'canConsultFromCard', 'canConsultFromDetail', '--assume-same-input', '--json');
    expect(comparison.status).toBe(0);
    expect(JSON.parse(comparison.stdout)).toMatchObject({ counterexample: { 'arg0.status': 'reserved' }, left: { evidence: { file: 'src/rules.ts' } } });
  });
  it('returns explicit unknown/unsupported statuses', () => {
    expect(run('compare', 'examples/react-vite', 'canConsultFromCard', 'canConsultFromDetail').status).toBe(2);
    const unsupported = run('compare', 'examples/react-vite', 'isPremium', 'canConsultFromCard', '--assume-same-input');
    expect(unsupported.status).toBe(2);
    expect(JSON.parse(unsupported.stdout).status).toBe('Unsupported');
  });
  it('fails clearly on bad commands, missing projects and ambiguous selectors', () => {
    for (const args of [['bad'], ['scan', 'missing-project'], ['scan', 'examples/react-vite', '--bad'], ['compare', 'tests/fixtures', 'check', 'primitive']]) {
      const result = run(...args);
      expect(result.status).toBe(1);
      expect(JSON.parse(result.stderr).error).toBeTruthy();
    }
    expect(run('--help').stdout).toContain('Ontosary');
  });
  it('reports compiler errors and refuses proof from invalid code', () => {
    mkdirSync('work', { recursive: true });
    const dir = mkdtempSync(path.resolve('work/invalid-'));
    try {
      writeFileSync(path.join(dir, 'tsconfig.json'), JSON.stringify({ compilerOptions: { strict: true, types: [] }, include: ['input.ts'] }));
      writeFileSync(path.join(dir, 'input.ts'), "export const broken = (x: 'a' | 'b') => x === missing; export const ok = (x: 'a' | 'b') => x === 'a';");
      const result = run('scan', dir);
      expect(result.status).toBe(1);
      expect(JSON.parse(result.stdout).diagnostics.some((d: { category: string }) => d.category === 'Error')).toBe(true);
      expect(run('compare', dir, 'ok', 'ok', '--assume-same-input').status).toBe(1);
      expect(selectFunction(scan(dir), 'ok').predicate.status).toBe('unsupported');
      writeFileSync(path.join(dir, 'tsconfig.json'), JSON.stringify({ compilerOptions: { strict: false }, include: ['input.ts'] }));
      expect(() => scan(dir)).toThrow('strictNullChecks');
    } finally { rmSync(dir, { recursive: true, force: true }); }
  });
  it('can invoke the compiled bin directly through Node without Vite', () => {
    expect(execFileSync(process.execPath, ['dist/cli/index.js', '--help'], { encoding: 'utf8' })).toContain('ontosary scan');
  });
});
