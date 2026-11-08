import fs from 'node:fs';
import path from 'node:path';
import { gunzipSync } from 'node:zlib';
import { pathToFileURL } from 'node:url';
import { validateModel } from '../v1/validate.mjs';
import { checkAnalysisInputs } from './inputs.mjs';
export function validateInput(root,results,{anchorsOnly=false}={}) {
 const model=JSON.parse(fs.readFileSync(path.join(results,'model-after.json'),'utf8'));
 const facts=JSON.parse(gunzipSync(fs.readFileSync(path.join(results,'facts.json.gz'))));
 const candidates=JSON.parse(fs.readFileSync(path.join(results,'fca.json'),'utf8')).candidates;
 const anchors=validateModel(model,facts,candidates,f=>fs.readFileSync(path.join(root,f),'utf8'));
 const inputs=anchorsOnly?{valid:false,status:'not-checked'}:checkAnalysisInputs(root);
 const invalidatedFacts=inputs.valid?[]:facts.filter(f=>f.method==='typescript-ast-symbol-identity').map(f=>f.id);
 const invalidatedCandidates=inputs.valid?[]:candidates.map(c=>c.id);
 // Conservative whole-model review: source-only interpretations coexist with automatic role evidence.
 const staleItems=inputs.valid?anchors.staleItems:model.items.map(i=>i.id).sort();
 return {valid:anchors.valid&&inputs.valid,anchorValid:anchors.valid,analysisInputsValid:inputs.valid,status:anchors.valid&&inputs.valid?'verified':anchorsOnly?'partial':'requires-review',requiresReview:!anchors.valid||!inputs.valid,
  semanticApproval:anchors.semanticApproval,anchorErrors:anchors.errors,analysisInputs:inputs,staleFacts:[...new Set([...anchors.staleFacts,...invalidatedFacts])].sort(),staleCandidates:invalidatedCandidates,staleItems};
}
if(process.argv[1] && import.meta.url===pathToFileURL(process.argv[1]).href){
 const [root,results,mode]=process.argv.slice(2);
 const result=validateInput(root,results,{anchorsOnly:mode==='--anchors-only'});
 console.log(JSON.stringify(result,null,2));process.exitCode=result.valid?0:1;
}
