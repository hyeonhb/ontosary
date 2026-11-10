import fs from 'node:fs';
import path from 'node:path';
import { checkedDiagnosticSnapshot } from './snapshot-gate.js';
import { openEnvironment, evaluateSubmission } from '../evaluation/evaluate.js';
import { deltaSubmission, manifest } from '../evaluation/submission.js';
import { variantDelta } from '../evaluation/variants.js';
import { stable } from '../lib/analysis-session.js';
// Private known reference fixture only. This cannot turn blocked live output into a submitted trial result.
const [snapshot,cache,out,repo=process.cwd()]=process.argv.slice(2);
if(!snapshot||!cache||!out)throw Error('Usage: evaluate-calibration-snapshot <diagnostic-reference-snapshot> <cache> <new-output> [repo]');
if(fs.existsSync(out))throw Error('Output exists');
const sources=checkedDiagnosticSnapshot(snapshot),env=openEnvironment(path.resolve(cache),path.resolve(repo));
const expected=deltaSubmission(env.baseline,variantDelta('reference',env.baseline,path.resolve(repo)));
if(stable(manifest(sources))!==stable(manifest(expected)))throw Error('Not the known reference calibration fixture');
const evaluation=await evaluateSubmission(env,sources,'complete-root');
checkedDiagnosticSnapshot(snapshot);
fs.writeFileSync(out,JSON.stringify({kind:'known-reference-calibration',validTrialSubmission:false,evaluation},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({overall:evaluation.overall,sourceBinding:evaluation.sourceBinding,validTrialSubmission:false}));
