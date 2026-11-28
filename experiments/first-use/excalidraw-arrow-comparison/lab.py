"""Local macOS workspaces for the arrow comparison. No provider access."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = 'e32836f799b65f978cbf4877eab7ffc42c6e6494'
REFERENCE = 'a89a03c66ccbd3d44078be78a82d7adfb8f05953'
PROBE = HERE.parent / 'excalidraw-followup/reviewer/arrow-probe.tsx'
NOTES = HERE.parent / 'excalidraw-eraser'
W = ROOT / 'work/arrow-comparison'
OUT = HERE / 'observations'
LASSO = 'packages/excalidraw/tests/lasso.test.tsx'
ARROW = 'packages/excalidraw/tests/fast-arrow.test.tsx'
NODE = Path(subprocess.check_output(['node', '-p', 'process.execPath'], text=True).strip())
XCODE = Path(subprocess.check_output(['xcrun', '-f', 'python3'], text=True).strip()).parents[2]
RG = Path(shutil.which('rg')).resolve()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


def git(src, *args, data=None):
    return subprocess.check_output(['git', '-C', src, '-c', 'core.hooksPath=/dev/null', *args], input=data)


def workspace(template):
    area = Path(tempfile.mkdtemp(prefix='drawing-', dir='/private/tmp'))
    subprocess.run(['cp', '-cR', template, area / 'source'], check=True)
    (area / 'tmp').mkdir()
    return area


def shell(area, command, timeout, output_limit=20000):
    source = area / 'source'
    tmp = area / 'tmp'
    reads = ['/usr/bin', '/bin', '/usr/libexec', str(NODE.parent.parent), str(RG), str(XCODE),
             str(RG.parent), str(area), '/private/etc/hosts', '/dev/null', '/dev/random', '/dev/urandom',
             '/opt/homebrew/Cellar/pcre2', '/opt/homebrew/opt/pcre2']
    paths = ' '.join('(subpath ' + json.dumps(p) + ')' for p in reads)
    profile = f'''(version 1)
(deny default)
(import "system.sb")
(allow sysctl-read process-exec process-fork file-read-metadata)
(allow signal (target same-sandbox))
(allow file-read* file-map-executable {paths})
(allow file-write* (subpath "{source}") (subpath "{tmp}") (literal "/dev/null"))
(deny file-write* (subpath "{source}/.git"))
(allow mach-lookup (global-name "com.apple.system.opendirectoryd.libinfo"))
(deny network*)
'''
    env = dict(HOME=str(tmp), TMPDIR=str(tmp)+'/', PATH=':'.join(map(str,[
        NODE.parent, RG.parent, XCODE/'usr/bin','/usr/bin','/bin'])), LANG='en_US.UTF-8',
        CI='1', GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null', GIT_OPTIONAL_LOCKS='0')
    start = time.monotonic()
    with tempfile.TemporaryFile() as log:
        p = subprocess.Popen(['/usr/bin/sandbox-exec','-p',profile,'/bin/bash','-c',command],
                             cwd=source, env=env, stdout=log, stderr=subprocess.STDOUT,
                             stdin=subprocess.DEVNULL, start_new_session=True)
        try:
            p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            pass
        finally:
            expired = p.poll() is None
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            p.wait()
        size = log.tell()
        log.seek(0)
        raw = log.read(output_limit)
        if size > output_limit:
            log.seek(-output_limit//2, 2)
            raw = raw[:output_limit//2] + b'\n[... output clipped ...]\n' + log.read()
    return dict(exit=p.returncode, timeout=expired, bytes=size, output=raw.decode(errors='replace'),
                seconds=round(time.monotonic()-start,3))
