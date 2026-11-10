#!/bin/sh
set -eu
# Preparation only: network enabled, no secrets; isolated Linux copy only.
cd /environment
node --version
npm --version
sha256sum package-lock.json
npm ci --ignore-scripts --no-audit --no-fund --workspace=@vendure/admin-ui --workspace=@vendure/common --include-workspace-root
npm run build --workspace=@vendure/common
sha256sum package-lock.json
