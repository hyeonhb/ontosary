import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { performance } from 'node:perf_hooks';
import { fileURLToPath } from 'node:url';
import { gunzipSync, gzipSync } from 'node:zlib';
import { hash } from '../lib/analysis-session.js';
import { tree } from './runtime.js';
/** Copy public source and pinned installed dependencies; never grant tools access to the original cache. */
export function stageEnvironment(cache:string,repo:string,out:string) {
    if(fs.existsSync(out))throw Error('Environment output exists');
    const start=performance.now();fs.mkdirSync(out,{recursive:true});
    const entries=JSON.parse(gunzipSync(fs.readFileSync(path.join(repo,'experiments/public-app/results/2026-11-08/vendure/inventory.json.gz'))).toString()) as {path:string;sha256:string}[];
    const manifest:Record<string,string>={};
    for(const e of entries) {
        const input=path.join(cache,e.path),b=fs.readFileSync(input);
        if(!fs.lstatSync(input).isFile()||hash(b)!==e.sha256)throw Error('Baseline mismatch: '+e.path);
        const dest=path.join(out,'environment',e.path);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,b);manifest[e.path]=e.sha256;
    }
    for(const rel of ['node_modules','packages/admin-ui/node_modules','packages/common/lib']) {
        const dest=path.join(out,'environment',rel);fs.mkdirSync(path.dirname(dest),{recursive:true});
        execFileSync('/bin/cp',['-cR',path.join(cache,rel),dest]);
    }
    const scope='packages/admin-ui/ontosary.scope.json';fs.copyFileSync(path.join(cache,scope),path.join(out,'environment',scope));
    // All dependency symlinks must resolve inside this copy; no source-cache capability leaks.
    const root=fs.realpathSync(path.join(out,'environment'));
    function inspect(dir:string) {for(const e of fs.readdirSync(dir,{withFileTypes:true})) {const f=path.join(dir,e.name);if(e.isSymbolicLink()){const target=fs.realpathSync(f);if(!target.startsWith(root+path.sep))throw Error('External dependency symlink: '+path.relative(root,f));}else if(e.isDirectory())inspect(f);}}
    inspect(root);
    const tools=path.join(out,'tools');fs.mkdirSync(path.join(tools,'node_modules'),{recursive:true});
    const require=createRequire(import.meta.url),tsRoot=path.dirname(require.resolve('typescript/package.json'));
    execFileSync('/bin/cp',['-cR',tsRoot,path.join(tools,'node_modules/typescript')]);
    fs.copyFileSync(fileURLToPath(new URL('./public-check.js',import.meta.url)),path.join(tools,'public-check.js'));
    fs.writeFileSync(path.join(tools,'package.json'),'{"type":"module"}\n');
    fs.writeFileSync(path.join(tools,'baseline-manifest.json'),JSON.stringify(manifest));
    fs.copyFileSync(fs.realpathSync(process.execPath),path.join(tools,'node'));fs.chmodSync(path.join(tools,'node'),0o555);
    const script=`#!/bin/sh\nexec ${quote(path.join(tools,'node'))} ${quote(path.join(tools,'public-check.js'))} "$PWD" ${quote(root)} ${quote(path.join(tools,'baseline-manifest.json'))}\n`;
    fs.writeFileSync(path.join(tools,'public-check'),script,{mode:0o555});
    const dependencyManifest:Record<string,unknown>={};
    const fingerprint=(dir:string)=>{for(const e of fs.readdirSync(dir,{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name))){const f=path.join(dir,e.name),relative=path.relative(root,f);if(e.isSymbolicLink())dependencyManifest[relative]={symlink:fs.readlinkSync(f)};else if(e.isDirectory())fingerprint(f);else {const b=fs.readFileSync(f);if(hash(b)!==hash(fs.readFileSync(path.join(cache,relative))))throw Error('Dependency copy differs: '+relative);dependencyManifest[relative]={sha256:hash(b),bytes:b.length};}}};
    for(const rel of ['node_modules','packages/admin-ui/node_modules','packages/common/lib'])fingerprint(path.join(root,rel));
    const dependencyText=JSON.stringify(dependencyManifest);fs.writeFileSync(path.join(out,'dependencies.json.gz'),gzipSync(dependencyText));
    const report={dependencyManifestHash:hash(dependencyText),dependencyFiles:Object.keys(dependencyManifest).length,node:process.version,platform:process.platform,arch:process.arch,sourceFiles:entries.length,sourceManifest:manifest,toolManifest:tree(tools),preparationMs:performance.now()-start,dependencies:'APFS clone of installed cache; no install or rebuild; symlinks checked within copied environment',privateEvaluatorFiles:0};
    fs.writeFileSync(path.join(out,'environment-manifest.json'),JSON.stringify(report,null,2)+'\n');return report;
}
function quote(s:string){return "'"+s.replaceAll("'","'\\''")+"'";}
if(process.argv[1]?.endsWith('/environment.js')) {
    const [cache,out,repo=process.cwd()]=process.argv.slice(2);if(!cache||!out)throw Error('Usage: environment <cache> <new-output> [repo]');
    const r=stageEnvironment(path.resolve(cache),path.resolve(repo),path.resolve(out));console.log(JSON.stringify({sourceFiles:r.sourceFiles,preparationMs:r.preparationMs}));
}
