"""Start uncertainty, runtime authority and narrow comparison normalization regressions."""
import contextlib,copy,importlib.util,json,os,pathlib,sys,tempfile,time,unittest
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).parent.parent/'lifecycle'))
import common
import linux_job as job
import compare
class JobTests(unittest.TestCase):
    def test_only_finite_jobs(self):
        for value in ['sh -c true','../reference','reference;exit','']:
            with self.assertRaises(ValueError):job.specification(value)
    def test_never_started_is_not_normal_exit(self):
        for s in [{'Running':False,'Pid':0,'Status':'created','StartedAt':'0001-01-01T00:00:00Z','ExitCode':0},{'Running':False,'Pid':7,'Status':'exited','StartedAt':'2026-11-11','ExitCode':0}]:
            with self.assertRaisesRegex(RuntimeError,'runtime-exit-unclear'):job.runtime_exit({'State':s})
    def test_exit_code_is_runtime_status_not_evaluator_pass(self):
        for code in [0,7]:self.assertEqual(job.runtime_exit({'State':{'Running':False,'Pid':0,'Status':'exited','StartedAt':'2026-11-11','ExitCode':code}}),('exit',code))
        self.assertIsNone(job.runtime_exit({'State':{'Running':True}}))
    def test_oom_is_diagnostic(self):self.assertEqual(job.runtime_exit({'State':{'OOMKilled':True,'ExitCode':137}}),('oom',137))
    def uncertain(self,stage):
        with tempfile.TemporaryDirectory() as t:
            run=pathlib.Path(t)/'0123456789ab';run.mkdir();(run/'lease.json').write_text('{}')
            image={'target':'target','chain':'chain'};state={'job':job.specification('baseline'),'cgroup':'/sys/fs/cgroup/not-this-process','taskSeconds':180,'slice':'test.slice','image':image,'createPending':False,'startPending':False}
            calls=[];cid='a'*64
            def read(p):return {'mono':time.monotonic()} if p.name=='lease.json' else state.copy()
            def update(r,**kw):state.update(kw);return state.copy()
            def command(r,args,**kw):
                calls.append(args)
                self.assertIn('workStarted',state);self.assertEqual(state['deadlineMono'],state['workStarted']['mono']+180)
                if 'create' in args:return (124,'','timeout') if stage=='create' else (0,cid,'')
                if 'inspect' in args:return (0,json.dumps([{'Image':'image','Labels':{'nerdctl/image-digest':'target'},'SnapshotInfo':{'Parent':'chain'}}]),'')
                if 'start' in args:raise RuntimeError('start-timeout')
                raise AssertionError(args)
            with patch.object(pathlib.Path,'read_text',return_value='0::/supervisor\n'),patch.object(os,'readlink',return_value='cgroup:[fixture]'),patch.multiple(job,read=read,state=update,command=command,write=lambda *a:None,lock=lambda *a:contextlib.nullcontext(),identify=lambda *a:image):
                with self.assertRaisesRegex(RuntimeError,'job-create-unsettled|start-timeout'):job.supervise_job(run)
            self.assertTrue(state[stage+'Pending']);self.assertNotIn('terminationConfirmed',state)
            self.assertEqual(len([c for c in calls if 'start' in c]),0 if stage=='create' else 1)
    def test_create_timeout_stays_pending(self):self.uncertain('create')
    def test_start_timeout_stays_pending(self):self.uncertain('start')
    def test_empty_cgroup_cannot_clear_pending_create_or_start(self):
        for field in ['createPending','startPending']:
            with tempfile.TemporaryDirectory() as t:
                root=pathlib.Path(t);run=root/'0123456789ab';run.mkdir();cg=root/'group';cg.mkdir();(cg/'cgroup.kill').touch()
                common.write(run/'state.json',{'state':'running',field:True,'cgroup':str(cg),'runId':run.name});common.write(root/'gate.json',{'runId':run.name,'allowNext':False})
                with patch.object(common,'ROOT',root),patch.object(common,'cgroup_snapshot',return_value={'events':{'populated':'0'},'members':[]}):
                    with self.assertRaisesRegex(RuntimeError,'runtime-request-unsettled'):common.stop_confirm(run)
                self.assertFalse((run/'termination.json').exists())
class ComparisonTests(unittest.TestCase):
    def sample(self):
        aliases=compare.policy['rootCorrespondence']
        return {'environment':{'cost':{'wallTimeMs':1}},'environmentRecheck':{'wallTimeMs':1},'behavior':{'cost':{'wallTimeMs':1},'cases':[{'payload':{'orderId':'correct'}}]},'typecheck':{'cost':{'wallTimeMs':1},'checkedFiles':[{'file':x['macOS'],'sha256':x['sha256']} for x in aliases],'inputHashes':{x['macOS']:x['sha256'] for x in aliases},'diagnostics':[]}}
    def test_exact_aliases_preserve_bytes_and_original(self):
        original=self.sample();saved=copy.deepcopy(original);actual=compare.normalized(original,'macOS');self.assertEqual(original,saved)
        self.assertEqual(len(actual['typecheck']['checkedFiles']),9);self.assertEqual(set(actual['typecheck']['inputHashes'].values()),set(original['typecheck']['inputHashes'].values()))
    def test_alias_cannot_hide_hash_change_or_collision(self):
        for mode in ['hash','collision','duplicate']:
            data=self.sample();alias=compare.policy['rootCorrespondence'][0]
            if mode=='hash':data['typecheck']['checkedFiles'][0]['sha256']='different'
            if mode=='collision':data['typecheck']['inputHashes'][alias['linux']]=alias['sha256']
            if mode=='duplicate':data['typecheck']['checkedFiles'].append(data['typecheck']['checkedFiles'][0].copy())
            with self.assertRaises(AssertionError):compare.normalized(data,'macOS')
    def test_payload_and_diagnostics_are_never_ignored(self):
        a=compare.normalized(self.sample(),'macOS');b=copy.deepcopy(a);b['behavior']['cases'][0]['payload']['orderId']='wrong';b['typecheck']['diagnostics']=[{'code':123}]
        paths={x['path'] for x in compare.compare(a,b)};self.assertIn('/behavior/cases/0/payload/orderId',paths);self.assertIn('/typecheck/diagnostics/length',paths)
if __name__=='__main__':unittest.main(verbosity=2)
