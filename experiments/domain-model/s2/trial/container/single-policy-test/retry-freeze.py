"""Freeze all explicitly analysis-tagged snapshots once; never absorb closing or unknown files."""
import argparse,json,pathlib,importlib.util
from snapshot import snapshot
from scope import rows,registered_scope
p=argparse.ArgumentParser();p.add_argument('--work',required=True);a=p.parse_args();work=pathlib.Path(a.work);assert not (work/'analysis-scope.json').exists()
snapshot(work,['python3',str(pathlib.Path(__file__)),'--work',str(work)],'exploration','analysis')
registry=json.loads((work/'closing-registry.json').read_text());closing={r['id'] for r in registry};ids=[]
for p in (work/'snapshots').glob('*.json'):
 meta=json.loads(p.read_text())
 if p.stem in closing:continue
 assert meta['category']=='analysis' and meta['phase'] in ['plan','environment','diagnosis','exploration','finish'],'unclassified-analysis'
 ids.append(p.stem)
(work/'analysis-scope.json').write_text(json.dumps(rows(work/'snapshots',sorted(ids)),indent=2)+'\n');registered_scope(work)
spec=importlib.util.spec_from_file_location('retry_audit',pathlib.Path(__file__).with_name('retry-audit.py'));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);result=module.audit(work);(work/'audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['outcome','blockedReasons','candidateApplications','candidateStarts','containers','originalInputsUnchanged']}))
