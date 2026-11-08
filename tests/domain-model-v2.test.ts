import { describe,it,expect,afterAll } from 'vitest';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawnSync } from 'node:child_process';
import { navigate } from '../experiments/domain-model/v2/navigate.mjs';
const results='experiments/domain-model/results/2026-11-08';
const model=JSON.parse(fs.readFileSync(`${results}/model-after.json`,'utf8'));
const facts=new Set(JSON.parse((await import('node:zlib')).gunzipSync(fs.readFileSync(`${results}/facts.json.gz`)).toString()).map((f:any)=>f.id));
describe('V2 actual consumer navigation',()=>{
 it.each([['order',['branch']],['cancel-request',['dialog-submit','cancel-transport','refund-also-cancels','dismiss']],['refund-request',['refund-transport','refund-also-cancels','dismiss']]])('%s reaches actions with evidence',(id,targets)=>{
  const result=navigate(model,id);
  for(const target of targets){const route=result.paths.find((p:any)=>p.to===target);expect(route.direction).toBe('incoming');expect(route.declaredEdge).toEqual([target,id]);expect(route.factRefs.every((f:string)=>facts.has(f))).toBe(true);}
 });
 it('does not traverse unrelated transitive paths',()=>expect(navigate(model,'order').paths.some((p:any)=>p.to==='refund-transport')).toBe(false));
 it('unknown ID does not fabricate connections',()=>expect(navigate(model,'absent')).toEqual({found:false,id:'absent',paths:[]}));
 it('CLI exposes the same contract',()=>{const r=spawnSync(process.execPath,['experiments/domain-model/v2/navigate.mjs',`${results}/model-after.json`,'cancel-request'],{encoding:'utf8'});expect(r.status).toBe(0);expect(JSON.parse(r.stdout)).toEqual(navigate(model,'cancel-request'));});
});
const root='/tmp/ontosary-vendure-preparation-20261108/vendure';
const scratch=fs.mkdtempSync(path.join(os.tmpdir(),'ontosary-v2-'));
afterAll(()=>fs.rmSync(scratch,{recursive:true,force:true}));
const run=(source:string,mode?:string)=>{const r=spawnSync(process.execPath,['experiments/domain-model/v2/validate.mjs',source,results,...(mode?[mode]:[])],{encoding:'utf8'});return {exit:r.status,...JSON.parse(r.stdout)};};
describe.skipIf(!fs.existsSync(root))('V2 validator CLI on pinned prepared cache (read-only)',()=>{
 it('accepts intact analysis inputs and anchors',()=>{const r=run(root);expect(r.exit).toBe(0);expect(r.anchorValid).toBe(true);expect(r.analysisInputsValid).toBe(true);});
 it('anchor-only mode never grants full validity',()=>{const r=run(root,'--anchors-only');expect(r.anchorValid).toBe(true);expect(r.valid).toBe(false);expect(r.status).toBe('partial');expect(r.staleFacts).toHaveLength(468);});
 it('target-only edit is caught while occurrence anchors stay intact',()=>{
  const m=JSON.parse(fs.readFileSync('experiments/domain-model/v1/manifest.json','utf8'));
  for(const file of Object.keys(m.inputHashes)){const dest=path.join(scratch,file);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.copyFileSync(path.join(root,file),dest);}
  const file='packages/admin-ui/src/lib/core/src/providers/modal/modal.service.ts',dest=path.join(scratch,file),text=fs.readFileSync(dest,'utf8');
  fs.writeFileSync(dest,text.replaceAll('fromComponent','renamedComponent'));
  const r=run(scratch);expect(r.exit).toBe(1);expect(r.anchorValid).toBe(true);expect(r.analysisInputsValid).toBe(false);expect(r.analysisInputs.reason).toContain(file);expect(r.staleFacts).toHaveLength(468);expect(r.staleCandidates).toHaveLength(5);expect(r.staleItems).toHaveLength(12);
  fs.writeFileSync(dest,text);
 });
 it('missing resolution configuration is not success',()=>{const r=run(scratch);expect(r.valid).toBe(false);expect(r.analysisInputs.status).toBe('unverified-or-changed');});
 it('source edits invalidate both anchor and input checks',()=>{
  const file=path.join(scratch,'packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts');fs.appendFileSync(file,'\n// fixture edit\n');
  const r=run(scratch);expect(r.anchorValid).toBe(false);expect(r.analysisInputsValid).toBe(false);expect(r.requiresReview).toBe(true);
 });
});
