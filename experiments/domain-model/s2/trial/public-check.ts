import fs from 'node:fs';
import path from 'node:path';
import ts from 'typescript';
/** Standalone public type gate. No oracle, expected payloads, variants or private file lists. */
export function publicCheck(source:string, environment:string, baselineManifest:Record<string,string>, config='packages/admin-ui/ontosary.scope.json') {
    source=path.resolve(source);environment=path.resolve(environment);
    const rel=(f:string)=>path.relative(environment,path.resolve(f)).split(path.sep).join('/');
    const names=new Set<string>();
    const walk=(d:string)=>{for(const e of fs.readdirSync(path.join(source,d),{withFileTypes:true})) {if(['.git','node_modules'].includes(e.name))continue;const f=path.posix.join(d,e.name);if(e.isSymbolicLink()||!e.isFile()&&!e.isDirectory())throw Error('Nonregular production file: '+f);if(e.isDirectory())walk(f);else names.add(f);}};walk('');
    const read=(f:string)=>{const r=rel(f);if(!r.startsWith('../')&&(names.has(r)||Object.hasOwn(baselineManifest,r))&&!r.endsWith('.json'))return names.has(r)?fs.readFileSync(path.join(source,r),'utf8'):undefined;return ts.sys.readFile(f);};
    const exists=(f:string)=>{const r=rel(f);return names.has(r)||Object.hasOwn(baselineManifest,r)?names.has(r):ts.sys.fileExists(f);};
    const raw=ts.readConfigFile(path.join(environment,config),read);
    const parsed=ts.parseJsonConfigFileContent(raw.config??{}, {...ts.sys,readFile:read,fileExists:exists},path.dirname(path.join(environment,config)),{noEmit:true});
    if((!parsed.options.strict&&!parsed.options.strictNullChecks)||parsed.options.strictNullChecks===false)throw Error('Strict scope required');
    const host=ts.createCompilerHost(parsed.options);host.readFile=read;host.fileExists=exists;
    const oldDir=host.directoryExists?.bind(host);host.directoryExists=d=>fs.existsSync(path.join(source,rel(d)))||oldDir?.(d)===true;
    const program=ts.createProgram({rootNames:parsed.fileNames,options:parsed.options,projectReferences:parsed.projectReferences,host});
    const diagnostics=[...(raw.error?[raw.error]:[]),...parsed.errors,...ts.getPreEmitDiagnostics(program)].map(d=>({code:d.code,file:d.file?rel(d.file.fileName):null,line:d.file&&d.start!==undefined?d.file.getLineAndCharacterOfPosition(d.start).line+1:null,message:ts.flattenDiagnosticMessageText(d.messageText,'\n').split(environment).join('<environment>')}));
    return {status:diagnostics.length?'failed':'passed',diagnostics,typescript:ts.version,programFiles:program.getSourceFiles().length,scope:'Type diagnostics only. Private change/syntax/behavior gates remain separate.'};
}
if(process.argv[1]?.endsWith('/public-check.js')) {
    const [source,environment,manifest,config]=process.argv.slice(2);
    if(!source||!environment||!manifest)throw Error('Usage: public-check <source> <environment> <baseline-manifest> [config]');
    const result=publicCheck(source,environment,JSON.parse(fs.readFileSync(manifest,'utf8')),config);
    console.log(JSON.stringify(result));process.exitCode=result.status==='passed'?0:1;
}
