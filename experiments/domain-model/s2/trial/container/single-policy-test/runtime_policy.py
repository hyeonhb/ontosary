"""Exact OCI comparison after only predetermined owned-identity substitutions."""
import copy,json
from policy import RULE
ROLES={'/source':'source','/output':'auxiliary','/home/runner/cli-state':'cli-state','/home/worker':'shell-home','/scratch':'scratch','/materials':'materials'}
def normalize(native,run,shared,slice_name,old=False):
 s=copy.deepcopy(native['Spec']);cid=native['ID'];short=cid[:12];a=s['annotations']
 assert s['hostname']==short and a['nerdctl/hostname']==short
 s['hostname']=a['nerdctl/hostname']='<container-hostname>'
 expected_name='s2-namespace-baseline' if old else 'ontosary-'+run.rsplit('/',1)[-1]
 assert a['nerdctl/name']==expected_name;a['nerdctl/name']='<owned-unit>'
 state='/var/lib/nerdctl/1935db59/containers/default/'+cid;assert a['nerdctl/state-dir']==state;a['nerdctl/state-dir']='<owned-state>'
 expected_cgroup='system.slice:nerdctl:'+cid if old else slice_name+':nerdctl:'+cid
 assert s['linux']['cgroupsPath']==expected_cgroup;s['linux']['cgroupsPath']='<owned-parent>:nerdctl:<container>'
 roles={dst:run+'/'+({'auxiliary':'output','cli-state':'state'}.get(role,role) if old else role) for dst,role in ROLES.items()}
 roles.update({'/probe':shared+'/probe','/home/runner/cli-state/config.toml':shared+'/policy.toml','/etc/hostname':state+'/hostname','/etc/resolv.conf':state+'/resolv.conf','/etc/hosts':'/var/lib/nerdctl/1935db59/etchosts/default/'+cid+'/hosts'})
 for m in s['mounts']:
  if m['type']=='bind':assert m['destination'] in roles and m['source']==roles[m['destination']],'unowned-mount-source';m['source']='<role:'+m['destination']+'>'
 assert [m['destination'] for m in s['mounts']].index('/home/runner/cli-state')<[m['destination'] for m in s['mounts']].index('/home/runner/cli-state/config.toml')
 s['mounts']=sorted(s['mounts'],key=lambda m:m['destination'])
 for k,v in list(a.items()):
  if k.startswith('nerdctl/mounts.'):
   m=json.loads(v)
   if m['Type']=='bind':assert m['Source']==roles[m['Destination']];m['Source']='<role:'+m['Destination']+'>'
   a[k]=json.dumps(m,sort_keys=True)
 env=s['process']['env'];assert env.count('HOSTNAME='+short)==1;s['process']['env']=['HOSTNAME=<container-hostname>' if v=='HOSTNAME='+short else v for v in env]
 for hooks in s.get('hooks',{}).values():
  for hook in hooks:
   hook['env']=[v.split('=',1)[0]+'=<systemd-dynamic>' if v.split('=',1)[0] in ['INVOCATION_ID','JOURNAL_STREAM','SYSTEMD_EXEC_PID'] else v for v in hook.get('env',[])]
 return s

def baseline_verify(native,prior,run,shared,slice_name):
 n=normalize(native,run,shared,slice_name);p=normalize(prior,'/opt/ontosary-namespace-diagnosis/baseline','/opt/ontosary-namespace-diagnosis','system.slice',True)
 def security(s):return {'process':{k:v for k,v in s['process'].items() if k not in ['args','env']},'linux':s['linux'],'root':s['root'],'mounts':s['mounts'],'network':s['annotations']['nerdctl/networks']}
 assert security(n)==security(p),'baseline-security-mismatch'
 return n

def verify(candidate,baseline,candidate_identity,baseline_identity):
 c=normalize(candidate,**candidate_identity);b=normalize(baseline,**baseline_identity);b['linux']['seccomp']['syscalls'].append(copy.deepcopy(RULE))
 assert c==b,'candidate-extra-difference'
 return {'exactAddedRule':RULE,'normalizedSpecUnchangedOtherwise':True,'candidateIdentity':candidate_identity,'baselineIdentity':baseline_identity}
