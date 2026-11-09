# S2 평가 계약 R8/R9/R10 보완 인계 — 2026-11-09

**보완 구현·자체 검증 완료, 독립 재검토 대기**다. 실제 제출 타입 검사와 요청 인자 판정을 추가했고 참조 수정의 환불 범위 회귀를 보완했다. `readyForTrial:false`이며 본 비교·H-O/H-F 효과·사람 의미 승인·S3를 수행하거나 완료로 주장하지 않는다.

기준 main `af5e56ffeb3875bb2545c04ca857095e4227c6b2`, 작업 브랜치 `codex/s2-contract-fix`, 미병합 의존 브랜치 없음. [개발 지시](2026-11-09-s2-contract-fix-instructions.md), [독립 리뷰](2026-11-09-s2-preparation-independent-review.md), [평가 계약 v2](../../experiments/domain-model/s2/evaluation/TASK-REVIEW.md), [실행 README](../../experiments/domain-model/s2/README.md)를 기준으로 한다. 다른 checkout의 브랜치를 전환하지 않았다.

## 발견별 전후 결과

| 항목 | 수정 전 재현 | 이번 구현·실측 |
| --- | --- | --- |
| R8 | baseline 진단0, 역사적 참조 진단5에도24/24 | 실제 원래 클래스/호출자·추가 helper 검사. 새 참조 진단0·52/52, 역사적 진단5를 거부하고 behavior not-run |
| R9 | 잘못된 주문 ID·환불 결제/금액도24/24 | 전체 payload·횟수·순서 비교. 주문 ID/결제 ID/금액/취소 line ID/수량 변형을 각각 진단0 후 동작에서 검출 |
| R10 | 환불만+공백 보존에서 baseline7/7·참조6/7 | 취소가 실제 있을 때만 guard, 취소 payload만 trim. 환불만 정상/앞뒤 공백/공백만 및 혼합 환불 reason 보존. 두 범위 회귀 변형 검출 |

수정 전 원래 oracle/독립 probe를 새 경로에서 재실행해 [before-probes](../../experiments/domain-model/s2/verification/2026-11-09/before-probes.json), before-*-cases.json.gz와 원래 교정 요약을 보존했다. 과거 리뷰/probe·2026-11-08 결과는 수정하지 않았다. 새 분모52는 두 입력 fixture의 보존16+요구36이다. 과거24라는 분모를 유지하려고 새 사례를 제외하지 않았다.

## 타입 문맥·소스 결합과 상태

`submission.ts`는 완전한 제출 root의 파일 snapshot을 읽는다. 일반 제출의 누락 원본을 baseline으로 보충하지 않는다. 교정 runner는 별도로 `explicit-baseline-delta`를 기록하고 원본+선언된 추가/수정/삭제를 구성한다. 동일 source snapshot을 CompilerHost와 executor가 소비한다. 실제 Program/제출/실행 hash가 일치해야 전체 합격이며 실제 완전한 제출 CLI와 delta 참조의 submissionId도 일치했다.

고정 Vendure revision `534e6003534f74761e82de1b8c6061cba89945d1`, 원래 scoped config·strict·의존성을 유지했다. Node22.19.0/TS5.9.3, baseline Program1,638·진단0이다. helper 제출은1,639파일이며 추가 helper 본문과 import를 검사한다. 설정 JSON은 환경 고정값을 사용하고 설정/비TS/삭제·검사 범위 밖 변경은 미지원이다. 새 설치·Angular/DB 구축·캐시 수정·진단 필터·stub/any/오류 억제는 없다.

`typecheck`에는 code/file/line/column/message, 원래 설정/도구, 전체 제출·입력 지문, 검사 파일 및 변경 포함 여부를 남긴다. 실패/미지원이면 `behavior:not-run`과 이유, 집계 null을 기록한다. 실행 seam/의존/예외 한계는 unsupported, 기대값 불일치는 failed다. overall은 타입·동작·sourceBinding 모두 통과해야 passed다. CLI exit0은 관찰 수집 완료이고 전체 합격과 별개다. 입력/환경 준비 오류는 not-run 보고와 exit1이다.

## 요청 기대값·실행 범위

기대 요청은 제출 출력과 독립적인 fixture/계약이다. 서로 다른 주문/결제/line 식별자, 수량1/2 및3/4, 금액10/75, 배송 flag true/false, 포함/제외 line/payment를 사용했다. 취소 orderId/reason/lines/cancelShipping과 환불 paymentId/amount/lines/reason/shipping/adjustment를 판정한다. 호출 시점에 복제하며 객체 key/lines 순서는 무시하되 lines 중복·누락·수량과 호출 순서/횟수는 유지한다. undefined 객체 필드 부재는 동일 JSON 전송 의미로 취급한다.

부모/dialog는 같은 주문 상태를 사용한다. 정상 취소→환불, 취소 오류 결과 후 환불 중단, dismiss/invalid의 요청0, active lines 생략을 확인한다. 원래 UI에서 truthiness로 배제되는 빈문자/null/undefined는 강제 메서드 입력으로 구분했다. HTML·constructor/field/상속/decorator·Angular/실제 네트워크/서버·동기 예외/stream error 정책 전체는 평가 밖이다. 기존 Promise/async·미검토 operator 미지원 회귀를 유지한다. VM은 격리가 아니다.

새 참조 수정은 취소 service 반환 타입을 유지한 빈 Observable로 초안(a)을 구현한다. 환불 dialog는 실제 취소 lines가 있을 때만 검사하고 환불 reason을 바꾸지 않는다. 별도 상대 helper 해법도52/52이므로 특정 diff/함수명을 정답으로 요구하지 않는다. 최종 실패 처리 정책·UI 표시/닫힘·B/C 의미 동등성·oracle 원문 충실성은 독립 검토 전이다.

## 실제 교정 행렬

타입 열 괄호는 진단 수다. 동작은 보존·요구 순서다. 동작 결함13종은 모두 새 참조에 독립 적용했고 **진단0 후 assertion 불일치**로 검출했다. 타입 오류 때문에 거부된 것을 동작 검출로 세지 않았다.

| 제출 | 타입 (진단) | 보존 · 요구 | 전체 |
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

[원시 교정](../../experiments/domain-model/s2/verification/2026-11-09/oracle/)에 제출별 전체 진단·기대/실제 요청·실패 사례·상태·소스/환경/평가기 hash와 원문 메서드 anchor/구간, 변경 전후 텍스트를 gzip JSON으로 남겼다. 해석을 위한 [요약](../../experiments/domain-model/s2/verification/2026-11-09/oracle/summary.json)도 있다. 참조/교정 패치는 평가자 전용이다.

## 검증·재현·비용

- `pnpm check`: 타입 검사·214테스트/skip0·예제 빌드 통과. 새 항상 실행 fixture18개는 외부 cache 없이 타입 오류/구문/추가 helper/삭제/검사 범위·설정/상태 gate/payload 비교를 검증한다.
- `pnpm experiment`: 기존 비교4/4 통과.
- 22제출 교정을 다른 출력 경로에서 반복했다. [46파일 대조](../../experiments/domain-model/s2/verification/2026-11-09/evaluation-reproduction.json)는 gzip을 해제하고 wallTimeMs만 제외했다. 진단·실패/성공·요청·소스/환경/평가기 hash를 모두 유지해 일치했다.
- 새 준비 두 번의 비시간147파일·세 ID가 일치했다. [배포 감사](../../experiments/domain-model/s2/verification/2026-11-09/deployment-audit.json)는 과거 결과 대비 evaluator/run-plan.json과 timing만 다름을 확인한다. A/B/C142파일·모델12항목/16링크·fact22/candidate2·승인0 및 근거 bytes는 동일하다. [새 준비 자료](../../experiments/domain-model/s2/results/2026-11-09/)는 갱신한 평가자 metadata를 보존한다.
- 실제 A/B/C workspace 각각 원문4,735개+자료2/70/70개를 inventory/allowlist/hash로 대조했다. symlink/evaluator 파일0이다. 같은 호스트 폴더이므로 isolation은 unverified다.

평가 배치 두 번은63.774초/53.204초, 각각 baseline 환경 감사/Program1회 약3.287초/2.836초와 제출별 Program1회(22회)를 포함한다. 각 제출의 typecheck/behavior/환경 재검사 wallTimeMs를 별도로 기록했다. 새 준비는4.817초/4.668초·Program각1회다. 같은 호스트에서 개발 검사도 진행했으며 통제된 성능 벤치마크/속도 개선 주장은 아니다. 과거 동작 전용3초 교정과 작업량이 다르다. 실제 cache 지문은 배치 시작과 각 제출 뒤 재검사했다. 사람 작성/재작업·agent 효용/토큰 비용은 미측정이다.

재현 명령(저장소 root, 새 출력 경로 사용):

```sh
pnpm s2:oracle-check /tmp/ontosary-vendure-preparation-20261108/vendure work/s2-contract-oracle-a
pnpm s2:oracle-check /tmp/ontosary-vendure-preparation-20261108/vendure work/s2-contract-oracle-b
pnpm s2:verify-evaluation work/s2-contract-oracle-a work/s2-contract-oracle-b work/s2-contract-reproduction.json
pnpm s2:prepare /tmp/ontosary-vendure-preparation-20261108/vendure work/s2-contract-prepare-a
pnpm s2:prepare /tmp/ontosary-vendure-preparation-20261108/vendure work/s2-contract-prepare-b
pnpm s2:verify work/s2-contract-prepare-a work/s2-contract-prepare-b work/s2-contract-prepare-reproduction.json
pnpm s2:workspace work/s2-contract-prepare-a /tmp/ontosary-vendure-preparation-20261108/vendure B work/s2-contract-agent-b
pnpm s2:evaluate <complete-submitted-source-root> /tmp/ontosary-vendure-preparation-20261108/vendure <new-result.json>
pnpm check
pnpm experiment
```

기준 커밋에서 실행한 수정 전 명령은 `s2:oracle-check`와 `node docs/reviews/evidence/2026-11-09-s2-review-probes.mjs <cache> <new-out>`다. 역사적 probe는 과거 evaluator 인터페이스를 재현하는 코드로 보존하고, 새 runner에는 동등한 결함을 옮겼다. run-plan과 보고에 `s2-evaluation-v2-cancel-only` 및 실제 evaluatorId를 남겼다. [구현 지문/검사 요약](../../experiments/domain-model/s2/verification/2026-11-09/implementation.json).

완료 조건1~5는 위 타입·동작·교정·전체 검사·배포/재현 증거로 인계한다. 조건6의 미정 정책/사람 검토·실제 격리·agent 모델/도구/예산/배정/공개 테스트는 그대로 미정이며 본 비교는 실행하지 않았다. 조건7은 현재 문서/ADR-026·Conventional Commit·PR 자체 검토/원격 반영 절차로 완료한다. 다음 한 작업은 R8/R9/R10의 독립 재검토이며 이 문서는 reviewer의 해결 판정을 대신하지 않는다.
