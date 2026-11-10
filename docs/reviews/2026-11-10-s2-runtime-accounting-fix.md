# S2 R12 보완과 R11 차단 인계 — 2026-11-10

**R12를 구현·자체 검증했으며 R11의 모든 writer 종료 경계는 확보하지 못했다.** production 수집·평가를 명시적으로 차단하고 진단/알려진 참조 교정을 분리했다. 전체 준비 완료나 독립 해결 판정이 아니다. 실제 모델 호출·연결 시험·비교 실행은0회이며 `trialAuthorized:false`, `readyForTrial:false`, `results:null`을 유지한다.

기준 main `ef60bc98d408114b1368ed46e58b26ed726054be`, 작업 브랜치 `codex/s2-runtime-accounting-fix`, 의존 브랜치 없음. 최종 구현 파일 지문과 검증 로그는 [implementation](../../experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix/implementation.json), 최종 저장소 commit은 병합 PR과 완료 응답에서 확인한다. [개발 지시](2026-11-10-s2-runtime-accounting-fix-instructions.md)·[독립 리뷰](2026-11-10-s2-trial-preparation-independent-review.md)를 따른다. 제품 core·FCA·모델/자료 의미·평가기 v4·과거 증거를 변경하지 않았다.

## R11: 선택 근거와 남은 차단

구현 전 [선택 기록](../../experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix/SELECTION.md)에 조사·비용·탈출 경로를 남겼다. 환경은 macOS26.6.2(25G83)/arm64, Node22.19.0, Codex CLI0.167.0-alpha.3.2이며 [바이너리/SDK 지문](../../experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix/before/environment.json)을 기록했다.

기존 CLI profile에서 원래 detached 반례를 두 번 재현했다. 설치 launchd 설명은 정리 대상을 같은 process group으로 한정하므로 설정 이동만으로 해결되지 않는다. 설치 SDK와 [Apple 공개 헤더](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/sys/event.h)는 NOTE_TRACK/NOTE_CHILD 미지원을 명시한다. 실제 kqueue 등록도 ENOTSUP(45)를 반환했다. [최소 C probe](../../experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix/before/native-track.c)와 [결과](../../experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix/before/native-track.json)를 보존했다. 단발 ps·후손 폴링·이름 검색을 보안 경계로 덧붙이지 않았다.

선택한 구현은 **강제 종료 해결책이 아니라 fail-closed 수명주기**다. running → stopping → blocked로 귀결하며 종료 확인을 발급하는 경로가 없다. 정상 exit·비정상 exit·timeout·spawn 오류·처리 가능한 SIGINT/SIGTERM/AbortSignal을 구분하고, task exit/signal·제한 시각·stop/parent-exit/반환 시각·정리 시간과 오류를 남긴다. 부모가 끝나도 collectionAllowed=false다. process-group SIGKILL은 해당 그룹에 대한 진단용 best effort이며 unrelated PID를 검색/종료하지 않는다.

정리 대기는250ms로 제한했다. 자손이 stdout/stderr를 계속 잡아도 무한히 기다리지 않고 pipe-close-deadline으로 기록한다. 실제 스케줄링 지연은 기록된 시각을 따르며250ms의 실시간 보장을 주장하지 않는다. task 예산은1,800초 그대로이고 정리 지연을 추가 작업 시간으로 허용하거나 deadline 순간 snapshot이라고 소급 표현하지 않는다. supervisor 자체 SIGKILL/호스트 장애는 자손 종료를 보장하지 못하며 live 다음 실행은 시작할 수 없다.

`snapshot()`과 `checkedSnapshot()`/`evaluate-snapshot.ts`는 production 수집·평가를 항상 거부한다. 발급된 종료 authority가 없으므로 caller의 true 플래그나 위조 manifest는 통과하지 않는다. `collectDiagnostic()`은 supervisor가 보유한 객체 identity, 해당 실행의 source/auxiliary 경로·profile 지문과 연결하고 **diagnostic, validSubmission=false**로만 수집한다. manifest에도 종료 미확인을 남긴다. 추가/수정/삭제·auxiliary를 보존하고 중간 변경/링크/누락/수집 실패는 거부하며 실패 staging을 정상 산출물로 노출하지 않는다.

`checkedDiagnosticSnapshot()`은 전체 source/auxiliary·manifest checksum·reader coverage를 검사한다. checksum/chmod만으로 OS 불변성을 주장하지 않는다. 실제 같은 UID/profile에서 source·auxiliary·manifest·checksum의 chmod/쓰기/추가가 거부됐다. 기본 production 평가 entry는 소스나 cache를 열기 전에 차단한다. 별도 `evaluate-calibration-snapshot.ts`는 trusted baseline에서 생성한 알려진 reference 전체 bytes와 일치하는 fixture만 읽기 전용 환경에서 평가한다. 이 결과는 유효한 trial 제출이 아니다.

## 실제 macOS 관찰

[반복 probe](../../experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix/runtime-probe.json)는11종×2회, 각기 새 임시 경로를 사용했다. 자손 fixture는 스스로 종료하고 바깥 정리가 그 시간을 기다린다. 이는 시험 정리이며 모든 writer 종료 증명으로 쓰지 않는다.

| 사례 | 관찰과 판정 |
| --- | --- |
| 정상 도구 | 정상 exit/EOF. 그래도 production 수집 차단 |
| 일반 timeout | 약350ms 제한 뒤 반환, task timeout과 collection 차단 분리 |
| 부모 정상 종료 후 자식 | 부모 종료 뒤 늦은 쓰기 재현. R11 미해결 |
| detached·분리 손자·열린 핸들 fixture | 늦은 쓰기 재현. 다음 workspace canary 쓰기는 EPERM이고 원래 bytes 유지 |
| 열린 stdout/stderr | 약603ms에 반환, pipe-close-deadline 기록. 미완전 로그 |
| 출력 용량 초과 | captured prefix와 outputTruncated 명시, usage total=null |
| spawn 오류·중단·주입한 kill EPERM | 제한 안에 blocked 반환, 오류/종료 사유 보존 |
| 위조 receipt·production 평가·read-only 쓰기 | 거부. 진단 자료를 sealed로 승격하지 않음 |

[추가 probe](../../experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix/extra-runtime/report.json)는 실제 exit7·supervisor SIGINT·잘린 stdout의 압축 원문/지문을 보존한다. kill EPERM은 결정적 오류 주입이며 OS가 실제 권한 오류를 발생시켰다는 주장이 아니다. [신규 접근 probe](../../experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix/access-probe.json)에서 기존 외부 canary/package.json/상위 경로/symlink/control·TCP/Unix socket 거부도 유지했다.

초기 matrix에서는 새로 복사한 Node의 cold start가350ms를 소모해 child fixture 자체가 실행되지 않았다. 이를 성공으로 세지 않고 [실패/불충분 관찰](../../experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix/cold-start-inconclusive.json)을 보존했다. 기존 probe처럼 고정 Node warm-up을 과업 계측 전에 수행한 뒤 같은350ms·700ms 지연 쓰기로 다시 검증했다. 원래 탈출 동작을 제거하거나 제한을 늘리지 않았다. warm-up 시간은 별도 필드다.

## R12: 입력·identity·완료 의미

새 스키마는 `s2-usage-v2-turn-state`다. JSON을 unknown에서 검사하고 null/array/non-object·잘린 JSON·잘못된 type·usage를 issue로 남긴다. 정상 unknown object 이벤트는 비계측 행으로 보존한다. [공개 exec 이벤트 정의](https://github.com/openai/codex/blob/main/sdk/typescript/src/events.ts)와 설치 CLI help/기존 자료를 기준으로 순차 활성 turn을 관리한다. 해당 공개 소스가 설치 alpha 바이너리와 완전히 같거나 실제 provider 로그를 검증했다는 뜻은 아니다.

공개 지원 계약에 turn ID가 없어 시작 순서로 번호를 부여한다. 선택적 event id는 합성/수집 계층의 스트림 내 재전달 identity이며 turn id가 아니다. 동일 identity·동일 내용의 같은-turn 재전달만 한 번 처리한다. 다른 내용·다른 활성 turn에서의 재사용·서로 다른 완료 ID·ID 없는 추가 완료는 모순으로 표시하고 해당 turn의 이전 합계도 철회한다. 숫자가 같은 별개의 정상 turn은 각각 집계한다. 지원하지 않는 turn_id/중첩 순서는 추측해 정상화하지 않는다.

수치는 비음수 safe integer, cache≤input/reasoning≤output을 검사하고 누적 overflow도 거부한다. cache/reasoning은 이미 총량 안에 있어 다시 더하지 않는다. 미관측 세부값은 null이다. 완료 조건은 모든 관찰 turn의 정상 종료, 명시적인 정상 EOF·exit0·로그 무결성·종료 근거다. 현재 runtime의 종료 authority가 unverified이므로 **부모가 정상 종료해도 전체 total은 null**이다. 합성 정상 입력은 termination=fixture로 명시해 확정 집계 경로를 검사한다.

subtotal은 모순 없는 검증된 turn만 남긴 관찰 합계이며 소비 하한이라고 부르지 않는다. consumptionLowerBound는 unknown(null)이다. 확정 총량의 초과, subtotal에서 확인된 초과, 전체 미초과 여부를 구분한다.100,000은 참고선이고 hard cap/중단 규칙은 없다. runtime 종료/절단/읽기 오류를 `usageEnd`로 연결한다. [최종 코드로 원시 로그를 재집계한 결과](../../experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix/runtime-accounting-replay.json)는 실제 OS probe와 최종 계측 구현을 구분해 연결한다.

raw JSONL과 메모리 집계를 분리했다. 집계는1-based 행 번호/hash/turn/제외 사유를 남기며10,000행·행64KiB·총4MiB에서 중단한다. 무한 iterable도 이 상한에서 읽기를 멈춘다. 깊은 중첩 identity의 직렬화 오류도 전체 집계를 예외로 잃지 않는다. runtime은 stdout/stderr 합계4MiB prefix만 보존하며 절단을 완전한 로그로 표시하지 않는다. in-flight/공급자 내부 요청·청구 전체는 여전히 미관측이다.

| 독립 반례 | 수정 전 | 새 합성 계약 |
| --- | --- | --- |
| started → completed(10+2) | total12 | fixture 종료 근거에서12 |
| 정상 turn 뒤 started | incomplete | total=null, 정상 subtotal12 |
| 시작 없는 completed | 잘못된 total12 | total=null, lifecycle issue |
| 다른 완료 ID2개 뒤 미완료 turn | 잘못된 total24 | total=null, 모순된 turn 철회 |
| JSON null | TypeError | 구조 issue와 결과 반환 |

[18개 원시 fixture](../../experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix/accounting-fixtures.json)와 회귀 테스트에서 정상 다중 turn·중복/충돌·누락/실패·잘린 JSON·수치/누적 overflow·timeout/절단·상한을 검사했다.99,999+5=100,004, cache90,000/reasoning2의 중복 없는 subtotal과 초과4도 유지한다. 이는 실제 공급자 사용량이 아니다.

## 회귀·보존·동결

`pnpm check`: **303테스트, skip0**, 타입 검사·예제 빌드 통과. 기존252개에서51개 회귀를 추가했다. `pnpm experiment`: **4/4**. 새 runtime의29제출 교정1회를 기존 v4와 비교해 [60파일](../../experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix/evaluation-reproduction.json)이 gzip 해제 후 wallTimeMs만 제외하고 일치했다. R8/R9/R10·종료 정책·20동작 결함과 reference/helper52/52가 유지됐다. 평가기 자체를 바꾸지 않아 evaluatorId도 유지된다.

[알려진 참조 diagnostic](../../experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix/reference-equivalence.json)은 complete-root 방식으로 평가해 delta와 submissionId·52사례/요청/modal/종료 trace가 같다. 종료가 확인된 실제 agent 제출의 성공 사례는 없다. R11 미해결 부분을 fixture 결과로 대체하지 않는다.

TASK/B/C·agent84파일·모델12항목/16링크·승인0과 세 ID를 유지했다. bundleId는 `ab522d70da78c0e71b6ddc01f32056980b85de245e150bdde55f39c16a17c509`다. [보존·재사용 감사](../../experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix/preservation-and-reuse.json)에84개 bytes 지문, 공개 checker/환경 공급/workspace 모듈과 configuration/child environment의 불변 지문을 기록했다. 공통 권한·자료 공급을 바꾸지 않아 기존 A/B/C·공개/private7제출 대조·환경 증거를 그 범위에서만 재사용한다. 새 runtime 종료/계측의 통과 근거로 옛 probe를 재사용하지 않는다. cache 설치/빌드는 하지 않았다.

새 [execution manifest](../../experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix/execution/execution-manifest.json)는 동일 정적 bundle과 현재 구현/계측 스키마·새 종료/usage 증거·명시된 재사용 범위를 hash로 연결한다. executionId는 자기 자신을 제외해 산출했다. 과거 bundle/manifest/원시 리뷰는 그대로다. live entry와 production 평가 entry의 거부도 확인했다. [재현 명령·exit code](../../experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix/README.md)를 제공한다.

| 항목 | 상태 |
| --- | --- |
| R12 입력·turn·집계·종료 연결 | 구현·자체 검증 완료, 독립 판정 대기 |
| R11 반환 대기/진단·제출 분리 | 보완했으나 강제 종료 경계 unresolved |
| 전체 실행 준비·실제 모델/본 비교 | 차단, 실행0회 |
| C 사람 동등성·도메인 의미 승인 | 각각 pending, 승인 지식0 |
| 실제 CLI 도구/인증/전역 지시·플러그인 격리 | 미검증 |
| immutable backend 버전·자원 정책 | 기존 관측 한계/미동결 유지 |

다음 리뷰는 R12의 과소/과대 확정 여부와 production 차단 경계를 검토해야 한다. R11은 VM/container의 작업 단위 격리, 권한이 필요한 native 서비스, subprocess를 제한하는 도구 정책 중 비용·계약 차이를 결정한 뒤 진행할 수 있다. 선택 기록에 최소 범위/운영 부담을 남겼고 새 플랫폼·권한·API를 자동 도입하지 않았다. 작업 공수·과거 비용을 소급 추정하지 않았다. H-O/H-F 결과나 S3 구현은 없다.
