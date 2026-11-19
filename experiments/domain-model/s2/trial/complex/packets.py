"""Reuse the pilot's public file selection and exact unmodified B/C knowledge."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

here = Path(__file__).resolve().parent
source, output = map(Path, sys.argv[1:])
with tempfile.TemporaryDirectory() as tmp:
    template = Path(tmp)
    subprocess.run([sys.executable, str(here.parent/'fixed-input/packets.py'), str(source), tmp], check=True)
    base = json.loads((template/'inputs.json').read_bytes())
    original = (template/'A.txt').read_bytes()
    # Replace only the previous public task. The public guide, source and submission format follow it.
    guide = 'admin-ui의 지원되는 TypeScript'.encode()
    body = original[original.index(guide):]
    for task in sorted((here/'public').glob('*.md')):
        directory = output/task.stem/'inputs'
        directory.mkdir(parents=True, exist_ok=True)
        common = task.read_bytes().rstrip() + b'\n\n' + body
        manifest = {**base, 'common': {'bytes': len(common), 'sha256': hashlib.sha256(common).hexdigest()}, 'conditions': {}}
        for arm in 'ABC':
            old = (template/f'{arm}.txt').read_bytes()
            assert old.startswith(original)
            packet = common + old[len(original):]
            (directory/f'{arm}.txt').write_bytes(packet)
            manifest['conditions'][arm] = {**base['conditions'][arm], 'bytes': len(packet), 'sha256': hashlib.sha256(packet).hexdigest()}
        (directory/'inputs.json').write_text(json.dumps(manifest, indent=2)+'\n')
