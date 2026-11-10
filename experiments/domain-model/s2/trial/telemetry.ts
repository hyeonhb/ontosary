export interface UsageEvent { id:string; input:number; output:number; cachedInput:number|null; reasoningOutput:number|null; }
export class Ledger {
    readonly events:UsageEvent[]=[]; readonly issues:string[]=[]; private seen=new Map<string,string>();
    add(event:UsageEvent) {
        const text=JSON.stringify(event), prior=this.seen.get(event.id);
        if(prior) {if(prior!==text)this.issues.push('Conflicting duplicate usage '+event.id);return;}
        if(!event.id||[event.input,event.output,event.cachedInput??0,event.reasoningOutput??0].some(x=>!Number.isSafeInteger(x)||x<0)||event.cachedInput!==null&&event.cachedInput>event.input||event.reasoningOutput!==null&&event.reasoningOutput>event.output) {this.issues.push('Invalid usage event');return;}
        this.seen.set(event.id,text);this.events.push({...event});
    }
    summary() {
        const input=this.events.reduce((n,e)=>n+e.input,0),output=this.events.reduce((n,e)=>n+e.output,0);
        const complete=this.events.length>0&&this.issues.length===0;
        return {inputObserved:input,outputObserved:output,totalObserved:input+output,input:complete?input:null,output:complete?output:null,total:complete?input+output:null,cachedInput:this.events.some(e=>e.cachedInput===null)?null:this.events.reduce((n,e)=>n+e.cachedInput!,0),reasoningOutput:this.events.some(e=>e.reasoningOutput===null)?null:this.events.reduce((n,e)=>n+e.reasoningOutput!,0),referenceTokens:100000,overReference:Math.max(0,input+output-100000),hardCap:false,complete,issues:[...this.issues],definition:'Input includes cached input; output includes reasoning. Neither detail is added again.'};
    }
}
/** JSONL turn.completed usage is turn-level, not a guarantee of request-level coverage. */
export function collectUsage(lines:string[]) {
    const ledger=new Ledger();let turn=0;
    for(const [i,line] of lines.entries()) {
        let e:any;try{e=JSON.parse(line);}catch{ledger.issues.push('Malformed JSONL line '+i);continue;}
        if(e.type==='turn.started')turn++;
        if(e.type==='turn.completed') {
            const u=e.usage;if(!u){ledger.issues.push('Missing usage for turn '+turn);continue;}
            ledger.add({id:e.id??'turn/'+turn,input:u.input_tokens,output:u.output_tokens,cachedInput:u.cached_input_tokens??null,reasoningOutput:u.reasoning_output_tokens??null});
        }
        if(e.type==='turn.failed'||e.type==='error')ledger.issues.push('Failed/incomplete turn '+turn);
    }
    if(!ledger.events.length)ledger.issues.push('No completed-turn usage; consumption unknown, not zero');
    if(ledger.events.length<turn)ledger.issues.push('Usage missing for started turn(s)');
    return ledger;
}
export function schedule(seed:string) {
    // A seeded permutation followed by cyclic rotations is balanced in every position.
    let n=2166136261;for(const c of seed)n=Math.imul(n^c.charCodeAt(0),16777619)>>>0;
    const conditions=['A','B','C'];for(let i=2;i>0;i--){n=(Math.imul(n,1664525)+1013904223)>>>0;const j=n%(i+1);[conditions[i],conditions[j]]=[conditions[j]!,conditions[i]!];}
    return Array.from({length:9},(_,i)=>({runId:'run-'+String(i+1).padStart(2,'0'),block:Math.floor(i/3)+1,position:i%3+1,condition:conditions[(i%3+Math.floor(i/3))%3],status:'not-run',attempts:[]}));
}
export function refuseTrial():never {throw Error('Trial not authorized: preparation entry point cannot dispatch a model. Independent review and hash-bound approval are pending.');}
