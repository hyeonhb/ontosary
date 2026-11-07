// Review-only observation probe; exit 0 reports behavior and is not a correctness gate.
// Mutations below affect in-memory copies only; historical corpus evidence is preserved.
import fs from 'node:fs';import path from 'node:path';import os from 'node:os';import {gunzipSync} from 'node:zlib';import {pathToFileURL} from 'node:url';
const root=process.cwd();
const {scan}=await import(pathToFileURL(path.join(root,'dist/core/index.js')));
const {evaluateLabel}=await import(pathToFileURL(path.join(root,'experiments/corpus/evaluate-labels.mjs')));
const dir=fs.mkdtempSync(path.join(os.tmpdir(),'ontosary-label-review-'));
const source='export function unused() { return true; }\nexport function recursive() { return recursive(); }';
try {
fs.writeFileSync(path.join(dir,'tsconfig.json'),JSON.stringify({compilerOptions:{strict:true,types:[]},include:['input.ts']}));
fs.writeFileSync(path.join(dir,'input.ts'),source.replace('recursive() {','recursive(): boolean {'));
const facts=scan(dir);
const examples=facts.functions.map(f=>({name:f.name,references:f.references,result:evaluateLabel({id:f.name,kind:'reference',name:f.name,source:{file:'input.ts',offset:f.evidence.start.offset},target:{file:'input.ts',offset:f.evidence.start.offset}},facts)}));
const labels=JSON.parse(fs.readFileSync('experiments/corpus/labels.json'));
const date=JSON.parse(gunzipSync(fs.readFileSync('experiments/corpus/results/2026-11-07/date-fns-weekday-scan.json.gz')));
const l=labels.labels.find(l=>l.id==='date-fns-10');
const original=date.types.find(f=>f.name==='DateArg');const changed=structuredClone(date);changed.types.find(f=>f.name==='DateArg').type='never';
const queue=JSON.parse(gunzipSync(fs.readFileSync('experiments/corpus/results/2026-11-07/p-queue-priority-queue-scan.json.gz')));
const ql=labels.labels.find(l=>l.id==='p-queue-02'); const qchanged=structuredClone(queue);qchanged.functions.find(f=>f.name==='lowerBound').parameters.find(p=>p.name==='array').type='number';
const actualLabel=labels.labels.find(l=>l.id==='p-queue-04');const qrefs=structuredClone(queue);const qf=qrefs.functions.find(f=>f.name==='lowerBound'); qf.references=qf.references.filter(r=>r.target.name!=='comparator'||r.evidence.start.offset===r.target.evidence.start.offset);
console.log(JSON.stringify({diagnostics:facts.diagnostics,examples,claimMutation:{label:l.id,claim:l.claim,originalType:original.type,original:evaluateLabel(l,date),mutatedType:'never',mutated:evaluateLabel(l,changed)},parameterMutation:{label:ql.id,claim:ql.claim,mutatedType:'number',result:evaluateLabel(ql,qchanged)},existingComparatorLabelAfterRemovingUses:evaluateLabel(actualLabel,qrefs)},null,2));
} finally{fs.rmSync(dir,{recursive:true,force:true});}
