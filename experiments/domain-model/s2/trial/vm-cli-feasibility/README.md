# Direct VM CLI feasibility — stopped before runtime

The 2026-11-17 round is **inconclusive**. The 15-minute minimum implementation /
cleanup gate was missed. No VM was created and none of the four native CLI units
ran. This directory contains an **unexecuted, disabled draft**, local regression
tests, and a verifier for the stopped record. It is not a usable runtime adapter.

See the [result report](../../../../../docs/reviews/2026-11-17-s2-vm-cli-feasibility.md)
and [indexed evidence](../../verification/2026-11-17-vm-cli-feasibility/index.json).
The elapsed-time budget was not restarted. Later local tests do not retroactively
pass the preparation gate. Independent result review is required before merging.

## What was actually checked

- Four existing public cache archives were rehashed. The OCI manifest/config/chain
  and 11 blobs were checked; nine selected regular files were inspected in place.
  No public binary was materialized, installed in a VM, or executed.
- Local synthetic archive tests exercise selective extraction, traversal, links,
  whiteouts, duplicates, missing files, and the cumulative byte limit.
- Local tests cover deadline refusal, killing a local sleeping process, cleanup
  dispatch after an exception, bounded collector refusal, and disabled entrypoints.
- Stored-record tests reject missing evidence, success promotion, restarted gates,
  altered counters, raw-file tampering, unindexed files, and symlinks.

The stored-record verifier only confirms a consistent **zero-runtime inconclusive
record**. It cannot validate actual argv, service/cgroup identity, sandbox access,
or VM cleanup because those observations do not exist. It deliberately cannot
produce `feasible-for-next-integration`. The draft `checks.py` is not a substitute
for a future verifier that cross-checks those raw observations.

```sh
python3 -m unittest discover -s experiments/domain-model/s2/trial/vm-cli-feasibility -p 'test_*.py' -v
python3 experiments/domain-model/s2/trial/vm-cli-feasibility/verify.py experiments/domain-model/s2/verification/2026-11-17-vm-cli-feasibility
```

These commands perform local offline checks only. `host.py`, `guest.py`,
`worker.py`, and `payload.mjs` refuse execution. `host.execute()` also refuses
before opening a plan or registering resources. No enable flag is provided.
The draft functions are review material, not a supported callable API.

## Unfinished draft and reuse boundaries

The draft sketches a nonprivileged systemd worker, root supervisor, independent
host disposal watchdog, per-unit CLI state, positive-control servers, native
sandbox payload, and termination-before-collection. It imports the existing
deadline, artifact, recovery, and no-follow reader modules without changing them.
Container evidence is explicitly not applicable; no OCI check has been converted
into a passing direct-VM check.

Do not enable this draft by removing its refusal alone. Among the unfinished
items found during handoff:

- The host watchdog calls `limit()` at expiry; its exception can escape before
  disposal. Deadline expiry and disposal must have a tested, unconditional link.
- Result checks do not yet bind raw CLI argv/binary/config hashes and PID/cgroup
  identity. Actual cgroup limits and external-network namespace evidence need
  strict comparisons, beyond requested systemd properties.
- Late-write observation is currently anchored to unit registration rather than
  the actual scheduling event. Root supervisor lifetime/InvocationID retention,
  pending command settlement, and aggregate recovery time need real validation.
- Runtime packaging/plan freezing is unfinished. There is no frozen execution
  command, input bundle, effective guest config, or guest dependency result.
- The default Lima guest has never received these selected public binaries.
  Compatibility, license/provenance packaging, and no-new-package feasibility
  remain open; archive inspection is not installation proof.

Any follow-up needs an independently reviewed scope and a new explicitly recorded
round. The current round must not be resumed with a fresh clock. No production
runner is connected. R11 remains unresolved; R12 retains its previous scope.
`fixtureOnly=true`, `validSubmission=false`, `trialAuthorized=false`,
`readyForTrial=false`, `results=null`; H-O/H-F remain unverified. Real credentials,
login/refresh, provider/model calls, and the comparison remain out of scope.
