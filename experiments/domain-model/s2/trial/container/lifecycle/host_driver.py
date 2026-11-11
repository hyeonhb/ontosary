"""Host lease sender. No detached sender survives this wrapper's death."""
import argparse,json,os,pathlib,subprocess,time

def guest(prefix,home,args,timeout=3):
    p=subprocess.run([str(pathlib.Path(prefix)/'bin'/'limactl'),'shell','--workdir=/tmp','s2-lifecycle','sudo','python3','/opt/ontosary-fixture/code/manager.py',*args],env={**os.environ,'LIMA_HOME':home},capture_output=True,timeout=timeout)
    if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')+p.stdout.decode(errors='replace'))
    return json.loads(p.stdout)

def drive(prefix,home,rid,log,seconds=60):
    start=time.monotonic();nextbeat=start;prior=None
    with pathlib.Path(log).open('x') as out:
        def record(kind,value):out.write(json.dumps({'kind':kind,'mono':time.monotonic(),'pid':os.getpid(),'value':value})+'\n');out.flush()
        while time.monotonic()-start<seconds:
            if time.monotonic()>=nextbeat:
                record('heartbeat',guest(prefix,home,['heartbeat',rid]));nextbeat+=1
            status=guest(prefix,home,['query',rid])
            if status!=prior:record('query',status);prior=status
            if status['state'] in ['finalized','blocked'] and status.get('cleanupDone'):return status
            time.sleep(min(.1,max(0,nextbeat-time.monotonic())))
    raise RuntimeError('host-outer-timeout')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);p.add_argument('--home',required=True);p.add_argument('--run',required=True);p.add_argument('--log',required=True);p.add_argument('--seconds',type=int,choices=[60,240],default=60);a=p.parse_args();print(json.dumps(drive(a.prefix,a.home,a.run,a.log,a.seconds)))
