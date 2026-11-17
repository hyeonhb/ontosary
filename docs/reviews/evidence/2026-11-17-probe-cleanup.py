"""Local Round.cleanup probe; VM commands are replaced, no VM/network actions."""
import datetime,json,pathlib,sys,tempfile,time
ROOT=pathlib.Path.cwd()
sys.path.insert(0,str(ROOT/'experiments/domain-model/s2/trial/container/execution-lifecycle'))
import round as runner
rows=[]
for failure in ['archive-copy','export-transport']:
 with tempfile.TemporaryDirectory() as tmp:
  w=pathlib.Path(tmp).resolve();vm=w/'ontosary-s2-execution-lifecycle-fix-20261115';(vm/'prefix/bin').mkdir(parents=True);(vm/'prefix/bin/limactl').touch();(vm/'lima/test-vm').mkdir(parents=True)
  now=datetime.datetime.now(datetime.timezone.utc)
  for name,value in [('plan.json',{'vmRoot':str(vm),'vmName':'test-vm','store':str(w/'store'),'round':'probe'}),('budget.json',{'deadlines':{'finish':{'utc':(now+datetime.timedelta(seconds=60)).isoformat(),'monotonic':time.monotonic()+60}}}),('ownership.json',{'root':str(vm),'vmName':'test-vm','vmRegistrations':1})]:
   (w/name).write_text(json.dumps(value))
  obj=runner.Round(w);calls=[]
  def guest(args,**kw):
   calls.append(['guest',*args])
   if failure=='export-transport':raise RuntimeError('injected-export-transport-failure')
   return {'exitCode':0},'{}'
  def cmd(args,**kw):
   calls.append(['cmd',*args])
   if 'copy' in args:raise RuntimeError('injected-archive-copy-failure')
   return {'exitCode':0},''
  obj.guest=guest;obj.cmd=cmd
  try:obj.cleanup();error=None
  except RuntimeError as e:error=str(e)
  row={'failure':failure,'error':error,'stopCalls':sum('stop' in c for c in calls),'deleteCalls':sum('delete' in c for c in calls),'rootStillPresent':vm.exists(),'cleanupRecord':(w/'cleanup.json').exists(),'calls':calls}
  assert error and row['stopCalls']==row['deleteCalls']==0 and row['rootStillPresent'] and not row['cleanupRecord']
  rows.append(row)
print(json.dumps({'runtimeCommandsExecuted':0,'cases':rows},indent=2))
