import fs from 'node:fs';
import path from 'node:path';
import { gunzipSync } from 'node:zlib';
import { hash, stable } from '../lib/analysis-session.js';
const [left,right,out]=process.argv.slice(2);
if(!left||!right||!out)throw Error('Usage: verify-evaluation <first-dir> <repeat-dir> <new-report.json>');
function normalized(value:unknown):unknown {
    if(Array.isArray(value))return value.map(normalized);
    if(value&&typeof value==='object')return Object.fromEntries(Object.entries(value).filter(([key])=>key!=='wallTimeMs').map(([key,v])=>[key,normalized(v)]));
    return value;
}
const names=fs.readdirSync(left).sort();
if(stable(names)!==stable(fs.readdirSync(right).sort()))throw Error('File lists differ');
const hashes:Record<string,string>={};
for(const file of names) {
    const read=(root:string)=>{const f=path.join(root,file);if(!fs.lstatSync(f).isFile())throw Error('Nonregular evidence file');const bytes=fs.readFileSync(f);return normalized(JSON.parse((file.endsWith('.gz')?gunzipSync(bytes):bytes).toString()));};
    const a=stable(read(left)),b=stable(read(right));
    if(a!==b)throw Error('Evaluation evidence differs: '+file);
    hashes[file]=hash(a);
}
fs.writeFileSync(out,JSON.stringify({equivalent:true,files:names.length,excluded:['wallTimeMs fields only; gzip envelope decoded'],hashes},null,2)+'\n',{flag:'wx'});
console.log(names.length);
