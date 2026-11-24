"""Run the existing complete-root evaluator with read-only inputs and a single writable output."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

repo = Path(__file__).resolve().parents[5]
source, environment, output = (Path(arg).resolve() for arg in sys.argv[1:4])
task = sys.argv[4:]
entry = "evaluation/run.js"
if task == ["refund-discovery"]:
    entry = "trial/discovery/menu.js"
elif task:
    if task not in (["allocation"], ["quantity"], ["refresh"]):
        raise SystemExit("Unknown evaluation task")
    entry = "trial/complex/evaluator/run.js"
if output.exists() or not output.parent.is_dir():
    raise SystemExit('Expected an existing output directory and a fresh result path')
node = Path(subprocess.check_output([shutil.which('node'), '-p', 'process.execPath'], text=True).strip())
readable = [source, environment, repo / 'experiments', repo / 'work/s2-build',
            repo / 'node_modules', repo / 'package.json', node.parent.parent, Path('/System'), Path('/usr/lib'),
            Path('/usr/share'), Path('/private/var/db/timezone')]
rules = ' '.join('(subpath ' + json.dumps(str(p)) + ')' for p in readable)
profile = f"""(version 1)
(deny default)
(import "system.sb")
(deny network* process-fork file-write*)
(allow process-exec (literal {json.dumps(str(node))}))
(allow file-read-metadata sysctl-read)
(allow file-read* (literal {json.dumps(str(repo))}))
(allow file-read* {rules} (literal "/dev/null") (literal "/dev/urandom") (literal "/dev/random"))
(allow file-write* (literal {json.dumps(str(output))}))
"""
subprocess.run(['/usr/bin/sandbox-exec', '-p', profile, str(node),
                str(repo / 'work/s2-build' / entry), str(source),
                str(environment), str(output), str(repo), *task], cwd=repo, env={"LANG": "C", "PATH": "/usr/bin:/bin"}, check=True, timeout=180)
