"""Killable host wrapper. It does not own guest termination or deletion."""
import datetime,json,os,pathlib,subprocess,sys,time

def main():
 work=pathlib.Path(sys.argv[1]);mode=sys.argv[2];plan=json.loads((work/'plan.json').read_text());root=pathlib.Path(plan['vmRoot']);env={**os.environ,'LIMA_HOME':str(root/'lima')};prefix=[str(root/'prefix/bin/limactl'),'shell','--workdir=/tmp',plan['vmName'],'sudo','python3','/opt/ontosary-execution/execution-lifecycle/engine.py'];started=time.monotonic();outer=datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=120)
 def call(args,timeout=3):
  remaining=min(120-(time.monotonic()-started),(outer-datetime.datetime.now(datetime.timezone.utc)).total_seconds());p=subprocess.run(prefix+args,capture_output=True,text=True,timeout=min(timeout,remaining),env=env)
  with (work/(mode+'-commands.jsonl')).open('a') as f:f.write(json.dumps({'command':prefix+args,'exitCode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'hostMono':time.monotonic()})+'\n')
  p.check_returncode();return json.loads(p.stdout) if p.stdout.strip() else None
 registration=call(['register',mode,'--remaining','114','--host-deadline',outer.isoformat()],5);rid=registration['runId'];(work/(mode+'-registration.json')).write_text(json.dumps({'hostStartedMono':started,'hostDeadlineUtc':outer.isoformat(),'hostRegistrationSeconds':time.monotonic()-started,**registration})+'\n')
 while time.monotonic()-started<120:
  state=call(['status',rid]);(work/(mode+'-status.json')).write_text(json.dumps(state)+'\n')
  if state.get('serviceInactiveConfirmed') or state.get('discardVM'):break
  if not state.get('workClosed'):call(['heartbeat',rid])
  time.sleep(.2)
 else:raise RuntimeError('host-unit-deadline')
 if not state.get('serviceInactiveConfirmed'):raise RuntimeError('unit-not-sealed')
if __name__=='__main__':main()
