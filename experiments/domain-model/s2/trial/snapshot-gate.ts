import fs from 'node:fs';
import path from 'node:path';
import { tree } from './runtime.js';
import { hash, stable } from '../lib/analysis-session.js';
import { readSubmission, manifest } from '../evaluation/submission.js';
/** No production receipt issuer exists in this runtime. A caller-authored manifest cannot grant authority. */
export function checkedSnapshot(_root:string):never {
    throw Error('R11 unresolved: no verified termination receipt; production evaluation blocked');
}
/** Integrity only, never proof of writer termination. Private calibration additionally checks known fixture bytes. */
export function checkedDiagnosticSnapshot(root:string) {
    const text=fs.readFileSync(path.join(root,'manifest.json'),'utf8');
    if(hash(text)!==fs.readFileSync(path.join(root,'manifest.sha256'),'utf8').trim())throw Error('Diagnostic manifest integrity mismatch');
    const record=JSON.parse(text) as {version:number;kind:string;validSubmission:boolean;source:Record<string,string>;auxiliary:Record<string,string>;sourceId:string};
    if(record.version!==2||record.kind!=='diagnostic'||record.validSubmission!==false)throw Error('Expected diagnostic evidence, never sealed submission');
    const actual=tree(path.join(root,'source'));
    if(stable(actual)!==stable(record.source)||hash(JSON.stringify(actual))!==record.sourceId||stable(tree(path.join(root,'auxiliary')))!==stable(record.auxiliary))throw Error('Snapshot integrity mismatch');
    const sources=readSubmission(path.join(root,'source'));
    if(stable(manifest(sources))!==stable(record.source))throw Error('Unsupported production files would be omitted by evaluator; preserve snapshot and reject, never restore baseline');
    return sources;
}
