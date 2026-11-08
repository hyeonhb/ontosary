import fs from 'node:fs';
import { pathToFileURL } from 'node:url';
export function navigate(model,id) {
 const start=model.items.find(i=>i.id===id);
 if(!start) return {found:false,id,paths:[]};
 const paths=model.items.filter(i=>i.id!==id).flatMap(item=>{
  const directions=[];
  if(start.relatedItems.includes(item.id)) directions.push('outgoing');
  if(item.relatedItems.includes(id)) directions.push('incoming');
  return directions.map(direction=>({from:id,to:item.id,direction,declaredEdge:direction==='outgoing'?[id,item.id]:[item.id,id],kind:item.kind,factRefs:item.factRefs,candidateRefs:item.candidateRefs}));
 });
 return {found:true,id,factRefs:start.factRefs,candidateRefs:start.candidateRefs,contract:'One-hop incoming/outgoing reference lookup; no transitive closure or symmetric business relation inferred',paths};
}
if(process.argv[1] && import.meta.url===pathToFileURL(process.argv[1]).href){
 const [file,id]=process.argv.slice(2);const result=navigate(JSON.parse(fs.readFileSync(file,'utf8')),id);
 console.log(JSON.stringify(result,null,2));process.exitCode=result.found?0:1;
}
