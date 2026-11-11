"""One mechanical correction: journalctl -k, existing windows only; no rerun/attach."""
import datetime,json,pathlib,subprocess
root=pathlib.Path('/opt/ontosary-namespace-diagnosis');rows=[]
for mode in ['baseline','traced']:
 events=[json.loads(l) for l in (root/mode/'audit/events.jsonl').read_text().splitlines()]
 old=next(e for e in events if e.get('command',[None])[0]=='journalctl')
 assert old['exitCode']==1 and "unrecognized option '--kernel'" in old['stderr']
 args=old['command'].copy();args[1]='-k'
 # Original unit windows rounded outward to whole UTC seconds, same exact process/profile filter.
 for key,up in [('--since',False),('--until',True)]:
  idx=args.index(key)+1;t=datetime.datetime.fromisoformat(args[idx])
  if up and t.microsecond:t+=datetime.timedelta(seconds=1)
  args[idx]=t.strftime('%Y-%m-%d %H:%M:%S UTC')
 p=subprocess.run(args,capture_output=True,text=True,timeout=5)
 rows.append({'mode':mode,'originalError':old['stderr'],'command':args,'exitCode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'meaning':'No matches does not prove LSM permission; this does not repeat a worker.'})
(root/'kernel-log-correction.json').write_text(json.dumps({'mechanicalCorrection':1,'reason':'journalctl uses -k/--dmesg, not --kernel','rows':rows},indent=2)+'\n')
print(json.dumps(rows))
