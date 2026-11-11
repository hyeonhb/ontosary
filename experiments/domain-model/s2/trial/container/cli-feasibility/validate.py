"""Host checks only. Reuse an authentic prior receipt, never manufacture new authority."""
import hashlib,json,pathlib,subprocess,tarfile,tempfile
base=pathlib.Path('experiments/domain-model/s2/trial/container')
for p in (base/'cli-feasibility').glob('*.py'):compile(p.read_text(),str(p),'exec')
for args in [
 ['pnpm','s2:build'],
 ['python3',str(base/'lifecycle/test_collector.py')],
 ['python3',str(base/'lifecycle/test_cleanup.py')],
]:
 print('CHECK',args,flush=True);subprocess.run(args,check=True,timeout=60)
archive=pathlib.Path('experiments/domain-model/s2/verification/2026-11-11-linux-evaluation/job-probes/7ca7f2d67f77/raw.tar.gz')
with tarfile.open(archive) as t:receipt=t.extractfile('result/fixture.json').read()
record={'archive':str(archive),'archiveSha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'member':'result/fixture.json','receiptSha256':hashlib.sha256(receipt).hexdigest(),'historicalReceipt':True,'newCLIReceipt':False}
pathlib.Path('work/s2-cli-feasibility/refusal-source.json').write_text(json.dumps(record,indent=2)+'\n')
with tempfile.TemporaryDirectory(prefix='ontosary-cli-refusal-') as folder:
 pathlib.Path(folder,'fixture.json').write_bytes(receipt)
 subprocess.run(['node',str(base/'lifecycle/refusal.mjs'),folder],check=True,timeout=20)
