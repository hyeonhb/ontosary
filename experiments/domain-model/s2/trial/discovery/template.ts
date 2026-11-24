import {
    AST, ASTWithSource, Binary, Call, ImplicitReceiver, LiteralPrimitive, PrefixNot, PropertyRead,
    ThisReceiver, TmplAstBoundAttribute, TmplAstElement, TmplAstNode, TmplAstTemplate,
} from '@angular/compiler';
import {type Runtime} from '../../evaluation/execute.js';
import {Failure} from '../../lib/model.js';

type Scope = {detail: Runtime; order: Runtime};
type Expression = (scope: Scope) => unknown;

function unsupported(reason: string): never {
    throw new Failure('UnsupportedEvaluation', 'menu template', reason);
}

function property(receiver: unknown, name: string): unknown {
    if (!receiver || typeof receiver !== 'object' || !(name in receiver))
        unsupported('Receiver or field outside observed fixture: ' + name);
    return Reflect.get(receiver, name);
}

// Compile the Angular tree before running any case, including both sides of short-circuit operators.
function compile(node: AST): Expression {
    if (node instanceof ASTWithSource) return compile(node.ast);
    if (node instanceof LiteralPrimitive) return () => node.value;
    if (node instanceof ImplicitReceiver) return ({detail}) => detail;
    if (node instanceof PropertyRead) {
        if (node.name === 'order' && node.receiver instanceof ImplicitReceiver && !(node.receiver instanceof ThisReceiver))
            return ({order}) => order;
        const receiver = compile(node.receiver);
        return scope => property(receiver(scope), node.name);
    }
    if (node instanceof Call && node.receiver instanceof PropertyRead) {
        const member = node.receiver, receiver = compile(member.receiver), args = node.args.map(compile);
        return scope => {
            const target = receiver(scope), method = property(target, member.name);
            if (typeof method !== 'function') unsupported('Call outside observed fixture: ' + member.name);
            return Reflect.apply(method, target, args.map(arg => arg(scope)));
        };
    }
    if (node instanceof PrefixNot) {
        const operand = compile(node.expression);
        return scope => !operand(scope);
    }
    if (node instanceof Binary) {
        const left = compile(node.left), right = compile(node.right);
        switch (node.operation) {
            case '&&': return scope => left(scope) && right(scope);
            case '||': return scope => left(scope) || right(scope);
            case '===': return scope => left(scope) === right(scope);
            case '!==': return scope => left(scope) !== right(scope);
        }
    }
    return unsupported('Unobserved Angular expression: ' + node.constructor.name);
}

function dropdown(nodes: TmplAstNode[], start: number): TmplAstTemplate | undefined {
    for (const node of nodes) {
        if (node instanceof TmplAstTemplate && node.sourceSpan.start.offset === start) return node;
        if (node instanceof TmplAstTemplate || node instanceof TmplAstElement) {
            const match = dropdown(node.children, start);
            if (match) return match;
        }
    }
}

function ngIf(node: TmplAstTemplate) {
    const attr = node.templateAttrs.find(a => a.name === 'ngIf');
    if (!(attr instanceof TmplAstBoundAttribute)) unsupported('Missing Angular ngIf binding');
    return compile(attr.value);
}

export function menuBindings(baseline: string, submitted: string, nodes: TmplAstNode[]) {
    const original = /<button\s+type="button"\s+vdrDropdownItem\s+\*ngIf="[^"]+"\s+\(click\)="[^"]+"\s*>\s*<clr-icon shape="error-standard"[\s\S]*?<\/button>/g;
    const matches = [...baseline.matchAll(original)];
    if (matches.length !== 1) throw new Failure('Environment','template','Unknown baseline dropdown');
    const start = matches[0]!.index!, suffix = baseline.slice(start + matches[0]![0].length);
    if (!submitted.startsWith(baseline.slice(0,start)) || !submitted.endsWith(suffix))
        unsupported('Changes outside supported button');
    const button = submitted.slice(start,submitted.length-suffix.length);
    // Keep the structural/translation seam narrow. Binding values come from Angular, never from JS evaluation.
    const shape = /^<button\s+type="button"\s+vdrDropdownItem\s+\*ngIf="[^"]+"\s+\(click\)="[^"]+"\s*>\s*<clr-icon shape="error-standard" class="is-error"><\/clr-icon>\s*<ng-container \*ngIf="[^";]+;\s*else cancelOnly">\s*{{\s*'([\w.-]+)'\s*\|\s*translate\s*}}\s*<\/ng-container>\s*<ng-template #cancelOnly>\s*{{\s*'([\w.-]+)'\s*\|\s*translate\s*}}\s*<\/ng-template>\s*<\/button>$/;
    const labels = shape.exec(button);
    const gate = dropdown(nodes, start), element = gate?.children[0];
    if (!labels || !gate || !(element instanceof TmplAstElement)) unsupported('Unobserved menu structure');
    // The outer button uses the default then-view. Additional inputs can select a different view.
    const outerInputs = gate.templateAttrs.map(attr => attr.name);
    if (outerInputs.length !== 1 || outerInputs[0] !== 'ngIf' || gate.variables.length)
        unsupported('Unobserved outer menu bindings: ' + [...outerInputs, ...gate.variables.map(v => v.name)].join(', '));
    const condition = element.children.find(c => c instanceof TmplAstTemplate && c.tagName === 'ng-container');
    const click = element.outputs.find(e => e.name === 'click');
    if (!(condition instanceof TmplAstTemplate) || !click) unsupported('Unobserved Angular button bindings');
    return {gate:ngIf(gate), condition:ngIf(condition), click:compile(click.handler), yes:labels[1]!, no:labels[2]!};
}
