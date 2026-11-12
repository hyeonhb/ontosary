import hashlib,json,pathlib,subprocess,os,time,urllib.request,tarfile
root=pathlib.Path('/tmp/ontosary-s2-single-policy-test-20261112');root.mkdir(exist_ok=False)
evidence=pathlib.Path('work/s2-single-policy-test').resolve()
urls=[('274d59968f7fc4016d852a0fa9a95e78a7253670ae8095bcb06076eec1f922f8','8eb876c2ccc4b6ff89e4a65d511815923b285e04503ba465809bf587f763da24'),('975f12320da58d431eba0c59caf918381721d37c81297f52a261383a54420186','fe0ef0e9840ee8932640e6058f84b7fa98050f9726e44af44883a5b804ae830e')]
cache=[{'path':str(pathlib.Path.home()/'Library/Caches/lima/download/by-url-sha256'/u),'expectedDataSha256':h,'existedBefore':(pathlib.Path.home()/'Library/Caches/lima/download/by-url-sha256'/u).exists()} for u,h in urls]
(evidence/'ownership.json').write_text(json.dumps({'root':str(root),'cache':cache,'createdMonotonic':time.monotonic()},indent=2))
archive=root/'lima.tar.gz'
subprocess.run(['curl','--fail','--location','--max-time','240','--output',str(archive),'https://github.com/lima-vm/lima/releases/download/v2.3.0/lima-2.3.0-Darwin-arm64.tar.gz'],check=True)
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='b7af444bd8f91d3c307477e562f2cf3bd7595d62b9429185e4fa841563578cfc'
prefix=root/'prefix';prefix.mkdir()
with tarfile.open(archive) as t:t.extractall(prefix,filter='data')
os.environ['LIMA_HOME']=str(root/'lima')
subprocess.run([str(prefix/'bin/limactl'),'start','--yes','--name=s2-lifecycle','--timeout=7m','experiments/domain-model/s2/trial/container/lima.yaml'],check=True,timeout=450)
