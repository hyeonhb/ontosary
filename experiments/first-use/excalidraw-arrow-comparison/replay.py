"""Audit recorded requests without provider access. Optionally re-run blind grading."""
import argparse
import json
from pathlib import Path
from grade import grade
from collect import KEYS, PLAN, LIMIT, packet
from lab import BASE, OUT, REFERENCE, git, sha


def read(path):
    return json.loads(path.read_bytes())


def grade_batch(template, repo, dest):
    # The grader sees only patch bytes and opaque directory names, never the allocation.
    dest.mkdir(parents=True,exist_ok=False)
    patches = {'original':b'', 'reference':git(repo,'diff','--binary',BASE,REFERENCE)}
    patches.update({f.parent.name:f.read_bytes() for f in sorted(OUT.glob('*/first.patch'))})
    for name, data in patches.items():
        patch = dest/(name+'.patch')
        patch.write_bytes(data)
        result = grade(template,patch,dest/(name+'.json'))
        archived = OUT/(name+'.json') if name in ('original','reference') else OUT/'grades'/(name+'.json')
        if archived.exists():
            prior = read(archived)
            for field in ('patchSha256','applied','scenes','probe','lasso','actions','complete'):
                if result.get(field) != prior.get(field):
                    raise ValueError(f'{name}: changed {field}')
        print(name, result.get('actions'), result.get('lasso'),result['complete'],flush=True)


def audit(grades):
    plan = read(PLAN)
    rows = []
    stopped = False
    batch = dict.fromkeys(KEYS,0)
    for slot in plan['slots']:
        d = OUT/slot['id']
        if not d.exists():
            assert stopped
            rows.append({**slot,'stop':'held','submitted':False,'observedUsage':dict.fromkeys(KEYS,0)})
            continue
        assert not stopped
        seal = read(d/'seal.json')
        submissions = 0
        shells = 0
        errors = 0
        history = []
        usage = dict.fromkeys(KEYS,0)
        names = set()
        unknown_model_responses = 0
        turns = [json.loads(line) for line in (d/'trace.jsonl').read_bytes().splitlines()]
        for i, turn in enumerate(turns,1):
            marker = turn['request']
            assert marker['packetSha256']==sha(packet(slot['arm'],history,usage))
            assert all(usage[k]<LIMIT[k] and batch[k]<6*LIMIT[k] for k in ('input_tokens','output_tokens'))
            r = turn['response']
            names.update(r['serverModels'])
            unknown_model_responses += not bool(r['serverModels'])
            if r['usage']:
                assert 0 <= r['usage']['cached_input_tokens'] <= r['usage']['input_tokens']
                assert 0 <= r['usage']['reasoning_output_tokens'] <= r['usage']['output_tokens']
                for k in KEYS:
                    usage[k]+=r['usage'][k]
                    batch[k]+=r['usage'][k]
            try:
                action = json.loads(r['answer'] or '')
            except ValueError:
                action = None
            if 'tool' in r:
                assert action['op']=='shell'
                shells+=1
                errors+=r['tool']['exit']!=0
                history.append({'action':action,'result':r['tool']})
            elif r['answer'] and isinstance(action,dict) and action.get('op')=='submit' and seal['submitted']:
                submissions+=1
                assert i==len(turns)
            else:
                history.append({'answer':r['answer'],'error':'Expected a JSON shell or submit action.'})
        assert submissions==int(seal['submitted']) and usage==seal['observedUsage']
        assert (d/'first.patch').exists()==seal['submitted']
        row = {**slot,**seal,'calls':len(turns),'shells':shells,'shellErrors':errors,
               'serverModels':sorted(names),'responsesWithoutModel':unknown_model_responses,'complete':False}
        if seal['submitted']:
            result = read(grades/(slot['id']+'.json'))
            assert result['patchSha256']==seal['sha256']==sha((d/'first.patch').read_bytes())
            row.update({k:result[k] for k in ('applied','actions','lasso','complete') if k in result})
        rows.append(row)
        stopped = seal['holdRemaining']
    return {'slots':rows,'observedTotal':batch}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--grade',nargs=3,type=Path,metavar=('TEMPLATE','UPSTREAM_GIT','NEW_OUTPUT'))
    p.add_argument('--grades',type=Path,default=OUT/'grades')
    args=p.parse_args()
    grades=args.grades
    if args.grade:
        template,repo,grades=map(Path.resolve,args.grade)
        grade_batch(template,repo,grades)
    print(json.dumps(audit(grades),indent=2))
