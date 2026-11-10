#!/usr/bin/env python3
"""Export only reviewed evidence; never starts a runtime or model."""
import argparse, hashlib, json, pathlib, re
p = argparse.ArgumentParser()
p.add_argument('work', type=pathlib.Path)
p.add_argument('output', type=pathlib.Path)
a = p.parse_args()
repo = pathlib.Path(__file__).resolve().parents[5]
files = '''budget.json cleanup.json codex-linux-npm.json codex-npm.json input-archives.json
lima-info.json lima-release.json node-image-native.json node-image.json pre-cleanup-host.json
pre-cleanup-vm.json stopped-vm.json worker-image.json accounting-regression.json
01-lima-download.log 02-vm-start.log 03-node-pull.log 04-image-build.log
05-vendure-install-build.log 06-vendure-install-build-retry.log
accounting-regression.log cleanup-delete.log cleanup-stop.log deleted-vm-list.jsonl
cli-preflight.log guest-preflight.log host-check.log host-experiment.log host-s2-build.log
nerdctl-info.log pre-cleanup-guest.log supplementary-commands.json verification.json'''.split()
raw = a.output / 'raw'
raw.mkdir(parents=True, exist_ok=True)
replacements = [('/private/tmp/ontosary-s2-container-20261110', '<task-root>'),
    ('/tmp/ontosary-s2-container-20261110', '<task-root>'),
    (str(repo), '<repo>'), (str(pathlib.Path.home()) + '/Library/Caches', '<host-cache>'),
    ('/home/hyeon.guest', '<guest-home>'), (str(pathlib.Path.home()), '<host-home>'),
    ('황보현', '<host-display-name>'), ('hyeon', '<host-user>')]
exports = {}
for name in files:
    source = (a.work / name).read_bytes()
    text = source.decode()
    for old, new in replacements:
        text = text.replace(old, new)
    text = re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', text)
    text = '\n'.join(line.rstrip() for line in text.splitlines()).rstrip() + '\n' if text else ''
    (raw / name).write_text(text)
    exports[name] = {'originalSha256': hashlib.sha256(source).hexdigest(),
                     'exportSha256': hashlib.sha256(text.encode()).hexdigest()}
implementation = {}
for directory in [pathlib.Path(__file__).parent, a.output / 'implementation-at-execution']:
    for f in sorted(directory.rglob('*')):
        if f.is_file() and '__pycache__' not in f.parts:
            implementation[str(f.resolve().relative_to(repo))] = hashlib.sha256(f.read_bytes()).hexdigest()
# Existing implementation is identified without changing historical freeze manifests.
existing = {}
for f in sorted((repo / 'experiments/domain-model/s2').rglob('*.ts')):
    if '/verification/' not in str(f) and '/results/' not in str(f):
        existing[str(f.relative_to(repo))] = hashlib.sha256(f.read_bytes()).hexdigest()
evidence = {str(f.relative_to(a.output)): hashlib.sha256(f.read_bytes()).hexdigest()
    for f in sorted(a.output.rglob('*')) if f.is_file() and f.name != 'manifest.json'}
image = json.loads((a.work / 'worker-image.json').read_text())[0]
manifest = {'version': 's2-container-feasibility-evidence-v1', 'status': 'inconclusive',
    'baseCommit': '2f2acb22279c8cc34d0947e4eca40d4fd213307e',
    'implementation': implementation, 'existingImplementation': existing, 'evidence': evidence,
    'normalization': 'Host paths/identities, ANSI escapes, line endings and trailing whitespace only; messages, digests, diagnostics and counts retained. Empty CLI stdout is accompanied by tool-captured stderr in supplementary-commands.json.',
    'exports': exports, 'imageManifestDigest': image['RepoDigests'][0].split('@')[1],
    'imageConfigDigest': image['Id'], 'trialAuthorized': False, 'readyForTrial': False,
    'results': None, 'providerCalls': 0, 'trialRuns': 0}
manifest['implementationId'] = hashlib.sha256(json.dumps(implementation,sort_keys=True,separators=(',',':')).encode()).hexdigest()
(a.output / 'manifest.json').write_text(json.dumps(manifest,indent=2) + '\n')
print(json.dumps({'implementationFiles':len(implementation),'evidenceFiles':len(evidence),'implementationId':manifest['implementationId']}))
