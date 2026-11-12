#!/usr/bin/env python3
"""Snapshot first, then recompute the single absolute host deadline before dispatch."""
import argparse,json,pathlib
from snapshot import snapshot
from deadline import run
def execute(ledger,log,phase,cmd,timeout=None,category='analysis'):
 lp=pathlib.Path(ledger);identity=snapshot(lp.parent,cmd,phase,category)
 with pathlib.Path(log).open('x') as output:result=run(cmd,json.loads(lp.read_text()),phase,lp.parent/'commands.jsonl',timeout,stdout=output)
 result['snapshot']=identity;d=json.loads(lp.read_text());d['events'].append(result);lp.write_text(json.dumps(d,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ledger',required=True);p.add_argument('--log',required=True);p.add_argument('--phase',required=True);p.add_argument('--timeout',type=float);p.add_argument('--category',choices=['analysis','closing'],default='analysis');p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
 cmd=a.command[1:] if a.command[:1]==['--'] else a.command;r=execute(a.ledger,a.log,a.phase,cmd,a.timeout,a.category);print(json.dumps(r));raise SystemExit(r['exitCode'])
