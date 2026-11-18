"""Real subprocess/state transitions; every external control command is a local fake."""
import contextlib,datetime,importlib.util,json,pathlib,sys,tempfile,time,unittest
from unittest.mock import patch

HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
spec=importlib.util.spec_from_file_location('cleanup_budget_smoke',HERE/'run.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

FAKE='''import json,pathlib,sys,time
base=pathlib.Path(BASE)
action=sys.argv[1]
cfg=json.loads((base/'scenario.json').read_text())
mode=cfg.get(action,'normal')
if action in ('stop','delete'):
 print('progress '+action,flush=True)
 if mode=='noisy':
  for _ in range(20):
   sys.stdout.write('x'*65536);sys.stdout.flush()
   sys.stderr.write('y'*65536);sys.stderr.flush()
 if mode=='hang':time.sleep(10)
 if mode=='fail':sys.exit(7)
 time.sleep(.15)
 (base/(action+'.done')).write_text('complete')
 if action=='delete':(base/'vm.json').unlink(missing_ok=True)
elif action in ('list','ps'):
 if mode=='hang':time.sleep(10)
 if mode=='fail':sys.exit(8)
 if mode=='malformed':print('not-json');sys.exit(0)
 if mode=='wrong-type':print('[]');sys.exit(0)
 if mode=='truncated':print(' '*1100000);sys.exit(0)
 if action=='list' and (base/'vm.json').exists():print((base/'vm.json').read_text())
 if action=='ps' and mode=='present':print('123 '+cfg['ownedRoot']+'/prefix/bin/still-running')
'''

def scenario(name='normal',commands=None,fault=None):
    with tempfile.TemporaryDirectory(prefix='s2-r20-local-') as tmp:
        base=pathlib.Path(tmp).resolve();work=base/'work';work.mkdir()
        owned=base/'ontosary-s2-fake';tool=owned/'prefix/bin/limactl';tool.parent.mkdir(parents=True)
        tool.write_text('#!'+m.PYTHON+'\nBASE='+repr(str(base))+'\n'+FAKE);tool.chmod(0o700)
        fake_ps=base/'fake_ps.py';fake_ps.write_text('BASE='+repr(str(base))+'\n'+FAKE)
        m.write(base/'scenario.json',{'ownedRoot':str(owned),**(commands or {})})
        m.write(base/'vm.json',{'name':'fixture-vm'})
        m.write(work/'plan.json',{'root':str(owned),'name':'fixture-vm'})
        now=datetime.datetime.now(datetime.timezone.utc)
        m.write(work/'budget.json',{'deadlines':{'experiment':{'utc':(now-datetime.timedelta(seconds=1)).isoformat(),'monotonic':time.monotonic()-1}}})
        m.write(work/'ownership.json',{'root':str(owned),'name':'fixture-vm','vmRegistered':True})
        if name=='exhausted':
            left=4*1024**2-65536
            for i in range(4):
                size=min(left,1024**2);(work/f'old-{i}.stdout').write_bytes(b'x'*size);left-=size
        smoke=m.Smoke(work);real=m.capture;calls=[]
        def external(args,seconds,**kw):
            calls.append(list(args))
            if args[0]=='ps':args=[m.PYTHON,str(fake_ps),'ps']
            action=args[-1] if args[0]==m.PYTHON else args[1]
            return real(args,min(seconds,.25 if (commands or {}).get(action)=='hang' else 3),**kw)
        before=sum(p.stat().st_size for p in work.glob('*.stdout'))
        started=time.monotonic()
        with patch.object(m,'capture',external):
            if fault:
                with fault(smoke):result=smoke.dispose()
            else:result=smoke.dispose()
        return {'condition':name,'result':result,'stopCompleted':(base/'stop.done').exists(),
                'deleteCompleted':(base/'delete.done').exists(),'vmStatePresent':(base/'vm.json').exists(),
                'ownedRootPresent':owned.exists(),'seconds':time.monotonic()-started,'actions':[a[1] for a in calls if a[0]==str(tool)],
                'storedTotalBytesAfter':sum(p.stat().st_size for p in work.iterdir() if p.is_file()),
                'storedStreamBytesBefore':before,'storedStreamBytesAfter':sum(p.stat().st_size for pattern in ['*.stdout','*.stderr'] for p in work.glob(pattern))}

class CleanupBudgetTests(unittest.TestCase):
    def test_normal_and_exhausted_budget_reach_real_completion(self):
        for name in ['normal','exhausted']:
            with self.subTest(name=name):
                row=scenario(name)
                self.assertTrue(row['stopCompleted']);self.assertTrue(row['deleteCompleted'])
                self.assertFalse(row['vmStatePresent']);self.assertFalse(row['ownedRootPresent'])
                self.assertEqual(row['result']['cleanupStatus'],'complete')
                self.assertEqual(row['actions'],['stop','delete','list'])
                self.assertLessEqual(row['storedStreamBytesAfter'],4*1024**2-65536)
                self.assertLessEqual(row['storedTotalBytesAfter'],4*1024**2)

    def test_diagnostic_lookup_failure_does_not_prevent_completion(self):
        row=scenario(fault=lambda s:patch.object(s,'diagnostic_capacity',side_effect=OSError('scan denied')))
        self.assertTrue(row['stopCompleted'] and row['deleteCompleted']);self.assertFalse(row['vmStatePresent'])
        self.assertEqual(row['result']['cleanupStatus'],'complete')
        self.assertEqual(len(row['result']['diagnosticErrors']),3)

    def test_command_stream_and_metadata_write_failures_do_not_prevent_completion(self):
        for target in ['stream','metadata']:
            @contextlib.contextmanager
            def fault(s):
                real=m.write
                def write(path,value):
                    if pathlib.Path(path).name.startswith('command-'):raise OSError('metadata full')
                    return real(path,value)
                with (patch.object(pathlib.Path,'write_bytes',side_effect=OSError('stream full')) if target=='stream' else patch.object(m,'write',write)):yield
            with self.subTest(target=target):
                row=scenario(fault=fault)
                self.assertTrue(row['stopCompleted'] and row['deleteCompleted']);self.assertFalse(row['vmStatePresent'])
                self.assertEqual(row['result']['cleanupStatus'],'complete');self.assertEqual(len(row['result']['diagnosticErrors']),3)

    def test_all_report_writes_can_fail_after_real_cleanup(self):
        row=scenario(fault=lambda s:patch.object(m,'write',side_effect=OSError('disk full')))
        self.assertFalse(row['ownedRootPresent']);self.assertFalse(row['vmStatePresent'])
        self.assertEqual(row['result']['cleanupStatus'],'complete');self.assertFalse(row['result']['receiptWritten'])
        self.assertTrue(any(x['action']=='cleanup-receipt' for x in row['result']['diagnosticErrors']))

    def test_disposed_marker_failure_is_a_diagnostic_error(self):
        row=scenario(fault=lambda s:patch.object(pathlib.Path,'touch',side_effect=OSError('marker full')))
        self.assertFalse(row['vmStatePresent']);self.assertEqual(row['result']['cleanupStatus'],'complete')
        self.assertTrue(any(x['action']=='disposed-marker' for x in row['result']['diagnosticErrors']))

    def test_unreadable_prior_receipt_does_not_skip_cleanup(self):
        @contextlib.contextmanager
        def fault(s):
            (s.w/'disposed').touch();(s.w/'cleanup.json').write_text('partial json')
            yield
        row=scenario(fault=fault)
        self.assertTrue(row['stopCompleted'] and row['deleteCompleted']);self.assertFalse(row['vmStatePresent'])
        self.assertTrue(any(x['action']=='prior-receipt' for x in row['result']['diagnosticErrors']))

    def test_existing_owner_lock_needs_no_writable_diagnostic_file(self):
        @contextlib.contextmanager
        def fault(s):
            real=pathlib.Path.open
            def opened(path,mode='r',*args,**kw):
                if path.parent==s.w and any(c in mode for c in 'wax+'):raise OSError('diagnostics read-only')
                return real(path,mode,*args,**kw)
            with patch.object(pathlib.Path,'open',opened):yield
        row=scenario(fault=fault)
        self.assertTrue(row['stopCompleted'] and row['deleteCompleted']);self.assertFalse(row['ownedRootPresent'])
        self.assertEqual(row['result']['cleanupStatus'],'complete');self.assertFalse(row['result']['receiptWritten'])

    def test_owner_mismatch_blocks_dispatch_and_cached_receipt(self):
        @contextlib.contextmanager
        def fault(s):
            m.write(s.w/'ownership.json',{'root':str(s.root),'name':'someone-else','vmRegistered':True})
            (s.w/'disposed').touch()
            with patch.object(m,'capture',side_effect=AssertionError('must not dispatch')):yield
        with self.assertRaisesRegex(RuntimeError,'cleanup-ownership'):scenario(fault=fault)

    def test_noisy_cleanup_completes_with_bounded_storage(self):
        row=scenario(commands={'stop':'noisy','delete':'noisy'})
        self.assertTrue(row['stopCompleted'] and row['deleteCompleted']);self.assertFalse(row['vmStatePresent'])
        self.assertEqual(row['result']['cleanupStatus'],'complete')
        self.assertTrue(all(r['truncated'] for r in row['result']['commandResults'][:2]))
        self.assertLessEqual(row['storedTotalBytesAfter'],4*1024**2)

    def test_stop_failure_or_timeout_does_not_prevent_delete(self):
        for mode in ['fail','hang']:
            with self.subTest(mode=mode):
                row=scenario(commands={'stop':mode})
                self.assertFalse(row['stopCompleted']);self.assertTrue(row['deleteCompleted'])
                self.assertFalse(row['vmStatePresent']);self.assertEqual(row['result']['cleanupStatus'],'complete')
                self.assertTrue(any(x['action']=='stop' for x in row['result']['errors']));self.assertLess(row['seconds'],6)

    def test_delete_failure_or_timeout_keeps_state_unconfirmed(self):
        for mode in ['fail','hang']:
            with self.subTest(mode=mode):
                row=scenario(commands={'delete':mode})
                self.assertEqual(row['actions'],['stop','delete','list'])
                self.assertTrue(row['vmStatePresent']);self.assertTrue(row['ownedRootPresent'])
                self.assertEqual(row['result']['cleanupStatus'],'unconfirmed');self.assertLess(row['seconds'],6)

    def test_incomplete_or_malformed_listing_never_proves_absence(self):
        for mode in ['fail','hang','truncated','malformed','wrong-type']:
            with self.subTest(mode=mode):
                row=scenario(commands={'list':mode})
                self.assertTrue(row['deleteCompleted']);self.assertFalse(row['vmStatePresent'])
                self.assertTrue(row['ownedRootPresent']);self.assertFalse(row['result']['vmAbsent'])
                self.assertEqual(row['result']['cleanupStatus'],'unconfirmed');self.assertLess(row['seconds'],6)

    def test_process_query_failure_or_presence_never_proves_absence(self):
        for mode in ['fail','hang','truncated','malformed','present']:
            with self.subTest(mode=mode):
                row=scenario(commands={'ps':mode})
                self.assertFalse(row['vmStatePresent']);self.assertTrue(row['ownedRootPresent'])
                self.assertEqual(row['result']['cleanupStatus'],'unconfirmed');self.assertLess(row['seconds'],6)

    def test_discard_still_times_out_even_after_pipe_eof(self):
        row=m.capture([m.PYTHON,'-c','import os,time;os.close(1);os.close(2);time.sleep(10)'],.2,overflow='discard')
        self.assertTrue(row['timedOut']);self.assertNotEqual(row['exitCode'],0);self.assertLess(row['seconds'],4)

    def test_general_output_overflow_still_stops_before_side_effect(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=pathlib.Path(tmp)/'must-not-exist'
            row=m.capture([m.PYTHON,'-c','import pathlib,sys,time;print("x"*100,flush=True);time.sleep(.3);pathlib.Path(sys.argv[1]).touch()',str(target)],2,cap=16)
            self.assertTrue(row['truncated']);self.assertNotEqual(row['exitCode'],0);self.assertFalse(target.exists())

if __name__=='__main__':unittest.main()
