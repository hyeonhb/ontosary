import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import net from 'node:net';
import { configuration, runTool, Layout, tree, collectDiagnostic } from './runtime.js';
import { collectUsage, usageEnd } from './telemetry.js';
export async function probe(codex:string,out:string) {
    if(fs.existsSync(out))throw Error('Output exists');
    const root=fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(),'s2-probe-')));
    const agent=path.join(root,'agent'),control=path.join(root,'control'),outside=path.join(root,'outside');
    const bin=path.join(root,'bin');fs.mkdirSync(bin);const node=path.join(bin,'node');fs.copyFileSync(fs.realpathSync(process.execPath),node);fs.chmodSync(node,0o555);
    const l:Layout={root:agent,source:path.join(agent,'source'),materials:path.join(agent,'materials'),auxiliary:path.join(agent,'auxiliary'),scratch:path.join(agent,'scratch'),home:path.join(agent,'home'),control,readOnly:[bin],denied:[outside,control,'/Users']};
    for(const p of [l.source,l.materials,l.auxiliary,l.scratch,l.home,control,outside])fs.mkdirSync(p,{recursive:true});
    fs.writeFileSync(path.join(control,'config.toml'),configuration(l));
    const source=path.join(l.source,'allowed.txt'),material=path.join(l.materials,'read-only.txt'),canary=path.join(outside,'existing-canary.txt');
    fs.writeFileSync(source,'original');fs.writeFileSync(material,'material');fs.writeFileSync(canary,'NONSECRET-CANARY');fs.writeFileSync(path.join(outside,'package.json'),'{"nonsecretCanary":true}');
    const original=tree(l.source);
    fs.symlinkSync(canary,path.join(l.source,'escape'));
    const socket=path.join(outside,'host.sock'),server=net.createServer(s=>s.end());
    await new Promise<void>(resolve=>server.listen(socket,resolve));
    const code=`const fs=require('node:fs'),net=require('node:net');
const errors={};
for(const [name,file] of Object.entries(${JSON.stringify({outside:canary,packageException:path.join(outside,'package.json'),parent:path.join(l.source,'../../outside/existing-canary.txt'),symlink:path.join(l.source,'escape'),control:path.join(control,'config.toml')})})) {try{fs.readFileSync(file);errors[name]='READ';}catch(e){errors[name]=e.code;}}
let write='';try{fs.writeFileSync(${JSON.stringify(material)},'bad');write='WRITE';}catch(e){write=e.code;}
fs.appendFileSync(${JSON.stringify(source)},'-edited');
const tests=[['external',{host:'1.1.1.1',port:443}],['socket',{path:${JSON.stringify(socket)}}]];
Promise.all(tests.map(([name,target])=>new Promise(resolve=>{const s=net.connect(target);s.once('error',e=>resolve([name,e.code]));s.once('connect',()=>{s.destroy();resolve([name,'CONNECTED']);});s.setTimeout(800,()=>{s.destroy();resolve([name,'TIMEOUT']);});}))).then(n=>console.log(JSON.stringify({errors,write,read:fs.readFileSync(${JSON.stringify(material)},'utf8'),source:fs.readFileSync(${JSON.stringify(source)},'utf8'),network:Object.fromEntries(n)})));`;
    try {
        const result=await runTool(codex,l,[node,'-e',code],5000);
        const observation=result.code===0?JSON.parse(result.stdout):null;
        const denied=(v:unknown)=>v==='EPERM'||v==='EACCES';
        const access=!!observation&&Object.values(observation.errors).every(denied)&&denied(observation.write)&&Object.values(observation.network).every(denied)&&observation.read==='material'&&observation.source==='original-edited';
        fs.unlinkSync(path.join(l.source,'escape'));
        const usageLines=[JSON.stringify({type:'turn.started'}),JSON.stringify({id:'u1',type:'turn.completed',usage:{input_tokens:99999,output_tokens:5,cached_input_tokens:90000,reasoning_output_tokens:2}})];
        const stub=await runTool(codex,l,[node,'-e',`console.log(${JSON.stringify(usageLines.join('\n'))})`],5000);
        const usage=collectUsage(stub.stdout.trim().split('\n'),usageEnd(stub)).summary();
        // A detached descendant tests a known gap of a process-group-only supervisor.
        const escape=path.join(l.scratch,'escaped.txt');
        const detachedCode=`require('node:child_process').spawn(process.execPath,['-e',${JSON.stringify(`setTimeout(()=>require('node:fs').writeFileSync(${JSON.stringify(escape)},'alive'),700)`)}],{detached:true,stdio:'ignore'}).unref();setInterval(()=>{},1000);`;
        const timed=await runTool(codex,l,[node,'-e',detachedCode],350);
        await new Promise(resolve=>setTimeout(resolve,900));
        const daemonContained=timed.reason==='timeout'&&!fs.existsSync(escape);
        fs.writeFileSync(path.join(l.source,'added.ts'),'export const value=1;');fs.writeFileSync(path.join(l.auxiliary,'notes.txt'),'fixture notes');
        const frozen=collectDiagnostic(timed,l,path.join(root,'final'),original);
        const finalLayout={...l,source:path.join(root,'final/source'),sourceReadOnly:true,readOnly:[...l.readOnly,path.join(root,'final')]};
        // Evaluate snapshots with read-only rights; do not reuse writable source permissions.
        const finalConfig=configuration(finalLayout).replace(JSON.stringify(finalLayout.source)+' = "write"',JSON.stringify(finalLayout.source)+' = "read"');
        fs.writeFileSync(path.join(control,'config.toml'),configuration(finalLayout));
        const sealed=await runTool(codex,finalLayout,[node,'-e',`try{require('node:fs').chmodSync(${JSON.stringify(path.join(root,'final/source/allowed.txt'))},0o644);require('node:fs').writeFileSync(${JSON.stringify(path.join(root,'final/source/allowed.txt'))},'bad');console.log('WRITE');}catch(e){console.log(e.code);}`],5000);
        const record={snapshotWriteDenied:sealed.stdout.trim()==='EPERM'||sealed.stdout.trim()==='EACCES',version:1,platform:process.platform,arch:process.arch,node:process.version,uid:process.getuid?.(),sameToolBoundary:'codex sandbox with generated trial profile; no model call',accessVerified:access,observation,probeExit:result.code,probeError:result.stderr.split(root).join('<probe>'),usageFixture:usage,usageRaw:stub.stdout,usageCoverage:'Deterministic stub events only; no provider requests',timeout:{reason:timed.reason,limitMs:350,wallTimeMs:timed.wallTimeMs,detachedDescendantContained:daemonContained},diagnosticSnapshot:frozen,collectionAllowed:false,readOnlySnapshotProfile:finalConfig.split(root).join('<probe>'),readyForTrial:false,blockers:[...(!access?['filesystem/network probe failed']:[]),...(!daemonContained?['Detached descendants escape process-group shutdown; immutable final collection not guaranteed for hostile processes']:[]),'Live CLI tool inventory, credential separation and inherited instruction exclusion not exercised without a model session'],measurement:'Probe/script stub only; no provider usage, no agent task',results:null};
        fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(record,null,2).split(root).join('<probe>').split(fs.realpathSync(process.execPath)).join('<node>')+'\n');
        return record;
    } finally {server.close();fs.rmSync(root,{recursive:true,force:true});}
}
if(process.argv[1]?.endsWith('/probe.js')) {
    const [codex,out]=process.argv.slice(2);if(!codex||!out)throw Error('Usage: probe <codex-binary> <new-evidence.json>');
    const r=await probe(codex,out);console.log(JSON.stringify({accessVerified:r.accessVerified,blockers:r.blockers,output:out}));
}
