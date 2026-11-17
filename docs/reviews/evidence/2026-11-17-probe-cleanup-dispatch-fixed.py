"""Independent host-only check of round.main at 153f887; no runtime actions."""
import contextlib, io, json, pathlib, sys, tempfile
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path.cwd()/'experiments/domain-model/s2/trial/container/execution-lifecycle'))
import round as runner
results=[]
for action in ['prepare','fixtures']:
 for failure in ['none','scope','registry','snapshot']:
  with tempfile.TemporaryDirectory() as td:
   w=pathlib.Path(td).resolve();calls=[];original=RuntimeError('original-'+action)
   command=lambda a:['python3',str(runner.HERE/'round.py'),a,'--work',str(w)]
   plan={'vmRoot':str(w/'unused'),'vmName':'not-created','closingAllowed':[{'phase':'finish','command':command('cleanup')},{'phase':'finish','command':command('seal')}]}
   runner.write(w/'plan.json',plan);runner.write(w/'budget.json',{});runner.snapshot(w,command(action),'analysis')
   real_write=runner.write;real_snapshot=runner.snapshot
   def write(p,v):
    if p.name=={'scope':'analysis-scope.json','registry':'closing-registry.json'}.get(failure):raise OSError('injected-'+failure)
    real_write(p,v)
   def snapshot(*a,**kw):
    if failure=='snapshot':raise OSError('injected-snapshot')
    return real_snapshot(*a,**kw)
   def fail(r):calls.append(action);raise original
   def cleanup(r):calls.append('cleanup');return {'cleanupStatus':'complete'}
   with patch.object(runner.Round,action,fail),patch.object(runner.Round,'cleanup',cleanup),patch.object(runner,'write',side_effect=write),patch.object(runner,'snapshot',side_effect=snapshot),patch.object(sys,'argv',['round.py',action,'--work',str(w)]),contextlib.redirect_stderr(io.StringIO()):
    try:runner.main();raise AssertionError('unexpected success')
    except RuntimeError as e:error=e
    except ExceptionGroup as e:error=e
   def leaves(e):return sum((leaves(x) for x in e.exceptions),[]) if isinstance(e,ExceptionGroup) else [e]
   assert original in leaves(error) and calls==[action,'cleanup']
   receipt=json.loads((w/'dispatch-failure.json').read_text());assert receipt['auditRegistered']==(failure=='none')
   if failure=='none':runner.require_failure_audit(runner.Round(w))
   else:
    try:runner.require_failure_audit(runner.Round(w))
    except RuntimeError as e:assert str(e)=='dispatch-audit-incomplete'
    else:raise AssertionError('unregistered seal accepted')
   results.append({'action':action,'failure':failure,'cleanupCalls':calls.count('cleanup'),'originalPreserved':True,'auditRegistered':receipt['auditRegistered']})
print(json.dumps({'runtimeCommandsExecuted':0,'cases':results},indent=2))
