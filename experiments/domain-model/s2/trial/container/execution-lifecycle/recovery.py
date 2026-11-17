"""Finite evidence retrieval and independent owned-resource cleanup."""
import datetime,hashlib,io,json,os,pathlib,shutil,subprocess,tarfile,tempfile,time
from deadline import limit
from artifacts import Store
MAX_BYTES=16*1024*1024
RECEIPT_RESERVE=8192

def write(path,value):
 data=(json.dumps(value,indent=2)+'\n').encode()
 if len(data)>RECEIPT_RESERVE:raise RuntimeError('recovery-receipt-bound')
 tmp=path.with_suffix('.tmp');tmp.write_bytes(data);os.replace(tmp,path)
def remaining(r):
 try:return limit(r.budget,'finish')
 except Exception:return 0

def verify_pair(archive,index):
 expected=json.loads(index.read_text());actual={};total=index.stat().st_size
 if len(expected)+1>1024 or total>MAX_BYTES-RECEIPT_RESERVE:raise RuntimeError('recovery-index-bound')
 with tarfile.open(archive) as t:
  for m in t:
   if not m.isfile() or m.name in actual or m.name.startswith('/') or '..' in pathlib.PurePosixPath(m.name).parts:raise RuntimeError('recovery-entry')
   total+=m.size
   if total>MAX_BYTES-RECEIPT_RESERVE or len(actual)>=1023:raise RuntimeError('recovery-byte-or-count-bound')
   h=hashlib.sha256()
   with t.extractfile(m) as f:
    while b:=f.read(65536):h.update(b)
   actual[m.name]={'sha256':h.hexdigest(),'bytes':m.size}
 if actual!=expected:raise RuntimeError('recovery-index-mismatch')
 return {'files':len(actual),'bytes':total}

def retrieve(r,scope,run_id=None,seconds=None):
 if not scope.replace('-','').isalnum():raise RuntimeError('recovery-scope')
 budget=min(30,max(0,remaining(r)-90)) if seconds is None else min(seconds,30,max(0,remaining(r)-90))
 try:budget=min(budget,limit(r.budget,r.phase))
 except Exception:budget=0
 receipt={'scope':scope,'runId':run_id,'evidenceStatus':'missing','errors':[],'secondsAvailable':budget,'partialPublished':False}
 output=r.w/('recovery-'+scope+'.tar.gz');record=r.w/('recovery-'+scope+'.json');started=time.monotonic();end=started+budget
 def save():
  try:write(record,receipt)
  except Exception as e:receipt['errors'].append({'phase':'record','error':str(e)});print(json.dumps({'recoveryRecordFailure':receipt}),flush=True)
 if budget<=0:receipt['reason']='cleanup-reserve';save();return receipt
 if output.exists():receipt['reason']='already-published-not-reused';save();return receipt
 try:
  with tempfile.TemporaryDirectory(prefix='.recovery-'+scope+'-',dir=r.w) as name:
   stage=pathlib.Path(name)
   def call(args,guest=False):
    left=min(end-time.monotonic(),remaining(r)-90)
    if left<=0:raise RuntimeError('recovery-deadline')
    result,out=(r.guest if guest else r.cmd)(args,timeout=left,check=False)
    if result['exitCode']:raise RuntimeError('recovery-command:'+str(result['exitCode'])+':'+out[-600:])
    return out
   utc=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=max(0,end-time.monotonic()))).isoformat()
   out=call(['python3','/opt/ontosary-execution/execution-lifecycle/guest.py','export',scope,run_id or '-',utc],True);announced=json.loads(out)
   if announced['status']=='error-receipt':
    receipt.update(evidenceStatus='error-receipt',guestReceipt=announced);save();return receipt
   for filename in ['evidence.tar.gz','index.json']:
    call([r.lima,'copy',r.plan['vmName']+':/tmp/s2-execution-export-'+scope+'/'+filename,str(stage/filename)])
   checked=verify_pair(stage/'evidence.tar.gz',stage/'index.json')
   if time.monotonic()>=end:raise RuntimeError('recovery-deadline')
   envelope=stage/'envelope.tar.gz'
   with tarfile.open(envelope,'w:gz') as t:
    for filename in ['evidence.tar.gz','index.json']:t.add(stage/filename,arcname=filename,recursive=False)
   if time.monotonic()>=end:raise RuntimeError('recovery-deadline')
   os.rename(envelope,output);receipt.update(evidenceStatus=announced['status'],verified=checked,artifact=output.name,archiveSha256=hashlib.sha256(output.read_bytes()).hexdigest())
 except Exception as e:receipt['errors'].append({'phase':'retrieve','error':str(e)})
 receipt['seconds']=time.monotonic()-started;save();return receipt

def cleanup(r):
 r.phase='finish';result={'evidenceStatus':'missing','cleanupStatus':'unconfirmed','errors':[],'attempts':[],'vmAbsent':False,'rootAbsent':not r.root.exists(),'vmDisposalIsNotUnitTerminationProof':True};started=time.monotonic()
 def record_error(phase,e):result['errors'].append({'phase':phase,'error':str(e)})
 def call(args,timeout=30):
  left=remaining(r);result['attempts'].append(args)
  if left>0:return r.cmd(args,timeout=min(timeout,left),check=False)
  # Safety disposal may exceed the experiment clock; never used for retrieval/work.
  result['safetyDeadlineOverrun']=True
  p=subprocess.run(args,capture_output=True,text=True,env=r.env,timeout=timeout)
  return {'exitCode':p.returncode},p.stdout+p.stderr
 try:
  owner_path=r.w/'ownership.json'
  if not owner_path.exists():
   result.update(cleanupStatus='not-created' if not r.root.exists() else 'unconfirmed',reason='no-ownership-record');return result
  owner=json.loads(owner_path.read_text())
  if owner['root']!=str(r.root) or owner['vmName']!=r.plan['vmName'] or not r.root.name.startswith('ontosary-s2-') or r.root.is_symlink():raise RuntimeError('cleanup-ownership-mismatch')
  if not r.root.exists():result.update(cleanupStatus='complete',vmAbsent=True,rootAbsent=True,evidenceStatus='not-retried',duplicateCleanup=True);return result
  try:
   receipt=retrieve(r,'final');result['evidenceStatus']=receipt['evidenceStatus'];result['errors']+=receipt['errors']
  except Exception as e:record_error('retrieve-unexpected',e)
  # No evidence/recording error can skip the following owned-resource attempts.
  if pathlib.Path(r.lima).exists():
   for action in ['stop','delete']:
    try:
     row,out=call([r.lima,action,'--force',r.plan['vmName']])
     if row['exitCode']:record_error(action,RuntimeError(str(row['exitCode'])+':'+out[-500:]))
    except Exception as e:record_error(action,e)
   try:
    args=[__import__('sys').executable,'-c','import subprocess,sys,json;p=subprocess.run([sys.argv[1],"list","--json"],capture_output=True,text=True,timeout=7);print(json.dumps({"exitCode":p.returncode,"stdout":p.stdout,"stderr":p.stderr}))',r.lima];row,out=call(args,8)
    if row['exitCode']:raise RuntimeError('listing-error:'+out[-500:])
    listing=json.loads(out);result['listing']=listing
    if listing['exitCode']:raise RuntimeError('listing-status:'+str(listing['exitCode']))
    lines=[json.loads(line) for line in listing['stdout'].splitlines() if line.strip()]
    if any(x.get('name')==r.plan['vmName'] for x in lines) or (r.root/'lima'/r.plan['vmName']).exists():raise RuntimeError('owned-vm-still-present')
    processes=subprocess.check_output(['ps','-axo','pid=,ppid=,command='],text=True)
    if any(str(r.root/'prefix') in line or str(r.root/'lima') in line for line in processes.splitlines()):raise RuntimeError('owned-process-still-present')
    result['vmAbsent']=True
   except Exception as e:record_error('absence',e)
  elif not owner.get('vmRegistrations'):result['vmAbsent']=True
  else:record_error('absence',RuntimeError('owned-lima-executable-missing'))
  if result['vmAbsent']:
   try:shutil.rmtree(r.root);result['rootAbsent']=True
   except Exception as e:record_error('root-remove',e)
  try:
   store=Store(r.plan['store'],owner_tag=r.plan['round']);result['retainedBytes']=store.usage();result['ownedTemporaryRemoved']=store.cleanup_pending(time.monotonic()+min(5,max(.01,remaining(r))));result['temporaryEntries']=[p.name for p in store.root.glob('.pending-*')]
  except Exception as e:record_error('store',e)
  result['cleanupStatus']='complete' if result['vmAbsent'] and result['rootAbsent'] else 'unconfirmed'
 except Exception as e:record_error('ownership-or-cleanup',e)
 finally:
  result['seconds']=time.monotonic()-started;result['remainingSeconds']=remaining(r)
  try:write(r.w/'cleanup.json',result)
  except Exception as e:record_error('cleanup-record',e)
  print(json.dumps(result),flush=True)
 return result
