"""Full OCI Spec comparison; identities are checked before exact-position substitution."""
import copy,difflib,hashlib,json,pathlib
RULE={'names':['clone'],'action':'SCMP_ACT_ALLOW','args':[{'index':0,'op':'SCMP_CMP_EQ','value':2013397009}]}
RUNTIME_ENV={'HOME':'/root','LANG':'C.UTF-8'}
HOOK_ENV=['HOME=/root','LANG=C.UTF-8','PATH=:/usr/sbin:/sbin']
ROLES={'/source':'source','/output':'auxiliary','/home/runner/cli-state':'cli-state','/home/worker':'shell-home','/scratch':'scratch','/materials':'materials'}
class Rejected(RuntimeError):pass

def unique_env(env):
    keys=[]
    for entry in env:
        if '=' not in entry:raise Rejected('invalid-env')
        key=entry.split('=',1)[0]
        if key in keys:raise Rejected('duplicate-env:'+key)
        keys.append(key)
    return dict(x.split('=',1) for x in env)

def normalize(native,identity):
    s=copy.deepcopy(native['Spec']);proof=[];cid=identity['containerId'];rid=identity['runId'];run=identity['run'];shared=identity['shared'];image=identity['image']
    if native['ID']!=cid or native['Labels']['nerdctl/image-digest']!=image['target'] or native['SnapshotInfo']['Parent']!=image['chain']:raise Rejected('container-image-binding')
    if run!='/opt/ontosary-fixture/runs/'+rid or identity['slice']!='ontosary-'+rid+'.slice':raise Rejected('run-ownership')
    def replace(parent,key,expected,replacement,path,reason):
        if parent[key]!=expected:raise Rejected('ownership:'+path)
        proof.append({'path':path,'original':parent[key],'replacement':replacement,'proof':reason});parent[key]=replacement
    a=s['annotations'];short=cid[:12];state='/var/lib/nerdctl/1935db59/containers/default/'+cid
    replace(s,'hostname',short,'<hostname>','/hostname','actual container ID')
    for key,expected,value in [('nerdctl/hostname',short,'<hostname>'),('nerdctl/name','ontosary-'+rid,'<name>'),('nerdctl/state-dir',state,'<state>'),('nerdctl/image-digest',image['target'],'<verified-image>')]:replace(a,key,expected,value,'/annotations/'+key,'registered container/image binding')
    replace(s['linux'],'cgroupsPath',identity['slice']+':nerdctl:'+cid,'<worker-cgroup>','/linux/cgroupsPath','registered owned slice and container')
    roles={k:run+'/'+v for k,v in ROLES.items()};roles.update({'/probe':shared+'/probe','/home/runner/cli-state/config.toml':shared+'/policy.toml','/etc/hostname':state+'/hostname','/etc/resolv.conf':state+'/resolv.conf','/etc/hosts':'/var/lib/nerdctl/1935db59/etchosts/default/'+cid+'/hosts'})
    destinations=[m['destination'] for m in s['mounts']]
    allowed=set(roles)|{'/proc','/sys','/dev','/dev/mqueue','/dev/shm','/dev/pts','/sys/fs/cgroup','/tmp'}
    if len(set(destinations))!=len(destinations) or set(destinations)!=allowed:raise Rejected('mount-set-or-duplicate')
    # Only independent, pinned absolute destinations commute. Preserve every ancestor edge;
    # reject child-before-parent, duplicates and new/aliased destinations before sorting peers.
    for i,d in enumerate(destinations):
        for j,e in enumerate(destinations):
            if e.startswith(d+'/') and j<i:raise Rejected('mount-ancestor-order')
    for i,m in enumerate(s['mounts']):
        if m['type']=='bind':
            d=m['destination']
            if d not in roles:raise Rejected('unowned-bind')
            replace(m,'source',roles[d],'<role:'+d+'>',f'/mounts/{i}/source','registered mount role')
    for key,value in list(a.items()):
        if key.startswith('nerdctl/mounts.'):
            m=json.loads(value)
            if m['Type']=='bind':
                d=m['Destination']
                if d not in roles:raise Rejected('unowned-mount-annotation')
                replace(m,'Source',roles[d],'<role:'+d+'>','/annotations/'+key+'/Source','registered mount role')
            a[key]=json.dumps(m,sort_keys=True)
    s['mounts']=sorted(s['mounts'],key=lambda m:m['destination'])
    proof.append({'path':'/mounts','original':destinations,'replacement':[m['destination'] for m in s['mounts']],'proof':'fixed unique absolute destination set; all ancestor edges checked; independent peer mount operations only'})
    env=unique_env(s['process']['env'])
    if env.get('HOSTNAME')!=short:raise Rejected('hostname-env')
    i=s['process']['env'].index('HOSTNAME='+short);replace(s['process']['env'],i,'HOSTNAME='+short,'HOSTNAME=<hostname>',f'/process/env/{i}','actual container ID')
    if set(s.get('hooks',{}))!={'createRuntime','poststop'}:raise Rejected('hook-set')
    for kind,last in [('createRuntime','createRuntime'),('poststop','postStop')]:
        hooks=s['hooks'][kind]
        if len(hooks)!=1:raise Rejected('extra-hook')
        h=hooks[0];unique_env(h['env'])
        expected={'path':'/usr/local/bin/nerdctl','args':['/usr/local/bin/nerdctl','--address=/run/containerd/containerd.sock','--namespace=default','internal','oci-hook',last],'env':HOOK_ENV}
        if h!=expected:raise Rejected('hook-command-or-environment')
    return s,proof

def compare(candidate,baseline,candidate_identity,baseline_identity,added_rule=False):
    if candidate_identity['image']!=baseline_identity['image'] or candidate_identity['inputHashes']!=baseline_identity['inputHashes']:raise Rejected('experiment-input-mismatch')
    c,cp=normalize(candidate,candidate_identity);b,bp=normalize(baseline,baseline_identity)
    if added_rule:b['linux']['seccomp']['syscalls'].append(copy.deepcopy(RULE))
    diff=list(difflib.unified_diff(json.dumps(b,sort_keys=True,indent=2).splitlines(),json.dumps(c,sort_keys=True,indent=2).splitlines(),fromfile='expected',tofile='actual'))
    return {'accepted':not diff,'fullSpecDiff':diff,'candidateSubstitutions':cp,'baselineSubstitutions':bp,'exactAddedRule':RULE if added_rule else None}

def expected_legacy(native,identity,new_image):
    """Separate expected-input migration, never a permissive runtime normalizer.
    Caller pins original fixture bytes. Removes entire old inherited hook environment;
    old duplicate PATH / unverifiable systemd values are NOT accepted at runtime.
    """
    s=copy.deepcopy(native);changes=[]
    for k in ['createRuntime','poststop']:
        h=s['Spec']['hooks'][k][0];changes.append({'path':f'/hooks/{k}/0/env','old':h['env'],'new':HOOK_ENV,'reason':'explicit runtime environment replaces all inherited environment'});h['env']=HOOK_ENV.copy()
    old=s['Spec']['annotations']['nerdctl/image-digest'];s['Spec']['annotations']['nerdctl/image-digest']=new_image['target'];s['Labels']['nerdctl/image-digest']=new_image['target'];s['SnapshotInfo']['Parent']=new_image['chain']
    changes.append({'path':'image identity','old':old,'new':new_image,'reason':'same pinned recipe, new immutable archive identity; actual binaries separately verified'})
    ident={**identity,'image':new_image}
    return s,ident,changes
