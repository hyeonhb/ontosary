// Review-only fixture: scans temporary TypeScript source and asserts source-authored expectations.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
const repo=process.cwd();
const {scan}=await import(pathToFileURL(path.join(repo,'dist/core/index.js')));
const {evaluateLabel}=await import(pathToFileURL(path.join(repo,'experiments/corpus/v3/evaluate-labels.mjs')));
const source=`const key = 'slot';
export function identity<T>(input: T) { return input; }
export function mixed() {
  interface Same { flag: boolean }
  const Same = { flag: true };
  type Default<T = typeof Same> = T;
  const result = { [key]: identity<boolean>(Same.flag) };
  return result.slot;
}
export function typeOnly() {
  interface Shape { readonly [key]: boolean }
  type Alias<U extends Shape = Shape> = U;
  return true;
}
`;
const loc=anchor=>{const offset=source.indexOf(anchor);assert.ok(offset>=0&&source.indexOf(anchor,offset+1)===-1);return{file:'input.ts',anchor,offset,line:source.slice(0,offset).split('\n').length};};
const cases=[
 ['type-default-query','mixed','Same> = T','interface Same','reference','mismatch'],
 ['runtime-computed-key','mixed','key]: identity',"key = 'slot'",'reference','correct'],
 ['runtime-generic-call','mixed','identity<boolean>','export function identity','call','correct'],
 ['runtime-same-name-value','mixed','Same.flag)', 'interface Same','reference','correct'],
 ['runtime-property','mixed','flag) }','flag: true','reference','correct'],
 ['type-computed-key','typeOnly','key]: boolean',"key = 'slot'",'reference','mismatch'],
 ['constrained-type-parameter','typeOnly','U extends Shape','U extends Shape','reference','mismatch'],
 ['type-constraint','typeOnly','Shape = Shape','interface Shape','reference','mismatch'],
];
const root=fs.mkdtempSync(path.join(os.tmpdir(),'ontosary-v3-review-'));
try{
 fs.writeFileSync(path.join(root,'input.ts'),source);
 fs.writeFileSync(path.join(root,'tsconfig.json'),JSON.stringify({compilerOptions:{strict:true,types:[]},files:['input.ts']}));
 const facts=scan(root);assert.deepEqual(facts.diagnostics,[]);
 const observations=cases.map(([id,name,use,target,usageKind,expected])=>{
 const label={id,name,kind:'reference',contractVersion:2,source:loc(`export function ${name}(`),use:loc(use),target:loc(target),usageKind,unverified:[]};
 const result=evaluateLabel(label,facts,{readSource:()=>source});
 assert.equal(result.status,expected,id);
 return {id,expected,label,result};
 });
 console.log(JSON.stringify({reviewedRevision:'2dba3e2e52a3e085fcfe35fdee87a1fd16aa1365',source,diagnostics:facts.diagnostics,total:observations.length,passed:observations.length,labelClarification:'The initial same-name value label targeted the const declaration and was mislinked. The unchanged analyzer represents a merged symbol by declarations[0], here interface Same. This probe tests acceptance of the runtime use with that documented source-code identity, not value-declaration or data-flow resolution.',observations},null,2));
}finally{fs.rmSync(root,{recursive:true,force:true});}
