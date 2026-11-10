#!/usr/bin/env python3
"""Bound and record this finite smoke attempt; not a worker lifecycle boundary."""
import argparse, datetime, json, os, pathlib, signal, subprocess, time
p=argparse.ArgumentParser();p.add_argument('--ledger',required=True);p.add_argument('--log',required=True);p.add_argument('--timeout',type=int,required=True);p.add_argument('--finish',action='store_true');p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
lp=pathlib.Path(a.ledger);d=json.loads(lp.read_text());now=datetime.datetime.now(datetime.timezone.utc);start=time.monotonic();limit_seconds=1800 if a.finish else 1200
remaining=min(limit_seconds-(start-d['monotonicAccountingStart']),(datetime.datetime.fromisoformat(d['absoluteDeadline' if a.finish else 'explorationDeadline'])-now).total_seconds())
limit=min(a.timeout,remaining)
if limit<=0:raise SystemExit('Phase deadline reached; no command started')
command=a.command[1:] if a.command[:1]==['--'] else a.command
log=pathlib.Path(a.log);log.parent.mkdir(parents=True,exist_ok=True)
with log.open('xb') as out:
 proc=subprocess.Popen(command,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
 try:code=proc.wait(timeout=limit)
 except subprocess.TimeoutExpired:
  try:os.killpg(proc.pid,signal.SIGKILL)
  except ProcessLookupError:pass
  proc.wait(timeout=5);code=124
entry={'utcStart':now.isoformat(),'monotonicStart':start,'seconds':time.monotonic()-start,'timeoutSeconds':limit,'finishPhase':a.finish,'command':command,'exitCode':code,'log':str(log)}
d=json.loads(lp.read_text());d['events'].append(entry);lp.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(entry));raise SystemExit(code)
