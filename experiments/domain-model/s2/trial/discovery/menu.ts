import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {parseTemplate, VERSION} from '@angular/compiler';
import {Failure} from '../../lib/model.js';
import {attributionBindings, inCase, instrument, recordError, type Observation} from '../complex/evaluator/errors.js';
import {menuBindings} from './template.js';
import {createRequire} from 'node:module';
import {mappings} from '../../evaluation/behavior.js';
import {executor, type Runtime} from '../../evaluation/execute.js';
import {openEnvironment} from '../../evaluation/evaluate.js';
import {checkSubmission, manifest, readSubmission, sourceView} from '../../evaluation/submission.js';
import {hash, stable} from '../../lib/analysis-session.js';
import {Control} from '../complex/evaluator/dialogs.js';

const [source, root, output, repo] = process.argv.slice(2);
if (!source || !root || !output || !repo) throw Error("Expected source, environment, output, repository");
const html = mappings[0]!.file.replace(/\.ts$/, '.html');
const locale = 'packages/admin-ui/src/lib/static/i18n-messages/en.json';
const cancel = 'Cancel order or items', refund = 'Refund & cancel order';
const history = (state: string, total: number) => ({state, total});
const pay = (amount: number, refunds: ReturnType<typeof history>[] = [], state = 'Settled') => ({amount, refunds, state});
const exhausted = pay(100, [history('Settled', 60), history('Settled', 40)]);
const remaining = pay(70, [history('Pending', 40)]);
const order = (payments: ReturnType<typeof pay>[], state = 'PaymentSettled', active = false, type = 'Regular',
    nextStates = ['Cancelled']) => ({payments, state, active, type, nextStates});
const cases = [
    {name: 'fully refunded', order: order([exhausted]), label: cancel, modal: 'CancelOrderDialogComponent'},
    {name: 'one positive after exhausted', order: order([exhausted, remaining]), label: refund, modal: 'RefundOrderDialogComponent'},
    {name: 'positive before exhausted', order: order([remaining, exhausted]), label: refund, modal: 'RefundOrderDialogComponent'},
    {name: 'pending consumes remaining amount', order: order([pay(80,[history('Settled',50),history('Pending',30)])]), label: cancel, modal: 'CancelOrderDialogComponent'},
    {name: 'failed refund leaves balance', order: order([pay(100,[history('Settled',70),history('Failed',30)])]), label: refund, modal: 'RefundOrderDialogComponent'},
    {name: 'authorized only', order: order([pay(50, [], 'Authorized')], 'PaymentAuthorized'), label: cancel, modal: 'CancelOrderDialogComponent'},
    {name: 'authorized with settled share', order: order([pay(30), pay(100, [], 'Authorized')], 'PaymentAuthorized'), label: refund, modal: 'CancelOrderDialogComponent'},
    {name: 'active arranging part payment', order: order([pay(30)], 'ArrangingPayment', true), label: refund, modal: 'CancelOrderDialogComponent'},
    {name: 'active adding items', order: order([], 'AddingItems', true), label: cancel, modal: 'CancelOrderDialogComponent'},
    {name: 'aggregate hidden', order: order([remaining], 'PaymentSettled', false, 'Aggregate'), label: null, modal: null},
    {name: 'no cancelled transition', order: order([exhausted], 'Cancelled', false, 'Regular', []), label: null, modal: null},
];

const env = openEnvironment(root,repo), sources = readSubmission(source);
const actualManifest = manifest(sources);
const types = new Map(sources);
// The original TS Program does not consume HTML. Validate and interpret the submitted template independently.
types.set(html,env.baseline.get(html)!);
const checked = checkSubmission({root,config:env.config,baseline:env.baseline,sources:types,
    allowedChange:f=>f.startsWith('packages/admin-ui/src/') && f.endsWith('.ts')});
const used: Record<string,string> = {};
const view = sourceView(sources,(file,sha)=>{used[file]=sha;});
const template = view.read(html);
const parsed = parseTemplate(template,html);
const compilerLock = JSON.parse(env.baseline.get('package-lock.json')!.toString()).packages['node_modules/@angular/compiler'];
if (VERSION.full !== compilerLock.version) throw new Error('Evaluator compiler differs from the pinned Vendure lock');
const compilerFile = createRequire(import.meta.url).resolve('@angular/compiler');
// Angular can carry the same binding diagnostic across many later template spans.
const diagnostics = new Map<string, {file:string; line:number; column:number; message:string; occurrences:number}>();
for (const error of parsed.errors ?? []) {
    const existing = diagnostics.get(error.msg);
    if (existing) existing.occurrences++;
    else diagnostics.set(error.msg, {file:html,line:error.span.start.line+1,column:error.span.start.col+1,
        message:error.msg,occurrences:1});
}
const parser = {version:VERSION.full,compilerIntegrity:compilerLock.integrity,compilerSha256:hash(fs.readFileSync(compilerFile)),
    templateSha256:used[html],diagnostics:[...diagnostics.values()]};
type MenuCase = Observation & {passed:boolean; errorPhase?:string};
const observations: MenuCase[] = [];
let setupError: ReturnType<typeof recordError> | undefined;
try {
    if (checked.status === 'passed' && !diagnostics.size) {
        const menu = menuBindings(env.baseline.get(html)!.toString(),template,parsed.nodes);
        const translations = JSON.parse(view.read(locale));
        const rx = createRequire(path.join(root,'package.json'))('rxjs');
        const engine = executor(root,mappings,{marker:(s:string)=>s,gql:()=>'', ORDER_DETAIL_FRAGMENT:'',
            FormControl:Control, Validators:{min:()=>null,max:()=>null}, ...attributionBindings(rx.Subscriber),
            summate:(rows:Runtime[],key:string)=>rows.reduce((total,row)=>total+Number(row[key]),0)},root,
            {has:view.has, read:file=>instrument(file,view.read(file))});
        const dialogs = ['CancelOrderDialogComponent','RefundOrderDialogComponent'];
        const identities = dialogs.map(name=>engine.component(name));
        for (const test of cases) {
            const input = structuredClone(test.order);
            const opened: string[] = [];
            const expectedOpened = test.modal ? [test.modal] : [];
            const row: MenuCase = {name:test.name,group:'menu',status:'passed',
                expected:{label:test.label,opened:expectedOpened},passed:false};
            observations.push(row);
            inCase(row, () => {
                let label: string | null = null;
                let phase = 'component';
                try {
                    const detail = engine.instance('OrderDetailComponent');
                    Object.defineProperty(detail, 'detailForm', {get() {
                        throw new Failure('Environment','detailForm','Angular form initialization is outside the menu fixture');
                    }});
                    detail.modalService = {fromComponent:(component:Function, options:{locals:{order:unknown}})=>{
                        opened.push(options.locals.order === input ? dialogs[identities.indexOf(component)] ?? 'unknown dialog' : 'wrong order');
                        return rx.EMPTY;
                    }};
                    // Retain the per-expression timeout when a binding calls a submitted TS method.
                    const evaluate = (fn:typeof menu.gate) => vm.runInNewContext('run()', {run:()=>fn({detail,order:input})},{timeout:1000});
                    phase = 'visibility';
                    if (evaluate(menu.gate)) {
                        phase = 'label';
                        const key = evaluate(menu.condition) ? menu.yes : menu.no;
                        label = key.split('.').reduce((value,k)=>value?.[k],translations) ?? key;
                        phase = 'click';
                        evaluate(menu.click);
                    }
                    row.passed = label===test.label && JSON.stringify(opened)===JSON.stringify(expectedOpened);
                    row.status = row.passed ? 'passed' : 'failed';
                } catch (error) {
                    row.errorPhase = phase;
                    recordError(error,'synchronous');
                }
                row.actual = {label,opened};
            });
        }
    }
} catch (error) { setupError = recordError(error,'synchronous'); }
env.assertUnchanged();
const bound = Object.entries(used).every(([file,sha]) => actualManifest[file] === sha &&
    (!file.endsWith('.ts') || checked.checkedFiles.some(f=>f.file===file && f.sha256===sha)));
function outcome() {
    if (diagnostics.size || checked.status === 'failed') return 'failed';
    if (checked.status !== 'passed' || !bound) return 'unsupported';
    if (setupError) return setupError.status;
    // Preserve a proven failure even if another case is unobservable.
    for (const status of ['failed','environment-error','unsupported'] as const)
        if (observations.some(row=>row.status===status)) return status;
    return observations.length === cases.length ? 'passed' : 'unsupported';
}
fs.writeFileSync(output,JSON.stringify({status:outcome(),parser,setupError,typecheck:checked.status,diagnostics:checked.diagnostics,
    unsupportedChanges:checked.unsupported,programFiles:checked.cost.programFiles,submissionId:hash(stable(actualManifest)),
    environmentId:hash(stable(env.fingerprints)),bound,used,observations},null,2)+'\n',{flag:'wx'});
