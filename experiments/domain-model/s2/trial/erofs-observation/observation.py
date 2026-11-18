"""One owned VM, one traced baseline, one evidence-dependent comparison."""
import datetime
import json
from pathlib import Path
import re
import sys
import tarfile
import time

HERE = Path(__file__).resolve().parent
SMOKE = HERE.parent / "vm-cli-smoke"
sys.path.insert(0, str(SMOKE))
import run as smoke

HISTORY = HERE.parents[1] / "verification/2026-11-17-vm-cli-smoke/prepared"
TRACER_HASH = "0e69fa123b3d9732645ce1ac8c89819d100f83cdc9e52a80565d9ad8e7d8cf28"
LAYER = "4e203379e5699e33cd53d9fba002d751f454446b4aee88e8418df913e033fa41"
TARGET = "/tmp/codex-daemon-22002"


def confirming_pid(trace):
    helpers = set()
    pending = set()
    for line in trace.splitlines():
        new_exec = re.match(r'^(\d+)\s+execve(?:at)?\(', line)
        if new_exec:
            pid = new_exec[1]
            helpers.discard(pid)
            pending.discard(pid)
            is_helper = re.match(r'^\d+\s+execve\("[^"]+", \["codex-linux-sandbox"', line)
            if is_helper and line.endswith("<unfinished ...>"):
                pending.add(pid)
            elif is_helper and re.search(r'= 0$', line):
                helpers.add(pid)
            continue
        resumed = re.match(r'^(\d+)\s+<\.\.\. execve resumed>', line)
        if resumed and resumed[1] in pending:
            pending.remove(resumed[1])
            if re.search(r'= 0$', line):
                helpers.add(resumed[1])
            continue
        mkdir = re.fullmatch(r'(\d+)\s+(?:mkdir\(|mkdirat\(AT_FDCWD, )"'
                             + re.escape(TARGET) + r'", 0700\)\s+= -1 EROFS \(Read-only file system\)', line)
        if mkdir and mkdir[1] in helpers:
            return int(mkdir[1])
    return None


def eligible(outer, worker):
    n = worker.get("native", {})
    state = n.get("before", {})
    return (not outer["truncated"] and not outer["timedOut"] and outer["exitCode"] == 0
            and n.get("exitCode") == 1 and not n["timedOut"] and not n["truncated"]
            and worker.get("configUnchanged") and not worker.get("error")
            and n["stdout"] == "" and worker.get("outputContent") is None
            and state.get("tmp") == "/tmp" and state.get("uid") == 22002
            and state.get("readOnly") and state["target"] is None
            and "error building bubblewrap command: Read-only file system (os error 30)" in n["stderr"]
            and confirming_pid(n["stderr"]) is not None)


class Observation(smoke.Smoke):
    def extra_bundle_files(self):
        return {"strace": self.w / "strace", **{p: HERE / p for p in
                ("observe_worker.py", "prepare_directory.py")}}

    def unit(self, label, args):
        outer = self.guest(args, timeout=110, check=False)
        smoke.write(self.w / (label + "-outer.json"), outer)
        worker = json.loads(outer["stdout"]) if outer["exitCode"] == 0 and not (
            outer["timedOut"] or outer["truncated"]) else {}
        smoke.write(self.w / (label + "-worker.json"), worker)
        return outer, worker

    def run_units(self, args):
        args = [*args[:-1], "/opt/s2-smoke/observe_worker.py"]
        outer, worker = self.unit("baseline", args)
        if not eligible(outer, worker):
            return {"observation": "baseline-unconfirmed", "comparisonDispatched": False}
        prepared = self.guest(["python3", "/opt/s2-smoke/prepare_directory.py"], timeout=5)
        smoke.write(self.w / "directory.json", json.loads(prepared["stdout"]))
        outer, worker = self.unit("comparison", args)
        return {"observation": "daemon-mkdir-erofs", "comparisonDispatched": True,
                "comparisonPayload": smoke.verdict(worker, outer)}


def stage(work):
    work.mkdir(mode=0o700, parents=True, exist_ok=False)
    root = Path("/private/tmp/ontosary-s2-erofs-observation")
    if root.exists() or root.is_symlink():
        raise ValueError("VM root already exists")
    for name in ["worker-plan.json", "config.toml", "cache-inputs.json"]:
        (work / name).write_bytes((HISTORY / name).read_bytes())
    plan = smoke.read(HISTORY / "plan.json")
    plan.update(root=str(root), name="ontosary-s2-erofs-observation",
                diagnosticRoot=str(work), maximumSandboxCalls=2, maximumCliDiscovery=4)
    smoke.write(work / "plan.json", plan)
    record = next(x for x in smoke.read(work / "cache-inputs.json")
                  if x["request"]["name"] == "ontosary-fixed-trace-image")
    end = time.monotonic() + 60
    with tarfile.open(record["path"]) as archive:
        layer = archive.extractfile("blobs/sha256/" + LAYER)
        with tarfile.open(fileobj=layer, mode="r|gz") as members:
            for member in members:
                if time.monotonic() >= end:
                    raise TimeoutError("tracer extraction")
                if member.name.removeprefix("./") == "usr/bin/strace" and member.isfile():
                    if member.size != 1640712:
                        raise ValueError("unexpected tracer size")
                    (work / "strace").write_bytes(members.extractfile(member).read(member.size))
                    break
    if smoke.sha(work / "strace") != TRACER_HASH:
        raise ValueError("unexpected tracer hash")
    (work / "strace").chmod(0o555)
    now = datetime.datetime.now(datetime.timezone.utc)
    deadlines = {k: {"utc": (now + datetime.timedelta(seconds=v)).isoformat(),
                     "monotonic": time.monotonic() + v} for k, v in
                 [("experiment", 1800), ("finish", 2100)]}
    smoke.write(work / "budget.json", {"deadlines": deadlines})
    paths = list(HERE.glob("*.py")) + [SMOKE / name for name in
             ["run.py", "bounded.py", "worker.py", "setup.py", "payload.mjs", "materialize.py"]]
    smoke.write(work / "freeze.json", {"codeHashes": {str(p): smoke.sha(p) for p in paths},
                "inputHashes": {n: smoke.sha(work / n) for n in
                ["strace", "plan.json", "budget.json", "worker-plan.json", "config.toml", "cache-inputs.json"]}})


if __name__ == "__main__":
    work = Path(sys.argv[1]).resolve()
    stage(work)
    # The smoke gate reads this receipt before dispatch.
    import subprocess
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(HERE)],
                   check=True, timeout=30)
    smoke.write(work / "local-gate.json", {"passed": True})
    smoke.execute(Observation(work))
