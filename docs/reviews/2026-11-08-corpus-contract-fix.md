# Corpus 평가 계약 R4/R5 수정 인계 — 2026-11-08

**평가기 V2에서 R4의 타입·종류 미검사와 R5의 선언 이름 오인을 보완했다. 기존 V1/원시 증거는 보존했고, 새 결과의 22 correct / 2 unsupported는 검사 범위가 달라진 판정이다. 이 수치를 정확도 향상이나 사람의 승인으로 해석하지 않는다.**

기준 main은 `7adf2d1f67016e2e6ab3545aa159ad8838fff180`(독립 리뷰 전달 포함), 작업 브랜치는 `codex/corpus-evaluator-contract`다. 제품 코어/CLI, source schema, 의존성·lockfile, 원본 corpus·manifest, 분석 범위와 상한은 수정하지 않았다. [개발 지시](2026-11-07-corpus-review-next-plan.md)의 작은 평가기 수정 범위다. 이 문서는 구현 담당의 검증·self-review이며 새 독립 리뷰나 사람 승인으로 표시하지 않는다.

## R4: 주장과 검사 범위를 일치시킴

24개 라벨을 모두 점검했다. 새 [V2 입력](../../experiments/corpus/v2/labels.json)은 각 항목에 이전 claim, 변경 이유, 명시적 계약, `unverified`, humanReview=pending을 남긴다. V1 관찰 이후의 수정이며 새로운 blind dataset이나 첫 관찰 전 작성이라고 주장하지 않는다. 기대값은 원본 타입 선언·매개변수·구문에서 작성했다.

| 항목 | V1 검사 / 문제 | V2 계약 |
| --- | --- | --- |
| date-fns-10 DateArg | 이름·좌표만 검사, `never`로 변형해도 correct | kind=alias 및 DateType/number/string union 항목 검사; generic 제약·일반 타입 동치는 unverified |
| p-queue-02 array | 매개변수 이름만 검사, `number`로 변형해도 correct | 매개변수 위치·이름과 `readonly T[]` 타입 문자열 검사 |
| Queue type alias | generic alias라는 주장에 비해 kind도 미검사 | alias kind 검사, generic 설명은 unverified |
| FunctionFact / enqueue / toDate | generic·method/class 소속까지 읽힐 수 있음 | 해당 위치·이름의 FunctionFact 존재로 claim 한정; 추가 설명은 별도 unverified |
| distinct types / inherited property | 상속·구조 설명과 identity 판정 혼재 | 양쪽 kind/identity, property use→target을 검사; 상속 경로·구조적 동치는 unverified |
| conditions | 원문 일치에 runtime 의미를 덧붙일 위험 | exact kind/text/location 추출만 주장; normalization과 runtime 의미 분리 |

`exact`는 공백을 정규화한 타입 문자열, `unionMembers`는 단순 identifier/keyword 항목 순서만 무시하는 비교다. 구조적 타입 호환성이나 일반 TypeScript 타입 동치를 구현한 것이 아니다. 각 검사에는 expected/actual/passed가 기록되며 `unverified`는 JSON과 사람 검토표에 모두 보인다.

## R5: 실제 사용 위치와 선언 대상의 분리

V2 reference/property 라벨은 source·use·target의 별도 anchor를 요구한다. unchanged source를 TypeScript AST로 읽어 사용 위치가 해당 함수 본문에 있는지, 선언/header/지역 선언 이름·type 구문·다른 중첩 함수의 사용이 아닌지 확인한다. `usageKind: call`은 callee 위치를 검사하고, 일반 reference와 구분한다. 그런 다음 scan의 **해당 use 좌표의 edge**가 명시한 target 좌표로 이어지는지 대조한다. property 라벨은 기존 property fact도 요구한다.

따라서 이름 offset과 선언 offset이 다른 `export function unused()`의 이름을 본문 사용으로 승인하지 않는다. 모든 self-target를 제거하지 않으므로 실제 recursive 호출은 통과한다. imported 함수와 동명 parameter의 target도 구분한다. 결과는 `useEvidence`와 `targetEvidence`를 별도 제공한다. 이는 정적 구문/참조의 대조이며 실행 여부나 전체 호출 그래프를 보장하지 않는다.

## 검증과 전후 상태

실제 TS scan 진단 0인 fixture로 최소 실패를 먼저 확인했다. V1 복사본을 대상으로 최초 **8개 검사 중 6개 실패 / 2개 통과**했다. 타입 변형이 correct로 남고 unused 선언 이름이 사용으로 통과하는 문제가 재현됐다. [실패 로그](evidence/2026-11-08-corpus-contract-red.txt)는 workspace 접두사만 치환한 기록이며 원본 로그는 로컬 work에 보관했다.

수정 후 property/판정 구분 검사를 더한 **10개 회귀 검사 통과**. 실제 선언과 이름의 서로 다른 offset, unused/parameter/local declaration 거부, recursion/import 사용, call과 일반 참조 구분, 동명 shadow, nested 함수, source/target/use anchor 오류, 진단 오류, property edge 부재, unverified 보존을 확인했다. 타입/종류를 바꾼 in-memory fact는 correct가 아니다. original corpus 코드는 실행하지 않았다.

[실행 가능한 mutation probe](../../experiments/corpus/v2/check-mutations.mjs)와 [새 관찰 JSON](evidence/2026-11-08-corpus-contract-results.json)은 다음을 assert한다. 역사적 probe는 역사적 V1을 계속 가리키며 그 결과를 수정하지 않았다.

| 입력 | V1 | V2 |
| --- | --- | --- |
| DateArg.type → never | correct | mismatch |
| array.type → number | correct | mismatch |
| unused의 선언 이름을 self-use로 제시 | correct | mismatch |
| recursive의 실제 호출 위치와 self-target | correct | correct, use/target 근거 분리 |

전체 검증:

- `pnpm check`: **7파일 / 99개 테스트**, core/example 타입 검사, production build 통과.
- `pnpm experiment`: 기존 인공 비교 **4/4** 통과, 기존 산출물 diff 없음.
- `pnpm experiment:corpus:v1`: 2026-11-07 결과와 비시간 **14개 파일 byte 일치**. [기록](evidence/2026-11-08-corpus-v1-reproduction.json).
- `pnpm experiment:corpus` 및 두 번째 V2 scanner 실행: 비시간 **16개 파일 byte 일치**. [기록](../../experiments/corpus/results/2026-11-08-v2-reproduction.json).
- V2 실행의 scan/FCA/단순 그룹/비교/실패 **11개 raw 파일은 V1과 동일**하다. [대조](../../experiments/corpus/results/2026-11-08-v2/analysis-unchanged.json). 원래 설정 실패, p-queue 전체 FCA 상한 초과, predicate 지원 0, 비교 0/2도 유지됐다.
- Node 22.19.0, pnpm 11.19.0, TS 5.9.3. 새 준비 다운로드는 하지 않았으며 source hash/anchor를 다시 확인했다. timings의 preparation 값은 cache에 남은 최근 준비 기록이고 이번 작업의 새 다운로드 시간으로 해석하지 않는다.

## 버전·라벨별 전후 대조

루트의 기존 V1 라벨/평가기/runner/common/manifest와 2026-11-07 결과·gzip·관찰 보고서·독립 리뷰는 그대로다. 새 기본 package 명령은 V2를 실행하고 `experiment:corpus:v1`으로 과거 경로를 유지한다. 재사용 코드를 소급 변경해 과거 fingerprint를 깨뜨리지 않도록 작은 V2 runner를 별도 보존했다. 양쪽 실행 방법과 판정 계약은 [V2 README](../../experiments/corpus/v2/README.md)에 있다.

새 [summary](../../experiments/corpus/results/2026-11-08-v2/summary.json)는 label/evaluator 버전·입력/구현 hash를 기록한다. [label-changes](../../experiments/corpus/results/2026-11-08-v2/label-changes.json)는 **24개 전부**의 전후 claim/status/checks/unverified/변경 이유를 연결하고 comparableAsAccuracyDelta=false로 표시한다. [검토표](../../experiments/corpus/results/2026-11-08-v2/review.md)는 source/use/target 링크와 미검증 항목을 보여준다.

24개 중 22개 correct, 클래스 모델링 2개 unsupported는 두 버전에서 같지만 강한 타입 검사·사용 위치 검사가 추가됐고 일부 자연어 claim은 좁아졌다. 이를 동일 과업의 성능 전후 비교로 계산하지 않는다. 실제 원본 타입이 틀렸다는 발견도 아니다. humanReviewed=0, approvedKnowledge=[], 사람의 검토 시간=null을 유지했다. Gate 2~4는 올라가지 않는다.

## 다음 별도 제품 실험

[업무 개념 탐색 절차 초안](../experiments/concept-exploration-protocol.md)을 추가했다. 실제 업무 애플리케이션의 한 개념에서 관련 타입·코드·조건 근거를 찾는 질문을 검색/LSP, 동일 facts의 단순 그룹, FCA와 비교한다. 참가자별 첫 노출 조건, 학습 효과, 정답 근거 분리, 실제 시간·오류·검토 부담 기록 절차를 제안했다.

**대상 앱/revision·정확한 과업·정답·참가자는 아직 확정하지 않았다.** 주문 취소 질문은 검토용 후보이며 탐색 기능 구현이나 사람 실험을 수행한 것이 아니다. 다음 세션에서 이 입력을 고정하고 필요한 방향 결정을 사용자와 확인한다. utility 라벨 재판정만으로 사용자 가치가 검증됐다고 주장하지 않는다.
