"""One fixed native CLI sandbox command in an OS-isolated nonprivileged service."""
import hashlib,json,os,pathlib,subprocess,sys,time
from bounded import run
BASE=pathlib.Path('/opt/s2-smoke');PUBLIC=BASE/'public'
NODE=str(PUBLIC/'usr/local/bin/node')
CLI=str(PUBLIC/'usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-arm64/vendor/aarch64-unknown-linux-musl/bin/codex')
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        while b:=f.read(1024*1024):h.update(b)
    return h.hexdigest()
def main():
    plan=json.loads((BASE/'plan.json').read_text());out={'runId':plan['runId'],'calls':[],'sandboxAttempts':0,'workerPid':os.getpid()}
    try:
        status=pathlib.Path('/proc/self/status').read_text();cg=pathlib.Path('/proc/self/cgroup').read_text().strip().split('::',1)[1]
        network={'namespace':os.readlink('/proc/self/ns/net'),'managerNamespace':plan['managerNamespace']}
        for key,args in [('links',['ip','-j','link']),('routes4',['ip','-j','route']),('routes6',['ip','-j','-6','route'])]:
            r=run(args,2,env={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin'},cap=65536)
            if r['exitCode'] or r['truncated'] or r['timedOut']:raise RuntimeError('network-observation-missing')
            network[key]=json.loads(r['stdout'])
        limits={n:(pathlib.Path('/sys/fs/cgroup'+cg)/n).read_text().strip() for n in ['cpu.max','memory.max','pids.max']}
        out.update(uid=os.getuid(),gid=os.getgid(),groups=os.getgroups(),status=status,cgroup=cg,limits=limits,network=network,environmentKeys=sorted(os.environ),binaries={'node':sha(NODE),'codex':sha(CLI)},configHash=sha('/home/runner/cli-state/config.toml'),payloadHash=sha('/source/payload.mjs'))
        quota,period=map(int,limits['cpu.max'].split())
        if not (os.getuid()==22002 and os.getgid()==22002 and os.getgroups() in [[],[22002]] and 'CapEff:\t0000000000000000' in status and 'CapBnd:\t0000000000000000' in status and 'NoNewPrivs:\t1' in status and quota==2*period and limits['memory.max']==str(4*1024**3) and limits['pids.max']=='256'):raise RuntimeError('worker-security-or-resource-mismatch')
        if not (network['namespace']!=network['managerNamespace'] and network['links'] and all(x['ifname']=='lo' for x in network['links']) and all(x.get('dev')=='lo' for x in network['routes4']+network['routes6'])):raise RuntimeError('external-egress-not-isolated')
        if out['binaries']!=plan['binaries'] or out['configHash']!=plan['configHash'] or out['payloadHash']!=plan['payloadHash']:raise RuntimeError('frozen-input-mismatch')
        env={'PATH':'/usr/local/bin:/usr/bin:/bin','HOME':'/home/runner/cli-state','CODEX_HOME':'/home/runner/cli-state','TMPDIR':'/scratch','LANG':'C.UTF-8'}
        for args in [[NODE,'--version'],[CLI,'--version'],[CLI,'sandbox','--help']]:
            r=run(args,3,env=env,cap=65536);out['calls'].append(r)
            if r['exitCode'] or r['timedOut'] or r['truncated']:raise RuntimeError('discovery-failed')
        if out['calls'][0]['stdout'].strip()!='v22.19.0' or out['calls'][1]['stdout'].strip()!='codex-cli 0.167.0-alpha.3.2':raise RuntimeError('version-mismatch')
        out['sandboxAttempts']=1
        def observe(pid):
            return {'pid':pid,'cgroup':pathlib.Path(f'/proc/{pid}/cgroup').read_text(),'workerCgroup':cg}
        out['native']=run(plan['argv'],15,env=env,cwd='/source',cap=256*1024,on_start=observe)
        out['outputContent']=pathlib.Path('/source/output.txt').read_text() if pathlib.Path('/source/output.txt').exists() else None
        out['configUnchanged']=sha('/home/runner/cli-state/config.toml')==out['configHash']
    except Exception as e:out['error']=str(e)
    print(json.dumps(out),flush=True)
if __name__=='__main__':main()
