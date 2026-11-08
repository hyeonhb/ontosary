// Worker: preserve compiler program closure and raw scan, including failures.
import fs from 'node:fs';
import path from 'node:path';
import ts from 'typescript';
import { gzipSync } from 'node:zlib';
import { createHash } from 'node:crypto';
import { scan, buildContext, discoverConcepts } from '../../../dist/core/index.js';
const [rootArg, configName, outArg] = process.argv.slice(2);
const root = path.resolve(rootArg), out = path.resolve(outArg), config = path.join(root, configName);
const sha = b => createHash('sha256').update(b).digest('hex');
const tsLib = path.dirname(ts.getDefaultLibFilePath({}));
const clean = text => text.replaceAll(root, '<app>').replaceAll(tsLib, '<typescript-lib>');
const write = (name, obj) => { const text = clean(JSON.stringify(obj, null, 2)) + '\n'; fs.writeFileSync(path.join(out, name), name.endsWith('.gz') ? gzipSync(text) : text); };
const rel = f => f === root ? '.' : f.startsWith(root + path.sep) ? path.relative(root, f) : f.startsWith(tsLib + path.sep) ? `<typescript-lib>/${path.relative(tsLib, f)}` : '<external>/' + path.basename(f);
const loaded = ts.readConfigFile(config, ts.sys.readFile);
if (loaded.error) throw new Error(ts.flattenDiagnosticMessageText(loaded.error.messageText, '\n'));
const parsed = ts.parseJsonConfigFileContent(loaded.config, ts.sys, path.dirname(config), { noEmit: true }, config);
// Record config before invoking the unchanged product guard.
write('config.json', { config: configName, raw: loaded.config, effectiveOptions: parsed.options, scanEvidenceBase: rel(path.dirname(config)), roots: parsed.fileNames.map(rel),
  parseErrors: parsed.errors.map(d => ({ code: d.code, message: ts.flattenDiagnosticMessageText(d.messageText, '\n') })), projectReferences: parsed.projectReferences?.map(r => rel(r.path)) ?? [] });
if (parsed.errors.length || (!parsed.options.strict && !parsed.options.strictNullChecks) || parsed.options.strictNullChecks === false) {
  let rejection;
  try { scan(config); } catch (e) { rejection = e.message; }
  if (!rejection) throw new Error('Expected original config rejection');
  write('outcome.json', { status: 'rejected-before-program', error: rejection, groups: 'not-run', fca: 'not-run' });
  process.exit(0);
}
const program = ts.createProgram({ rootNames: parsed.fileNames, options: parsed.options, projectReferences: parsed.projectReferences });
const sources = program.getSourceFiles(), resolutions = [];
const resolutionCache = ts.createModuleResolutionCache(root, f => f, parsed.options);
for (const sf of sources.filter(sf => sf.fileName.startsWith(root + path.sep))) {
  for (const imported of ts.preProcessFile(sf.text, true, true).importedFiles) {
    const resolved = ts.resolveModuleName(imported.fileName, sf.fileName, parsed.options, ts.sys, resolutionCache).resolvedModule;
    resolutions.push({ from: rel(sf.fileName), specifier: imported.fileName, resolved: resolved ? rel(resolved.resolvedFileName) : null,
      externalLibrary: resolved?.isExternalLibraryImport ?? null });
  }
}
write('program.json.gz', { files: sources.map(sf => ({ path: rel(sf.fileName), sha256: sha(fs.readFileSync(sf.fileName)), declaration: sf.isDeclarationFile,
  externalLibrary: program.isSourceFileFromExternalLibrary(sf) })), imports: resolutions,
  note: 'Actual TypeScript Program files and preprocessing/resolution of literal imports/exports. Dynamic nonliteral imports/runtime/module plugin behavior are not fully enumerated. Missing modules are not stubbed.' });
// The product scan builds its own identical Program and preserves all diagnostics.
const facts = scan(config);
write('scan.json.gz', facts);
const errors = facts.diagnostics.filter(d => d.category === 'Error');
const counts = values => Object.fromEntries([...new Set(values)].sort().map(v => [v, values.filter(x => x === v).length]));
const summary = { status: errors.length ? 'compiler-errors' : 'scanned', analyzedFiles: facts.files.length, types: facts.types.length, functions: facts.functions.length,
  diagnostics: counts(facts.diagnostics.map(d => `${d.category}:${d.code}`)), errorCount: errors.length, omissions: facts.omissions.length,
  predicateSupport: counts(facts.functions.map(f => f.predicate.status)), programFiles: sources.length,
  unresolvedImports: resolutions.filter(r => !r.resolved).length, unresolvedSpecifiers: [...new Set(resolutions.filter(r => !r.resolved).map(r => r.specifier))].sort(),
  groups: 'not-run: compiler errors', fca: 'not-run: compiler errors' };
if (!errors.length) {
  const context = buildContext(facts);
  const groups = context.attributes.filter(a => /^(type|property):/.test(a)).map(a => ({ attribute: a, functions: context.objects.filter(o => context.incidence[o]?.includes(a)) })).filter(g => g.functions.length >= 2);
  write('simple-groups.json', groups);
  summary.groups = 'completed';
  try { const concepts = discoverConcepts(facts); write('concepts.json', concepts); summary.fca = 'completed'; }
  catch (e) { write('concepts-failure.json', { error: e.message }); summary.fca = 'rejected: ' + e.message; }
}
write('outcome.json', summary);
