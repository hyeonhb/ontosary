#!/usr/bin/env bash
# Assemble one role's inputs in a new directory. No installation or participant execution.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
tool=$(git -C "$here" rev-parse --show-toplevel)
revision=534e6003534f74761e82de1b8c6061cba89945d1
ontosary=35296d436a63f9c72739859c22b1aded4bc9f57a
if [[ $# == 3 && $1 == author ]]; then
    role=author
elif [[ $# == 4 && $1 == agent && -s $4 && -f $4 ]]; then
    role=agent
else
    echo 'Usage: prepare.sh author VENDURE_GIT NEW_DIR | prepare.sh agent VENDURE_GIT NEW_DIR COMPLETED_NOTE' >&2
    exit 2
fi
repo=$2
target=$3
mkdir "$target"
mkdir "$target/vendure"
git -C "$repo" archive "$revision" | tar -xf - -C "$target/vendure"
cp "$here/$role.md" "$target/START.md"
if [[ $role == author ]]; then
    mkdir "$target/ontosary"
    git -C "$tool" archive "$ontosary" -- src package.json pnpm-lock.yaml pnpm-workspace.yaml tsconfig.json LICENSE |
        tar -xf - -C "$target/ontosary"
    cp "$here/tsconfig.app.json" "$target/vendure/packages/admin-ui/ontosary.app.json"
else
    cp "$4" "$target/HANDOFF.md"
fi
