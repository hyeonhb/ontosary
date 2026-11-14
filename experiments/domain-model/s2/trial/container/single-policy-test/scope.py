"""Explicit frozen analysis scope and separately classified closing evidence."""
import hashlib,json,pathlib,tarfile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rows(root,ids):
 return [{'id':i,'manifestSha256':sha(root/(i+'.json')),'archiveSha256':sha(root/(i+'.tar.gz'))} for i in ids]
def verify(root,scope):
 for row in scope:
  manifest=root/(row['id']+'.json');archive=root/(row['id']+'.tar.gz')
  assert sha(manifest)==row['manifestSha256'],'manifest-hash'
  assert sha(archive)==row['archiveSha256'],'archive-hash'
  m=json.loads(manifest.read_text());assert m['id']==row['id'] and m['archiveSha256']==row['archiveSha256']
  with tarfile.open(archive) as t:
   actual={}
   for x in t.getmembers():
    assert x.isfile() and not pathlib.PurePosixPath(x.name).is_absolute() and '..' not in pathlib.PurePosixPath(x.name).parts
    assert x.name not in actual
    actual[x.name]={'sha256':hashlib.sha256(t.extractfile(x).read()).hexdigest(),'bytes':x.size}
  assert actual==m['files'],'snapshot-members'
 return {'snapshotsVerified':len(scope),'scope':scope}
def classify(root,analysis,closing):
 ids=[r['id'] for r in analysis+closing];assert len(ids)==len(set(ids)),'duplicate-scope'
 expected={i+ext for i in ids for ext in ['.json','.tar.gz']}
 assert {p.name for p in root.iterdir()}==expected,'unclassified-or-missing-snapshot'
 verify(root,analysis);verify(root,closing)
def inventory(root):
 result={};archives={}
 for p in sorted(root.rglob('*')):
  if p.is_file() and p!=root/'index.json':
   name=p.relative_to(root).as_posix();result[name]={'sha256':sha(p),'bytes':p.stat().st_size}
   if name.endswith('.tar.gz'):
    members={}
    with tarfile.open(p) as t:
     for m in t.getmembers():
      assert not pathlib.PurePosixPath(m.name).is_absolute() and '..' not in pathlib.PurePosixPath(m.name).parts and (m.isfile() or m.isdir())
      if m.isfile():
       assert m.name not in members
       members[m.name]={'sha256':hashlib.sha256(t.extractfile(m).read()).hexdigest(),'bytes':m.size}
    archives[name]=members
 return {'files':result,'archives':archives}
def verify_index(root):
 assert inventory(root)==json.loads((root/'index.json').read_text()),'whole-index-mismatch'
 s=json.loads((root/'snapshot-scope.json').read_text());classify(root/'snapshots',s['analysis'],s['closing'])
 if 'closingAllowed' in s:
  for row in s['closing']:
   assert {'phase':row['phase'],'command':row['command']} in s['closingAllowed'],'closing-command-not-allowed'
   meta=json.loads((root/'snapshots'/(row['id']+'.json')).read_text());assert meta.get('category')=='closing' and meta.get('phase')==row['phase'] and meta['command']==row['command'],'closing-registration-mismatch'
 if 'analysisAllowed' in s:
  for row in s['analysis']:
   meta=json.loads((root/'snapshots'/(row['id']+'.json')).read_text())
   assert meta.get('category')=='analysis' and {'phase':meta.get('phase'),'command':meta['command']} in s['analysisAllowed'],'analysis-registration-mismatch'
 return {'files':len(inventory(root)['files']),'analysis':len(s['analysis']),'closing':len(s['closing'])}

def registered_scope(work):
 work=pathlib.Path(work);analysis=json.loads((work/'analysis-scope.json').read_text());closing=json.loads((work/'closing-registry.json').read_text());plan=json.loads((work/'plan.json').read_text())
 for row in closing:
  assert {'phase':row['phase'],'command':row['command']} in plan['closingAllowed'],'closing-command-not-allowed'
  meta=json.loads((work/'snapshots'/(row['id']+'.json')).read_text())
  assert meta.get('category')=='closing' and meta.get('phase')==row['phase'] and meta['command']==row['command'],'closing-registration-mismatch'
 classify(work/'snapshots',analysis,closing)
 result={'analysis':analysis,'closing':closing,'closingAllowed':plan['closingAllowed']}
 if 'analysisAllowed' in plan:
  for row in analysis:
   meta=json.loads((work/'snapshots'/(row['id']+'.json')).read_text())
   assert meta.get('category')=='analysis' and {'phase':meta.get('phase'),'command':meta['command']} in plan['analysisAllowed'],'analysis-registration-mismatch'
  result['analysisAllowed']=plan['analysisAllowed']
 return result
