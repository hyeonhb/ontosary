import datetime,importlib.util,io,json,os,pathlib,sys,tarfile,tempfile,time,unittest
from unittest.mock import patch
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
spec=importlib.util.spec_from_file_location('smoke_run',HERE/'run.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class SmokeTests(unittest.TestCase):
    def owned(self,root,expired=False):
        work=root/'work';work.mkdir();owned=root/'ontosary-s2-local-test';(owned/'prefix/bin').mkdir(parents=True);(owned/'prefix/bin/limactl').touch()
        m.write(work/'plan.json',{'root':str(owned),'name':'smoke-test'})
        now=datetime.datetime.now(datetime.timezone.utc);delta=-1 if expired else 20
        m.write(work/'budget.json',{'deadlines':{key:{'utc':(now+datetime.timedelta(seconds=delta)).isoformat(),'monotonic':time.monotonic()+delta} for key in ['experiment','finish']}})
        m.write(work/'ownership.json',{'root':str(owned),'name':'smoke-test','vmRegistered':True})
        return m.Smoke(work)
    def fake(self,calls):
        def run(args,seconds,**kw):
            calls.append(args)
            return {'args':args,'exitCode':1 if args[0]=='fake-prepare' else 0,'stdout':'','stderr':'synthetic preparation error' if args[0]=='fake-prepare' else '', 'truncated':False,'timedOut':False}
        return run
    def assert_disposal(self,calls):
        self.assertEqual([a[1] for a in calls if len(a)>1 and a[0].endswith('limactl')],['stop','delete','list'])
        self.assertTrue(any(a[0]=='ps' for a in calls))
    def test_external_preparation_error_reaches_real_cleanup_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            s=self.owned(pathlib.Path(tmp).resolve());calls=[]
            # Inject the external preparation failure; execute/cmd/dispose/cleanup are real.
            with patch.object(s,'work',lambda:s.cmd(['fake-prepare'])),patch.object(m,'capture',self.fake(calls)):
                r=m.execute(s)
            self.assert_disposal(calls);self.assertEqual(r['cleanup']['cleanupStatus'],'complete');self.assertFalse(s.root.exists())
    def test_expired_watchdog_still_stops_deletes_and_checks_absence(self):
        with tempfile.TemporaryDirectory() as tmp:
            s=self.owned(pathlib.Path(tmp).resolve(),expired=True);calls=[]
            with patch.object(m,'capture',self.fake(calls)):m.watch(s,os.getpid())
            self.assert_disposal(calls);self.assertTrue((s.w/'disposed').exists())
    def test_diagnostic_failure_cannot_skip_disposal(self):
        with tempfile.TemporaryDirectory() as tmp:
            s=self.owned(pathlib.Path(tmp).resolve());calls=[];real=m.write
            def fail_result(path,value):
                if pathlib.Path(path).name=='result.json':raise OSError('diagnostic failure')
                return real(path,value)
            with patch.object(s,'work',lambda: {}),patch.object(m,'capture',self.fake(calls)),patch.object(m,'write',fail_result):
                with self.assertRaisesRegex(OSError,'diagnostic failure'):m.execute(s)
            self.assert_disposal(calls);self.assertFalse(s.root.exists())
    def test_stop_error_does_not_skip_delete_or_absence(self):
        with tempfile.TemporaryDirectory() as tmp:
            s=self.owned(pathlib.Path(tmp).resolve());calls=[];fake=self.fake(calls)
            def run(args,seconds,**kw):
                r=fake(args,seconds,**kw)
                if len(args)>1 and args[1]=='stop':raise TimeoutError('fake stop timeout')
                return r
            with patch.object(m,'capture',run):result=s.dispose()
            self.assert_disposal(calls);self.assertEqual(result['cleanupStatus'],'complete');self.assertEqual(result['errors'][0]['action'],'stop')
    def test_expired_work_command_is_not_dispatched(self):
        with tempfile.TemporaryDirectory() as tmp:
            s=self.owned(pathlib.Path(tmp).resolve(),expired=True)
            with patch.object(m,'capture') as call:
                with self.assertRaises(Exception):s.cmd(['fake-command'])
                call.assert_not_called()
    def test_actual_host_hash_and_filtered_extraction_api(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp);(root/'file').write_bytes(b'abc')
            self.assertEqual(m.sha(root/'file'),'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
            with tarfile.open(root/'safe.tar','w') as t:
                i=tarfile.TarInfo('public');i.size=3;t.addfile(i,io.BytesIO(b'abc'))
            r=m.capture([m.PYTHON,'-c','import tarfile,sys;tarfile.open(sys.argv[1]).extractall(sys.argv[2],filter="data")',str(root/'safe.tar'),str(root/'dest')],3)
            self.assertEqual(r['exitCode'],0);self.assertEqual((root/'dest/public').read_bytes(),b'abc')
            with tarfile.open(root/'bad.tar','w') as t:
                i=tarfile.TarInfo('../escape');i.size=1;t.addfile(i,io.BytesIO(b'x'))
            r=m.capture([m.PYTHON,'-c','import tarfile,sys;tarfile.open(sys.argv[1]).extractall(sys.argv[2],filter="data")',str(root/'bad.tar'),str(root/'blocked')],3)
            self.assertNotEqual(r['exitCode'],0);self.assertFalse((root/'escape').exists())
    def test_bounded_command_reports_timeout_and_truncation(self):
        r=m.capture([m.PYTHON,'-c','import time;time.sleep(10)'],.1);self.assertTrue(r['timedOut'])
        r=m.capture([m.PYTHON,'-c','print("x"*1024)'],2,cap=32);self.assertTrue(r['truncated']);self.assertLessEqual(len(r['stdout']),32)
    def test_payload_result_requires_all_markers_content_exit_and_no_truncation(self):
        w={'runId':'synthetic','native':{'stdout':'\n'.join(json.dumps(x) for x in [{'event':'payload-start','runId':'synthetic'},{'event':'payload-complete','runId':'synthetic','sourceRead':True,'sourceWrite':True,'materialRead':True}]),'exitCode':0},'outputContent':'smoke output synthetic\n','configUnchanged':True};outer={'exitCode':0}
        self.assertEqual(m.verdict(w,outer),'payload-completed')
        for mutation in ['truncated','exit','missing','content']:
            v=json.loads(json.dumps(w))
            if mutation=='truncated':v['native']['truncated']=True
            elif mutation=='exit':v['native']['exitCode']=1
            elif mutation=='missing':v['native']['stdout']=v['native']['stdout'].splitlines()[0]
            else:v['outputContent']='wrong'
            self.assertNotEqual(m.verdict(v,outer),'payload-completed')
        self.assertEqual(m.verdict({'runId':'synthetic','native':{'stdout':'','stderr':'EPERM','exitCode':1}},outer),'blocked-before-payload')
if __name__=='__main__':unittest.main()
