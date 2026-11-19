"""Apply one sealed first answer to a fresh complete copy. Never edit model hunks."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

answer, baseline, environment, out = (Path(arg).resolve() for arg in sys.argv[1:5])
out.mkdir(exist_ok=False)
raw = answer.read_bytes()
result = {'responseSha256': hashlib.sha256(raw).hexdigest(), 'applied': False}


def patch_bytes():
    if len(raw) > 49152:
        raise ValueError('Output exceeds 49152 bytes')
    text = raw.decode('utf-8').strip('\n')
    if text.startswith(('```diff\n', '```patch\n')) and text.endswith('\n```'):
        text = text.split('\n', 1)[1][:-4]
    if not text.startswith(('diff --git ', '--- a/', '--- /dev/null')):
        raise ValueError('Expected one unified diff')
    # Inspect actual file headers outside hunks (hunk lines carry a prefix).
    for line in text.splitlines():
        if re.match(r'^(old mode|new mode|new file mode|deleted file mode) ', line):
            if line.split()[-1] not in ('100644', '100755'):
                raise ValueError('Nonregular git mode')
        if line.startswith(('GIT binary patch', 'Binary files ', 'rename ', 'copy ')):
            raise ValueError('Expected textual additions, removals or changes')
    return (text + '\n').encode()


try:
    patch = patch_bytes()
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / 'source'
        shutil.copytree(baseline, source, symlinks=True)
        if any(p.is_symlink() or not (p.is_dir() or p.is_file()) for p in source.rglob('*')):
            raise RuntimeError('Baseline contains nonregular files')
        git_env = {'PATH': os.environ['PATH'], 'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': '/dev/null',
                   'GIT_CEILING_DIRECTORIES': directory, 'LC_ALL': 'C'}
        args = ['git', 'apply', '--whitespace=nowarn']
        def apply(extra):
            proc = subprocess.run(args + extra, input=patch, capture_output=True, cwd=source, env=git_env)
            if proc.returncode:
                raise ValueError(proc.stderr.decode('utf-8', errors='replace').strip())
            return proc.stdout
        try:
            apply(['--check'])
        except ValueError:
            args.append('--recount')
            apply(['--check'])
        entries = apply(['--numstat', '-z']).split(b'\0')
        if not entries[0]:
            raise ValueError('Empty patch')
        for entry in filter(None, entries):
            added, deleted, name = entry.decode().split('\t', 2)
            if not added.isdecimal() or not deleted.isdecimal() or any(
                s in ('', '.', '..', '.git', 'node_modules') for s in name.lower().split('/')
            ):
                raise ValueError('Unsupported binary or path')
        apply([])
        if any(p.is_symlink() or not (p.is_dir() or p.is_file()) for p in source.rglob('*')):
            raise ValueError('Submission contains nonregular files')
        result['applied'] = True
        target = out / 'evaluation.json'
        run = subprocess.run([sys.executable, str(Path(__file__).with_name('evaluate.py')), str(source),
                              str(environment), str(target), *sys.argv[5:]], capture_output=True)
        if target.exists():
            report = json.loads(target.read_bytes())
            if report.get('contractVersion') and report.get('typecheck', {}).get('submissionId'):
                result['status'] = report['overall']
            else:
                result.update(status='environment-error', error=report.get('error'))
        else:
            result.update(status='environment-error', error=run.stderr.decode(errors='replace')[-2000:])
except (ValueError, UnicodeError) as exc:
    result.update(status='patch-rejected', error=str(exc))
(out / 'grade.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
