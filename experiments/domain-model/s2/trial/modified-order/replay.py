"""Replay the local selection controls from two pinned upstream archives (no model or Vendure service)."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
from html.parser import HTMLParser

HERE = Path(__file__).resolve().parent
S2 = HERE.parents[1]
FROZEN = S2 / 'results/2026-11-10-trial-preparation'
RECORD = S2 / 'results/2026-11-24-modified-order-selection'
BASE = 'e30fd9e94214135de85c95631edc6f2fcedd0da1'
FIX = 'e7f8fe0029ceba9b450f60554226cec2cf628309'
ARCHIVES = {BASE: 'bda624352200663029f21ef715d3f10272b6066c263fce549ddef375b6e484f1',
            FIX: '6fe6d35095ed886c63d77c4ac346a51b9d1055bb93f376e8173e60975b3cbdec'}
DASH = Path('packages/dashboard/src')
ORDERS = Path('app/routes/_authenticated/_orders')
DIALOG = ORDERS / 'components/refund-order-dialog.tsx'
UTIL = ORDERS / 'utils/order-utils.ts'
FILES = [DIALOG, UTIL, ORDERS / 'hooks/use-refund-order.ts', ORDERS / 'utils/refund-utils.ts',
         Path('lib/components/ui/input.tsx')]
EXPECTED = {'original': [False, False, True, True], 'display-only': [False, False, True, True],
            'current-only': [True, True, False, True], 'upstream': [True, True, True, True]}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_bytes())


def replace(path, old, new, count):
    source = path.read_text()
    assert source.count(old) == count, path
    path.write_text(source.replace(old, new))


def audit(source):
    views = FROZEN/'B/views'
    materials = [*sorted(views.glob('*.json')), *(FROZEN/'C'/f for f in ('guide.md','observations.md','roles.md','evidence.md'))]
    parity = subprocess.check_output([sys.executable, S2/'verification/2026-11-10-trial-preparation/audit-parity.py', FROZEN])
    anchors = []
    for view in sorted(views.glob('evidence-*.json')):
        a = read_json(view)['value']
        raw = (source/a['file']).read_bytes()
        fragment = raw.decode().encode('utf-16-le')[2*a['offset']:2*a['end']].decode('utf-16-le')
        assert sha(raw) == a['sha256'] and fragment == a['text'], view
        anchors.append({'id':a['id'],'file':a['file'],'line':a['line'],'symbol':a['symbol'],'sha256':sha(raw)})
    return {'baseline':read_json(views/'status.json'), 'fileHashes':{str(p.relative_to(FROZEN)):sha(p.read_bytes()) for p in materials},
            'parityLeaves':json.loads(parity)['totalUnits'], 'anchorsAtParent':anchors,
            'dashboardAnchors':sum(a['file'].startswith('packages/dashboard/') for a in anchors)}


class ResultElement(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.text = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'pre' and dict(attrs).get('id') == 'result':
            self.active = True

    def handle_endtag(self, tag):
        if tag == 'pre':
            self.active = False

    def handle_data(self, data):
        if self.active:
            self.text += data


def observe(root, control, chrome):
    dist = root/control/'dist'
    subprocess.run(['node', HERE/'build.mjs', root/control/'src', dist], check=True)
    with tempfile.TemporaryDirectory() as profile:
        result = subprocess.run([chrome, '--headless', '--disable-gpu', '--disable-background-networking',
                                 '--no-first-run', '--user-data-dir='+profile, '--dump-dom', (dist/'index.html').as_uri()],
                                capture_output=True, text=True, check=True, timeout=60)
    parser = ResultElement()
    parser.feed(result.stdout)
    rows = json.loads(parser.text)
    assert isinstance(rows, list) and [r['name'] for r in rows] == ['increase','add','partial','exhausted'], rows
    for row, limit in zip(rows, [2,1,1,0]):
        if limit:
            # Compare independent expected quantities with what the mounted dialog showed and retained.
            display = row['quantityShown'] in ('1', '3') if row['name'] == 'partial' else row['quantityShown'] == str(limit)
            attempts = row['attempts']
            row['checks'] = {'display':display, 'selectable':row['selectable'], 'max':row['max']==str(limit),
                             'acceptsRemaining':bool(attempts) and attempts[0]=={'requested':limit,'retained':str(limit)},
                             'limitsExcess':bool(attempts) and attempts[-1]=={'requested':limit+1,'retained':str(limit)}}
        else:
            blocked = not row['selectable'] or (row['max'] == '0' and len(row['attempts']) == 1
                       and row['attempts'][0]['requested'] == 1 and row['attempts'][0]['retained'] in ('', '0'))
            row['checks'] = {'blocksDuplicate':blocked}
        row['passed'] = all(row['checks'].values())
    assert [r['passed'] for r in rows] == EXPECTED[control], (control,rows)
    # These two controls tie on complete cases; the visible quantity must distinguish them.
    assert rows[0]['checks']['display'] == (control != 'original')
    assert rows[0]['checks']['acceptsRemaining'] == (control in ('upstream', 'current-only'))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archives', type=Path, help='directory containing <commit>.tgz files')
    parser.add_argument('out', type=Path, help='new output directory')
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--chrome', default=os.getenv('CHROME_BIN') or '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    public = out/'public'
    public.mkdir()
    for rev, digest in ARCHIVES.items():
        assert sha((args.archives/(rev+'.tgz')).read_bytes()) == digest, rev
    with tarfile.open(args.archives/(BASE+'.tgz')) as base:
        base.extractall(public, filter='data')
    source = public/'source'
    (public/('vendure-'+BASE)).rename(source)
    assert not any(source.rglob('.git'))
    shutil.copyfile(HERE/'public/request.txt', public/'request.txt')
    results = {'parent':BASE, 'fix':FIX, 'archiveSha256':ARCHIVES, 'requestSha256':sha((public/'request.txt').read_bytes()),
               'participantCalls':0, 'materialAudit':audit(source), 'controls':{}}
    for control in EXPECTED:
        src = out/control/'src'
        for rel in FILES:
            (src/rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source/DASH/rel, src/rel)
        if control in ('upstream','current-only'):
            with tarfile.open(args.archives/(FIX+'.tgz')) as fix:
                for rel in (DIALOG, UTIL):
                    member = fix.extractfile(str(Path('vendure-'+FIX)/DASH/rel))
                    (src/rel).write_bytes(member.read())
        if control == 'display-only':
            replace(src/DIALOG, 'line.orderPlacedQuantity', 'Math.max(line.orderPlacedQuantity, line.quantity)', 2)
        if control == 'current-only':
            replace(src/UTIL, 'return Math.max(line.orderPlacedQuantity, line.quantity);', 'return line.quantity;', 1)
        results['controls'][control] = {'sourceHashes':{str(DASH/p):sha((src/p).read_bytes()) for p in FILES},
                                        'cases':observe(out,control,args.chrome)}
    raw = json.dumps(results,indent=2,ensure_ascii=False)+'\n'
    (out/'results.json').write_text(raw)
    if args.verify:
        assert raw.encode() == (RECORD/'results.json').read_bytes()
    print({c:sum(r['passed'] for r in g['cases']) for c,g in results['controls'].items()})
    print(subprocess.check_output([args.chrome,'--version'], text=True).strip())


if __name__ == '__main__':
    main()
