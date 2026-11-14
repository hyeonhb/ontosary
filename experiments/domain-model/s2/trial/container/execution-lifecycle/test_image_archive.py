import hashlib,io,json,pathlib,tarfile,tempfile,time,unittest
from artifacts import verify_image_archive,Rejected
class ImageArchiveTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=pathlib.Path(self.tmp.name)/'image.tar';layer=b'public layer';self.layer=hashlib.sha256(layer).hexdigest();config=json.dumps({'os':'linux','architecture':'arm64','rootfs':{'diff_ids':['sha256:'+self.layer]}}).encode();self.config=hashlib.sha256(config).hexdigest();manifest=json.dumps({'config':{'digest':'sha256:'+self.config},'layers':[{'digest':'sha256:'+self.layer}]}).encode();self.target=hashlib.sha256(manifest).hexdigest();self.files={'blobs/sha256/'+self.layer:layer,'blobs/sha256/'+self.config:config,'blobs/sha256/'+self.target:manifest};self.image={'target':'sha256:'+self.target,'config':'sha256:'+self.config,'chain':'sha256:'+self.layer}
 def tearDown(self):self.tmp.cleanup()
 def save(self):
  with tarfile.open(self.path,'w') as t:
   for name,data in self.files.items():i=tarfile.TarInfo(name);i.size=len(data);t.addfile(i,io.BytesIO(data))
 def test_manifest_config_chain_and_all_blobs(self):
  self.save();self.assertEqual(verify_image_archive(self.path,self.image,time.monotonic()+1)['blobsVerified'],3)
 def test_bad_blob(self):
  self.files['blobs/sha256/'+self.layer]=b'corrupt';self.save()
  with self.assertRaisesRegex(Rejected,'blob-hash'):verify_image_archive(self.path,self.image,time.monotonic()+1)
 def test_missing_layer(self):
  del self.files['blobs/sha256/'+self.layer];self.save()
  with self.assertRaisesRegex(Rejected,'missing-layer'):verify_image_archive(self.path,self.image,time.monotonic()+1)
 def test_wrong_chain(self):
  self.save();self.image['chain']='wrong'
  with self.assertRaisesRegex(Rejected,'archive-chain'):verify_image_archive(self.path,self.image,time.monotonic()+1)
if __name__=='__main__':unittest.main()
