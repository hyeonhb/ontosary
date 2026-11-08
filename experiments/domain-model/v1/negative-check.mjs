import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { gunzipSync } from 'node:zlib';
import { validateModel } from './validate.mjs';
const [root,results]=process.argv.slice(2);
const load=f=>JSON.parse(fs.readFileSync(path.join(results,f),'utf8'));
const model=load('model-after.json'),facts=JSON.parse(gunzipSync(fs.readFileSync(path.join(results,'facts.json.gz')))),candidates=load('fca.json').candidates;
const cases=[];
function probe(name,mutate,sourceChange=false){
 const m=structuredClone(model),f=structuredClone(facts),c=structuredClone(candidates);
 mutate(m,f,c);
 const result=validateModel(m,f,c,file=>fs.readFileSync(path.join(root,file),'utf8')+(sourceChange?'\n// simulated edit':'') );
 assert.equal(result.valid,false,name);
 if(sourceChange) assert.equal(result.staleItems.length,model.items.length);
 cases.push({name,valid:result.valid,errorCodes:[...new Set(result.errors.map(e=>e.code))],staleItems:result.staleItems});
}
probe('source hash changed (in-memory only)',()=>{},true);
probe('anchor mismatched',(m,f)=>{f[0].evidence.anchor='not the source';});
probe('broken fact ref',m=>{m.items[0].factRefs=['absent'];});
probe('broken candidate ref',m=>{m.items[0].candidateRefs=['absent'];});
probe('duplicate ID',(m,f)=>{f[1].id=f[0].id;});
probe('missing provenance',(m,f)=>{delete f[0].scope;});
probe('approval without decision',m=>{m.items[0].status='approved';});
probe('incomplete human decision',m=>{m.approvedKnowledge=[{id:'decision',itemRef:m.items[0].id,decision:{actor:'reviewer',actorKind:'human'}}];});
console.log(JSON.stringify({scope:'Copied records/in-memory source edits only; upstream untouched. Structural evidence validity, not semantic truth.',cases},null,2));
