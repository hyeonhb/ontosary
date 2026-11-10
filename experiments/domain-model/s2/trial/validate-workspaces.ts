import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { configuration, runTool, Layout, tree } from './runtime.js';
import { hash } from '../lib/analysis-session.js';
const [codex,bundleArg,cacheArg,environmentArg,outArg,repoArg=process.cwd()]=process.argv.slice(2);
if(!codex||!bundleArg||!cacheArg||!environmentArg||!outArg)throw Error('Usage: validate-workspaces <codex> <bundle> <cache> <environment> <new-evidence> [repo]');
const bundle=path.resolve(bundleArg),cache=path.resolve(cacheArg),environment=path.resolve(environmentArg),repo=path.resolve(repoArg),out=path.resolve(outArg);
if(fs.existsSync(out))throw Error('Output exists');
const root=fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(),'s2-workspaces-'))),rows:unknown[]=[];
const locations:Record<string,string>={A:'run-01',B:'run-02',C:'run-03'};
try {
    for(const c of ['A','B','C'])execFileSync(process.execPath,[fileURLToPath(new URL('../workspace.js',import.meta.url)),bundle,cache,c,path.join(root,locations[c]!),repo,environment]);
    for(const c of ['A','B','C']) {
        const dir=path.join(root,locations[c]!),l:Layout={root:dir,source:path.join(dir,'source'),materials:path.join(dir,'materials'),auxiliary:path.join(dir,'auxiliary'),scratch:path.join(dir,'scratch'),home:path.join(dir,'home'),control:path.join(root,'control-'+locations[c]),readOnly:[path.join(environment,'environment'),path.join(environment,'tools')],denied:[fs.realpathSync(cache),repo,'/Users']};
        for(const p of [l.auxiliary,l.scratch,l.home,l.control])fs.mkdirSync(p);fs.writeFileSync(path.join(l.control,'config.toml'),configuration(l));
        const materials=tree(l.materials),source=tree(l.source),other=path.join(root,locations[c==='A'?'B':'A']!,'materials/TASK.txt');
        const code=`const fs=require('node:fs');let denied={};for(const [k,p] of Object.entries(${JSON.stringify({other,repository:path.join(repo,'AGENTS.md'),cache:path.join(cache,'package.json')})})){try{fs.readFileSync(p);denied[k]='READ';}catch(e){denied[k]=e.code;}}let readonly;try{fs.appendFileSync(${JSON.stringify(path.join(l.materials,'TASK.txt'))},'bad');readonly='WRITE';}catch(e){readonly=e.code;}console.log(JSON.stringify({denied,readonly,task:fs.readFileSync(${JSON.stringify(path.join(l.materials,'TASK.txt'))},'utf8').length}));`;
        const access=await runTool(codex,l,[path.join(environment,'tools/node'),'-e',code],5000);
        const check=await runTool(codex,l,[path.join(dir,'tools/public-check')],30000);
        rows.push({condition:c,materials,sourceFiles:Object.keys(source).length,sourceId:hash(JSON.stringify(source)),taskHash:materials['TASK.txt'],guideHash:materials['RUN.md'],access:JSON.parse(access.stdout),publicCheck:JSON.parse(check.stdout),materialsUnchanged:JSON.stringify(materials)===JSON.stringify(tree(l.materials)),sourceUnchanged:JSON.stringify(source)===JSON.stringify(tree(l.source)),sameProfile:'generated trial profile, same UID as Codex shell',noEvaluatorFiles:Object.keys(materials).every(f=>!f.startsWith('evaluator/'))});
    }
    fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify({workspaces:rows,osIsolation:'filesystem/network probes only; process termination blocker remains',readyForTrial:false},null,2)+'\n');console.log(JSON.stringify({workspaces:rows.length,output:out}));
}finally{fs.rmSync(root,{recursive:true,force:true});}
