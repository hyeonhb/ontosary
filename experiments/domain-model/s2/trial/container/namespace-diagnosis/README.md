# Namespace diagnosis — proposal ready, unapplied

The [2026-11-11 report](../../../../../../docs/reviews/2026-11-11-s2-namespace-diagnosis.md) records **proposal-ready**, awaiting independent review. This means a narrow policy candidate is ready for review, not that it works or is authorized. The [inactive proposal](../../../../../../docs/reviews/2026-11-11-s2-namespace-policy-proposal.md) is Markdown only; no manager/runtime reads it. Original policies, Dockerfile, shared lifecycle, evaluator and product inputs are unchanged.

One owned VM and two preparation containers ran under the original security policy. The untraced baseline reproduced the namespace error. A strace-only diagnostic image retained the original eight filesystem layers and added one package layer. The traced CLI launched bwrap children whose namespace `clone` flags were `0x78020011`; the actual default seccomp clone mask allows only a zero intersection with `0x7e020000`. Both traced namespace clones returned EPERM. Ordinary thread/process clones succeeded. No clone3/unshare/setns call appeared in the captured interval. No other process was attached, and no capability/policy was relaxed.

The exact tagged CLI source agrees with this path, but a reproducible binary build and hash of the executed memfd were not obtained. The packaged CLI/resource hashes match the previous round. AppArmor's independent contribution remains unresolved; a generated profile is not a loaded compiled-policy dump. Kernel log absence is not permission evidence. Namespace entry and all downstream file/auth/network/lifecycle boundary checks remain unsuccessful/unexecuted.

## Preserved tools and limits

- `command.py` and `snapshot.py` enforce the original 10/25/40/50/60-minute round deadlines and snapshot helpers before subprocess execution.
- `host-prepare.py` reuses the pinned Lima/VZ preparation. `host-install.py` transfers only fixed helpers/config/input and runs `guest.py`.
- `guest.py` builds the original and strace-only images and creates at most two units, each with a pre-execution command/hash/expectation record, payload15 seconds and external120 seconds. `probe.mjs` invokes local version/sandbox commands only. State/auth directories are never exported.
- `metadata.py` reads selected kernel configuration, named loaded profile and generated default profile. `log-correction.py` corrects the initial unsupported `journalctl --kernel` query to `-k` over the same unit windows. The original guest helper deliberately remains the executed historical version; its failed queries and the separate correction are both preserved. This is a closed-round diagnostic record, not a supported runner.
- `finish.py`/host cleanup verify container/task/cgroup/image absence before removing the VM and only newly-owned URL/hash-matched cache leaves. Natural exits are not a new lifecycle termination guarantee.
- `audit.py` compares the real inputs, archived native policy, identity, syscall flags and unchanged inputs. `test_audit.py` rejects wrong archive/member hashes and changed namespace/NNP policy. `freeze.py` verifies the published evidence files and archive members without starting a runtime.

The new tools use standard libraries; only the disposable diagnostic image installed Debian strace6.1-0.1. Its package declares LGPL-2.1-or-later for strace (GPL-2.0-or-later for its test suite); the actual copyright and binary hash are in the raw result. No project dependency was added. Non-model CLI calls4, direct bwrap version calls2, strace version1 and traced CLI invocation1 are separate counts. Runtime retries0; one mechanical log-query correction. Policy changes, actual credentials/login/refresh/provider/model/trial calls are each0.

Offline evidence check:

```sh
python3 experiments/domain-model/s2/trial/container/namespace-diagnosis/freeze.py --verify experiments/domain-model/s2/verification/2026-11-11-namespace-diagnosis
```

`pnpm check`304 and five real-evidence validation tests passed. S2 build, prior Python suites, Vendure and product experiments were not repeated because their implementation is unchanged. Further runtime work requires a separately reviewed scope and budget. R11 unresolved; trialAuthorized/readyForTrial=false; results=null; production/live refusal unchanged.
