# S2 namespace 정책 진단 개발 지시 — 2026-11-11

## 목표와 승인 범위

동일 Lima/VZ + containerd/nerdctl 후보에서 Codex native sandbox의 namespace 생성이 막히는 원인을 좁히고, **적용하지 않은 최소 정책 변경안**을 제시한다. 새 회차의 총 상한은60분이다. 실제 정책 변경, 실제 자격 증명 전달, 로그인/갱신, provider·모델 호출과 본 비교는 결과 리뷰 뒤 별도로 결정한다.

최종 목적은 S2에서 변경 전 도메인 모델이 agent 수정 작업에 도움이 되는지 확인하는 것이다. 이번 진단은 그 실험을 계속할 가치가 있는지 판단할 근거를 만드는 작업이며 범용 sandbox/runner 개발이 아니다. 권한 완화 없이 원인을 완전히 분리할 수 없다면 관찰·정책상 차단 근거·추정·미확인을 나눠 인계한다. 성공 실행을 만들기 위해 범위를 확대하지 않는다.

## 시작점과 직전 독립 리뷰

최초 작업 명령에서 UTC와 host monotonic을 기록하고 AGENTS, PROGRESS, ARCHITECTURE, ROADMAP, CONTRIBUTING을 읽는다. 원격/브랜치/사용자 변경을 확인한다. 이 지시의 코드·증거 기준은 main `bbb43c9`(PR #46)이다. 지시 문서 병합 이후의 실제 시작 head와 차이를 기록하고, 제품/실험 코드가 달라졌으면 영향부터 확인한다.

- [직전 결과](2026-11-11-s2-cli-feasibility.md), [직전 지시](2026-11-11-s2-cli-feasibility-instructions.md), [구현/재현 안내](../../experiments/domain-model/s2/trial/container/cli-feasibility/README.md)를 먼저 확인한다.
- 독립 리뷰는 blocked 판정에 동의했다. 증거68파일·20archive 무결성, pnpm check304테스트, S2 build와 collector13/cleanup3 회귀를 확인했다. 새 VM에서 재실행한 리뷰는 아니다.
- 첫 sandbox 호출은 고정 버전과 문법이 맞지 않았지만 수정한 `codex sandbox -P fixture -C /source -- …`도 namespace 오류로 실패했다. 별도 `unshare --user --map-root-user -- /bin/true`도 EPERM이었다. parent source/material 작업은 성공했고 native payload는0회 시작했다.
- 실제 OCI는 seccomp default ERRNO·unshare 허용 없음, clone namespace flags 제한·clone3 ENOSYS다. proc는 Seccomp2·NNP1·capability0, userns sysctl1/max21089, AppArmor userns 제한1/nerdctl-default를 기록했다. bwrap의 첫 실패 syscall과 AppArmor의 독립 기여는 아직 모른다.
- 직전 보고서29행의 “전체 사용자 config를 읽지 않았다”는 표현은 부정확하다. auth-metadata.py는 전체 TOML을 파싱하고 허용한 값만 기록한다. 새 보고서에서 이를 정정하고, 실제 auth 파일 내용은 읽지 않았다는 사실과 구분한다. 과거 보고/원시 증거는 덮어쓰지 않는다. 이번에는 호스트 인증 조사 자체를 반복할 필요가 없다.

기존 lifecycle fixture와 Linux baseline/reference 재현 결과는 유지한다. R11 unresolved·R12 기존 검증 범위·production/live 거부·trialAuthorized/readyForTrial=false·results=null을 유지하고 모델/B/C·평가기·배포 ID를 바꾸지 않는다.

## 시간과 재시도 계약

읽기·자료 조사·환경 준비·다운로드/대기·코드 작성·실패/재시도·검사·정리·보고를 최초 시계부터 같은60분에 포함한다. 이전 회차의 남은 시간을 재개하거나 실패 뒤 시계를 초기화하지 않는다. 신규 유료 비용은0이다. 실제 소요와 이전 누적10040.202초를 분리하고 새 누적을 기록한다. Git 게시/PR/merge 시간은 별도 기록한다.

| 경과 | 해야 할 일과 중단 판단 |
| --- | --- |
| 0~10분 | 기존 증거/정책/고정 버전 검토, 가설표 작성, 새 동적 관찰의 필요성과 실행 계획 고정 |
| 25분까지 | 필요할 때만 기존 제한 그대로 환경 준비·기준 실패 확인. 준비가 끝나지 않으면 동적 탐색을 중단하고 보존 증거로 인계 |
| 40분까지 | 가능한 범위의 syscall/LSM 근거 확보, 최소 변경 후보와 미확인 항목 작성 |
| 50분 | 모든 새 탐색/재시도 종료. 근거 정리·검증·자원 정리·보고에 집중 |
| 60분 | 최종 마감. 미완료 항목/잔여 자원/후속 필요를 명시하고 종료 |

기계적인 경로/인자/수집 오류는 원인이 확인된 경우에만 총2회까지 국소 수정한다. 동일 실패 명령의 무근거 반복은 하지 않는다. 버전·후보·권한 정책 변경은 재시도가 아니다. 정리 시간을 확보할 수 없으면 중간 마감 전에도 탐색을 끝낸다.

## 작업 순서

### 1. 보존 증거로 차단 경로를 분해한다

실제 OCI seccomp/AppArmor/namespace/UID/capability/NNP와 실행 binary의 hash/version을 대조한다. 일반 기본 설정 파일보다 실제 컨테이너 Spec을 우선한다. kernel·runtime·CLI·bwrap 버전별 공식 문서/공개 구현에서 관련 조건만 확인하고 URL·revision·해당 구문을 기록한다. 최신 문서만으로 고정 CLI의 구현을 단정하지 않는다. 정확한 구현 revision을 연결하지 못하면 그 한계를 남긴다.

다음 가설을 표로 작성한다: seccomp syscall 차단, clone/clone3의 flags·fallback, AppArmor userns 제한, kernel userns 조건, CLI/bwrap 자체 요구 조건. 각 행에 기존 관찰, 정책/구현 근거, 반대 근거, 필요한 추가 관찰, 현재 확신 수준을 둔다. 동일 errno만으로 원인을 하나로 확정하지 않는다. bwrap의 일반 오류 메시지를 sysctl 상태의 증거로 사용하지 않는다.

정책에서 특정 syscall을 거부한다는 사실과 **bwrap가 실제 그 syscall에서 먼저 실패했다는 사실**을 분리한다. 한 차단 요인이 확인돼도 다른 계층이 허용한다는 결론은 내리지 않는다.

### 2. 기존 제한 안에서만 필요한 관찰을 추가한다

기존 증거와 구현 대조로 변경안의 근거가 충분하면 새 VM을 만들지 않아도 된다. 새 관찰은 어떤 미확인 항목을 줄이는지 먼저 기록한다. 필요하면 소유 임시 VM1개와 준비 container 최대2개만 사용한다. 기존 VM은 정리됐으므로 재준비 시간도 포함한다.

고정 CLI0.167.0-alpha.3.2, 기존 후보/게스트·runtime 버전과 worker 제한을 유지한다. UID/GID1000, capability 전부 제거, NNP, RO root/cgroup, network none, CPU2·메모리4GiB·PID256·tmp64MiB를 실제 Spec으로 확인한다. 기존 정책 파일·runtime 설정·sysctl·AppArmor profile은 변경하지 않는다. 정책을 바꾸지 않은 새 컨테이너 생성은 허용되지만, 새로운 진단 mount/도구 파일은 목록·용도·hash를 기록하고 읽기 전용 합성 입력으로 제한한다.

비모델 baseline 명령과, 가능한 경우 같은 제한 아래 자식으로 시작한 bwrap/CLI의 좁은 syscall trace를 비교한다. 필요한 호출 종류·flags·반환값·직접 자식 관계만 수집한다. 새 추적 도구가 필요하면 관리자 준비 단계에서 패키지 버전/라이선스/이미지 차이를 기록하고, worker 권한을 바꾸지 않는다. 진단 이미지와 원래 실행 이미지를 혼동하지 않는다. 도구 설치가 예산을 압박하면 생략한다.

ptrace/추적이 현재 정책에서 거부되면 그것도 결과다. 관찰을 위해 SYS_PTRACE/SYS_ADMIN을 추가하거나 seccomp/AppArmor를 끄지 않는다. 호스트/게스트의 다른 프로세스에 attach하지 않는다. 기존 관리자 권한으로 조회 가능한 해당 시험의 kernel/LSM 로그만 좁게 읽을 수 있으며, 새 audit 설정/커널 추적 장치/권한 변경은 하지 않는다. 일반 시스템 로그 전체를 보관하지 않는다. 로그 부재를 AppArmor 허용의 증명으로 쓰지 않는다.

동적 단위는 실행 전에 명령·입력/정책 hash·실패 기대·시한을 기록한다. payload 최대15초, container 생성부터 외부 마감120초, 준비 단위 전체 최대2개를 지킨다. 관찰이 instrumentation의 영향을 받는 경우 untraced 기준 실패와 구분한다. 무변경 기준이 예상과 달리 성공하면 승인 범위 밖의 경계 검증을 이어가지 말고 환경 차이부터 보고한다.

준비 단위는 fixtureOnly/validSubmission=false다. 소유 runtime/PID/cgroup 부재를 확인해 정리하되 이를 CLI timeout/수집 경계의 새 통과 증거로 주장하지 않는다. 기존 최소 준비 도구를 재사용하고 범용 trace runner나 새 lifecycle adapter는 만들지 않는다.

### 3. 적용하지 않은 최소 변경안을 작성한다

가장 작은 근거 있는 후보1개를 중심으로 제시한다. 정확한 최소 집합을 입증할 수 없다면 **최소 후보이며 충분성 미검증**이라고 표시한다. seccomp 한 항목만 수정하면 성공한다고 약속하지 않는다. AppArmor 등 추가 계층이 필요할 가능성은 별도 조건으로 둔다.

| 변경안 필드 | 필수 내용 |
| --- | --- |
| 기존 값 → 제안 값 | 실제 기존 정책의 정확한 항목과 제안 차이. syscall/flags/architecture/profile 범위 등을 근거가 있는 수준까지 명시 |
| 필요 근거 | 원시 관찰·정책 구문·고정 버전 구현의 연결. 추론과 직접 관찰 구분 |
| 적용 단위 | 해당 시험 container/profile에 국한 가능한지, VM/host 전체 설정이 필요한지 |
| 권한 영향 | CLI parent뿐 아니라 도구 자식도 얻는 능력, 다른 namespace/마운트/프로세스·파일/네트워크 경계 영향 |
| 남는 차단/불확실성 | 다른 계층, 미확인 syscall 순서, 적용 후 확인해야 할 가설 |
| 후속 검증·복구 | 승인 후 최소 시험 순서, 부정 대조, 되돌릴 설정/자원, 실패 시 중단 기준 |
| 비용 | 정책 시험과 전체 경계 회귀를 나눈 예상 시간·운영 부담. 이번 관찰값과 추정 구분 |

제안은 문서 또는 실행 경로와 분리된 비활성 diff로만 저장한다. manager가 읽는 정책·Dockerfile·실행 기본값·runtime profile에는 반영하지 않는다. dry-run이라는 이름으로 runtime에 새 정책을 전달하지 않는다. 코드 생성기는 불필요하다.

후속 검증안에는 source RW/자료 RO 양성 대조, control/가짜 인증 직접·symlink·proc/FD/환경 접근 거부, parent 서버 양성/명령 네트워크 음성, 새 정상2회·CLI 자손 timeout/유한 writer 대조·종료 후 수집·cleanup 회귀를 포함한다. namespace 진입 성공만으로 기존 경계가 유지된다고 보지 않는다. **이번에는 이 변경 후 검증을 실행하지 않는다.**

현 후보를 유지할 근거가 약하면 추가 투자를 권하지 않아도 된다. 동일 후보 유지안과 중단 시 대안의 비용을 간단히 비교하되 새 후보/직접 VM/API runner/proxy 구현은 시작하지 않는다.

## 즉시 중단 기준

- 진단 또는 해결을 위해 실제 seccomp/AppArmor/sysctl/capability/NNP 정책 변경, privileged 실행, sandbox 해제나 legacy 방식 전환이 필요하다.
- 호스트 home/인증/키체인/socket 제공, 실제 auth 내용 읽기·전달·로그인/refresh, provider/모델 호출이 필요하다.
- 고정 CLI/후보 교체·새 유료 비용·대규모 런타임 개조가 필요하거나 환경25분/탐색50분/전체60분 마감에 도달한다.
- 이전 증거와 현재 버전/정책의 차이를 해소하지 못하거나 새 진단이 다른 보안 문맥에서만 가능하다. 기존 증거 기반 분석으로 전환하고 동등한 재현으로 표시하지 않는다.
- 자원 종료/정리나 민감 정보 비포함을 확인할 수 없다. 새 실행을 막고 잔여 상태·소유 범위·필요한 후속 조치를 보고한다.

일반적인 패키지/공식 문서 다운로드와 관리자 환경 준비는 모델/provider 요청과 구분한다. worker의 network none은 유지한다. 준비가 필요해도 credential·호스트 전체 config/env를 다시 조사하거나 archive하지 않는다.

## 검증과 인계

새 결과는 `docs/reviews/2026-11-11-s2-namespace-diagnosis.md`와 `experiments/domain-model/s2/verification/2026-11-11-namespace-diagnosis/`에 저장한다. 날짜가 바뀌면 실제 날짜를 사용한다. 새 도구가 꼭 필요하면 `trial/container/namespace-diagnosis/`에 한정한다. 과거 증거와 공유 lifecycle·제품 코어·평가기·A/B/C 자료는 유지한다.

보고서에는 원인별 근거표, 실제 실행/미실행과 분모, 변경안 및 비적용 확인, 비용/재시도 ledger, 입력/정책 무변경 확인, 소유 자원 정리, 다음 의사결정을 넣는다. 동적 실행이0회여도 이유를 명시하고 보존 증거와 구분하면 된다. 관찰 전 snapshot과 실제 실행본을 연결하고 trace·로그가 없으면 없다고 적는다. 입력 불변성은 시작 시 범위를 고정해 종료 시 대조한다.

`pnpm check`와 문서 링크/변경 범위 검사를 실행한다. TS/공유 경계를 바꾸지 않는 한 S2 build·Python 전체 회귀·Vendure 설치/7평가·pnpm experiment를 반복할 필요는 없다. 새 증거 검증 도구를 작성했다면 실제 archive/실행 기록과 대조하고 잘못된 hash/정책 입력을 거부하는지 확인한다. 검사 실패는 숨기지 말고 완료 상태를 낮춘다. 검사·정리를 위한 시간을 최초60분에 예약한다.

최종 판정은 다음 중 하나다.

- **proposal-ready:** 근거 있는 정책 변경 후보·권한 영향·미확인·후속 검증/비용을 제시했다. 변경이 효과적이라는 실증이나 적용 승인은 아니다.
- **inconclusive:** 근거/시간이 부족해 좁은 후보를 제시하지 못했다. 필요한 다음 관찰과 추가 투자 가치만 명시한다.
- **blocked:** 허용 범위 내 진단을 진행할 수 없거나 금지한 범위 확대가 필요하다. 차단 조건과 정리 상태를 남긴다.

완료 조건은60분 안의 진단/정리/인계와 사실에 맞는 판정이다. 모든 원인의 확정이나 성공 후보 제시는 강제하지 않는다. PROGRESS·ARCHITECTURE·ROADMAP·REVIEW_CONTEXT와 필요한 DECISIONS를 갱신하고, pnpm check 및 자체 diff 검토 뒤 CONTRIBUTING의 저장소 게시 절차를 따른다. 저장소 반영 권한을 실제 정책 적용이나 모델 실행 승인으로 확대하지 않는다. 다음 단계는 결과 리뷰에서 정한다.
