# CLI feasibility — blocked before native payload execution

The [2026-11-11 handoff](../../../../../../docs/reviews/2026-11-11-s2-cli-feasibility.md) records **blocked**, awaiting independent review. The pinned CLI starts, but its bubblewrap sandbox cannot create a namespace under the unchanged nonprivileged container policy. Parent file operations succeed; the explicit-profile sandbox payload never starts. This is not a successful deny test or a live runner.

The round used two finite **preparation containers**, ten local non-model CLI invocations (six exit0, four exit1), and zero registered lifecycle jobs. The first `sandbox linux --help` attempt followed current documentation but the pinned CLI accepts `sandbox -- …` instead. The corrected invocation fails with the same namespace error; `unshare` reports EPERM. The actual OCI seccomp policy defaults to ERRNO, omits unshare, masks clone namespace flags and returns ENOSYS for clone3. AppArmor also applies; its independent contribution was not isolated. No privilege, seccomp, sysctl or candidate change was attempted.

`command.py` bounds host preparation/check/cleanup commands against the original UTC and monotonic deadlines. `snapshot.py` archives helpers **before subprocess execution**. `host-prepare.py`/`host-install.py` prepare the same pinned VM/image and record native identity. `discover.mjs` runs seven local commands. `host-diagnose.py`/`diagnose.py`/`diagnose.mjs` perform only the narrow blocker diagnosis with a read-only policy bind and synthetic file. `finish.py`, `host-finish.py` and `host-cleanup.py` verify stopped/absent preparation containers and remove the owned image, VM, prefix and new URL/hash-verified cache leaves. They are not the lifecycle supervisor or submission collector.

The policy is a **partially observed diagnostic input**, not a validated security profile. Named selection and a missing-profile negative control are observed; filesystem enforcement, command environment filtering, instructions/skills/rules isolation, credential parser and actual turn tool inventory are unverified. `--strict-config` is unsupported by `features` in this pinned version. No control/auth state directory is archived. The synthetic marker is not an account or credential.

Native file/auth/network checks, normal2 repeats, timeout/control and lifecycle integration were stopped at the prerequisite failure. Existing lifecycle/evaluator code and timings remain unchanged. Production/live entry points still refuse a real prior fixture receipt; this round issued no new receipt. R11 remains unresolved, trialAuthorized/readyForTrial=false and results=null. Credential transfer, login, refresh, provider requests, model calls and trial runs are each0.

No runtime should be restarted from these scripts without a new reviewed scope and budget. Offline evidence verification:

```sh
python3 experiments/domain-model/s2/trial/container/cli-feasibility/freeze.py --verify experiments/domain-model/s2/verification/2026-11-11-cli-feasibility
```

The [evidence](../../../verification/2026-11-11-cli-feasibility/) includes the first failed call, corrected call, fixed policy, native image/config/container records, bounded logs, exact pre-execution snapshots, cost and cleanup. `pnpm check` (304 tests), S2 build, collector13 and cleanup3 passed. No fresh VM regression set, Vendure7 or product experiment is claimed.
