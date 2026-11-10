// Synthetic records only. After pnpm s2:build, run from repository root with a new output path.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import { collectUsage } from '../../../../../work/s2-build/trial/telemetry.js';
const out=process.argv[2];if(!out||fs.existsSync(out))throw Error('New output required');
const end={termination:'fixture',reason:'completed',code:0,normalEOF:true,outputTruncated:false,readErrors:[]};
const s={type:'turn.started'},d=id=>({type:'turn.completed',...(id?{id}:{}),usage:{input_tokens:10,output_tokens:2,cached_input_tokens:5,reasoning_output_tokens:1}});
const inputs={valid:[s,d()],unfinishedSecondTurn:[s,d(),s],completionWithoutStart:[d()],twoCompletionsMaskUnfinishedTurn:[s,d('a'),d('b'),s],nullEvent:[null],sameNumbersTwoTurns:[s,d(),s,d()],redelivery:[s,d('a'),d('a')],conflict:[s,d('a'),{...d('a'),usage:{input_tokens:20,output_tokens:2}}],idlessDuplicate:[s,d(),d()],nested:[s,s,d()],failed:[s,{type:'turn.failed',error:{message:'fixture'}}],missingUsage:[s,{type:'turn.completed'}],overflow:[s,{type:'turn.completed',usage:{input_tokens:Number.MAX_SAFE_INTEGER,output_tokens:1}}],referenceExcess:[s,{type:'turn.completed',usage:{input_tokens:99999,output_tokens:5,cached_input_tokens:90000,reasoning_output_tokens:2}}]};
const rows=Object.entries(inputs).map(([name,events])=>({name,raw:events.map(e=>JSON.stringify(e)),end,actual:collectUsage(events.map(e=>JSON.stringify(e)),end).summary()}));
for(const [name,ending] of Object.entries({timeout:{...end,reason:'timeout'},truncated:{...end,outputTruncated:true},stopped:{...end,normalEOF:false}}))rows.push({name,raw:[s,d()].map(e=>JSON.stringify(e)),end:ending,actual:collectUsage([s,d()].map(e=>JSON.stringify(e)),ending).summary()});
rows.push({name:'malformed',raw:[JSON.stringify(s),JSON.stringify(d()),'{bad'],end,actual:collectUsage([JSON.stringify(s),JSON.stringify(d()),'{bad'],end).summary()});
const get=name=>rows.find(x=>x.name===name).actual;
assert.equal(get('valid').total,12);assert.equal(get('unfinishedSecondTurn').total,null);assert.equal(get('completionWithoutStart').total,null);assert.equal(get('twoCompletionsMaskUnfinishedTurn').subtotal.total,null);assert.equal(get('nullEvent').complete,false);assert.equal(get('sameNumbersTwoTurns').total,24);assert.equal(get('redelivery').total,12);assert.equal(get('referenceExcess').total,100004);assert.equal(get('referenceExcess').reference.confirmedExcess,4);
for(const name of ['timeout','truncated','stopped','malformed','conflict','idlessDuplicate','nested','failed','missingUsage','overflow'])assert.equal(get(name).complete,false);
fs.writeFileSync(out,JSON.stringify({kind:'synthetic-JSONL-accounting',providerCalls:0,rows},null,2)+'\n',{flag:'wx'});
console.log(rows.length);
