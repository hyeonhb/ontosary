"""Run the frozen smoke worker with a tracer only around its native command."""
import json
import os
from pathlib import Path
import stat

import worker

TARGET = Path("/tmp/codex-daemon-22002")
TRACER = "/opt/s2-smoke/strace"
original_run = worker.run


def snapshot():
    try:
        info = TARGET.lstat()
        target = dict(mode=oct(info.st_mode), uid=info.st_uid, gid=info.st_gid)
    except FileNotFoundError:
        target = None
    paths = ["/tmp", "/scratch", "/source", "/home/worker", "/home/runner/cli-state"]
    mounts = [line for line in Path("/proc/self/mountinfo").read_text().splitlines()
              if line.split()[4] in ["/", *paths, str(TARGET)]]
    return dict(uid=os.geteuid(), cwd=os.getcwd(), tmp=os.path.realpath("/tmp"),
                readOnly=bool(os.statvfs("/tmp").f_flag & os.ST_RDONLY),
                target=target, mountNamespace=os.readlink("/proc/self/ns/mnt"),
                mounts=mounts, entries={p: sorted(os.listdir(p))[:64] for p in paths[1:]})


def observed_run(args, seconds, **kwargs):
    if args[:2] != [worker.CLI, "sandbox"]:
        return original_run(args, seconds, **kwargs)
    before = snapshot()
    # -o directs PID-prefixed trace lines to the bounded stderr pipe. The
    # worker still receives the tracee stdout which contains the payload markers.
    command = [TRACER, "-f", "-qq", "-s", "384", "-o", "/dev/stderr",
               "-e", "trace=%process,mkdir,mkdirat,openat,mount", "--", *args]
    row = original_run(command, seconds, **kwargs)
    row.update(before=before, traceeArgv=args, traceeEnv=kwargs["env"],
               tracerSha256=worker.sha(TRACER))
    return row


worker.run = observed_run
worker.main()
