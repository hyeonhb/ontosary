"""Build evaluator patches separately, submit their bytes, and verify the recorded observations."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from grade import HERE, PARENT, MODIFIER, sha

FIX = 'e30fd9e94214135de85c95631edc6f2fcedd0da1'
HELPER = str(Path(MODIFIER).with_name('shipping-cancellation-amount.ts'))
SERVICE = 'packages/core/src/service/services/order.service.ts'
RECORD = HERE.parents[2] / 'results/2026-11-26-shipping-submission-grading'
SELECTION = HERE.parents[2] / 'results/2026-11-24-angular-selection/behavior.json'
HELPER_SOURCE = """import type { ShippingLine } from '../../../entity/shipping-line/shipping-line.entity';

export function cancellationAmount(line: ShippingLine): number {
    if (!line.listPriceIncludesTax) {
        return -line.discountedPrice;
    }
    return -line.discountedPriceWithTax;
}
"""


def replace(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def fixtures(repo, out):
    # Only this fixture builder reads the solution revision.
    staging = out / 'fixture-builder'
    subprocess.run(['git', 'clone', '--quiet', '--shared', '--no-checkout', str(repo), str(staging)], check=True)

    def git(*args):
        return subprocess.check_output(['git', '-C', staging, *args])

    git('-c', 'advice.detachedHead=false', 'checkout', '--quiet', '--detach', PARENT)
    base = (staging / MODIFIER).read_text()
    upstream = git('show', FIX + ':' + MODIFIER).decode()
    assert git('rev-parse', FIX + '^').decode().strip() == PARENT
    old = 'amount: -shippingLine.discountedPrice,'
    partial = replace(base, old, 'amount: -shippingLine.discountedPriceWithTax,')
    external = ("import { cancellationAmount } from './shipping-cancellation-amount';\n" +
                replace(base, old, 'amount: cancellationAmount(shippingLine),'))
    service = (staging / SERVICE).read_text()
    skipped = replace(service, 'let allOrderItemsCancelled = false;',
                      "throw new Error('cancellation unavailable');\n        let allOrderItemsCancelled = false;")
    unknown = replace(base, old, 'amount: ctx.channel.defaultTaxZone?.id ? -shippingLine.discountedPriceWithTax : -shippingLine.discountedPrice,')
    unused_branch = replace(upstream, 'return new EmptyOrderLineSelectionError();',
                            "throw new Error('empty selection');")
    sources = {
        'original':{}, 'always-gross':{MODIFIER:partial}, 'upstream':{MODIFIER:upstream},
        'helper':{MODIFIER:external, HELPER:HELPER_SOURCE},
        'helper-mutated':{MODIFIER:external, HELPER:replace(HELPER_SOURCE, 'return -line.discountedPriceWithTax;', 'return -line.discountedPrice;')},
        'unobserved-service':{MODIFIER:upstream, SERVICE:skipped},
        'missing-context':{MODIFIER:unknown}, 'unreached-branch':{MODIFIER:unused_branch},
    }
    patches = {}
    for name, files in sources.items():
        git('reset', '--hard', '--quiet', PARENT)
        for path, text in files.items():
            (staging / path).write_text(text)
        git('add', '--all')
        patches[name] = git('diff', '--cached', '--no-renames', '--no-ext-diff', '--full-index', '--no-color')
    patches['rejected'] = patches['always-gross'].replace(old.encode(), b'amount: -shippingLine.missingPriorPrice,')
    return patches


def verify(results):
    previous = json.loads(SELECTION.read_text())['controls']
    for name, prior in [('original','original'), ('always-gross','always-gross'), ('upstream','upstream'),
                        ('helper','upstream'), ('helper-mutated','original')]:
        result = results[name]
        assert result['stage'] == 'observation' and result['measured'] == 6 and result['ungradable'] == 0
        for row, old in zip(result['rows'], previous[prior], strict=True):
            assert {k:row[k] for k in old} == old, (name, row)
            assert row['status'] == ('pass' if old['passed'] else 'fail')
            assert row['calls'][MODIFIER + '#cancelOrderByOrderLines'] == 1
            if name.startswith('helper'):
                assert row['calls'].get(HELPER + '#cancellationAmount', 0) == int(row['cancelShipping'])
        for change in result['changes']:
            assert change['sha256'] == result['sources'][change['path']]
    rejected = results['rejected']
    assert rejected['stage'] == 'patch-rejected' and rejected['attempted'] == 0
    skipped = results['unobserved-service']
    assert skipped['ungradable'] == 6 and all(SERVICE in r['reason'] for r in skipped['rows'])
    branch = results['unreached-branch']
    assert branch['ungradable'] == 6 and branch['measured'] == 6
    assert all(r['stage'] == 'coverage' for r in branch['rows'])
    context = results['missing-context']
    assert context['ungradable'] == 4 and context['passed'] == 2 and context['failed'] == 0
    assert all('channel.defaultTaxZone' in r['reason'] for r in context['rows'] if r['cancelShipping'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repository', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    out = args.output.resolve()
    repo = args.repository.resolve()
    out.mkdir(parents=True, exist_ok=False)
    results = {}
    patches = fixtures(repo, out)
    # All grading checkouts descend from a shallow repository that lacks the solution object.
    baseline = out / 'parent.git'
    subprocess.run(['git', 'init', '--quiet', '--bare', '--initial-branch=base', str(baseline)], check=True)
    subprocess.run(['git', '-C', baseline, 'fetch', '--quiet', '--depth=1', '--no-tags',
                    repo.as_uri(), PARENT + ':refs/heads/base'], check=True)
    assert subprocess.run(['git', '-C', baseline, 'cat-file', '-e', FIX], capture_output=True).returncode != 0
    for name, patch in patches.items():
        path = out / (name + '.patch')
        path.write_bytes(patch)
        subprocess.run([sys.executable, '-B', HERE / 'grade.py', baseline, path, out / name], check=True)
        results[name] = json.loads((out / name / 'grade.json').read_text())
        assert results[name]['patchSha256'] == sha(patch)
    verify(results)
    record = {'participantCalls':0, 'results':results}
    data = (json.dumps(record, ensure_ascii=False, indent=2) + '\n').encode()
    (out / 'results.json').write_bytes(data)
    if args.verify:
        assert data == (RECORD / 'results.json').read_bytes(), 'recorded results differ'
    print('Verified expected behavior and grading boundaries.')


if __name__ == '__main__':
    main()
