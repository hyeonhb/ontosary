"""Test-only external fake runtime: exercise real CLI dispatch/state/publication paths."""
import json,os,pathlib,shutil,sys,time
root=pathlib.Path(os.environ['S2_TEST_ROOT']);db=root/'fake.json';s=json.loads(db.read_text());args=sys.argv[1:]
with (root/'fake-calls.jsonl').open('a') as f:f.write(json.dumps(args)+'\n')
if args[0] in ['nerdctl','ctr']:
 tool=args[0];args=args[1:]
 for option in ['--address','--namespace']:
  if option in args:i=args.index(option);del args[i:i+2]
 if s.get('queryFail') and args[0] in ['inspect','containers','tasks']:sys.exit(7)
 if tool=='ctr':
  if args==['containers','list','-q']:print(s['cid'] if s['present'] else '')
  elif args==['tasks','list']:print('TASK PID STATUS')
  else:raise RuntimeError(args)
 elif args[0]=='inspect':
  if not s['present']:sys.exit(4)
  if '--mode=native' in args:
   print(json.dumps([{'ID':s['cid'],'Labels':{'nerdctl/image-digest':'image'},'SnapshotInfo':{'Parent':'chain'},'Spec':{'annotations':{'nerdctl/name':'ontosary-'+s['rid']},'linux':{'cgroupsPath':('foreign' if s.get('foreign') else 'ontosary-'+s['rid']+'.slice')+':nerdctl:'+s['cid']}}}]))
  else:print(json.dumps([{'State':{'Running':False,'Pid':0,'ExitCode':0}}]))
 elif args[0]=='rm':
  if s.get('removeFail'):sys.exit(9)
  s['present']=False;db.write_text(json.dumps(s))
 elif args[0]=='create':
  if s.get('requestTimeout'):time.sleep(1)
  s['present']=True;db.write_text(json.dumps(s));print(s['cid']);sys.exit(s.get('requestExit',0))
 elif args[0]=='start':
  if s.get('requestExit'):print('exec /missing-fixture-entrypoint: no such file or directory',file=sys.stderr)
  sys.exit(s.get('requestExit',0))
 else:raise RuntimeError(args)
elif args[0]=='systemctl':
 if args[1]=='stop':shutil.rmtree(root/'cgroup')
 elif args[1]=='show':print('ActiveState=inactive\nInactiveEnterTimestampMonotonic='+str(int(time.monotonic()*1000000)))
 elif args[1]!='daemon-reload':raise RuntimeError(args)
else:raise RuntimeError(args)
