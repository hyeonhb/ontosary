// Attribute only values observed at a submitted throw or an actual RxJS subscriber's error call.
// A fixture exception passing through submitted frames is insufficient evidence.
import { AsyncLocalStorage } from 'node:async_hooks';
import ts from 'typescript';
import { Failure } from '../../../lib/model.js';

interface Site { file: string; line: number; operation: 'throw' | 'subscriber.error' }
export interface Observation {
    name: string;
    group: string;
    expected: unknown;
    actual?: unknown;
    status: 'passed' | 'failed' | 'unsupported' | 'environment-error';
    errors?: ReturnType<typeof diagnosis>[];
}
const scope = new AsyncLocalStorage<{ observation: Observation; sites: Map<unknown, Site>; caught: Set<unknown> }>();
export function inCase(observation: Observation, fn: () => void) {
    scope.run({observation, sites:new Map(), caught:new Set()}, fn);
}
function diagnosis(error: unknown, channel: 'synchronous' | 'rxjs') {
    const site = scope.getStore()?.sites.get(error);
    let message: string;
    try { message = String(error); } catch { message = 'Thrown value is not printable'; }
    if (error instanceof Failure && error.code === 'UnsupportedEvaluation')
        return {channel, kind:'unsupported-feature', message, field:error.field, status:'unsupported' as const};
    if (error instanceof Failure && error.code === 'Environment')
        return {channel, kind:'environment', message, field:error.field, status:'environment-error' as const};
    if (site) return {channel, kind:'submission', message, site, status:'failed' as const};
    return {channel, kind:'unattributed', message, status:'unsupported' as const};
}
export function recordError(error: unknown, channel: 'synchronous' | 'rxjs') {
    const diagnostic = diagnosis(error,channel);
    const row = scope.getStore()?.observation;
    if (row) {
        (row.errors ??= []).push(diagnostic);
        if (row.status !== 'environment-error' && (row.status !== 'unsupported' || diagnostic.status === 'environment-error'))
            row.status = diagnostic.status;
    }
    return diagnostic;
}

// Insert balanced expression wrappers without pretty-printing the original class or changing the
// value caught by application code. The outer evaluator hashes and typechecks the original bytes.
const marker = '__ontosaryComplexThrowSite';
const receiver = '__ontosaryComplexErrorReceiver';
const caught = '__ontosaryComplexCaught';
export function instrument(file: string, source: string): string {
    const sf = ts.createSourceFile(file,source,ts.ScriptTarget.Latest,true);
    const insertions = new Map<number,string[]>();
    function insert(at: number, text: string) {
        const parts = insertions.get(at) ?? [];
        parts.push(text);
        insertions.set(at,parts);
    }
    function visit(node: ts.Node) {
        if (ts.isIdentifier(node) && (node.text===marker || node.text===receiver || node.text===caught))
            throw new Failure('UnsupportedEvaluation',file,'Reserved evaluator binding collision');
        if (ts.isConstructorDeclaration(node) || ts.isPropertyDeclaration(node) || ts.isDecorator(node)) return;
        let target: ts.Expression | undefined, hook: string | undefined;
        // Catch/rethrow and catch/subscriber.error are transports. Preserve an existing origin,
        // and do not attribute an unmarked exception (e.g. a missing injected field) on forwarding.
        if (ts.isCatchClause(node) && node.variableDeclaration && ts.isIdentifier(node.variableDeclaration.name)) {
            insert(node.block.getStart(sf)+1, caught+'('+node.variableDeclaration.name.text+');');
        }
        if (ts.isThrowStatement(node)) { target=node.expression; hook=marker; }
        if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression) &&
            node.expression.name.text==='error' && node.expression.expression.kind!==ts.SyntaxKind.SuperKeyword && !node.questionDotToken && !ts.isOptionalChain(node.expression)) {
            target=node.expression.expression; hook=receiver;
        }
        if (target) {
            const pos = target.getStart(sf), line = sf.getLineAndCharacterOfPosition(pos).line+1;
            insert(pos,hook+'('+JSON.stringify(file)+','+line+',(');
        }
        ts.forEachChild(node,visit);
        if (target) insert(target.end,'))');
    }
    visit(sf);
    let text = '', previous = 0;
    for (const [pos,parts] of [...insertions].sort(([a],[b])=>a-b)) {
        text += source.slice(previous,pos)+parts.join('');
        previous=pos;
    }
    return text+source.slice(previous);
}
export function attributionBindings(Subscriber: Function) {
    function remember(site: Site, value: unknown) {
        // Host exceptions (including incomplete evaluator seams) can be rethrown by the submission.
        const active = scope.getStore();
        if (active && !(value instanceof Error) && !active.caught.has(value) && !active.sites.has(value))
            active.sites.set(value,site);
        return value;
    }
    return {
        [caught]: (value: unknown) => scope.getStore()?.caught.add(value),
        [marker]: (file: string,line: number,value: unknown) => remember({file,line,operation:'throw'},value),
        [receiver]: (file: string,line: number,value: unknown) => {
            if (!(value instanceof Subscriber)) return value;
            const subscriber = value as {error: (error: unknown) => void};
            const original = subscriber.error;
            return {error: (error: unknown) => original.call(subscriber,remember({file,line,operation:'subscriber.error'},error))};
        },
    };
}
