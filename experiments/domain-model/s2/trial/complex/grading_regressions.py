"""Drive offline counterexamples through the holdout's actual observation and cost functions."""
import gzip
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

from holdout import here, observe, read, scoring_evidence, sha, summarize, write

# name, task, patch, expected final status, diagnostic provenance
examples = [
    ('inverted-visibility', 'quantity', 'hidden', 'behavior-failed', None),
    ('direct-throw', 'quantity', 'throw', 'behavior-failed', ('synchronous','submission')),
    ('rxjs-throw', 'refresh', 'rx-throw', 'behavior-failed', ('rxjs','submission')),
    ('rxjs-notification', 'refresh', 'rx-error', 'behavior-failed', ('rxjs','submission')),
    ('unreviewed-operator', 'refresh', 'unsupported-operator', 'unsupported', ('rxjs','unsupported-feature')),
    ('unattributed-seam', 'quantity', 'missing-seam', 'unsupported', ('synchronous','unattributed')),
    ('missing-environment', 'quantity', 'reference', 'environment-error', None),
]


def mock_cost(arm):
    factor = 'ABC'.index(arm)+1
    return {'elapsedSeconds':factor, 'usage':{'input_tokens':factor*10, 'output_tokens':factor+1}}


def regression(name, source, environment, packets, output):
    _,task,patch,status,diagnostic = next(x for x in examples if x[0]==name)
    plan = read(scoring_evidence/'contract.json')
    attempt = next(x for x in plan['order'] if x['condition']=='A' and x['task']==task)
    run = attempt['id']
    with TemporaryDirectory() as tmp:
        work = Path(tmp)
        (work/task).mkdir()
        (work/task/'inputs').symlink_to((packets/task/'inputs').resolve(),target_is_directory=True)
        directory = work/'attempts'/run/run
        directory.mkdir(parents=True)
        answer = here/'evaluator/controls'/f'{task}-{patch}.patch'
        shutil.copyfile(answer,directory/'answer.txt')
        cost = mock_cost('A')
        events = [{'type':'thread.started','thread_id':'synthetic-regression'},
                  {'type':'turn.started'}, {'type':'item.completed','item':{'type':'agent_message','text':answer.read_text()}},
                  {'type':'turn.completed','usage':cost['usage']}]
        (directory/'events.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in events))
        write(directory/'seal.json', {'id':run,'answerSha256':sha(answer),'exitCode':0,'timeout':False,
              'packetSha256':sha(work/task/'inputs/A.txt'),'eventsSha256':sha(directory/'events.jsonl'),
              'elapsedSeconds':cost['elapsedSeconds']})
        if name=='missing-environment':
            environment = Path('/nonexistent/ontosary-grading-regression-env')
        row = observe(work,source,environment,plan,attempt,work/'scored')
        assert row['status']==status and not row['success'] and row['usage']==cost['usage'],row
        shutil.copytree(work/'scored'/run/'submission',output)
    report = json.loads(gzip.decompress((output/'evaluation.json.gz').read_bytes()))
    if status!='environment-error':
        assert report['typecheck']['status']=='passed' and report['sourceBinding']
        cases = report['behavior']['cases']
        if diagnostic:
            errors = [(c,e) for c in cases for e in c.get('errors',[])]
            assert errors and all((e['channel'],e['kind'])==diagnostic and c['status']==e['status'] for c,e in errors),errors
        if name=='inverted-visibility':
            assert [c['name'] for c in cases if c['status']=='failed']==[
                'quantity-and-cancel-controls/available','quantity-and-cancel-controls/exhausted']
        if name=='direct-throw':
            assert len(errors)==3 and all(c['group']=='change' and e['site']['operation']=='throw' for c,e in errors)
        if name in ('rxjs-throw','rxjs-notification'):
            assert report['behavior']['unhandled']
            operation = 'throw' if name=='rxjs-throw' else 'subscriber.error'
            assert all(e['site']['operation']==operation for _,e in errors)
    # Only the counterexample row is graded here. Set the other 17 to a known success to expose
    # the effect of one classified failure on the full scheduled denominator, cost and ratios.
    rows = [row if a==attempt else {**a,**mock_cost(a['condition']),'status':'passed','success':True}
            for a in plan['order']]
    result = summarize(rows)
    for arm in 'ABC':
        total = result['allScheduled'][arm]
        assert total['scheduled']==6 and total['successes']==(5 if arm=='A' else 6)
        assert total['input_tokens']['total']==6*mock_cost(arm)['usage']['input_tokens']
    for arm in 'BC':
        effect = result['effects'][arm+'-A']
        comparable = status=='behavior-failed'
        assert effect['comparable']==comparable and effect['additionalSuccesses']==1
        for key in ('input_tokens','output_tokens','elapsedSeconds'):
            metric = effect[key]
            assert metric['perAdditionalSuccess']==(metric['difference'] if comparable else None)
    write(output/'cost.json', {'fixture':'Synthetic usage and 17 assumed successes; zero participant calls',
          'scoredAttempt':row, 'allScheduled':result['allScheduled'],'effects':result['effects']})
