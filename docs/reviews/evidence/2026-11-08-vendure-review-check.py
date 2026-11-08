"""Audit prepared-input replay and measure existing entry-file bounds, without FCA.

Arguments: new replay directory containing original/scoped, input-audit and
program-path-audit.json; prepared app root. Never install, build or alter inputs.
"""
import collections
import datetime
import gzip
import hashlib
import json
from pathlib import Path
import sys

repo = Path(__file__).resolve().parents[3]
fresh, app = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
saved = repo / 'experiments/public-app/results/2026-11-08-prepared'


def read(p):
    b = p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix == '.gz' else b)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


provenance = read(saved / 'provenance.json')
for name, expected in provenance['fingerprints'].items():
    assert sha(repo / name) == expected, name
for name in ['summary.json', 'dependency-files.json.gz', 'packages.json.gz', 'generated-files.json', 'links.json']:
    assert (fresh / 'input-audit' / name).read_bytes() == (saved / 'input-audit' / name).read_bytes(), name
paths = read(fresh / 'program-path-audit.json')['observations']
assert paths == read(saved / 'program-path-audit.json.gz')['observations']
for scope in ['original', 'scoped']:
    for file in (saved / scope).iterdir():
        assert file.read_bytes() == (fresh / scope / file.name).read_bytes(), f'{scope}/{file.name}'

budget = read(saved / 'budget-result.json')
stamp = datetime.datetime.fromisoformat
start, end, deadline = map(stamp, [budget['preparationStartUtc'], budget['preparationEndUtc'], budget['deadlineUtc']])
assert (deadline - start).total_seconds() == 1800
assert abs((end - start).total_seconds() - budget['elapsedSeconds']) < 0.000001
commands = []
for file in sorted(saved.glob('[0-9][0-9]-*.json')):
    c = read(file)
    a, b = stamp(c['startUtc']), stamp(c['endUtc'])
    assert start <= a <= b <= end <= deadline, file.name
    assert c['deadlineUtc'] == budget['deadlineUtc']
    assert abs((b-a).total_seconds()*1000-c['wallTimeMs']) <= 0.5
    assert abs((deadline-a).total_seconds()*1000-c['remainingAtStartMs']) <= 0.5
    assert c['signal'] is None and c['timedOut'] is False
    assert c['exitCode'] == (1 if file.name == '02-install.json' else 0)
    commands.append({'record': file.name, 'exitCode': c['exitCode'], 'wallTimeMs': c['wallTimeMs']})

manifest = read(repo / 'experiments/public-app/v1/manifest.json')
candidate = next(c for c in manifest['candidates'] if c['id'] == 'vendure')
task = read(repo / 'experiments/public-app/v1/vendure-task.json')
for e in task['evidence']:
    text = (app / e['file']).read_text()
    assert sha(app / e['file']) == e['sha256']
    assert text.count(e['anchor']) == 1
    offset = text.index(e['anchor'])
    assert len(text[:offset].encode('utf-16-le')) // 2 == e['offsetUtf16']
    assert text[:offset].count('\n') + 1 == e['line']
assert read(app / 'packages/admin-ui/ontosary.scope.json') == candidate['scopedConfig']

facts = read(fresh / 'scoped/scan.json.gz')
context = read(fresh / 'scoped/context.json.gz')
assert facts['diagnostics'] == []
# Independent reconstruction of the published attribute definition.
incidence = {}
for f in facts['functions']:
    attrs = {f'type:{t["id"]}' for t in f['referencedTypes']}
    attrs |= {f'property:{p["id"]}' for p in f['properties']}
    attrs.add('returns:' + f['returnType'])
    for c in f['conditions']:
        n = c['normalization']
        if n['status'] == 'supported':
            attrs |= {f'condition:{v["declaration"]["id"]}' for v in n['variables']}
    incidence[f['id']] = sorted(attrs)
# Recorder replaces absolute path prefixes after the core sorted its raw strings.
# Compare the mathematical sets, not their post-substitution lexical order.
assert incidence.keys() == context['incidence'].keys()
assert all(set(values) == set(context['incidence'][key]) for key, values in incidence.items())
assert len(context['objects']) == len(set(context['objects']))
assert set(incidence) == set(context['objects'])
assert len(context['attributes']) == len(set(context['attributes']))
assert {a for values in incidence.values() for a in values} == set(context['attributes'])
entries = [f for f in facts['functions'] if f['evidence']['file'] in candidate['scopedConfig']['files']]
entry_attrs = {a for f in entries for a in incidence[f['id']]}
original = read(fresh / 'original/scan.json.gz')
assert len(original['diagnostics']) == 495
assert all(d['category'] == 'Error' and d['evidence']['file'].endswith('.spec.ts') for d in original['diagnostics'])

result = {
    'reviewedRevision': 'b4449c373eb97f68373cc3848623f5f8ba6e1b87',
    'scope': 'Independent review observations in the existing installed cache; no reinstall/build, no FCA enumeration or new task selection.',
    'reproduction': read(fresh / 'reproduction.json'),
    'provenanceFingerprintsVerified': len(provenance['fingerprints']),
    'inputAuditArtifactsByteIdentical': 5,
    'inputAuditSummary': read(fresh / 'input-audit/summary.json'),
    'taskAnchorsVerified': len(task['evidence']),
    'originalConfig': {'diagnostics': len(original['diagnostics']), 'allInSpecs': True,
                       'codes': dict(collections.Counter(str(d['code']) for d in original['diagnostics']))},
    'programPathAudit': {s: {k: v for k, v in o.items() if k != 'files'} for s, o in paths.items()},
    'budgetRecordConsistent': True,
    'reportedElapsedSeconds': budget['elapsedSeconds'],
    'commands': commands,
    'contextReconstructedFromFacts': True,
    'fullContext': {'objects': len(context['objects']), 'attributes': len(context['attributes']),
                    'attributeKinds': dict(collections.Counter(a.split(':', 1)[0] for a in context['attributes']))},
    'existingEntryInventory': {'functions': len(entries), 'distinctAttributes': len(entry_attrs),
                               'attributeKinds': dict(collections.Counter(a.split(':', 1)[0] for a in sorted(entry_attrs)))},
    'interpretation': '129 entry functions and 314 attributes also exceed both defaults. This is a size diagnostic of already-declared roots, not a selected successful FCA experiment or proof of utility.'
}
print(json.dumps(result, ensure_ascii=False, indent=2))
