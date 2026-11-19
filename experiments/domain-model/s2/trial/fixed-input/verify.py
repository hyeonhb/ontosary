"""Verify sealed inputs, one-turn events and complete-root scores without a model call."""
import gzip
import hashlib
import json
import sys
from pathlib import Path

evidence, packets = (Path(arg) for arg in sys.argv[1:])
def read(name):
    return json.loads((evidence / name).read_bytes())

manifest = read('inputs.json')
assert json.loads((packets / 'inputs.json').read_bytes()) == manifest
preflight = read('preflight.json')
assert preflight['defaultPreview']['tools'] and not preflight['configuredPreview']['tools']
assert not preflight['localRequest']['tools']
oracle = read('calibration.json')
baseline_manifest = None
for key, expected in [('baseline', (16, 6)), ('reference', (16, 36))]:
    raw = gzip.decompress((evidence / (key + '.json.gz')).read_bytes())
    assert hashlib.sha256(raw).hexdigest() == oracle[key]['rawSha256']
    report = json.loads(raw)
    assert report['inputMode'] == 'complete-root' and report['sourceBinding'] and report['typecheck']['status'] == 'passed'
    cases = report['behavior']['cases']
    assert len(cases) == 52 and tuple(sum(c['category'] == cat and c['status'] == 'passed' for c in cases)
        for cat in ('preservation', 'draft-requirement')) == expected
    if key == 'baseline':
        baseline_manifest = report['typecheck']['submittedManifest']

results = read('results.json')
order = read('plan.json')['order']
assert sorted(item['condition'] for item in order) == list('ABC') and len({i['id'] for i in order}) == 3
assert all(baseline_manifest[path] == digest for path, digest in manifest['sourceFiles'].items())
threads = set()
for item in order:
    arm, run = item['condition'], item['id']
    seal = read(run + '/seal.json')
    data = (packets / (arm + '.txt')).read_bytes()
    assert hashlib.sha256(data).hexdigest() == manifest['conditions'][arm]['sha256'] == seal['packetSha256'] == preflight['localRequest']['packetHashes'][arm]
    assert data.startswith((packets / 'A.txt').read_bytes())
    events = (evidence / run / 'events.jsonl').read_bytes()
    assert hashlib.sha256(events).hexdigest() == seal['eventsSha256']
    rows = list(map(json.loads, events.splitlines()))
    assert [r['type'] for r in rows] == ['thread.started', 'turn.started', 'item.completed', 'turn.completed']
    threads.add(rows[0]['thread_id'])
    answer = (evidence / run / 'answer.txt').read_bytes()
    assert rows[2]['item']['type'] == 'agent_message' and rows[2]['item']['text'].rstrip('\n') == answer.decode().rstrip('\n')
    grade = read(run + '/grade.json')
    assert hashlib.sha256(answer).hexdigest() == seal['answerSha256'] == grade['responseSha256']
    assert rows[3]['usage'] == results[arm]['usage'] and not seal['timeout'] and seal['exitCode'] == 0
    report = json.loads(gzip.decompress((evidence / run / 'evaluation.json.gz').read_bytes()))
    assert grade['applied'] and report['evaluatorId'] == oracle['baseline']['evaluatorId'] and report['inputMode'] == 'complete-root'
    assert report['typecheck']['submissionId'] == results[arm]['submissionId'] and report['sourceBinding']
    assert report['overall'] == results[arm]['overall'] and report['typecheck']['status'] == results[arm]['typecheck']
    for category, total in [('preservation', 16), ('draft-requirement', 36)]:
        cases = [c for c in report['behavior']['cases'] if c['category'] == category]
        assert len(cases) == total and sum(c['status'] == 'passed' for c in cases) == results[arm][category]
assert len(threads) == 3
print('Verified 3 packets, 3 distinct single-turn seals, 2 calibrations and 3 complete-root scores.')
