# S2 실행 전 준비 인계 — 2026-11-10

**자료·평가·공개 검사·계측 대역 구현과 검증을 인계한다. 전체 실행 준비와 실행 계약 동결은 완료하지 않았다.** macOS의 파일/네트워크 경계는 검증했지만 detached 자손이 process-group 종료를 벗어나는 반례가 남아 불변 제출 수집을 보장할 수 없다. 이 결함은 실행 차단 조건이다. 실제 모델 호출/본 비교0회, `trialAuthorized:false`, `readyForTrial:false`, `results:null`을 유지한다.

기준 main `300a004`(PR #31), 작업 브랜치 `codex/s2-trial-preparation`, 의존 브랜치 없음. [개발 지시](2026-11-10-s2-trial-preparation-instructions.md), [직전 독립 판정](2026-11-10-s2-modal-independent-review.md), [운영 명령·경계](../../experiments/domain-model/s2/trial/README.md)를 따른다. 제품 core/CLI·FCA·S1/V1/V2·모델 의미/순수 조회·과거 결과/리뷰는 바꾸지 않았다.

## 사용자 후속 결정과 과업 계약

구현 전 확인에서 사용자에게 기존 CLI 또는 API 실행기 확대를 질문했다. 사용자는 **기존 CLI·검증 가능한 macOS 격리만 사용하고 API로 확대하지 않으며, 누적 토큰 hard cap을 필수 준비 조건에서 제외**하도록 결정했다(ADR-029). 대신30분 제한과 raw usage·계측 범위/누락/참고선 초과를 보고한다.100,000토큰은 보고용 참고선이며 초과만으로 실패/준비 차단을 만들지 않는다. 격리·자료 공정성·제출 평가 결함은 차단한다. 이는 원래 지시 §5의 토큰 조건만 대체하며 실제 모델 호출 승인으로 확대하지 않는다.

`trial/task.ts`의 단일 TASK/공개 안내를 A/B/C에 동일 hash로 제공했다. 허용 문법·공개 타입 검사·production/auxiliary 수집 경계를 공개하며 해법이나 숨긴 입력값을 TASK에 넣지 않는다. 모델/정적 B/C는 변경 전 지식이며 새 사유 정책을 주입하지 않았다.

| 공개 요구 | private 관찰 |
| --- | --- |
| 정상 취소 reason 앞뒤 공백 제거 | 기존 전체 payload 비교 |
| empty/공백/null/undefined 무요청 | 요청0 + 종료 계약 |
| 혼합 invalid 취소와 후속 환불 중단 | 기존 호출 순서/횟수 |
| 환불만 동작·혼합 환불 원래 reason 보존 | 기존 보존/요구 사례 |
| invalid dialog undefined1회 | 실제 modal trace의 resolveCount/value |
| invalid service 값 없이 완료·예외/error 없음 | `stream.ts`의 next/complete/error/throw 관찰 |
| 닫기·취소 실패 후 중단·다른 payload 유지 | 기존 R9/R10 assertion |

## C 설명 문서와 대응 검토

B의68개 view는 byte 그대로 유지했다. C는 `guide.md`의12개 개념/흐름, `observations.md`의22개 코드 관찰, `roles.md`의2개 역할 후보, `evidence.md`의 원문/식별·좌표 부록으로 구성했다. 본문에 기존 해석·조건·불확실성·미확인 질문·상태·관계 from/to/방향/종류를 문장으로 보존했다. 긴 구성원 ID는 부록에서 추적하며 본문에는 동일 객체의 클래스/메서드명을 사용한다. B 전체 JSON을 C에 붙이지 않았다. C의 공개 문서에 다른 조건 코드/목록을 넣지 않았다.

[배포](../../experiments/domain-model/s2/results/2026-11-10-trial-preparation/)의 evaluator/parity68파일은 **1511개 leaf 단위**의 안정 ID, B경로/필드, C절·실제 줄 구간·텍스트 hash, 변환 종류, source evidence hash와 상태를 기록한다. 빈 배열/null과 반복 참조도 누락시키지 않는다. [개발자 자체 검토](../../experiments/domain-model/s2/verification/2026-11-10-trial-preparation/developer-parity-review.json)는 전체68view와1511대응을 대상으로 해석/관계/상태 문장과 템플릿을 검토하고 모든 값·줄 구간을 자동 대조한 기록이다. 모든 메타데이터 셀을 사람이 개별 승인했다는 의미가 아니다.

조건 부정·방향 반전·승인 상태 변경·근거 누락·C전용 해법 추가·단위 누락/중복을 회귀 fixture로 거부한다. 이는 **고정 문서의 drift/coverage 검사**이며 임의 자연어의 의미 동등성 증명이 아니다. semanticHash 하나로 승인하지 않는다. [핵심 흐름 대응](../../experiments/domain-model/s2/verification/2026-11-10-trial-preparation/policy-parity-review.json), [사람 검토 양식](../../experiments/domain-model/s2/verification/2026-11-10-trial-preparation/execution/HUMAN-REVIEW.md)을 준비했다. `humanParityReview:pending`, `semanticReview:pending`, 승인 지식0이다.

| 조건 | agent 파일 | 전체 bytes |
| --- | ---: | ---: |
| A | 4 | 43,425 |
| B | 72 | 136,552 |
| C | 8 | 150,552 |

총84파일이다. 공통 source tree4735파일·환경/의존성은 이 수에 포함하지 않는다. 차이는 문서 구조 그대로 기록하며 padding/정보 삭제로 맞추지 않았다. tokenizer가 없어 전체 tokens는 null이다. 실제 읽은 자료 bytes와 공급자 입력 tokens도 별개이며 임의 셸 읽기 완전 계측은 미구현이다.

## 공개 검사·배포·환경

`trial/public-check.ts`는 비공개 evaluator 없이 원래 strict scope와 원래 환경에서 실제 제출/추가 helper를 검사한다. [7개 공개/비공개 타입 대조](../../experiments/domain-model/s2/verification/2026-11-10-trial-preparation/public-private-type-equivalence.json)에서 baseline/reference/helper는 진단0 통과, helper 타입/구문/누락·삭제는 동일 진단으로 실패한다. 공개 검사는 타입 진단이며 private 범위/동작 합격을 대신하지 않는다.

원래 cache를 read-only로 다루고 별도 환경에 public source·의존성·scope/common lib·TypeScript/Node/public tool만 복제했다. 새 설치/빌드나 새 의존성은 없다. Node22.19.0·TS5.9.3·Darwin arm64다. 85416개 dependency 파일/link의 manifest를 기록하고 일반 파일 bytes를 원래 cache와 대조했으며 link는 복제 환경 내부로만 해석됨을 확인했다. 복제 준비 실측은35.303초이며 과거 설치 재현이나 다른 플랫폼 동등성 주장이 아니다. Node/TypeScript binary·의존성 자체는 저장소에 커밋하지 않았다.

새 준비2회는 **157비시간 파일**이 일치했다. 실제 A/B/C workspace에서 동일 TASK/RUN hash·각 조건 정확한 allowlist84파일·source4735파일 hash·공개 타입 검사와 읽기 전용 자료를 확인했다. 조건은 evaluator만 알고 작업공간은 blind run ID와 같은 source/materials/tools/auxiliary/scratch 경로를 쓴다. [배포 감사](../../experiments/domain-model/s2/verification/2026-11-10-trial-preparation/deployment-audit.json), [실제 workspace 검증](../../experiments/domain-model/s2/verification/2026-11-10-trial-preparation/workspaces.json).

## 격리·종료·계측의 실제 결과와 미완료

설치된 Codex CLI `0.167.0-alpha.3.2`의 동일 named permission profile/사용자 권한에서 도구 대역과 공개 검사를 실행했다. 현재 turn_context의 `gpt-6-astra`/`high`와 bundled catalog를 확인했고 바이너리 hash를 남겼다. immutable backend snapshot과 service tier는 기록에서 확인하지 못했으며 모델 응답으로 추정하지 않았다. 실제 모델 요청·인증 공급·연결 시험은 하지 않았다.

최초 workspace 감사에서 최소 profile의 **package.json 읽기 예외** 때문에 원래 cache/package.json이 읽혔다. [수정 전 증거](../../experiments/domain-model/s2/verification/2026-11-10-trial-preparation/before-explicit-deny-workspaces.json)를 보존했다. 별도 Node 실행 파일을 공급하고 원래 cache·checkout·호스트 홈을 명시적으로 deny한 후 모든 조건에서 EPERM을 확인했다. 존재하는 외부 package.json canary도 거부됐다. 평가도 필요한 evaluator/근거/TypeScript만 별도 복제하고 호스트 홈 읽기를 거부한다.

[최종 격리·usage 대역 증거](../../experiments/domain-model/s2/verification/2026-11-10-trial-preparation/isolation-and-usage-probe.json)는 허용 소스 읽기/편집, 자료 변경 거부, 실제 존재하는 외부 canary·상위 경로·symlink·control 접근 거부, 외부 TCP/호스트 Unix socket 거부를 포함한다. owner의 chmod 후 snapshot 수정 시도도 거부한다. 없는 경로의 ENOENT를 격리 성공으로 세지 않았다. 알려진29교정과 complete-root도 제한된 복제 evaluator에서 수행했지만 임의 적대적 제출의 보안성까지 입증한 것은 아니다.

**남은 확정 차단:** 350ms 제한에서 실행기 그룹은 종료되지만 detached 자손은 살아남아 나중에 파일을 썼다. 실제 프로세스 종료 경계의 결함이므로 source snapshot의 최종 정지를 보장할 수 없다. 추가/수정/삭제·auxiliary 보존과 중간 변경 거부, read-only 평가 profile은 구현했지만 이 반례를 해결했다고 표시하지 않는다. macOS 권한 확대/계정 생성·새 container/유료 인프라를 도입하지 않았고 실제 agent 실행은 계속 차단한다.

수집 후 `snapshot-gate.ts`가 source/auxiliary 전체 hash와 평가기 파일 목록을 대조한다. 기존 reader가 건너뛸 `.git`/`node_modules` 내 생산 파일도 조용히 누락하지 않고 증거를 보존한 채 거부한다. 변경 후 hash 불일치도 거부한다. [reference snapshot 검증](../../experiments/domain-model/s2/verification/2026-11-10-trial-preparation/snapshot-equivalence.json)은 제한된 read-only 평가에서 complete-root/delta와 동일52사례·source 지문을 확인했다. 이 검사는 위 종료 차단을 해소하지 않는다.

추가 미검증은 실제 CLI 세션의 도구 inventory·credential 경로·전역 지시/플러그인 유입 배제, immutable 모델 버전 및 CPU/메모리 상한이다. 독립 검토 뒤 과업과 무관한 최소 연결 점검이 필요하면 별도 승인 절차를 논의한다. 이번에 그 확인을 핑계로 실제 과업을 보내지 않았다.

usage 대역은 raw JSONL을 보존하고 input99,999+output5=100,004로 기록한다. cache90,000과 reasoning2는 이미 각 총량에 포함되어 다시 더하지 않는다. 중복·충돌·누락/실패·참고선 초과를 테스트했다. 누락 시 total은 null이고 관찰된 하한만 남긴다. completed-turn 계측이며 in-flight/공급자 내부 요청의 완전 계측은 아니다. timeout·자손 반례·최종 snapshot을 짧은 실제 제한으로 검증했고30분을 기다리지 않았다. 실제 provider usage/읽힌 자료 tokens는 미측정이다. 제작/검토의 과거 비용·사람 재작업 시간은 null이며 소급 추정하지 않았다.

## 평가 v4와 교정 행렬

`s2-evaluation-v4-termination`은 기존52사례(보존16+요구36)를 유지하면서 종료 assertion을 추가한다. `stream.js`를 evaluator 지문에 포함했다. 미지원 실행 Failure는 unsupported를 유지하며 실제 동기 예외/stream error는 승인된 invalid 정책의 실패로 관찰한다. 정상 service 호출의 예외/error는 기존 unsupported 경계를 유지한다. 기존24제출의 submissionId·판정·payload assertion은 그대로다. 새5개는 요청0이어도 잘못된 방출/미완료/error/throw/null반환으로 거부된다. 기존 R8/R9/R10·15동작 결함과 새5개, 총20동작 결함은 모두 타입 통과 후 failed다.

| 제출 | 타입 (진단 수) | 보존 · 요구 | 전체 |
| --- | --- | --- | --- |
| baseline | passed (0) | 16/16 · 6/36 | failed |
| reference | passed (0) | 16/16 · 36/36 | passed |
| historical-reference | failed (5) | not-run | failed |
| helper | passed (0) | 16/16 · 36/36 | passed |
| helper-type-error | failed (1) | not-run | failed |
| helper-syntax-error | failed (1) | not-run | failed |
| missing-helper | failed (3) | not-run | failed |
| deleted-module | failed (4) | not-run | failed |
| out-of-scope | unsupported (0) | not-run | unsupported |
| direct-only | passed (0) | 16/16 · 16/36 | failed |
| no-trim | passed (0) | 16/16 · 24/36 | failed |
| force-cancel | passed (0) | 10/16 · 36/36 | failed |
| dismiss-request | passed (0) | 14/16 · 36/36 | failed |
| continue-after-failure | passed (0) | 14/16 · 36/36 | failed |
| omit-followup-refund | passed (0) | 16/16 · 32/36 | failed |
| wrong-order-id | passed (0) | 10/16 · 24/36 | failed |
| wrong-payment-id | passed (0) | 10/16 · 32/36 | failed |
| wrong-refund-amount | passed (0) | 10/16 · 32/36 | failed |
| wrong-cancel-line-id | passed (0) | 14/16 · 32/36 | failed |
| wrong-cancel-quantity | passed (0) | 14/16 · 32/36 | failed |
| guard-refund-only | passed (0) | 14/16 · 36/36 | failed |
| trim-refund-reason | passed (0) | 12/16 · 34/36 | failed |
| wrong-modal-order | passed (0) | 12/16 · 32/36 | failed |
| wrong-modal-active | passed (0) | 14/16 · 32/36 | failed |
| invalid-service-value | passed (0) | 16/16 · 28/36 | failed |
| invalid-service-never | passed (0) | 16/16 · 28/36 | failed |
| invalid-service-error | passed (0) | 16/16 · 28/36 | failed |
| invalid-service-throw | passed (0) | 16/16 · 28/36 | failed |
| invalid-dialog-null | passed (0) | 16/16 · 28/36 | failed |

두 제한된29제출 교정은 gzip 해제 후 wallTimeMs만 제외한 **60파일**이 일치했다. modal/termination trace·진단·요청·실패 사례·지문을 제외하지 않았다. complete-root CLI와 delta의 submissionId·전체52case/요청/modal/종료 관찰·evaluatorId도 같다. [원시 교정](../../experiments/domain-model/s2/verification/2026-11-10-trial-preparation/oracle/), [반복 검증](../../experiments/domain-model/s2/verification/2026-11-10-trial-preparation/evaluation-reproduction.json), [CLI 동등성](../../experiments/domain-model/s2/verification/2026-11-10-trial-preparation/complete-root-equivalence.json).

`pnpm check`: **252테스트, skip0**, 타입 검사·예제 빌드 통과. 새 회귀22개는 외부 Vendure 없이 실행된다. `pnpm experiment`: **4/4** 통과. 환경/공개 검사·거부 probe는 별도 실제 실행으로 기록하며 없는 환경을 skip 성공으로 포장하지 않는다. 교정/준비 시간은 로그의 실측이며 성능 비교가 아니다.

## 산출물과 다음 단계

- baselineId `7707db72b46a21570152b2b8920e6526996952abaac1574642d6638c477ba0d8`와 modelId `2ba6c772263da8814256efaa5491c69f723d79157a7f8aad7f22d898e297e5cf`는 유지했다.
- 새 bundleId `ab522d70da78c0e71b6ddc01f32056980b85de245e150bdde55f39c16a17c509`는 TASK/안내/C 변화와84개 agent 자료를 식별한다.
- 실행 준비 기록은 별도 [execution-manifest](../../experiments/domain-model/s2/verification/2026-11-10-trial-preparation/execution/execution-manifest.json)에 static manifest·run-plan·구현·CLI/환경/probe 증거 hash와9개 예정 실행·예산·평가 방식을 연결한다. 자기 ID는 자기 hash 입력에서 제외한다. 확정되지 않은 실행 환경을 동결 완료라고 표시하지 않는다.
- 9개 실행은 모두 not-run, 각 조건3회이며 seed 기반 블록/위치 균형이다. 성공·타입/동작 실패·미지원·timeout/미제출·환경 실패를 모두 남기고52사례를52표본으로 세지 않는다. 환경 장애만 최대1회 대체하고 원래 시도를 보존한다. 성능 재시도는 금지하며 반복 장애/공통 평가 결함은 배치 중단이다. 블라인드 diff 검토 양식도 포함했다.

완료 조건1·2·4 및 문서/배포 부분은 위 증거로 인계한다. 조건3의 전체 격리/종료·실제 실행 설정은 **미충족**이며, 따라서 조건5의 실행 환경 전체 동결도 미완료다. 다음은 detached 자손의 강제 종료 경계를 해결할 수 있는 방법의 검토, CLI 격리 미검증 항목 확인, 이 변경의 독립 리뷰와 C 사람 대응 검토다. 새 플랫폼·광범위한 권한 변경이 필요하면 구체적 대안을 별도 결정한다. H-O/H-F 결과·업무 의미 승인·S3는 없다.

재현은 [trial README](../../experiments/domain-model/s2/trial/README.md)의 명령과 같은 입력/새 출력 경로를 사용한다. private 교정은 빌드 후 `node work/s2-build/trial/isolated-command.js <codex> <repo> <cache> <new-out> work/s2-build/evaluation/oracle-check.js <cache> <new-out>/oracle`로 실행하고 두 결과를 s2:verify-evaluation으로 비교한다. complete-root는 마지막 script/인자를 evaluation/run.js와 완전한 제출 경로로 바꾼다. 본 비교 명령은 현재 거부되는 것이 정상이다.
