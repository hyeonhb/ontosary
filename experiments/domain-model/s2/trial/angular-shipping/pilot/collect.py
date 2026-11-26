"""Freeze, locally inspect and collect the authorized shipping pilot, once. No grading here."""
import argparse
import json
import os
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
S2 = HERE.parents[2]
sys.path[:0] = [str(S2 / 'trial/discovery'), str(S2 / 'trial/fixed-input')]
from session import Session, digest, encode, material_files, public
from model_evidence import server_models

BASE = '8dbb6e4063248c3084e5768d613347a3453eda41'
VERSION = '31759cf58c673405be9716288b00c9dd4b50138b'
OUT = S2 / 'results/2026-11-26-shipping-pilot'
FROZEN = S2 / 'results/2026-11-10-trial-preparation'
PRIOR = json.loads((S2 / 'results/2026-11-20-sol-comparison/preflight/quantity.json').read_bytes())
MODEL = PRIOR['model']
SYSTEM = 'Use only the public prompt and action history. Return one JSON action.'
LIMITS = dict(seconds=1800, requests=24, actions=24, replyBytes=4096, input_tokens=160000, output_tokens=8000)
ENDPOINT = 'https://chatgpt.com/backend-api/codex'
RUBRIC = [
    'Name how direct cancellation and refund with cancellation converge, with a correct pre-change code location or symbol.',
    'Explain the shipping adjustment and net/gross price basis through order totals, with correct pre-change code locations or symbols.',
]


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


def prompt(arm):
    result = public(arm)
    result.update(task=(HERE.parent / 'public/request.txt').read_text().rstrip('\n'),
                  revision=BASE, scope='Vendure repository source and documentation')
    result['protocol'][0] = result['protocol'][0].replace(' in this mock', ' per session')
    return result


def git(directory, *args):
    return subprocess.check_output(['git', '-C', directory, *args])


def baseline(directory):
    files = {}
    for entry in git(directory, 'ls-files', '--stage', '-z').split(b'\0')[:-1]:
        meta, name = entry.split(b'\t', 1)
        if meta.split()[0] in (b'100644', b'100755'):
            files[name.decode()] = (directory / name.decode()).read_bytes()
    return files


def packet(arm, history):
    return encode({'public': prompt(arm), 'history': history})


def config(work, url):
    return [*PRIOR['settings'], 'model_provider="shipping"',
            'model_providers.shipping.name="Codex shipping pilot"',
            'model_providers.shipping.wire_api="responses"',
            'model_providers.shipping.base_url=' + json.dumps(url),
            'model_providers.shipping.request_max_retries=0', 'model_providers.shipping.stream_max_retries=0',
            'model_providers.shipping.requires_openai_auth=' + ('true' if url == ENDPOINT else 'false'),
            'model_catalog_json=' + json.dumps(str(work / 'catalog.json')),
            'model_instructions_file=' + json.dumps(str(work / 'system.txt'))]


def command(work, url):
    return ['codex', 'exec', '--ignore-user-config', '--ignore-rules', '--ephemeral', '--json',
            '--skip-git-repo-check', '-C', str(work / 'empty'), '-s', 'read-only', '-m', MODEL,
            *[piece for setting in config(work, url) for piece in ('-c', setting)], '-']


def local_check(work, source):
    received = []
    class Capture(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            received.append(json.loads(self.rfile.read(int(self.headers['Content-Length']))))
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"error":{"message":"loopback capture"}}')

    proof = {}
    with HTTPServer(('127.0.0.1', 0), Capture) as server:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        env = dict(PATH=os.environ['PATH'], HOME=str(work / 'mock-home'), CODEX_HOME=str(work / 'mock-home'), LANG='C')
        for arm in 'ABC':
            session = Session(arm, source, material_files(arm, FROZEN))
            example = prompt(arm)['example']
            reply = session.step(example)
            assert reply['rows']
            proof[arm] = []
            for history in ([], [dict(action=example, reply=reply)]):
                data = packet(arm, history)
                received.clear()
                proc = subprocess.run(command(work, f'http://127.0.0.1:{server.server_port}/v1'),
                                      cwd=work/'empty', env=env, input=data, capture_output=True, timeout=45)
                assert len(received) == 1, proc.stderr[-1200:]
                req, = received
                assert req['model'] == MODEL and req['reasoning']['effort'] == 'medium'
                assert not any(part.get('tools') for part in [req, *req['input']])
                assert req.get('instructions') in (None, '', SYSTEM)
                assert [(i['type'], i['role'], [c['text'] for c in i['content']]) for i in req['input']] == [
                    ('message', 'developer', [SYSTEM]), ('message', 'user', [data.decode()])]
                proof[arm].append(digest(data))
        server.shutdown()
    return proof


def fingerprint(files):
    return digest(encode([(path, digest(data)) for path, data in sorted(files.items())]))


def prepare(repository, work):
    work.mkdir(parents=True, exist_ok=False)
    OUT.mkdir(exist_ok=False)
    for name in ('empty', 'mock-home'):
        (work / name).mkdir()
    original = json.loads((Path.home() / '.codex/models_cache.json').read_bytes())
    entry = next(m for m in original['models'] if m['slug'] == MODEL)
    save(work/'catalog.json', {'models': [{**entry, **PRIOR['catalogOverrides']}]})
    (work/'system.txt').write_text(SYSTEM)
    arms = {}
    for arm in 'ABC':
        copy = work / arm
        subprocess.run(['git', 'clone', '--quiet', '--shared', '--no-checkout', str(repository), copy], check=True)
        git(copy, '-c', 'advice.detachedHead=false', 'checkout', '-q', '--detach', BASE)
        source = baseline(copy)
        spaces = material_files(arm, FROZEN)
        assert sum(map(len, spaces.values())) == {'A': 0, 'B': 68, 'C': 4}[arm]
        arms[arm] = dict(public=prompt(arm), source=fingerprint(source), files=len(source),
                         materials={p: digest(raw) for files in spaces.values() for p, raw in files.items()})
    proof = local_check(work, source)
    save(OUT/'freeze.json', dict(base=BASE, evaluatorRevision=VERSION, order=list('ABC'), model=MODEL,
         effort='medium', system=SYSTEM, limits=LIMITS, rubric=RUBRIC, arms=arms, loopbackPacketHashes=proof,
         loopbackRoles=['developer', 'user'], loopbackTools=[], cli=subprocess.check_output(['codex','--version'],text=True).strip(),
         settings=config(work, ENDPOINT)[:-2], catalogSha256=digest((work/'catalog.json').read_bytes()),
         hostSha256=digest(Path(__file__).read_bytes()), created=datetime.now(timezone.utc).isoformat()))


def invoke(work, data, remaining):
    env = {k: os.environ[k] for k in ('PATH','HOME','LANG','USER','TMPDIR') if k in os.environ}
    env['RUST_LOG'] = 'codex_core::session=trace,codex_api::sse::responses=trace'
    proc = subprocess.Popen(command(work, ENDPOINT), cwd=work/'empty', env=env, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    expired = False
    try:
        stdout, stderr = proc.communicate(data, timeout=remaining)
    except subprocess.TimeoutExpired:
        expired = True
        os.killpg(proc.pid, signal.SIGKILL)
        stdout, stderr = proc.communicate()
    events = [json.loads(line) for line in stdout.splitlines() if line.startswith(b'{')]
    answers = [event['item']['text'] for event in events if event.get('type') == 'item.completed'
               and event['item']['type'] == 'agent_message']
    usages = [event.get('usage') for event in events if event.get('type') == 'turn.completed']
    errors = [event.get('message') or event.get('error') for event in events
              if event.get('type') in ('turn.failed', 'error')]
    return dict(exitCode=proc.returncode, timeout=expired, usage=usages[0] if len(usages)==1 else None,
                errors=errors, serverModels=server_models(stderr.decode(errors='replace').splitlines()),
                answer=answers[-1] if answers else None)


def collect_patch(copy, before, after):
    for name, raw in after.items():
        if before.get(name) != raw:
            target = copy / name
            if any(p.is_symlink() for p in [target, *target.parents] if p.is_relative_to(copy)):
                raise ValueError('working copy symlink collision')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            git(copy, '--literal-pathspecs', 'add', '-f', '--', name)
    return git(copy, 'diff', '--cached', '--full-index', '--binary', '--no-renames', '--no-ext-diff')


def run(work):
    freeze = json.loads((OUT/'freeze.json').read_bytes())
    assert digest(Path(__file__).read_bytes()) == freeze['hostSha256']
    assert digest((work/'catalog.json').read_bytes()) == freeze['catalogSha256'] and (work/'system.txt').read_text() == SYSTEM
    assert freeze['settings'] == config(work, ENDPOINT)[:-2]
    # A started allocation cannot silently launch another session, even after a host crash.
    save(OUT/'allocation.json', dict(order=list('ABC'), started=datetime.now(timezone.utc).isoformat()))
    for arm in 'ABC':
        directory = OUT/arm
        directory.mkdir()
        source = baseline(work/arm)
        materials = material_files(arm,FROZEN)
        assert fingerprint(source) == freeze['arms'][arm]['source'] and prompt(arm) == freeze['arms'][arm]['public']
        assert {p:digest(raw) for files in materials.values() for p,raw in files.items()} == freeze['arms'][arm]['materials']
        session = Session(arm, source, materials)
        history = []
        totals = dict(input_tokens=0, output_tokens=0)
        start = time.monotonic()
        reason = 'request-limit'
        hold = False
        for index in range(1,LIMITS['requests']+1):
            data = packet(arm, history)
            if index == 1:
                assert digest(data) == freeze['loopbackPacketHashes'][arm][0]
            remaining = LIMITS['seconds'] - (time.monotonic()-start)
            if remaining <= 0:
                reason = 'time-limit'
                break
            marker = dict(request=index, packetSha256=digest(data), started=datetime.now(timezone.utc).isoformat())
            save(work/f'{arm}-{index}-start.json', marker)
            result = invoke(work, data, remaining)
            row = {**marker, **result}
            usage = row['usage']
            if not usage or any(type(usage.get(k)) is not int or usage[k]<0 for k in totals):
                reason, hold = 'missing-usage', True
            elif set(row['serverModels']) - {MODEL}:
                reason, hold = 'model-mismatch', True
            else:
                for key in totals:
                    totals[key] += usage[key]
            if not hold and not result['timeout'] and time.monotonic()-start < LIMITS['seconds']:
                try:
                    action = json.loads(result['answer'] or '')
                except ValueError:
                    action = None
                reply = session.step(action)
                history.append(dict(action=action, reply=reply))
                row.update(action=action, replySha256=digest(encode(reply)), replyBytes=len(encode(reply)),
                           replyRows=len(reply.get('rows',[])), actionError='error' in reply,
                           hostNanoseconds=session.elapsed_ns[-1])
                if 'sealed' in reply:
                    row['impactSeal'] = reply['sealed']
            row['elapsedSeconds'] = round(time.monotonic()-start,3)
            save(directory/f'{index:02}.json', row)
            print(arm, index, reason if hold else (row.get('action') or {}).get('op') if isinstance(row.get('action'), dict) else 'invalid', totals, flush=True)
            if hold:
                break
            if session.finished:
                reason = 'finished'
                break
            if result['timeout'] or row['elapsedSeconds'] >= LIMITS['seconds']:
                reason = 'time-limit'
                break
            if any(totals[k] >= LIMITS[k] for k in totals):
                reason = 'token-limit'
                break
        seal = dict(reason=reason, holdRemaining=hold, impact=session.impact, elapsedSeconds=row['elapsedSeconds'])
        if session.finished:
            patch = collect_patch(work/arm, source, session.spaces['source'])
            (directory/'first.patch').write_bytes(patch)
            seal['patchSha256'] = digest(patch)
        save(directory/'seal.json', seal)
        if hold:
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['prepare','run'])
    parser.add_argument('repository',type=Path)
    parser.add_argument('work',type=Path)
    args = parser.parse_args()
    if args.mode == 'prepare':
        prepare(args.repository.resolve(), args.work.resolve())
    else:
        run(args.work.resolve())
