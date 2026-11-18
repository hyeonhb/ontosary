"""Replay the 2026-11-17 verifier with its exact Git code; optionally replay R20 fakes."""
import argparse,hashlib,json,pathlib,subprocess,sys,tempfile

HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[4]
COMMIT='2008351b926aa8c7f7c762f297c0be8b43c2e2a9'
REL=HERE.relative_to(ROOT)
EVIDENCE=ROOT/'experiments/domain-model/s2/verification/2026-11-17-vm-cli-smoke'

def replay(reproduce=False):
    frozen=json.loads((EVIDENCE/'prepared/freeze.json').read_text())['codeHashes']
    paths=[REL/pathlib.Path(p).name for p in frozen]+[REL/'verify.py']
    paths += [REL.parent/'container'/p for p in ['single-policy-test/deadline.py','single-policy-test/scope.py','execution-lifecycle/artifacts.py']]
    with tempfile.TemporaryDirectory(prefix='s2-r20-historical-') as tmp:
        snapshot=pathlib.Path(tmp);hashes={}
        for path in paths:
            data=subprocess.check_output(['git','show',COMMIT+':'+str(path)],cwd=ROOT,timeout=10)
            dest=snapshot/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
            hashes[str(path)]=hashlib.sha256(data).hexdigest()
        for name,h in frozen.items():
            if hashes[str(REL/pathlib.Path(name).name)]!=h:raise RuntimeError('historical freeze mismatch')
        script='''import importlib.util,json,pathlib,sys
sys.path.insert(0,sys.argv[1])
import run as archived
import verify
result={'historicalVerification':verify.verify(sys.argv[2])}
if sys.argv[4]=='yes':
 spec=importlib.util.spec_from_file_location('local_r20_fixture',sys.argv[3]);fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture);fixture.m=archived
 result['cases']=[fixture.scenario('normal'),fixture.scenario('exhausted')]
print(json.dumps(result))
'''
        raw=subprocess.run([sys.executable,'-c',script,str(snapshot/REL),str(EVIDENCE),str(HERE/'test_cleanup_budget.py'),'yes' if reproduce else 'no'],capture_output=True,text=True,timeout=30,check=True)
        return {'historicalCommit':COMMIT,'sourceHashes':hashes,'fixtureHash':hashlib.sha256((HERE/'test_cleanup_budget.py').read_bytes()).hexdigest(),**json.loads(raw.stdout)}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--reproduce-r20',action='store_true');args=parser.parse_args()
    print(json.dumps(replay(args.reproduce_r20),indent=2))
