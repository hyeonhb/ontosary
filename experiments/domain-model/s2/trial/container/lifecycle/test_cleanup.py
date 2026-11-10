"""Publication and unsettled-request regressions without a container runtime."""
import json,os,pathlib,tempfile,unittest
from unittest.mock import patch
import common
class CleanupTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.temp.name);self.run=self.root/'0123456789ab';self.run.mkdir();(self.run/'result').mkdir();(self.run/'result/fixture.json').write_text('{"fixtureOnly":true,"validSubmission":false}')
        self.group=self.root/'group';self.group.mkdir();(self.group/'cgroup.kill').write_text('')
        self.s={'runId':self.run.name,'state':'finalized','cleanupDone':False,'containerId':'immutable','image':{'target':'current'},'cgroup':str(self.group),'cgroupInode':self.group.stat().st_ino,'reason':'exit','exitCode':0}
        common.write(self.run/'state.json',self.s);common.write(self.root/'gate.json',{'runId':self.run.name,'allowNext':False})
        self.root_patch=patch.object(common,'ROOT',self.root);self.root_patch.start()
        self.kernel_patch=patch.object(common,'cgroup_snapshot',return_value={'events':{'populated':'0'},'members':[]});self.kernel_patch.start()
    def tearDown(self):self.kernel_patch.stop();self.root_patch.stop();self.temp.cleanup()
    def test_service_death_revokes_already_published_result(self):
        with patch.dict(os.environ,{'SERVICE_RESULT':'signal'}),patch.object(common,'stop_confirm',return_value={'confirmed':True}):common.cleanup(self.run)
        self.assertFalse((self.run/'result').exists());self.assertTrue((self.run/'quarantined-result/fixture.json').exists())
        state=common.read(self.run/'state.json');self.assertEqual(state['state'],'blocked');self.assertTrue(state['cleanupDone']);self.assertIsNone(state['classification']);self.assertFalse(common.read(self.root/'gate.json')['allowNext'])
    def test_manual_cleanup_cannot_preempt_systemd_success(self):
        response=(0,json.dumps([{'State':{'Running':False}}]),'')
        with patch.dict(os.environ,{},clear=True),patch.object(common,'command',return_value=response):common.cleanup(self.run)
        self.assertFalse(common.read(self.run/'state.json')['cleanupDone']);self.assertFalse(common.read(self.root/'gate.json')['allowNext'])
        with patch.dict(os.environ,{'SERVICE_RESULT':'success'}),patch.object(common,'command',return_value=response):common.cleanup(self.run)
        self.assertTrue(common.read(self.run/'state.json')['cleanupDone']);self.assertTrue(common.read(self.root/'gate.json')['allowNext'])
    def test_empty_parent_does_not_settle_an_unknown_exec_request(self):
        common.state(self.run,state='running',execPending=True)
        with self.assertRaisesRegex(RuntimeError,'runtime-request-unsettled'):common.stop_confirm(self.run)
        self.assertEqual((self.group/'cgroup.kill').read_text(),'1')
        self.assertFalse((self.run/'termination.json').exists());self.assertFalse(common.read(self.root/'gate.json')['allowNext'])
if __name__=='__main__':unittest.main(verbosity=2)
