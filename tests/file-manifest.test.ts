import { afterEach, describe, expect, it } from 'vitest';
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { scan } from '../src/core/index.js';

const temporary: string[] = [];
function project(files: Record<string, string>, include = ['*']) {
  mkdirSync('work', { recursive: true });
  const dir = mkdtempSync(path.resolve('work/manifest-'));
  temporary.push(dir);
  writeFileSync(path.join(dir, 'tsconfig.json'), JSON.stringify({ compilerOptions: {
    strict: true, allowJs: true, checkJs: false, target: 'ES2022', module: 'ESNext',
    moduleResolution: 'Bundler', jsx: 'preserve', types: [],
  }, include }));
  for (const [file, text] of Object.entries(files)) writeFileSync(path.join(dir, file), text);
  return dir;
}
afterEach(() => { for (const dir of temporary.splice(0)) rmSync(dir, { recursive: true, force: true }); });

const mixed = {
  'plain.ts': 'export function tsFunction() { return true; }',
  'component.tsx': 'export const tsxFunction = () => true;',
  'esm.mts': 'export const mtsFunction = () => true;',
  'common.cts': 'export const ctsFunction = () => true;',
  'skipped.js': 'export function jsFunction() { return true; }',
  'skipped-jsx.jsx': 'export function jsxFunction() { return true; }',
  'skipped-esm.mjs': 'export function mjsFunction() { return true; }',
  'skipped-common.cjs': 'exports.cjsFunction = function () { return true; };',
  'types.d.ts': 'export declare function declaredFunction(): boolean;',
  'module.d.mts': 'export declare const declaredEsm: boolean;',
  'common-types.d.cts': 'export declare const declaredCommon: boolean;',
};
const analyzed = ['common.cts', 'component.tsx', 'esm.mts', 'plain.ts'];
const skipped = ['skipped-common.cjs', 'skipped-esm.mjs', 'skipped-jsx.jsx', 'skipped.js'];

describe('R3: files counts only analyzed source files', () => {
  it('keeps TS/TSX/MTS/CTS and reports every skipped implementation file with evidence', () => {
    const facts = scan(project(mixed));
    expect(facts.diagnostics).toEqual([]);
    expect(facts.files).toEqual(analyzed);
    expect(facts.functions.map(f => f.name).sort()).toEqual(['ctsFunction', 'mtsFunction', 'tsFunction', 'tsxFunction']);
    expect(facts.omissions.map(o => o.evidence?.file)).toEqual(skipped);
    for (const omission of facts.omissions) {
      expect(omission.reason).toContain('Unsupported source file extension');
      expect(omission.evidence?.start.line).toBe(1);
    }
    for (const fact of [...facts.types, ...facts.functions]) expect(facts.files).toContain(fact.evidence.file);
  });
  it('keeps imported JS available for type resolution without counting it as analyzed', () => {
    const facts = scan(project({
      'input.ts': "import { helper } from './helper.js'; export function callsHelper() { return helper(); }",
      'helper.js': "throw new Error('must never execute'); export function helper() { return true; }",
    }, ['input.ts']));
    expect(facts.diagnostics).toEqual([]);
    expect(facts.files).toEqual(['input.ts']);
    expect(facts.functions[0]?.returnType).toBe('boolean');
    expect(facts.functions[0]?.references.some(r => r.target.evidence.file === 'helper.js')).toBe(true);
    expect(facts.omissions).toEqual([expect.objectContaining({ evidence: expect.objectContaining({ file: 'helper.js' }) })]);
  });
  it('does not report phantom omissions when allowJs is enabled with no JS inputs', () => {
    const facts = scan(project({ 'only.ts': 'export const predicate = () => true;' }));
    expect(facts.diagnostics).toEqual([]);
    expect(facts.files).toEqual(['only.ts']);
    expect(facts.omissions).toEqual([]);
  });
  it('returns an empty analysis with explicit exclusions for a JS-only program', () => {
    const facts = scan(project({ 'only.js': 'export const ignored = () => true;' }));
    expect(facts.diagnostics).toEqual([]);
    expect(facts.files).toEqual([]);
    expect(facts.functions).toEqual([]);
    expect(facts.types).toEqual([]);
    expect(facts.omissions[0]?.evidence?.file).toBe('only.js');
  });
  it('retains diagnostics from excluded files and still refuses proofs', () => {
    const facts = scan(project({
      'input.ts': "import './broken.js'; export const valid = () => true;",
      'broken.js': 'export function broken( {',
    }, ['input.ts']));
    expect(facts.files).toEqual(['input.ts']);
    expect(facts.diagnostics.some(d => d.category === 'Error' && d.evidence?.file === 'broken.js')).toBe(true);
    expect(facts.functions[0]?.predicate.status).toBe('unsupported');
    expect(facts.omissions[0]?.evidence?.file).toBe('broken.js');
  });
  it('uses the same deterministic manifest and denominator in CLI JSON', () => {
    const dir = project(mixed);
    const result = spawnSync(process.execPath, ['dist/cli/index.js', 'scan', dir, '--json'], { encoding: 'utf8' });
    expect(result.status).toBe(0);
    expect(result.stderr).toBe('');
    const cli = JSON.parse(result.stdout);
    expect(cli).toEqual(scan(dir));
    expect(cli.files).toEqual(analyzed);
    expect(cli.files.length).toBe(4); // experiments count analyzed files with this contract
    expect(cli.omissions.map((o: { evidence: { file: string } }) => o.evidence.file)).toEqual(skipped);
  });
});
