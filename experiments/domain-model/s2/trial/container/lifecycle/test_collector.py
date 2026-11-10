"""Host regressions: rejection before unsafe reads and no partial publication."""
import hashlib,json,os,pathlib,socket,tempfile,time,unittest
from collector import collect,inventory,Rejected
class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.run=pathlib.Path(self.temp.name)
        self.roots={n:self.run/n for n in ['source','auxiliary']}
        for root in self.roots.values():root.mkdir()
        (self.roots['source']/'old').write_bytes(b'baseline')
        (self.roots['source']/'delete').write_bytes(b'delete')
        self.baseline=inventory(self.roots)
        self.term={'state':'stopped-confirmed','confirmed':True,'admissionClosed':True,'runId':'fixture','containerId':'immutable','image':{'target':'current'},'cgroup':'persistent','cgroupInode':1,'source':str(self.roots['source']),'auxiliary':str(self.roots['auxiliary']),'reason':'exit','exitCode':0}
        self.current={**self.term,'state':'collecting','terminationConfirmed':True}
        self.save_state()
    def save_state(self):(self.run/'state.json').write_text(json.dumps(self.current))
    def tearDown(self):
        for root,dirs,files in os.walk(self.run):
            os.chmod(root,0o700)
        self.temp.cleanup()
    def rejected(self,reason):
        with self.assertRaisesRegex(Rejected,reason):collect(self.run,self.baseline,self.term)
        self.assertFalse((self.run/'result').exists());self.assertFalse((self.run/'staging').exists())
    def test_complete_bytes_delta_and_diagnostic(self):
        (self.roots['source']/'old').write_bytes(b'\x00\xffnew');(self.roots['source']/'delete').unlink()
        (self.roots['auxiliary']/'helper').write_bytes(b'helper')
        self.term['reason']='timeout';self.term['exitCode']=None
        result=collect(self.run,self.baseline,self.term)
        self.assertEqual(result['delta'],{'added':['auxiliary/helper'],'deleted':['source/delete'],'modified':['source/old']})
        self.assertEqual((self.run/'result/source/old').read_bytes(),b'\x00\xffnew')
        self.assertEqual(result['snapshot']['files']['source/old']['sha256'],hashlib.sha256(b'\x00\xffnew').hexdigest())
        self.assertEqual(result['classification'],'diagnostic');self.assertFalse(result['validSubmission'])
    def test_unconfirmed(self):
        self.term['confirmed']=False;self.rejected('termination-not-confirmed')
    def test_mismatched_run_or_paths(self):
        for key,value in [('containerId','other'),('cgroupInode',2),('source','/elsewhere')]:
            old=self.term[key];self.term[key]=value;self.rejected('termination-');self.term[key]=old
    def test_pending_runtime_request(self):
        for key in ['createPending','startPending','execPending']:
            self.current[key]=True;self.save_state();self.rejected('manager-state');self.current[key]=False
    def test_symlink_does_not_copy_external_secret(self):
        secret=self.run/'secret';secret.write_text('not worker input');(self.roots['source']/'link').symlink_to(secret);self.rejected('nonregular:source/link')
    def test_hardlink(self):
        os.link(self.roots['source']/'old',self.roots['source']/'link');self.rejected('hardlink')
    def test_fifo_rejected_without_open(self):
        os.mkfifo(self.roots['source']/'fifo');start=time.monotonic();self.rejected('nonregular');self.assertLess(time.monotonic()-start,1)
    def test_socket(self):
        with socket.socket(socket.AF_UNIX) as sock:
            sock.bind(str(self.roots['source']/'socket'));self.rejected('nonregular')
    def test_file_limit(self):
        for i in range(127):(self.roots['auxiliary']/str(i)).write_bytes(b'')
        self.rejected('file-count-limit')
    def test_byte_limit(self):
        with (self.roots['source']/'large').open('wb') as f:f.truncate(16*1024*1024+1)
        self.rejected('byte-limit')
    def test_depth_limit(self):
        p=self.roots['source']
        for i in range(17):p=p/'d';p.mkdir()
        self.rejected('path-depth-limit')
    def test_copy_failure_never_publishes(self):
        with self.assertRaisesRegex(Rejected,'injected-copy-failure'):collect(self.run,self.baseline,self.term,1)
        self.assertFalse((self.run/'result').exists());self.assertFalse((self.run/'staging').exists())
    def test_expired_collection_deadline(self):
        with self.assertRaisesRegex(Rejected,'collection-time-limit'):inventory(self.roots,deadline=time.monotonic()-1)
if __name__=='__main__':unittest.main(verbosity=2)
