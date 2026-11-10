// Local synthetic tools only; no model calls. Output directory must not exist.
import fs from 'node:fs';import os from 'node:os';import path from 'node:path';import {gzipSync} from 'node:zlib';import {createHash} from 'node:crypto';
import {configuration,runTool} from '../../../../../work/s2-build/trial/runtime.js';
import {collectUsage,usageEnd} from '../../../../../work/s2-build/trial/telemetry.js';
const [codex,out]=process.argv.slice(2);if(!codex||!out||fs.existsSync(out))throw Error('New output directory required');fs.mkdirSync(out,{recursive:true});
const root=fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(),'s2-extra-runtime-')));
const l={root,source:path.join(root,'source'),materials:path.join(root,'materials'),auxiliary:path.join(root,'auxiliary'),scratch:path.join(root,'scratch'),home:path.join(root,'home'),control:path.join(root,'control'),readOnly:[path.join(root,'bin')],denied:['/Users']};
for(const key of ['source','materials','auxiliary','scratch','home','control'])fs.mkdirSync(l[key]);fs.mkdirSync(path.join(root,'bin'));
const node=path.join(root,'bin/node');fs.copyFileSync(fs.realpathSync(process.execPath),node);fs.chmodSync(node,0o555);fs.writeFileSync(path.join(l.control,'config.toml'),configuration(l));
const rows=[];const raw=[{type:'turn.started'},{type:'turn.completed',usage:{input_tokens:10,output_tokens:2}}].map(e=>JSON.stringify(e)).join('\n');
try{
 const warm=await runTool(codex,l,[node,'-e','console.log("ready")'],5000);if(warm.code!==0)throw Error('Warmup failed');
 for(const name of ['nonzero','signal','truncated']){
  const code=`console.log(${JSON.stringify(raw)});`+(name==='nonzero'?'process.exit(7);':name==='signal'?'setInterval(()=>{},1000);':'process.stdout.write("x".repeat(5*1024*1024));');
  const timer=name==='signal'?setTimeout(()=>process.kill(process.pid,'SIGINT'),150):null;
  let r;try{r=await runTool(codex,l,[node,'-e',code],3000);}finally{if(timer)clearTimeout(timer);}
  const file=name+'.stdout.jsonl.gz',data=Buffer.from(r.stdout);fs.writeFileSync(path.join(out,file),gzipSync(data));
  const summary=collectUsage(r.stdout.trim().split('\n'),usageEnd(r)).summary();
  if(summary.complete)throw Error('False complete');
  rows.push({name,run:{...r,stdout:undefined},raw:{file,bytes:data.length,sha256:createHash('sha256').update(data).digest('hex'),coverage:r.outputTruncated?'captured prefix only; truncated':'captured stdout'},summary});
 }
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({providerCalls:0,rows},null,2)+'\n');
}finally{fs.rmSync(root,{recursive:true,force:true});}
