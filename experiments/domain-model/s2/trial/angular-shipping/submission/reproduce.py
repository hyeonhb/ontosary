"""Build evaluator patches separately, submit their bytes, and verify the recorded observations."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from grade import HERE, ROOT, PARENT, MODIFIER, sha

FIX = 'e30fd9e94214135de85c95631edc6f2fcedd0da1'
HELPER = str(Path(MODIFIER).with_name('shipping-cancellation-amount.ts'))
SERVICE = 'packages/core/src/service/services/order.service.ts'
RECORD = HERE.parents[2] / 'results/2026-11-26-shipping-grading-fix'
REVIEW = ROOT / 'docs/reviews/evidence/2026-11-26-shipping-grading-countercontrols.json'
INCLUSIVE_REVIEW = ROOT / 'docs/reviews/evidence/2026-11-26-shipping-grading-inclusive-only.json'
INCLUSIVE_RECORD = HERE.parents[2] / 'results/2026-11-26-shipping-inclusive-only/grade.json'
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
    raw_connection = replace(upstream, 'await this.connection.getRepository(ctx, Order).save(orderWithLines,',
                             'await this.connection.rawConnection.getRepository(Order).save(orderWithLines,')
    sources = {
        'original':{}, 'always-gross':{MODIFIER:partial}, 'upstream':{MODIFIER:upstream},
        'helper':{MODIFIER:external, HELPER:HELPER_SOURCE},
        'helper-mutated':{MODIFIER:external, HELPER:replace(HELPER_SOURCE, 'return -line.discountedPriceWithTax;', 'return -line.discountedPrice;')},
        'unobserved-service':{MODIFIER:upstream, SERVICE:skipped},
        'missing-context':{MODIFIER:unknown}, 'unreached-branch':{MODIFIER:unused_branch},
        'unattributed-exception':{MODIFIER:raw_connection},
    }
    patches = {}
    for name, files in sources.items():
        git('reset', '--hard', '--quiet', PARENT)
        for path, text in files.items():
            (staging / path).write_text(text)
        git('add', '--all')
        patches[name] = git('diff', '--cached', '--no-renames', '--no-ext-diff', '--full-index', '--no-color')
    patches['rejected'] = patches['always-gross'].replace(old.encode(), b'amount: -shippingLine.missingPriorPrice,')
    review = json.loads(REVIEW.read_bytes())
    assert review['parent'] == PARENT
    for name, submission in review['submissions'].items():
        patches[name] = submission['patch'].encode('utf-8')
        assert sha(patches[name]) == submission['patchSha256']
    inclusive = json.loads(INCLUSIVE_REVIEW.read_bytes())
    assert inclusive['parent'] == PARENT
    patches['inclusive-only'] = inclusive['patch'].encode('utf-8')
    assert sha(patches['inclusive-only']) == inclusive['patchSha256']
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
            assert row['orderSaves'] == [old['after']]
            assert row['allCancelled'] == old['cancelShipping']
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

    error = results['unattributed-exception']
    assert error['failed'] == 0 and error['ungradable'] == 6
    assert all(r['stage'] == 'runtime' and 'getRepository' in r['reason'] for r in error['rows'])
    for name, original in json.loads(REVIEW.read_bytes())['submissions'].items():
        result = results[name]
        assert result['tree'] == original['tree'] and result['patchSha256'] == original['patchSha256']
        assert result['failed'] == result['measured'] == 6 and result['ungradable'] == 0
        for row, reviewed in zip(result['rows'], original['rows'], strict=True):
            assert all(row[k] == reviewed[k] for k in ('path', 'taxIncluded', 'cancelShipping'))
            assert row['status'] == 'fail'
            reasons = {m['field']: (m['expected'], m['actual']) for m in row['mismatches']}
            if name == 'save-first':
                saved = reviewed['independentMoneyAtOrderSave']
                assert row['orderSaves'] == [saved] and row['after'] == row['expected']
                assert reasons == {'moneyAtOrderSave': (row['expected'], saved)}
            else:
                assert name == 'wrong-quantity'
                assert row['remainingItems'] == 2 and row['allCancelled'] is False
                if row['cancelShipping']:
                    assert reasons['allCancelled'] == (True, False)
                else:
                    assert 'allCancelled' not in reasons
                    assert reasons['remainingItems'] == (1, 2)

    review = json.loads(INCLUSIVE_REVIEW.read_bytes())
    inclusive = results['inclusive-only']
    assert inclusive['tree'] == review['tree'] and inclusive['patchSha256'] == review['patchSha256']
    assert (inclusive['passed'], inclusive['failed'], inclusive['ungradable']) == (4, 2, 0)
    for row, diagnostic in zip(inclusive['rows'], review['rows'], strict=True):
        for key in ('path', 'taxIncluded', 'cancelShipping', 'expected', 'orderSaves', 'after', 'shippingSaveObserved'):
            assert row[key] == diagnostic[key], (key, row)
        if row['cancelShipping'] and not row['taxIncluded']:
            assert row['status'] == 'fail'
            assert row['mismatches'] == [
                {'field': field, 'expected': [0, 0, 0, 0], 'actual': [1000, 1200, 1000, 1200]}
                for field in ('moneyAtOrderSave', 'moneyAtReturn')
            ]
        else:
            assert row['status'] == 'pass' and not row['mismatches']


def verify_records(record, out):
    # The prior record predates the diagnostic. Compare every field it contained.
    prior = json.loads((RECORD / 'results.json').read_bytes())
    assert record['participantCalls'] == prior['participantCalls']
    assert set(record['results']) == set(prior['results']) | {'inclusive-only'}
    for name, old in prior['results'].items():
        current = dict(record['results'][name])
        if 'rows' in current:
            current['rows'] = [{k: v for k, v in row.items() if k != 'shippingSaveObserved'}
                               for row in current['rows']]
        assert current == old, f'{name}: previous result changed'
    assert (out / 'inclusive-only/grade.json').read_bytes() == INCLUSIVE_RECORD.read_bytes()


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
        verify_records(record, out)
    print('Verified expected behavior and grading boundaries.')


if __name__ == '__main__':
    main()
