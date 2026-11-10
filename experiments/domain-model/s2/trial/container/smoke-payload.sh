#!/bin/sh
set -eu
# Invoked in a fresh nonprivileged, network-none container; no model session.
case "$1" in
  basic)
    printf 'S2_SMOKE_STARTED\n'
    id
    node -e 'if(process.version!=="v22.19.0" || process.getuid()!==1000 || process.getgid()!==1000) process.exit(9); console.log(JSON.stringify({kind:"fixed-local-smoke",value:42,node:process.version,uid:process.getuid(),gid:process.getgid()}))'
    node -e 'const fs=require("fs"); const read=n=>fs.readFileSync("/sys/fs/cgroup/"+n,"utf8").trim(); const cpu=read("cpu.max").split(" ").map(Number); const limits={cpuMax:read("cpu.max"),memoryMax:read("memory.max"),pidsMax:read("pids.max")}; if(cpu[0]/cpu[1]!==2 || limits.memoryMax!=="4294967296" || limits.pidsMax!=="256") process.exit(10);console.log(JSON.stringify(limits))'
    cat /proc/self/status
    cat /proc/self/mountinfo
    ;;
  exit7)
    printf 'S2_EXIT7_STARTED\n'
    exit 7
    ;;
  cli)
    printf 'S2_CLI_STARTED\n'
    mkdir -p /tmp/smoke-home/codex
    test -z "$(ls -A /tmp/smoke-home/codex)"
    codex --version
    codex --help
    command -v codex
    sha256sum "$(command -v codex)"
    find /usr/local/lib/node_modules/@openai -type f -name codex -exec sha256sum '{}' ';'
    ;;
  *) exit 64 ;;
esac
