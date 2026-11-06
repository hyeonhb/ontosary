// Review-only probe. Run after pnpm build; does not edit product sources or tests.
// Prints observations, including known defects; exit 0 is not a soundness gate.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
const root = path.resolve(process.argv[2] ?? '.');
const require = createRequire(path.join(root, 'package.json'));
const ts = require('typescript');
const { scan, selectFunction, compare, evaluate, formalConcepts } = await import(pathToFileURL(path.join(root, 'dist/core/index.js')));
const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'ontosary-review-'));
const config = { compilerOptions: { strict: true, target: 'ES2022', module: 'ESNext', types: [] }, include: ['*.ts'] };
function project(name, source, extra = {}) {
  const dir = path.join(temp, name); fs.mkdirSync(dir);
  fs.writeFileSync(path.join(dir, 'tsconfig.json'), JSON.stringify({ ...config, ...extra }));
  fs.writeFileSync(path.join(dir, 'input.ts'), source);
  return dir;
}
async function runtime(source) {
  const js = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 } }).outputText;
  return import('data:text/javascript;base64,' + Buffer.from(js).toString('base64'));
}
function cli(dir, left, right) {
  const r = spawnSync(process.execPath, [path.join(root, 'dist/cli/index.js'), 'compare', dir, left, right, '--assume-same-input', '--json'], { encoding: 'utf8' });
  return { exitCode: r.status, output: r.stdout ? JSON.parse(r.stdout) : null, stderr: r.stderr };
}
try {
  const source = `export type S = 'a' | 'b';
export enum E { A = 'a', B = 'b' }
export function optionalEnum(e?: typeof E) { return e?.A === 'a'; }
export function always(e?: typeof E) { return true; }
export function withThis(this: void, a: S, b: S) { return a === 'a'; }
export function first(a: S, b: S) { return a === 'a'; }
export function second(a: S, b: S) { return b === 'a'; }
export function getEnum(): typeof E { throw new Error('not total'); }
export function callEnum(e?: typeof E) { return getEnum().A === 'a'; }
export function genuineEnum(e: E) { return e === E.A; }
`;
  const dir = project('soundness', source), facts = scan(dir), run = await runtime(source);
  assert.deepEqual(facts.diagnostics, []);
  const p = n => selectFunction(facts, n).predicate;
  const withThis = run.withThis; // invoke unbound: this is undefined, as declared this:void
  assert.equal(p('genuineEnum').status, 'supported');
  let callOutcome;
  try { callOutcome = run.callEnum(); } catch (e) { callOutcome = { throws: e.message }; }
  const soundness = {
    source, diagnostics: facts.diagnostics,
    predicates: Object.fromEntries(facts.functions.map(f => [f.name, f.predicate])),
    optionalVsTrue: cli(dir, 'optionalEnum', 'always'),
    thisVsSecond: cli(dir, 'withThis', 'second'),
    thisVsFirst: compare(p('withThis'), p('first'), { sameInput: true }),
    callVsTrue: compare(p('callEnum'), p('always'), { sameInput: true }),
    execution: { optionalUndefined: run.optionalEnum(undefined), alwaysUndefined: run.always(undefined), withThisAB: withThis('a', 'b'), firstAB: run.first('a', 'b'), secondAB: run.second('a', 'b'), callOutcome }
  };

  const expressions = ["a === 'a'", "a !== 'b'", "!(a !== 'a')", "a === 'a' || a === 'b'", "!(a !== 'a' && a !== 'b')", "a === 'a' && b !== 'c'", "!(a === 'a' && b !== 'c')", "a !== 'a' || b === 'c'", "(a === 'a' || b === 'b') && !(a === 'c')", "b === 'c'", 'true', 'false', "!(a === 'a' || b === 'b')", "a !== 'a' && b !== 'b'", "'a' === a", "!!(a === 'b')"];
  const positivesSource = expressions.map((e, i) => `export function f${i}(a: 'a'|'b'|'c', b: 'a'|'b'|'c') { return ${e}; }`).join('\n');
  const positives = scan(project('positive', positivesSource)), exec = await runtime(positivesSource);
  assert.deepEqual(positives.diagnostics, []);
  let evaluations = 0, pairs = 0, witnesses = 0;
  for (let i = 0; i < expressions.length; i++) {
    const a = selectFunction(positives, `f${i}`).predicate; assert.equal(a.status, 'supported');
    for (const x of ['a','b','c']) for (const y of ['a','b','c']) {
      assert.equal(evaluate(a.logic, {arg0:x,arg1:y}), exec[`f${i}`](x,y)); evaluations++;
    }
    for (let j = 0; j < expressions.length; j++) {
      const b = selectFunction(positives, `f${j}`).predicate;
      const result = compare(a,b,{sameInput:true});
      let leftOnly=false,rightOnly=false;
      for (const x of ['a','b','c']) for (const y of ['a','b','c']) {
        const l=exec[`f${i}`](x,y),r=exec[`f${j}`](x,y);
        leftOnly ||= l&&!r; rightOnly ||= !l&&r;
      }
      assert.equal(result.leftImpliesRight,!leftOnly); assert.equal(result.rightImpliesLeft,!rightOnly);
      assert.equal(result.status,!leftOnly&&!rightOnly?'Equivalent':!leftOnly||!rightOnly?'Implies':'Different');
      for (const side of ['leftOnly','rightOnly']) if(result[side]) {
        const w=result[side],l=exec[`f${i}`](w.arg0??'a',w.arg1??'a'),r=exec[`f${j}`](w.arg0??'a',w.arg1??'a');
        assert.ok(side==='leftOnly'?l&&!r:!l&&r); witnesses++;
      }
      pairs++;
    }
  }
  const boundarySource = [12,13].map(n=>`export function b${n}(${Array.from({length:n},(_,i)=>`x${i}: 'a'|'b'`).join(',')}) { return ${Array.from({length:n},(_,i)=>`x${i} === 'a'`).join(' && ')}; }`).join('\n');
  const bounds = scan(project('bounds',boundarySource)); assert.deepEqual(bounds.diagnostics,[]);
  const boundary = Object.fromEntries([12,13].map(n=>{ const p=selectFunction(bounds,`b${n}`).predicate; return [n,compare(p,p,{sameInput:true})]; }));
  assert.equal(boundary[12].evaluatedAssignments,4096); assert.equal(boundary[12].status,'Equivalent');
  assert.equal(boundary[13].evaluatedAssignments,0); assert.equal(boundary[13].status,'Unknown');

  // Oracle enumerates object subsets (implementation traverses attribute closures).
  const objects=['o0','o1','o2','o3'], attrs=['z','a','m'];
  const canonical=a=>JSON.stringify([...a].sort());
  for(let matrix=0;matrix<4096;matrix++) {
    const incidence=Object.fromEntries(objects.map((o,i)=>[o,attrs.filter((_,j)=>matrix & (1<<(i*3+j)))]));
    const expected=new Map();
    for(let bits=0;bits<16;bits++) {
      const selected=objects.filter((_,i)=>bits & (1<<i));
      const intent=attrs.filter(a=>selected.every(o=>incidence[o].includes(a)));
      const extent=objects.filter(o=>intent.every(a=>incidence[o].includes(a)));
      expected.set(canonical(intent),canonical(extent));
    }
    const output=formalConcepts({objects,attributes:attrs,incidence});
    assert.equal(output.truncated,false); assert.equal(output.concepts.length,expected.size);
    for(const c of output.concepts) assert.equal(expected.get(canonical(c.intent)),canonical(c.extent));
  }
  const jsdir=project('mixed-js',"export function tsFunction() { return true; }",{compilerOptions:{...config.compilerOptions,allowJs:true},include:['*.ts','*.js']});
  fs.writeFileSync(path.join(jsdir,'ignored.js'), 'export function jsFunction() { return true; }');
  const js=scan(jsdir);
  assert.deepEqual(js.diagnostics,[]);
  console.log(JSON.stringify({environment:{node:process.version,typescript:ts.version},soundness,positive:{expressions:expressions.length,evaluations,pairs,witnesses,boundary},fca:{contexts:4096,shape:'4 objects x 3 attributes',attributeOrder:attrs,oracle:'object-subset enumeration',passed:true},mixedJs:{files:js.files,functions:js.functions.map(f=>f.name),omissions:js.omissions}},null,2));
} finally { fs.rmSync(temp,{recursive:true,force:true}); }
