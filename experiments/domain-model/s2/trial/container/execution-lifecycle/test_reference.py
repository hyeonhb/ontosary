import hashlib,json,os,pathlib,tempfile,time,unittest
from unittest.mock import patch
import reference as ref,common as c
class ReferenceTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.tmp.name);self.run=self.root/('a'*12);self.run.mkdir();self.units=self.root/'units';self.units.mkdir();self.now=time.monotonic();self.calls=[]
  self.state={'runId':self.run.name,'service':'ontosary-execution-'+self.run.name+'.service','registeredAt':{'mono':self.now-5},'finalizedAt':{'mono':self.now-2},'deadlines':{'work':self.now+10,'finish':self.now+20},'invocationId':'b'*32};c.write(self.run/'state.json',self.state)
  self.worker={'Id':self.state['service'],'LoadState':'loaded','ActiveState':'inactive','SubState':'dead','InvocationID':'b'*32,'InactiveEnterTimestampMonotonic':int((self.now-1)*1000000),'Result':'success'};self.holderActive=True
 def tearDown(self):self.tmp.cleanup()
 def command(self,run,args,phase='finish',timeout=3,check=True):
  self.calls.append(args)
  if args[1]=='stop':self.holderActive=False
  if args[1]=='show':
   if args[2].endswith('.target'):v={'Id':args[2],'LoadState':'loaded','ActiveState':'active' if self.holderActive else 'inactive','After':self.state['service'],'BindsTo':'ontosary-execution-seal.service'}
   else:v=self.worker
   return 0,'\n'.join(k+'='+str(value) for k,value in v.items()),''
  return 0,'',''
 def acquire(self):ref.acquire(self.run,self.units,self.command)
 def test_reference_acquire_before_start_and_release_after_receipt(self):
  self.acquire();text=(self.units/('ontosary-reference-'+self.run.name+'.target')).read_text();self.assertIn('After='+self.state['service'],text);self.assertNotIn('Wants=',text);self.assertNotIn('Requires=',text)
  self.worker['ActiveState']='active'
  with patch.dict(os.environ,{'INVOCATION_ID':'b'*32}):ref.invocation(self.run,self.units,self.command)
  self.worker['ActiveState']='inactive';receipt=ref.end_observation(self.run,self.units,self.command)
  with self.assertRaisesRegex(RuntimeError,'durable-receipt'):ref.release(self.run,self.units,self.command)
  c.write(self.run/'seal-receipt.json',receipt);ref.release(self.run,self.units,self.command);self.assertEqual(c.read(self.run/'reference.json')['phase'],'released');self.assertEqual(list(self.units.iterdir()),[])
 def test_failed_and_deactivating_states(self):
  self.acquire();self.worker.update(ActiveState='failed',Result='signal');self.assertIsNotNone(ref.end_observation(self.run,self.units,self.command));self.worker['ActiveState']='deactivating';self.assertIsNone(ref.end_observation(self.run,self.units,self.command))
 def test_unloaded_not_found_and_missing_or_zero_timestamp(self):
  self.acquire()
  for key,value in [('LoadState','not-found'),('InactiveEnterTimestampMonotonic',0),('InactiveEnterTimestampMonotonic','')]:
   with self.subTest(key=key,value=value):
    old=self.worker[key];self.worker[key]=value
    with self.assertRaises((RuntimeError,ValueError)):ref.end_observation(self.run,self.units,self.command)
    self.worker[key]=old
  self.assertGreater(len((self.run/'service-raw.jsonl').read_text().splitlines()),3)
 def test_timestamp_outside_deadline_and_before_finalizer(self):
  self.acquire()
  for stamp in [self.now+30,self.now-3]:
   self.worker['InactiveEnterTimestampMonotonic']=int(stamp*1000000)
   with self.assertRaisesRegex(RuntimeError,'inactive-deadline'):ref.end_observation(self.run,self.units,self.command)
 def test_late_observation_rejected_without_new_clock(self):
  self.acquire()
  with patch.object(ref.time,'monotonic',return_value=self.now+21),self.assertRaisesRegex(RuntimeError,'inactive-deadline'):ref.end_observation(self.run,self.units,self.command)
 def test_same_name_other_invocation_rejected(self):
  self.acquire();self.worker['InvocationID']='c'*32
  with self.assertRaisesRegex(RuntimeError,'invocation-end-binding'):ref.end_observation(self.run,self.units,self.command)
 def test_holder_failure_blocks(self):
  self.acquire();self.holderActive=False
  with self.assertRaisesRegex(RuntimeError,'reference-holder-lost'):ref.end_observation(self.run,self.units,self.command)
 def test_block_receipt_precedes_release(self):
  self.acquire();c.write(self.run/'blocked-receipt.json',{'reason':'holder lost'});ref.release(self.run,self.units,self.command,True);self.assertTrue(c.read(self.run/'reference.json')['blocked'])
if __name__=='__main__':unittest.main()
