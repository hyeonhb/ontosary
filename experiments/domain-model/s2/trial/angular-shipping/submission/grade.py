"""Apply one submitted diff to a fresh checkout and observe the resulting six cases."""
import argparse
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
PARENT = '8dbb6e4063248c3084e5768d613347a3453eda41'
MODIFIER = 'packages/core/src/service/helpers/order-modifier/order-modifier.ts'
CASES = json.loads((HERE.parent / 'cases.json').read_bytes())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run_node(source, manifest):
    node = Path(subprocess.check_output(['node', '-p', 'process.execPath'], text=True).strip())
    paths = [source, manifest, HERE.parent, ROOT / 'node_modules', ROOT / 'package.json',
             node.parent.parent, Path('/System'), Path('/usr/lib'), Path('/usr/share'),
             Path('/private/var/db/timezone')]
    reads = ' '.join('(subpath ' + json.dumps(str(path)) + ')' for path in paths)
    profile = f'''(version 1)
(deny default)
(import "system.sb")
(deny network* process-fork file-write*)
(allow process-exec (literal {json.dumps(str(node))}))
(allow file-read-metadata sysctl-read)
(allow file-read* {reads} (literal "/dev/null") (literal "/dev/urandom") (literal "/dev/random"))
'''
    result = subprocess.run(['/usr/bin/sandbox-exec', '-p', profile, str(node), str(HERE / 'run.mjs'),
                             str(source), str(manifest)], cwd=ROOT, capture_output=True, text=True,
                            timeout=30, env={'LANG': 'C', 'PATH': '/usr/bin:/bin'})
    if result.returncode:
        raise RuntimeError(result.stderr.strip()[-1500:] or f'worker exit {result.returncode}')
    return json.loads(result.stdout)


def grade(repository, patch, out):
    out.mkdir(parents=True, exist_ok=False)
    source = out / 'source'
    data = patch.read_bytes()
    record = {'parent': PARENT, 'patchSha256': sha(data), 'patchBytes': len(data)}
    subprocess.run(['git', 'clone', '--quiet', '--shared', '--no-checkout', '--no-tags',
                    str(repository), str(source)], check=True)

    def git(*args):
        return subprocess.check_output(['git', '-C', source, *args])

    git('-c', 'advice.detachedHead=false', 'checkout', '--quiet', '--detach', PARENT)
    if data:
        applied = subprocess.run(['git', '-C', source, 'apply', '--index', '--whitespace=nowarn', '-'],
                                 input=data, capture_output=True)
        if applied.returncode:
            return {**record, 'stage':'patch-rejected', 'reason':applied.stderr.decode(errors='replace').strip(),
                    'passed':0, 'failed':0, 'ungradable':0, 'attempted':0, 'measured':0}
    tree = git('write-tree').decode().strip()
    changes = []
    entries = git('diff', '--cached', '--no-renames', '--name-status', '-z').decode().split('\0')[:-1]
    for status, path in zip(entries[::2], entries[1::2], strict=True):
        item = {'status':status, 'path':path}
        if status != 'D':
            meta = git('ls-files', '--stage', '--', path).split(b'\t')[0].decode().split()
            item.update(mode=meta[0], blob=meta[1])
            if meta[0] in ('100644', '100755'):
                item['sha256'] = sha((source / path).read_bytes())
        else:
            item['mode'] = None
        changes.append(item)
    git('diff', '--exit-code', '--quiet')
    manifest = out / 'manifest.json'
    base = git('show', PARENT + ':' + MODIFIER).decode()
    lines = []
    deletions = []
    if any(c['path'] == MODIFIER and c['mode'] == '100644' for c in changes):
        actual = (source / MODIFIER).read_text(errors='replace')
        parent_lines = base.splitlines()
        diff = SequenceMatcher(None, parent_lines, actual.splitlines(), autojunk=False)
        for tag, old_start, old_end, start, end in diff.get_opcodes():
            if tag == 'delete' and any(line.strip() for line in parent_lines[old_start:old_end]):
                deletions.append([old_start + 1, old_end])
            if tag != 'equal':
                lines.extend(range(start + 1, end + 1))
    manifest.write_text(json.dumps({'changes':changes, 'baseModifier':base, 'changedLines':lines, 'deletedOnly':deletions}))
    try:
        result = run_node(source, manifest)
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
        result = {'sources':{}, 'rows':[{**case, 'status':'ungradable', 'stage':'worker', 'reason':str(exc)} for case in CASES]}
    statuses = [row['status'] for row in result['rows']]
    return {**record, 'tree':tree, 'changes':changes, 'stage':'observation', **result,
            'passed':statuses.count('pass'), 'failed':statuses.count('fail'),
            'ungradable':statuses.count('ungradable'), 'attempted':sum('calls' in row for row in result['rows']),
            'measured':sum('after' in row for row in result['rows'])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('repository', 'patch', 'output'):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    result = grade(args.repository.resolve(), args.patch, out)
    (out / 'grade.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(result['stage'], 'pass', result['passed'], 'fail', result['failed'], 'ungradable', result['ungradable'])


if __name__ == '__main__':
    main()
