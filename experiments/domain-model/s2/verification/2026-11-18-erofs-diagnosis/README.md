# Offline EROFS diagnosis evidence

This directory contains read-only provenance/path analysis, not a new VM or CLI
execution. See the [report](../../../../../docs/reviews/2026-11-18-s2-erofs-diagnosis.md).
The leading candidate remains **unconfirmed** without the actual failed syscall.

- `analysis.json`: original observation, reconstructed environments, candidate,
  source-identity checks and historical/current code distinction.
- `package-comparison.json` and `release-package-comparison.json`: registry/archive
  and historical binary comparisons. The 165,822,267-byte npm archive was read for
  analysis only; it was neither installed/executed nor committed.
- Package/registry/tag/attestation JSON: preserved public metadata. The decoded
  attestation is the SLSA provenance statement; the raw response also includes
  npm's publish statement. Signature-chain verification was not performed.
- `source-index.json`: immutable source URLs, Git blob IDs and SHA-256 hashes for
  the 12 relevant files read at `c40729ea5cf8e947481b130c59807273eda2f8e9`.
- `source-excerpts.json`: exact selected lines from those sources, not a buildable
  vendored runtime. They are Apache-2.0 material from OpenAI Codex; the upstream
  LICENSE and NOTICE are retained as `UPSTREAM-LICENSE` and `UPSTREAM-NOTICE`.
  No code within an excerpt was edited; selection and JSON wrapping are ours.
- `pnpm-check.log` and `summary.json`: repository validation and elapsed time.

Original smoke evidence and its freeze are unchanged. The source provenance is a
publisher declaration tied to matching package bytes, not a reproducible-build
proof. The reconstructed helper environment is not a proc-environ measurement.
