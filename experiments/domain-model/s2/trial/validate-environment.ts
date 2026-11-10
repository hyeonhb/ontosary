import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { configuration, runTool, Layout, tree } from './runtime.js';
import { variantDelta } from '../evaluation/variants.js';
import { deltaSubmission } from '../evaluation/submission.js';
export async function validateEnvironment(codex:string,environmentDir:string,repo:string,out:string) {
    if(fs.existsSync(out))throw Error('Output exists');
    const env=path.join(environmentDir,'environment'),tools=path.join(environmentDir,'tools');
    const manifest=JSON.parse(fs.readFileSync(path.join(environmentDir,'environment-manifest.json'),'utf8')).sourceManifest as Record<string,string>;
    const baseline=new Map(Object.keys(manifest).map(f=>[f,fs.readFileSync(path.join(env,f))]));
    const root=fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(),'s2-public-')));
    const l:Layout={root,source:path.join(root,'source'),materials:path.join(root,'materials'),auxiliary:path.join(root,'auxiliary'),scratch:path.join(root,'scratch'),home:path.join(root,'home'),control:path.join(root,'control'),readOnly:[env,tools],denied:[repo,'/Users']};
    for(const p of [l.materials,l.auxiliary,l.scratch,l.home,l.control])fs.mkdirSync(p,{recursive:true});fs.writeFileSync(path.join(l.control,'config.toml'),configuration(l));
    const reports:unknown[]=[];
    try {
        for(const name of ['baseline','reference','helper','helper-type-error','helper-syntax-error','missing-helper','deleted-module']) {
            fs.rmSync(l.source,{recursive:true,force:true});fs.mkdirSync(l.source);
            const sources=deltaSubmission(baseline,variantDelta(name,baseline,repo));
            for(const [f,b] of sources){const dest=path.join(l.source,f);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,b);}
            const r=await runTool(codex,l,[path.join(tools,'public-check')],30000);
            const result=r.stdout.trim()?JSON.parse(r.stdout):{status:'environment-error',stderr:r.stderr};
            reports.push({name,result,exit:r.code,wallTimeMs:r.wallTimeMs,sourceManifest:tree(l.source)});
        }
        fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify({reports,boundary:'public checker only; no private oracle files readable',platform:process.platform,node:process.version},null,2)+'\n');return reports;
    }finally{fs.rmSync(root,{recursive:true,force:true});}
}
if(process.argv[1]?.endsWith('/validate-environment.js')) {
    const [codex,environment,out,repo=process.cwd()]=process.argv.slice(2);if(!codex||!environment||!out)throw Error('Usage: validate-environment <codex> <environment-dir> <new-report> [repo]');
    const rows=await validateEnvironment(codex,path.resolve(environment),path.resolve(repo),out);console.log(JSON.stringify({cases:rows.length,output:out}));
}
