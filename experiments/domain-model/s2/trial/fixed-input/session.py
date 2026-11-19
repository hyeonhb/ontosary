"""Inspect the tool surface or collect exactly one first answer per frozen Codex session."""
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import threading
import time

mode, scratch_arg, evidence_arg = sys.argv[1:]
scratch = Path(scratch_arg).resolve()
evidence = Path(evidence_arg).resolve()
model = 'gpt-6.2-astra'
system = 'Use only the supplied text and return a single unified diff.'
env = {k: v for k, v in os.environ.items() if k in ('PATH', 'HOME', 'TMPDIR', 'LANG', 'USER')}
catalog = scratch / 'catalog.json'
instructions = scratch / 'system.txt'
frozen = json.loads((evidence / 'inputs.json').read_text())
settings = [
    'tools.update_plan.enabled=false', 'web_search="disabled"', 'project_doc_max_bytes=0',
    'include_environment_context=false', 'include_permissions_instructions=false',
    'include_collaboration_mode_instructions=false', 'skills.include_instructions=false',
    'model_reasoning_effort="medium"', 'model_context_window=512000',
    'tools.experimental_request_user_input.enabled=false',
    'features.multi_agent_v2={enabled=false,disable_native_tools=true}',
]
for feature in ('apps', 'plugins', 'multi_agent', 'memories', 'shell_tool', 'unified_exec',
                'image_generation', 'view_image', 'code_mode', 'code_mode_only', 'js_repl',
                'exec_permission_approvals', 'remote_models', 'incremental_tools',
                'enable_request_compression', 'skill_search', 'recommended_plugins',
                'shell_snapshot', 'goals', 'default_mode_request_user_input'):
    settings.append('features.' + feature + '=false')
overrides = dict(multi_agent_version=None, tool_mode='direct', shell_type='disabled',
                 apply_patch_tool_type=None, experimental_supported_tools=[], node_repl_disabled=True,
                 supports_search_tool=False)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write(path, value):
    with path.open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')


def flags(config):
    return [v for c in config for v in ('-c', c)]


def cli(directory, config):
    return ['codex', 'exec', '--ignore-user-config', '--ignore-rules', '--ephemeral', '--json',
            '--skip-git-repo-check', '-C', directory, '-s', 'read-only', '-m', model, *flags(config)]


def surface(request):
    return [t.get('name', t.get('type')) for section in [request, *request.get('input', [])]
            for t in section.get('tools', [])]


def packet(arm):
    data = (scratch / 'inputs' / (arm + '.txt')).read_bytes()
    if sha(data) != frozen['conditions'][arm]['sha256']:
        raise ValueError('Packet differs from freeze')
    return data


if mode == 'inspect':
    original = json.loads((Path.home() / '.codex/models_cache.json').read_bytes())
    entry = next(m for m in original['models'] if m['slug'] == model)
    entry.update(overrides)
    catalog.write_text(json.dumps({'models': [entry]}))
    instructions.write_text(system)
config = settings + ['model_catalog_json=' + json.dumps(str(catalog)),
                     'model_instructions_file=' + json.dumps(str(instructions))]
if mode == 'inspect':
    if entry['max_context_window'] < 512000:
        raise ValueError('Requested context exceeds model catalog')
    with tempfile.TemporaryDirectory() as directory:
        marker = 'Local preflight marker.'
        def preview(opts):
            r = subprocess.run(['codex', 'debug', 'prompt-input', '-c', 'model=' + json.dumps(model),
                                *flags(opts), marker], cwd=directory, env=env, capture_output=True, check=True)
            items = json.loads(r.stdout)
            return {'tools': surface({'input': items}), 'itemTypes': [i['type'] for i in items],
                    'roles': [i['role'] for i in items]}
        standard, native = preview([]), preview(config)
        assert standard['tools'] and not native['tools']
        observed = {}
        class Receiver(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass
            def do_POST(self):
                req = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                observed['items'] = req['input']
                observed['tools'] = surface(req)
                observed['model'] = req['model']
                observed['reasoning'] = req['reasoning']['effort']
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error":{"message":"Local capture only"}}')
        with HTTPServer(('127.0.0.1', 0), Receiver) as server:
            threading.Thread(target=server.serve_forever, daemon=True).start()
            local = config + ['model_provider="pilotlocal"', 'model_providers.pilotlocal.name="Local preflight"',
                              f'model_providers.pilotlocal.base_url="http://127.0.0.1:{server.server_port}/v1"',
                              'model_providers.pilotlocal.wire_api="responses"']
            captured = {}
            for arm in 'ABC':
                observed.clear()
                data = packet(arm)
                subprocess.run(cli(directory, local) + ['-'], input=data, env=env, cwd=directory,
                               capture_output=True, timeout=45)
                assert observed['tools'] == [] and observed['model'] == model and observed['reasoning'] == 'medium'
                items = observed['items']
                assert [(i['role'], i['type']) for i in items] == [('developer', 'message'), ('user', 'message')]
                assert [i['content'][0]['text'] for i in items] == [system, data.decode()]
                assert all(len(i['content']) == 1 for i in items)
                captured[arm] = sha(data)
            server.shutdown()
        write(evidence / 'preflight.json', {'codex': subprocess.check_output(['codex', '--version'], text=True).strip(),
              'model': model, 'catalogSha256': sha(catalog.read_bytes()), 'catalogOverrides': overrides,
              'settings': settings, 'system': system, 'defaultPreview': standard, 'configuredPreview': native,
              'localRequest': {'tools': [], 'roles': ['developer', 'user'], 'packetHashes': captured},
              'configuredContext': 512000, 'catalogMaximum': entry['max_context_window'],
              'effectivePercent': entry['effective_context_window_percent']})
elif mode == 'run':
    check = json.loads((evidence / 'preflight.json').read_text())
    assert check['catalogSha256'] == sha(catalog.read_bytes()) and instructions.read_text() == check['system']
    assert settings == check['settings'] and not check['configuredPreview']['tools']
    plan = json.loads((evidence / 'plan.json').read_text())
    for item in plan['order']:
        arm, run = item['condition'], item['id']
        data = packet(arm)
        destination = evidence / run
        destination.mkdir()  # An existing attempt is never overwritten or repeated.
        with tempfile.TemporaryDirectory() as directory:
            start = time.monotonic()
            with (destination / 'events.jsonl').open('xb') as stdout, (scratch / (run + '.stderr')).open('xb') as stderr:
                proc = subprocess.Popen(cli(directory, config) + ['-o', str(destination / 'answer.txt'), '-'],
                                        env=env, cwd=directory, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr,
                                        start_new_session=True)
                expired = False
                try:
                    proc.communicate(data, timeout=plan['seconds'])
                except subprocess.TimeoutExpired:
                    expired = True
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
            answer = destination / 'answer.txt'
            write(destination / 'seal.json', {'id': run, 'packetSha256': sha(data), 'exitCode': proc.returncode,
                  'timeout': expired, 'elapsedSeconds': round(time.monotonic()-start, 3),
                  'answerSha256': sha(answer.read_bytes()) if answer.exists() else None,
                  'eventsSha256': sha((destination / 'events.jsonl').read_bytes())})
else:
    raise SystemExit('Expected inspect or run')
