"""Compare first-patch quality and all observed costs with the historical Astra+A batch."""
from decimal import Decimal
from pathlib import Path
import argparse
import gzip
import json

s2 = Path(__file__).resolve().parents[2]
astra = s2 / 'results/2026-11-20-complex-comparison'
sol = s2 / 'results/2026-11-20-sol-comparison'
rates = {'Sol': (50, Decimal('2.5'), 250), 'Astra': (200, 10, 1000)}


def arm(summary, condition, model):
    rows = [row for row in summary['attempts'] if row['condition'] == condition]
    total = summary['allScheduled'][condition]
    cost = None
    if all(row['usage'] and all(key in row['usage'] for key in
           ('input_tokens', 'cached_input_tokens', 'output_tokens')) for row in rows):
        regular, cached, output = rates[model]
        charge = sum((r['usage']['input_tokens'] - r['usage']['cached_input_tokens']) * regular
                     + r['usage']['cached_input_tokens'] * cached + r['usage']['output_tokens'] * output
                     for r in rows)
        cost = float(charge / Decimal(1000000))
    return {'scheduled': len(rows), 'successes': total['successes'],
            'successesByTask': {task: sum(r['success'] for r in rows if r['task'] == task)
                                for task in ('quantity', 'refresh')},
            **{key: total[key]['total'] for key in ('input_tokens', 'output_tokens', 'elapsedSeconds')},
            'standardRateEquivalentCredits': cost}


def paired_cases(rows, score):
    """Count observed A failures passing under B/C at the same task and repeat."""
    observations = {}
    for row in rows:
        case_map = None
        if row['status'] in ('passed', 'behavior-failed'):
            path = score / row['id'] / 'submission/evaluation.json.gz'
            report = json.loads(gzip.decompress(path.read_bytes()))
            assert report['sourceBinding'] and report['typecheck']['status'] == 'passed'
            case_map = {(c['group'], c['name']): c['status'] for c in report['behavior']['cases']}
        observations.setdefault((row['task'], row['repeat']), {})[row['condition']] = case_map

    pairs = []
    for (task, repeat), conditions in sorted(observations.items()):
        for other in 'BC':
            a, b = conditions['A'], conditions[other]
            comparable = a is not None and b is not None
            recovered = None
            if comparable:
                assert a.keys() == b.keys()
                recovered = [{'group': group, 'case': name} for (group, name), status in a.items()
                             if status == 'failed' and b[group, name] == 'passed']
            pairs.append({'task': task, 'repeat': repeat, 'other': other,
                          'comparedCases': len(a) if comparable else 0, 'aFailedOtherPassed': recovered})
    return pairs


def comparison(sol_summary, astra_summary, score):
    baseline = arm(astra_summary, 'A', 'Astra')
    arms = {condition: arm(sol_summary, condition, 'Sol') for condition in 'ABC'}
    differences = {}
    for condition, row in arms.items():
        differences[condition] = {key: round(row[key] - baseline[key], 8)
                                  if row[key] is not None else None
                                  for key in ('successes','input_tokens','output_tokens','elapsedSeconds',
                                              'standardRateEquivalentCredits')}
    return {'rateCardDate': '2026-11-20', 'rateCard': 'https://learn.chatgpt.com/docs/pricing',
            'unit': 'Standard-speed Codex credits per million tokens; rate equivalent, not subscription charges',
            'astraA': baseline, 'sol': arms, 'solMinusAstraA': differences,
            'withinSol': sol_summary['effects'],
            'pairedBusinessCases': paired_cases(sol_summary['attempts'], score)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('score', nargs='?', type=Path, default=sol/'score')
    score = parser.parse_args().score
    print(json.dumps(comparison(json.loads((score/'summary.json').read_bytes()),
                                json.loads((astra/'score/summary.json').read_bytes()), score), indent=2))
