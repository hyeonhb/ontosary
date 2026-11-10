# 2026-11-10 container feasibility evidence

**inconclusive — environment invocation stopped after one correction/retry.** No task container, termination probe, Linux type/behavior evaluation or actual model session ran. Image build's temporary BuildKit steps are preparation, not worker/evaluator tests. [Report](../../../../../docs/reviews/2026-11-10-s2-container-feasibility.md), [preparation sources](../../trial/container/).

`raw/budget.json` preserves UTC stage starts/durations/commands/exit codes and the early stop. Exact initial task time was not captured: 10:50 UTC is a conservative accounting start before the first clock observation at 10:59, not a measured timestamp. Final environment charge includes all preflight; the separate measured preparation interval starts at the first download. Runtime candidates 1, environment correction/retry 1, paid cost 0.

`raw/05-*` and `raw/06-*` preserve both failed preparation invocations. `raw/cli-preflight.log` is empty stdout; its captured fatal stderr/exit 1 is explicitly preserved in `raw/supplementary-commands.json`. Initial repo@manifest resolution tried the registry; the correction used the Docker-compatible inspect config ID, which nerdctl did not resolve. `raw/pre-cleanup-guest.log` subsequently records nerdctl's native image ID as the manifest digest. This is an invocation/identity mix-up, **not evidence that Lima cannot run an isolated CLI**. No second correction was tried.

`raw/node-image*.json`, `raw/worker-image.json`, release/npm metadata, build logs and `raw/input-archives.json` bind the attempted environment. The VM image is Ubuntu 26.04.1 arm64; guest kernel 7.0.0-38; cgroup v2/systemd were observed. The local worker image config digest and manifest digest are separate fields. Linux CLI package availability/build installation is observed; binary hash/version/help/config/shell behavior remains untested.

`raw/guest-preflight.log` and `raw/pre-cleanup-guest.log` retain guest mounts and inventories. No host home bind mount was configured or shown. This is **not** a worker canary or namespace proof. Neither cgroup.kill/empty nor movement denial was tested. The worker image's proposed UID/limits did not get exercised. VM stop/absence proves cleanup of this attempt, not the future per-run stop→collect contract.

`raw/pre-cleanup-host.json` records allocated `du` counts and exact owned cache entries. These are a point-in-time sum, not a unique physical/peak disk measurement (APFS sharing may double count). Lima macOS ignores `XDG_CACHE_HOME` for this downloader; the task removed only the two recorded new entries. `raw/cleanup.json`, stop/delete logs, empty VM list and absent hostagent PID verify no retained VM/image/volume or worker. No global prune or host service/security change occurred.

`raw/verification.json` records host 303 tests/15 files/skip 0, comparison 4/4, S2 build, 18 accounting fixtures equal to historical records, 84 static bundle hashes, 4,735 original source hashes and live/production refusals. **Linux test count is zero.** No historical macOS oracle was counted as Linux success. R11 stays unresolved; R12's verified scope is preserved; trialAuthorized/readyForTrial=false, results=null, model/provider/trials=0.

The manifest recursively covers every file under `trial/container`, including Dockerfile/YAML/Python/shell/README and this evidence tree. It also binds existing S2 TypeScript without modifying the old freeze manifest. `implementation-at-execution/bounded-command.initial.py` preserves the initial helper used for download/start before the deadline/process-group patch. No timeout occurred in either version. The archive snapshot preceded final documentation/export tooling; only the Dockerfile was executed inside BuildKit. `prepare-vendure.sh` never executed.

Logs normalize only host paths/identities, ANSI escapes, line endings and trailing whitespace. `manifest.json` includes original and exported byte hashes; stderr messages, public digests and semantic fields are retained. Raw local logs remain under ignored `work/s2-container-feasibility`; private SSH keys/cloud-init files and downloaded binaries are not committed.

To verify committed artifacts, compare every `manifest.json` implementation/existingImplementation/evidence SHA-256 against the named repository/evidence paths. To re-export reviewed local logs (no runtime activity):

```sh
python3 experiments/domain-model/s2/trial/container/freeze-evidence.py \
  work/s2-container-feasibility \
  experiments/domain-model/s2/verification/2026-11-10-container-feasibility
```

A new runtime attempt needs an explicitly reviewed follow-up budget. Keep the current failed calls as evidence; do not rerun the closed ledger or silently replace failure logs.
