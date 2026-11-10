"""Independent structural/line coverage audit; does not certify natural-language meaning."""
import hashlib
import json
import sys
from pathlib import Path
root = Path(sys.argv[1])
def leaves(value, pointer=''):
    if isinstance(value, (dict, list)) and value:
        pairs = value.items() if isinstance(value, dict) else enumerate(value)
        return [row for k, v in pairs for row in leaves(v, pointer + '/' + str(k).replace('~', '~0').replace('/', '~1'))]
    return [(pointer, value)]
def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
rows = []
for view in sorted((root / 'B/views').glob('*.json')):
    expected = dict(leaves(json.loads(view.read_text())))
    units = json.loads((root / 'evaluator/parity' / view.name).read_text())
    assert len({u['id'] for u in units}) == len(units)
    assert len(units) == len(expected)
    assert {u['pointer'] for u in units} == set(expected)
    for unit in units:
        assert unit['view'] == 'B/views/' + view.name
        assert unit['id'] == view.stem + '#' + unit['pointer']
        assert encoded(unit['value']) == encoded(expected[unit['pointer']])
        target = unit['C']
        text = '\n'.join((root / target['file']).read_text().split('\n')[target['startLine'] - 1:target['endLine']])
        assert hashlib.sha256(text.encode()).hexdigest() == target['sha256']
    rows.append({'view': view.name, 'units': len(units), 'sourceValuesAndExactCIntervalsMatch': True})
print(json.dumps({'views': rows, 'totalUnits': sum(x['units'] for x in rows), 'meaningProven': False}, indent=2))
