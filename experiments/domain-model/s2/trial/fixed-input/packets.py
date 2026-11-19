"""Materialize the public UTF-8 packets byte-for-byte from pinned inputs."""
import gzip
import hashlib
import json
import sys
from pathlib import Path

repo = Path(__file__).resolve().parents[5]
s2 = repo / 'experiments/domain-model/s2'
prepared = s2 / 'results/2026-11-10-trial-preparation'
source, output = (Path(a) for a in sys.argv[1:])
output.mkdir(parents=True, exist_ok=True)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def block(name, data):
    return f'\n--- FILE {name} ({len(data)} bytes) ---\n'.encode() + data + b'\n'


inventory = json.loads(gzip.decompress((repo / 'experiments/public-app/results/2026-11-08/vendure/inventory.json.gz').read_bytes()))
task = (prepared / 'A/TASK.txt').read_text().split('시작은 START.md')[0].strip()
guide = (prepared / 'A/RUN.md').read_text().split('source/는 생산 소스다. ')[1].split('\n\n')[0]
public = (s2 / 'trial/task.ts').read_text()
assert task in public and guide in public
rules = (
    '제공된 텍스트만 사용한다. 경로는 Vendure 저장소 루트 기준이다. '
    '다른 자료, 도구, 파일 탐색, 셸, 검색, 실행 중 질문은 사용할 수 없다. '
    '첫 응답에 기준 소스에 적용할 단일 Git unified diff만 반환한다. 파일 경로는 a/와 b/ 접두사를 사용한다. '
    '설명과 코드 펜스 없이 최대 49152 UTF-8 바이트로 제출한다. git apply로 적용하고 필요한 경우 --recount로 줄 수만 다시 계산하며 문맥 줄이나 변경 내용을 보정하지 않는다. '
    '패치에는 텍스트 일반 파일만 허용하며 심볼릭 링크·특수 파일·경로 이탈은 거부한다.'
)
common = (task + '\n\n' + guide + '\n\n' + rules + '\n').encode()
files = {}
for entry in sorted(inventory, key=lambda e: e['path']):
    name = entry['path']
    path = Path(name)
    if not (name.startswith('packages/admin-ui/src/') and name.endswith('.ts')
            and any(term in path.name.lower() for term in ('order', 'cancel', 'refund'))):
        continue
    if name.endswith(('.spec.ts', '.test.ts', '.d.ts')) or {'testing', 'generated', '__tests__'} & set(path.parts):
        continue
    data = (source / name).read_bytes()
    assert digest(data) == entry['sha256'], name
    files[name] = digest(data)
    common += block(name, data)
extras = {'A': [], 'B': sorted((prepared / 'B/views').glob('*.json')),
          'C': [prepared / 'C' / name for name in ('guide.md', 'observations.md', 'roles.md', 'evidence.md')]}
manifest = {'revision': json.loads((prepared / 'A/SOURCE-NOTICE.txt').read_text().split('\n\n')[0])['revision'],
            'common': {'sha256': digest(common), 'bytes': len(common)}, 'sourceFiles': files, 'conditions': {}}
for arm, paths in extras.items():
    packet = common
    materials = {}
    for path in paths:
        name = path.relative_to(prepared / arm).as_posix()
        data = path.read_bytes()
        materials[name] = digest(data)
        packet += block(name, data)
    (output / f'{arm}.txt').write_bytes(packet)
    manifest['conditions'][arm] = {'bytes': len(packet), 'sha256': digest(packet), 'materials': materials}
(output / 'inputs.json').write_text(json.dumps(manifest, indent=2) + '\n')
