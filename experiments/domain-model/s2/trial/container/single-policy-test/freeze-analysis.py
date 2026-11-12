"""Freeze analysis IDs before auditing. Later snapshots are separately classified."""
import pathlib,json,subprocess,datetime,time
from snapshot import snapshot
from scope import rows
work=pathlib.Path('work/s2-single-policy-test');budget=json.loads((work/'budget.json').read_text());assert time.monotonic()-budget['monotonic']<45*60
cmd=['python3','experiments/domain-model/s2/trial/container/single-policy-test/audit.py']
snapshot(work,cmd)
ids=sorted(p.stem for p in (work/'snapshots').glob('*.json'))
(work/'analysis-scope.json').write_text(json.dumps(rows(work/'snapshots',ids),indent=2)+'\n')
with (work/'audit.log').open('x') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=30)
