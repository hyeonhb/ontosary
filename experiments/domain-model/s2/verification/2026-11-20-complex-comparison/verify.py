"""Replay the published first responses against the frozen v3 contract without inference."""
import argparse
import gzip
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

s2 = Path(__file__).resolve().parents[2]
record = s2 / 'results/2026-11-20-complex-comparison'
trial = s2 / 'trial/complex'
frozen = s2 / 'results/2026-11-19-complex-preparation/heldout'


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def compare_scores(actual, expected):
    files = {p.relative_to(actual) for p in actual.rglob('*') if p.is_file()}
    assert files == {p.relative_to(expected) for p in expected.rglob('*') if p.is_file()}
    for name in sorted(files):
        assert read(actual / name) == read(expected / name), name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('environment', type=Path)
    parser.add_argument('--sol', action='store_true', help='Replay the Sol batch on the same evaluator')
    args = parser.parse_args()
    batch = s2 / 'results/2026-11-20-sol-comparison' if args.sol else record
    plan = read(s2 / 'results/2026-11-19-complex-grading-v3/contract.json')
    if args.sol:
        sol_plan = read(batch/'contract.json')
        assert sol_plan['participantModel'] == 'gpt-6.2-sol'
        assert {k:v for k,v in sol_plan.items() if k not in ('participantModel','order')} == {
            k:v for k,v in plan.items() if k not in ('participantModel','order')}
        assert [{k:v for k,v in a.items() if k != 'id'} for a in sol_plan['order']] == [
            {k:v for k,v in a.items() if k != 'id'} for a in plan['order']]
        plan = sol_plan
    order = plan['order']
    assert len({a['id'] for a in order}) == len(order) == 18
    assert {p.name for p in (batch / 'attempts').iterdir()} == {a['id'] for a in order}
    with TemporaryDirectory() as directory:
        work = Path(directory)
        subprocess.run([sys.executable, trial / 'packets.py', args.source, work], check=True)
        for task in {a['task'] for a in order}:
            assert read(work / task / 'inputs/inputs.json') == read(frozen / task / 'inputs.json')
            current = read(batch / 'preflight' / (task + '.json'))
            prior = read(frozen / task / 'preflight.json')
            excluded = {'defaultPreview'}
            if args.sol:
                excluded.update(('catalogSha256','model'))
            assert current['model'] == plan['participantModel']
            assert {k:v for k,v in current.items() if k not in excluded} == {
                k:v for k,v in prior.items() if k not in excluded}
        for a in order:
            path = batch / 'attempts' / a['id']
            assert read(path / 'plan.json') == {'seconds':plan['deadlineSeconds'], 'order':[a]}
        (work / 'attempts').symlink_to(batch / 'attempts', target_is_directory=True)
        subprocess.run([sys.executable, trial / 'holdout.py', 'score', work, '--source', args.source,
                        '--environment', args.environment, '--output', work / 'score', *(['--sol'] if args.sol else [])], check=True)
        compare_scores(work / 'score', batch / 'score')
        if args.sol:
            script = s2 / 'verification/2026-11-20-sol-comparison/comparison.py'
            rebuilt = json.loads(subprocess.check_output([sys.executable, script, work / 'score']))
            assert rebuilt == read(batch / 'comparison.json'), 'Astra+A comparison differs'
    print(f"Reproduced all {len(order)} scheduled outcomes, grades and cost totals.")


if __name__ == '__main__':
    main()
