"""Inspect the upstream objects and frozen participant views used in candidate selection."""
import hashlib
import json
from functools import cache
from pathlib import Path
import subprocess
import sys

S2 = Path(__file__).resolve().parents[2]
MATERIAL = S2 / 'results/2026-11-10-trial-preparation'
REPO = sys.argv[1]
HEAD = 'a67242a6b685d6a98a7beebb109c19db07550369'
BASE = '534e6003534f74761e82de1b8c6061cba89945d1'
FREEZE = 'c6d093310ee8a2fb5e8fef61decd01dd4e51ec7d'
CANDIDATES = {
    '3150': '37775552b38b7d3f7158875756074b34a091fcd0',
    '2608': '913e6d8e082c0ac04f836aa6c305e3465849c4dc',
    '4348': 'e30fd9e94214135de85c95631edc6f2fcedd0da1',
}


def git(*args):
    return subprocess.check_output(['git', '-C', REPO, *args])


@cache
def blob(revision, path):
    return git('show', f'{revision}:{path}')


def inspect(anchor, revision):
    data = blob(revision, anchor['file'])
    source = data.decode()
    span = source.encode('utf-16-le')[2 * anchor['offset']:2 * anchor['end']]
    return {
        'fileHashMatch': hashlib.sha256(data).hexdigest() == anchor['sha256'],
        'spanMatch': span == anchor['text'].encode('utf-16-le'),
        'quoteOccurrences': source.count(anchor['text']),
    }


def main():
    views = sorted((MATERIAL / 'B/views').glob('*.json'))
    narrative = [MATERIAL / 'C' / name for name in ('guide.md', 'observations.md', 'roles.md', 'evidence.md')]
    assert (len(views), len(narrative)) == (68, 4)
    roots = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in views + narrative}
    for path in roots:
        relative = path.relative_to(S2.parents[2])
        frozen = subprocess.check_output(['git', '-C', S2, 'show', f'{FREEZE}:{relative}'])
        assert hashlib.sha256(frozen).hexdigest() == roots[path], path
    parity = subprocess.check_output([sys.executable, S2 / 'verification/2026-11-10-trial-preparation/audit-parity.py', MATERIAL])
    anchors = [json.loads(path.read_bytes())['value'] for path in views if path.name.startswith('evidence-')]
    paths = sorted({a['file'] for a in anchors})
    assert (len(anchors), len(paths)) == (30, 8)
    log = git('log', '--full-history', '--no-merges', '--format=%H %as %s', HEAD, '--', *paths)
    out = {
        'upstreamHead': HEAD, 'baseline': BASE, 'materialsFreeze': FREEZE,
        'verifiedFiles': len(roots), 'parityLeaves': json.loads(parity)['totalUnits'],
        'seedFiles': paths, 'seedHistoryCommits': len(log.splitlines()),
        'seedHistorySha256': hashlib.sha256(log).hexdigest(), 'candidates': {},
    }
    for issue, fix in CANDIDATES.items():
        parent = git('rev-parse', fix + '^').decode().strip()
        checks = {a['id']: inspect(a, parent) for a in anchors}
        terms = {
            '2608': ['orderPlacedQuantity', 'refundedCount', 'lineCanBeRefundedOrCancelled'],
            '3150': ['proratedUnitPriceWithTax', 'prorated-unit-price'],
            '4348': ['discountedPriceWithTax', 'listPriceIncludesTax', 'pricesIncludeTax', 'shipping cancellation'],
        }[issue] + ['#' + issue]
        out['candidates'][issue] = {
            'parent': parent, 'fix': fix,
            'baselineIsAncestorOfParent': subprocess.run(
                ['git', '-C', REPO, 'merge-base', '--is-ancestor', BASE, parent], check=False,
            ).returncode == 0,
            'exactFiles': sum(hashlib.sha256(blob(parent, path)).hexdigest() ==
                              next(a['sha256'] for a in anchors if a['file'] == path) for path in paths),
            'anchors': checks,
            'materialTermHits': {term: [str(p.relative_to(MATERIAL)) for p in roots
                                        if term.casefold() in p.read_text().casefold()] for term in terms},
        }
    assert all(c['fileHashMatch'] and c['spanMatch'] for c in out['candidates']['4348']['anchors'].values())
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
