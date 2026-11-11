#!/usr/bin/env python3
"""Phase-bounded preparation/verification commands; not a termination authority."""
import argparse,datetime,json,os,pathlib,signal,subprocess,time
p=argparse.ArgumentParser();p.add_argument('--ledger',required=True);p.add_argument('--log',required=True);p.add_argument('--phase',choices=['environment','core','exploration','finish'],required=True);p.add_argument('--timeout',type=int,required=True);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
lp=pathlib.Path(a.ledger);d=json.loads(lp.read_text());now=datetime.datetime.now(datetime.timezone.utc);start=time.monotonic();minutes={'environment':45,'core':90,'exploration':150,'finish':180}[a.phase];key=a.phase
limit=min(a.timeout,minutes*60-(start-d['monotonic']),(datetime.datetime.fromisoformat(d['deadlines'][key])-now).total_seconds())
if limit<=0:raise SystemExit('Phase deadline reached; no command started')
cmd=a.command[1:] if a.command[:1]==['--'] else a.command;log=pathlib.Path(a.log);log.parent.mkdir(parents=True,exist_ok=True)
with log.open('xb') as out:
 proc=subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
 try:code=proc.wait(timeout=limit)
 except subprocess.TimeoutExpired:
  try:os.killpg(proc.pid,signal.SIGKILL)
  except ProcessLookupError:pass
  proc.wait(timeout=5);code=124
entry={'utc':now.isoformat(),'monotonic':start,'seconds':time.monotonic()-start,'timeoutSeconds':limit,'phase':a.phase,'command':cmd,'exitCode':code,'log':str(log)}
d=json.loads(lp.read_text());d['events'].append(entry);lp.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(entry));raise SystemExit(code)
