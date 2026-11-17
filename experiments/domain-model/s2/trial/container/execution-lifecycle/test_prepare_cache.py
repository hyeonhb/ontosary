"""Exercise the actual Round.prepare entrypoint twice; external VM commands are fake."""
import datetime,hashlib,io,json,pathlib,tarfile,tempfile,time,unittest,shutil
from unittest.mock import patch
import round as round_module
from artifacts import Store,Rejected
from image_cache import ImageCache,build_inputs,key
class PrepareCacheTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.tmp.name).resolve();self.store=self.root/'store';self.calls=[];self.archive=self.root/'fixture-image.tar'
  layer=b'public layer';layer_sha=hashlib.sha256(layer).hexdigest();config=json.dumps({'os':'linux','architecture':'arm64','rootfs':{'diff_ids':['sha256:'+layer_sha]}}).encode();config_sha=hashlib.sha256(config).hexdigest();manifest=json.dumps({'config':{'digest':'sha256:'+config_sha},'layers':[{'digest':'sha256:'+layer_sha}]}).encode();target=hashlib.sha256(manifest).hexdigest()
  with tarfile.open(self.archive,'w') as t:
   for name,data in [(layer_sha,layer),(config_sha,config),(target,manifest)]:m=tarfile.TarInfo('blobs/sha256/'+name);m.size=len(data);t.addfile(m,io.BytesIO(data))
  self.export={'bytes':self.archive.stat().st_size,'sha256':hashlib.sha256(self.archive.read_bytes()).hexdigest(),'image':{'name':'fixture-image','target':'sha256:'+target,'config':'sha256:'+config_sha,'chain':'sha256:'+layer_sha,'platform':'linux/arm64'}}
 def tearDown(self):self.tmp.cleanup()
 def prepare(self,name,forbid_build=False,mutate_inputs=None,probe_change=False,import_bad=False):
  w=self.root/name;w.mkdir();future=datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(minutes=10)
  budget={'deadlines':{n:{'utc':future.isoformat(),'monotonic':time.monotonic()+600} for n in ['plan','environment']},'environmentEntered':{'mono':time.monotonic()}}
  for n,v in [('budget.json',budget),('prior-pair.json',{}),('local-gate.json',{'passed':True,'codeHashes':{}}),('plan.json',{'round':name,'vmRoot':str(w/'vm'),'vmName':name,'store':str(self.store)})]:(w/n).write_text(json.dumps(v))
  obj=round_module.Round(w);obj.action='prepare';test=self
  class FakeDownloads(Store):
   def acquire(self,request,producer,end):
    if request['name'].startswith(('lima-','ubuntu-','nerdctl-')):return {'path':str(test.archive),'cacheHit':True,'actual':{'sha256':request['sha256'],'bytes':1},'request':request}
    return super().acquire(request,producer,end)
   def lookup(self,request,end):
    if request['name'].startswith(('lima-','ubuntu-','nerdctl-')):return {'path':str(test.archive),'cacheHit':True}
    return super().lookup(request,end)
  def cmd(args,**kw):
   self.calls.append((name,'cmd',args))
   if args[1]=='shell':return {'exitCode':0},json.dumps({'path':'/tmp/ontosary-transfer-test','uid':501})
   if len(args)>2 and args[1]=='copy' and args[2].endswith(':/opt/ontosary-execution/image.tar'):
    if forbid_build:self.fail('save/export producer called on hit')
    shutil.copyfile(self.archive,args[3])
   return {'exitCode':0},''
  def guest(args,**kw):
   self.calls.append((name,'guest',args))
   if args[:2]==['python3','-c']:return {'exitCode':0},json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'guestMonotonic':1})
   if args[-1]=='build' and forbid_build:self.fail('build called on cache hit')
   if args[0]=='cat':return {'exitCode':0},json.dumps(self.export)
   if len(args)>2 and args[2]=='import' and import_bad:raise RuntimeError('import-image-identity')
   return {'exitCode':0},''
  obj.cmd=cmd;obj.guest=guest;real_sha=round_module.sha
  def changed_sha(p):return 'different-probe' if probe_change and str(p).endswith('retry-probe.mjs') else real_sha(p)
  def inputs(docker):
   result=build_inputs(docker)
   if mutate_inputs:mutate_inputs(result)
   return result
  def forbidden_download(*a):
   def producer(sink):self.fail('download producer called')
   return producer
  with patch('recovery.retrieve',return_value={'evidenceStatus':'diagnostic'}),patch.object(round_module,'Store',FakeDownloads),patch.object(round_module,'download',forbidden_download),patch.object(round_module,'sha',side_effect=changed_sha),patch.object(round_module,'build_inputs',side_effect=inputs):obj.prepare()
  return json.loads((w/'image-artifact.json').read_text())
 def test_actual_entrypoint_miss_then_distinct_round_hit(self):
  first=self.prepare('first');second=self.prepare('second',forbid_build=True,probe_change=True)
  self.assertEqual(first['builds'],1);self.assertEqual(second['builds'],0);self.assertEqual(first['binding'],second['binding']);self.assertEqual(sum(n=='second' and kind=='guest' and len(args)>2 and args[2]=='publish' for n,kind,args in self.calls),2);self.assertTrue(any(n=='second' and args[-1]=='prepare' for n,kind,args in self.calls))
 def test_real_build_inputs_invalidate_key(self):
  self.prepare('first')
  # A miss must reach build; stop there instead of claiming the same fake output is new.
  for label,mutate in [('recipe',lambda x:x['context']['Dockerfile'].update(sha256='new')),('base',lambda x:x['buildArgs'].update(BASE_IMAGE='new')),('tool',lambda x:x['tools'].update(nerdctl='new'))]:
   with self.subTest(label=label),self.assertRaisesRegex(AssertionError,'build called'):self.prepare(label,forbid_build=True,mutate_inputs=mutate)
 def test_corrupt_registered_archive_rejects_before_build(self):
  first=self.prepare('first');p=pathlib.Path(first['artifact']['path']);p.chmod(0o600);p.write_bytes(b'corrupt')
  with self.assertRaisesRegex(Rejected,'corrupt'):self.prepare('second',forbid_build=True)
 def test_partial_binding_rejected(self):
  first=self.prepare('first');p=self.store/('.image-key-'+first['binding']['key']+'.json');p.chmod(0o600);p.write_text('{}')
  with self.assertRaisesRegex(Rejected,'image-input-binding'):self.prepare('second',forbid_build=True)
 def test_import_identity_failure_blocks_preparation(self):
  self.prepare('first')
  with self.assertRaisesRegex(RuntimeError,'import-image-identity'):self.prepare('second',forbid_build=True,import_bad=True)
  self.assertFalse((self.root/'second/preparation-complete.json').exists())
 def test_output_fields_are_not_lookup_inputs(self):
  inputs=build_inputs(b'FROM pinned');serialized=json.dumps(inputs)
  for forbidden in ['imageId','archiveSha256','target','config','chain']:self.assertNotIn(forbidden,serialized)
 def test_conflicting_same_key_cannot_overwrite(self):
  first=self.prepare('first');cache=ImageCache(Store(self.store))
  with self.assertRaisesRegex(Rejected,'image-key-conflict'):cache.bind(first['binding']['inputs'],first['binding']['request'],{**first['binding']['image'],'chain':'different'},{},time.monotonic()+3)
if __name__=='__main__':unittest.main()
