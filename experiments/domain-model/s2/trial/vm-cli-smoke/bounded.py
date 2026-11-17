"""Finite stdout/stderr capture; no shell, process-group deadline, explicit truncation."""
import datetime, os, selectors, signal, subprocess, time

def run(args, seconds, env=None, cwd=None, cap=1024*1024, on_start=None):
    if seconds <= 0:
        raise TimeoutError('expired-before-dispatch')
    start=time.monotonic(); end=start+seconds
    row={'args':args,'startedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'limitSeconds':seconds,'truncated':False,'timedOut':False,'capPerStream':cap}
    p=subprocess.Popen(args,env=env,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
    row['pid']=p.pid; data={'stdout':bytearray(),'stderr':bytearray()}
    def kill():
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
                    if len(chunk)>room:row['truncated']=True;kill()
        p.wait(timeout=max(.1,min(2,end-time.monotonic())))
    finally:
        if p.poll() is None:kill();p.wait(timeout=3)
        p.stdout.close();p.stderr.close()
    row.update(exitCode=p.returncode,seconds=time.monotonic()-start,finishedUtc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    row.update({name:bytes(body).decode('utf-8',errors='replace') for name,body in data.items()})
    return row
