import fs from 'node:fs';
import path from 'node:path';
import { openEnvironment, evaluateSubmission } from './evaluate.js';
import { readSubmission } from './submission.js';
const [sourceArg,envArg,out,repoArg]=process.argv.slice(2);
if(!sourceArg||!envArg||!out) throw Error('Usage: evaluate <complete-submitted-source-root> <prepared-environment-root> <new-result.json> [repo]');
if(fs.existsSync(out)) throw Error('Output exists');
fs.mkdirSync(path.dirname(out),{recursive:true});
try {
    const env=openEnvironment(path.resolve(envArg),path.resolve(repoArg??'.'));
    const report=await evaluateSubmission(env,readSubmission(path.resolve(sourceArg)),'complete-root');
    fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n',{flag:'wx'});
    console.log(JSON.stringify({overall:report.overall,typecheck:report.typecheck.status,behavior:report.behavior.status}));
} catch(e) {
    fs.writeFileSync(out,JSON.stringify({overall:'unsupported',typecheck:{status:'not-run'},behavior:{status:'not-run'},error:String(e),readyForTrial:false},null,2)+'\n',{flag:'wx'});
    process.exitCode=1;
}
