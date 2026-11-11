// Manager-only known submissions. Complete roots contain exactly the pinned inventory plus variantDelta.
import fs from 'node:fs';import path from 'node:path';
import {openEnvironment} from './build/evaluation/evaluate.js';
import {variantDelta} from './build/evaluation/variants.js';
import {deltaSubmission,manifest} from './build/evaluation/submission.js';
import {hash,stable} from './build/lib/analysis-session.js';
const env=openEnvironment('/environment','/tools/repo');
for(const name of ['baseline','reference','helper-type-error','wrong-modal-order']) {
 const delta=variantDelta(name,env.baseline,'/tools/repo');const sources=deltaSubmission(env.baseline,delta);const root='/assembled/'+name;fs.mkdirSync(root);
 for(const [file,bytes] of sources){const f=path.join(root,file);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,bytes);}
 const submittedManifest=manifest(sources);
 fs.writeFileSync('/assembled/'+name+'.json',JSON.stringify({name,kind:'known-submission-input',delta,submittedManifest,submissionId:hash(stable(submittedManifest))},null,2)+'\n');
}
env.assertUnchanged();console.log('Four complete roots assembled from the original variantDelta');
