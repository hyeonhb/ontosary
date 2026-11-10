"""Current native target/config/rootfs binding; no model invocation."""
import hashlib,json,pathlib,sys
from common import ROOT,NERD,CTR,command,write

def identify(log,name):
    native=json.loads(command(log,NERD+['image','inspect','--mode=native',name])[1])[0]
    target=native['Image']['Target']['digest']
    raw=command(log,CTR+['content','get',target])[1];assert 'sha256:'+hashlib.sha256(raw.encode()).hexdigest()==target
    manifest=json.loads(raw);config_digest=manifest['config']['digest']
    rawconfig=command(log,CTR+['content','get',config_digest])[1];assert 'sha256:'+hashlib.sha256(rawconfig.encode()).hexdigest()==config_digest
    config=json.loads(rawconfig);assert (config['os'],config['architecture'])==('linux','arm64')
    layers=config['rootfs']['diff_ids'];chain=layers[0]
    for layer in layers[1:]:chain='sha256:'+hashlib.sha256((chain+' '+layer).encode()).hexdigest()
    (log/'manifest.oci').write_text(raw);(log/'config.oci').write_text(rawconfig);write(log/'native-image.json',native)
    return {'name':native['Image']['Name'],'target':target,'config':config_digest,'chain':chain,'platform':'linux/arm64'}
if __name__=='__main__':
    ROOT.mkdir(mode=0o700,exist_ok=True);log=ROOT/'environment';log.mkdir(mode=0o700)
    for args in [['uname','-a'],['systemctl','--version'],NERD+['version'],['sh','-c','command -v python3; command -v systemctl; command -v mkfifo; test -d /sys/fs/cgroup']]:command(log,args)
    image=identify(log,sys.argv[1]);write(ROOT/'image.json',image)
    cid=command(log,NERD+['create','--pull=never','--name','s2-lifecycle-environment','--user','1000:1000','--cap-drop','ALL','--security-opt','no-new-privileges','--network','none','--cpus','2','--memory','4g','--pids-limit','256','--read-only',image['target'],'sh','-c','echo LIFECYCLE_ENV_STARTED; id; node --version'])[1].strip()
    before=json.loads(command(log,NERD+['inspect',cid])[1])[0];assert before['Image']==image['target'];write(log/'container.json',before)
    command(log,NERD+['start',cid]);code=command(log,NERD+['wait',cid])[1].strip();output=command(log,NERD+['logs',cid])[1];assert code=='0' and 'LIFECYCLE_ENV_STARTED' in output and 'v22.19.0' in output
    command(log,NERD+['rm',cid]);print(json.dumps(image))
