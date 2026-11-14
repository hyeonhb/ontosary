import datetime,json,pathlib,sys,tempfile,time
from unittest.mock import patch
base=pathlib.Path('experiments/domain-model/s2/trial/container/execution-lifecycle').resolve();sys.path.insert(0,str(base));import round as r
calls=[]
class StopAtBuild(Exception):pass
class FakeStore:
 def __init__(self,*a,**kw):pass
 def acquire(self,req,*a):calls.append(['acquire',req['name']]);return {'path':'/existing/verified/data','cacheHit':True}
 def lookup(self,req,*a):calls.append(['lookup',req['name']]);return {'path':'/existing/verified/data','cacheHit':True}
with tempfile.TemporaryDirectory() as tmp:
 w=pathlib.Path(tmp);obj=r.Round.__new__(r.Round);obj.w=w;obj.root=w/'vm';obj.plan={'vmRoot':str(obj.root),'vmName':'fake','store':str(w/'store'),'round':'review'};obj.budget={'deadlines':{'environment':{'monotonic':time.monotonic()+1200}},'environmentEntered':{'mono':time.monotonic()}};obj.lima='fake-lima';obj.env={};obj.shell=['fake-shell'];obj.action='prepare'
 (w/'local-gate.json').write_text(json.dumps({'passed':True,'codeHashes':{}}))
 for n in ['budget.json','prior-pair.json']:(w/n).write_text('{}')
 obj.cmd=lambda *a,**kw: ({'exitCode':0},'')
 def guest(args,**kw):
  calls.append(['guest',args])
  if args[0]=='python3' and args[1]=='-c':return ({'exitCode':0},json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'guestMonotonic':time.monotonic()}))
  if args[-1]=='prepare':raise StopAtBuild()
  return ({'exitCode':0},'')
 obj.guest=guest
 with patch.object(r,'Store',FakeStore),patch.object(r,'limit',lambda *a:1200):
  try:obj.prepare()
  except StopAtBuild:pass
result={'mockedExternalCommands':True,'runtimeStarted':False,'allRequestedArtifactsWereCacheHits':True,'reachedUnconditionalGuestBuild':any(c[0]=='guest' and c[1][-1]=='prepare' for c in calls),'imageLookupBeforeBuild':any(c[0] in ['lookup','acquire'] and c[1]=='ontosary-fixed-trace-image' for c in calls),'calls':calls}
print(json.dumps(result,indent=2))
assert result['reachedUnconditionalGuestBuild'] and not result['imageLookupBeforeBuild']
