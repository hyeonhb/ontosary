"""Install this round's fixed helper code; assemble immutable known inputs once."""
import pathlib,sys,os,json,subprocess,time
ROOT=pathlib.Path('/opt/ontosary-linux-evaluation');LOG=ROOT/'setup';LOG.mkdir()
sys.path.insert(0,'/opt/ontosary-fixture/code')
from common import command,write,NERD
image=json.loads((ROOT/'preparation/image.json').read_text());write(pathlib.Path('/opt/ontosary-fixture/image.json'),image)
(ROOT/'tools/readonly-proof.txt').write_text('Read-only mount canary\n');os.chmod(ROOT/'tools/readonly-proof.txt',0o666)
(ROOT/'assembled').mkdir();os.chown(ROOT/'assembled',1000,1000)
args=NERD+['run','--rm','--pull=never','--name','s2-linux-assemble','--user','1000:1000','--cap-drop','ALL','--security-opt','no-new-privileges','--network','none','--cpus','2','--memory','4g','--pids-limit','256','--read-only','--mount',f'type=bind,src={ROOT}/environment,dst=/environment,readonly=true','--mount',f'type=bind,src={ROOT}/tools,dst=/tools,readonly=true','--mount',f'type=bind,src={ROOT}/assembled,dst=/assembled,readonly=false',image['target'],'node','/tools/assemble.mjs']
command(LOG,args,timeout=120)
from fingerprint import fingerprint,inputs_fingerprint
start=time.monotonic();f=fingerprint(ROOT/'environment')
import gzip
(LOG/'environment-fingerprint.json.gz').write_bytes(gzip.compress((json.dumps(f,sort_keys=True)+'\n').encode(),mtime=0));write(LOG/'environment-summary.json',{'sha256':f['sha256'],'fileCount':f['fileCount'],'seconds':time.monotonic()-start})
licenses={}
lock=json.loads((ROOT/'environment/package-lock.json').read_text())
for name,p in lock['packages'].items():licenses[name]={k:p[k] for k in ['version','resolved','integrity','license','link','optional','os','cpu'] if k in p}
write(LOG/'dependency-lock-metadata.json',licenses)
print(json.dumps({'status':'assembled','environmentSha256':f['sha256']}))

f=inputs_fingerprint(ROOT);(LOG/'inputs-fingerprint.json.gz').write_bytes(gzip.compress((json.dumps(f,sort_keys=True)+'\n').encode(),mtime=0));write(LOG/'inputs-summary.json',{'sha256':f['sha256'],'fileCount':f['fileCount']})
