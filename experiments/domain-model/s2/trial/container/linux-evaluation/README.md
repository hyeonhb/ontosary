# Linux known-submission calibration

2026-11-11: **linux-evaluation-reproduced, awaiting independent review**. See the [handoff](../../../../../../docs/reviews/2026-11-11-s2-linux-evaluation.md) and [dated evidence](../../../verification/2026-11-11-linux-evaluation/). This is an experimental finite adapter. It does not authorize a model call, CLI session, arbitrary agent submission, production receipt or live comparison.

`package.py` verifies and packages the 4,735 inventory files, pinned config/lockfile, required repository contracts and portable TS5.9.3 output. It never copies host dependencies. `prepare.py` uses the unchanged image configuration and `prepare-vendure.sh` inside the owned VM, then runs the original `openEnvironment()` through `open.mjs`. A historical input mismatch produces a diagnostic list and blocks progress; no hashes are refrozen. TypeScript ESM resolution uses an explicit immutable-image symlink, not `NODE_PATH`.

`assemble.mjs` uses the existing `variantDelta` to create four complete roots and their full manifests/submission IDs. `job.mjs` reads a complete root with `readSubmission`, or the explicitly selected delta. It performs the unchanged evaluator and optional public type check. Environment/source/tools are RO binds; only the per-run report and auxiliary directories are RW. The pinned image's `docker-entrypoint.sh` **execs Node**: native initial argv is preserved, and `/proc/self/status` plus `process.pid` verify that the evaluator itself is Node PID1. There is no holding process plus runtime exec.

The existing lifecycle manager has a small `linux-evaluation` branch. `linux_job.py` uses immutable native image/container identity, pending create/start state, a deadline starting immediately before the first create request, the same independent supervisor/lease, persistent slice, `stop_confirm`, collector and systemd cleanup. Limits are job180s, lease5s, termination10s, collection10s, service210s (start5/stop12), outer240s. The original fixture10/5/40/60s settings remain separate. Runtime exit0 and an evaluator `overall:failed` can be a normal baseline calibration. A timeout/OOM/unclear start or failed service cannot supply a normal calibration receipt.

`run.py` fingerprints environment, tools and assembled inputs before/after each final unit; only finalized + successful service cleanup is consumed. `fingerprint.py` rejects environment dependency symlinks escaping that environment. Its sole tools exception is the exact TypeScript link to the immutable image. The collector still accepts at most128 ordinary files/16MiB/depth16 with1MiB logs; source inventories never pass through it. `probes.py` runs the same PID1 entrypoint with a2s timeout/5s delayed writer and a finite no-kill control, then checks clean-next output.

`comparison-policy.json` v2 was frozen before the final seven units. It excludes exactly four wall-time fields and declares the complete-root/delta mode difference. Nine exact macOS common declaration labels are mapped to their historical Program paths, **with matching frozen hashes, uniqueness and collision checks**. Every other field, diagnostic, dependency/build hash, source manifest and trace is compared. The original `evaluation/verify.ts` and six evaluator modules are unchanged. V1 failures and the intermediate third run are preserved separately; the final denominator is seven.

For an authorized repeat, start a new UTC/monotonic ledger and owned prefix, retain the45/90/150/180-minute deadlines, and follow the archived host commands. Do not reuse the closed round's deadlines or treat this README as new execution authorization. The exact executed preparation scripts, initial job code, final guest code and host helpers are in the evidence archives. General sequence:

```sh
pnpm s2:build
python3 experiments/domain-model/s2/trial/container/linux-evaluation/package.py /tmp/ontosary-vendure-preparation-20261108/vendure work/s2-linux-evaluation
# Owned Lima start, copy, prepare.py, setup.py: use archived commands and bounded command.py.
# run.py: baseline/reference first, then repetitions, negatives and explicit reference delta.
python3 experiments/domain-model/s2/trial/container/linux-evaluation/compare.py work/s2-linux-evaluation/validation-units work/s2-linux-evaluation/seven-comparison.json
python3 -m unittest discover -s experiments/domain-model/s2/trial/container/linux-evaluation -p 'test_*.py'
```

`finish.py` verifies final immutable inputs, reuses recorded-resource removal and exports full collected/quarantined reports plus manager records. The native missing-image query returns0/empty in this version; the independent empty image listing is required as well. `host-cleanup.py` stops/deletes only the recorded VM and prefix and removes only newly-created cache leaves after exact URL/hash ownership checks. No shared prune is used. `static.py` verifies the untouched source cache,84 deployment files, model12/16/0 and fixed identities. Costs, failures, archive-member hashes and cleanup proofs are part of the result.

Actual RuntimeMaxSec exhaustion and supervisor death during an ambiguous create remain untested. R11 stays unresolved, R12 retains its previous scope, `trialAuthorized:false`, `readyForTrial:false`, `results:null`; actual CLI/model/provider/trial calls:0. Results await review before any next phase.
