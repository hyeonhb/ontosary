# S2 finite execution lifecycle

This is a fixture runner for the approved 2026-11-17 seal/recovery round.
R11 remains unresolved; production/live dispatch remains refused.
Every result is `fixtureOnly=true`, `validSubmission=false`;
`trialAuthorized=false`, `readyForTrial=false`, `results=null` remain unchanged.
The [latest handoff](../../../../../../docs/reviews/2026-11-17-s2-seal-recovery.md)
records all seven required default-policy fixtures, seven raw Spec/seal replays,
nine stage recovery archives, and confirmed VM disposal. These observations do
not establish CLI native sandbox feasibility or authorize a trial. PR #54 awaits
independent review. The [previous handoff](../../../../../../docs/reviews/2026-11-15-s2-execution-lifecycle-fix.md)
retains the earlier seal/metadata failure without a guest archive.

The three responsibilities are deliberately separate:

- `artifacts.py` owns public, immutable bytes. A manager lock, unique staging
  directory, actual SHA-256/size verification and atomic rename register a file.
  Every hit requires the exact requested manifest and rehashes the file. The
  10 GiB cap includes registered metadata/data and unfinished staging. Corruption,
  symlinks, incomplete registration, conflicting names and changed build inputs
  are rejected. Only pending directories with this round's owner tag may be removed.
- `engine.py` owns each execution record and one stop/remove/collect path. It
  reuses `lifecycle/common.py` cgroup/task confirmation and the no-follow bounded
  collector. `ExecStopPost` closes admission, confirms full stop and settled
  requests, deletes and confirms absence, then collects. A separate guest service
  seals the supervisor's actual inactive timestamp and removes its unit file.
  The host wrapper only supplies heartbeat/observation; killing it cannot become
  the only cleanup mechanism. Uncertain requests/query/removal suppress results
  and require VM disposal; disposal is not a termination receipt.
- `identity.py` verifies registered container, image, slice and bind-source
  identities, records exact JSON substitutions, then compares the entire Spec.
  Unknown fields and extra policy changes remain differences. The historical candidate comparison remains covered by local tests, but actual
  policy-pair execution is refused in this correction round. There is no security-only projection.

`outcome`, `terminationConfirmed`, `removalConfirmed`, `collectionStatus`, service
inactivity and recovery are separate. Failed outcomes never become task success.
A repeated finalizer does not republish a result. Supervisor/collector failure
suppresses or quarantines results. Explicit recovery checks confirmed absence and
preserves the original failure. Runtime query errors are not evidence of absence.

Registration starts the external 120 s clock. Six seconds are reserved for host
transport: the independent guest budget is at most 114 s, with work through
finish−40, removal through finish−10, and collection/sealing through finish.
Payload is at most 15 s. Lock waits and subprocess calls consume those absolute
limits. Host UTC and monotonic use the earlier remaining duration; guest monotonic
is never directly compared with host monotonic. Clock calibration and registration
transport are recorded. Fault injection waits for the manager-observed readiness
and detached-descendant record, rather than an arbitrary sleep.

Runtime commands use absolute executable paths and the exact ordered environment
`HOME=/root`, `LANG=C.UTF-8`,
`PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`.
Preparation checks root-owned, non-worker-writable resolved directories and tools,
versions, `runc features`, AppArmor detection, and every transferred input hash
under the same runtime environment before any container create. Pinned nerdctl
2.4.2 appends a second PATH equal to the fixed PATH plus `:/usr/sbin:/sbin`.
Only this exact hook array and fixed hook commands are accepted. General process
environment duplicates, extra hooks and inherited systemd variables are rejected.
Historical expectation migration records original values separately; security
fields (including AppArmor and recursive read-only mounts) are never rewritten.

Mount normalization accepts only the fixed unique destination set. It verifies
every parent-before-child edge before sorting independent peers; reversing nested
mounts, duplicate/extra destinations and altered mount options are rejected.
Hook order and commands are never sorted or discarded.

## Owned storage and operation

The dedicated host store is
`/Users/hyeon/Library/Caches/ontosary/s2-prepared-v1`, owned by the invoking manager
(uid 501 in this round), directory mode 0700, registered files mode 0400.
Only one fixed Lima 2.3.0 Darwin/arm64 archive, Ubuntu 26.04 arm64 20261016 image,
nerdctl-full 2.4.2 arm64 archive and the public pinned image archive are allowed.
URL, version, platform, expected/actual SHA-256 and bytes, image identity and build
inputs are in the saved manifests. No large artifact is committed to Git.

Lima receives verified **local** archive paths. Its existing shared cache is not
modified or trusted as a hash receipt. The round's VM, extracted tools and disks
live under `/tmp/ontosary-s2-seal-recovery-20261117` and are disposable.
Every source/output/HOME/CLI-state/scratch directory is fresh. No worker mount
exposes the host store, host home, keychain, runtime socket or manager controls.
Prepared archive retention is intentional and distinct from resource leakage.
To retire the store later, stop users of this dedicated store, take its `.lock`,
verify the owner/manifest inventory and remove only its registered digest directories;
never prune the shared Lima/user cache. This round does not automatically retire it.

Run local contracts from the repository root:

```sh
python3 -m unittest discover -s experiments/domain-model/s2/trial/container/execution-lifecycle -p 'test_*.py'
python3 -m unittest discover -s experiments/domain-model/s2/trial/container/lifecycle -p 'test_*.py'
python3 -m unittest discover -s experiments/domain-model/s2/trial/container/single-policy-test -p 'test_retry*.py'
```

`round.py local --work ABSOLUTE_ROUND` records the required gate and exact code
hashes. `enter-preparation` fixes the environment deadline once; `prepare` requires
that gate unchanged. Execute these through `single-policy-test/command.py` with
exact command/args/phase entries in `plan.json`. Preparation uses the same remaining
20-minute deadline for cache verification, extraction, boot, archive import and hash
checks. This round requires cache hits: no download/build/save on a miss. `image_cache.py` hashes canonical `s2-image-input-v1` JSON containing the
base digest, exact Dockerfile/context bytes, build args, platform and tool bundle
versions/digest. Runtime-mounted probes and policies are separate execution hashes.
The actual `prepare` entrypoint looks up this key **before** build/save. A hit
rehashes the stored output and checks its OCI manifest/config/rootfs chain; the
fresh VM then imports it and independently verifies actual image identity.
The legacy preparation path permits one build on a miss; this round sets
`cacheOnly=true` and stops on missing or corrupt inputs. Output SHA/size/identity
are bound separately to the key.
A verified legacy-link record may reference existing immutable output manifests;
old evidence/manifests are never rewritten. Changed recipes invalidate lookup.
Unpinned external apt/npm queries mean new builds are not claimed reproducible.

`round.py fixtures` requests, once each: normal-1, precheck rejection, start failure,
timeout, wrapper death, supervisor death, normal-2 after explicit recovery.
`round.py pair` is refused in this correction round. The optional eighth
destructive runtime-failure fixture is not planned. Local fake-runtime CLI tests are not evidence of actual runtime-error
recovery. No hidden smoke containers are created. Image build is a separate
preparation stage. Failed runtime units are never patched and retried in this round.

`guest.export()` uses `exporter.py` and the shared FD-based collector reader.
Worker originals are never traversed. Only successful, sealed manager results
whose state/termination/removal/manifest bindings verify are eligible; suppressed,
failed, pending, unknown or revoked outcomes get allowlisted manager diagnostics
and an explicit exclusion reason. `DIAGNOSTICS`, `PREPARATION`, and `GLOBAL` list
all diagnostic filenames. No arbitrary file beneath a run is a diagnostic.
Export allows at most 1,024 files and 16 MiB including generated status and the
external index; collector limits remain 128 files/16 MiB. Ancestor symlinks,
hardlinks, special files, unsealed results, replacement/growth, depth, and time
violations are refused before publication. The verified archive/index pair is
published together by atomic directory rename; failures publish no partial pair.


`metadata.py` publishes validated transport bytes through manager-owned temporary
files, mode 0600 and atomic rename; UID/hash/schema/binding are checked across
transfer, import and export. Root-owned diagnostic archives are readable for host
retrieval and never mounted into workers.

`reference.py` starts a manager target with `After=<worker.service>` and a
`BindsTo` relationship to the existing seal observer. It pins InvocationID and
stores raw systemd observations before interpretation. A durable seal or blocked
receipt precedes release; only confirmed release opens the next execution.
`recovery.py` retrieves at preparation and each unit boundary. A failed individual
diagnostic is excluded with a reason; invalid results cannot be partially published.
Metadata and error receipts consume the same cumulative quota. Final retrieval
uses at most 30 seconds and leaves 90 seconds for independent stop/delete/absence
checks. Evidence and cleanup status are separate, including on top-level failure.

Freeze explicit analysis IDs/hashes before closing. Only the planned `cleanup`,
`validate`, `seal` closing commands may be registered; package rejects undeclared
or forged analysis/closing commands. `seal` registers its own snapshot before
atomic packaging; do not wrap it a second time. The final index includes every
saved file and archive member, apart from the index itself. Historical evidence
is immutable. The five failed retry runtime entrypoints now refuse execution and
point to this common lifecycle; their historical execution copies remain archived.

Implementation references:
[Lima v2.3.0 downloader](https://github.com/lima-vm/lima/blob/v2.3.0/pkg/downloader/downloader.go),
[nerdctl v2.4.2 hook creation](https://github.com/containerd/nerdctl/blob/v2.4.2/pkg/cmd/container/create.go),
[systemd v260 service environment](https://github.com/systemd/systemd/blob/v260/man/systemd.exec.xml).

Latest offline replay (no runtime dispatch):

```sh
python3 experiments/domain-model/s2/trial/container/execution-lifecycle/verify_recovery.py --root experiments/domain-model/s2/verification/2026-11-17-seal-recovery
```
