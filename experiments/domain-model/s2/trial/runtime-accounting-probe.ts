import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { configuration, runTool, Layout, tree, collectDiagnostic, snapshot } from './runtime.js';
import { checkedSnapshot, checkedDiagnosticSnapshot } from './snapshot-gate.js';
import { collectUsage, usageEnd } from './telemetry.js';
const [codex,out]=process.argv.slice(2);
if(!codex||!out||fs.existsSync(out))throw Error('Usage: runtime-accounting-probe <codex> <new-report>');
const rows:unknown[]=[],failures:{repeat:number;name:string;error:string}[]=[];
const wait=(ms:number)=>new Promise(resolve=>setTimeout(resolve,ms));
for(let repeat=1;repeat<=2;repeat++)for(const name of ['normal','timeout','normal-child','detached','grandchild','open-handle','inherited-pipe','truncated','spawn-error','interrupted','kill-error']) {
    const root=fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(),'s2-runtime-v2-')));
    const l:Layout={root,source:path.join(root,'source'),materials:path.join(root,'materials'),auxiliary:path.join(root,'auxiliary'),scratch:path.join(root,'scratch'),home:path.join(root,'home'),control:path.join(root,'control'),readOnly:[path.join(root,'bin')],denied:['/Users']};
    for(const key of ['source','materials','auxiliary','scratch','home','control'] as const)fs.mkdirSync(l[key]);
    fs.mkdirSync(path.join(root,'bin'));const node=path.join(root,'bin/node');fs.copyFileSync(fs.realpathSync(process.execPath),node);fs.chmodSync(node,0o555);
    fs.writeFileSync(path.join(l.control,'config.toml'),configuration(l));fs.writeFileSync(path.join(l.source,'original.txt'),'baseline');
    const next=path.join(root,'next-run');fs.mkdirSync(next);fs.writeFileSync(path.join(next,'canary'),'NONSECRET');
    const baseline=tree(l.source),late=path.join(l.source,'late.txt'),cross=path.join(l.source,'cross.json');
    const writer=`const fs=require('node:fs');const fd=fs.openSync(${JSON.stringify(late)},'a');setTimeout(()=>{fs.writeSync(fd,'late');fs.closeSync(fd);try{fs.writeFileSync(${JSON.stringify(path.join(next,'canary'))},'bad');fs.writeFileSync(${JSON.stringify(cross)},'WRITE');}catch(e){fs.writeFileSync(${JSON.stringify(cross)},e.code);}process.exit(0);},700);`;
    const spawn=(body:string,pipe=false)=>`require('node:child_process').spawn(process.execPath,['-e',${JSON.stringify(body)}],{detached:true,stdio:${pipe?"['ignore','inherit','inherit']":"'ignore'"}}).unref();`;
    const events=[{type:'turn.started'},{type:'turn.completed',usage:{input_tokens:10,output_tokens:2}}].map(x=>JSON.stringify(x)).join('\n');
    let code=`console.log(${JSON.stringify(events)});`;
    if(name==='timeout')code+='setInterval(()=>{},1000);';
    if(['normal-child','detached','open-handle'].includes(name))code+=spawn(writer)+(name==='normal-child'?`const fs=require('node:fs');setInterval(()=>{if(fs.existsSync(${JSON.stringify(late)}))process.exit(0);},10);`:'setInterval(()=>{},1000);');
    if(name==='grandchild')code+=spawn(spawn(writer))+'setInterval(()=>{},1000);';
    if(name==='inherited-pipe')code+=spawn('setTimeout(()=>process.exit(0),1600);',true)+'setInterval(()=>{},1000);';
    if(name==='truncated')code+='process.stdout.write("x".repeat(5*1024*1024));';
    if(name==='interrupted'||name==='kill-error')code+='setTimeout(()=>process.exit(0),900);';
    let fixtureStart=performance.now();let kill=process.kill;const controller=new AbortController();let interrupt:NodeJS.Timeout|undefined;
    try {
        const warmup=await runTool(codex,l,[node,'-e','console.log("ready")'],5000);
        if(warmup.code!==0||warmup.stdout.trim()!=='ready')throw Error('Fixed Node warmup failed');
        fixtureStart=performance.now();
        if(name==='interrupted')interrupt=setTimeout(()=>controller.abort(),100);
        if(name==='kill-error')process.kill=(()=>{throw Object.assign(Error('injected'),{code:'EPERM'});}) as typeof process.kill;
        const result=await runTool(name==='spawn-error'?path.join(root,'absent-codex'):codex,l,[node,'-e',code],350,controller.signal);
        process.kill=kill;
        // All descendant fixtures self-exit by 1.6 s. Waiting is cleanup of this diagnostic, never a production receipt.
        await wait(1800);
        const lateText=fs.existsSync(late)?fs.readFileSync(late,'utf8'):null;
        const crossResult=fs.existsSync(cross)?fs.readFileSync(cross,'utf8'):null;
        const evidence=path.join(root,'diagnostic');const captured=collectDiagnostic(result,l,evidence,baseline);
        let productionRejected=false,receiptMismatch=false;
        try{snapshot(result,true);}catch{productionRejected=true;}
        try{collectDiagnostic({...result},l,path.join(root,'forged'),baseline);}catch{receiptMismatch=true;}
        let evaluationRejected=false;try{checkedSnapshot(evidence);}catch{evaluationRejected=true;}
        checkedDiagnosticSnapshot(evidence);
        const evalLayout={...l,source:path.join(evidence,'source'),sourceReadOnly:true,readOnly:[...l.readOnly,evidence]};
        fs.writeFileSync(path.join(l.control,'config.toml'),configuration(evalLayout));
        const targets=['source/original.txt','auxiliary','manifest.json','manifest.sha256'];
        const permission=await runTool(codex,evalLayout,[node,'-e',`const fs=require('node:fs');const r={};for(const t of ${JSON.stringify(targets)}){try{const p=${JSON.stringify(evidence)}+'/'+t;if(t==='auxiliary')fs.writeFileSync(p+'/added','bad');else{fs.chmodSync(p,0o644);fs.writeFileSync(p,'bad');}r[t]='WRITE';}catch(e){r[t]=e.code;}}console.log(JSON.stringify(r));`],5000);
        const rights=JSON.parse(permission.stdout) as Record<string,string>;
        const usage=collectUsage(result.stdout.trim().split('\n'),usageEnd(result)).summary();
        rows.push({repeat,name,warmup:{code:warmup.code,wallTimeMs:warmup.wallTimeMs},run:{...result,stdout:undefined,stderr:result.stderr.split(root).join('<probe>')},rawUsage:name==='truncated'?null:result.stdout,usage,lateText,crossResult,nextCanary:fs.readFileSync(path.join(next,'canary'),'utf8'),diagnosticKind:captured.kind,productionRejected,evaluationRejected,receiptMismatch,readOnly: rights,finiteFixtureCleanup:'waited beyond self-exit timers; not termination certification'});
        fs.writeFileSync(out,JSON.stringify({status:'running',rows,failures},null,2)+'\n');
        console.log(JSON.stringify({repeat,name,lateText,reason:result.reason,wallTimeMs:result.wallTimeMs}));
        if(!productionRejected||!evaluationRejected||!receiptMismatch||Object.values(rights).some(x=>!['EPERM','EACCES'].includes(x)))throw Error('Collection/permission gate regression');
        if(result.wallTimeMs>1600)throw Error('Supervisor did not return within bounded tolerance');
        if(['normal-child','detached','grandchild','open-handle'].includes(name)&&lateText!=='late')throw Error('Original escape fixture did not reproduce; do not claim a fix');
        if(['timeout','inherited-pipe','truncated','interrupted','spawn-error'].includes(name)&&usage.complete)throw Error('False usage completion');
    } catch(e) {failures.push({repeat,name,error:String(e).split(root).join('<probe>')});} finally {process.kill=kill;if(interrupt)clearTimeout(interrupt);await wait(Math.max(0,2200-(performance.now()-fixtureStart)));fs.rmSync(root,{recursive:true,force:true});}
}
fs.writeFileSync(out,JSON.stringify({schema:'s2-runtime-v2-diagnostic',R11:'unresolved',productionCollection:'blocked',providerCalls:0,failures,rows},null,2)+'\n');
console.log(JSON.stringify({cases:rows.length,failures,R11:'unresolved',output:out}));

process.exitCode=failures.length?1:0;
