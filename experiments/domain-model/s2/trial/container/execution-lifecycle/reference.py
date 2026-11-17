"""A loaded active target retains the execution unit without starting it."""
import hashlib,json,os,pathlib,re,time
import common as c
PROPERTIES=['Id','LoadState','ActiveState','SubState','InvocationID','InactiveEnterTimestampMonotonic','ActiveEnterTimestampMonotonic','Result','ExecMainCode','ExecMainStatus','After','BindsTo']

def raw(run,unit,command,phase='finish'):
 code,out,err=command(run,['systemctl','show',unit,*sum((['-p',p] for p in PROPERTIES),[])],phase,check=False)
 record={'unit':unit,'exitCode':code,'stdout':out,'stderr':err,'observed':c.stamp()}
 # Store raw bytes/exit/identity BEFORE parsing or rejecting.
 with (run/'service-raw.jsonl').open('a') as f:f.write(json.dumps(record,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
 fields={}
 for line in out.splitlines():
  if '=' not in line:continue
  k,v=line.split('=',1)
  if k in fields:raise RuntimeError('duplicate-service-property')
  fields[k]=v
 if code or fields.get('Id')!=unit or fields.get('LoadState')!='loaded':raise RuntimeError('service-query-identity')
 return fields,record

def acquire(run,units,command):
 s=c.read(run/'state.json');name='ontosary-reference-'+run.name+'.target'
 text=f'[Unit]\nDescription=Ontosary owned service reference {run.name}\nDefaultDependencies=no\nAfter={s["service"]}\nBindsTo=ontosary-execution-seal.service\n'
 record={'runId':run.name,'holder':name,'service':s['service'],'phase':'planned','fileSha256':hashlib.sha256(text.encode()).hexdigest(),'workerActivationDependency':False,**c.stamp()};c.write(run/'reference.json',record);c.state(run,referenceHolder=name)
 (units/name).write_text(text);os.chmod(units/name,0o644);command(run,['systemctl','daemon-reload'],'work');command(run,['systemctl','start',name],'work')
 fields,observed=raw(run,name,command,'work')
 if fields.get('ActiveState')!='active' or s['service'] not in fields.get('After','').split() or 'ontosary-execution-seal.service' not in fields.get('BindsTo','').split():raise RuntimeError('reference-not-held')
 record.update(phase='held',acquired=observed['observed']);c.write(run/'reference.json',record)

def held(run,units,command,phase='finish'):
 r=c.read(run/'reference.json');s=c.read(run/'state.json')
 if r['phase']!='held' or r['runId']!=run.name or r['service']!=s['service'] or r['holder']!=s['referenceHolder']:raise RuntimeError('reference-record-binding')
 p=units/r['holder']
 if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=r['fileSha256']:raise RuntimeError('reference-file-binding')
 fields,_=raw(run,r['holder'],command,phase)
 if fields.get('ActiveState')!='active' or s['service'] not in fields.get('After','').split():raise RuntimeError('reference-holder-lost')
 return r

def invocation(run,units,command):
 held(run,units,command,'work');s=c.read(run/'state.json');value=os.environ.get('INVOCATION_ID','')
 fields,record=raw(run,s['service'],command,'work')
 if not re.fullmatch('[0-9a-f]{32}',value) or fields.get('InvocationID')!=value or fields.get('ActiveState') not in ['activating','active']:raise RuntimeError('invocation-start-binding')
 c.state(run,invocationId=value,invocationObserved=record['observed']);return value

def end_observation(run,units,command):
 held(run,units,command);s=c.read(run/'state.json');fields,record=raw(run,s['service'],command)
 if fields.get('InvocationID')!=s.get('invocationId') or not re.fullmatch('[0-9a-f]{32}',s.get('invocationId','')):raise RuntimeError('invocation-end-binding')
 if fields.get('ActiveState') not in ['inactive','failed']:return None
 stamp=int(fields.get('InactiveEnterTimestampMonotonic','0'))/1000000
 if stamp<=0 or stamp>s['deadlines']['finish'] or stamp<s['finalizedAt']['mono'] or record['observed']['mono']>s['deadlines']['finish']:raise RuntimeError('inactive-deadline-unconfirmed')
 return {'runId':run.name,'service':s['service'],'invocationId':s['invocationId'],'inactiveAtMono':stamp,'raw':record,'fields':fields}

def release(run,units,command,blocked=False):
 r=c.read(run/'reference.json')
 if r['phase']=='released':return
 if not (run/('blocked-receipt.json' if blocked else 'seal-receipt.json')).exists():raise RuntimeError('release-before-durable-receipt')
 command(run,['systemctl','stop',r['holder']],'finish')
 fields,_=raw(run,r['holder'],command)
 if fields.get('ActiveState')!='inactive':raise RuntimeError('reference-release-unconfirmed')
 for name in [r['holder'],r['service']]:
  p=units/name
  if p.exists():p.unlink()
 command(run,['systemctl','daemon-reload'],'finish');r.update(phase='released',released=c.stamp(),blocked=blocked);c.write(run/'reference.json',r)
