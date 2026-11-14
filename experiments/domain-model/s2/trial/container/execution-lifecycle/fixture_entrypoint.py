"""Subprocess adapter exclusively for tests; no production alternate backend."""
import os,pathlib,sys
import engine as e
root=pathlib.Path(os.environ['S2_TEST_ROOT']);e.c.ROOT=root;e.UNITS=root/'units';e.SHARED=root/'shared'
e.c.NERD=[sys.executable,str(pathlib.Path(__file__).with_name('fixture_runtime_cli.py')),'nerdctl'];e.c.CTR=[sys.executable,str(pathlib.Path(__file__).with_name('fixture_runtime_cli.py')),'ctr']
original=e.command
# External subprocess runs a CLI fixture, never a mocked return value for runtime errors.
def cmd(run,args,phase='remove',timeout=3,check=True):
 if args[0]=='systemctl':args=[sys.executable,str(pathlib.Path(__file__).with_name('fixture_runtime_cli.py')),*args]
 env={**e.MANAGER_ENV,'S2_TEST_ROOT':str(root)}
 return e.c.command(run,args,timeout,check,env=env,deadline=e.deadline(run,phase))
e.command=cmd
common_command=e.c.command
def common_cmd(run,args,*a,**kw):
 kw['env']={**(kw.get('env') or {}),'S2_TEST_ROOT':str(root)}
 return common_command(run,args,*a,**kw)
e.c.command=common_cmd
if sys.argv[1]=='test-request':
 run=e.c.runpath(sys.argv[2]);e.request(run,sys.argv[3],e.c.NERD+[sys.argv[3]],.05)
else:e.main()
