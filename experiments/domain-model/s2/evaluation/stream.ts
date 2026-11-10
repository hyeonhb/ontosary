import { Failure } from '../lib/model.js';
import { traceValue } from './modal.js';
export interface StreamObservation { values: unknown[]; completions: number; errors: string[]; thrown: string | null; events: string[]; }
/** Observe the supported synchronous boundary directly; a silent stream is not completion. */
export function observeStream(call: () => unknown, capturePolicyFailure = true): StreamObservation {
    const o: StreamObservation = {values:[],completions:0,errors:[],thrown:null,events:[]};
    try {
        const stream = call() as {subscribe(observer: {next(v:unknown):void;error(e:unknown):void;complete():void}): unknown};
        if (!stream || typeof stream.subscribe !== 'function') throw new Failure('UnsupportedEvaluation','service','Non-observable service result');
        stream.subscribe({next(v){o.values.push(traceValue(v));o.events.push('next');},error(e){o.errors.push(String(e));o.events.push('error');},complete(){o.completions++;o.events.push('complete');}});
    } catch(e) { if(e instanceof Failure||!capturePolicyFailure)throw e; o.thrown=String(e);o.events.push('throw'); }
    if(!capturePolicyFailure&&o.errors.length)throw new Failure('UnsupportedEvaluation','service','Unexpected service stream error: '+o.errors.join(', '));
    return o;
}
export function emptyCompletion(o: StreamObservation): boolean {
    return o.values.length===0 && o.completions===1 && o.errors.length===0 && o.thrown===null && o.events.join(',')==='complete';
}
