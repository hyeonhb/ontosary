import { execFileSync } from 'node:child_process';
for (const key of ['legacy-peer-deps','force','install-links','install-strategy','ignore-scripts']) console.log(key + '=' + execFileSync('npm', ['config','get',key],{encoding:'utf8'}).trim());
