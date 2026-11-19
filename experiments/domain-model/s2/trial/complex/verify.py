"""Rebuild packets, verify the seal and optionally replay the complete-root controls without inference."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
s2 = here.parents[1]
record = s2/'results/2026-11-19-complex-preparation'
parser = argparse.ArgumentParser()
parser.add_argument('source', type=Path)
parser.add_argument('work', type=Path, help='Fresh scratch directory')
parser.add_argument('--environment', type=Path, help='Also replay nine controls and the sealed probe')
args = parser.parse_args()
args.work.mkdir(parents=True,exist_ok=False)

def read(path):
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes())

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(script,*argv):
    subprocess.run([sys.executable,str(script),*map(str,argv)],check=True)

plan = read(record/'heldout/contract.json')
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
    controls = record/'controls'/task
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
    assert read(args.work/'probe-replay/submission/evaluation.json.gz')==read(probe/'score/evaluation.json.gz')

material=s2/'results/2026-11-10-trial-preparation'
parity=json.loads(subprocess.check_output([sys.executable,str(s2/'verification/2026-11-10-trial-preparation/audit-parity.py'),str(material)]))
assert parity['totalUnits']==1511
for file in (material/'B/views').glob('evidence-*.json'):
    ref=read(file)['value']
    source=args.source/ref['file']
    assert digest(source)==ref['sha256']
    text=source.read_text().encode('utf-16-le')[ref['offset']*2:ref['end']*2].decode('utf-16-le')
    assert text==ref['text']
print('Verified packets, comparison schedule, controls, probe seal, 1511 leaf correspondences and 30 source anchors.')
