"""One absolute host-clock contract, shared by wrapper and nested preparation."""
import datetime,json,os,pathlib,signal,subprocess,time
class DeadlineExpired(RuntimeError):pass
def remaining(budget,phase,mono=None,utc=None):
 mono=time.monotonic() if mono is None else mono;utc=datetime.datetime.now(datetime.timezone.utc) if utc is None else utc
 d=budget['deadlines'][phase];return min(d['monotonic']-mono,(datetime.datetime.fromisoformat(d['utc'])-utc).total_seconds())
def limit(budget,phase,requested=None,**clocks):
 value=remaining(budget,phase,**clocks)
 if value<=0:raise DeadlineExpired('absolute phase deadline exhausted')
 return value if requested is None else min(value,requested)
def run(args,budget,phase,ledger,requested=None,stdout=None,env=None):
 start=time.monotonic();record={'command':args,'phase':phase,'requestedLimitSeconds':requested,'absoluteDeadline':budget['deadlines'][phase],'remainingBeforeDispatch':remaining(budget,phase),'startedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'startedMonotonic':start,'terminationRequested':False}
 proc=None
 try:
  effective=limit(budget,phase,requested);record['effectiveLimitSeconds']=effective
  proc=subprocess.Popen(args,stdout=stdout,stderr=subprocess.STDOUT if stdout is not None else None,env=env,start_new_session=True)
  record['pid']=proc.pid
  # Popen overhead also consumes the same absolute deadline.
  code=proc.wait(timeout=min(effective,limit(budget,phase,requested)));record.update(exitCode=code,reason='exit' if code==0 else 'command-failed')
 except (subprocess.TimeoutExpired,DeadlineExpired):
  record.update(exitCode=124,reason='deadline-exhausted',terminationRequested=proc is not None)
  if proc is not None:
   try:os.killpg(proc.pid,signal.SIGKILL)
   except ProcessLookupError:pass
   proc.wait(timeout=5)
 finally:
  record.update(seconds=time.monotonic()-start,remainingAfter=remaining(budget,phase),cleanupRequired=record.get('exitCode',1)!=0)
  with pathlib.Path(ledger).open('a') as f:f.write(json.dumps(record)+'\n')
 return record
