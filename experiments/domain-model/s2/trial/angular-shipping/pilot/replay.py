"""Replay sealed actions, regenerate each first patch, grade it, and print the result tables offline."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import subprocess
import sys

from collect import (BASE, FROZEN, HERE, LIMITS, MODEL, OUT, VERSION, Session, baseline, collect_patch,
                     digest, encode, fingerprint, git, material_files, packet, prompt)
sys.path.insert(0, str(HERE.parent / 'submission'))
from grade import grade


def load(path):
    return json.loads(path.read_bytes())


def table(headers, rows):
    for row in [headers, ['---']*len(headers), *rows]:
        print('| ' + ' | '.join(str(value) for value in row) + ' |')
    print()


def print_tables(outcomes, costs, tools):
    rows = []
    cases = []
    rejections = []
    submitted = attempted = 0
    for arm, reason, marks, patch_hash, result in outcomes:
        if patch_hash is None:
            assert result is None
            rows.append([arm, reason, *marks, '미제출', '—', 0, '—', '—', '—'])
            continue
        assert result['patchSha256'] == patch_hash
        submitted += 1
        attempted += result['attempted']
        stage = result['stage']
        if stage == 'patch-rejected':
            rejections.append((arm, result['reason']))
            verdicts = ['—'] * 3
            application = '적용 거부'
        elif stage == 'observation':
            verdicts = [result[k] for k in ('passed', 'failed', 'ungradable')]
            application = '적용 완료'
        else:
            raise ValueError(f'Unknown grading stage: {stage}')
        rows.append([arm, reason, *marks, '제출', application, result['attempted'], *verdicts])
        for row in result.get('rows',[]):
            cases.append([arm,row['path'],'포함' if row['taxIncluded'] else '별도',
                          '전체' if row['cancelShipping'] else '일부',row['status'],
                          row['expected'],row.get('orderSaves','—'),row.get('after','—')])

    print('## 조건별 판정\n')
    table(['조건', '종료 사유', '취소 경로 합류', '배송 차감·합계', '봉인된 첫 패치', '패치 적용',
           '사례 실행', '통과', '업무 실패', '판정 불가'], rows)
    print(f'최종 제출 {submitted}건 · 적용 거부 {len(rejections)}건 · 사례 실행 {attempted}건.\n')
    for arm, diagnostic in rejections:
        print(f'{arm}의 패치 적용 거부 사유\n')
        for line in diagnostic.splitlines():
            print('    ' + line)
        print()

    print('## 누적 비용과 차이\n')
    table(['조건','시점','요청','초','입력','출력','캐시 입력','추론 출력'],costs)
    print('## 조회 작업\n')
    table(['조건','자료','작업','회','반환 바이트','반환 행','오류'],tools)
    print('## 첫 패치의 사례별 금액\n')
    if not cases:
        print('저장·반환 금액을 표시할 채점 사례 행이 없다.')
        return
    table(['조건','경로','세금','취소','판정','기대','주문 저장 시점들','반환 시점'],cases)


def cost(rows):
    usage = Counter()
    for row in rows:
        if row['usage'] is None:
            return None
        usage.update(row['usage'])
    return usage


def numbers(rows):
    usage = cost(rows)
    return [len(rows), rows[-1]['elapsedSeconds'] if rows else 0,
            *[usage[key] if usage is not None and key in usage else '—' for key in
              ('input_tokens', 'output_tokens', 'cached_input_tokens', 'reasoning_output_tokens')]]


def verify_arm(repository, work, arm, freeze):
    directory = OUT/arm
    records = [load(path) for path in sorted(directory.glob('[0-9][0-9].json'))]
    seal = load(directory/'seal.json')
    copy = work/arm
    subprocess.run(['git','clone','--quiet','--shared','--no-checkout',str(repository),copy],check=True)
    git(copy,'-c','advice.detachedHead=false','checkout','--quiet','--detach',BASE)
    source = baseline(copy)
    aux = material_files(arm, FROZEN)
    public = freeze['arms'][arm]
    assert fingerprint(source) == public['source'] and prompt(arm) == public['public']
    assert {p:digest(raw) for files in aux.values() for p,raw in files.items()} == public['materials']
    session = Session(arm, source, aux)
    history = []
    by_tool = defaultdict(Counter)
    impact_index = None
    previous_time = 0
    for i, row in enumerate(records, 1):
        assert row['request'] == i and i <= LIMITS['requests']
        assert row['packetSha256'] == digest(packet(arm,history))
        assert previous_time <= row['elapsedSeconds']
        previous_time = row['elapsedSeconds']
        if row['usage'] is None:
            assert i == len(records) and seal['reason'] == 'missing-usage' and seal['holdRemaining']
        if 'action' not in row:
            continue
        action = row['action']
        try:
            parsed = json.loads(row['answer'])
        except (ValueError, TypeError):
            parsed = None
        assert parsed == action
        reply = session.step(action)
        assert digest(encode(reply)) == row['replySha256'] and len(encode(reply)) == row['replyBytes'] <= LIMITS['replyBytes']
        assert ('error' in reply) == row['actionError'] and len(reply.get('rows', [])) == row['replyRows']
        history.append(dict(action=action,reply=reply))
        if 'sealed' in reply:
            assert row['impactSeal'] == reply['sealed']
            impact_index = i
        op = action.get('op') if isinstance(action,dict) else None
        if op in ('list','search','read'):
            counts = by_tool[(action.get('space'), op)]
            counts.update(count=1, bytes=row['replyBytes'], rows=row['replyRows'], errors=int(row['actionError']))
    assert records and seal['elapsedSeconds'] == previous_time
    assert session.impact == seal['impact'] and session.finished == ('patchSha256' in seal)
    result = None
    if session.finished:
        patch = directory/'first.patch'
        assert collect_patch(copy,source,session.spaces['source']) == patch.read_bytes()
        assert digest(patch.read_bytes()) == seal['patchSha256']
        result = grade(repository,patch,work/(arm+'-grade'))
        (work/(arm+'-grade')/'grade.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
        if (directory/'grade.json').exists():
            assert result == load(directory/'grade.json'), f'{arm} grade differs'
    return records, seal, impact_index, result, by_tool


def main(repository, work):
    freeze = load(OUT/'freeze.json')
    assert freeze['order'] == ['A','B','C'] and freeze['limits'] == LIMITS
    assert freeze['evaluatorRevision'] == VERSION and freeze['base'] == BASE
    subprocess.run(['git','diff','--exit-code',VERSION,'--',str(HERE.parent/'submission'),
                    str(HERE.parent/'cases.json'),str(HERE.parent/'observe.mjs'),
                    str(HERE.parent/'replay.mjs'),str(HERE.parent/'load-controls.mjs')],check=True)
    work.mkdir(parents=True,exist_ok=False)
    decisions = load(OUT/'discovery.json')
    outcomes, costs, tools, deltas = [], [], [], []
    phases = {}
    stopped = False
    for arm in freeze['order']:
        if not (OUT/arm).exists():
            assert stopped
            outcomes.append((arm, '미실행', ['—', '—'], None, None))
            costs.append([arm,'미실행',0,0,0,0,0,0])
            continue
        records, seal, index, result, by_tool = verify_arm(repository,work,arm,freeze)
        assert not stopped
        stopped = seal['holdRemaining']
        decision = decisions[arm]
        assert decision['impactSha256'] == (digest(seal['impact'].encode()) if index else None)
        marks = ['충족' if d['met'] else '미충족' for d in decision['items']] if index else ['미제출']*2
        outcomes.append((arm, seal['reason'], marks, seal.get('patchSha256'), result))
        for stage, rows in [('수정 전 제출',records[:index] if index else None),('종료',records)]:
            if rows is not None:
                values = numbers(rows)
                phases[arm,stage] = values
                costs.append([arm,stage,*values])
        if not index:
            costs.append([arm,'수정 전 미제출',*['—']*6])
        known = [row for row in records if row['usage'] is not None]
        if known and len(known) < len(records):
            costs.append([arm,'usage 수신 요청 소계',*numbers(known)])
        for (space,op), c in sorted(by_tool.items()):
            tools.append([arm,space,op,c['count'],c['bytes'],c['rows'],c['errors']])
    for arm in 'BC':
        for stage in ('수정 전 제출','종료'):
            if (arm,stage) in phases and ('A',stage) in phases:
                diff = [round(v-base,3) if isinstance(v,(int,float)) and isinstance(base,(int,float)) else '—'
                        for v,base in zip(phases[arm,stage],phases['A',stage],strict=True)]
                deltas.append([arm+'−A',stage,*diff])
            else:
                deltas.append([arm+'−A',stage,*['—']*6])
    print_tables(outcomes, costs + deltas, tools)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repository',type=Path)
    parser.add_argument('work',type=Path)
    args = parser.parse_args()
    main(args.repository.resolve(),args.work.resolve())
