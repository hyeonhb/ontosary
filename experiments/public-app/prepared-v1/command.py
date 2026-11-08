"""Run one command within the persisted preparation deadline; never reset on resume."""
import datetime, json, os, pathlib, signal, subprocess, sys, time
here = pathlib.Path(__file__).resolve().parent
repo = here.parents[2]
manifest = json.loads((here / 'manifest.json').read_text())
label, cwd, *command = sys.argv[1:]
output = repo / 'experiments/public-app/results/2026-11-08-prepared'
output.mkdir(parents=True, exist_ok=True)
if (output / 'budget-result.json').exists(): raise SystemExit('Preparation already closed; do not resume or reset this run')
record = output / (label + '.json')
if record.exists(): raise SystemExit('Existing command evidence; choose another label')
start = datetime.datetime.now(datetime.timezone.utc)
deadline = datetime.datetime.fromisoformat(manifest['budget']['deadlineUtc'])
remaining = (deadline - start).total_seconds()
if remaining <= 0: raise SystemExit('Preparation deadline expired; no new preparation command allowed')
env = os.environ.copy()
for name in ['empty-user.npmrc', 'empty-global.npmrc']:
    pathlib.Path(manifest['cache'], name).touch(exist_ok=True)
env.update(NPM_CONFIG_USERCONFIG=manifest['cache'] + '/empty-user.npmrc', NPM_CONFIG_GLOBALCONFIG=manifest['cache'] + '/empty-global.npmrc', NPM_CONFIG_CACHE=manifest['cache'] + '/npm-cache', NPM_CONFIG_REGISTRY='https://registry.npmjs.org/')
log = output / (label + '.log')
raw = repo / 'work/vendure-preparation' / (label + '.raw.log')
raw.parent.mkdir(parents=True, exist_ok=True)
with raw.open('wb') as handle:
    child = subprocess.Popen(command, cwd=cwd, env=env, stdout=handle, stderr=subprocess.STDOUT, start_new_session=True)
    timed_out = False
    try: code = child.wait(timeout=remaining)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(child.pid, signal.SIGKILL)
        code = child.wait()
end = datetime.datetime.now(datetime.timezone.utc)
text = raw.read_text(errors='replace').replace(str(repo), '<workspace>').replace(str(pathlib.Path.home()), '<home>').replace(manifest['cache'], '<cache>')
log.write_text(text)
record.write_text(json.dumps(dict(command=[a.replace(str(repo), '<workspace>') for a in command], cwd=cwd.replace(manifest['cache'], '<cache>').replace(str(repo), '<workspace>'), startUtc=start.isoformat(), endUtc=end.isoformat(), wallTimeMs=round((end-start).total_seconds()*1000), remainingAtStartMs=round(remaining*1000), exitCode=code if code>=0 else None, signal=-code if code<0 else None, timedOut=timed_out, deadlineUtc=deadline.isoformat(), environmentPolicy='Public registry; empty user/global npm config; isolated npm cache; inherited process environment not dumped.'), indent=2)+'\n')
print(json.dumps(dict(label=label,exitCode=code,timedOut=timed_out,wallTimeMs=round((end-start).total_seconds()*1000))))
sys.exit(1 if code else 0)
