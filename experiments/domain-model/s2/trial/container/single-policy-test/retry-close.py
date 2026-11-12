"""Register closing before execution, validate in temporary output, then publish once."""
import argparse,datetime,importlib.util,json,pathlib,re,shutil,subprocess,tempfile,time,urllib.parse
from snapshot import snapshot
from scope import registered_scope,verify_index
from package import package
p=argparse.ArgumentParser();p.add_argument('--work',required=True);a=p.parse_args();work=pathlib.Path(a.work);base=pathlib.Path(__file__).parent;budget=json.loads((work/'budget.json').read_text());plan=json.loads((work/'plan.json').read_text());out=pathlib.Path(plan['output']);base=pathlib.Path(plan['source'])
command=['python3',str(base/'retry-close.py'),'--work',str(work)];snapshot(work,command,'finish','closing');registered_scope(work)
# Prepublication reproduction uses the same package entry point on a temporary copy.
(work/'cost.json').write_text(json.dumps({'status':'finalization-in-progress'})+'\n')
spec=importlib.util.spec_from_file_location('retry_verify',base/'retry-verify.py');verify=importlib.util.module_from_spec(spec);spec.loader.exec_module(verify)
with tempfile.TemporaryDirectory() as temporary:
 temp=pathlib.Path(temporary);copy=temp/'work';shutil.copytree(work,copy,ignore=shutil.ignore_patterns('guest','removal','__pycache__'));temporary_plan=dict(plan);temporary_plan['output']=str(temp/'evidence');(copy/'plan.json').write_text(json.dumps(temporary_plan)+'\n')
 package(copy,temp/'evidence');pre=verify.verify(temp/'evidence')
(work/'prepublication-verification.json').write_text(json.dumps(pre,indent=2)+'\n')
now=datetime.datetime.now(datetime.timezone.utc);mono=time.monotonic();seconds=mono-budget['monotonic'];prior=budget['previousMeasuredSeconds'];assert seconds+5<45*60
cost={'status':'closed','startedUtc':budget['utc'],'measuredUntilUtc':now.isoformat(),'startedMonotonic':budget['monotonic'],'measuredUntilMonotonic':mono,'roundMeasuredSeconds':seconds,'previousMeasuredSeconds':prior,'cumulativeMeasuredSeconds':prior+seconds,'previousSerializationUpperBoundSeconds':5,'currentSerializationUpperBoundSeconds':5,'cumulativeUpperBoundSeconds':prior+seconds+10,'roundUpperBoundSeconds':seconds+5,'newPaidCost':0,'gitDeliveryIncluded':False,'completion':{'fixes':'verified','observation':'blocked-inconclusive','resources':'removed'},'runtimeRetries':0,'preStartMechanicalRetries':0}
(work/'cost.json').write_text(json.dumps(cost,indent=2)+'\n')
report=pathlib.Path('docs/reviews/2026-11-12-s2-policy-retry.md');report.write_text(report.read_text().replace('ROUND_SECONDS',f'{seconds:.3f}').replace('CUMULATIVE_SECONDS',f'{prior+seconds:.3f}'))
result=package(work,out);verified=verify.verify(out)
files=['docs/PROGRESS.md','docs/ARCHITECTURE.md','docs/ROADMAP.md','docs/DECISIONS.md','docs/reviews/REVIEW_CONTEXT.md',str(report)];links=0
for name in files:
 path=pathlib.Path(name)
 for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
  if target.startswith(('http:','https:','#','mailto:')):continue
  target=urllib.parse.unquote(target.split('#')[0]);assert (path.parent/target).exists(),(name,target);links+=1
changed=subprocess.check_output(['git','diff','--name-only','HEAD'],text=True).splitlines();assert all(p in files or p.startswith(str(base)+'/') or p.startswith(str(out)+'/') for p in changed),changed
tail=time.monotonic()-mono;assert tail<=5
print(json.dumps({'verified':verified,'localLinks':links,'roundMeasuredSeconds':seconds,'finalSerializationSeconds':tail,'roundActualSeconds':seconds+tail,'finishedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat()}))
