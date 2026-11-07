// Independent review probe: controlled fixtures only; never executes scanned user code.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
const root=path.resolve(process.argv[2]??'.');
const require=createRequire(path.join(root,'package.json'));
const ts=require('typescript');
const {scan,selectFunction,compare,evaluate}=await import(pathToFileURL(path.join(root,'dist/core/index.js')));
const dir=fs.mkdtempSync(path.join(os.tmpdir(),'ontosary-followup-'));
function write(name,value){fs.writeFileSync(path.join(dir,name),value);}
try {
  write('tsconfig.json',JSON.stringify({compilerOptions:{strict:true,target:'ES2022',module:'ESNext',moduleResolution:'Bundler',types:[],allowJs:true,resolveJsonModule:true},include:['*.ts','*.js']}));
  write('enums.ts',`export enum E { A='a', B='b' }\nexport enum N { A=-1, B=2 }\nexport const enum C { A='a', B='b' }`);
  write('barrel.ts',`export { E as Renamed, N, C } from './enums';`);
  const receivers={satisfies:'(E satisfies typeof E)',comma:'(touch(), E)',conditional:"(s === 'a' ? E : E)",nonNull:'E!',assertion:'(E as typeof E)',optional:'maybe?.A',nested:'box.e',valueAlias:'alias',call:'make()',parameter:'value',computed:"({ e: E })['e']",optionalNested:'box?.e'};
  const wrappers=[x=>x,x=>`!(${x})`,x=>`true || (${x})`];
  const negative=Object.entries(receivers).flatMap(([name,receiver])=>wrappers.map((wrap,i)=>({name:`reject_${name}_${i}`,expression:wrap(`${name==='optional'?receiver:`${receiver}.A`} === 'a'`)})));
  const code=`import { Renamed as E, N, C } from './barrel';
export type S='a'|'b';
const alias=E;
function touch() { return true; }
function make() { return E; }
${negative.map(x=>`export function ${x.name}(s:S, maybe:typeof E|undefined, box:{e:typeof E}, value:typeof E) { return ${x.expression}; }`).join('\n')}
export function renamed(s:S) { return s === E.A; }
export function parenthesized(s:S) { return ((E)).A === s; }
export function constEnum(s:S) { return s === C.A; }
export function numeric(n:N) { return n === N.A; }
export function numericNegation(n:N) { return !(n !== N.A); }
export function normal(s:S) { return s === 'a'; }
export const expressionThis = function(this:void,s:S) { return s === 'a'; };
export const object = { objectMethod(this:void,s:S) { return s === 'a'; } };
export class Class { classMethod(this:void,s:S) { return s === 'a'; } }
export function branchThis(this:void,s:S) { if(s === 'a') return true; return false; }
`;
  write('input.ts',code);
  write('empty.js','');
  write('only-comment.js','// Nothing to analyze.\n');
  write('data.json','{"kind":"a"}');
  write('json.ts',`import data from './data.json'; export function readJson(){return data.kind;}`);
  const facts=scan(dir); assert.deepEqual(facts.diagnostics,[]);
  const predicate=name=>selectFunction(facts,name).predicate;
  for(const n of negative){
    const fact=selectFunction(facts,n.name); assert.equal(fact.predicate.status,'unsupported',n.name);
    const returned=fact.conditions.filter(c=>c.kind==='return');assert.equal(returned.length,1);assert.deepEqual(returned[0].normalization,fact.predicate);
    const c=compare(fact.predicate,predicate('normal'),{sameInput:true});assert.equal(c.status,'Unsupported');assert.equal(c.evaluatedAssignments,0);assert.ok(!('equivalent' in c));
  }
  const thisNames=['expressionThis','objectMethod','classMethod','branchThis'];
  for(const name of thisNames){const f=selectFunction(facts,name);assert.equal(f.predicate.status,'unsupported');assert.ok(f.conditions.length>0);for(const c of f.conditions){assert.equal(c.normalization.status,'unsupported');assert.match(c.normalization.reason,/this/);}}
  // Compile and execute only this generated fixture; require() is restricted to its local modules.
  const modules={};
  function load(name){
    if(modules[name])return modules[name];
    const file=name.replace(/^\.\//,'')+'.ts';
    const emitted=ts.transpileModule(fs.readFileSync(path.join(dir,file),'utf8'),{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.CommonJS}}).outputText;
    const module={exports:{}};modules[name]=module.exports;
    new Function('require','module','exports',emitted)(load,module,module.exports);return module.exports;
  }
  const runtime=load('./input');
  let evaluations=0;
  for(const name of ['renamed','parenthesized','constEnum','normal','numeric','numericNegation']){
    const p=predicate(name);assert.equal(p.status,'supported',name);
    for(const value of name.startsWith('numeric')?[-1,2]:['a','b']){assert.equal(evaluate(p.logic,{arg0:value}),runtime[name](value));evaluations++;}
  }
  const comparisons={renamed:compare(predicate('renamed'),predicate('normal'),{sameInput:true}),constantEnum:compare(predicate('constEnum'),predicate('normal'),{sameInput:true}),numeric:compare(predicate('numeric'),predicate('numericNegation'),{sameInput:true})};
  for(const c of Object.values(comparisons))assert.equal(c.status,'Equivalent');
  assert.deepEqual(facts.files,['barrel.ts','enums.ts','input.ts','json.ts']);
  const excluded=facts.omissions.filter(x=>x.reason.startsWith('Unsupported source file extension'));
  assert.deepEqual(excluded.map(x=>x.evidence.file),['data.json','empty.js','only-comment.js']);
  for(const x of excluded){assert.ok(x.evidence.start.offset>=0);assert.ok(x.evidence.end.offset>=x.evidence.start.offset);}
  const cli=spawnSync(process.execPath,[path.join(root,'dist/cli/index.js'),'scan',dir,'--json'],{encoding:'utf8'});
  assert.equal(cli.status,0);assert.deepEqual(JSON.parse(cli.stdout),facts);
  console.log(JSON.stringify({schemaVersion:1,reviewedCommit:spawnSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).stdout.trim(),environment:{node:process.version,typescript:ts.version},diagnostics:facts.diagnostics,negativeCases:negative,negativeCasesPassed:negative.length,explicitThisCases:thisNames,positiveEvaluations:evaluations,comparisons,files:facts.files,excluded,cliParity:true,result:'All independent boundary assertions passed'},null,2));
}finally{fs.rmSync(dir,{recursive:true,force:true});}
