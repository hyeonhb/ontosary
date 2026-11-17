# Single-policy experiment tools

2026-11-14: new execution uses [the common lifecycle](../execution-lifecycle/README.md).
The five `retry-job/guest/install/remove/export.py` entrypoints now refuse runtime
execution. Their original code remains in immutable historical snapshots. The
legacy normalizer remains for historical replay; new executions use the strict
full-Spec comparator with verified ownership and explicit runtime environment.
Snapshot/package now also support exact planned analysis commands and multiple
source directories while retaining the previous callers' defaults. The following
paragraphs describe the historical 2026-11-12 implementation.

The 2026-11-12 retry fixes the two reviewed audit/deadline defects, but its runtime
observation remains **inconclusive**. The original policy reproduced two namespace
clone EPERM calls inside one CLI sandbox invocation. The candidate was created
with exactly the approved seccomp row, but never started: the strict whole-Spec
gate rejected an unlisted supervisor MEMORY_PRESSURE_WATCH path difference.
Termination was confirmed in 0.275s; removal of that stopped candidate took
181.412s, exceeding the 120s unit contract. All owned resources were eventually
removed. This is a blocked diagnostic fixture, not a validated runtime adapter.

`command.py --ledger ... --log ... --phase ... [--category closing] -- COMMAND`
uses explicit round paths. It snapshots before dispatch, then recomputes the
smaller remaining host UTC/monotonic budget. Nested preparation consumes the same
absolute deadline. No inherited 450s/7m/240s caller limits remain. Finite unit and
cleanup limits have separate purposes recorded in the plan. Host process-group
cleanup is not a claim of full agent termination; unchanged lifecycle helpers
check owned worker cgroups, runtime tasks/PIDs and pending requests.

`scope.verify()` uses frozen IDs/hashes. `snapshot()` registers closing IDs/hashes
at creation only for exact planned command/args/phase matches. Analysis snapshots
are refused after freeze. `package.py --work ROUND --out NEW_OUTPUT` requires the
analysis list plus explicit closing registry to equal the actual snapshot set.
It validates before staging, checks again in staging, and publishes once. It
never discovers and assigns extra snapshots to closing, or overwrites an existing
output. Historical 11+1 and 6+6 scopes are reproduced without changing old evidence.
The final index covers all files and archive members except itself.

Run the 31 new tests plus the original 13 regressions from the repository root:

```sh
python3 -m unittest discover -s experiments/domain-model/s2/trial/container/single-policy-test/ -p 'test_retry*.py'
python3 experiments/domain-model/s2/trial/container/single-policy-test/retry-verify.py --root experiments/domain-model/s2/verification/2026-11-12-policy-retry
```

`runtime_policy.py` validates predetermined owned identities and rejects every
other OCI difference. The recorded MEMORY_PRESSURE_WATCH difference remains
rejected; it was not retrospectively allowed. `policy.py` retains strict offline
same-identity fixture comparison. Exact seccomp in a created Spec does not prove
kernel enforcement or clone success in an unstarted container.

`retry-*.py` runtime helpers are finite, round-specific experiment code. Do not
rerun preparation, installation or cleanup as offline tests. The older fixed-path
scripts describe the previous round; they are not continuation entry points.
No shared lifecycle, evaluator, model or product code changed. Any continuation,
new execution boundary, persistent cache/VM, credentials or model connection
requires the next reviewed scope; this result does not automatically retry.
