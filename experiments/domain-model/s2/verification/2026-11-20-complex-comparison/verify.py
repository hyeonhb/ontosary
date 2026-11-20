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
    args = parser.parse_args()
    plan = read(s2 / 'results/2026-11-19-complex-grading-v3/contract.json')
    order = plan['order']
    assert {p.name for p in (record / 'attempts').iterdir()} == {a['id'] for a in order}
    with TemporaryDirectory() as directory:
        work = Path(directory)
        subprocess.run([sys.executable, trial / 'packets.py', args.source, work], check=True)
        for task in {a['task'] for a in order}:
            assert read(work / task / 'inputs/inputs.json') == read(frozen / task / 'inputs.json')
            current = read(record / 'preflight' / (task + '.json'))
            prior = read(frozen / task / 'preflight.json')
            assert {k:v for k,v in current.items() if k != 'defaultPreview'} == {
                k:v for k,v in prior.items() if k != 'defaultPreview'}
        for a in order:
            path = record / 'attempts' / a['id']
            assert read(path / 'plan.json') == {'seconds':plan['deadlineSeconds'], 'order':[a]}
        (work / 'attempts').symlink_to(record / 'attempts', target_is_directory=True)
        subprocess.run([sys.executable, trial / 'holdout.py', 'score', work, '--source', args.source,
                        '--environment', args.environment, '--output', work / 'score'], check=True)
        compare_scores(work / 'score', record / 'score')
    print(f"Reproduced all {len(order)} scheduled outcomes, grades and cost totals.")


if __name__ == '__main__':
    main()
