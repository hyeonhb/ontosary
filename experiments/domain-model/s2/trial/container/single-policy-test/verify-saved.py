"""Reproduce the frozen analysis and full closing-inclusive inventory from delivered files."""
import json,pathlib,tempfile,shutil
from scope import verify_index,verify
from audit import audit
root=pathlib.Path('experiments/domain-model/s2/verification/2026-11-12-single-policy-test')
index=verify_index(root)
with tempfile.TemporaryDirectory() as temporary:
 work=pathlib.Path(temporary);shutil.copytree(root/'host',work,dirs_exist_ok=True);shutil.copytree(root/'snapshots',work/'snapshots')
 assert audit(work)==json.loads((work/'audit.json').read_text()),'analysis-not-reproducible'
print(json.dumps({'index':index,'analysisReproduced':True}))
