"""Independent V2 consumer checks. Copy only pinned files; never edit upstream."""
import gzip, hashlib, json, pathlib, shutil, subprocess, sys, tempfile
repo = pathlib.Path(__file__).resolve().parents[3]
root, fresh = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
base = repo / 'experiments/domain-model'
saved = base / 'results/2026-11-08-v2'
def load(p):
    return json.loads(gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_bytes())
def call(script, *args):
    r = subprocess.run(['node', str(base / 'v2' / script), *map(str,args)], cwd=repo, capture_output=True, text=True)
    return r.returncode, json.loads(r.stdout)
files = sorted(p.name for p in saved.iterdir() if p.name != 'timing.json')
assert files == sorted(p.name for p in fresh.iterdir() if p.name != 'timing.json')
for name in files: assert (fresh/name).read_bytes() == (saved/name).read_bytes(), name
old = base/'results/2026-11-08'
old_files = sorted(p.name for p in old.iterdir() if p.name != 'timing.json')
for name in old_files: assert (fresh/name).read_bytes() == (old/name).read_bytes(), name
provided = load(base/'v2/agent-input-manifest.json')['files']
for name, expected in provided.items(): assert hashlib.sha256((base/name).read_bytes()).hexdigest() == expected
model = load(saved/'model-after.json')
items = {i['id']:i for i in model['items']}
fact_ids = {f['id'] for f in load(saved/'facts.json.gz')}
for ident, item in items.items():
    code, result = call('navigate.mjs', saved/'model-after.json', ident)
    expected = set()
    for other in model['items']:
        if other['id'] == ident: continue
        if other['id'] in item['relatedItems']: expected.add((other['id'],'outgoing'))
        if ident in other['relatedItems']: expected.add((other['id'],'incoming'))
    assert code == 0
    assert {(p['to'],p['direction']) for p in result['paths']} == expected
    for p in result['paths']:
        assert p['declaredEdge'] == ([ident,p['to']] if p['direction']=='outgoing' else [p['to'],ident])
        assert p['factRefs'] == items[p['to']]['factRefs'] and set(p['factRefs']) <= fact_ids
code, result = call('navigate.mjs', saved/'model-after.json','missing-id')
assert code == 1 and result['found'] is False
checks=[]
def check(name, source, expected, *mode):
    code, r=call('validate.mjs',source,saved,*mode)
    actual=(r['anchorValid'],r['analysisInputsValid'],r['valid'],code,r['requiresReview'])
    assert actual == expected, (name,actual)
    if not r['analysisInputsValid']:
        assert len(r['staleFacts']) >= 468 and len(r['staleCandidates']) == 5
        assert set(r['staleItems']) == set(items)
    checks.append({'case':name,'exit':code,'anchorValid':r['anchorValid'],'analysisInputsValid':r['analysisInputsValid'],'valid':r['valid'],'status':r['status'],'requiresReview':r['requiresReview'],'staleFacts':len(r['staleFacts']),'staleCandidates':len(r['staleCandidates']),'staleItems':len(r['staleItems']),'reason':r['analysisInputs'].get('reason')})
check('unchanged prepared input',root,(True,True,True,0,False))
check('explicit anchors-only',root,(True,False,False,1,True),'--anchors-only')
with tempfile.TemporaryDirectory(prefix='ontosary-review-v2-') as tmp:
    clone=pathlib.Path(tmp)
    for f in load(base/'v1/manifest.json')['inputHashes']:
        dest=clone/f; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(root/f,dest)
    target=clone/'packages/admin-ui/src/lib/core/src/providers/modal/modal.service.ts'
    original=target.read_bytes()
    changed=original.replace(b'    fromComponent<T extends Dialog<any>, R>(',b'    renamedFromComponent<T extends Dialog<any>, R>(')
    assert changed != original
    target.write_bytes(changed)
    check('target declaration only',clone,(True,False,False,1,True))
    assert 'modal.service.ts' in checks[-1]['reason']
    target.write_bytes(original)
    config=clone/'packages/admin-ui/ontosary.scope.json'; config.unlink()
    check('actual scoped configuration missing',clone,(True,False,False,1,True))
    shutil.copyfile(root/'packages/admin-ui/ontosary.scope.json',config)
    source=clone/'packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts'
    source.write_bytes(source.read_bytes()+b'\n// independent fixture edit\n')
    check('occurrence source changed',clone,(False,False,False,1,True))
print(json.dumps({'reviewedRevision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),'reproducedV2Files':len(files),'preservedV1Files':len(old_files),'providedHashes':len(provided),'navigationStartIds':len(items),'missingIdExit':1,'validatorCases':checks,'scope':'Same installed cache; sparse temporary copies only for negative cases. No installation/build or semantic approval.'},ensure_ascii=False,indent=2))
