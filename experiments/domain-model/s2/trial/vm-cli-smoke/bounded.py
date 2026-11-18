"""Finite stdout/stderr capture; no shell, process-group deadline, explicit truncation."""
import datetime, os, selectors, signal, subprocess, time

def run(args, seconds, env=None, cwd=None, cap=1024*1024, on_start=None, overflow='terminate'):
    if overflow not in ('terminate','discard') or cap < 0:
        raise ValueError('invalid-output-policy')
    if seconds <= 0:
        raise TimeoutError('expired-before-dispatch')
    start=time.monotonic(); end=start+seconds
    row={'args':args,'startedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'limitSeconds':seconds,'truncated':False,'timedOut':False,'capPerStream':cap,'outputPolicy':overflow}
    p=subprocess.Popen(args,env=env,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
    row['pid']=p.pid; data={'stdout':bytearray(),'stderr':bytearray()};kill_requested=False
    def kill():
        nonlocal kill_requested
        if kill_requested:return
        kill_requested=True
        try:os.killpg(p.pid,signal.SIGKILL)
        except ProcessLookupError:pass
    try:
        if on_start:row['processObservation']=on_start(p.pid)
        with selectors.DefaultSelector() as selector:
            for name,stream in [('stdout',p.stdout),('stderr',p.stderr)]:selector.register(stream,selectors.EVENT_READ,name)
            while selector.get_map():
                if time.monotonic()>=end:
                    row['timedOut']=True;kill();break
                for key,_ in selector.select(min(.1,max(0,end-time.monotonic()))):
                    chunk=os.read(key.fileobj.fileno(),65536)
                    if not chunk:selector.unregister(key.fileobj);continue
                    target=data[key.data]; room=max(0,cap-len(target));target.extend(chunk[:room])
                    if len(chunk)>room:
                        row['truncated']=True
                        if overflow=='terminate':kill()
        try:p.wait(timeout=3 if kill_requested else max(0,end-time.monotonic()))
        except subprocess.TimeoutExpired:row['timedOut']=True;kill();p.wait(timeout=3)
    finally:
        try:
            if p.poll() is None:kill();p.wait(timeout=3)
        finally:p.stdout.close();p.stderr.close()
    row.update(exitCode=p.returncode,seconds=time.monotonic()-start,finishedUtc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    row.update({name:bytes(body).decode('utf-8',errors='replace') for name,body in data.items()})
    return row
