"""Single-use, metered comparison. The shell runs locally and Codex has no native tools."""
import argparse
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from lab import BASE, HERE, NOTES, OUT, ROOT, W, git, save, sha, shell, workspace

spec = importlib.util.spec_from_file_location('shipping',ROOT/'experiments/domain-model/s2/trial/angular-shipping/pilot/collect.py')
shipping = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shipping)
LIMIT = {'seconds':720,'input_tokens':400000,'output_tokens':8000}
KEYS = ('input_tokens','cached_input_tokens','output_tokens','reasoning_output_tokens')
HISTORY = '3bdaafe4b5ecde577fe9b5c69a5d1819e37c4ccb'
REPO = ROOT/'work/excalidraw-followup/upstream.git'
PLAN = HERE/'allocation.json'
COMMON = """You have a clean Excalidraw source tree with installed dependencies. Respond with one JSON object at a time. {"op":"shell","command":"..."} runs bash from the repository root. You may search, edit (including new files), and test locally with rg, git diff, python3, node, and ./node_modules/.bin/vitest run --pool=threads. Files persist between commands. Command output is limited to 20000 bytes (head and tail). {"op":"submit","summary":"..."} immediately submits the current source changes, including new non-ignored files, and ends the session. No need to print a diff or commit. No internet. Work within 720 seconds, 400000 cumulative input and 8000 cumulative output tokens (including reasoning)."""
EXTRA = 'An optional development note is available at ../material/note.md. Its relative attachment is beside it. Files cited by its GitHub links are available offline under ../material/archive/ at their linked paths.'
REQUEST = HERE.parent/'excalidraw-followup/request.md'


def packet(arm, history, usage):
    payload = {'instructions':COMMON, 'task':REQUEST.read_text()}
    if arm != 'A':
        payload['material'] = EXTRA
    payload.update(history=history, cumulativeUsage=usage)
    return shipping.encode(payload)


def material_files(arm):
    if arm == 'A':
        return {}
    note = (HERE/'prose.md' if arm=='B' else NOTES/'note.md').read_bytes()
    paths = set(re.findall(r'github.com/excalidraw/excalidraw/blob/'+HISTORY+r'/([^#)]+)', note.decode()))
    assert len(paths)==4
    return {'note.md':note,'source-check.json':(NOTES/'source-check.json').read_bytes(),
            **{'archive/'+p:git(REPO,'show',HISTORY+':'+p) for p in sorted(paths)}}


def validate_packet(data, work):
    captured = []
    class Capture(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass
        def do_POST(self):
            captured.append(json.loads(self.rfile.read(int(self.headers['Content-Length']))))
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"error":{"message":"loopback capture"}}')
    with HTTPServer(('127.0.0.1',0),Capture) as http:
        thread = threading.Thread(target=http.serve_forever,daemon=True)
        thread.start()
        env = dict(PATH=os.environ['PATH'], HOME=str(work/'mock-home'), CODEX_HOME=str(work/'mock-home'),LANG='C')
        proc = subprocess.run(shipping.command(work,f'http://127.0.0.1:{http.server_port}/v1'),
                              cwd=work/'empty',env=env,input=data,capture_output=True,timeout=45)
        http.shutdown()
    if len(captured)!=1:
        raise ValueError(proc.stderr.decode()[-2000:])
    req, = captured
    summary = [(i.get('type'),i.get('role')) for i in req['input']]
    assert not req.get('tools') and summary==[('message','developer'),('message','user')], summary
    assert req['model']==shipping.MODEL and req['reasoning']['effort']=='medium'
    assert req.get('instructions') in (None,'',shipping.SYSTEM)
    assert [i['content'][0]['text'] for i in req['input']]==[shipping.SYSTEM,data.decode()]
    assert all(len(i['content'])==1 for i in req['input'])
    return sha(data)


def prepare():
    for d in ('empty','mock-home'):
        (W/d).mkdir(exist_ok=True)
    cache = json.loads((Path.home()/'.codex/models_cache.json').read_bytes())
    entry = next(m for m in cache['models'] if m['slug']==shipping.MODEL)
    (W/'catalog.json').write_text(json.dumps({'models':[{**entry,**shipping.PRIOR['catalogOverrides']}]}))
    (W/'system.txt').write_text(shipping.SYSTEM)
    zero = dict.fromkeys(KEYS,0)
    arms = {}
    for arm in 'ABC':
        initial = packet(arm,[],zero)
        capture = validate_packet(initial,W)
        arms[arm] = dict(initialPacketSha256=capture,
                         files={p:sha(b) for p,b in material_files(arm).items()})
    slots = []
    for block in (1,2):
        arms_in_block = list('ABC')
        secrets.SystemRandom().shuffle(arms_in_block)
        for arm in arms_in_block:
            slots.append(dict(block=block,arm=arm,id=secrets.token_hex(5)))
    save(PLAN,dict(slots=slots,base=BASE,limit=LIMIT,model=shipping.MODEL,effort='medium',
                   cli=subprocess.check_output(['codex','--version'],text=True).strip(),
                   settings=shipping.config(W,shipping.ENDPOINT)[:-2],catalogSha256=sha((W/'catalog.json').read_bytes()),
                   nativeTools=[],system=shipping.SYSTEM,arms=arms))


def now():
    return datetime.now(timezone.utc).isoformat()


def run():
    plan = json.loads(PLAN.read_bytes())
    t = Path((W/'template').read_text())
    assert sha((W/'catalog.json').read_bytes())==plan['catalogSha256'] and (W/'system.txt').read_text()==shipping.SYSTEM
    assert plan['settings']==shipping.config(W,shipping.ENDPOINT)[:-2] and git(t,'status','--porcelain')==b''
    original,reference = [json.loads((OUT/(s+'.json')).read_bytes()) for s in ('original','reference')]
    assert original['actions']==dict(ordinary=False,locked=True,**{'off-path':True}) and original['lasso']==['passed']*6
    assert original['probe']==['passed']*2 and original['run']['exit']==0 and reference['complete']
    save(OUT/'started.json',dict(at=now(),commit=git(ROOT,'rev-parse','HEAD').decode().strip()))
    total = dict.fromkeys(KEYS,0)
    active = 0
    for slot in plan['slots']:
        arm = slot['arm']
        folder = OUT/slot['id']
        area = workspace(t)
        files = material_files(arm)
        assert {p:sha(b) for p,b in files.items()}==plan['arms'][arm]['files']
        for p,data in files.items():
            path = area/'material'/p
            path.parent.mkdir(exist_ok=True,parents=True)
            path.write_bytes(data)
        usage = dict.fromkeys(KEYS,0)
        history = []
        start = time.monotonic()
        deadline = start+min(720,4320-active)
        stop = None
        hold = False
        n = 0
        submitted = False
        while not stop:
            data = packet(arm,history,usage)
            n += 1
            if n==1:
                assert sha(data)==plan['arms'][arm]['initialPacketSha256']
            remaining = deadline-time.monotonic()
            if remaining<=0:
                stop = 'time-limit'
                break
            request = dict(started=now(),packetSha256=sha(data))
            save(folder/f'{n:02}-start.json',request)
            result = shipping.invoke(W,data,remaining)
            record = dict(**result,received=now())
            u = result['usage']
            measured = isinstance(u,dict) and all(type(u.get(k)) is int and u[k]>=0 for k in KEYS)
            if measured:
                for k in KEYS:
                    usage[k]+=u[k]
                    total[k]+=u[k]
            if not measured or set(result['serverModels'])-{shipping.MODEL}:
                stop = 'missing-usage' if not measured else 'model-mismatch'
                hold = True
            elif time.monotonic()>=deadline or result['timeout']:
                stop = 'time-limit'
            elif result['exitCode']!=0:
                stop = 'provider-error'
            else:
                try:
                    action = json.loads(result['answer'] or '')
                except ValueError:
                    action = None
                if isinstance(action,dict) and action.get('op')=='submit':
                    submitted = True
                    stop = 'submitted'
                elif isinstance(action,dict) and action.get('op')=='shell' and isinstance(action.get('command'),str):
                    record['tool'] = shell(area,action['command'],max(0.001,deadline-time.monotonic()))
                    history.append({'action':action,'result':record['tool']})
                else:
                    history.append({'answer':result['answer'],'error':'Expected a JSON shell or submit action.'})
            elapsed = time.monotonic()-start
            if elapsed>=deadline-start and not stop:
                stop = 'time-limit'
            if not stop and any(usage[k]>=LIMIT[k] for k in ('input_tokens','output_tokens')):
                stop = 'token-limit'
            if any(total[k]>=LIMIT[k]*6 for k in ('input_tokens','output_tokens')):
                hold = True
                stop = stop or 'batch-token-limit'
            record['elapsedSeconds'] = round(elapsed,3)
            save(folder/f'{n:02}.json',record)
            print(slot['id'],n,stop or 'continue',usage,flush=True)
        elapsed = time.monotonic()-start
        seal = dict(stop=stop,holdRemaining=hold,participantSeconds=round(elapsed,3),usageKnown=not(stop=='missing-usage'),
                    observedUsage=usage, submitted=submitted)
        if submitted:
            source = area/'source'
            git(source,'add','-A')
            patch = git(source,'diff','--cached','--binary','--full-index','--no-ext-diff','HEAD')
            (folder/'first.patch').write_bytes(patch)
            seal['sha256'] = sha(patch)
        save(folder/'seal.json',seal)
        active += elapsed
        shutil.rmtree(area)
        if hold or active>=4320:
            break


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['prepare','run'])
    args=parser.parse_args()
    (prepare if args.action=='prepare' else run)()
