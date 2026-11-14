import json,pathlib,sys,tempfile,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parent.parent/'single-policy-test'))
from snapshot import snapshot
from scope import rows,registered_scope
class AuditTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.work=pathlib.Path(self.tmp.name);self.command=['python3','round.py','local'];self.plan={'analysisAllowed':[{'phase':'plan','command':self.command}],'closingAllowed':[]};self.save('plan.json',self.plan);self.save('closing-registry.json',[])
 def tearDown(self):self.tmp.cleanup()
 def save(self,name,value):(self.work/name).write_text(json.dumps(value))
 def test_exact_registered_analysis(self):
  identity=snapshot(self.work,self.command,'plan');self.save('analysis-scope.json',rows(self.work/'snapshots',[identity]));self.assertEqual(len(registered_scope(self.work)['analysis']),1)
 def test_wrong_args_rejected_before_snapshot(self):
  with self.assertRaisesRegex(AssertionError,'analysis-command-not-allowed'):snapshot(self.work,self.command+['--execute'],'plan')
  self.assertFalse((self.work/'snapshots').exists())
 def test_forged_analysis_rejected_at_packaging_gate(self):
  identity=snapshot(self.work,self.command,'plan');p=self.work/'snapshots'/(identity+'.json');meta=json.loads(p.read_text());meta['phase']='exploration';p.write_text(json.dumps(meta));self.save('analysis-scope.json',rows(self.work/'snapshots',[identity]))
  with self.assertRaisesRegex(AssertionError,'analysis-registration-mismatch'):registered_scope(self.work)
 def test_frozen_analysis_cannot_run(self):
  self.save('analysis-scope.json',[])
  with self.assertRaisesRegex(ValueError,'analysis-frozen'):snapshot(self.work,self.command,'plan')
if __name__=='__main__':unittest.main()
