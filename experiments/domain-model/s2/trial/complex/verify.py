"""Rebuild packets, verify the seal and optionally replay the complete-root controls without inference."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from grading_regressions import examples, regression
from holdout import scoring_evidence

here = Path(__file__).resolve().parent
s2 = here.parents[1]
record = s2/'results/2026-11-19-complex-preparation'
parser = argparse.ArgumentParser()
parser.add_argument('source', type=Path)
parser.add_argument('work', type=Path, help='Fresh scratch directory')
parser.add_argument('--environment', type=Path, help='Also replay nine controls, the sealed probe and all grading regressions')
args = parser.parse_args()
args.work.mkdir(parents=True,exist_ok=False)

def read(path):
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes())

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(script,*argv):
    subprocess.run([sys.executable,str(script),*map(str,argv)],check=True)

original_plan = read(record/'heldout/contract.json')
plan = read(scoring_evidence/'contract.json')
assert {k:v for k,v in plan.items() if k!='evaluation'} == {k:v for k,v in original_plan.items() if k!='evaluation'}
prior = s2/'results/2026-11-19-complex-grading-v2'
for relative in [*sorted((prior/'controls').rglob('evaluation.json.gz')),
                 *sorted((prior/'regressions').rglob('evaluation.json.gz')),
                 prior/'probe/submission/evaluation.json.gz']:
    updated = scoring_evidence/relative.relative_to(prior)
    metadata = {'contractVersion','evaluatorId','fingerprint'}
    assert {k:v for k,v in read(relative).items() if k not in metadata} == {
        k:v for k,v in read(updated).items() if k not in metadata}, relative
    previous_cost = relative.with_name('cost.json')
    if previous_cost.is_file():
        assert read(previous_cost)==read(updated.with_name('cost.json')), relative

# Bind the two preserved UI entry points to the HTML at the frozen Vendure revision.
template = args.source/'packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.html'
assert digest(template)=='9ea4b2b1adf7cd7f5907e1438d5ba9ed837f2679ae02402908e3c3db1a483ef5'
for name in ('hidden','throw'):
    directory = prior/'v1-review-replay'/name
    assert read(directory/'grade.json')['responseSha256']==digest(here/'evaluator/controls'/f'quantity-{name}.patch')
    previous = read(directory/'evaluation.json.gz')
    assert previous['contractVersion']=='s2-complex-v1'
    changes = [c['status'] for c in previous['behavior']['cases'] if c['group']=='change']
    assert changes==(['passed']*3 if name=='hidden' else ['unsupported']*3)
    assert all(c['status']=='passed' for c in previous['behavior']['cases'] if c['group']=='preserve')
for name,task,patch,old_status in (
        ('wrapped-seam','quantity','wrapped-seam','behavior-failed'),
        ('rxjs-optional','refresh','rx-optional','unsupported'),
        ('rxjs-bracket','refresh','rx-bracket','unsupported')):
    replay = scoring_evidence/'v2-review-replay'/name
    assert read(replay/'grade.json')['responseSha256']==digest(here/'evaluator/controls'/f'{task}-{patch}.patch')
    assert read(replay/'evaluation.json.gz')['evaluatorId']==read(prior/'contract.json')['evaluation'][task]['evaluatorId']
    assert read(replay/'cost.json')['scoredAttempt']['status']==old_status
order = plan['order']
assert len(order)==len({a['id'] for a in order})==plan['scheduledAttempts']==18
for t in ('quantity','refresh'):
    blocks = [[a['condition'] for a in order if a['task']==t and a['repeat']==i] for i in (1,2,3)]
    assert all(sorted(block)==list('ABC') for block in blocks)
    assert all(sorted(pos)==list('ABC') for pos in zip(*blocks))
run(here/'packets.py',args.source,args.work)
old = read(s2/'results/2026-11-18-fixed-input-pilot/inputs.json')
for task in ('allocation','quantity','refresh'):
    frozen = record/('probe' if task=='allocation' else 'heldout/'+task)
    manifest = read(frozen/'inputs.json')
    inspection = read(frozen/'preflight.json')
    assert manifest == read(args.work/task/'inputs/inputs.json')
    assert manifest['sourceFiles']==old['sourceFiles'] and manifest['revision']==old['revision']
    for arm in 'ABC':
        inp = args.work/task/'inputs'/f'{arm}.txt'
        assert digest(inp)==manifest['conditions'][arm]['sha256']==inspection['localRequest']['packetHashes'][arm]
        assert manifest['conditions'][arm]['materials']==old['conditions'][arm]['materials']
        assert inp.stat().st_size+len(inspection['system'].encode())+4096+49152 < plan['effectiveContextTokens']
    assert inspection['localRequest']['tools']==inspection['configuredPreview']['tools']==[]
    if task in plan['evaluation']:
        assert digest(frozen/'inputs.json')==plan['inputManifestsSha256'][task]
    controls = scoring_evidence/'controls'/task
    if args.environment:
        run(here/'calibrate.py',task,args.source,args.environment,args.work/task/'controls')
    for control in ('baseline','partial','reference'):
        original = read(controls/control/'evaluation.json.gz')
        assert original['sourceBinding'] and original['typecheck']['status']=='passed'
        assert original['overall']==('passed' if control=='reference' else 'failed')
        if task in plan['evaluation']:
            assert all(original[k]==v for k,v in plan['evaluation'][task].items())
        if args.environment:
            assert original==read(args.work/task/'controls'/control/'evaluation.json.gz')

probe = record/'probe'
attempt, = read(probe/'plan.json')['order']
assert attempt['condition']=='A'
directory=probe/attempt['id']
seal=read(directory/'seal.json')
events=list(map(json.loads,(directory/'events.jsonl').read_bytes().splitlines()))
assert [e['type'] for e in events]==['thread.started','turn.started','item.completed','turn.completed']
assert events[2]['item']['type']=='agent_message' and events[2]['item']['text'].rstrip('\n')==(directory/'answer.txt').read_text().rstrip('\n')
assert digest(directory/'answer.txt')==seal['answerSha256']==read(probe/'score/grade.json')['responseSha256']
assert digest(directory/'events.jsonl')==seal['eventsSha256'] and not seal['timeout'] and seal['exitCode']==0
assert seal['packetSha256']==read(probe/'inputs.json')['conditions']['A']['sha256']
assert read(probe/'score/evaluation.json.gz')['overall']=='passed'
if args.environment:
    run(here/'calibrate.py','allocation',args.source,args.environment,args.work/'probe-replay','--answer',directory/'answer.txt')
    assert read(args.work/'probe-replay/submission/evaluation.json.gz')==read(scoring_evidence/'probe/submission/evaluation.json.gz')

# The three spellings must identify the very same emitted value, source location and cases.
reports = [read(scoring_evidence/'regressions'/name/'evaluation.json.gz')['behavior']
           for name in ('rxjs-notification','rxjs-optional','rxjs-bracket')]
assert reports[0]==reports[1]==reports[2]
for name,task,patch,status,_ in examples:
    saved = scoring_evidence/'regressions'/name
    assert read(saved/'grade.json')['responseSha256']==digest(here/'evaluator/controls'/f'{task}-{patch}.patch')
    assert read(saved/'cost.json')['scoredAttempt']['status']==status
    if args.environment:
        replay = args.work/'regressions'/name
        regression(name,args.source,args.environment,args.work,replay)
        for file in ('grade.json','evaluation.json.gz','cost.json'):
            assert read(replay/file)==read(saved/file), (name,file)

material=s2/'results/2026-11-10-trial-preparation'
parity=json.loads(subprocess.check_output([sys.executable,str(s2/'verification/2026-11-10-trial-preparation/audit-parity.py'),str(material)]))
assert parity['totalUnits']==1511
for file in (material/'B/views').glob('evidence-*.json'):
    ref=read(file)['value']
    source=args.source/ref['file']
    assert digest(source)==ref['sha256']
    text=source.read_text().encode('utf-16-le')[ref['offset']*2:ref['end']*2].decode('utf-16-le')
    assert text==ref['text']
print(f'Verified packets, comparison schedule, v3 controls, {len(examples)} regressions, probe seal, 1511 leaf correspondences and 30 source anchors.')
