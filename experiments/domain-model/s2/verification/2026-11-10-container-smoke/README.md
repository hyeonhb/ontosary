# 2026-11-10 container smoke

**smoke-passed, limited to image identity and model-free minimum execution.** [Report](../../../../../docs/reviews/2026-11-10-s2-container-smoke.md), [implementation](../../trial/container/).

`raw/budget.json` contains UTC/monotonic starts, clamped command deadlines, one diagnosed validation correction, prior/current/cumulative time and the early exploration stop. The first clock capture followed the initial instruction read; a conservative extra60seconds is charged and explicitly not presented as a measured start. No deadline was exceeded. Host and guest monotonic clocks are separate clock domains.

`raw/guest/smoke-run-v1` preserves the first **read-only** identity validation failure; no container existed then. In nerdctl2.4.2 Docker-compatible `RootFS.Layers` contains cumulative chain IDs. `raw/09-layer-diagnosis.log` compares config diff IDs, manifest compressed layer digests and native snapshot names. V2 verifies every computed prefix chain ID instead of falsely equating the list with individual diff IDs. Both executed script versions are preserved under `raw/implementation-at-execution`. One corrected harness execution, no image rebuild or workload retry.

`raw/guest/smoke-run-v2` contains commands with arguments/UTC/monotonic durations/exit codes, exact OCI content, native/Docker-compatible image/container metadata, snapshot parents and workload logs. Four fresh container IDs share the recorded target and rootfs chain. `*-wait.stdout` records workload0/7/0/0 while each wait manager command exits0. Start markers are required. The two basic runs verify Node22.19.0, UID/GID1000, cpu.max200000/100000, memory.max4294967296 and pids.max256; status shows CapEff0/NoNewPrivs1. CLI logs preserve version/help and launcher/native executable SHA-256. CLI executes only `--version` and `--help`, with an empty container-local HOME/CODEX_HOME and network none.

Identity is not inferred from a tag or Config.Image string: manager endpoint/namespace is explicit, manifest/config bytes are SHA-256 checked, config diff IDs derive the snapshot chain, each container's actual `Image` target and snapshot parent match, and image target is checked before/after. The same target reference is passed with `--pull=never`. OCI manifest/config stdout bytes are exported unchanged for digest verification. Other files normalize host paths/identities, ANSI and whitespace; original/export hashes are recorded. Private SSH keys and VM/image/archive binaries are excluded.

`raw/ownership.json` records cache absence before preparation. `raw/disk-downloads.json` records URL/hash/allocated size after. Stop/Stopped/delete/empty-list logs plus `raw/cleanup.json` verify removal of the dedicated VM, image, prefix and only the two newly created URL cache entries. No preexisting entry or global cache was pruned. All four containers were removed individually first. This cleanup is not R11 hostile descendant containment.

`raw/14-host-check.log`: host303tests/15files/skip0, typecheck and example build pass. No Linux Vendure/install/build/evaluator, 29-submission calibration, R11 adapter/collection/attack probes, provider/model session or comparison trial was run. R12 semantics and production/live refusal are unchanged. Static model/materials and old evidence remain untouched. No `pnpm experiment` rerun was required for this scope.

`manifest.json` recursively hashes current preparation implementation and this new evidence. Historical feasibility manifests are not rewritten. To re-export and validate already collected evidence without any runtime activity:

```sh
python3 experiments/domain-model/s2/trial/container/freeze-smoke.py \
  work/s2-container-smoke \
  experiments/domain-model/s2/verification/2026-11-10-container-smoke
```

The round is closed. Review the smoke result before deciding scope/budget for R11 lifecycle or Linux Vendure work. `trialAuthorized:false`, `readyForTrial:false`, `results:null`, model/provider/trials0.
