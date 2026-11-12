# Single policy test — bounded preboot stop

2026-11-12 outcome: **inconclusive**. The sole Lima preparation command reached its
450-second bound during the Ubuntu image download. No guest boot, container,
CLI observation or candidate policy application occurred. This command bound
was inherited from the prior helper and was shorter than the approved 20-minute
environment phase; it is not evidence that the full phase would have failed.
The stopped registration, private prefix and exclusively created partial cache
were removed. See the dated review and evidence directory.

The shipped tools cover explicit snapshot scopes, offline exact-policy checks,
preparation/cleanup, bounded command recording and packaging. The tentative
original/candidate runners present in early source snapshots were **never
executed**, and are omitted from this final tree. They are not validated runners.
No shared lifecycle, evaluator or product code changed.

Run offline regressions from the repository root:

```sh
python3 -m unittest discover -s experiments/domain-model/s2/trial/container/single-policy-test -p test_contract.py
```

`scope.verify()` uses the frozen IDs and manifest/archive hashes. Analysis audit
results remain stable when classified closing evidence is added. `verify_index()`
checks every final file and archive member and rejects unknown snapshots.
Historical analysis 11 + closing 1 is recorded without rewriting old evidence.
The final index itself is the external integrity manifest, not self-hashed.

`policy.verify()` checks historical OCI fixtures with the exact approved rule,
including negative tests. It does not establish that a custom profile was applied
in a real container. The pinned containerd source accepts OCI `LinuxSeccomp`
JSON directly; no format conversion was necessary in the proposed plan.

Do not rerun preparation or cleanup as an offline test. Both are round-specific,
owned-resource operations. A new execution needs a reviewed continuation scope
and budget; this stopped round does not grant further policy or model authority.
