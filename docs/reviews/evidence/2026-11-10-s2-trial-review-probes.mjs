// Independent bounded probes. No model dispatch or changes to implementation/cache.
// After pnpm s2:build: node <this-file> <codex-path> <new-output.json>
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import { collectUsage } from '../../../work/s2-build/trial/telemetry.js';
import { configuration, runTool } from '../../../work/s2-build/trial/runtime.js';
const [codex, out] = process.argv.slice(2);
if (!codex || !out || fs.existsSync(out)) throw Error('Expected codex path and new output');
const usage = { input_tokens: 10, output_tokens: 2, cached_input_tokens: 5, reasoning_output_tokens: 1 };
const terminal = id => ({ type: 'turn.completed', ...(id ? { id } : {}), usage });
const cases = {
    valid: [{ type: 'turn.started' }, terminal()],
    unfinishedSecondTurn: [{ type: 'turn.started' }, terminal(), { type: 'turn.started' }],
    completionWithoutStart: [terminal()],
    twoCompletionsMaskUnfinishedTurn: [{ type: 'turn.started' }, terminal('a'), terminal('b'), { type: 'turn.started' }],
    nullEvent: [null],
};
const observations = Object.fromEntries(Object.entries(cases).map(([name, events]) => {
    try { return [name, { raw: events, actual: collectUsage(events.map(e => JSON.stringify(e))).summary() }]; }
    catch (error) { return [name, { raw: events, thrown: String(error) }]; }
}));
assert.equal(observations.valid.actual.complete, true);
assert.equal(observations.unfinishedSecondTurn.actual.complete, false);

const root = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 's2-review-pipe-')));
let timeout;
try {
    const layout = { root, source: path.join(root, 'source'), materials: path.join(root, 'materials'), auxiliary: path.join(root, 'auxiliary'), scratch: path.join(root, 'scratch'), home: path.join(root, 'home'), control: path.join(root, 'control'), readOnly: [path.join(root, 'bin')], denied: ['/Users'] };
    for (const key of ['source', 'materials', 'auxiliary', 'scratch', 'home', 'control']) fs.mkdirSync(layout[key]);
    fs.mkdirSync(path.join(root, 'bin'));
    const node = path.join(root, 'bin/node'); fs.copyFileSync(fs.realpathSync(process.execPath), node); fs.chmodSync(node, 0o555);
    fs.writeFileSync(path.join(layout.control, 'config.toml'), configuration(layout));
    // Bounded check of inherited-pipe behavior; descendant exits on its own after 1.6 s.
    const childCode = 'setTimeout(()=>process.exit(0),1600)';
    const parentCode = `require('node:child_process').spawn(process.execPath,['-e',${JSON.stringify(childCode)}],{detached:true,stdio:['ignore','inherit','inherit']}).unref();setInterval(()=>{},1000);`;
    timeout = await runTool(codex, layout, [node, '-e', parentCode], 350);
    assert.equal(timeout.reason, 'timeout');
} finally { fs.rmSync(root, { recursive: true, force: true }); }

const bundle = 'experiments/domain-model/s2/results/2026-11-10-trial-preparation';
const old = 'experiments/domain-model/s2/results/2026-11-09-modal-fix';
const guide = fs.readFileSync(path.join(bundle, 'C/guide.md'), 'utf8');
const facts = fs.readFileSync(path.join(bundle, 'C/observations.md'), 'utf8');
const evidence = fs.readFileSync(path.join(bundle, 'C/evidence.md'), 'utf8');
const viewFiles = fs.readdirSync(path.join(bundle, 'B/views'));
let items = 0, claims = 0, quotes = 0, relations = 0;
for (const file of viewFiles) {
    const bytes = fs.readFileSync(path.join(bundle, 'B/views', file));
    assert.equal(bytes.toString(), fs.readFileSync(path.join(old, 'B/views', file), 'utf8'));
    const v = JSON.parse(bytes);
    if (file.startsWith('item-')) {
        items++; assert.ok(guide.includes(v.item.value.source.interpretation));
        for (const q of v.item.value.source.unverified) assert.ok(guide.includes(JSON.stringify(q)));
        for (const r of v.neighbors.value) {
            relations++; assert.ok(guide.includes(`관계 "${r.kind}"는 "${r.from}"에서 "${r.to}"로 향한다. 이 항목에서 본 방향은 "${r.direction}"`));
        }
    } else if (file.startsWith('fact-')) { claims++; assert.ok(facts.includes(v.value.source.claim)); }
    else if (file.startsWith('evidence-')) { quotes++; assert.ok(evidence.includes('~~~text\n' + v.value.text + '\n~~~')); }
}
fs.writeFileSync(out, JSON.stringify({ usage: observations, inheritedPipeTimeout: { limitMs: 350, ...timeout }, materialChecks: { unchangedBViews: viewFiles.length, interpretations: items, claims, sourceQuotes: quotes, directedNeighborOccurrences: relations, humanApproval: false }, scope: 'Synthetic event boundaries and bounded sandbox process probe; no provider or agent calls' }, null, 2) + '\n', { flag: 'wx' });
console.log('Independent probes recorded');
