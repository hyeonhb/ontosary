import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { performance } from 'node:perf_hooks';
import { createHash, randomUUID } from 'node:crypto';
const sha=(b:Buffer|string)=>createHash('sha256').update(b).digest('hex');
export interface Layout { root:string; source:string; materials:string; auxiliary:string; scratch:string; home:string; control:string; readOnly:string[]; sourceReadOnly?:boolean; denied?:string[]; }
export function configuration(l:Layout) {
    const roots=new Map<string,string>([[':minimal','read'],['/System/Library/OpenSSL','read'],[l.source,l.sourceReadOnly?'read':'write'],[l.materials,'read'],[l.auxiliary,'write'],[l.scratch,'write'],[l.home,'write'],...l.readOnly.map(p=>[p,'read'] as [string,string])]);
    for(const p of l.denied??[])roots.set(p,'deny');
    return `model = "gpt-6-astra"\nmodel_reasoning_effort = "high"\napproval_policy = "never"\ndefault_permissions = "trial"\nweb_search = "disabled"\nproject_doc_max_bytes = 0\nallow_login_shell = false\n[features]\napps = false\nmulti_agent = false\nremote_plugin = false\nshell_snapshot = false\n[plugins._default]\nenabled = false\n[permissions.trial.filesystem]\n${[...roots].map(([p,a])=>JSON.stringify(p)+' = '+JSON.stringify(a)).join('\n')}\n[permissions.trial.network]\nenabled = false\n[shell_environment_policy]\ninherit = "none"\n`;
}
export function childEnvironment(l:Layout):NodeJS.ProcessEnv {
    return {PATH:'/usr/bin:/bin',HOME:l.home,TMPDIR:l.scratch,CODEX_HOME:l.control,LANG:'en_US.UTF-8'};
}
export interface RunResult {
    runId:string; code:number|null; signal:string|null;
    reason:'completed'|'timeout'|'spawn-error'|'interrupted';
    wallTimeMs:number; stdout:string; stderr:string; outputTruncated:boolean; normalEOF:boolean; readErrors:string[];
    lifecycle:{state:'blocked';collectionAllowed:false;boundary:'unverified-process-group';deadlineMs:number;stopRequestedMs:number;parentExitMs:number|null;returnedMs:number;cleanupMs:number;cleanupLimitMs:number;errors:string[]};
    binding:{source:string;auxiliary:string;configuration:string};
}
const receipts=new WeakMap<RunResult,{source:string;auxiliary:string;configuration:string;runId:string;binding:RunResult['binding'];lifecycle:RunResult['lifecycle']}>();
/** Diagnostic/calibration tools only. Parent completion never grants production collection rights. */
export async function runTool(codex:string,l:Layout,command:string[],timeoutMs=1800000,abort?:AbortSignal):Promise<RunResult> {
    if(process.platform!=='darwin')throw Error('macOS runtime unavailable');
    if(!Number.isFinite(timeoutMs)||timeoutMs<=0||timeoutMs>1800000)throw Error('Invalid time budget');
    const config=configuration(l);
    if(fs.readFileSync(path.join(l.control,'config.toml'),'utf8')!==config)throw Error('Runtime configuration changed');
    const start=performance.now(),runId=randomUUID(),roots={source:fs.realpathSync(l.source),auxiliary:fs.realpathSync(l.auxiliary),configuration:sha(config)};
    const binding={source:sha(roots.source),auxiliary:sha(roots.auxiliary),configuration:roots.configuration};
    return new Promise(resolve=>{
        const child=spawn(codex,['sandbox','-P','trial','-C',l.source,'--',...command],{cwd:l.source,env:childEnvironment(l),detached:true,stdio:['ignore','pipe','pipe']});
        const buffers:{stdout:Buffer[];stderr:Buffer[]}={stdout:[],stderr:[]};
        let bytes=0,truncated=false,closed=false,settled=false,code:number|null=null,signal:string|null=null,parentExitMs:number|null=null;
        let reason:RunResult['reason']='completed',stopRequestedMs:number|null=null,cleanup:NodeJS.Timeout|undefined;
        const errors:string[]=[],readErrors:string[]=[],cleanupLimitMs=250;
        const elapsed=()=>performance.now()-start;
        const append=(key:'stdout'|'stderr',b:Buffer)=>{const n=Math.min(b.length,Math.max(0,4*1024*1024-bytes));if(n<b.length)truncated=true;if(n){buffers[key].push(b.subarray(0,n));bytes+=n;}};
        child.stdout.on('data',(b:Buffer)=>append('stdout',b));child.stderr.on('data',(b:Buffer)=>append('stderr',b));
        for(const stream of [child.stdout,child.stderr])stream.on('error',(e:NodeJS.ErrnoException)=>{if(readErrors.length<32)readErrors.push(e.code??'pipe-error');});
        const interrupt=()=>stop('interrupted');
        const finish=()=>{
            if(settled)return;settled=true;clearTimeout(deadline);if(cleanup)clearTimeout(cleanup);
            process.removeListener('SIGINT',interrupt);process.removeListener('SIGTERM',interrupt);abort?.removeEventListener('abort',interrupt);
            if(!closed){readErrors.push('pipe-close-deadline');child.stdout.destroy();child.stderr.destroy();child.unref();}
            const returnedMs=elapsed();
            const result:RunResult={runId,code,signal,reason,wallTimeMs:returnedMs,stdout:Buffer.concat(buffers.stdout).toString('utf8'),stderr:Buffer.concat(buffers.stderr).toString('utf8'),outputTruncated:truncated,normalEOF:closed,readErrors,
                lifecycle:{state:'blocked',collectionAllowed:false,boundary:'unverified-process-group',deadlineMs:timeoutMs,stopRequestedMs:stopRequestedMs??returnedMs,parentExitMs,returnedMs,cleanupMs:returnedMs-(stopRequestedMs??returnedMs),cleanupLimitMs,errors},binding};
            receipts.set(result,{...roots,runId,binding:{...binding},lifecycle:structuredClone(result.lifecycle)});resolve(result);
        };
        const stop=(why:RunResult['reason'])=>{
            if(stopRequestedMs!==null)return;reason=why;stopRequestedMs=elapsed();clearTimeout(deadline);
            // Only this spawned process group; no process-name scans or unrelated PID sweeps.
            if(child.pid)try{process.kill(-child.pid,'SIGKILL');}catch(e){const c=(e as NodeJS.ErrnoException).code;if(c!=='ESRCH')errors.push(c??'kill-error');}
            cleanup=setTimeout(finish,cleanupLimitMs);if(closed)finish();
        };
        const deadline=setTimeout(()=>stop('timeout'),timeoutMs);
        child.on('error',(e:NodeJS.ErrnoException)=>{errors.push(e.code??'spawn-error');stop('spawn-error');});
        child.on('exit',(c,s)=>{code=c;signal=s;parentExitMs=elapsed();stop('completed');});
        child.on('close',(c,s)=>{code=c;signal=s;closed=true;stop('completed');finish();});
        process.once('SIGINT',interrupt);process.once('SIGTERM',interrupt);abort?.addEventListener('abort',interrupt,{once:true});
        if(abort?.aborted)interrupt();
    });
}
/** No implementation can issue a sealed submission until an OS boundary is established. */
export function snapshot(..._args:unknown[]):never {throw Error('R11 unresolved: production collection blocked; diagnostic evidence is not a submission');}
export function collectDiagnostic(result:RunResult,l:Layout,out:string,baseline:Record<string,string>) {
    const receipt=receipts.get(result);
    if(!receipt||receipt.source!==fs.realpathSync(l.source)||receipt.auxiliary!==fs.realpathSync(l.auxiliary)||receipt.configuration!==sha(configuration(l)))throw Error('Run/path receipt mismatch');
    return captureDiagnostic(l.source,l.auxiliary,out,baseline,{runId:receipt.runId,binding:receipt.binding,lifecycle:receipt.lifecycle});
}
/** Explicit fixture capture, never an agent submission; evaluation must independently allowlist the fixture. */
export function calibrationSnapshot(source:string,auxiliary:string,out:string,baseline:Record<string,string>) {
    return captureDiagnostic(source,auxiliary,out,baseline,{fixture:true,termination:'not-certified'});
}
export function tree(root:string):Record<string,string> {
    const result:Record<string,string>={};
    const walk=(dir:string)=>{for(const e of fs.readdirSync(path.join(root,dir),{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name))) {
        const f=path.posix.join(dir,e.name),full=path.join(root,f);
        if(e.isSymbolicLink()||!e.isFile()&&!e.isDirectory())throw Error('Nonregular snapshot file: '+f);
        if(e.isDirectory())walk(f);else result[f]=sha(fs.readFileSync(full));
    }};walk('');return result;
}
/** Preserve diagnostic evidence atomically without promoting it to sealed. */
function captureDiagnostic(source:string,auxiliary:string,out:string,baseline:Record<string,string>,origin:unknown) {
    if(fs.existsSync(out))throw Error('Snapshot already exists');
    const before=tree(source),aux=tree(auxiliary),stage=fs.mkdtempSync(path.join(path.dirname(out),'.snapshot-'));
    try {
        fs.cpSync(source,path.join(stage,'source'),{recursive:true});fs.cpSync(auxiliary,path.join(stage,'auxiliary'),{recursive:true});
        if(JSON.stringify(tree(source))!==JSON.stringify(before)||JSON.stringify(tree(path.join(stage,'source')))!==JSON.stringify(before)||JSON.stringify(tree(auxiliary))!==JSON.stringify(aux)||JSON.stringify(tree(path.join(stage,'auxiliary')))!==JSON.stringify(aux))throw Error('Source changed during snapshot');
        const delta=Array.from(new Set([...Object.keys(baseline),...Object.keys(before)])).sort().filter(f=>baseline[f]!==before[f]).map(file=>({file,kind:!before[file]?'deleted':!baseline[file]?'added':'modified',before:baseline[file]??null,after:before[file]??null}));
        const record={version:2,kind:'diagnostic',validSubmission:false,origin,source:before,auxiliary:aux,delta,sourceId:sha(JSON.stringify(before)),readOnlyEnforcement:'evaluate only under a profile granting read, never chmod alone'};
        const text=JSON.stringify(record,null,2)+'\n';
        fs.writeFileSync(path.join(stage,'manifest.json'),text);fs.writeFileSync(path.join(stage,'manifest.sha256'),sha(text)+'\n');
        for(const [folder,entries] of [['source',before],['auxiliary',aux]] as const)for(const f of Object.keys(entries))fs.chmodSync(path.join(stage,folder,f),0o444);
        fs.chmodSync(path.join(stage,'manifest.json'),0o444);fs.chmodSync(path.join(stage,'manifest.sha256'),0o444);
        fs.renameSync(stage,out);return record;
    }catch(e){fs.rmSync(stage,{recursive:true,force:true});throw e;}
}
