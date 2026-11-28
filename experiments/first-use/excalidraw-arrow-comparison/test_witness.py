"""Run only the test-file hunks of a sealed patch on the unchanged application."""
import argparse
from pathlib import Path
import shlex
import shutil
from lab import git, save, sha, shell, workspace


def observe(template, patch):
    raw = patch.read_bytes()
    area = workspace(template)
    try:
        source = area/'source'
        git(source,'update-index','--refresh')
        paths = []
        if raw:
            git(source,'apply','--include=*.test.ts','--include=*.test.tsx','--allow-empty',
                '--index','--whitespace=nowarn','-',data=raw)
            paths = git(source,'diff','--cached','--name-only','--diff-filter=AM','-z').decode().split('\0')[:-1]
        result = {'patchSha256':sha(raw),'paths':paths}
        if paths:
            result['run'] = shell(area,'./node_modules/.bin/vitest run --pool=threads '+shlex.join(paths),120)
        return result
    finally:
        shutil.rmtree(area)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('template','patch','output'):
        parser.add_argument(name,type=Path)
    args = parser.parse_args()
    save(args.output,observe(args.template.resolve(),args.patch))
