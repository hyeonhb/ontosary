import fs from 'node:fs';
const runId = process.argv[2];
console.log(JSON.stringify({event:'payload-start',runId}));
const sourceRead = fs.readFileSync('/source/input.txt','utf8') === 'smoke source\n';
fs.writeFileSync('/source/output.txt',`smoke output ${runId}\n`);
const sourceWrite = fs.readFileSync('/source/output.txt','utf8') === `smoke output ${runId}\n`;
const materialRead = fs.readFileSync('/materials/input.txt','utf8') === 'smoke material\n';
console.log(JSON.stringify({event:'payload-complete',runId,sourceRead,sourceWrite,materialRead}));
process.exit(sourceRead && sourceWrite && materialRead ? 0 : 2);
