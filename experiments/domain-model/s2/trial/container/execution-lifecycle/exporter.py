"""Export sealed collector results and enumerated manager diagnostics, never originals."""
import hashlib,json,os,pathlib,re,shutil,tarfile,tempfile,time
from collector import SafeFiles,Rejected,open_directory,inventory
DIAGNOSTICS=('state.json','events.jsonl','baseline.json','supervisor.json','native.json','identity.json','identity-proof.json','baseline-policy-verification.json','policy-verification.json','termination.json','removed.json','ready.json','heartbeat.json','recovery.json','service-raw.jsonl','reference.json','seal-receipt.json','blocked-receipt.json')
PREPARATION=('events.jsonl','manifest.oci','config.oci','native-image.json','runtime-tools.json')
GLOBAL=('image.json','image-export.json','import-verified.json','metadata-publication.json')

def collect_result(run,state,safe,prefix,payload,stage,deadline):
 result=run/'result';info=result.lstat()
 if info.st_uid!=os.getuid() or info.st_mode&0o222 or result.is_symlink():raise Rejected('unsealed-result')
 record=json.loads(safe.copy(result/'fixture.json',prefix+'result/fixture.json',sealed=True).read_text())
 term=record['termination'];manager_term=json.loads((payload/(prefix+'termination.json')).read_text());removed=json.loads((payload/(prefix+'removed.json')).read_text())
 if term!=manager_term or term.get('state')!='stopped-confirmed' or not term.get('confirmed') or not term.get('admissionClosed') or not removed.get('containerAbsent') or not removed.get('taskAbsent') or removed.get('pending'):raise Rejected('export-termination')
 for key in ['runId','containerId','image','cgroup','cgroupInode']:
  if term.get(key)!=state.get(key):raise Rejected('export-binding:'+key)
 if term.get('source')!=str(run/'source') or term.get('auxiliary')!=str(run/'auxiliary'):raise Rejected('export-path-binding')
 if record.get('schema')!='s2-lifecycle-fixture-v1' or record.get('fixtureOnly') is not True or record.get('validSubmission') is not False:raise Rejected('export-fixture-contract')
 names=inventory({n:result/n for n in ['source','auxiliary']},deadline=safe.deadline,names_only=True);expected={**record['snapshot'],'files':{n:{'bytes':v['bytes']} for n,v in record['snapshot']['files'].items()}}
 if names!=expected:raise Rejected('result-manifest-mismatch')
 manifest=record['snapshot']['files']
 if len(manifest)>128 or sum(v['bytes'] for v in manifest.values())>16*1024*1024:raise Rejected('collector-bound')
 for name,row in sorted(manifest.items()):
  parts=pathlib.PurePosixPath(name).parts
  if not parts or parts[0] not in ['source','auxiliary'] or '..' in parts or name.startswith('/'):raise Rejected('result-manifest-path')
  safe.copy(result/name,prefix+'result/'+name,sealed=True)
  if safe.members[prefix+'result/'+name]!=row:raise Rejected('result-manifest-mismatch')
 # Manager result is immutable after seal; recheck authority without touching originals.
 authority='_authority/'+run.name+'.json'
 try:
  reread=json.loads(safe.copy(run/'state.json',authority).read_text())
  if reread!=state:raise Rejected('result-authority-changed')
 finally:
  if authority in safe.members:(payload/authority).unlink();del safe.members[authority]
 return len(manifest)

def export(root,shared,target,deadline,max_files=1024,max_bytes=16*1024*1024,fail_after=None,run_id=None,strict=False):
 root=pathlib.Path(root);shared=pathlib.Path(shared);target=pathlib.Path(target)
 if target.exists():raise Rejected('export-already-published')
 stage=pathlib.Path(tempfile.mkdtemp(prefix='.s2-export-',dir=target.parent)).resolve();payload=stage/'payload';payload.mkdir(mode=0o700)
 collection_end=deadline-min(2,max(0,(deadline-time.monotonic())/4));reserve=min(528*1024,max_bytes//2);safe=SafeFiles(payload,collection_end,max(0,max_files-3),max_bytes-reserve);statuses={};rejections=[];omitted=0;stopped=False
 def reject(name,error):
  nonlocal omitted,stopped
  if strict:raise error
  text=str(error)
  if len(rejections)<32:rejections.append({'path':name[:160],'reason':text[:180]})
  else:omitted+=1
  if 'limit' in text or 'bound' in text or time.monotonic()>=deadline:stopped=True
 def copy(path,name,optional=False):
  if stopped:return None
  try:return safe.copy(path,name)
  except FileNotFoundError as e:
   if not optional:reject(name,e)
  except (Rejected,OSError,ValueError) as e:reject(name,e)
  return None
 try:
  runs=root/'runs';names=[]
  if runs.exists():
   try:
    fd=open_directory(runs)
    try:
     with os.scandir(fd) as entries:
      for ent in entries:
       if time.monotonic()>=deadline or len(names)>=7:raise Rejected('run-count-or-time-limit')
       if not re.fullmatch('[0-9a-f]{12}',ent.name) or not ent.is_dir(follow_symlinks=False):raise Rejected('run-directory')
       names.append(ent.name)
    finally:os.close(fd)
   except (Rejected,OSError) as e:reject('runs',e);names=[]
  if run_id is not None:
   if not re.fullmatch('[0-9a-f]{12}',run_id):raise Rejected('export-run-id')
   names=[n for n in names if n==run_id]
   if not names:reject('runs/'+run_id,Rejected('requested-run-missing'))
  for rid in sorted(names):
   if stopped:break
   run=runs/rid;prefix='runs/'+rid+'/'
   state_path=copy(run/'state.json',prefix+'state.json')
   if state_path is None:continue
   try:
    state=json.loads(state_path.read_text())
    if state.get('runId')!=rid:raise Rejected('export-run-binding')
   except (ValueError,Rejected) as e:reject(prefix,e);continue
   for n in DIAGNOSTICS:
    if n!='state.json':copy(run/n,prefix+n,True)
   eligible=state.get('collectionStatus')=='collected' and all(state.get(k) for k in ['terminationConfirmed','removalConfirmed','cleanupDone','serviceInactiveConfirmed','unitFilesRemoved']) and not any(state.get(k) for k in ['createPending','startPending','execPending','discardVM'])
   statuses[rid]={'exportedResult':False,'reason':'collection-or-termination-not-valid','collectionStatus':state.get('collectionStatus')}
   if eligible and not stopped:
    try:
     count=collect_result(run,state,safe,prefix,payload,stage,deadline);statuses[rid]={'exportedResult':True,'files':count,'collectionStatus':'collected'}
    except (Rejected,OSError,ValueError,KeyError) as e:
     # Never publish part of an invalid normal result. Budget consumed stays consumed.
     for name in list(safe.members):
      if name.startswith(prefix+'result/'):
       (payload/name).unlink();del safe.members[name]
     reject(prefix+'result',e);statuses[rid]['reason']='result-validation-rejected'
  for folder in ['preparation','import']:
   for name in PREPARATION:copy(shared/folder/name,folder+'/'+name,True)
  for name in GLOBAL:copy(shared/name,name,True)
  copy(root/'gate.json','gate.json',True)
  status='partial' if rejections or stopped else ('complete' if statuses and all(v['exportedResult'] for v in statuses.values()) else 'diagnostic')
  safe.max_files=max_files;safe.max_bytes=max_bytes;safe.deadline=deadline
  # Reserved metadata is serialized even when body collection hit the time boundary.
  if time.monotonic()>=deadline:raise Rejected('export-time-limit')
  safe.metadata('export-status.json',{'schema':'s2-safe-export-v2','status':status,'fixtureOnly':True,'validSubmission':False,'runs':statuses,'diagnosticAllowlist':list(DIAGNOSTICS),'rejections':rejections,'additionalRejections':omitted,'collectionStopped':stopped,'uncollectedScope':'remaining allowlist/results' if stopped else None,'limits':{'files':max_files,'bytes':max_bytes},'workerOriginalsRead':False})
  members=dict(safe.members);indexdata=(json.dumps(members,sort_keys=True,indent=2)+'\n').encode();safe.reserve('export-index.json',len(indexdata));archive=stage/'evidence.tar.gz'
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
  for p in stage.iterdir():os.chmod(p,0o444)
  os.chmod(stage,0o755) # public fixture diagnostics; root-owned, never worker-mounted
  os.rename(stage,target)
  return {'status':status,'files':len(members),'metadataIncludedFiles':len(members)+1,'boundedBytes':safe.bytes,'archive':str(target/'evidence.tar.gz'),'bytes':(target/'evidence.tar.gz').stat().st_size,'sha256':archive_sha,'runs':statuses}
 except Exception as e:
  if strict:raise
  # This is an error receipt, never a fallback result or a fresh collection budget.
  receipt={'status':'error-receipt','error':str(e)[:500],'consumedBytes':safe.bytes,'consumedFiles':safe.attempts,'deadlineExpired':time.monotonic()>=deadline,'validSubmission':False}
  data=(json.dumps(receipt)+'\n').encode()
  if safe.bytes+len(data)>max_bytes or safe.attempts+1>max_files:raise Rejected('receipt-reserve-exhausted') from e
  for p in list(stage.iterdir()):
   if p.is_dir():shutil.rmtree(p)
   else:p.unlink()
  (stage/'receipt.json').write_bytes(data);os.chmod(stage/'receipt.json',0o444);os.chmod(stage,0o755);os.rename(stage,target);return receipt
 finally:
  if stage.exists():shutil.rmtree(stage)
