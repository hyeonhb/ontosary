// Exploratory literal search after source reading. This is not a timed human baseline.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { gunzipSync } from 'node:zlib';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
const [id, cache, result] = process.argv.slice(2), here = path.dirname(fileURLToPath(import.meta.url));
const manifest = JSON.parse(fs.readFileSync(path.join(here, 'manifest.json'))), c = manifest.candidates.find(c => c.id === id);
if (!c || !cache || !result) throw new Error('Usage: node experiments/public-app/v1/search-baseline.mjs <candidate> <cache> <result>');
const task = JSON.parse(fs.readFileSync(path.join(here, c.task)));
const facts = JSON.parse(gunzipSync(fs.readFileSync(path.join(result, 'scoped/scan.json.gz'))));
const configDir = path.dirname(c.scopedConfigPath ?? 'ontosary.scope.json');
const files = [...new Set([...facts.files.map(f => path.posix.normalize(path.posix.join(configDir, f))), ...task.evidence.filter(e => e.file.endsWith('.html')).map(e => e.file)])].sort();
const pattern = 'cancelOrder|OrderCancel|cancel-order|cancelOrRefund';
const run = spawnSync('rg', ['--json', '-i', '-e', pattern, '--', ...files], { cwd: path.join(path.resolve(cache), id), encoding: 'utf8', maxBuffer: 16 * 1024 * 1024 });
if (run.status !== 0) throw new Error(`rg failed: ${run.stderr}`);
const hits = run.stdout.trim().split('\n').map(s => JSON.parse(s)).filter(e => e.type === 'match').map(e => ({ file: e.data.path.text, line: e.data.line_number }));
console.log(JSON.stringify({ candidate: id, tool: spawnSync('rg', ['--version'], { encoding: 'utf8' }).stdout.split('\n')[0], pattern,
  scope: 'Same scoped scan file list plus explicitly required HTML source; compiler-error facts provide only a file inventory, not trusted groups.',
  inputFiles: files, matchedFiles: [...new Set(hits.map(h => h.file))].sort(), matchedLines: hits.length,
  requiredEvidence: task.evidence.filter(e => e.role === 'required').map(e => ({ id: e.id, file: e.file, line: e.line, fileReached: hits.some(h => h.file === e.file), anchorLineMatched: hits.some(h => h.file === e.file && h.line === e.line) })),
  scriptSha256: createHash('sha256').update(fs.readFileSync(fileURLToPath(import.meta.url))).digest('hex'),
  interpretation: 'Agent knew the provisional answer while choosing these terms. Filename/line hits do not prove understanding or task completion. LSP and human timing were not exercised.' }, null, 2));
