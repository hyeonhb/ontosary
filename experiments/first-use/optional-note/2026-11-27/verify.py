"""Replay the observed four first submissions using the checked-in evidence."""
import hashlib
import json
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(path):
    return json.loads(path.read_text())


def verify():
    protocol = load(HERE / 'protocol.json')
    costs = load(HERE / 'costs.json')
    tasks = {'methods', 'slug'}
    assert set(costs) == set(protocol['tasks']) == tasks
    sessions = HERE / 'sessions'
    assert {p.stem for p in sessions.glob('*.json')} == {
        f'{task}-{role}' for task in tasks for role in 'AB'
    }
    threads, responses, plans = set(), set(), set()
    for task, conditions in costs.items():
        assert set(conditions) == {'A', 'B'}
        request = protocol['tasks'][task]['request']
        for role, cost in conditions.items():
            session = load(sessions / f'{task}-{role}.json')
            first, last = rows = session['turns']
            assert first['kind'] == 'checkpoint' and last['kind'] == 'plan'
            assert first['prompt'] == '\n\n'.join([protocol['common'], request, protocol['checkpoint']])
            finish = [protocol['offer'], protocol['finish']] if role == 'B' else [protocol['finish']]
            assert last['prompt'] == '\n\n'.join(finish)
            assert not first['resume'] and last['resume']
            thread = first['threadDigest']
            assert thread == last['threadDigest'] and thread not in threads
            threads.add(thread)
            plan = (sessions / last['firstPlan']).resolve()
            assert plan.parent == HERE / 'blind' and plan.stem.startswith(task + '-')
            assert plan not in plans and hashlib.sha256(plan.read_bytes()).hexdigest() == last['firstPlanSha256']
            plans.add(plan)

            usage = dict.fromkeys(session['tokens'], 0)
            count = 0
            for row in rows:
                assert row['turnContext'] == {'model': 'gpt-6.2-sol', 'effort': 'medium'}
                assert row['exitCode'] == 0 and not row['timedOut']
                for entry in row['responseUsages']:
                    assert entry['responseDigest'] not in responses
                    responses.add(entry['responseDigest'])
                    count += 1
                    for key in usage:
                        usage[key] += entry[key]
                cli, = row['rawCliUsage']
                assert usage == {key: cli[key] for key in usage}
            assert count == cost['meteredModelResponses'] == session['measuredResponses']
            assert usage == cost['tokens'] == session['tokens']
            elapsed = datetime.fromisoformat(last['endedUTC']) - datetime.fromisoformat(first['startedUTC'])
            assert round(elapsed.total_seconds(), 3) == cost['elapsed'] == session['elapsedSeconds']
            active = round(sum(row['activeSeconds'] for row in rows), 3)
            assert active == cost['workerActive'] == session['activeSeconds']
            assert round(cost['elapsed'] - active, 3) == cost['betweenWorkerTurns']
            assert cost['workerTurns'] == 2 and cost['writerTurns'] == cost['writerActive'] == 0
            print(f"{task} {role} {plan.stem} | {count} responses | "
                  f"{usage['input_tokens']} input, {usage['output_tokens']} output | {cost['elapsed']} s")
    assert plans == set((HERE / 'blind').glob('*.md'))
    print(f"{len(threads)} workers, 0 note requests, 0 writers, {len(responses)} metered responses")


if __name__ == '__main__':
    verify()
