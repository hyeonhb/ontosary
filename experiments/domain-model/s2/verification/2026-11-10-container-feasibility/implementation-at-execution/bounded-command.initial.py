#!/usr/bin/env python3
"""Record bounded, model-free preparation commands; never invoke live trials."""
import argparse, datetime, json, pathlib, subprocess, time
p = argparse.ArgumentParser()
p.add_argument('--ledger', required=True)
p.add_argument('--log', required=True)
p.add_argument('--environment', action='store_true')
p.add_argument('--timeout', type=int, required=True)
p.add_argument('command', nargs=argparse.REMAINDER)
a = p.parse_args()
ledger_path = pathlib.Path(a.ledger)
ledger = json.loads(ledger_path.read_text())
now = datetime.datetime.now(datetime.timezone.utc)
remaining = (datetime.datetime.fromisoformat(ledger['explorationDeadline']) - now).total_seconds()
if a.environment:
    remaining = min(remaining, ledger['environmentLimitSeconds'] - ledger['environmentSeconds'])
limit = min(a.timeout, int(remaining))
if limit <= 0:
    raise SystemExit('Budget exhausted; no command started')
command = a.command[1:] if a.command[:1] == ['--'] else a.command
log = pathlib.Path(a.log)
log.parent.mkdir(parents=True, exist_ok=True)
start = time.monotonic()
with log.open('wb') as out:
    try:
        result = subprocess.run(command, stdout=out, stderr=subprocess.STDOUT, timeout=limit)
        code = result.returncode
    except subprocess.TimeoutExpired:
        code = 124
elapsed = time.monotonic() - start
if a.environment:
    ledger['environmentSeconds'] += elapsed
ledger['events'].append(dict(start=now.isoformat(), seconds=elapsed, environment=a.environment,
    command=command, exitCode=code, log=str(log), timeoutSeconds=limit))
ledger_path.write_text(json.dumps(ledger, indent=2) + '\n')
print(json.dumps(ledger['events'][-1]))
raise SystemExit(code)
