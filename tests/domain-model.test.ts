import { beforeAll, afterAll, describe, expect, it } from 'vitest';
import ts from 'typescript';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { observeRoles, binaryContext, sha } from '../experiments/domain-model/v1/observe.mjs';
import { validateModel } from '../experiments/domain-model/v1/validate.mjs';
let root: string;
const text = `export class Target { cancel() {} }
class Other { cancel() {} }
class Subject {
  constructor(private t: Target, private o: Other, private unsafe: any) {}
  declarationOnly(t: Target) { const cancel = t.cancel; return cancel; }
  direct() { this.t.cancel(); }
  different() { this.o.cancel(); }
  nested() { return () => this.t.cancel(); }
  bracket() { this.t['cancel'](); }
  optional() { this.t?.cancel(); }
  uncertain() { this.unsafe.cancel(); }
  computed(k: string) { this.unsafe[k](); }
  nestedClass() { class Inner { run(t: Target) { t.cancel(); } } return Inner; }
  ambiguous(t: Target | Other) { t.cancel(); }
  aliasExcluded() { const fn = this.t.cancel; fn(); }
  get accessor() { this.t.cancel(); return 1; }
  field = () => this.t.cancel();
}
`;
const spec = { revision:'fixture',classes:[{name:'Subject',file:'input.ts'}],attributes:[{id:'cancel',label:'direct target member occurrence',targets:[{name:'Target',file:'input.ts',member:'cancel'}],arguments:'any'}] };
let observation: ReturnType<typeof observeRoles>;
beforeAll(() => {
 root=fs.mkdtempSync(path.join(os.tmpdir(),'ontosary-model-'));
 fs.writeFileSync(path.join(root,'input.ts'),text);
 const program=ts.createProgram([path.join(root,'input.ts')],{strict:true,types:[],target:ts.ScriptTarget.ES2022});
 expect(ts.getPreEmitDiagnostics(program)).toEqual([]);
 observation=observeRoles(program,spec,root);
});
afterAll(()=>fs.rmSync(root,{recursive:true,force:true}));
describe('role observer uses call role and declaration identity',()=>{
 it.each([['declarationOnly','no'],['direct','yes'],['different','no'],['nested','yes'],['bracket','yes'],['optional','yes'],['uncertain','unknown'],['computed','unknown'],['nestedClass','no'],['aliasExcluded','no'],['ambiguous','unknown']])('%s is %s',(name,value)=>{
  expect(observation.objects.find((o:any)=>o.name===name).cells.cancel.value).toBe(value);
 });
 it('excludes constructors/accessors/field callbacks from own method objects',()=>expect(observation.objects).toHaveLength(11));
 it('unknown never enters binary incidence',()=>expect(binaryContext(observation,spec.attributes)).toEqual({status:'unknown-cells',context:null}));
 it('missing target and diagnostics conservatively produce unknown',()=>{
  const program=ts.createProgram([path.join(root,'input.ts')],{types:[]});
  for(const [selected,diagnostics] of [[spec,[{code:1}]],[{...spec,attributes:[{...spec.attributes[0],targets:[{name:'Missing',file:'input.ts',member:'cancel'}]}]},[]]] as any[]){
   const result=observeRoles(program,selected,root,diagnostics);
   expect(result.facts.every((f:any)=>f.value==='unknown')).toBe(true);
  }
 });
});
const evidence={file:'a.ts',symbol:'x',offset:0,line:1,anchor:'const x = 1;',sha256:sha('const x = 1;')};
const fact={id:'f',kind:'observed-in-source',author:'agent',method:'manual',scope:'fixture static source',support:'manual',claim:'x declaration',evidence};
const item={id:'i',kind:'concept-candidate',label:'x',status:'pending-review',author:'agent',interpretation:'hypothesis',unverified:['meaning?'],factRefs:['f'],candidateRefs:['c'],relatedItems:[],intendedPolicy:null};
const model={revision:'fixed',author:'agent',scope:'fixture',useContract:'reread stale source',items:[item],approvedKnowledge:[]};
const candidate={id:'c',factRefs:['f']};
const check=(m:any=model,f:any[]=[fact],c:any[]=[candidate],source='const x = 1;')=>validateModel(m,f,c,()=>source);
describe('model evidence validator is not a semantic approver',()=>{
 it('accepts intact pending model without granting approval',()=>{const r=check();expect(r.valid).toBe(true);expect(r.semanticApproval).toContain('not-assessed');});
 it('marks source edits and linked items stale',()=>{const r=check(model,[fact],[candidate],'const x = 2;');expect(r.valid).toBe(false);expect(r.staleItems).toEqual(['i']);});
 it('detects wrong anchor even with matching hash',()=>expect(check(model,[{...fact,evidence:{...evidence,anchor:'wrong'}}]).valid).toBe(false));
 it('detects missing source',()=>expect(validateModel(model,[fact],[candidate],()=>{throw Error('missing');}).staleItems).toEqual(['i']));
 it.each(['factRefs','candidateRefs','relatedItems'])('rejects broken %s',(key)=>expect(check({...model,items:[{...item,[key]:['absent']}]}).valid).toBe(false));
 it('rejects missing collections',()=>expect(validateModel({},[],[],()=>text).valid).toBe(false));
 it('rejects duplicate IDs',()=>expect(check(model,[fact,fact]).valid).toBe(false));
 it('rejects missing provenance',()=>expect(check(model,[{...fact,scope:undefined}]).valid).toBe(false));
 it('does not accept approved status without decision',()=>expect(check({...model,items:[{...item,status:'approved'}]}).valid).toBe(false));
 it('rejects incomplete or agent approval records',()=>{
  expect(check({...model,approvedKnowledge:[{id:'decision',itemRef:'i'}]}).valid).toBe(false);
  expect(check({...model,approvedKnowledge:[{id:'decision',itemRef:'i',decision:{actor:'agent',actorKind:'agent',rationale:'pass',at:'2026-11-08',evidenceRefs:['f']}}]}).valid).toBe(false);
 });
 it('propagates stale candidate support to model even with intact direct fact',()=>{
  const second={...fact,id:'other',evidence:{...evidence,sha256:'0'.repeat(64)}};
  const r=check(model,[fact,second],[{...candidate,factRefs:['other']}]);expect(r.staleItems).toEqual(['i']);
 });
});
