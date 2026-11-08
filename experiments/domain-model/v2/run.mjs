import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import { checkAnalysisInputs } from './inputs.mjs';
import { validateInput } from './validate.mjs';
import { navigate } from './navigate.mjs';
import { sha } from '../v1/observe.mjs';
const [root,out]=process.argv.slice(2),here=path.dirname(fileURLToPath(import.meta.url));
const inputs=checkAnalysisInputs(root);
if(!inputs.valid) throw new Error(JSON.stringify(inputs));
// Historical V1 is immutable. Reuse its extraction/FCA, including redundant historical guards.
execFileSync(process.execPath,[path.join(here,'../v1/run.mjs'),root,out],{stdio:'inherit'});
const write=(file,data)=>fs.writeFileSync(path.join(out,file),JSON.stringify(data,null,2)+'\n');
const model=JSON.parse(fs.readFileSync(path.join(out,'model-after.json'),'utf8'));
write('navigation.json',Object.fromEntries(model.items.map(i=>[i.id,navigate(model,i.id)])));
write('validation-v2.json',validateInput(root,out));
write('contract-v2.json',{baseRevision:'2cd6e72d553ae61954f8469c31f0d6e41ef0a883',version:2,modelUnchanged:true,semanticChanges:0,inputValidation:inputs,
 fingerprints:Object.fromEntries(fs.readdirSync(here).filter(f=>f.endsWith('.mjs')).sort().map(f=>[f,sha(fs.readFileSync(path.join(here,f)))]))});
