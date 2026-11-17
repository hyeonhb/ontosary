# Direct VM CLI smoke — blocked before payload

The 2026-11-17 one-command smoke observed **`blocked-before-payload`**. The pinned
CLI exited1 with `error building bubblewrap command: Read-only file system
(os error 30)`. No payload marker or output file was produced. VM disposal and
owned-process/root absence were confirmed. See the [report](../../../../../docs/reviews/2026-11-17-s2-vm-cli-smoke.md)
and [indexed host diagnostics](../../verification/2026-11-17-vm-cli-smoke/index.json).

This is a narrow compatibility observation, not a production runner or a verified
submission/termination/isolation protocol. PR #67 remains separate and unmerged.
No policy, permissions, code or CLI candidate was changed after the actual sandbox
attempt; no second sandbox/trace command was run.

`run.py` prepares one owned Lima/VZ VM, runs one OS transient worker service, and
uses a separate host watchdog plus the same owned stop/delete/absence cleanup path.
It adapts the existing `execution-lifecycle/recovery.py` disposal logic while
omitting container export and cache mutation. `bounded.py` limits process groups
and output; the existing absolute-clock helpers bound work. Normal cleanup has
finite safety deadlines independently of an expired experiment clock.

`setup.py` creates UID/GID22002 and immutable config. `worker.py` checks actual
capabilities/NNP, cgroup limits and network namespace/interfaces/routes before
version/help and the sole native sandbox call. `payload.mjs` has only synthetic
source read/write/reread and materials read. There are no credential/socket/proc
negative controls, generated code, model calls or submission exports.

`materialize.py` comes from PR #67 `ed0250b`; provenance records its original hash.
The first local preparation over-rejected OCI `.` directory metadata before VM
creation. The sole correction ignores that normal directory entry; root files,
traversal, links, whiteouts and bounds remain checked. The initial diagnostics and
exact pre-VM patch are preserved. Both preparations share the original60-minute
clock; only the second reached VM creation. No Python or dependency was installed.

Use the already-installed pinned Python3.13 interpreter for reproduction:

```sh
/opt/homebrew/bin/python3.13 -m unittest discover -s experiments/domain-model/s2/trial/vm-cli-smoke -p 'test_*.py' -v
/opt/homebrew/bin/python3.13 experiments/domain-model/s2/trial/vm-cli-smoke/verify.py experiments/domain-model/s2/verification/2026-11-17-vm-cli-smoke
```

These are offline checks. The original round is closed and `execution-started.json`
prevents repeating its command. New runtime work requires a separately reviewed
scope/budget. The error does not identify the failing filesystem path or establish
a namespace/mount syscall failure; no additional trace was authorized or run.

R19's reused host API path was checked with the actual interpreter; the unused
socket defect is not fixed. R11 unresolved, R12 previous scope, production/live
refusal, `fixtureOnly=true`, `validSubmission=false`, `trialAuthorized=false`,
`readyForTrial=false`, `results=null`, and unverified H-O/H-F remain unchanged.
