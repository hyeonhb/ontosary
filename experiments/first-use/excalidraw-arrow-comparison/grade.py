"""Replay sealed diffs by blind ID against an installed, pristine source snapshot."""
import argparse
import json
import re
import shutil
import time
from pathlib import Path
from lab import ARROW, LASSO, PROBE, git, save, sha, shell, workspace


def grade(template, patch, dest):
    start = time.monotonic()
    raw = patch.read_bytes()
    result = dict(patchSha256=sha(raw), complete=False, applied=False)
    area = workspace(template)
    try:
        source = area/'source'
        git(source,'update-index','--refresh')
        if raw:
            import subprocess
            applied = subprocess.run(['git', '-C',source,'apply','--index','--whitespace=nowarn','-'],
                                     input=raw, capture_output=True)
            if applied.returncode:
                result['applyError'] = applied.stderr.decode(errors='replace')
                return result
        result['applied'] = True
        for target, original in [(source/ARROW, PROBE), (source/LASSO, template/LASSO)]:
            if target.resolve() != target:
                raise ValueError('test path contains a symlink')
            shutil.copyfile(original, target)
        report = area/'tmp/vitest.json'
        run = shell(area, f'./node_modules/.bin/vitest run --pool=threads --reporter=default --reporter=json --outputFile.json={report} {ARROW} {LASSO}', 150, 100000)
        result['run'] = run
        scenes = [json.loads(x) for x in re.findall(r'^ARROW_SCENE (\[.*\])\s*$', re.sub(r'\x1b\[[0-9;]*m','',run['output']), re.M)]
        results = json.loads(report.read_bytes())['testResults'] if report.exists() else []
        def cases(path):
            return [a['status'] for f in results if f['name'] == str(source/path) for a in f['assertionResults']]
        result.update(scenes=scenes, lasso=cases(LASSO), probe=cases(ARROW))
        expected_ids = [['ordinary','locked'], ['ordinary','locked','off-path']]
        if [[el['id'] for el in scene] for scene in scenes] == expected_ids:
            result['actions'] = {key:all(el['deleted'] is (key=='ordinary') and el['live'] is (key!='ordinary')
                                 for scene in scenes for el in scene if el['id']==key) for key in expected_ids[1]}
        result['complete'] = bool(result.get('actions') and all(result['actions'].values()) and
                                  run['exit']==0 and result['lasso']==['passed']*6 and result['probe']==['passed']*2)
        return result
    finally:
        result['secondsIncludingCopy'] = round(time.monotonic()-start,3)
        save(dest,result)
        shutil.rmtree(area)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('template','patch','output'):
        parser.add_argument(name,type=Path)
    args = parser.parse_args()
    grade(args.template.resolve(),args.patch,args.output)
