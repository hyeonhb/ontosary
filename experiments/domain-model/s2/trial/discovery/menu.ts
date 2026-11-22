import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
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

// Recognize the original dropdown structure with replaceable Angular bindings and translation keys.
// A different template structure needs another interpreter or an Angular rendering review.
function bindings(baseline: string, submitted: string) {
    const original = /<button\s+type="button"\s+vdrDropdownItem\s+\*ngIf="[^"]+"\s+\(click\)="[^"]+"\s*>\s*<clr-icon shape="error-standard"[\s\S]*?<\/button>/g;
    const matches = [...baseline.matchAll(original)];
    if (matches.length !== 1) throw Error('Unknown baseline dropdown');
    const start = matches[0]!.index!, end = start + matches[0]![0].length;
    const suffix = baseline.slice(end);
    if (!submitted.startsWith(baseline.slice(0,start)) || !submitted.endsWith(suffix)) throw Error('Changes outside supported button');
    const button = submitted.slice(start,submitted.length-suffix.length);
    const pattern = /^<button\s+type="button"\s+vdrDropdownItem\s+\*ngIf="([^"]+)"\s+\(click\)="([^"]+)"\s*>\s*<clr-icon shape="error-standard" class="is-error"><\/clr-icon>\s*<ng-container \*ngIf="([^";]+);\s*else (\w+)">\s*{{\s*'([^']+)'\s*\|\s*translate\s*}}\s*<\/ng-container>\s*<ng-template #(\w+)>\s*{{\s*'([^']+)'\s*\|\s*translate\s*}}\s*<\/ng-template>\s*<\/button>$/;
    const m = pattern.exec(button);
    if (!m || m[4] !== m[6]) throw Error('Unsupported menu structure');
    return {gate:m[1]!, click:m[2]!, condition:m[3]!, yes:m[5]!, no:m[7]!};
}

const env = openEnvironment(root,repo), sources = readSubmission(source);
const actualManifest = manifest(sources);
const types = new Map(sources);
// The original TS Program does not consume HTML. Validate and interpret the submitted template independently.
types.set(html,env.baseline.get(html)!);
const checked = checkSubmission({root,config:env.config,baseline:env.baseline,sources:types,
    allowedChange:f=>f.startsWith('packages/admin-ui/src/') && f.endsWith('.ts')});
const used: Record<string,string> = {};
const view = sourceView(sources,(file,sha)=>{used[file]=sha;});
const observations = [];
let unsupported: string | undefined;
try {
    if (checked.status === 'passed') {
        const menu = bindings(env.baseline.get(html)!.toString(),view.read(html));
        const translations = JSON.parse(view.read(locale));
        const rx = createRequire(path.join(root,'package.json'))('rxjs');
        const engine = executor(root,mappings,{marker:(s:string)=>s,gql:()=>'', ORDER_DETAIL_FRAGMENT:'',
            FormControl:Control, Validators:{min:()=>null,max:()=>null},
            summate:(rows:Runtime[],key:string)=>rows.reduce((total,row)=>total+Number(row[key]),0)},root,view);
        const dialogs = ['CancelOrderDialogComponent','RefundOrderDialogComponent'];
        const identities = dialogs.map(name=>engine.component(name));
        for (const test of cases) {
            const input = structuredClone(test.order);
            const opened: string[] = [];
            const detail = engine.instance('OrderDetailComponent');
            detail.modalService = {fromComponent:(component:Function, options:{locals:{order:unknown}})=>{
                opened.push(options.locals.order === input ? dialogs[identities.indexOf(component)] ?? 'unknown dialog' : 'wrong order');
                return rx.EMPTY;
            }};
            const evaluate = (expr:string)=>vm.runInNewContext('with (detail) { ('+expr+') }',{detail,order:input},{timeout:1000});
            let label = null;
            if (evaluate(menu.gate)) {
                const key = evaluate(menu.condition) ? menu.yes : menu.no;
                label = key.split('.').reduce((value,k)=>value?.[k],translations) ?? key;
                evaluate(menu.click);
            }
            const expectedOpened = test.modal ? [test.modal] : [];
            observations.push({name:test.name,expected:{label:test.label,opened:expectedOpened},actual:{label,opened},
                passed:label===test.label && JSON.stringify(opened)===JSON.stringify(expectedOpened)});
        }
    }
} catch (e) { unsupported = String(e); }
env.assertUnchanged();
const bound = Object.entries(used).every(([file,sha]) => actualManifest[file] === sha &&
    (!file.endsWith('.ts') || checked.checkedFiles.some(f=>f.file===file && f.sha256===sha)));
const status = checked.status !== 'passed' ? checked.status : unsupported || !bound ? 'unsupported' :
    observations.length === cases.length && observations.every(r=>r.passed) ? 'passed' : 'failed';
fs.writeFileSync(output,JSON.stringify({status,unsupported,typecheck:checked.status,diagnostics:checked.diagnostics,
    unsupportedChanges:checked.unsupported,programFiles:checked.cost.programFiles,submissionId:hash(stable(actualManifest)),
    environmentId:hash(stable(env.fingerprints)),bound,used,observations},null,2)+'\n',{flag:'wx'});
