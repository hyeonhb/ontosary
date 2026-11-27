#!/usr/bin/env bash
# Run from any directory. Each revision gets its own source, hooks and dependencies.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
scratch=$(mktemp -d)
trap 'rm -rf -- "$scratch"' EXIT

run_probe() {
  local revision=$1
  local checkout="$scratch/$revision"
  local test=packages/excalidraw/tests/ontosary-eraser.test.tsx
  mkdir "$checkout"
  curl -fsSL --retry 2 "https://codeload.github.com/excalidraw/excalidraw/tar.gz/$revision" |
    tar xz --strip-components=1 -C "$checkout"
  cp "$here/probe.tsx" "$checkout/$test"
  (
    cd "$checkout"
    git init -q
    npx --yes --package=yarn@1.22.22 -c 'yarn install --frozen-lockfile --non-interactive' > install.log 2>&1 ||
      { tail -30 install.log >&2; exit 1; }
    ./node_modules/.bin/vitest run "$test" | tee "$scratch/$revision.log"
  )
}

before=204e06b77bf7b592e29891160b775df33399ff4d
after=1161f1b8ba860a34602fc4aa211ea9f5b28c30eb
run_probe "$before"
run_probe "$after"
python3 - "$scratch" "$here/observations.json" "$before" "$after" <<'PY'
import json
import sys
from pathlib import Path

logs, baseline, *revisions = sys.argv[1:]
expected = json.loads(Path(baseline).read_text())
for revision in revisions:
    lines = (Path(logs) / (revision + ".log")).read_text().splitlines()
    scenes = [json.loads(line.removeprefix("ERASER_SCENE ")) for line in lines
              if line.startswith("ERASER_SCENE ")]
    if scenes != [expected[revision]]:
        raise SystemExit(f"{revision}: unexpected scene output {scenes}")
    print(revision, scenes[0])
PY
