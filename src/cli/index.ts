#!/usr/bin/env node
import { parseArgs } from 'node:util';
import { selectFunction, compare, discoverConcepts } from '../core/index.js';
import { scanWithCompiler } from '../core/analyzer.js';
import { selectCompiler } from './compiler.js';

const help = `Ontosary — evidence-based TypeScript analysis (PoC)

ontosary scan <project-directory|tsconfig.json> [--json]
ontosary concepts <project-directory|tsconfig.json> [--json]
ontosary compare <project-directory|tsconfig.json> <function-name-or-id> <function-name-or-id> --assume-same-input [--json]

All commands accept --typescript-version 4.9.4|5.9.3 (default 5.9.3).
An explicit selection reports compiler.requested and compiler.used in the JSON result.
Outputs JSON by default. Comparisons use positional arguments and property paths.
Functions with explicit TypeScript this parameters are Unsupported (not arg0).
--assume-same-input explicitly asserts that both predicates receive the same inputs.
Exit codes: 0 result, 1 usage/project/compiler error, 2 Unknown/Unsupported.
No code is executed or modified by the analyzer.`;
let compilerInfo: { requested: string; used: string | null } | undefined;
try {
  const { values, positionals } = parseArgs({ options: { 'typescript-version': { type: 'string' }, json: { type: 'boolean' }, help: { type: 'boolean', short: 'h' }, 'assume-same-input': { type: 'boolean' } }, allowPositionals: true });
  if (values.help || !positionals.length) { console.log(help); }
  else {
    const [command, project, left, right] = positionals;
    if (!['scan', 'concepts', 'compare'].includes(command!) || !project || positionals.length !== (command === 'compare' ? 4 : 2)) throw new Error(help);
    const requested = values['typescript-version'];
    if (requested !== undefined) compilerInfo = { requested, used: null };
    const compiler = selectCompiler(requested);
    if (compilerInfo) compilerInfo.used = compiler.version;
    const facts = scanWithCompiler(project, compiler);
    const errors = facts.diagnostics.filter(d => d.category === 'Error');
    if (command !== 'scan' && errors.length) throw new Error(`Compiler errors prevent analysis: ${errors.map(d => d.message).join('; ')}`);
    if (command === 'scan') {
      console.log(JSON.stringify({ ...facts, compiler: compilerInfo }, null, 2));
      if (errors.length) process.exitCode = 1;
    } else if (command === 'concepts') console.log(JSON.stringify({ ...discoverConcepts(facts), compiler: compilerInfo }, null, 2));
    else {
      const a = selectFunction(facts, left!), b = selectFunction(facts, right!);
      const comparison = compare(a.predicate, b.predicate, { sameInput: values['assume-same-input'] });
      console.log(JSON.stringify({ schemaVersion: 1, category: 'code-facts', left: { id: a.id, evidence: a.predicateEvidence ?? a.evidence, predicate: a.predicate }, right: { id: b.id, evidence: b.predicateEvidence ?? b.evidence, predicate: b.predicate }, ...comparison, compiler: compilerInfo,
        interpretation: 'A logical difference is not evidence of a business-policy violation without an independently established shared policy.' }, null, 2));
      if (comparison.status === 'Unknown' || comparison.status === 'Unsupported') process.exitCode = 2;
    }
  }
} catch (error) {
  console.error(JSON.stringify({ error: error instanceof Error ? error.message : String(error), compiler: compilerInfo }));
  process.exitCode = 1;
}
