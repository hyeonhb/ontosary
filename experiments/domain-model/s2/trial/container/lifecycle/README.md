# Finite container lifecycle fixtures

2026-11-11 follow-up: the finite `linux-evaluation` mode delegates to [the known-submission job helper](../linux-evaluation/). It reuses this manager, independent service, persistent slice, termination checks, collector and cleanup. Its 180-second job/210-second service/240-second outer limits are separate from the original fixture timings. The original normal/timeout/wrapper-loss/supervisor-death/post-publication-failure paths were rerun once each; collector13 and cleanup3 host regressions passed. [New evidence](../../../verification/2026-11-11-linux-evaluation/) preserves all 17 registrations in this round. Production/live dispatch remains refused; the old25-case report below is historical.

The [2026-11-10 result](../../../../../../docs/reviews/2026-11-11-s2-lifecycle-fixture.md) is **fixture-boundary-passed**, awaiting independent review. R11 remains unresolved; these tools do not implement or authorize production collection, Vendure evaluation, model calls, or live trials.

This single Lima/VZ + containerd/nerdctl candidate uses Python/Node standard libraries. The existing parent Dockerfile and pinned base remain unchanged. No installed product dependency or core API was added.

## Responsibilities

- `command.py`: records host UTC/monotonic command durations and enforces the approved round deadlines. Its process-group timeout is not worker termination authority.
- `image.py`: resolves the current native target, hashes OCI manifest/config bytes, derives the rootfs chain, and checks the minimal shell/Node environment.
- `manager.py`: registers manager-owned run IDs, immutable container identities, source/auxiliary directories, persistent systemd slices, admission and guest-received heartbeat timestamps. Only explicit safe recovery opens admission after a blocked run.
- `host_driver.py`: synchronously sends one heartbeat per second. No repeating asynchronous helper survives the host wrapper.
- `supervisor.py` / `common.py`: independent systemd service, outside the worker slice. A holding PID 1 allows a separately observed main process to exit while detached grandchildren remain alive. `ctr tasks exec` preserves its exit status; `nerdctl exec` mapped exit 7 to CLI exit 1 in the observed version. Container creation/inspection still uses nerdctl.
- `collector.py`: after a matching stopped-confirmed record, copies all source/auxiliary ordinary files and directories through no-follow directory descriptors, verifies the copied manifest and delta, and atomically renames manager-only staging.
- `fixture.js` / `probe.py`: finite known workloads and ready-driven fault injection. The probe requires the original `--budget` ledger and refuses a new fixture with less than 60 seconds left before exploration cutoff.
- `audit.py`: separately checks the actual cgroup placement, resource limits, FD/pipe/namespace evidence, permissions, full byte manifests/deltas, classification and recovery outcomes.
- `export.py` / `remove.py`: exports bounded evidence without reading rejected input kinds, then removes only recorded containers, units/slices and the owned image.
- `test_collector.py` / `test_cleanup.py` / `refusal.mjs`: host negative regressions and refusal of a real fixture by existing production/live entry points.
- `freeze.py`: packages and verifies evidence without starting a runtime.

## Bounds and failure behavior

Task deadline: 10 seconds, or 5 for timeout fixtures, fixed just before container start. Heartbeat expiry: 5 seconds measured in the guest clock. Stop confirmation and collection: 10 seconds each. Outer fixture: 60 seconds. The service has `RuntimeMaxSec=40`, `TimeoutStopSec=12`, no restart, `KillMode=control-group` and `KillSignal=SIGKILL`. The last setting is required by the observed supervisor-death regression: waiting for an exec client delayed ExecStopPost and allowed a late write.

The manager closes admission, writes the persistent parent slice's `cgroup.kill`, verifies hierarchical `populated=0`, reconciles the runtime's STOPPED task record, and checks that no creation/start/exec request is pending. The parent inode must still match. A missing parent, uncertain request, failed query/cleanup or collection failure blocks publication and the next run. Unknown runtime requests require discarding the VM; the fixture harness does not infer completion from an empty group alone. The one early parser rejection was reconciled only from its completed pre-dispatch error, absent container and empty parent; that recovery and the original failure remain in the evidence.

Workers use UID/GID 1000, no capabilities, no-new-privileges, private cgroup namespace, read-only cgroup/rootfs, network none, CPU 2 / memory 4 GiB / PIDs 256 and bounded tmpfs. Only that run's source/auxiliary are writable application binds. Root-owned control, runtime socket, previous-run canaries and result paths are not mounted. The small result consumer gets one additional recursive read-only bind; its actual mountinfo and EROFS write refusal are recorded.

Collection rejects symlinks, file hardlinks, FIFOs, devices and sockets before opening them. Limits are 128 regular files, 16 MiB combined regular-file bytes, depth 16 and 1 MiB workload log. A test character device is prepared by the guest manager; workers are not granted mknod capability. Timeout, wrapper loss and nonzero exit produce diagnostic fixture records only. Supervisor/management/collection failures produce no result. Every record has `fixtureOnly:true`, `validSubmission:false`. A result published just before supervisor death is moved to manager-only `quarantined-result` and blocked; consumers require finalized state plus confirmed successful service cleanup. Manual duplicate cleanup cannot open admission before systemd reports service success.

The local regression can be run without a VM:

```sh
python3 experiments/domain-model/s2/trial/container/lifecycle/test_collector.py
python3 experiments/domain-model/s2/trial/container/lifecycle/test_cleanup.py
pnpm check
python3 experiments/domain-model/s2/trial/container/lifecycle/freeze.py --verify experiments/domain-model/s2/verification/2026-11-11-lifecycle-fixture
```

The completed round's VM and owned caches have been removed. Do not interpret these commands or the success classification as authorization to start another runtime round. Further scope and budget follow result review.
