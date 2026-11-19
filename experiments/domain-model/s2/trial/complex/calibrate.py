"""Replay controls or a sealed response. Never starts a model."""
import argparse
import gzip
import json
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument('task', choices=['allocation','quantity','refresh'])
parser.add_argument('baseline', type=Path)
parser.add_argument('environment', type=Path)
parser.add_argument('output', type=Path)
parser.add_argument('--answer', type=Path, help='Grade only this sealed response')
args = parser.parse_args()
here = Path(__file__).resolve().parent
fixed = here.parent/'fixed-input'
args.output.mkdir(parents=True, exist_ok=False)
controls = ['submission'] if args.answer else ['baseline','reference','partial']
for control in controls:
    dest = args.output/control
    if control == 'baseline':
        dest.mkdir()
        cmd = [fixed/'evaluate.py',args.baseline,args.environment,dest/'evaluation.json',args.task]
    else:
        answer = args.answer or here/'evaluator/controls'/f'{args.task}-{control}.patch'
        cmd = [fixed/'grade.py',answer,args.baseline,args.environment,dest,args.task]
    subprocess.run([sys.executable,*map(str,cmd)],check=True)
    raw = dest/'evaluation.json'
    if not raw.exists():
        if control != 'submission':
            raise ValueError(f'Control {control} did not apply')
        continue
    report = json.loads(raw.read_bytes())
    if control != 'submission':
        assert report['sourceBinding'] and report['typecheck']['status']=='passed' and report['inputMode']=='complete-root'
        cases = report['behavior']['cases']
        assert all(c['status'] in ('passed','failed') for c in cases)
        if control == 'baseline':
            assert report['typecheck']['changedFiles'] == []
            assert any(c['group']=='change' and c['status']=='failed' for c in cases)
            assert all(c['status']=='passed' for c in cases if c['group']=='preserve')
        if control == 'reference': assert report['overall']=='passed'
        if control == 'partial': assert any(c['group']=='preserve' and c['status']=='failed' for c in cases)
    raw.with_suffix('.json.gz').write_bytes(gzip.compress(raw.read_bytes(),mtime=0))
    raw.unlink()
