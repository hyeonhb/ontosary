import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { performance } from 'node:perf_hooks';
import { createHash } from 'node:crypto';
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
export interface RunResult {code:number|null;signal:string|null;reason:'completed'|'timeout';wallTimeMs:number;stdout:string;stderr:string;outputTruncated:boolean;}
/** No model dispatch. Same named Codex permission profile used for deterministic tools and evaluator. */
export async function runTool(codex:string,l:Layout,command:string[],timeoutMs=1800000):Promise<RunResult> {
    if(process.platform!=='darwin')throw Error('macOS runtime unavailable');
    if(!Number.isFinite(timeoutMs)||timeoutMs<=0||timeoutMs>1800000)throw Error('Invalid time budget');
    if(fs.readFileSync(path.join(l.control,'config.toml'),'utf8')!==configuration(l))throw Error('Runtime configuration changed');
    const start=performance.now();
    return new Promise((resolve,reject)=>{
        const child=spawn(codex,['sandbox','-P','trial','-C',l.source,'--',...command],{cwd:l.source,env:childEnvironment(l),detached:true,stdio:['ignore','pipe','pipe']});
        let stdout='',stderr='',timed=false,truncated=false;
        const add=(old:string,b:Buffer)=>{if(old.length+b.length>4*1024*1024){truncated=true;return old;}return old+b.toString();};
        child.stdout.on('data',b=>stdout=add(stdout,b));child.stderr.on('data',b=>stderr=add(stderr,b));
        const kill=()=>{try{process.kill(-child.pid!,'SIGKILL');}catch(e){if((e as NodeJS.ErrnoException).code!=='ESRCH')throw e;}};
        const timer=setTimeout(()=>{timed=true;kill();},timeoutMs);
        child.on('error',e=>{clearTimeout(timer);reject(e);});
        child.on('close',(code,signal)=>{clearTimeout(timer);kill();resolve({code,signal,reason:timed?'timeout':'completed',wallTimeMs:performance.now()-start,stdout,stderr,outputTruncated:truncated});});
    });
}
export function tree(root:string):Record<string,string> {
    const result:Record<string,string>={};
    const walk=(dir:string)=>{for(const e of fs.readdirSync(path.join(root,dir),{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name))) {
        const f=path.posix.join(dir,e.name),full=path.join(root,f);
        if(e.isSymbolicLink()||!e.isFile()&&!e.isDirectory())throw Error('Nonregular snapshot file: '+f);
        if(e.isDirectory())walk(f);else result[f]=sha(fs.readFileSync(full));
    }};walk('');return result;
}
/** Call only after supervisor shutdown. Captures every production and auxiliary file; never restores baseline. */
export function snapshot(source:string,auxiliary:string,out:string,baseline:Record<string,string>) {
    if(fs.existsSync(out))throw Error('Snapshot already exists');
    const before=tree(source),aux=tree(auxiliary),stage=fs.mkdtempSync(path.join(path.dirname(out),'.snapshot-'));
    try {
        fs.cpSync(source,path.join(stage,'source'),{recursive:true});fs.cpSync(auxiliary,path.join(stage,'auxiliary'),{recursive:true});
        if(JSON.stringify(tree(source))!==JSON.stringify(before)||JSON.stringify(tree(path.join(stage,'source')))!==JSON.stringify(before)||JSON.stringify(tree(auxiliary))!==JSON.stringify(aux)||JSON.stringify(tree(path.join(stage,'auxiliary')))!==JSON.stringify(aux))throw Error('Source changed during snapshot');
        const delta=Array.from(new Set([...Object.keys(baseline),...Object.keys(before)])).sort().filter(f=>baseline[f]!==before[f]).map(file=>({file,kind:!before[file]?'deleted':!baseline[file]?'added':'modified',before:baseline[file]??null,after:before[file]??null}));
        const record={version:1,source:before,auxiliary:aux,delta,sourceId:sha(JSON.stringify(before)),readOnlyEnforcement:'evaluate only under a profile granting read, never chmod alone'};
        fs.writeFileSync(path.join(stage,'manifest.json'),JSON.stringify(record,null,2)+'\n');
        for(const f of Object.keys(before))fs.chmodSync(path.join(stage,'source',f),0o444);
        fs.renameSync(stage,out);return record;
    }catch(e){fs.rmSync(stage,{recursive:true,force:true});throw e;}
}
