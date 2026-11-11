# S2 CLI 비모델 타당성 결과 — 2026-11-11

**blocked, 독립 리뷰 대기.** 고정 CLI는 기동하지만 승인된 비특권 container 설정에서 native sandbox의 namespace 생성이 거부된다. 허용한 source 작업조차 시작하지 못하므로 CLI 제어/가짜 인증과 명령 권한의 분리를 성립시켰다고 판단할 수 없다. 권한 확대나 후보 교체 없이 환경 단계에서 탐색을 종료했다. [지시](2026-11-11-s2-cli-feasibility-instructions.md), [구현/재현 범위](../../experiments/domain-model/s2/trial/container/cli-feasibility/README.md), [새 원시 증거](../../experiments/domain-model/s2/verification/2026-11-11-cli-feasibility/)를 함께 검토한다.

기준 main은 지시의 `bcab22e`에서 `8cf5ad0`(PR #45)로 진행되어 있었다. 차이는 지시/맥락 문서6개뿐이며 새 작업은 `8cf5ad0`에서 시작했다. 제품·평가기·모델/B/C·과거 증거와 공유 lifecycle 코드는 변경하지 않았다. R11 unresolved·R12 기존 범위·production/live 거부·trialAuthorized/readyForTrial=false·results=null을 유지한다.

## 필수 표와 분모

| 항목 | 실제 관찰 | 판정/남은 범위 |
| --- | --- | --- |
| 고정 CLI 기동 | Codex0.167.0-alpha.3.2/Node22.19.0, launcher/native/bwrap hash, version/help/features, 새 CODEX_HOME helper 경고 없음 | 기동 확인; helper 디렉터리는 생성됐으나 sandbox payload 실행 실패 |
| 설정 격리 | RO config bind, 명시적 `-P fixture`가 namespace 준비까지 진행, 없는 profile은 resolution에서 거부 | 부분 관찰; 전체 key 지원·계층/지시 상속 배제·effective 권한은 미검증 |
| 파일 권한 | parent source 읽기·쓰기/자료 읽기 성공; native 허용 쓰기 산출물 없음 | 실패; 거부 성공으로 계산하지 않음 |
| 가짜 인증 | synthetic-only 파일을 parent가 읽음, 값은 결과에 출력하지 않음 | sandbox 직접/우회/proc/FD/환경 검사 및 parser 미실행 |
| 내부 네트워크 | 두 준비 container의 network none/namespace/mount/route 기록 | 서버 양성/음성 대조·외부 연결 시도 없음; 네트워크 경계 통과 주장 없음 |
| 실행 간 독립성 | 준비 container2개는 서로 다름 | 요구한 정상 경계2회는0/2; 상태 불상속 검증 아님 |
| 종료·수집 | 준비 container2개의 자연 종료/Pid0/삭제와 VM 삭제 전 runtime/task/cgroup 부재 확인 | CLI lifecycle 등록0, timeout/유한 대조0/2, 신규 collector receipt0; 전체 종료 보장의 새 증거 아님 |

비모델 CLI는 **10회: exit0 6회 / exit1 4회**다. discovery7회와 국소 원인 확인3회를 분리 보존했다. sandbox 진입 시도2회 중 첫 호출은 문서 형식 착오를 포함하며, 올바른 명시적 profile 호출은1회다. native sandbox payload 시작은0회, parent 양성 helper 묶음은1회, 보조 `unshare` 호출은1회다. 정상2회·timeout·네트워크·공유 lifecycle 실제 회귀를 이번에 실행한 것처럼 합산하지 않는다.

실제 자격 증명 전달0·로그인0·갱신0·provider 요청0·모델 호출0·본 비교0이다. 기능 목록 출력은 실제 turn의 도구 inventory나 지시 내용 관찰이 아니다.

## 세션·설정·가짜 인증·네트워크

Lima2.3.0/VZ + containerd/nerdctl2.4.2, 기존 pinned Dockerfile/base를 유지했다. 실제 build의 target/config/rootfs chain과 두 container snapshot parent를 다시 연결했다. UID/GID1000, capability 전부 제거, NNP, RO root/cgroup, CPU2·메모리4GiB·PID256, tmp64MiB·network none을 실제 OCI/proc 자료로 남겼다.

호스트 home/config/auth/socket은 mount하지 않았다. CLI 환경은 PATH/HOME/CODEX_HOME/TMPDIR/LANG만 직접 구성한다. 새 CLI 상태는 `/home/runner/cli-state`, 셸용 HOME `/home/worker`, scratch `/scratch`다. 두 번째 준비 container에는 manager가 만든 config 파일을 RO로 별도 bind했고 source는 RW, 자료/진단 도구는 RO다. native profile은 control 경로 deny와 network disabled를 요청하지만 **실행 중 강제는 확인되지 않았다**. source/config 등의 내용 지문은 실행 전에 보존했다. 일반 결과에 CLI 상태 저장소 전체를 수집하지 않았다.

호스트 인증 조사는 allowlist된 `cli_auth_credentials_store` 값과 `auth.json`의 lstat뿐이다. 파일은 regular/0600이며 설정값은 unset-or-unknown이다. 활성 backend는 **unknown**으로 남긴다. 파일 존재만으로 파일 backend 사용을 단정하지 않는다. 실제 auth 내용·키체인·계정 식별자·전체 config/env는 읽기/복사/hash/archive하지 않았다. 후속에는 사용자가 선택한 저장 backend와 실제 연결 범위를 먼저 확정해야 하며 이번 메타데이터가 연결 승인이 되지 않는다.

현재 [공식 설정 문서](https://learn.chatgpt.com/docs/config-file/config-basic)는 CLI override, trusted project, profile, user, cloud defaults, system, built-in 순서와 별도 requirements 제약을 설명한다. 이번 고정 버전에서는 help의 CODEX_HOME/profile/override 지원과 explicit profile resolution만 확인했다. `.codex`/`.agents`/AGENTS/exec rules의 표식별 적용·환경 우선순위·시스템/조직 계층 전체는 확인하지 않았다. [공식 인증 문서](https://learn.chatgpt.com/docs/auth)의 저장 옵션 설명도 현재 호스트 backend 관찰과 구분한다. 기능/환경 필터 설정만으로 실제 세션·도구 격리를 주장하지 않는다.

## 최초 실패와 국소 재확인

1. discovery에서 현재 [CLI 문서](https://learn.chatgpt.com/docs/cli/reference)를 따라 `codex sandbox linux --help`를 호출했다. 고정 버전의 실제 `sandbox --help`에는 linux 하위 명령이 없고 command positional이 있다. 따라서 이 호출은 단순 help 조회가 아니라 `linux --help`를 실행하려는 sandbox 진입 시도였다. payload 전에 namespace 생성 오류로 exit1했다. 원문은 그대로 보존했다.
2. 지원되는 `codex sandbox -P fixture -C /source -- /usr/local/bin/node …`로 국소 확인했다. 존재하지 않는 profile은 resolution 오류, 존재하는 profile은 bubblewrap namespace 오류를 냈다. source/material을 사용하는 유한 허용 명령은 시작하지 못했다. 별도 `--strict-config features list`는 이 버전에서 지원하지 않는 조합으로 거부됐다. 성공으로 집계하거나 설정 전체를 검증했다고 표시하지 않는다.
3. 같은 문맥에서 `unshare --user --map-root-user -- /bin/true`도 `Operation not permitted`였다. 실제 OCI seccomp는 default ERRNO이고 unshare 허용 규칙이 없으며 clone namespace flags를 제한하고 clone3에는 ENOSYS를 지정한다. `/proc`는 Seccomp2·NNP1·capability0, kernel unprivileged_userns_clone1/max_user_namespaces21089, AppArmor userns 제한1/nerdctl-default를 보여준다. **단순 sysctl 비활성 때문이라는 bwrap의 일반 안내를 확정 원인으로 옮기지 않는다.** 고정 보안 설정이 namespace 생성을 차단한다는 근거이며, bwrap의 첫 실패 syscall이나 AppArmor의 독립 기여는 syscall trace/정책 변경으로 분리하지 않았다.

[공식 권한 문서](https://learn.chatgpt.com/docs/permissions)는 Linux filesystem 제한에 bubblewrap/seccomp를 사용하고 필요한 namespace 작업이 막힌 환경은 해당 정책을 실행할 수 없다고 설명한다. 이 설명과 실제 실패가 일치한다. legacy Landlock 전환, sandbox 해제, capability/seccomp/sysctl 완화, 다른 CLI/후보/API/proxy로 우회하지 않았다. 탐색 중단 뒤에는 검사·증거 대조·정리·보고만 수행했다.

## 검사·비용·정리

`pnpm check`의304테스트(skip0)·타입 검사·예제 build, S2 build, collector13·cleanup3 회귀가 통과했다. 실제 과거 fixture `7ca7f2d67f77`로 production 수집·평가/live 거부를 다시 확인했다. 이는 과거 receipt를 재사용한 거부 회귀이며 새 CLI 제출 receipt가 아니다. 공유 lifecycle를 수정하지 않아 실제 normal/timeout/wrapper/supervisor/publication 재주입은 하지 않았다. Vendure 재설치/7평가와 `pnpm experiment`도 실행하지 않았다. 새 audit은 image/chain·실제 제한·실패/양성 대조·호출 분모·snapshot 내부 hash·기존 입력 불변성을 대조한다.

최초 UTC **2026-11-11T12:25:08.368877Z**, host monotonic **152464.702334833**을 유지했다. VM/image 대기·문서 조사·실패·검사·정리·보고를 새90분에 포함했다. 환경20분 마감 전에 CLI 기동/저장 메타데이터/국소 namespace 실패를 확인하고 중단했다. 핵심45분/탐색70분을 새로운 예산으로 재시작하지 않았다. 신규 유료 비용0이며 정확한 이번/이전/누적 시간은 [cost.json](../../experiments/domain-model/s2/verification/2026-11-11-cli-feasibility/cost.json), 명령별 시간과 snapshot 연결은 evidence의 host/budget.json에 기록했다. Git 게시/PR/merge 시간은 실험 마감 이후 별도 집계한다.

이번 회차는 **1120.033초**, 환경 청구는 **649.418초**다. 이전 회차 합산 8920.169초에서 누적 10040.202초가 됐고, 환경 누적은 4390.147초다. 수치는 검사·정리·보고 검토를 마친 시점이며 마지막 비용/증거 index 갱신은 checkpoint 직후 bookkeeping으로 분리한다. 90분 초과는 없다.

두 준비 container는 각각 exit0/Pid0를 확인하고 삭제했다(내부 CLI 실패는 JSON에 보존). VM 삭제 **전** container/task/cgroup/image/volume/작업 unit 부재를 대조했다. 테스트 서버/custom network rules/lifecycle 서비스는 만들지 않았다. 그 뒤 소유 VM·prefix·새로 생성한2개 cache leaf만 시작 inventory와 URL/data hash를 대조해 제거했다. 기존 Vendure cache와 호스트 인증은 변경하지 않았다. 복구할 소유 자원은 남지 않았으며 VM 삭제를 CLI 자손 timeout 보장으로 제시하지 않는다.

## 실제 연결 전 남은 검증과 다음 선택

현재 판정은 ready-for-live-connection-review가 아니다. 네트워크/가짜 인증 우회·환경/FD·설정 계층/실제 tool inventory·정상2회·CLI 자손 timeout·성공 cleanup 이후 수집이 남아 있다. 임의 수정 소스 제출 평가 연결과 C 사람 의미 검토도 그대로 남는다.

먼저 이 실패 증거와 고정 CLI의 문서 차이를 독립 검토한다. 다음에 재개하려면 같은 후보 안의 **최소 namespace 정책 변경을 별도 위협 검토/승인/예산으로 설계**할지, 현 후보 조합을 중단할지를 선택해야 한다. 정책을 바꾸면 namespace 진입뿐 아니라 파일/가짜 인증/proc/FD/네트워크와 lifecycle 영향 회귀를 처음부터 확인해야 한다. 준비 비용의 관찰값은 이번 ledger에 있지만 새 정책 검증 총비용은 아직 추정하지 못한다. 단순 재실행으로 해결될 근거는 없다. 실제 credential·로그인/갱신·provider/model·본 비교는 시작하지 않고 결과 리뷰를 기다린다.
