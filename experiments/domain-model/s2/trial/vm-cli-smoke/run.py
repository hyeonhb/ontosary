"""One disposable VM and one CLI smoke command; bounded diagnostics, no submission."""
import argparse,datetime,fcntl,hashlib,json,os,pathlib,shutil,signal,subprocess,sys,tarfile,time,uuid
HERE=pathlib.Path(__file__).resolve().parent;CONTAINER=HERE.parent/'container'
sys.path[:0]=[str(HERE),str(CONTAINER/'single-policy-test'),str(CONTAINER/'execution-lifecycle')]
from artifacts import Store,digest_file
from deadline import remaining,limit
from materialize import extract,VENDOR
from bounded import run as capture
PYTHON=str(pathlib.Path(sys.executable).resolve())
def read(p):return json.loads(pathlib.Path(p).read_text())
def write(p,v):pathlib.Path(p).write_text(json.dumps(v,indent=2)+'\n')
def sha(p):return digest_file(p,time.monotonic()+30)['sha256']

def verdict(worker,outer):
    if outer.get('truncated') or outer.get('timedOut'):return 'inconclusive'
    native=worker.get('native')
    if not native:return 'blocked-before-payload' if worker.get('error') else 'inconclusive'
    if native.get('truncated') or native.get('timedOut'):return 'inconclusive'
    try:events=[json.loads(line) for line in native['stdout'].splitlines()]
    except (ValueError,KeyError):return 'inconclusive'
    started=any(x=={'event':'payload-start','runId':worker['runId']} for x in events)
    if not started:return 'blocked-before-payload' if native['exitCode']!=0 else 'inconclusive'
    expected={'event':'payload-complete','runId':worker['runId'],'sourceRead':True,'sourceWrite':True,'materialRead':True}
    if native['exitCode']!=0:return 'payload-failed'
    return 'payload-completed' if events==[{'event':'payload-start','runId':worker['runId']},expected] and worker.get('outputContent')=='smoke output '+worker['runId']+'\n' and worker.get('configUnchanged') is True and not worker.get('error') and outer['exitCode']==0 else 'inconclusive'

class Smoke:
    def __init__(self,work):
        self.w=pathlib.Path(work).resolve();self.plan=read(self.w/'plan.json');self.budget=read(self.w/'budget.json');self.root=pathlib.Path(self.plan['root']);self.name=self.plan['name'];self.lima=str(self.root/'prefix/bin/limactl');self.phase='experiment'
        self.env={'PATH':'/usr/bin:/bin:/usr/sbin:/sbin','HOME':str(self.root/'home'),'LIMA_HOME':str(self.root/'lima'),'LANG':'C.UTF-8'}
    def diagnostic_capacity(self):
        diagnostic_root=pathlib.Path(self.plan.get('diagnosticRoot',str(self.w)))
        used=sum(p.stat().st_size for pattern in ['*.stdout','*.stderr'] for p in diagnostic_root.rglob(pattern))
        return min(1024*1024,max(0,(4*1024*1024-used-65536)//2))
    def record_command(self,row,cap):
        key='command-'+uuid.uuid4().hex[:12]
        stored=0;dropped=False
        for stream in ['stdout','stderr']:
            data=row[stream].encode('utf-8');part=data[:cap]
            dropped |= len(part)!=len(data)
            if cap:(self.w/(key+'.'+stream)).write_bytes(part)
            stored+=len(part)
        row['diagnostics']={'status':'partial' if dropped or row['truncated'] else 'stored',
                            'storedBytes':stored,'storageTruncated':dropped,'captureTruncated':row['truncated'],'record':key+'.json'}
        write(self.w/(key+'.json'),{k:v for k,v in row.items() if k not in ['stdout','stderr']})
    def cmd(self,args,timeout=30,check=True,safety=False):
        seconds=timeout if safety else limit(self.budget,self.phase,timeout)
        if safety:
            # Completion and query parsing use bounded memory, independently of log storage.
            row=capture(args,seconds,env=self.env,cap=1024*1024,overflow='discard')
            try:self.record_command(row,self.diagnostic_capacity())
            except Exception as e:row['diagnostics']={'status':'failed','error':str(e)[:500]}
        else:
            cap=self.diagnostic_capacity();row=capture(args,seconds,env=self.env,cap=cap)
            self.record_command(row,cap)
        if check and (row['exitCode'] or row['truncated'] or row['timedOut']):raise RuntimeError('command-failed:'+str(args)+':'+row['stderr'][-800:])
        return row
    def cleanup_receipt(self,result):
        result['receiptWritten']=True
        try:write(self.w/'cleanup.json',result)
        except Exception as e:
            result['receiptWritten']=False
            result['diagnosticErrors'].append({'action':'cleanup-receipt','error':str(e)[:500]})
        return result
    def guest(self,args,**kw):return self.cmd([self.lima,'shell','--workdir=/tmp',self.name,'sudo','-n',*args],**kw)
    def checked_owner(self):
        owner=read(self.w/'ownership.json')
        if owner['root']!=str(self.root) or owner['name']!=self.name or not self.root.name.startswith('ontosary-s2-') or self.root.is_symlink():raise RuntimeError('cleanup-ownership')
        return owner
    def cleanup(self):
        """Adapted recovery.cleanup ownership/stop/delete/absence path; no container export."""
        result={'cleanupStatus':'unconfirmed','vmAbsent':False,'rootAbsent':not self.root.exists(),'attempts':[],'errors':[],'commandResults':[],'diagnosticErrors':[],'owner':{'root':str(self.root),'name':self.name},'vmDisposalIsNotSubmissionProof':True}
        def observe(action,row):
            result['commandResults'].append({'action':action,**{k:row[k] for k in ['exitCode','timedOut','truncated','diagnostics'] if k in row}})
            if row.get('diagnostics',{}).get('status')=='failed':result['diagnosticErrors'].append({'action':action,**row['diagnostics']})
        owner_path=self.w/'ownership.json'
        if not owner_path.exists():
            result['cleanupStatus']='not-created' if not self.root.exists() else 'unconfirmed';return self.cleanup_receipt(result)
        owner=self.checked_owner()
        # Safety disposal has its own finite allowance even if the experiment has expired.
        if pathlib.Path(self.lima).exists():
            for action in ['stop','delete']:
                args=[self.lima,action,'--force',self.name];result['attempts'].append(args)
                try:
                    r=self.cmd(args,30,check=False,safety=True)
                    observe(action,r)
                    if r['exitCode'] or r['timedOut']:result['errors'].append({'action':action,'exitCode':r['exitCode'],'timedOut':r['timedOut']})
                except Exception as e:result['errors'].append({'action':action,'error':str(e)})
            try:
                args=[self.lima,'list','--json'];result['attempts'].append(args);r=self.cmd(args,8,check=False,safety=True)
                observe('list',r)
                if r['exitCode'] or r['truncated'] or r['timedOut']:raise RuntimeError('listing-failed')
                rows=[json.loads(x) for x in r['stdout'].splitlines() if x.strip()]
                if any(not isinstance(x,dict) or not isinstance(x.get('name'),str) or not x['name'] for x in rows):raise RuntimeError('listing-schema')
                if any(x.get('name')==self.name for x in rows) or (self.root/'lima'/self.name).exists():raise RuntimeError('VM-present')
                ps=capture(['ps','-axo','pid=,command='],5,cap=1024*1024,overflow='discard')
                observe('process-absence',ps)
                if ps['exitCode'] or ps['truncated'] or ps['timedOut']:raise RuntimeError('owned-process-presence-unknown')
                processes=[line.split(None,1) for line in ps['stdout'].splitlines() if line.strip()]
                if any(len(row)!=2 or not row[0].isdigit() or int(row[0])<=0 for row in processes):raise RuntimeError('process-listing-schema')
                if any(str(self.root/'prefix') in command or str(self.root/'lima') in command for pid,command in processes):raise RuntimeError('owned-process-presence-unknown')
                result['vmAbsent']=True;result['ownedProcesses']=[]
            except Exception as e:result['errors'].append({'action':'absence','error':str(e)})
        elif not owner['vmRegistered']:result['vmAbsent']=True
        else:result['errors'].append({'action':'absence','error':'owned-lima-executable-missing'})
        if result['vmAbsent']:
            try:
                if self.root.exists():shutil.rmtree(self.root)
                result.update(rootAbsent=True,cleanupStatus='complete')
            except Exception as e:result['errors'].append({'action':'root-remove','error':str(e)[:500]})
        return self.cleanup_receipt(result)
    def dispose(self):
        owner=self.w/'ownership.json'
        if not owner.exists():return self.cleanup()
        # Ownership already exists before resources do; logging need not be writable to lock it.
        with owner.open('r') as lock:
            end=time.monotonic()+100
            while True:
                try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);break
                except BlockingIOError:
                    if time.monotonic()>end:raise TimeoutError('cleanup-lock')
                    time.sleep(.1)
            self.checked_owner()
            diagnostic_errors=[]
            if (self.w/'disposed').exists():
                try:
                    prior=read(self.w/'cleanup.json')
                    if prior.get('owner')=={'root':str(self.root),'name':self.name} and prior.get('cleanupStatus')=='complete' and prior.get('vmAbsent') and prior.get('rootAbsent') and not self.root.exists():return prior
                except Exception as e:diagnostic_errors.append({'action':'prior-receipt','error':str(e)[:500]})
            result=self.cleanup()
            result['diagnosticErrors']+=diagnostic_errors
            if result['cleanupStatus']=='complete' and result['receiptWritten']:
                try:(self.w/'disposed').touch()
                except Exception as e:result['diagnosticErrors'].append({'action':'disposed-marker','error':str(e)[:500]})
            if diagnostic_errors or any(x['action']=='disposed-marker' for x in result['diagnosticErrors']):self.cleanup_receipt(result)
            return result
    def extra_bundle_files(self):
        return {}

    def work(self):
        if (self.w/'execution-started.json').exists():raise RuntimeError('round-already-attempted')
        freeze=read(self.w/'freeze.json')
        if not read(self.w/'local-gate.json')['passed'] or any(sha(path)!=value for path,value in freeze['codeHashes'].items()):raise RuntimeError('local-or-code-gate')
        if any(sha(self.w/name)!=value for name,value in freeze['inputHashes'].items()):raise RuntimeError('frozen-plan-mismatch')
        write(self.w/'execution-started.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'freezeHash':sha(self.w/'freeze.json')})
        if self.root.exists():raise RuntimeError('owned-root-exists')
        write(self.w/'ownership.json',{'root':str(self.root),'name':self.name,'vmRegistered':False});self.root.mkdir(mode=0o700);(self.root/'home').mkdir(mode=0o700)
        store=Store(self.plan['store']);cache=[]
        for old in read(self.w/'cache-inputs.json'):
            r=store.lookup(old['request'],time.monotonic()+limit(self.budget,'experiment',30))
            if not r or r['actual']!=old['actual']:raise RuntimeError('public-cache-mismatch')
            cache.append(r)
        write(self.w/'cache.json',cache);byname={r['request']['name']:r for r in cache}
        (self.root/'prefix').mkdir()
        self.cmd([PYTHON,'-c','import tarfile,sys;tarfile.open(sys.argv[1]).extractall(sys.argv[2],filter="data")',byname['lima-2.3.0-Darwin-arm64']['path'],str(self.root/'prefix')],30)
        bundle=self.root/'bundle';bundle.mkdir(mode=0o755)
        materialized=extract(byname['ontosary-fixed-trace-image'],bundle/'public',time.monotonic()+limit(self.budget,'experiment',60));(bundle/'public').chmod(0o755);write(self.w/'materialized.json',materialized)
        for name in ['bounded.py','worker.py','setup.py','payload.mjs']:shutil.copyfile(HERE/name,bundle/name)
        for name, path in self.extra_bundle_files().items():
            shutil.copy(path, bundle / name)
        shutil.copyfile(self.w/'config.toml',bundle/'config.toml');shutil.copyfile(self.w/'worker-plan.json',bundle/'plan.json')
        files={str(p.relative_to(bundle)):sha(p) for p in bundle.rglob('*') if p.is_file()};write(self.w/'input-hashes.json',files);write(bundle/'manifest.json',files)
        archive=self.root/'inputs.tar'
        # Packaging is bounded by the same host command deadline, not an unbounded inline tar.
        self.cmd([PYTHON,'-c','import tarfile,pathlib,sys;t=tarfile.open(sys.argv[2],"w");b=pathlib.Path(sys.argv[1]);[(t.add(p,arcname=str(p.relative_to(b)),recursive=False)) for p in b.rglob("*") if p.is_file()];t.close()',str(bundle),str(archive)],60)
        ubuntu=byname['ubuntu-26.04-20261016-arm64'];nerd=byname['nerdctl-full-2.4.2-linux-arm64'];text=(CONTAINER/'lima.yaml').read_text().replace(ubuntu['request']['url'],ubuntu['path']).replace('  system: true','  archives:\n    - location: '+nerd['path']+'\n      arch: aarch64\n      digest: sha256:'+nerd['actual']['sha256']+'\n  system: true');(self.root/'vm.yaml').write_text(text);write(self.w/'vm-config.json',{'text':text,'sourceHash':sha(CONTAINER/'lima.yaml')})
        if limit(self.budget,'experiment')<210:raise RuntimeError('insufficient-start-and-cleanup-reserve')
        write(self.w/'ownership.json',{'root':str(self.root),'name':self.name,'vmRegistered':True})
        guard=subprocess.Popen([PYTHON,str(HERE/'run.py'),'watch','--work',str(self.w),'--parent',str(os.getpid())],start_new_session=True,stdout=(self.w/'watchdog.log').open('w'),stderr=subprocess.STDOUT);write(self.w/'watchdog.json',{'pid':guard.pid,'parent':os.getpid(),'experimentDeadline':self.budget['deadlines']['experiment'],'disposalTool':'same owned cleanup path, separate process/session'})
        self.cmd([self.lima,'start','--yes','--name='+self.name,'--timeout='+str(int(limit(self.budget,'experiment',600)))+'s',str(self.root/'vm.yaml')],600)
        manager=self.cmd([self.lima,'shell','--workdir=/tmp',self.name,'id','-un'])['stdout'].strip()
        self.cmd([self.lima,'copy',str(archive),self.name+':/tmp/ontosary-smoke-inputs.tar'],60)
        installer="import pathlib,tarfile,hashlib,json,sys; p=pathlib.Path('/tmp/ontosary-smoke-inputs.tar'); assert hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==sys.argv[1]; b=pathlib.Path('/opt/s2-smoke'); assert not b.exists(); b.mkdir(); t=tarfile.open(p); assert all(m.isfile() and not m.name.startswith('/') and '..' not in pathlib.PurePosixPath(m.name).parts for m in t.getmembers()); t.extractall(b,filter='data'); manifest=json.loads((b/'manifest.json').read_text()); assert all(hashlib.file_digest((b/n).open('rb'),'sha256').hexdigest()==h for n,h in manifest.items()); p.unlink(); print(sys.version)"
        self.guest(['python3','-c',installer,sha(archive)],timeout=60)
        setup=self.guest(['python3','/opt/s2-smoke/setup.py',manager],timeout=15);prepared=json.loads(setup['stdout']);write(self.w/'guest-preparation.json',prepared)
        if limit(self.budget,'experiment')<210:raise RuntimeError('insufficient-unit-reserve')
        props=[line for line in prepared['unit'].splitlines() if '=' in line and line.split('=',1)[0] not in ['Type','ExecStart','StandardOutput','StandardError']]
        args=['systemd-run','--unit=ontosary-smoke','--wait','--pipe','--collect',*["--property="+p for p in props],'/usr/bin/env','-i','PATH=/usr/sbin:/usr/bin:/sbin:/bin','LANG=C.UTF-8','HOME=/home/worker','/usr/bin/python3','/opt/s2-smoke/worker.py']
        write(self.w/'native-command.json',{'serviceArgs':args,'cliArgs':prepared['plan']['argv'],'inputHashes':files,'preparedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'maximumSeconds':120,'payloadLimitSeconds':15})
        return self.run_units(args)

    def run_units(self,args):
        outer=self.guest(args,timeout=110,check=False);write(self.w/'outer.json',outer)
        rows=[json.loads(line) for line in outer['stdout'].splitlines() if line.startswith('{')];worker=rows[-1] if rows else {};write(self.w/'worker.json',worker)
        self.guest(['systemctl','stop','ontosary-smoke.service'],timeout=5,check=False)
        return {'observation':verdict(worker,outer),'sandboxAttempts':worker.get('sandboxAttempts',0),'cliDiscoveryCalls':sum(bool(x.get('args') and x['args'][0].endswith('/codex')) for x in worker.get('calls',[]))}

def execute(smoke):
    result={'observation':'inconclusive','fixtureOnly':True,'validSubmission':False,'trialAuthorized':False,'readyForTrial':False,'results':None}
    try:result.update(smoke.work())
    except Exception as e:result['error']=str(e)
    finally:
        # A diagnostic write failure cannot precede or bypass disposal.
        try:result['cleanup']=smoke.dispose()
        except Exception as e:result['cleanupError']=str(e)
    write(smoke.w/'result.json',result);print(json.dumps(result),flush=True)
    return result

def watch(smoke,parent):
    while not (smoke.w/'disposed').exists():
        try:os.kill(parent,0);alive=True
        except ProcessLookupError:alive=False
        if not alive or remaining(smoke.budget,'experiment')<=0:
            smoke.dispose();return
        time.sleep(.5)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['execute','cleanup','watch']);p.add_argument('--work',required=True);p.add_argument('--parent',type=int);a=p.parse_args();s=Smoke(a.work)
    if a.action=='execute':execute(s)
    elif a.action=='cleanup':print(json.dumps(s.dispose()))
    else:watch(s,a.parent)
