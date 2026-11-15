"""Export sealed collector results and enumerated manager diagnostics, never originals."""
import hashlib,json,os,pathlib,re,shutil,tarfile,tempfile,time
from collector import SafeFiles,Rejected,open_directory,inventory
DIAGNOSTICS=('state.json','events.jsonl','baseline.json','supervisor.json','native.json','identity.json','identity-proof.json','baseline-policy-verification.json','policy-verification.json','termination.json','removed.json','ready.json','heartbeat.json','recovery.json')
PREPARATION=('events.jsonl','manifest.oci','config.oci','native-image.json','runtime-tools.json')
GLOBAL=('image.json','image-export.json','import-verified.json')

def export(root,shared,target,deadline,max_files=1024,max_bytes=16*1024*1024,fail_after=None):
 root=pathlib.Path(root);shared=pathlib.Path(shared);target=pathlib.Path(target)
 if target.exists():raise Rejected('export-already-published')
 stage=pathlib.Path(tempfile.mkdtemp(prefix='.s2-export-',dir=target.parent)).resolve();payload=stage/'payload';payload.mkdir(mode=0o700)
 safe=SafeFiles(payload,deadline,max_files,max_bytes);statuses={}
 def optional(path,name):
  try:return safe.copy(path,name)
  except FileNotFoundError:return None
 try:
  runs=root/'runs'
  if runs.exists():
   fd=open_directory(runs)
   try:
    with os.scandir(fd) as entries:
     names=[]
     for ent in entries:
      if time.monotonic()>=deadline or len(names)>=7:raise Rejected('run-count-or-time')
      if not re.fullmatch('[0-9a-f]{12}',ent.name) or not ent.is_dir(follow_symlinks=False):raise Rejected('run-directory')
      names.append(ent.name)
   finally:os.close(fd)
   for rid in sorted(names):
    run=runs/rid;prefix='runs/'+rid+'/'
    state=json.loads(safe.copy(run/'state.json',prefix+'state.json').read_text())
    if state.get('runId')!=rid:raise Rejected('export-run-binding')
    for n in DIAGNOSTICS:
     if n!='state.json':optional(run/n,prefix+n)
    eligible=state.get('collectionStatus')=='collected' and all(state.get(k) for k in ['terminationConfirmed','removalConfirmed','cleanupDone','serviceInactiveConfirmed','unitFilesRemoved']) and not any(state.get(k) for k in ['createPending','startPending','execPending','discardVM'])
    if not eligible:
     statuses[rid]={'exportedResult':False,'reason':'collection-or-termination-not-valid','collectionStatus':state.get('collectionStatus')};continue
    result=run/'result';info=result.lstat()
    if info.st_uid!=os.getuid() or info.st_mode&0o222 or result.is_symlink():raise Rejected('unsealed-result')
    record=json.loads(safe.copy(result/'fixture.json',prefix+'result/fixture.json',sealed=True).read_text())
    term=record['termination'];manager_term=json.loads((payload/(prefix+'termination.json')).read_text());removed=json.loads((payload/(prefix+'removed.json')).read_text())
    if term!=manager_term or term.get('state')!='stopped-confirmed' or not term.get('confirmed') or not term.get('admissionClosed') or not removed.get('containerAbsent') or not removed.get('taskAbsent') or removed.get('pending'):raise Rejected('export-termination')
    for key in ['runId','containerId','image','cgroup','cgroupInode']:
     if term.get(key)!=state.get(key):raise Rejected('export-binding:'+key)
    if term.get('source')!=str(run/'source') or term.get('auxiliary')!=str(run/'auxiliary'):raise Rejected('export-path-binding')
    if record.get('schema')!='s2-lifecycle-fixture-v1' or record.get('fixtureOnly') is not True or record.get('validSubmission') is not False:raise Rejected('export-fixture-contract')
    if inventory({n:result/n for n in ['source','auxiliary']},deadline=deadline)!=record['snapshot']:raise Rejected('result-manifest-mismatch')
    manifest=record['snapshot']['files']
    if len(manifest)>128 or sum(v['bytes'] for v in manifest.values())>16*1024*1024:raise Rejected('collector-bound')
    for name,row in sorted(manifest.items()):
     parts=pathlib.PurePosixPath(name).parts
     if not parts or parts[0] not in ['source','auxiliary'] or '..' in parts or name.startswith('/'):raise Rejected('result-manifest-path')
     safe.copy(result/name,prefix+'result/'+name,sealed=True)
     if safe.members[prefix+'result/'+name]!=row:raise Rejected('result-manifest-mismatch')
    # Manager result is immutable after seal; recheck authority without touching originals.
    again=SafeFiles(stage/'authority-check',deadline,1,1024*1024)
    reread=json.loads(again.copy(run/'state.json','state.json').read_text())
    if reread!=state:raise Rejected('result-authority-changed')
    shutil.rmtree(stage/'authority-check')
    statuses[rid]={'exportedResult':True,'files':len(manifest),'collectionStatus':'collected'}
  for folder in ['preparation','import']:
   for name in PREPARATION:optional(shared/folder/name,folder+'/'+name)
  for name in GLOBAL:optional(shared/name,name)
  optional(root/'gate.json','gate.json')
  safe.metadata('export-status.json',{'schema':'s2-safe-export-v1','fixtureOnly':True,'validSubmission':False,'runs':statuses,'diagnosticAllowlist':list(DIAGNOSTICS),'limits':{'files':max_files,'bytes':max_bytes},'workerOriginalsRead':False})
  members=dict(safe.members);indexdata=(json.dumps(members,sort_keys=True,indent=2)+'\n').encode()
  # External index itself consumes the same quota; it is not an archive member.
  safe.reserve('export-index.json',len(indexdata))
  archive=stage/'evidence.tar.gz'
  with tarfile.open(archive,'w:gz') as tar:
   for i,name in enumerate(sorted(members)):
    if time.monotonic()>=deadline:raise Rejected('export-time-limit')
    if fail_after is not None and i>=fail_after:raise Rejected('injected-export-failure')
    tar.add(payload/name,arcname=name,recursive=False)
  actual={}
  with tarfile.open(archive) as tar:
   for m in tar:
    if time.monotonic()>=deadline:raise Rejected('export-time-limit')
    if not m.isfile() or m.name in actual:raise Rejected('export-archive-entry')
    h=hashlib.sha256();size=0
    with tar.extractfile(m) as f:
     while True:
      if time.monotonic()>=deadline:raise Rejected('export-time-limit')
      b=f.read(65536)
      if not b:break
      h.update(b);size+=len(b)
    actual[m.name]={'sha256':h.hexdigest(),'bytes':size}
  if actual!=members:raise Rejected('export-index-mismatch')
  (stage/'index.json').write_bytes(indexdata);shutil.rmtree(payload)
  if time.monotonic()>=deadline:raise Rejected('export-time-limit')
  with archive.open('rb') as f:archive_sha=hashlib.file_digest(f,'sha256').hexdigest()
  os.rename(stage,target)
  return {'files':len(members),'metadataIncludedFiles':len(members)+1,'boundedBytes':safe.bytes,'archive':str(target/'evidence.tar.gz'),'bytes':(target/'evidence.tar.gz').stat().st_size,'sha256':archive_sha,'runs':statuses}
 finally:
  if stage.exists():shutil.rmtree(stage)
