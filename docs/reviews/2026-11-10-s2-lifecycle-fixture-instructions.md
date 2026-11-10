# S2 fixture 실행의 전체 종료와 수집 경계 검증

개발 세션은 **호스트 래퍼와 독립된 게스트 감독자, 실행별 cgroup, 전체 종료 확인 뒤 관리자 전용 수집** 구조를 작은 fixture로 구현·검증한다. 사용자는 이 구조와 **새 회차 총3시간 상한**을 승인했다. 정상 종료·timeout·호스트 래퍼 사망·감독자 실패를 구분하고, 종료를 확인하지 못하면 결과 확정과 다음 실행을 차단한다.

이번 결과는 선택한 환경의 fixture 경계에만 적용한다. 성공해도 Vendure 설치/빌드, 실제 CLI 도구·인증/provider 연결, 제출 평가기, 본 비교로 넘어가지 않는다. 해당 범위와 비용은 결과 리뷰 뒤 정한다. 기존 production/live 차단과 R12 계약, 과업·모델·B/C 자료는 유지한다. 이번 지시는 ADR-035의 실행 범위이며 이전 회차의 잔여 예산을 재개하지 않는다.

## 1. 시작과 기준 자료

**첫 명령으로 UTC·단조 시각과 절대 마감을 기록한 뒤 읽기를 시작한다.** 최초 읽기 전에 기록하지 못했다면 누락 구간을 명시하고 임의 보정치를 실측값으로 표현하지 않는다. PROGRESS → ARCHITECTURE → ROADMAP, AGENTS/CONTRIBUTING을 읽고 원격/브랜치/사용자 변경을 확인한다. PR #40의 `45fdcd6` 이후 이 지시가 포함된 최신 main을 기준으로 실제 base SHA를 기록한다. 다른 checkout이나 원본 Vendure cache를 변경하지 않는다.

- [smoke 결과](2026-11-10-s2-container-smoke.md), [지시](2026-11-10-s2-container-smoke-instructions.md), [원시 증거](../../experiments/domain-model/s2/verification/2026-11-10-container-smoke/).
- [기존 준비 구현](../../experiments/domain-model/s2/trial/container/), 특히 smoke.py의 native image target/config/rootfs chain과 실제 container 대응. 재빌드 digest를 과거 값으로 하드코딩하지 않는다.
- [R11/R12 독립 리뷰](2026-11-10-s2-runtime-accounting-independent-review.md), [기존 runtime](../../experiments/domain-model/s2/trial/runtime.ts), [snapshot gate](../../experiments/domain-model/s2/trial/snapshot-gate.ts), [trial 계약](../../experiments/domain-model/s2/trial/README.md).

출발 상태는 smoke4개 통과·호스트303테스트·R11 unresolved다. 직전 독립 검토에서 OCI/실행 연결과 증거 hash를 대조했으며 새 VM 재실행은 하지 않았다. CLI version/help의 임시 CODEX_HOME 보조 실행 파일 생성 경고는 후속 CLI 환경 검토 항목이다. 이번에는 셸·Node fixture만 사용하고 경고 수정이나 실제 CLI 세션을 병행하지 않는다.

## 2. 비용과 구현 순서

| 경과 시점 | 작업과 중단 기준 |
| --- | --- |
| 0~20분 | 같은 후보/버전의 VM·이미지 재준비, native target 확인, 최소 셸 실행.20분까지 재현하지 못하면 탐색 중단·인계 |
| 시작 후90분까지 | 감독자/전용 cgroup 배치 → 시한/생존 신호 → 전체 종료 확인 → 제한된 수집. 정상 종료와 timeout의 실제 전체 종료 확인·수집 경로를 확보하지 못하면 중단 |
| 시작 후150분까지 | 래퍼/감독자 사망, 관리 오류, 자손 생성 경쟁, 수집 실패·다음 실행 격리와 반복 검증 |
| 150~180분 | 새 설치/수정/probe를 중단하고 회귀·정리·증거·최소 보고. 더 일찍 완료하면 즉시 마무리 |

읽기·조사·다운로드·빌드·대기·구현·재시도·검증·정리·보고를 경과 시간에 포함한다. 명령 timeout은 단계의 남은 시간 이하로 두고150분에 미완료 탐색 명령을 끝낸다. 마감/세션 재시작으로 예산을 초기화하지 않는다. 기존 고정 수정1회 제한은 적용하지 않으며 **근거가 생긴 국소 수정만 시간 내 재시도**한다. 오류·원인 증거·수정 가설·결과를 남기고 같은 실패를 근거 없이 반복하지 않는다.

환경은 Lima2.3.0/VZ + containerd/nerdctl2.4.2, 기존 고정 Node22.19.0 이미지/base digest를 유지한다. 후보1개·신규 유료 비용0이다. 새 라이브러리/플랫폼·호스트 관리자 권한·보안 설정/전역 서비스/기본 Docker context 변경·새 계정·CLI 포크/API 실행기는 범위 밖이다. 필요한 표준 도구의 부재가 확인되면 대체 구현으로 범위를 넓히지 말고 인계한다. VM 내부의 전용 임시 systemd unit/slice와 guest 관리 권한은 이번에 허용한 구조다.

이전 두 회차와 이번 회차의 환경/전체 시간을 별도 열로 기록하고 합산한다. 이전 환경 합계1,728.267초, 전체 약2,588.951초에는 추정 시작 구간이 포함돼 있다. 회차 사이 사용자 검토 대기·Git 전달 시간은 작업 구간과 분리한다. 기존90분/4시간 잔여 예산은 사용할 수 없다.180분 뒤 새 검증은 금지하며 소유 자원 정리·최소 증거 보존의 불가피한 초과만 이유와 함께 기록한다. PR/merge 전달은 별도 계측하고 실험을 재개하지 않는다.

## 3. 최소 구현 구조

실험 내부 `trial/container/` 아래에 한 후보의 호스트 driver, 게스트 supervisor/cleanup, collector, 유한 fixture/probe를 둔다. 현재 Python·shell·Node와 표준 라이브러리를 우선 재사용한다. 의미 있는 책임 경계만 나누고 다중 backend 프레임워크·범용 snapshot 저장소·새 제품 API를 만들지 않는다.

| 구성 | 책임과 접근 범위 |
| --- | --- |
| 호스트 래퍼 | 실행 요청·생존 신호·결과 조회. 실행 중 사라져도 guest의 감독/시한은 유지 |
| 게스트 감독자 | 임시 systemd service. manager 권한으로 실행 ID·불변 container ID·이미지 target·전용 cgroup·경로·시한·상태 소유 |
| worker | 기존 비특권 container. 자신의 source/auxiliary만 쓰기 가능. control·결과·다른 실행·host home·runtime socket·실제 자격 증명은 미제공 |
| collector | 전체 종료 확인 뒤 감독자가 실행. 관리자 전용 staging과 결과 디렉터리만 사용 |

worker는 UID/GID1000, cap-drop ALL, no-new-privileges, network none, CPU2/memory4GiB/PID256, readonly rootfs와 한정 tmpfs를 유지한다. source/auxiliary는 VM 내부의 실행별 별도 경로를 필요한 범위만 bind한다. 컨테이너 단위의 쓰기 영역을 공유·재사용하지 않는다. 배포 이미지/준비 다운로드와 worker 네트워크 권한을 구분한다.

감독자와 cleanup은 worker의 종료 대상 cgroup 밖에 둔다. 실행별 **manager 소유의 상위 cgroup/slice** 아래에 worker를 배치하고, runtime이 자식 scope를 지워도 상위 그룹을 증거 확인까지 유지한다. 현재 systemd driver에 맞는 cgroup-parent 표현을 확인하고 실제 PID/cgroup 경로로 배치를 대조한다. 이름/OCI 선언만으로 배치 성공을 판정하지 않는다. cgroup namespace는 private, 제어 파일은 worker에서 쓰기 불가이며 이동/재위임·외부 실행 API 접근을 막는다.

실행 ID와 전용 경로/cgroup을 먼저 등록하고 감독·cleanup 경로가 준비된 뒤 worker를 시작한다. 최소 실행 정보는 manager 소유 파일에 원자적으로 기록한다. container 생성 직후 ID를 기록하되 생성 중 실패에도 전용 상위 cgroup으로 정리할 수 있어야 한다. worker가 제공한 경로/receipt로 종료 대상이나 수집 권한을 결정하지 않는다. 자동 restart는 끄고 실행 상태 변경은 단일 감독자가 직렬화한다.

호스트 래퍼는1초마다 생존 신호를 보내고 감독자는 **게스트에서 수신한 단조 시각**을 기준으로5초 미수신 시 중단한다. control 경로를 worker에 제공하지 않는다. 첫 생존 신호와 감독자 준비가 확인되기 전 작업을 시작하지 않는다. 생존 신호는 실행 시한을 연장하지 않는다. 통신 장애도 중단으로 분류하며 정상 성공으로 복구하지 않는다. 비동기 전송 helper가 래퍼 사망 후 신호를 계속 보내지 않는지 검증한다.

감독자에는 systemd RuntimeMaxSec와 ExecStopPost의 독립 정리 경로를 둔다. 전자는 감독자 실패에 대비한 바깥 상한이며 worker의 정확한 실행 시한을 대신하지 않는다. **service가 끝났다고 container가 끝난 것으로 간주하지 않는다.** ExecStopPost는 기록된 실행의 admission을 닫고 해당 cgroup/container만 정리한다. 감독자/cleanup 중복 호출은 멱등적으로 처리하고 작업을 재시작하지 않는다. 감독자가 죽으면 정상 결과 확정은 금지한다. cleanup까지 실패하면 VM을 폐기·차단하고 수동 복구 대상/증거를 인계한다.

## 4. 상태와 종료 계약

상태는 `prepared → running → stopping → stopped-confirmed → collecting → finalized`와 `blocked`로 충분하다. 상태 전이는 manager 소유이며 실행 사유(exit0/nonzero/timeout/wrapper-lost/supervisor-failed)와 분리해 저장한다. 상태 확인 실패는 성공으로 치환하지 않는다.

- **정상 주 작업 종료:** 종료 코드를 보존하고 잔여 자손까지 정리한다. 정상 부모 종료나 stdout/pipe EOF만으로 수집하지 않는다. nonzero 종료도 수집 가능 여부와 작업 성공 여부를 구분한다.
- **timeout:** 실행 시한에 전용 cgroup 전체 종료를 요청한다. 종료 정리 시간을 작업의 추가 허용 시간으로 취급하지 않는다. 확인 후 회수한 자료도 진단용이다.
- **호스트 래퍼 사망:** 독립 감독자가 생존 신호 만료로 중단한다. workload의 원래 시한도 계속 유효하다. 사용자/worker가 준 새 시각으로 예산을 늘리지 않는다.
- **감독자 사망/관리 실패:** systemd의 별도 정리 후에도 정상 결과를 만들지 않는다. 기록 누락·확인 불가·복사 실패는 blocked다. 기존 실행이 안전하게 정리됐다는 관리자 확인 전에는 다음 실행을 거부한다.

종료 절차는 실행/재시작 admission 닫기 → 전용 상위 cgroup의 `cgroup.kill` → `cgroup.events`의 **하위 그룹 포함 populated=0 확인** → runtime task/미완료 시작 작업 확인 → 수집 허용이다. worker가 그룹 밖으로 이동할 권한이 없고, manager가 새 writer를 시작하지 않는다는 전제를 함께 확인한다. cgroup 경로 소실·조회 오류·kill 반환·한 번의 ps 출력·hash 안정만으로 통과하지 않는다. supervisor 실패 당시 runtime 생성/시작 요청의 완료 여부가 불명확하면 결과/다음 실행을 차단하고 VM 정리로 끝낸다.

fixture 실행 시한은 기본10초, timeout 사례는5초로 고정한다. supervisor가 worker start 직전에 실행 시한을 기록하고 시작 준비 표식이 없어도 시한은 연장하지 않는다. 정상 종료/시한/신호 만료에서 **전체 종료 확인 상한10초**, 수집 상한10초, 단일 fixture 전체 바깥 상한60초를 둔다. systemd의 바깥 상한·cleanup timeout도 이 값 및 회차 남은 예산과 정합되게 설정한다. 마감 직전 새 fixture를 시작하지 않는다. 실제 요청·정지 확인·수집 시각과 지연을 기록하고 정확히 deadline 순간의 snapshot이라고 표현하지 않는다.

## 5. 수집과 fixture 전용 결과

수집은 stopped-confirmed 상태와 같은 실행의 ID/container/image/cgroup/path 대응이 있어야 시작한다. 미리 정한 작업 루트의 source/auxiliary **전체**를 관리자 전용 staging으로 복사한다. 확장자 필터로 helper/auxiliary를 버리거나 원래 baseline 파일을 복원하지 않는다. baseline 목록과 비교해 추가·수정·삭제를 모두 기록한다.

이번 fixture 지원은 일반 파일/디렉터리로 제한한다. symlink·hardlink(파일 link count>1)·FIFO·device·socket은 명시적으로 거부하고 어떤 항목 때문에 수집을 거부했는지 남긴다. lstat/no-follow 방식으로 루트 밖 경로를 따라가지 않으며 결과 경로를 source 아래에 두지 않는다. worker 경로를 root 권한의 shell 문자열로 보간하지 않는다. 거부할 파일을 먼저 읽어 block되거나 외부 데이터를 복사하지 않도록 한다.

상한은 source/auxiliary 합산 **파일128개·일반 파일 총16MiB·경로 깊이16**, workload 로그는 실행별1MiB로 둔다. 초과를 조용히 잘라 정상 결과로 만들지 않는다. 자료는 바이트를 보존해 순차 복사/hash하고 경로 목록을 정렬한다. 별도 증분 저장/CAS는 만들지 않는다. 관리 증거 로그와 workload 로그를 구별해 부정 사례가 기록 자체를 고갈시키지 않도록 한다.

완료된 staging의 파일 목록/hash와 종료 기록을 검증한 뒤 **같은 파일시스템의 원자적 rename**으로 최종 경로를 공개한다. 실패 시 최종 성공 경로가 없어야 한다. manager만 소유/수정하고 worker에는 노출하지 않는다. 작은 검증 container에는 read-only mount로만 제공하고 읽기 성공/쓰기 거부를 검사한다. chmod만으로 불변성을 주장하지 않는다.

결과는 fixture 전용 schema/경로로 만들고 `fixtureOnly:true`, `validSubmission:false`를 유지한다. run ID·image target·container ID·cgroup 식별·입력 기준 hash·source/auxiliary manifest·delta·실행 사유/exit code·시한/종료/수집 시각을 결합한다. 정상 exit0와 전체 확인을 마친 경우만 정상 fixture 결과로 분류한다. timeout/wrapper-lost/nonzero는 종료가 확인돼도 진단이며, 종료 미확인/감독자 실패에는 정상 결과를 발급하지 않는다. 부분 staging은 성공 결과와 분리한다.

`checkedSnapshot()`/production snapshot/live dispatcher를 열거나 기존 종료 상태를 전역 verified로 바꾸지 않는다. 임의 manifest·이번 fixture 기록을 기존 평가기 제출 권한으로 받아들이지 않는 회귀를 확인한다. R12/기존 평가 의미와 정적 자료는 그대로다.

## 6. 유한 fixture 검증 표

각 fixture의 시작·실제 쓰기·자손 준비 표식을 먼저 확인한 후 실패를 주입한다. 시작하지 않은 writer의 무출력을 종료 성공으로 세지 않는다. 고정 지연만으로 race를 만들지 말고 준비 표식과 manager 상태로 시점을 맞춘다. kill을 생략한 짧은 유한 대조에서 writer가 계속 쓰는지도 확인한다. 핵심 정상/timeout/wrapper-lost 사례는 **새 실행 단위로 각2회** 반복한다. 수백 회 stress나 무제한 fork는 하지 않는다.

| 묶음 | 필수 사례 | 통과 기준 |
| --- | --- | --- |
| 정상 종료 | 단순 exit0, nonzero, 주 작업이 setsid/손자 writer를 남기고 종료 | 종료 코드 보존, 모든 자손의 준비·실제 배치 확인 후 전체 종료. exit0만 정상 fixture 분류 |
| timeout | 주 작업 유지, detached/손자·열린 파일 FD·상속 stdout/pipe를 가진 지연 writer | EOF에 매달리지 않고 시한 처리. populated=0 확인 후 늦은 쓰기 없음, 결과는 진단 |
| 래퍼 사망 | worker/자손 준비 후 호스트 래퍼 SIGKILL | 감독자가 살아 있고 생존 신호가 멈춤. 원래 시한보다 먼저 신호 만료로 중단하도록 사례를 구성. 진단 분류 |
| 감독자/관리 실패 | 감독자 SIGKILL, 종료 명령 실패·상태 조회 오류 주입 | ExecStopPost의 해당 단위 정리 확인. 정상 결과 미발급, 미확인 상태에서 다음 실행 거부. 공용 daemon을 실제로 죽이지 않음 |
| 종료 경쟁 | 종료 직전 유한 자손 생성(최대8개), 중복 종료/cleanup 요청 | 잔여 writer/상태 역행/재시작 없음. 같은 실행에 성공 결과가 중복 확정되지 않음 |
| 수집 정확성 | 추가·수정·삭제·auxiliary, 금지 파일 종류, 파일 수/바이트/깊이 상한, 복사 중 실패 | 전체 목록/hash/delta가 독립 기대값과 일치. 거부는 명시적이며 미완성 최종 경로 없음 |
| 경계/다음 실행 | cgroup 이동/재위임 시도, control·관리 socket·이전 source/결과 접근, readonly 결과 쓰기 시도 | 준비된 canary의 접근 거부, 자기 source는 정상 읽기/쓰기. 새 실행은 이전 실행이 확정 정리된 후에만 허용 |

접근 거부는 관리자에게 실제 대상이 존재하는지 먼저 확인하고 mount/namespace 증거와 결합한다. 경로 오타의 ENOENT나 빈 cgroup만으로 통과하지 않는다. 전체 종료 확인 뒤 fixture의 예정된 지연 쓰기 시점을 넘겨 관찰하고 원본/수집 결과의 불변성을 대조한다. 이 관찰은 kernel 상태/권한 증거를 보완할 뿐 대체하지 않는다.

정상 결과를 읽는 검증 container는 단순 파일 검증기이며 Vendure evaluator가 아니다. 이 container도 같은 lifecycle로 끝내고 읽기 전용 소비를 확인한다. 이번 범위에서 악성 커널 exploit·모든 I/O 형태·네트워크 격리 전체·실제 모델 도구 inventory를 검증했다고 주장하지 않는다.

## 7. 중단과 완료 조건

20분 환경/90분 핵심 경로/150분 탐색/180분 회차 상한을 지킨다. 후보/버전 교체·호스트 권한 확대·범용 플랫폼·Vendure 준비/실제 CLI 연결이 필요하거나 경계 이탈/종료 확인 실패의 원인을 남은 시간 내 검증할 수 없으면 중단한다. 실패를 숨기기 위한 fixture 약화나 상태 조회 우회는 금지한다. 작은 근거 있는 수정은 같은 예산에서 수행하고 최초 실패도 보존한다.

판정은 `fixture-boundary-passed`(필수 표·반복·수집·부정 경로·정리 모두 통과), `inconclusive`(시간/증거 부족), `blocked`(승인 범위 내 진행 불가 원인 확인)로 둔다. 부분 통과/미실행은 항목별로 남긴다. 명령 exit0이나 정상 사례만으로 전체 통과를 선언하지 않는다.

공통 완료 조건은 재검토 가능한 실제 실행/실패 증거, 구현/환경/입력 지문, 단계별 시간·비용, 소유 자원 정리 또는 구체적 복구 인계, 기존 자료/production 차단 보존이다. **fixture-boundary-passed도 R11 전체 해결이나 본 비교 준비 완료를 뜻하지 않는다.** 독립 리뷰 전 R11 unresolved, R12 기존 검증 범위, trialAuthorized/readyForTrial=false·results=null·모델/provider/본 비교0회를 유지한다. 실패 인계도 공통 조건을 충족하면 이번 조사 작업을 마칠 수 있다.

## 8. 증거와 저장소 인계

새 `experiments/domain-model/s2/verification/<실제 날짜>-lifecycle-fixture/`와 `docs/reviews/<실제 날짜>-s2-lifecycle-fixture.md`에 남긴다. 이미 존재하면 새 suffix를 붙이고 과거 manifest/원시 증거를 덮어쓰지 않는다. systemd unit 설정·게스트 버전·kernel/cgroup·image/실제 container 대응, 당시 실행본과 모든 shell/Python/Node 하위 파일을 재귀 hash로 묶는다. manager 원시 상태/명령/exit·생존 신호·상태 전이·cgroup 증거·파일 대조·실패 주입·반복 분모를 보존한다. 자기 commit hash를 파일에 넣는 순환 지문은 피한다.

보고서는 결론/범위 → 필수 표 결과 → 정상/timeout/사망별 흐름 → 구현 선택/실패와 수정 → 비용/잔존 자원 → 후속 미검증 순서로 작성한다. 최초 시계·host/guest clock domain 차이·실제 정지 지연을 공개한다. 늦은 쓰기 없음과 정상 제출 자격을 구분한다. 새 경계 코드는 구현이며 과거 모델의 agent 효용이나 FCA 기여에 대한 결과는 아니다.

전체 검증 후 전용 worker·검증 container·임시 systemd unit/slice·VM/image/volume·작업 prefix를 정리하고 실제 부재/종료를 확인한다. 기존 cache는 보존하고 URL·시작 전 inventory·hash로 소유권을 확인한 신규 cache만 삭제한다. 공용 prune을 하지 않는다. cleanup 실패 시 대상 ID/경로·관측 상태·복구 명령을 인계한다. VM 폐기만으로 개별 fixture 종료/수집을 통과 처리하지 않는다.

`pnpm check`와 변경한 경계의 의미 있는 부정 회귀를 실행한다. 제품 분석/원래 fixture 의미를 바꾸지 않으므로 `pnpm experiment`나 기존29제출 전체 교정은 기본 요구가 아니다. 호스트 검사와 게스트 검증을 구분하고 기존 production/live 거부 및 fixture 기록의 승격 거부를 실제 확인한다. 시간 안에 검사를 끝내지 못하면 미완료를 기록하고 검증 없이 merge하지 않는다.

PROGRESS·ARCHITECTURE·ROADMAP·REVIEW_CONTEXT·관련 README를 실제 결과와 리뷰 대기로 갱신한다. 중요한 구현 선택은 DECISIONS에 근거·한계와 함께 추가한다. staged diff 검토 후 지속 승인에 따라 commit → push → PR/자체 검토 → 필수 검사·검증한 head 확인 후 merge → 로컬 main 동기화한다. **성공해도 이후 단계는 시작하지 않고 결과 리뷰를 기다린다.**

기술 근거: [Linux cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html), [nerdctl2.4.2 명령 계약](https://github.com/containerd/nerdctl/blob/v2.4.2/docs/command-reference.md), [systemd service 설정](https://github.com/systemd/systemd/blob/main/man/systemd.service.xml). 문서의 지원과 실제 guest의 동작을 구분해 검증한다.
