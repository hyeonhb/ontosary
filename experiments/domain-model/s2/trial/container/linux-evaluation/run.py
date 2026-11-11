"""Sequential, fixed known-submission unit. Finalized + successful cleanup is mandatory."""
import argparse,datetime,gzip,hashlib,json,os,pathlib,subprocess,sys,time
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--output',required=True);p.add_argument('--job',required=True,choices=['baseline','reference','helper-type-error','wrong-modal-order','reference-delta','timeout','control']);p.add_argument('--budget',required=True);p.add_argument('--phase',choices=['core','exploration'],required=True);a=p.parse_args()
root=pathlib.Path(a.root);output=pathlib.Path(a.output);output.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(pathlib.Path(__file__).parent.parent/'lifecycle'))
from host_driver import guest,drive
prefix=str(root/'prefix');home=str(root/'lima');lima=str(root/'prefix/bin/limactl');unit_start=time.monotonic()
budget=json.loads(pathlib.Path(a.budget).read_text());deadline=datetime.datetime.fromisoformat(budget['deadlines'][a.phase]);minutes={'core':90,'exploration':150}[a.phase]
remaining=min((deadline-datetime.datetime.now(datetime.timezone.utc)).total_seconds(),minutes*60-(unit_start-budget['monotonic']))
if remaining<240:raise RuntimeError('Insufficient phase budget for another unit')
def shell(args,timeout=30):
 t=min(timeout,240-(time.monotonic()-unit_start))
 if t<=0:raise RuntimeError('unit-outer-timeout')
 proc=subprocess.run([lima,'shell','--workdir=/tmp','s2-lifecycle','sudo',*args],env={**os.environ,'LIMA_HOME':home},capture_output=True,timeout=t)
 if proc.returncode:raise RuntimeError(proc.stderr.decode()+proc.stdout.decode())
 return proc.stdout.decode()
def fingerprint(label):
 result=json.loads(shell(['python3','/opt/ontosary-fixture/code/fingerprint.py','/opt/ontosary-linux-evaluation','/tmp/s2-env-'+label+'.json.gz','inputs']))
 expected=json.loads(shell(['cat','/opt/ontosary-linux-evaluation/setup/inputs-summary.json']))
 if result['sha256']!=expected['sha256']:raise RuntimeError('immutable-environment-changed')
 return result
before=fingerprint('before')
prepared=guest(prefix,home,['prepare','linux-evaluation',a.job]);rid=prepared['runId'];case=output/rid;case.mkdir()
(case/'prepare.json').write_text(json.dumps(prepared,indent=2)+'\n');(case/'environment-before.json').write_text(json.dumps(before,indent=2)+'\n')
print(json.dumps({'event':'prepared','job':a.job,'runId':rid}),flush=True)
status=drive(prefix,home,rid,str(case/'driver.jsonl'),240-(time.monotonic()-unit_start))
(case/'terminal.json').write_text(json.dumps(status,indent=2)+'\n')
after=fingerprint('after');(case/'environment-after.json').write_text(json.dumps(after,indent=2)+'\n')
service=shell(['systemctl','show',status['service'],'-p','Result','-p','ExecMainCode','-p','ExecMainStatus','-p','ActiveState','-p','SubState'])
(case/'service.txt').write_text(service)
archive='/tmp/s2-unit-'+rid+'.tar.gz'
export="import pathlib,tarfile; p=pathlib.Path('/opt/ontosary-fixture/runs/"+rid+"'); t=tarfile.open('"+archive+"','w:gz'); [(t.add(f,arcname=f.name)) for f in p.iterdir() if f.is_file() or f.name in ['result','quarantined-result']]; t.close()"
shell(['python3','-c',export])
subprocess.run([lima,'copy','s2-lifecycle:'+archive,str(case/'raw.tar.gz')],env={**os.environ,'LIMA_HOME':home},check=True,timeout=20)
import tarfile
with tarfile.open(case/'raw.tar.gz') as t:t.extractall(case/'raw',filter='data')
if status['state']!='finalized' or not status.get('cleanupDone') or 'Result=success\n' not in service:raise RuntimeError('unit-not-approved:'+rid)
receipt=json.loads((case/'raw/result/fixture.json').read_text());assert receipt['fixtureOnly'] and not receipt['validSubmission']
if a.job=='timeout':assert status['reason']=='timeout' and receipt['classification']=='diagnostic'
else:assert status['reason']=='exit' and status['exitCode']==0 and receipt['classification']=='normal-fixture'
summary={'kind':'known-submission-calibration' if a.job not in ['timeout','control'] else 'finite-job-lifecycle-probe','fixtureOnly':True,'validSubmission':False,'trialAuthorized':False,'readyForTrial':False,'job':a.job,'runId':rid,'state':status['state'],'cleanupDone':True,'reason':status['reason'],'runtimeExitCode':status['exitCode'],'collectionBytes':receipt['snapshot']['bytes'],'unitSeconds':time.monotonic()-unit_start,'environmentUnchanged':before['sha256']==after['sha256'],'archiveSha256':hashlib.sha256((case/'raw.tar.gz').read_bytes()).hexdigest()}
report=case/'raw/result/source/evaluation.json'
if report.exists():
 r=json.loads(report.read_text());summary.update(evaluatorOverall=r['overall'],typecheck=r['typecheck']['status'],behavior=r['behavior']['status'],sourceBinding=r['sourceBinding'])
assert summary['unitSeconds']<240
(case/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)
