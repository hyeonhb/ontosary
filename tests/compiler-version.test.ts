import { appendFileSync, copyFileSync, cpSync, mkdirSync, mkdtempSync, readdirSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import type { ScanResult } from '../src/core/model.js';

function run(...args: string[]) {
  return spawnSync(process.execPath, ['dist/cli/index.js', ...args], { encoding: 'utf8' });
}

describe.each(['4.9.4', '5.9.3'])('TypeScript %s through the public CLI', version => {
  let dir: string;
  const selection = ['--typescript-version', version];
  const compiler = { requested: version, used: version };

  beforeAll(() => {
    dir = mkdtempSync(path.join(tmpdir(), 'ontosary-compiler-'));
    for (const file of ['a.ts', 'b.ts', 'cases.ts']) {
      copyFileSync(path.join('tests/fixtures', file), path.join(dir, file));
    }
    writeFileSync(path.join(dir, 'tsconfig.json'), JSON.stringify({
      compilerOptions: { strict: true, target: 'ES2022', moduleResolution: 'node', types: [],
        declaration: true, emitDeclarationOnly: true }, include: ['*.ts'],
    }));
  });
  afterAll(() => rmSync(dir, { recursive: true, force: true }));

  it('resolves imports and same-name symbols, normalizes conditions and preserves the default output', () => {
    const result = run('scan', dir, ...selection);
    expect(result.status).toBe(0);
    const { compiler: used, ...facts } = JSON.parse(result.stdout) as ScanResult & { compiler: typeof compiler };
    expect(used).toEqual(compiler);
    expect(facts.diagnostics).toEqual([]);
    const checks = facts.functions.filter(fn => fn.name === 'check');
    expect(checks.map(fn => fn.properties[0]?.evidence.file)).toEqual(['a.ts', 'b.ts']);
    const alias = facts.functions.find(fn => fn.name === 'usesAlias')!;
    expect(alias.references.find(ref => ref.target.name === 'check')?.target.id).toBe(checks[0]!.id);
    expect(alias.referencedTypes.find(ref => ref.name === 'Item')?.evidence.file).toBe('a.ts');
    expect(checks[0]!.conditions[0]!.normalization).toEqual(checks[0]!.predicate);
    const numeric = facts.functions.find(fn => fn.name === 'numericEnum')!;
    expect(numeric.predicate.status).toBe('unsupported');
    if (version === '5.9.3') {
      const defaultScan = run('scan', dir);
      expect(defaultScan.status).toBe(0);
      expect(defaultScan.stdout).toBe(JSON.stringify(facts, null, 2) + '\n');
    }
    const compare = run('compare', dir, checks[0]!.id, checks[1]!.id, '--assume-same-input', ...selection);
    expect(compare.status).toBe(0);
    expect(JSON.parse(compare.stdout)).toMatchObject({ compiler, status: 'Implies', evaluatedAssignments: 3,
      counterexample: { 'arg0.status': 'reserved' }, left: { evidence: { file: 'a.ts' } }, right: { evidence: { file: 'b.ts' } } });
    const stringEnum = run('compare', dir, 'enumOnline', 'enumPhone', '--assume-same-input', ...selection);
    expect(stringEnum.status).toBe(0);
    expect(JSON.parse(stringEnum.stdout)).toMatchObject({ compiler, status: 'Equivalent', evaluatedAssignments: 2 });
    const concepts = run('concepts', dir, ...selection);
    expect(concepts.status).toBe(0);
    expect(JSON.parse(concepts.stdout).candidates.length).toBeGreaterThan(0);
    expect(JSON.parse(concepts.stdout).compiler).toEqual(compiler);
    expect(readdirSync(dir).sort()).toEqual(['a.ts', 'b.ts', 'cases.ts', 'tsconfig.json']);
  });

  it('rejects numeric enum enumeration on a well-typed out-of-range runtime witness', () => {
    const project = 'tests/fixtures/open-numeric-enum';
    const out = mkdtempSync(path.join(tmpdir(), 'ontosary-enum-'));
    try {
      const pkg = version === '4.9.4' ? 'typescript-4-9-4' : 'typescript';
      const tsc = spawnSync(process.execPath, [`node_modules/${pkg}/bin/tsc`, '-p', project, '--outDir', out], { encoding: 'utf8' });
      expect([tsc.status, tsc.stdout, tsc.stderr]).toEqual([0, '', '']);
      const witness = spawnSync(process.execPath, ['-p', "JSON.stringify(require('./input.js').results)"], { cwd: out, encoding: 'utf8' });
      expect(witness.status).toBe(0);
      expect(JSON.parse(witness.stdout)).toEqual([false, true]);
    } finally {
      rmSync(out, { recursive: true, force: true });
    }

    const scan = run('scan', project, ...selection);
    expect(scan.status).toBe(0);
    const facts: ScanResult = JSON.parse(scan.stdout);
    expect(facts.diagnostics).toEqual([]);
    const unsupported = { status: 'unsupported', reason: expect.stringContaining('Numeric enum') };
    for (const name of ['isPending', 'notConfirmed']) {
      expect(facts.functions.find(fn => fn.name === name)?.predicate).toMatchObject(unsupported);
    }
    const branch = facts.functions.find(fn => fn.name === 'pendingBranch')!;
    expect(branch.conditions.find(c => c.kind === 'if')?.normalization).toMatchObject(unsupported);
    const args = ['compare', project, 'isPending', 'notConfirmed', '--assume-same-input'];
    const comparison = run(...args, ...selection);
    expect(comparison.status).toBe(2);
    const { compiler: selected, ...verdict } = JSON.parse(comparison.stdout);
    expect(selected).toEqual(compiler);
    expect(verdict).toMatchObject({ status: 'Unsupported', evaluatedAssignments: 0 });
    if (version === '5.9.3') {
      const implicit = run(...args);
      expect(implicit.status).toBe(2);
      expect(JSON.parse(implicit.stdout)).toEqual(verdict);
    }
  });

  it('retains a real type error and refuses both derived analyses', () => {
    // Add one error to the normal inputs, then restore the copy for other cases.
    const target = path.join(dir, 'b.ts');
    appendFileSync(target, 'export const invalid: string = 7;\n');
    try {
      const scan = run('scan', dir, ...selection);
      expect(scan.status).toBe(1);
      const facts = JSON.parse(scan.stdout);
      expect(facts.compiler).toEqual(compiler);
      expect(facts.diagnostics).toEqual([expect.objectContaining({
        category: 'Error', code: 2322, evidence: expect.objectContaining({
          file: 'b.ts', start: expect.objectContaining({ line: 3, column: 14 }),
        }),
      })]);
      expect(facts.functions[0].predicate.status).toBe('unsupported');
      for (const args of [['concepts', dir], ['compare', dir, 'primitive', 'reversed', '--assume-same-input']]) {
        const result = run(...args, ...selection);
        expect(result.status).toBe(1);
        expect(result.stdout).toBe('');
        expect(JSON.parse(result.stderr)).toMatchObject({ compiler, error: expect.stringContaining('Compiler errors') });
      }
    } finally {
      copyFileSync('tests/fixtures/b.ts', target);
    }
  });
});

it('rejects an unverified compiler before reading the project', () => {
  const result = run('scan', 'missing-project', '--typescript-version', '4.9.5');
  expect(result.status).toBe(1);
  expect(result.stdout).toBe('');
  expect(JSON.parse(result.stderr)).toMatchObject({
    compiler: { requested: '4.9.5', used: null }, error: expect.stringContaining('Unverified TypeScript version'),
  });
});

it('does not substitute another compiler when the pinned dependency is missing or mismatched', () => {
  const dir = mkdtempSync(path.join(tmpdir(), 'ontosary-install-'));
  try {
    cpSync('dist', path.join(dir, 'dist'), { recursive: true });
    writeFileSync(path.join(dir, 'package.json'), '{"type":"module"}');
    const modules = path.join(dir, 'node_modules');
    mkdirSync(modules);
    const baseline = path.resolve('node_modules/typescript');
    const otherVersion = path.join(modules, 'typescript-4-9-4');
    symlinkSync(path.resolve('node_modules/typescript-4-9-4'), otherVersion, 'junction');
    for (const selection of [[], ['--typescript-version', '5.9.3']]) {
      const missingDefault = spawnSync(process.execPath, [
        path.join(dir, 'dist/cli/index.js'), 'scan', 'tests/fixtures', ...selection,
      ], { encoding: 'utf8' });
      expect([missingDefault.status, missingDefault.stdout]).toEqual([1, '']);
      expect(JSON.parse(missingDefault.stderr)).toMatchObject({
        compiler: { requested: '5.9.3', used: null }, error: expect.stringContaining("Cannot find module 'typescript'"),
      });
    }
    rmSync(otherVersion);
    symlinkSync(baseline, path.join(modules, 'typescript'), 'junction');
    for (const state of ['missing', 'mismatched']) {
      if (state === 'mismatched') symlinkSync(baseline, path.join(modules, 'typescript-4-9-4'), 'junction');
      const result = spawnSync(process.execPath, [
        path.join(dir, 'dist/cli/index.js'), 'scan', 'tests/fixtures', '--typescript-version', '4.9.4',
      ], { encoding: 'utf8' });
      expect(result.status).toBe(1);
      expect(result.stdout).toBe('');
      expect(JSON.parse(result.stderr)).toMatchObject({
        compiler: { requested: '4.9.4', used: null },
        error: expect.stringContaining(state === 'missing' ? 'typescript-4-9-4' : 'loaded 5.9.3'),
      });
    }
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});
