import contextlib,io,json,os,pathlib,sys,tarfile,tempfile,types
base=pathlib.Path('experiments/domain-model/s2/trial/container/execution-lifecycle').resolve();sys.path.insert(0,str(base));import guest
from collector import inventory
Path=pathlib.Path
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);shared=root/'shared';shared.mkdir();owned=root/'owned';run=owned/'runs'/'aaaaaaaaaaaa';source=run/'source';source.mkdir(parents=True)
 canary=root/'manager-canary.txt';canary.write_text('public-test-canary');os.link(canary,source/'hardlink.txt')
 (run/'state.json').write_text(json.dumps({'terminationConfirmed':True,'removalConfirmed':True,'collectionStatus':'suppressed','cleanupDone':False}))
 try:inventory({'source':source});collector='accepted'
 except Exception as e:collector=str(e)
 guest.c.ROOT=owned;guest.SHARED=shared;output=root/'evidence.tar.gz'
 guest.pathlib=types.SimpleNamespace(Path=lambda value:output if value=='/tmp/s2-execution-evidence.tar.gz' else Path(value))
 with contextlib.redirect_stdout(io.StringIO()):guest.export()
 with tarfile.open(output) as t:
  name='runs/aaaaaaaaaaaa/source/hardlink.txt';data=t.extractfile(name).read().decode()
 result={'runtimeStarted':False,'collectorRejected':collector,'collectionStatus':'suppressed','exportContainsRejectedHardlink':data=='public-test-canary','exportMember':name}
 print(json.dumps(result,indent=2));assert result['exportContainsRejectedHardlink'] and collector!='accepted'
