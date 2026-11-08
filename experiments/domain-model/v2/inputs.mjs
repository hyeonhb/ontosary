import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { gunzipSync } from 'node:zlib';
import ts from 'typescript';
import { sha } from '../v1/observe.mjs';
const here = fileURLToPath(new URL('../v1/',import.meta.url));
const repo = path.resolve(here,'../../..');
export function checkAnalysisInputs(rootArg) {
 try {
 const root=fs.realpathSync(rootArg);
 const manifest=JSON.parse(fs.readFileSync(path.join(here,'manifest.json'),'utf8'));
const verifyHash = (file, hash) => { if (sha(fs.readFileSync(file)) !== hash) throw new Error(`Changed input: ${path.relative(root,file)}`); };
for (const [f,h] of Object.entries(manifest.inputHashes)) verifyHash(path.join(root,f),h);
for (const [f,h] of Object.entries(manifest.repositoryInputs)) verifyHash(path.join(here,f),h);
const inventory = JSON.parse(gunzipSync(fs.readFileSync(path.join(repo,'experiments/public-app/results/2026-11-08/vendure/inventory.json.gz'))));
for (const e of inventory) {
  if (e.symlink) { if (fs.readlinkSync(path.join(root,e.path)) !== e.symlink) throw new Error('Changed source symlink'); }
  else verifyHash(path.join(root,e.path),e.sha256);
}
const priorProgram = JSON.parse(gunzipSync(fs.readFileSync(path.join(repo,'experiments/public-app/results/2026-11-08-prepared/program-path-audit.json.gz')))).observations.scoped.files;
const lib = path.dirname(ts.getDefaultLibFilePath({}));
for (const f of priorProgram) verifyHash(f.path.startsWith('<typescript-lib>/') ? path.join(lib,f.path.slice('<typescript-lib>/'.length)) : path.join(root,f.path),f.sha256);
const config = path.join(root,manifest.config), loaded = ts.readConfigFile(config,ts.sys.readFile);
if (loaded.error) throw new Error('Cannot read preserved config');
const parsed = ts.parseJsonConfigFileContent(loaded.config,ts.sys,path.dirname(config),{noEmit:true},config);
const program = ts.createProgram({rootNames:parsed.fileNames,options:parsed.options,projectReferences:parsed.projectReferences});
const canonicalLib = fs.realpathSync(lib);
const currentProgram = program.getSourceFiles().map(sf => {
  const absolute = fs.realpathSync(sf.fileName);
  const file = absolute.startsWith(root + path.sep) ? path.relative(root,absolute) : absolute.startsWith(canonicalLib + path.sep) ? '<typescript-lib>/' + path.relative(canonicalLib,absolute) : null;
  if (!file) throw new Error('Unexpected dependency outside prepared cache / TypeScript lib');
  return {path:file,sha256:sha(fs.readFileSync(absolute))};
}).sort((a,b)=>a.path.localeCompare(b.path));
const expectedProgram = priorProgram.map(f=>({path:f.path,sha256:f.sha256})).sort((a,b)=>a.path.localeCompare(b.path));
if (JSON.stringify(currentProgram)!==JSON.stringify(expectedProgram)) throw new Error('Prepared Program membership changed');

const diagnostics = [...parsed.errors,...ts.getPreEmitDiagnostics(program)].map(d => ({code:d.code,category:ts.DiagnosticCategory[d.category],file:d.file ? path.relative(root,d.file.fileName) : null}));

if (diagnostics.length) throw new Error('Live compiler diagnostics present');
return { valid:true, status:'verified', originalEntries:inventory.length, programFiles:currentProgram.length, diagnostics };
} catch(e) { return {valid:false,status:'unverified-or-changed',reason:e.code === 'ENOENT' ? 'Required source/config/dependency input missing' : e.message.replaceAll(rootArg,'<app>')}; }
}
