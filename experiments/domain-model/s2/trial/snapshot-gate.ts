import fs from 'node:fs';
import path from 'node:path';
import { tree } from './runtime.js';
import { hash, stable } from '../lib/analysis-session.js';
import { readSubmission, manifest } from '../evaluation/submission.js';
/** Validate the entire collected tree before the legacy complete-root reader can skip environment directories. */
export function checkedSnapshot(root:string) {
    const record=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'),'utf8')) as {source:Record<string,string>;auxiliary:Record<string,string>;sourceId:string};
    const actual=tree(path.join(root,'source'));
    if(stable(actual)!==stable(record.source)||hash(JSON.stringify(actual))!==record.sourceId||stable(tree(path.join(root,'auxiliary')))!==stable(record.auxiliary))throw Error('Snapshot integrity mismatch');
    const sources=readSubmission(path.join(root,'source'));
    if(stable(manifest(sources))!==stable(record.source))throw Error('Unsupported production files would be omitted by evaluator; preserve snapshot and reject, never restore baseline');
    return sources;
}
