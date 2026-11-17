import copy,io,json,pathlib,sys,tarfile,tempfile,unittest
from unittest.mock import patch
import round as runner,policy_pair as pair,verify_pair
import test_dispatch as dispatch

class PairTests(unittest.TestCase):
 def setUp(self):
  self.base=dispatch.DispatchTests();self.base.setUp();self.w=self.base.w;self.calls=[]
  p=self.base.plan;p.update(purpose=pair.PURPOSE,fixtures=['baseline','candidate'],maximumUnits=2,maximumVMs=1,cacheOnly=True,maximumImageBuilds=0,candidateRule=copy.deepcopy(pair.RULE),payloadSeconds=15,phaseSeconds={'work':80,'remove':110,'finish':120},fixtureOnly=True,validSubmission=False,trialAuthorized=False,readyForTrial=False,results=None,historicalGate={'path':str(pair.HISTORY),'indexSha256':pair.HISTORY_SHA,'requiredUnits':7,'passedUnits':7})
  p['analysisAllowed'].append({'phase':'exploration','command':['python3',str(runner.HERE/'round.py'),'pair','--work',str(self.w)]});runner.write(self.w/'plan.json',p);self.plan=p
  runner.write(self.w/'preparation-complete.json',{});runner.write(self.w/'local-gate.json',{'passed':True,'codeHashes':{str(runner.HERE/'round.py'):runner.sha(runner.HERE/'round.py')}})
  with tarfile.open('experiments/domain-model/s2/verification/2026-11-12-policy-retry/host/guest-evidence.tar.gz') as t:self.result=json.load(t.extractfile('baseline-result.json'));self.native=json.load(t.extractfile('baseline/native.json'))
  self.observed=pair.trace_observation(self.result)
 def tearDown(self):self.base.tearDown()
 def unit(self,r,mode):
  self.calls.append(mode);rows=runner.read(self.w/'units.json') if (self.w/'units.json').exists() else [];rows.append({'mode':mode,'runId':'a'*12 if mode=='baseline' else 'b'*12});runner.write(self.w/'units.json',rows);return rows[-1]['runId']
 def recovered(self,r,mode,rid):return {'runs/'+rid+'/native.json':json.dumps(self.native).encode()},'runs/'+rid+'/',self.result,self.observed
 def invoke(self,unit=None,recovered=None,audit_failure=False):
  def clean(r):self.calls.append('cleanup')
  def guest(r,args,**kw):self.calls.append('profile');return {'exitCode':0},''
  real=runner.write
  def write(p,v):
   if audit_failure and p.name=='analysis-scope.json':raise OSError('audit-failure')
   return real(p,v)
  with patch.object(runner.Round,'unit',unit or (lambda r,m:self.unit(r,m))),patch.object(pair,'recovered_unit',side_effect=recovered or self.recovered),patch.object(runner.Round,'guest',guest),patch.object(runner.Round,'cleanup',clean),patch.object(runner,'write',side_effect=write),patch.object(sys,'argv',['round.py','pair','--work',str(self.w)]),patch.object(sys,'stderr',io.StringIO()):
   try:runner.main()
   except Exception as e:return e
 def test_approved_plan_and_historical_seven(self):self.assertTrue(pair.authorize(self.plan))
 def test_old_or_changed_plans_refused_before_units(self):
  for key,value in [('purpose',None),('maximumUnits',7),('fixtures',['candidate','baseline']),('candidateRule',{}),('cacheOnly',False),('historicalGate',{})]:
   with self.subTest(key=key):
    plan=copy.deepcopy(self.plan);plan[key]=value
    with self.assertRaises(RuntimeError):pair.authorize(plan)
 def test_actual_dispatch_normal_order_profile_and_no_error_cleanup(self):
  self.assertIsNone(self.invoke());self.assertEqual(self.calls,['baseline','profile','candidate']);self.assertFalse((self.w/'fixtures-complete.json').exists());self.assertEqual(runner.read(self.w/'pair-complete.json')['candidateUnits'],1)
  expected=copy.deepcopy(self.native['Spec']['linux']['seccomp']);expected['syscalls'].append(pair.RULE);self.assertEqual(runner.read(self.w/'candidate-profile.json'),expected)
 def test_baseline_result_mismatch_prevents_candidate_and_cleans_once(self):
  self.observed={**self.observed,'status':'inconclusive'};e=self.invoke();self.assertIn('baseline-clone-mismatch',str(e));self.assertEqual(self.calls,['baseline','cleanup'])
 def test_baseline_recovery_error_and_audit_error_still_cleanup(self):
  def fail(*args):raise RuntimeError('recovery-failure')
  e=self.invoke(recovered=fail,audit_failure=True);self.assertIsInstance(e,ExceptionGroup);self.assertEqual(self.calls,['baseline','cleanup']);self.assertFalse((self.w/'pair-complete.json').exists())
 def test_actual_common_unit_recovery_failure_reaches_dispatch_cleanup(self):
  import recovery
  real_unit=runner.Round.unit
  def work(r,mode):
   self.calls.append(mode);runner.write(self.w/'units.json',[{'mode':mode,'runId':'a'*12,'passed':True}]);return 'a'*12
  with patch.object(runner.Round,'_unit',work),patch.object(recovery,'retrieve',return_value={'evidenceStatus':'missing','errors':[]}):
   e=self.invoke(unit=real_unit)
  self.assertIn('unit-recovery',str(e));self.assertEqual(self.calls,['baseline','cleanup']);self.assertFalse(runner.read(self.w/'units.json')[0]['passed'])
 def test_candidate_failure_cleans_no_retry(self):
  def unit(r,mode):
   if mode=='candidate':self.calls.append(mode);raise RuntimeError('candidate-failure')
   return self.unit(r,mode)
  self.assertIn('candidate-failure',str(self.invoke(unit=unit)));self.assertEqual(self.calls,['baseline','profile','candidate','cleanup'])
 def test_candidate_recovery_failure_cleans_no_completion(self):
  def recovered(r,mode,rid):
   if mode=='candidate':raise RuntimeError('candidate-recovery')
   return self.recovered(r,mode,rid)
  self.assertIn('candidate-recovery',str(self.invoke(recovered=recovered)));self.assertEqual(self.calls,['baseline','profile','candidate','cleanup']);self.assertFalse((self.w/'pair-complete.json').exists())
 def test_unauthorized_main_cleans_without_unit(self):
  self.plan['purpose']='old';runner.write(self.w/'plan.json',self.plan);self.assertIsNotNone(self.invoke());self.assertEqual(self.calls,['cleanup'])
 def test_code_gate_tamper_blocks_before_unit(self):
  runner.write(self.w/'local-gate.json',{'passed':True,'codeHashes':{str(runner.HERE/'round.py'):'bad'}});self.assertIn('code-changed',str(self.invoke()));self.assertEqual(self.calls,['cleanup'])
 def test_pair_plan_refuses_fixture_path(self):
  with self.assertRaisesRegex(RuntimeError,'seven-fixtures'):runner.Round(self.w).fixtures()
 def test_saved_baseline_trace_and_pid_roles(self):
  self.assertEqual(self.observed['status'],'clone-still-denied');self.assertEqual({x['kind'] for x in self.observed['namespaceClones']},{'precheck','command-preparation'});self.assertTrue(all(x['errno']=='EPERM' for x in self.observed['namespaceClones']))
 def test_positive_clone_child_denial_and_unfinished(self):
  result=copy.deepcopy(self.result);rows=[]
  for pid,kind in [(41,'"/usr/bin/true"'),(42,'"/usr/local/bin/node"')]:
   rows.extend([f'[pid {pid}] execve("/proc/self/fd/3", ["bwrap", {kind}], 0) = 0',f'[pid {pid}] clone(child_stack=NULL, flags={pair.FLAGS} <unfinished ...>',f'[pid {pid}] <... clone resumed>) = {pid+100}',f'[pid {pid+100}] mount("none", "/", NULL, MS_PRIVATE, NULL) = -1 EPERM (Operation not permitted)'])
  result['calls'][-1]['stderr']='\n'.join(rows);o=pair.trace_observation(result);self.assertEqual(o['status'],'first-clone-passed-next-blocked');self.assertEqual(len(o['nextDenied']),2)
  result['nativePayloadStarted']=True;result['calls'][-1].update(exitCode=0,stdout='NATIVE_PAYLOAD_STARTED');self.assertEqual(pair.trace_observation(result)['status'],'synthetic-payload-completed')
 def test_unknown_trace_and_binary_drift_not_success(self):
  result=copy.deepcopy(self.result);result['calls'][-1]['stderr']='missing';self.assertEqual(pair.trace_observation(result)['status'],'inconclusive');result['nodeVersion']='other'
  with self.assertRaises(RuntimeError):pair.trace_observation(result)
 def test_empty_saved_pair_is_inconclusive(self):
  runner.write(self.w/'prior-pair.json',{'pairs':{'baseline':{}}});v=verify_pair.verify(self.w);self.assertEqual((v['status'],v['candidateStarts'],v['candidateUnits']),('inconclusive',0,0))
if __name__=='__main__':unittest.main()
