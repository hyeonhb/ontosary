import { hash, stable } from '../lib/analysis-session.js';
import type { RunResult } from './runtime.js';
export const accountingVersion = 's2-usage-v2-turn-state';
export interface LogEnd {
    termination: 'verified' | 'unverified' | 'fixture';
    reason: 'completed' | 'timeout' | 'spawn-error' | 'interrupted' | 'unknown';
    code: number | null;
    normalEOF: boolean;
    outputTruncated: boolean;
    readErrors: readonly string[];
}
export const unknownEnd: LogEnd = {termination:'unverified',reason:'unknown',code:null,normalEOF:false,outputTruncated:false,readErrors:[]};
export function usageEnd(r: RunResult): LogEnd {
    return {termination:'unverified',reason:r.reason,code:r.code,normalEOF:r.normalEOF,outputTruncated:r.outputTruncated,readErrors:r.readErrors};
}
interface Usage { input:number; output:number; cachedInput:number|null; reasoningOutput:number|null; }
interface Turn { ordinal:number; startLine:number; terminalLine:number|null; state:'active'|'completed'|'failed'; valid:boolean; usage:Usage|null; }
interface Row { line:number; sha256:string; type:string|null; turn:number|null; disposition:string; }
interface Issue { line:number|null; code:string; }
const object=(x:unknown):x is Record<string,unknown>=>!!x&&typeof x==='object'&&!Array.isArray(x);
const integer=(x:unknown):x is number=>typeof x==='number'&&Number.isSafeInteger(x)&&x>=0;
function usage(x:unknown):Usage|null {
    if(!object(x)||!integer(x.input_tokens)||!integer(x.output_tokens))return null;
    const cached=x.cached_input_tokens??null,reasoning=x.reasoning_output_tokens??null;
    if(cached!==null&&(!integer(cached)||cached>x.input_tokens)||reasoning!==null&&(!integer(reasoning)||reasoning>x.output_tokens))return null;
    return {input:x.input_tokens,output:x.output_tokens,cachedInput:cached as number|null,reasoningOutput:reasoning as number|null};
}
/** One pass, bounded metadata only. Caller keeps raw JSONL separately; row hashes refer to 1-based lines. */
export class UsageLedger {
    private turns:Turn[]=[];
    private rows:Row[]=[];
    private issues:Issue[]=[];
    private identities=new Map<string,{signature:string;turn:Turn|null}>();
    private active:Turn|null=null;
    private last:Turn|null=null;
    private bytes=0;
    private line=0;
    private limited=false;
    private end:LogEnd=unknownEnd;
    private finished=false;
    get atCapacity() {return this.limited;}
    readonly limits={lines:10000,lineBytes:65536,totalBytes:4*1024*1024};
    private issue(code:string,line:number|null=this.line) { this.issues.push({line,code}); }
    private invalidate(turn:Turn|null) { if(turn)turn.valid=false; }
    accept(raw:string) {
        if(this.finished)throw Error('Usage log already finished');
        this.line++;
        if(this.limited)return;
        this.bytes+=Buffer.byteLength(raw)+1;
        if(this.line>this.limits.lines||this.bytes>this.limits.totalBytes) {this.limited=true;this.issue('accounting-capacity-exceeded');return;}
        const row:Row={line:this.line,sha256:hash(raw),type:null,turn:null,disposition:'excluded'};this.rows.push(row);
        if(Buffer.byteLength(raw)>this.limits.lineBytes){this.issue('oversized-line');return;}
        let e:unknown;
        try {e=JSON.parse(raw);}catch {this.issue('malformed-json');return;}
        if(!object(e)||typeof e.type!=='string'||!e.type){this.issue('invalid-event-structure');return;}
        row.type=e.type;
        const known=['turn.started','turn.completed','turn.failed','error'].includes(e.type);
        if(!known){row.disposition='non-accounting-event';return;}
        // Public exec events have no turn ID. Do not silently interpret extensions as supported concurrency.
        if('turn_id' in e){this.issue('unsupported-turn-identity');this.invalidate(this.active);return;}
        const target=e.type==='turn.started'?null:(this.active??this.last);
        if('id' in e) {
            if(typeof e.id!=='string'||!e.id||e.id.length>256){this.issue('invalid-event-identity');this.invalidate(target);return;}
            let signature:string;
            try{signature=stable(e);}catch{this.issue('unrepresentable-event-identity');this.invalidate(target);this.invalidate(this.identities.get(e.id)?.turn??null);return;}
            const prior=this.identities.get(e.id);
            if(prior) {
                row.turn=prior.turn?.ordinal??null;
                if(prior.signature===signature&&(!this.active||prior.turn===this.active))row.disposition='identical-redelivery';
                else {this.issue('conflicting-or-cross-turn-identity');this.invalidate(prior.turn);this.invalidate(this.active);row.disposition='conflicting-redelivery';}
                return;
            }
            this.identities.set(e.id,{signature,turn:target});
        }
        if(e.type==='turn.started') {
            const overlap=this.active!==null;
            if(overlap){this.issue('nested-start');this.invalidate(this.active);}
            const t:Turn={ordinal:this.turns.length+1,startLine:this.line,terminalLine:null,state:'active',valid:!overlap,usage:null};
            this.turns.push(t);this.active=t;row.turn=t.ordinal;row.disposition='started';
            if(typeof e.id==='string')this.identities.get(e.id)!.turn=t;
            return;
        }
        row.turn=target?.ordinal??null;
        if(e.type==='error') {
            if(typeof e.message!=='string')this.issue('invalid-error-structure');
            this.issue('stream-error');this.invalidate(this.active);row.disposition='stream-error';return;
        }
        if(!this.active) {
            this.issue(this.last?'additional-terminal-without-start':'terminal-without-start');
            // Retract a previously counted turn when another terminal contradicts it, even with a new event ID.
            this.invalidate(this.last);return;
        }
        const t=this.active;this.active=null;this.last=t;t.terminalLine=this.line;
        if(e.type==='turn.failed') {
            t.state='failed';t.valid=false;
            if(!object(e.error)||typeof e.error.message!=='string')this.issue('invalid-failure-structure');
            this.issue('turn-failed');row.disposition='failed';return;
        }
        t.state='completed';t.usage=usage(e.usage);row.disposition='completed';
        if(!t.usage){t.valid=false;this.issue('missing-or-invalid-usage');}
    }
    finish(end:LogEnd) {
        if(this.finished)throw Error('Usage log already finished');
        this.finished=true;this.end={...end,readErrors:[...end.readErrors]};
        if(this.active){this.invalidate(this.active);this.issue('unfinished-turn',this.active.startLine);}
        if(!this.turns.length)this.issue('no-started-turn',null);
        if(!['verified','fixture'].includes(end.termination)||end.reason!=='completed'||end.code!==0||!end.normalEOF||end.outputTruncated||end.readErrors.length)this.issue('incomplete-log-or-execution',null);
        return this;
    }
    summary() {
        const valid=this.turns.filter(t=>t.valid&&t.state==='completed'&&t.usage!==null);
        const sum=(field:keyof Usage):number|null=>{
            if(!valid.length||valid.some(t=>t.usage![field]===null))return null;
            const n=valid.reduce((a,t)=>a+BigInt(t.usage![field]!),0n);
            return n<=BigInt(Number.MAX_SAFE_INTEGER)?Number(n):null;
        };
        const input=sum('input'),output=sum('output'),cachedInput=sum('cachedInput'),reasoningOutput=sum('reasoningOutput');
        const total=input!==null&&output!==null&&Number.isSafeInteger(input+output)?input+output:null;
        const overflow=valid.length>0&&total===null;
        const issues=[...this.issues,...(overflow?[{line:null,code:'aggregate-overflow'}]:[])];
        const complete=this.finished&&valid.length>0&&valid.length===this.turns.length&&issues.length===0;
        return {schema:accountingVersion,complete,input:complete?input:null,output:complete?output:null,total:complete?total:null,
            subtotal:{input,output,total,cachedInput,reasoningOutput,turns:valid.map(t=>t.ordinal),meaning:'Validated non-contradictory completed turns only; not a claimed lower bound of provider consumption'},
            consumptionLowerBound:null,referenceTokens:100000,hardCap:false,
            reference:{confirmedExcess:complete&&total!==null?Math.max(0,total-100000):null,validatedSubtotalExcess:total===null?null:Math.max(0,total-100000),wholeRunBelowReference:complete&&total!==null?total<=100000:null},
            issues,turns:this.turns.map(t=>({...t,usage:t.usage?{...t.usage}:null})),rows:this.rows.map(r=>({...r})),end:this.end,aggregationTruncated:this.limited,limits:this.limits,
            definition:'Sequential exec turns; input includes cache, output includes reasoning. Event IDs are optional stream-scoped replay identities, never turn IDs. No provider calls verified.'};
    }
}
export function collectUsage(lines:Iterable<string>,end:LogEnd=unknownEnd) {
    const ledger=new UsageLedger();for(const line of lines){ledger.accept(line);if(ledger.atCapacity)break;}return ledger.finish(end);
}
export function schedule(seed:string) {
    // A seeded permutation followed by cyclic rotations is balanced in every position.
    let n=2166136261;for(const c of seed)n=Math.imul(n^c.charCodeAt(0),16777619)>>>0;
    const conditions=['A','B','C'];for(let i=2;i>0;i--){n=(Math.imul(n,1664525)+1013904223)>>>0;const j=n%(i+1);[conditions[i],conditions[j]]=[conditions[j]!,conditions[i]!];}
    return Array.from({length:9},(_,i)=>({runId:'run-'+String(i+1).padStart(2,'0'),block:Math.floor(i/3)+1,position:i%3+1,condition:conditions[(i%3+Math.floor(i/3))%3],status:'not-run',attempts:[]}));
}
export function refuseTrial():never {throw Error('Trial not authorized: preparation entry point cannot dispatch a model. Independent review and hash-bound approval are pending.');}
