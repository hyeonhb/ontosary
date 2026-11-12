# S2 감사·시간 제한 보완과 단일 정책 재시도 — 2026-11-12

**보완 구현은 검증 완료, 시험 관찰은 blocked/inconclusive, 소유 자원 정리는 완료**다. 원래 정책에서 namespace clone EPERM을 재현했다. 후보는 실제 OCI seccomp에 정확한 한 행만 추가된 채 생성됐지만, 시작 전 전체 Spec 검사가 사전 허용 목록에 없는 감독자 경로 차이를 거부했다. 후보 실행/커널 정책 적용은0회이므로 정책 효과를 판정하지 않는다. 또 실패 후보 container 삭제가 생성 후181.412초에 이뤄져120초 계약을 넘겼다. 이 계약 위반을 별도 blocked 사유로 남긴다.

## 기준·계획·두 보완

[지시](2026-11-12-s2-policy-retry-instructions.md)의 기준은 `5d723b4`(PR #50), 실제 시작 head는 `d411944`(PR #51)다. 차이는 지시·맥락 문서6개뿐이며 사용자 변경은 없었다. 첫 시계는 UTC `2026-11-12T07:12:41.321458+00:00`, host monotonic `163729.284997333`이다. 10분 마감 전에 실행 계획과 두 보완19테스트·정책8테스트를 확인했다. 보완19테스트가 통과한 뒤에만 유일한 VM을 시작했다.

[도구](../../experiments/domain-model/s2/trial/container/single-policy-test/README.md)는 기존 `single-policy-test/`의 작은 함수/명시적 인자를 재사용한다. 과거 보고·원시 증거·scope/index를 덮어쓰지 않았다. 직전 보고의 “미분류 snapshot 거부 완료” 표현은 불충분했다. 과거 package가 분석 밖 snapshot을 closing으로 자동 편입하던 결함을 이번에 수정했다.

1. **closing 등록과 포장:** 계획에 정확한 command 배열·args·phase를 고정하고, 해당 종료 명령의 snapshot 생성 시 ID·manifest/archive hash를 등록한다. 분석 목록과 등록부의 합집합이 실제 snapshot 집합과 일치해야 한다. 누락·미등록·중복·분석/closing 중복·명령/단계/hash 차이를 거부한다. 포장에서 사후 분류하지 않으며, 검증 후 임시 staging을 만들고 재검증한 뒤 한 번만 공개한다. 기존 출력에는 쓰지 않는다. 부정 테스트는 실제 `package.py` CLI를 호출하고 실패 시 출력과 staging이 남지 않는지도 확인한다.
2. **단일 환경 마감:** wrapper·다운로드·압축 해제·Lima가 같은 최초20분의 UTC/host monotonic 절대 마감을 사용한다. snapshot·선행 단계 이후 남은 시간을 다시 계산해 두 시계의 작은 값을 적용한다. `450초/7분/240초`를 재사용하지 않았다. [Lima v2.3.0 구현](https://github.com/lima-vm/lima/blob/v2.3.0/pkg/instance/start.go)의 `--timeout`은 host-agent 실행 상태를 기다리는 구간이며 이미지 준비 전체의 상한이 아니다. 따라서 외부 host deadline이 다운로드부터 준비 완료까지 묶는다. VM 내부 monotonic은 호스트 시계와 비교하지 않았다.

실제 포장 부정 사례는 미등록 snapshot, 허용 밖 runtime 명령의 등록, 같은 executable/다른 args, 다른 phase, 중복·교차 중복, 누락·변조, closing 변조/누락, 기존 출력 보존을 포함한다. 실제 과거11+close1과6+closing6은 별도 설명 메타데이터로 재현한다. 가짜 시계와 짧은 subprocess는450초보다 긴 잔여 허용, 선행 작업·snapshot 시간 차감, 예산 재시작 방지, 만료 시 dispatch 거부, 더 이른 시계, timeout 종료 요청·실패 ledger/정리 전환을 확인한다. 첫 테스트에서 절대 경로 archive 이름 처리 문제가 발견되어 상대 archive 경로로 수정했고 최종 통과했다. runtime 재시도와 구분한다.

## 실제 시간 제한과 관찰

환경 마감은 `07:32:41.321458 UTC`였다. 준비 wrapper는 요청 상한을 새로 만들지 않았고, 유효 잔여1006.509초에서 시작해538.536초에 끝났다. Lima 단계는 선행 다운로드/해제 뒤1003.852초를 받았고 `--timeout=1004s`를 사용했지만 외부 실효 상한은1003.852초였다. 준비 완료 시467.974초가 남았다. 과거450초를 넘어 Ubuntu 다운로드·부팅이 완료됐다. 이후 이미지 build/원래 정책 실행/후보 사전 검사 명령은 환경 잔여418.035초 중39.161초를 사용했다. deadline과 요청/유효 제한·남은 시간·종료 이유는 `host/budget.json`, `commands.jsonl`, `preparation-commands.jsonl`, `install-commands.jsonl`에 남겼다.

별도 짧은 제한은 계획에 목적을 명시했다: 로컬 회귀30초, create/inspect3초, 단위 wait25초, payload15초, 독립 service95초/단위 외부120초, 개별 정리 명령30초다. host 준비 process group 종료를 실제 agent 전체 종료 보장으로 승격하지 않는다.

| 항목 | 원래 정책 | 후보 정책 |
| --- | --- | --- |
| container 생성 / 실제 시작 | 1 / 1 | 1 / 0 |
| 실제 seccomp | runtime 기본 | 기본 전체 + 승인한 clone EQ/ALLOW 한 행 |
| 같은 image/trace/합성 입력·명령 | 실제 실행 확인 | 생성 Spec·전달 입력으로 확인, 실행은 없음 |
| parent source 읽기·쓰기/자료 읽기 | 모두 성공 | 미실행 |
| namespace clone `0x78020011` | PID41·42에서 각각 EPERM | 미관찰 |
| 합성 payload | 미시작 | 미시작 |
| 전체 종료·container 부재 후 결과 수집 | 1.722초 내 확인 | worker 결과 없음, manager 사전 검사 기록만 보존 |

VM1개, 생성 container2개, 시작1개다. 비모델 CLI2회(version1·sandbox1), bwrap version1회, strace version1회·추적 CLI1회다. 한 sandbox 호출 안의 두 bwrap를 독립 시험2회로 합산하지 않는다. 내부 사전 점검(`/usr/bin/true`)과 실제 Node 명령 준비가 원시 exec/clone trace에 구분돼 있다. credential 전달·로그인·갱신·provider·model·본 비교는 각각0회다. 실행 전 기계적 재시도·후보 재시작도0회다.

이미지는 `sha256:f7b57733f88d06c56188105e4858e37dd99e18694c70f91b39cf3c240de97534`, config는 `sha256:e7298f32b244211e6d3c59a09234f50c874400af8cf00bb8bf3a259cff92a1a2`다. 저장 manifest/config/rootfs chain과 native Spec을 대조한다. CLI0.167.0-alpha.3.2·Node22.19.0 및 CLI/bwrap hash는 이전 값과 일치했다. Linux7.0.0-38-generic·containerd2.4.2의 고정 revision·nerdctl2.4.2, AppArmor `nerdctl-default (enforce)`를 관측했다. worker network none, UID/GID1000, capability0, NNP1, RO root/cgroup, CPU2·4GiB·PID256·tmp64MiB와 기존 권한 config를 유지했다.

## 후보의 시작 전 차단과 계약 한계

후보 profile은 관리자 소유0400이고 container 한 개에만 전달했다. 실제 native seccomp는 default/architecture/기존 규칙을 모두 보존하고 다음 한 행만 추가했다.

```json
{"names":["clone"],"action":"SCMP_ACT_ALLOW","args":[{"index":0,"op":"SCMP_CMP_EQ","value":2013397009}]}
```

그러나 전체 Spec의 `hooks.createRuntime[0].env[6]`와 `hooks.poststop[0].env[6]`에 있는 `MEMORY_PRESSURE_WATCH=/sys/fs/cgroup/system.slice/ontosary-fixture-<runId>.service/memory.pressure`가 달랐다. 두 값은 원래/후보 감독자의 서로 다른 소유 경로를 가리킨다. 사전 고정한 hook 환경 치환 목록에는 이 항목이 없었으므로 비교기는 차이를 숨기지 않고 실패했다. worker 환경·seccomp 규칙의 추가 차이는 발견되지 않았지만 이를 사후 허용하거나 새 실행으로 이어가지 않았다. 후보 profile의 **created Spec 할당1회와 시작/커널 적용0회**를 구분한다.

독립 ExecStopPost는 실패 후보를0.275초에 stopped-confirmed로 기록했고, cgroup populated=0/members=[], runtime Running=false/Pid=0, pending=false를 확인했다. 후보에는 실제 task가 시작되지 않았다. 하지만 상위 실패 경로가 즉시 container 삭제까지 이어지지 않아, 원인 확인 후 정리 명령에서181.412초에 삭제됐다. 따라서 **120초 외부 계약 미충족**이며 전체 단위/lifecycle 성공으로 표현하지 않는다. 원래 단위는1.722초 안에 삭제·수집을 마쳤다. 정리 기록의 원래 단위183.208초 값은 이후 부재 재확인 시점이며 최초 삭제 시간이 아니다.

현재 차단 사유는 미허용 hook 경로의 시작 전 거부와 실패 container 삭제 지연이다. 후보 clone이 여전히 거부됐거나 첫 clone을 통과했다고 판정할 근거는 없다. 추가 syscall/flags·trace·AppArmor/sysctl/NNP·capability 변경, 다른 후보/API/proxy와 실제 인증 연결을 하지 않았다.

## 증거·검증·정리·비용

[분석 감사](../../experiments/domain-model/s2/verification/2026-11-12-policy-retry/host/audit.json), [분석/closing 범위](../../experiments/domain-model/s2/verification/2026-11-12-policy-retry/snapshot-scope.json), [전체 index](../../experiments/domain-model/s2/verification/2026-11-12-policy-retry/index.json), [게스트 원시 archive](../../experiments/domain-model/s2/verification/2026-11-12-policy-retry/host/guest-evidence.tar.gz), [정리](../../experiments/domain-model/s2/verification/2026-11-12-policy-retry/host/host-cleanup.json)를 보존했다. 이번 분석8개를 동결했고 이후 종료 검사는 명시적 closing 등록부에서만 받아들인다. 분석 동결 뒤 runtime 실행은 없었다. 정리는 분석 동결 전에 수행되어 분석 목록에 포함된다. 최초 테스트 실패와 수정 후 통과도 각각 남겼다.

`pnpm check`304테스트·타입 검사·예제 build, 최종 Python44회귀(새31+기존13), 저장 증거의 분석 재현/전체 index·archive 내부 검사, 문서 링크·변경 범위 검사를 통과했다. 기존 S2 입력·증거2,385파일의 최초 hash가 유지된다. 제품/평가기/모델/B/C/배포 ID/공유 lifecycle에는 변경이 없다. TS/평가 의미가 바뀌지 않아 S2 build·Vendure7·pnpm experiment 전체를 반복하지 않았다.

소유 container/task/cgroup·systemd 단위·image·전용 profile·VM·전용 설치 경로를 제거했다. 신규 Ubuntu940,373,504바이트와 nerdctl270,513,423바이트 cache는 URL/data hash를 확인한 뒤 제거했으며, 기존 Vendure cache를 보존했다. 잔여 소유 프로세스/VM/container/task는 없다. VM 삭제를 worker 종료 증명의 대체물로 사용하지 않았다.

회차 측정 **1678.268초**, 이전 누적 측정12602.02857974998초, 새 누적 측정 **14280.297초**다. 이전 최종 직렬화 상한5초와 이번 최종 직렬화 상한5초는 측정값과 별도로 누적 상한에 포함한다. 읽기·조사·구현·대기·실패·검증·정리·보고를 최초 시계부터 계산했고45분 안에 종료했다. 유료 비용0, Git 게시/PR/merge는 종료 후 별도다. [비용](../../experiments/domain-model/s2/verification/2026-11-12-policy-retry/host/cost.json)을 참조한다.

다음은 이 부분 결과와 추가 투자 가치의 리뷰다. 같은 후보의 경로 치환 미세 조정·재시도를 자동 반복하지 않는다. 계속하려면 사전 identity 계약과 실패 시120초 내 제거 경로를 함께 검토해야 하며, 실행 경계/환경 운영 방식을 바꾸는 선택도 사용자와 별도로 결정한다. 새 구조·영구 cache/VM·권한 확대·실제 모델/본 비교 승인은 아니다. R11 unresolved·R12 기존 범위·production/live 거부·fixtureOnly=true/validSubmission=false·trialAuthorized/readyForTrial=false·results=null을 유지한다.
