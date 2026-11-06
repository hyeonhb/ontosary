# Contributing to Ontosary

## Branches and review

Ontosary uses **GitHub Flow**: `main` is the integration branch; each focused change uses a short-lived branch and a pull request. There is no permanent `develop` branch at this stage. Keep changes small enough to review and revert independently. External contributors can work from a fork.

Use lowercase, hyphen-separated branch names: `feat/<topic>`, `fix/<topic>`, `docs/<topic>`, `test/<topic>`, or `chore/<topic>`. Start from current `main` after inspecting local changes and fetching the remote. For dependent work, a branch may temporarily start from another unmerged branch; document that dependency in the handoff/PR and retarget after the base merges. Never overwrite other contributors' work or force-push a shared branch.

Run the relevant regression tests during development and `pnpm check` before completion. Run `pnpm experiment` when analysis behavior or fixtures change. Include the problem, resulting behavior, evidence, tests, and remaining limitations in the PR. Prefer squash merging a focused PR with a Conventional Commit title; preserve separate commits when they represent independently useful changes. Delete merged task branches when no longer needed. A sole maintainer may self-review; do not invent another person's approval.

`main` should accept reviewed, passing changes through PRs. These are project conventions, not a claim that GitHub branch protection or CI has been configured. The maintainer authorized repository delivery on 2026-11-06: after validation, automation should commit, push the task branch, open/review a PR, merge once required checks pass, and sync local main without asking again for each step. Respect branch protections and verify the expected head SHA; do not bypass failing checks. Report self-review accurately. This standing authorization covers repository changes, not package publication or permission changes.

## Commit messages

Use **Conventional Commits 1.0.0**:

```text
<type>[optional scope][!]: <short imperative description>

<why the change is needed and any important constraint>

[optional trailers]
```

Use English, lowercase types and concise imperative subjects, preferably within 72 characters. Use `feat` for new behavior, `fix` for defects, and `docs`, `test`, `refactor`, `perf`, `build`, `ci`, `chore`, or `revert` where appropriate. Scopes should identify a module, such as `logic`, `analyzer`, `fca`, or `cli`. Breaking public contracts require `!` and/or a `BREAKING CHANGE:` footer explaining migration. Bug fixes and their regression tests belong together. Do not claim tests or approvals that did not happen.

Examples:

```text
feat: initialize Ontosary proof of concept
fix(logic): reject unsafe enum receivers and explicit this parameters
docs: record the normalization review findings
```

Before committing, inspect `git status`, the staged diff and `git diff --cached --check`. Stage only the intended change. Do not commit dependencies, builds, scratch files, credentials, or private datasets. Update `docs/PROGRESS.md`; record important decisions in `docs/DECISIONS.md`. Historical review evidence is immutable: add dated follow-up results instead of replacing earlier observations.

## Scope and tests

Read `AGENTS.md`, `docs/PROGRESS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` before implementation. Unsupported syntax must remain explicit. Code facts, discovered candidates, and human-approved knowledge are different categories. A logical difference is not automatically a policy violation.

```sh
pnpm install --frozen-lockfile
pnpm check
pnpm experiment
```

The project uses Apache-2.0; see `LICENSE`. Dependencies retain their own licenses.

## Basis for these choices

Reviewed 2026-11-06. There is no single mandatory open-source branching strategy. GitHub Flow fits this small repository's focused changes and single integration line. Branch prefixes, English subjects, the 72-character preference, and the default squash preference are Ontosary conventions, not requirements of the cited standards.

- [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow): short descriptive branches, focused commits, pull requests and review.
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/): commit type/scope, descriptions and breaking-change notation.
