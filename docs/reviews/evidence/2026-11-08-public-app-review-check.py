"""Summarize fresh V1 runs; never modify upstream inputs or historical results.

Run prepare/run twice as documented, then pass their parent output directory and cache.
"""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

repo = Path(__file__).resolve().parents[3]
fresh = Path(sys.argv[1]).resolve()
cache = Path(sys.argv[2]).resolve()
historical = repo / 'experiments/public-app/results/2026-11-08'
manifest = json.loads((repo / 'experiments/public-app/v1/manifest.json').read_text())


def read(p):
    return json.loads(gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_bytes())


def differences(a, b, prefix=''):
    if isinstance(a, dict) and isinstance(b, dict) and a.keys() == b.keys():
        return sum((differences(a[k], b[k], f'{prefix}/{k}') for k in a), [])
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        return sum((differences(x, y, f'{prefix}/{i}') for i, (x, y) in enumerate(zip(a, b))), [])
    return [] if a == b else [prefix]


result = {'reviewedRevision': '685545fe85d67a0559e5908c6cd0fda4163a65e3',
          'method': 'Fresh immutable downloads; two runs at one new absolute cache path. No app install/build.',
          'candidates': {}}
for c in manifest['candidates']:
    name = c['id']
    a, b = fresh / f'{name}-a', fresh / f'{name}-b'
    old = historical / name
    verification = json.loads(subprocess.check_output([
        'node', str(repo / 'experiments/public-app/v1/verify.mjs'), str(a), str(b)]))
    assert read(a / 'inventory.json.gz') == read(old / 'inventory.json.gz')
    item = {'reproduction': verification, 'inventoryMatchesHistorical': True, 'observations': {}}
    for mode in ['original', 'scoped']:
        outcome = read(a / mode / 'outcome.json')
        assert outcome == read(old / mode / 'outcome.json')
        scan_path = a / mode / 'scan.json.gz'
        observation = {k: outcome[k] for k in ['status', 'analyzedFiles', 'functions', 'errorCount', 'omissions', 'groups', 'fca'] if k in outcome}
        observation['outcomeMatchesHistorical'] = True
        if scan_path.exists():
            scan = read(scan_path)
            observation['scanDifferencePathsFromHistorical'] = differences(read(old / mode / 'scan.json.gz'), scan)
            assert read(a / mode / 'program.json.gz') == read(old / mode / 'program.json.gz')
            observation['programMatchesHistorical'] = True
            if mode == 'scoped':
                counts = {f: sum(fn['evidence']['file'] == f for fn in scan['functions']) for f in c['scopedConfig']['files'] if not f.endswith('.d.ts')}
                observation['entryFunctionInventory'] = counts
                observation['entryFunctionTotal'] = sum(counts.values())
        item['observations'][mode] = observation
    search_bytes = subprocess.check_output(['node', str(repo / 'experiments/public-app/v1/search-baseline.mjs'), name,
                                           str(cache), str(a)])
    search = json.loads(search_bytes)
    assert search == read(historical / f'{name}-search.json')
    item['search'] = {'matchesHistorical': True, 'sha256': hashlib.sha256(search_bytes).hexdigest(),
                      'inputFiles': len(search['inputFiles']), 'matchedFiles': len(search['matchedFiles']),
                      'matchedLines': search['matchedLines'], 'required': len(search['requiredEvidence']),
                      'requiredFilesReached': sum(e['fileReached'] for e in search['requiredEvidence']),
                      'anchorLinesMatched': sum(e['anchorLineMatched'] for e in search['requiredEvidence'])}
    result['candidates'][name] = item
result['limits'] = {'fcaObjects': 128, 'fcaAttributes': 64,
                    'interpretation': 'Entry counts are syntax inventory under compiler errors, not successful semantic analysis/FCA. No human approval or utility measurement.'}
print(json.dumps(result, ensure_ascii=False, indent=2))
