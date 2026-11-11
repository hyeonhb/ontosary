"""Actual same-entrypoint timeout, delayed-writer control and clean-next-unit evidence."""
import hashlib,json,os,pathlib,subprocess,sys
root=pathlib.Path('/tmp/ontosary-s2-linux-evaluation-20261111');work=pathlib.Path('work/s2-linux-evaluation');base=pathlib.Path(__file__).parent
for name in ['timeout','control']:
 subprocess.run([sys.executable,str(base/'command.py'),'--ledger',str(work/'budget.json'),'--log',str(work/('job-'+name+'.log')),'--phase','exploration','--timeout','240','--',sys.executable,str(base/'run.py'),'--root',str(root),'--output',str(work/'job-probes'),'--job',name,'--budget',str(work/'budget.json'),'--phase','exploration'],check=True,timeout=250)
 cases=[p for p in (work/'job-probes').iterdir() if (p/'summary.json').exists() and json.loads((p/'summary.json').read_text())['job']==name];assert len(cases)==1
 case=cases[0];rid=case.name;state=json.loads((case/'terminal.json').read_text());receipt=json.loads((case/'raw/result/fixture.json').read_text())
 assert json.loads((case/'raw/baseline.json').read_text())['fileCount']==0
 if name=='timeout':
  assert receipt['classification']=='diagnostic' and not (case/'raw/result/source/late-writer.txt').exists()
  code="import json,pathlib,time,hashlib; p=pathlib.Path('/opt/ontosary-fixture/runs/"+rid+"'); s=json.loads((p/'state.json').read_text()); time.sleep(max(0,s['workStarted']['mono']+8-time.monotonic())); snapshot=json.loads((p/'result/fixture.json').read_text())['snapshot']['files']; current={str(f.relative_to(p)):{'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size} for folder in ['source','auxiliary'] for f in (p/folder).rglob('*') if f.is_file()}; assert current==snapshot; assert not (p/'source/late-writer.txt').exists(); print(json.dumps({'sameAsCollected':True,'lateWriterAbsent':True,'observedMono':time.monotonic(),'workStartedMono':s['workStarted']['mono'],'terminationConfirmedMono':json.loads((p/'termination.json').read_text())['confirmedAt']['mono'],'files':current}))"
  proc=subprocess.run([str(root/'prefix/bin/limactl'),'shell','--workdir=/tmp','s2-lifecycle','sudo','python3','-c',code],env={**os.environ,'LIMA_HOME':str(root/'lima')},capture_output=True,check=True,timeout=15)
  (case/'late-observation.json').write_bytes(proc.stdout)
 else:
  assert (case/'raw/result/source/late-writer.txt').read_text()=='finite delayed writer\n'
  assert json.loads((case/'raw/result/source/control.json').read_text())['wrote']
  assert receipt['classification']=='normal-fixture'
rows=[json.loads((p/'summary.json').read_text()) for p in (work/'job-probes').iterdir()];assert len({r['runId'] for r in rows})==2
(work/'job-probes-summary.json').write_text(json.dumps({'status':'passed','samePID1EntryPoint':True,'timeoutSeconds':2,'writerDelaySeconds':5,'observedAfterWorkStartSecondsAtLeast':8,'timeoutAcceptedAsCalibration':False,'finiteNoKillControlWrote':True,'nextUnitEmptyOutputBaseline':True,'rows':rows},indent=2)+'\n')
