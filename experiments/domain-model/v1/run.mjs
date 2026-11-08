import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { gzipSync, gunzipSync } from 'node:zlib';
import ts from 'typescript';
import { formalConcepts } from '../../../dist/core/fca.js';
import { observeRoles, binaryContext, sha } from './observe.mjs';
import { validateModel } from './validate.mjs';
const started = performance.now();
const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../../..');
const [rootArg, outArg] = process.argv.slice(2);
if (!rootArg || !outArg) throw new Error('Usage: node experiments/domain-model/v1/run.mjs <prepared-vendure> <new-output>');
const root = fs.realpathSync(rootArg), out = path.resolve(outArg);
if (fs.existsSync(out)) throw new Error('Output exists; preserve prior observations');
fs.mkdirSync(out, { recursive: true });
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const load = file => JSON.parse(fs.readFileSync(path.join(here, file), 'utf8'));
const write = (file, data) => { const bytes = Buffer.from(JSON.stringify(data,null,2)+'\n'); fs.writeFileSync(path.join(out,file), file.endsWith('.gz') ? gzipSync(bytes) : bytes); };
const manifest = load('manifest.json'), before = load('model-before.json'), manual = load('source-facts.json');
const verifyHash = (file, hash) => { if (sha(fs.readFileSync(file)) !== hash) throw new Error(`Changed input: ${path.basename(file)}`); };
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
write('program-inputs.json.gz',currentProgram);
const diagnostics = [...parsed.errors,...ts.getPreEmitDiagnostics(program)].map(d => ({code:d.code,category:ts.DiagnosticCategory[d.category],file:d.file ? path.relative(root,d.file.fileName) : null}));
const observation = observeRoles(program,manifest,root,diagnostics);
write('observation.json.gz',observation);
const facts = [...manual,...observation.facts];
write('facts.json.gz',facts);
write('model-before.json',before);
const binary = binaryContext(observation,manifest.attributes), context = binary.context;
let fca = null, groups = [], comparisons = [], candidates = [], relations = [], status = binary.status;
if (context && (context.objects.length > 128 || context.attributes.length > 64)) status = 'over-limit';
else if (context) {
  // Both comparisons receive exactly the same incidence; core buildContext is unchanged.
  const evidenceFor = (extent,intent) => extent.flatMap(id => intent.map(a => observation.objects.find(o => o.id === id).cells[a].factRef));
  groups = context.attributes.map(attribute => {
    const extent = context.objects.filter(o => context.incidence[o].includes(attribute));
    const intent = extent.length ? context.attributes.filter(a => extent.every(o => context.incidence[o].includes(a))) : [];
    return { id:`group:${attribute}`,attribute,extent,intent,factRefs:evidenceFor(extent,intent) };
  });
  fca = formalConcepts(context); // unchanged default bounds
  candidates = fca.concepts.filter(c => c.extent.length>=2 && c.intent.length).map(c => ({...c,id:`candidate:${c.id}`,factRefs:evidenceFor(c.extent,c.intent),status:'pending-review'}));
  relations = candidates.flatMap(g => candidates.filter(s => s.id!==g.id && g.intent.every(a => s.intent.includes(a))).map(s => ({general:g.id,specific:s.id,kind:'formal-intent-inclusion-only'})));
  comparisons = candidates.map(c => {
    const same = groups.filter(g => JSON.stringify(g.extent)===JSON.stringify(c.extent)).map(g=>g.id);
    return { candidateRef:c.id,sameExtentGroups:same,additionalIntersection:same.length===0,tooBroadForBusinessIdentity:c.extent.length>manifest.broadGroupThreshold,
      members:c.extent.map(id => {const o=observation.objects.find(x=>x.id===id);return `${o.class}.${o.name}`;}),
      interpretation:'Static role sharing only; business meaning deferred. Direct member-reference search also finds these calls.',
      disposition:'No new business item inferred; known connections retained or broad grouping withheld.' };
  });
  status = fca.truncated ? 'truncated' : 'compared';
}
write('context.json', {status,context});write('simple-groups.json',groups);write('fca.json',{status,formal:fca,candidates,relations,relationScope:'All strict inclusion pairs among emitted candidates, not Hasse edges or business inheritance'});write('candidate-review.json',comparisons);
const after = structuredClone(before);after.stage='after-fca';
const changes=[];
for (const [itemId,attribute] of [['refund-also-cancels','calls-cancel'],['dismiss','closes-dialog-empty']]) {
  const item = after.items.find(i=>i.id===itemId);
  const refs=candidates.filter(c=>c.intent.includes(attribute)).map(c=>c.id);
  item.candidateRefs=refs;
  if(refs.length) changes.push({itemRef:itemId,kind:'added-evidence-links-only',candidateRefs:refs,semanticChange:false,reason:'Already authored from source before FCA; same-extent direct role group is available. Not an FCA discovery.'});
}
write('model-after.json',after);write('model-changes.json',{changes,newSemanticItems:0,removedSemanticItems:0,interpretation:'FCA candidate links are review aids, not new approved knowledge or evidence of incremental utility.'});
const validation=validateModel(after,facts,candidates,read);write('validation.json',validation);
if(!validation.valid) throw new Error('Evidence validation failed');
const fingerprints = Object.fromEntries(fs.readdirSync(here).filter(f => /\.(json|mjs)$/.test(f)).sort().map(f=>[f,sha(fs.readFileSync(path.join(here,f)))]));
write('summary.json',{status,revision:manifest.revision,typescript:ts.version,node:process.version,originalInventoryVerified:inventory.length,preparedProgramFilesVerified:priorProgram.length,diagnostics,
  selectedMethods:observation.objects.length,classes:Object.fromEntries(manifest.classes.map(c=>[c.name,observation.objects.filter(o=>o.class===c.name).length])),attributes:manifest.attributes.length,
  cellCounts:Object.fromEntries(['yes','no','unknown'].map(v=>[v,observation.facts.filter(f=>f.value===v).length])),manualFacts:manual.length,automatedCellFacts:observation.facts.length,
  formalConcepts:fca?.concepts.length??null,candidates:candidates.length,simpleGroups:groups.length,additionalIntersections:comparisons.filter(c=>c.additionalIntersection).length,truncated:fca?.truncated??null,
  approvedKnowledge:after.approvedKnowledge.length,newSemanticItems:0,humanTimeMs:null,agentTaskEffect:null,fingerprints});
write('timing.json',{wallTimeMs:Math.round(performance.now()-started),scope:'Input integrity, live compiler diagnostics, role cells, groups/FCA, model linking and validation. Excludes authoring/tests/delivery.',humanTimeMs:null});
console.log(JSON.stringify({status,methods:observation.objects.length,attributes:manifest.attributes.length,unknown:observation.facts.filter(f=>f.value==='unknown').length,concepts:fca?.concepts.length,candidates:candidates.length,additionalIntersections:comparisons.filter(c=>c.additionalIntersection).length}));
