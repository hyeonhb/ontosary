# S2 namespace 진단 결과 — 2026-11-11

**proposal-ready, 독립 리뷰 대기.** 같은 제한에서 실행한 strace가 bwrap의 첫 namespace 생성 `clone`을 직접 관찰했고, flags `0x78020011`이 실제 seccomp 허용 조건에서 제외됨을 확인했다. [비활성 정책 후보](2026-11-11-s2-namespace-policy-proposal.md)는 이 조합에 한정한 추가 허용을 검토 대상으로 제시한다. **정책을 적용하거나 sandbox 성공을 확인한 결과가 아니다.** AppArmor의 독립 기여와 다음 차단점은 남아 있다.

[개발 지시](2026-11-11-s2-namespace-diagnosis-instructions.md)에 따라 새60분 회차로 진행했다. 지시 기준 `bbb43c9`에서 실제 시작 main은 `14202cc`(PR #47)였고 차이는 지시/맥락 문서6개뿐이다. 기존 제품·평가기·모델/B/C·정책·공유 lifecycle·과거 증거2521파일은 시작 지문과 일치한다. R11 unresolved·R12 기존 범위·production/live 거부·trialAuthorized/readyForTrial=false·results=null을 유지한다.

먼저 직전 [보고서](2026-11-11-s2-cli-feasibility.md)의 표현을 정정한다. `auth-metadata.py`는 **사용자 config.toml 전체를 메모리에서 TOML 파싱한 뒤 허용된 설정값만 결과에 기록**했다. 따라서 “전체 사용자 config를 읽지 않았다”는 표현은 부정확했다. 실제 auth.json은 lstat만 했고 그 내용·키체인 값은 읽거나 복사/hash/archive하지 않았다는 사실과 구분한다. 전체 config 파싱을 일부 키만 읽은 것으로 표현하지 않는다. 과거 보고/코드/원시 증거는 그대로 보존했으며 이번에는 호스트 인증/config 조사를 반복하지 않았다.

## 원인별 근거와 미확인

| 가설 | 기존/새 관찰과 정책·구현 근거 | 반대 근거·한계 | 현재 판단 |
| --- | --- | --- | --- |
| seccomp syscall 차단 | 실제 OCI default ERRNO. clone은 arg0 AND `0x7e020000`이0인 경우만 허용. trace flags AND 결과는 `0x78020000`. 두 bwrap 프로세스의 해당 clone이 EPERM | syscall 결과만으로 모든 차단 계층을 분리한 것은 아님 | **관찰된 호출을 거부하는 구체적 정책 근거 확보**. 해당 규칙과 실패가 일치 |
| clone/clone3 flags·fallback | 일반 thread/process clone은 성공. bwrap는 USER·NS·IPC·PID·NET·SIGCHLD로 raw clone. 추적 구간의 clone3/unshare/setns 호출은0. 정책의 clone3 ENOSYS는 그대로 | 추적하지 않은 경로나 이후 단계의 fallback을 배제하지 않음 | 첫 실패는 관찰된 clone. unshare만 허용하는 제안으로 이 호출을 해결할 근거 없음 |
| AppArmor userns/기타 제한 | worker `nerdctl-default (enforce)`, parser5.0.2, userns 제한1. 생성된 default template에 mount deny, same-profile ptrace 허용 | 수정한 제한 시간창의 kernel/LSM 조회는 매치0. template은 로드된 compiled policy의 추출본이 아님. 로그 부재는 허용 증명 아님 | **독립 기여 미확인**. 특히 clone 이후 mount 단계의 별도 제약 가능성을 유지 |
| kernel userns 조건 | 동일 Ubuntu7.0.0-38, CONFIG_USER_NS/NAMESPACES/SECCOMP_FILTER/APPARMOR=y, unprivileged_userns_clone1/max21089 | sysctl이 켜졌다는 사실만으로 모든 namespace 생성 조건이 성립하지 않음 | 전역 userns 미지원/비활성 설명은 관찰과 맞지 않음. 나머지 제한은 미확인 |
| CLI/bwrap 요구 | 정확한 CLI/resource hash 유지. version 일치 release tag의 raw_clone 코드·flags 구성·EPERM 분기와 trace 대응 | bundled `--version`은 “built for Codex”만 출력. tag source0.11.2와 바이너리의 재현 build/실행 FD3 byte hash는 미확보 | **고정 버전 구현과 관찰을 연결**, packaged resource와 실행 memfd의 동일 bytes까지 독립 입증한 것은 아님 |

seccomp ERRNO는 syscall 본체를 실행하지 않고 오류를 돌려준다. 따라서 현재 정책이 이 호출을 차단한다는 사실로 그 뒤 kernel/LSM 처리가 허용될 것이라고 추론하지 않는다. [Linux seccomp 문서](https://docs.kernel.org/userspace-api/seccomp_filter.html)의 의미와 실제 OCI/trace를 구분해 사용했다.

## 실제 실행과 instrumentation

사전 계획은 첫10분 안에 `host/plan.json`으로 고정했다. 기존 증거에는 첫 syscall/flags가 없어서 동적 관찰을 선택했다. 소유 VM1개, 준비 container **2개만** 만들었다. 원래 pinned Dockerfile/base·Codex0.167.0-alpha.3.2·Node22.19.0·Lima2.3.0/VZ·nerdctl/containerd2.4.2를 유지했다. containerd revision은 `b7a25261e029d68978bbf290df0a62fc819b3c51`이다.

기준은 원래 이미지이고 추적 이미지는 그8개 rootfs layer 뒤에 strace 패키지 layer1개를 추가했다. strace는 Debian `6.1-0.1`, 설치 패키지 고지상 LGPL-2.1-or-later이며 테스트 모음은 GPL-2.0-or-later다. 실제 버전·binary hash·패키지 copyright와 설치 로그를 보존했다. 원래 이미지와 진단 이미지 target/config/chain을 별도 기록하고 각 실제 container snapshot parent와 연결했다. 제품 의존성을 추가하지 않았으며 진단용 도구는 VM과 함께 제거했다.

UID/GID1000·capability0·NNP1·RO root/cgroup·CPU2·메모리4GiB·PID256·tmp64MiB·network none을 유지했다. 실제 seccomp, user/capability/NNP/AppArmor, namespace 종류, cgroup mount와 자원 정책을 직전 Spec 및 두 새 Spec 사이에서 대조했다. CLI/bwrap resource hash도 직전과 같다. 진단 helper·합성 자료·기존 config는 목록/hash를 기록하고 RO로 제공했다. source/output/전용 상태/scratch는 해당 준비 단위만의 기존 용도다. 호스트 home/auth/socket/config/env를 가져오지 않았다.

| 분모 | 결과 |
| --- | --- |
| 준비 container | 기준1 + 추적1 =2; 각각 자연 종료 후 삭제 |
| 비모델 CLI |4회: version2 + sandbox2. version은 exit0, sandbox는 exit1 |
| 직접 bwrap version |2회, 별도 집계 |
| strace |version1 + CLI 자식 추적1. 다른 프로세스 attach0 |
| 관찰된 namespace clone |추적한 내부 bwrap2개에서 같은 flags/EPERM2회. 내부 사전 점검과 실제 명령 준비로 구분하며 추가 CLI 호출로 합산하지 않음 |
| parent 양성/실제 payload |두 준비 단위 모두 source 읽기·쓰기/자료 읽기 성공; sandbox payload 시작0 |
| 새 정책 적용·실제 credential 전달·로그인·갱신·provider·model·본 비교 |각각0 |
| runtime 재시도 / 기계적 수정 |runtime 재시도0 / 로그 조회 옵션 수정1 |

trace는 launcher→고정 native CLI→전용 상태의 sandbox helper→`/proc/self/fd/3`의 bwrap exec와 직접 자식 PID 관계를 남긴다. 해당 bwrap41/42의 첫 namespace clone은 `CLONE_NEWNS|CLONE_NEWIPC|CLONE_NEWUSER|CLONE_NEWPID|CLONE_NEWNET|SIGCHLD`로 EPERM이다. 자손 추적은 기존 권한에서 가능했으며 SYS_PTRACE/SYS_ADMIN을 추가하지 않았다. trace의 signal/호출 원문도 보존했다. 진단 이미지·ptrace가 timing/관찰에 영향을 줄 수 있으므로 **untraced 기준 오류와 traced syscall 관찰을 별도 표본**으로 취급한다. 기준 실행의 내부 호출 순서까지 직접 관찰했다고 주장하지 않는다.

각 단위는 실행 전 command/input/policy/image 지문과 실패 기대, payload15초·create부터외부120초 상한을 기록했다. 실제 create→삭제는 기준0.829초/추적0.607초였고 각 로컬 명령은 최대5초 제한 안에서 끝났다. 자연 종료/Pid0·runtime/container/cgroup 부재를 VM 삭제 전에 확인했지만 이를 CLI timeout·전체 writer 종료·collector authority의 새 증명으로 쓰지 않는다.

## 구현 revision과 출처

실제 Spec을 우선하고 공개 구현은 다음처럼 연결했다. URL·revision·원본 byte hash·사용 여부는 `host/source-evidence.json`에 있다. 초기에 확인한 일반 upstream bwrap0.11.0은 최종 근거에서 제외했다.

- [nerdctl2.4.2 보안 선택](https://github.com/containerd/nerdctl/blob/94bc03df5247ece1781c4b115a44ef3d4b1e0e65/pkg/cmd/container/run_security_linux.go#L68): custom 옵션이 없는 경우의 containerd 기본 seccomp 및 default AppArmor 선택. tag revision `94bc03d…`를 고정했다.
- [실제 containerd revision의 seccomp](https://github.com/containerd/containerd/blob/b7a25261e029d68978bbf290df0a62fc819b3c51/contrib/seccomp/seccomp_default.go): CAP_SYS_ADMIN 없는 경로의 clone mask·clone3 오류가 실제 Spec과 대응한다.
- [CLI release tag의 bwrap](https://github.com/openai/codex/blob/c40729ea5cf8e947481b130c59807273eda2f8e9/codex-rs/vendor/bubblewrap/bubblewrap.c#L3089), [raw_clone](https://github.com/openai/codex/blob/c40729ea5cf8e947481b130c59807273eda2f8e9/codex-rs/vendor/bubblewrap/utils.c#L881): `rust-v0.167.0-alpha.3.2`는 `c40729e…`이고 해당 경로는 raw clone을 사용한다. arm64는 flags를 첫 인자로 전달한다. source와 실제 byte의 build provenance 한계는 위 표대로 남긴다.
- [AppArmor template](https://github.com/containerd/containerd/blob/b7a25261e029d68978bbf290df0a62fc819b3c51/contrib/apparmor/template.go#L81)과 [Ubuntu 설명](https://documentation.ubuntu.com/security/security-features/privilege-restriction/apparmor/)은 추가 계층의 근거다. 생성된 abi3.0 template에 userns 항목이 없다는 사실만으로 최신 Ubuntu에서 그 호출이 거부/허용된다고 단정하지 않는다. 정확한 Ubuntu kernel 패치 revision 전체와 loaded binary policy를 재구성하지 않았다.

현재 [OpenAI 권한 문서](https://learn.chatgpt.com/docs/permissions)는 Linux의 bubblewrap/seccomp 의존성을 설명하지만 이번 syscall 순서의 근거는 고정 코드와 실제 trace다. 현재 문서를 고정 binary의 구현 명세로 대신하지 않았다.

## 실패·검증·정리와 비용

최초 kernel log 조회에 `journalctl --kernel`이라는 잘못된 옵션을 썼다. 두 단위의 exit1/원문 오류를 보존하고, 원인이 확인된 **단일 기계적 수정**으로 `-k`와 같은 실행 시간창의 UTC 표기를 사용했다. 추가 worker를 만들거나 재실행하지 않았다. 수정한 두 조회는 stderr 없이 `No entries`였고 LSM 허용을 뜻하지 않는다. 일반 kernel log 전체, auth/state 전체, 다른 프로세스 attach 자료를 수집하지 않았다. 최초 guest.py의 당시 오류 호출도 실행 전 snapshot에 남겼다.

`pnpm check`의304테스트(skip0)·타입 검사·예제 build가 통과했다. 새 증거 audit은 실제 archive/실행 기록, image/chain, prior/native 정책, source/CLI hash와 flags를 대조했고, 실제 archive의 정상 검증 및 잘못된 archive hash·policy member hash·추가 namespace 허용·NNP 해제 거부의 **5개 테스트**를 통과했다. 문서 링크/변경 범위를 확인했다. TS/공유 경계를 바꾸지 않아 S2 build·Python 전체 회귀·Vendure7·pnpm experiment를 반복하지 않았다.

이미 생성한2개 container의 stopped/Pid0/삭제·cgroup 부재를 확인하고 VM 삭제 전에 runtime tasks/container/image/volume/작업 unit 부재를 확인했다. 두 image와 소유 VM/prefix, 처음에 없었던 URL/hash-검증 cache2개만 제거했다. 기존 cache/호스트 인증은 그대로이며 잔여 복구 자원은 없다. 새 audit 설정·kernel 추적 시설·custom network rules·lifecycle service는 만들지 않았다. 기본 runtime의 원래 default profile 적용 외에 정책을 수정/전달하지 않았다.

최초 UTC **2026-11-11T13:36:08.802554Z**, monotonic **156727.152075458**을 유지했다. 읽기·자료 조사·대기·준비·실패/수정·검사·정리·보고를 새60분에 청구했다. 이전 누적10040.202초와 이번/새 누적은 [cost.json](../../experiments/domain-model/s2/verification/2026-11-11-namespace-diagnosis/cost.json)에 분리하며 Git 게시 시간은 그 이후 별도다. 신규 유료 비용0, VM1개/준비2개/수정1회로 상한 안에서 종료했다. [새 증거](../../experiments/domain-model/s2/verification/2026-11-11-namespace-diagnosis/)와 [도구 설명](../../experiments/domain-model/s2/trial/container/namespace-diagnosis/README.md)에 실행 전 snapshot·원본 실패·수정 조회·실행본/입력 hash·정리 기록을 모았다.

이번 회차는 host monotonic 기준 **1367.973초**, 환경 청구 **491.102초**, 이전 합산 포함 누적 **11408.175초**다. UTC 경과는 1370.015초로 monotonic과 2.042초 차이가 관찰됐으며, 명령 시한은 양쪽 잔여 중 작은 값을 사용했다. 차이의 원인은 별도 조사하지 않았고 시계를 재설정하지 않았다. 수치는 검사·정리·보고 대조 완료 시점이며 마지막 비용/index 갱신 bookkeeping은 checkpoint 직후로 분리한다. 60분 초과는 없다.

## 다음 결정

[후보 문서](2026-11-11-s2-namespace-policy-proposal.md)는 정확한 차이·architecture/자식 권한 영향·추가 차단·후속 양성/음성/종료 검증·복구·예산을 정리한다. 첫 차단점만 시험하는 별도30~45분 계획을 검토할 근거는 있지만, 전체 sandbox가 시작되는 최종 최소 정책은 아직 모른다. 특히 mount/LSM 때문에 전체 경계 구현으로 바로 확대하지 않는다. 현 조합 중단과의 비용 비교도 후보 문서에 있다. **이번에 제안을 적용하거나 변경 후 검증을 실행하지 않았다. 다음은 독립 리뷰와 별도 결정이다.**
