"""Strict field-path comparison; only the pre-frozen timing paths and declared input mode differ."""
import argparse,collections,copy,gzip,hashlib,json,pathlib
policy=json.loads((pathlib.Path(__file__).parent/'comparison-policy.json').read_text())
def normalized(value,platform="linux"):
 value=copy.deepcopy(value)
 for pointer in policy['ignoredFieldPaths']:
  keys=pointer.strip('/').split('/');parent=value
  for k in keys[:-1]:parent=parent[k]
  parent.pop(keys[-1])
 checked=value['typecheck']['checkedFiles'];inputs=value['typecheck']['inputHashes']
 assert len({r['file'] for r in checked})==len(checked), 'Duplicate checked-file identity'
 if platform=='macOS':
  for alias in policy['rootCorrespondence']:
   old,new,h=alias['macOS'],alias['linux'],alias['sha256']
   matches=[r for r in checked if r['file']==old]
   assert len(matches)==1 and matches[0]['sha256']==h and inputs[old]==h
   assert new not in inputs and not any(r['file']==new for r in checked)
   matches[0]['file']=new;inputs[new]=inputs.pop(old)
 value['typecheck']['checkedFiles']=sorted(checked,key=lambda r:r['file'])
 return value

def compare(left,right):
 differences=[]
 def walk(a,b,p):
  if type(a)!=type(b):differences.append({'path':p,'left':a,'right':b});return
  if isinstance(a,dict):
   for k in sorted(a.keys()|b.keys()):
    q=p+'/'+k.replace('~','~0').replace('/','~1')
    if k not in a or k not in b:differences.append({'path':q,'leftPresent':k in a,'rightPresent':k in b})
    else:walk(a[k],b[k],q)
  elif isinstance(a,list):
   if len(a)!=len(b):differences.append({'path':p+'/length','left':len(a),'right':len(b)})
   for i,(x,y) in enumerate(zip(a,b)):walk(x,y,p+'/'+str(i))
  elif a!=b:differences.append({'path':p,'left':a,'right':b})
 walk(left,right,'');return differences

def audit(case,summary):
 raw=case/'raw';receipt=json.loads((raw/'result/fixture.json').read_text());term=receipt['termination'];state=json.loads((raw/'state.json').read_text())
 for key in ['runId','containerId','image','cgroup','cgroupInode']:assert term[key]==state[key]
 assert term['runId']==summary['runId']==case.name
 assert state['state']=='finalized' and state['cleanupDone'] and state['classification']=='normal-fixture'
 assert 'Result=success\n' in (case/'service.txt').read_text()
 assert term['confirmed'] and term['admissionClosed'] and term['kernel']['events']['populated']=='0' and not term['kernel']['members']
 assert term['reason']=='exit' and term['exitCode']==0 and term['runtimeState']['Pid']==0 and not term['runtimeState']['Running']
 assert not any(state.get(k) for k in ['createPending','startPending','execPending'])
 assert summary['environmentUnchanged'] and summary['unitSeconds']<240 and receipt['snapshot']['fileCount']<=128 and receipt['snapshot']['bytes']<=16*1024*1024
 for f,metadata in receipt['snapshot']['files'].items():
  b=(raw/'result'/f).read_bytes();assert len(b)==metadata['bytes'] and hashlib.sha256(b).hexdigest()==metadata['sha256']
 worker=json.loads((raw/'result/source/audit.json').read_text());assert worker['status'].startswith('Name:\tnode\n') and worker['pid']==1 and worker['uid']==1000 and worker['gid']==1000 and worker['readonly']==dict.fromkeys(['environment','source','tools'],'EROFS')
 assert 'NoNewPrivs:\t1' in worker['status'] and 'CapEff:\t0000000000000000' in worker['status']
 inspected=json.loads((raw/'container-started.json').read_text());native=json.loads((raw/'container-native.json').read_text());hc=inspected['HostConfig']
 assert hc['NetworkMode']=='none' and hc['ReadonlyRootfs'] and hc['CgroupnsMode']=='private' and not hc['Privileged'] and hc['Memory']==4*1024**3 and hc['CpuQuota']/hc['CpuPeriod']==2 and hc['PidsLimit']==256
 assert native['ID']==state['containerId']
 assert native['Spec']['process']['args']==['docker-entrypoint.sh','node','/tools/job.mjs',state['job']['variant'],state['job']['inputMode'],state['job']['public']]
 assert native['SnapshotInfo']['Parent']==state['image']['chain'] and native['Labels']['nerdctl/image-digest']==state['image']['target'] and inspected['Image']==state['image']['target']
 mounts={x['Destination']:x for x in inspected['Mounts']};assert set(mounts)=={'/environment','/tools','/source','/input.json','/output','/auxiliary','/tmp'}
 actual={line.split()[4]:line.split()[5].split(',') for line in worker['mountinfo'].splitlines()}
 for dst in ['/environment','/tools','/source','/input.json']:assert not mounts[dst]['RW'] and 'ro' in actual[dst]
 assert 'ro' in actual['/sys/fs/cgroup'] and mounts['/output']['Source']==term['source'] and mounts['/auxiliary']['Source']==term['auxiliary']
 assert 'RuntimeMaxSec=210' in (raw/'service.unit').read_text() and state['taskSeconds']==180 and term['deadlineMono']==term['start']['mono']+180
 return {'terminationAndCleanup':'passed','readOnlyAndResources':'passed','fullCollectedHashes':'passed'}

def main():
 p=argparse.ArgumentParser();p.add_argument('units');p.add_argument('output');p.add_argument('--core',action='store_true');a=p.parse_args()
 rows=[];reports=collections.defaultdict(list);differences=[]
 for case in sorted(pathlib.Path(a.units).iterdir()):
  if not (case/'summary.json').exists():continue
  summary=json.loads((case/'summary.json').read_text());job=summary['job']
  if job in ['timeout','control']:continue
  report=json.loads((case/'raw/result/source/evaluation.json').read_text());variant='reference' if job=='reference-delta' else job
  oracle_path=pathlib.Path('experiments/domain-model/s2/verification/2026-11-10-trial-preparation/oracle')/(variant+'.json.gz');oracle=json.loads(gzip.decompress(oracle_path.read_bytes()))
  expected_mode='explicit-baseline-delta' if job=='reference-delta' else 'complete-root';assert report['inputMode']==expected_mode and oracle['inputMode']=='explicit-baseline-delta'
  left=normalized(oracle,'macOS');right=normalized(report);left['inputMode']=right['inputMode']
  diff=compare(left,right);differences.extend({'runId':case.name,'comparison':'macOS',**d} for d in diff)
  gates=audit(case,summary)
  if job in ['baseline','reference']:
   public=json.loads((case/'raw/result/source/public.json').read_text());assert public['status']==report['typecheck']['status']=='passed' and public['diagnostics']==report['typecheck']['diagnostics']==[] and public['programFiles']==report['typecheck']['cost']['programFiles']
  if variant=='baseline':assert report['behavior']['preservation']=={'passed':16,'total':16} and report['behavior']['draft']=={'passed':6,'total':36} and report['overall']=='failed' and report['sourceBinding']
  if variant=='reference':assert report['overall']=='passed' and len(report['behavior']['cases'])==52 and all(c['status']=='passed' for c in report['behavior']['cases']) and report['sourceBinding']
  if variant=='helper-type-error':assert report['typecheck']['status']=='failed' and report['behavior']['status']=='not-run' and report['overall']!='passed'
  if variant=='wrong-modal-order':assert report['typecheck']['status']=='passed' and report['behavior']['status']=='failed' and any(not c['details']['payload']['pass'] for c in report['behavior']['cases'])
  reports[variant].append((case.name,report));rows.append({**summary,**gates,'macOSDifferenceCount':len(diff),'intentionalInputModeDifference':oracle['inputMode']!=report['inputMode']})
 for variant,values in reports.items():
  for rid,report in values[1:]:
   left=normalized(values[0][1]);right=normalized(report);left['inputMode']=right['inputMode']
   differences.extend({'runId':rid,'comparison':'linux-repeat-or-input-mode',**d} for d in compare(left,right))
 counts=collections.Counter(r['job'] for r in rows);expected={'baseline':1,'reference':1} if a.core else {'baseline':2,'reference':2,'helper-type-error':1,'wrong-modal-order':1,'reference-delta':1}
 complete=counts==expected
 result={'status':'passed' if complete and not differences else 'blocked','scope':'core' if a.core else 'seven-units','policy':policy,'counts':dict(counts),'expected':expected,'rows':rows,'differences':differences,'allFieldsCompared':True,'originalVerifyUnchanged':True}
 pathlib.Path(a.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'counts':dict(counts),'differences':len(differences)}))
 raise SystemExit(0 if result['status']=='passed' else 1)

if __name__=='__main__':main()
