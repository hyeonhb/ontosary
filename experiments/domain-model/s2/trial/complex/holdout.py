"""Stage packets offline, collect scheduled first replies, or score the entire sealed batch."""
import argparse
import fcntl
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

here = Path(__file__).resolve().parent
evidence = here.parents[1] / 'results/2026-11-19-complex-preparation'
scoring_evidence = here.parents[1] / 'results/2026-11-19-complex-grading-v3'
sol_record = here.parents[1] / 'results/2026-11-20-sol-comparison'
fixed = here.parent/'fixed-input'


def read(path):
    return json.loads(path.read_bytes())


def write(path, value):
    with path.open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(script, *args):
    subprocess.run([sys.executable, str(script), *map(str,args)], check=True)


def stage(work, source, model='gpt-6.2-astra'):
    command(here/'packets.py', source, work)
    for task in ('quantity', 'refresh'):
        frozen = evidence/'heldout'/task
        inputs = work/task/'inputs/inputs.json'
        if inputs.read_bytes() != (frozen/'inputs.json').read_bytes():
            raise ValueError('Public inputs have changed')
        verified = work/task/'inspection'
        verified.mkdir()
        shutil.copyfile(inputs, verified/'inputs.json')
        command(fixed/'session.py', 'inspect', work/task, verified, model)
        current, prior = read(verified/'preflight.json'), read(frozen/'preflight.json')
        # Default tools are only a positive control. The configured model request must exactly match.
        excluded = {'defaultPreview'}
        if model == 'gpt-6.2-sol':
            excluded.update(('model','catalogSha256'))
        if current['model'] != model or {k:v for k,v in current.items() if k not in excluded} != {k:v for k,v in prior.items() if k not in excluded}:
            raise ValueError('Session preflight differs from freeze')


def collect(work, plan):
    cli_version = subprocess.check_output(['codex','--version'],text=True).strip()
    model = plan['participantModel']
    for attempt in plan['order']:
        task, run = attempt['task'], attempt['id']
        directory = work/'attempts'/run
        sealed = directory/run/'seal.json'
        if model == 'gpt-6.2-sol':
            current = read(work/task/'inspection/preflight.json')
            if current != read(sol_record/'preflight'/(task+'.json')):
                raise ValueError('Sol preflight differs from the frozen batch')
        if sealed.exists():
            if model == 'gpt-6.2-sol' and model_status(read(sealed),model) == 'mismatch':
                raise ValueError('Model mismatch or invalid routing record; stop before the next call')
            continue
        if (directory/run).exists():
            # Startup was attempted. Its missing seal needs independent infrastructure adjudication.
            # Never submit its packet again. Preserve all existing bytes.
            if not (directory/'interrupted.json').exists():
                write(directory/'interrupted.json', {'id':run,'status':'infrastructure-error','reason':'missing seal after interrupted collection'})
            continue
        directory.mkdir(parents=True,exist_ok=True)
        frozen = evidence/'heldout'/task
        if read(frozen/'preflight.json')['codex'] != cli_version:
            raise ValueError('Participant CLI version changed')
        if not (work/task/'inspection/preflight.json').exists():
            raise ValueError('Run offline stage before collection')
        for name in ('inputs.json','preflight.json'):
            shutil.copyfile(work/task/'inspection'/name, directory/name)
        local_plan = {'seconds': plan['deadlineSeconds'], 'order':[attempt]}
        if not (directory/'plan.json').exists():
            write(directory/'plan.json',local_plan)
        if read(directory/'plan.json') != local_plan:
            raise ValueError('Attempt metadata changed')
        command(fixed/'session.py','run',work/task,directory,model)
        if model == 'gpt-6.2-sol' and model_status(read(sealed),model) == 'mismatch':
            raise ValueError('Model mismatch or invalid routing record; stop before the next call')


def model_status(seal, model):
    names = seal.get('serverReportedModels')
    if seal.get('requestedModel') != model or not isinstance(names, list) or any(n != model for n in names):
        return 'mismatch'
    return 'confirmed' if names else 'server-unconfirmed'


def observe(work, source, environment, plan, attempt, scoring):
    task, arm, run = attempt['task'], attempt['condition'], attempt['id']
    root = work/'attempts'/run
    d = root/run
    row = {**attempt,'status':'infrastructure-error','success':False,'elapsedSeconds':None,'usage':None}
    if not (d/'seal.json').exists():
        return row
    seal = read(d/'seal.json')
    packet = work/task/'inputs'/f'{arm}.txt'
    expected = read(evidence/'heldout'/task/'inputs.json')['conditions'][arm]['sha256']
    if sha(packet) != expected or seal['packetSha256'] != expected or sha(d/'events.jsonl') != seal['eventsSha256']:
        raise ValueError('Packet or event seal mismatch')
    row['elapsedSeconds'] = seal['elapsedSeconds']
    events = [json.loads(line) for line in (d/'events.jsonl').read_bytes().splitlines()]
    completed = [x for x in events if x['type']=='turn.completed']
    usage = completed[0].get('usage') if len(completed)==1 else None
    row['usage'] = usage
    if plan['participantModel']=='gpt-6.2-sol':
        row['modelStatus'] = model_status(seal,plan['participantModel'])
        if row['modelStatus'] == 'mismatch':
            row['error'] = 'Model mismatch or invalid routing record'
            return row
    if seal['timeout']:
        row['status'] = 'timeout'
        return row
    if seal['exitCode'] or len(completed)!=1:
        return row
    answers = [x['item']['text'] for x in events if x.get('item',{}).get('type')=='agent_message']
    thread_ids = [x['thread_id'] for x in events if x['type']=='thread.started']
    if len(thread_ids)!=1 or sum(x['type']=='turn.started' for x in events)!=1 or any(
        x.get('item',{}).get('type') not in (None,'agent_message','reasoning') for x in events
    ):
        return row
    row['threadId'] = thread_ids[0]
    answer = d/'answer.txt'
    if not answers or not any(answers):
        if not answer.exists() or not answer.stat().st_size:
            row['status'] = 'no-response'
        return row
    if not answer.is_file():
        row['error'] = 'Agent-message event exists but first-answer file is missing'
        return row
    if len(answers)!=1 or sha(answer)!=seal['answerSha256'] or answer.read_text().rstrip('\n')!=answers[0].rstrip('\n'):
        raise ValueError('First answer seal mismatch')
    if answer.stat().st_size > plan['outputBytes']:
        row['status'] = 'output-byte-limit'
        return row
    grade = scoring/run
    command(here/'calibrate.py',task,source,environment,grade,'--answer',answer)
    applied = read(grade/'submission/grade.json')
    row['applied'] = applied['applied']
    row['status'] = applied['status']
    raw = grade/'submission/evaluation.json.gz'
    if raw.exists():
        report = json.loads(gzip.decompress(raw.read_bytes()))
        expected_evaluator = plan['evaluation'][task]
        if report.get('overall')=='environment-error':
            row.update(status='environment-error', error=report.get('error', 'Evaluator environment error'))
        elif report.get('inputMode')!='complete-root' or not all(report.get(k)==v for k,v in expected_evaluator.items()):
            row['status']='infrastructure-error'
        else:
            row.update(typecheck=report['typecheck']['status'], behavioral=report['behavior']['status'],
                       sourceBinding=report['sourceBinding'], submissionId=report['typecheck']['submissionId'])
            row['status'] = ('type-failed' if row['typecheck']=='failed' else 'unsupported' if row['typecheck']=='unsupported'
                             else 'unsupported' if not row['sourceBinding'] else 'behavior-failed' if row['behavioral']=='failed' else report['overall'])
    if usage is None or any(not isinstance(usage.get(k),int) for k in ('input_tokens','output_tokens')):
        if row['status']=='passed': row['status']='usage-unknown'
    elif usage['input_tokens']>plan['posthocInputTokens'] or usage['output_tokens']>plan['posthocOutputTokens']:
        row['overTokenBudget'] = True
        if row['status']=='passed': row['status']='over-budget'
    row['success'] = row['status']=='passed'
    return row


def observed_cost(work, attempt):
    """Recover known cost independently of whether the submission or evaluator was usable."""
    d = work/'attempts'/attempt['id']/attempt['id']
    elapsed, usage = None, None
    if (d/'seal.json').is_file():
        try:
            elapsed = read(d/'seal.json').get('elapsedSeconds')
        except (OSError, ValueError):
            pass
    if (d/'events.jsonl').is_file():
        completions = []
        for line in (d/'events.jsonl').read_bytes().splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                break
            if event.get('type')=='turn.completed':
                completions.append(event.get('usage'))
        if len(completions)==1:
            usage = completions[0]
    return elapsed, usage


def summarize(rows):
    totals = {}
    for arm in 'ABC':
        group = [r for r in rows if r['condition']==arm]
        total = {'scheduled':len(group), 'successes':sum(r['success'] for r in group)}
        for key in ('input_tokens','output_tokens','elapsedSeconds'):
            values = [r.get(key) if key=='elapsedSeconds' else (r['usage'] or {}).get(key) for r in group]
            known = [v for v in values if v is not None]
            total[key] = {'total':sum(known) if len(known)==len(group) else None,
                          'observedSubtotal':sum(known) if known else None, 'observedCount':len(known)}
        totals[arm] = total
    effects = {}
    for arm in 'BC':
        delta = totals[arm]['successes']-totals['A']['successes']
        comparable = all(r['status'] not in ('infrastructure-error','environment-error','unsupported','usage-unknown')
                         for r in rows if r['condition'] in ('A',arm))
        effect = {'additionalSuccesses':delta,'comparable':comparable}
        for key in ('input_tokens','output_tokens','elapsedSeconds'):
            a, other = (totals[c][key]['total'] for c in ('A',arm))
            diff = None if a is None or other is None else other-a
            effect[key] = {'difference':diff,'perAdditionalSuccess':diff/delta if comparable and delta>0 and diff is not None else None}
        effects[arm+'-A'] = effect
    pairs = {}
    for row in rows:
        pairs.setdefault(f"{row['task']}/{row['repeat']}",{})[row['condition']] = row['status']
    return {'attempts':rows,'pairedFirstSubmissions':pairs,'allScheduled':totals,'effects':effects}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['stage','collect','score'])
    parser.add_argument('work',type=Path)
    parser.add_argument('--source',type=Path)
    parser.add_argument('--environment',type=Path)
    parser.add_argument('--output',type=Path,help='Fresh directory for external scoring')
    parser.add_argument('--sol',action='store_true',help='Use the separate Sol batch contract')
    args = parser.parse_args()
    plan = read((sol_record if args.sol else scoring_evidence)/'contract.json')
    if args.mode=='stage' and args.source:
        stage(args.work,args.source,plan['participantModel'])
    elif args.mode=='collect':
        with (args.work/'collection.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            collect(args.work,plan)
    elif args.mode=='score' and args.source and args.environment and args.output:
        for attempt in plan['order']:
            run=attempt['id']
            directory=args.work/'attempts'/run
            if not (directory/run/'seal.json').exists() and not (directory/'interrupted.json').exists():
                raise ValueError('Collection incomplete; seal the entire batch before scoring')
        # A different starting tree can type-check and pass behavioral cases. Check all original bytes before grading.
        prior = here.parents[1]/'results/2026-11-18-fixed-input-pilot/baseline.json.gz'
        expected = json.loads(gzip.decompress(prior.read_bytes()))['typecheck']['submittedManifest']
        actual = {}
        for path in args.source.rglob('*'):
            if path.is_symlink() or not (path.is_dir() or path.is_file()):
                raise ValueError('Nonregular baseline entry')
            if path.is_file():
                actual[path.relative_to(args.source).as_posix()] = sha(path)
        if actual != expected:
            raise ValueError('Complete baseline differs from calibration')
        args.output.mkdir(parents=True,exist_ok=False)
        rows = []
        for attempt in plan['order']:
            try:
                row = observe(args.work,args.source,args.environment,plan,attempt,args.output)
            except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
                row = {**attempt,'status':'infrastructure-error','success':False,'elapsedSeconds':None,
                       'usage':None,'error':str(error)}
            if row['status']=='infrastructure-error' and (row['usage'] is None or row['elapsedSeconds'] is None):
                elapsed, usage = observed_cost(args.work,attempt)
                row['elapsedSeconds'], row['usage'] = elapsed, usage
            rows.append(row)
        ids=[r['threadId'] for r in rows if 'threadId' in r]
        for row in rows:
            if 'threadId' in row and ids.count(row['threadId'])>1:
                row.update(status='infrastructure-error', success=False, error='Session reused')
        write(args.output/'summary.json',summarize(rows))
    else:
        parser.error('stage needs --source; score needs --source, --environment and --output')
