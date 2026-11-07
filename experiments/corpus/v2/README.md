# Corpus evaluator V2 — 2026-11-08

R4/R5의 평가 계약 보완이다. 코어·원본 corpus·TypeScript 버전·분석 범위·상한은 V1과 같다. [수정 인계](../../../docs/reviews/2026-11-08-corpus-contract-fix.md), [새 검토표](../results/2026-11-08-v2/review.md), [라벨별 전후 대조](../results/2026-11-08-v2/label-changes.json)를 함께 읽는다.

## 버전과 재현

루트의 `labels.json`, `evaluate-labels.mjs`, `run.mjs`와 2026-11-07 결과는 **R4/R5가 있는 역사적 V1**으로 보존했다. V1의 `correct`를 강한 자연어 주장 전체의 검증으로 읽지 않는다. 현재 기본 명령은 V2다. 두 버전 모두 기존 hash 검증 다운로드 cache를 쓰며 원본 코드를 실행하지 않는다.

```sh
pnpm experiment:corpus:prepare
pnpm experiment:corpus:v1 work/corpus-v1-a
node experiments/corpus/verify-reproduction.mjs experiments/corpus/results/2026-11-07 work/corpus-v1-a
pnpm experiment:corpus work/corpus-v2-a
pnpm experiment:corpus work/corpus-v2-b
node experiments/corpus/verify-reproduction.mjs work/corpus-v2-a work/corpus-v2-b
node experiments/corpus/v2/check-mutations.mjs
pnpm check
pnpm experiment
```

출력은 새 디렉터리만 허용한다. V2의 `summary.json`은 label/evaluator 버전과 양쪽 입력·구현 hash, 원래 source/lockfile/dist hash를 기록한다. `label-changes.json`에는 24개 라벨별 이전 주장/판정, 새 주장/판정/checks/unverified, 변경 이유가 있다. `analysis-unchanged.json`은 V1 대비 분석 raw 산출물 11개의 byte 일치를 확인한다. `timings.json`은 재현 비교에서 제외한다. 실제 의존성 경로가 달라지면 ID도 달라질 수 있다는 V1의 환경 제한은 유지된다.

V2 입력은 V1 관찰과 독립 리뷰 이후 원문을 재검토해 작성했다. 새 blind dataset이나 첫 관찰 전 사전 등록이라고 주장하지 않는다. 기대값은 unchanged source의 `DateType | number | string`, `readonly T[]`, type alias/interface 선언 및 실제 사용 위치에서 작성했다. scan/FCA에서 기대값을 복사하지 않았다.

## `correct`가 검사하는 범위

모든 라벨의 선언 file/UTF-16 offset·이름을 대조하고 source/target/use/other/parameter/condition anchor가 있는 경우 원문과 고유 anchor·행·offset을 검증한다. 컴파일 오류나 누락된 source reader/필수 계약은 indeterminate다.

| kind | 자동 검사 | 포함하지 않는 의미 |
| --- | --- | --- |
| function | 해당 위치·이름의 FunctionFact 존재 | 함수 구문 세부 종류, 클래스 소속, generic 인자/제약 |
| type | 해당 위치·이름·expectedKind, 명시된 expectedType | 명시하지 않은 전체 타입 구조·generic 제약 |
| parameter | 이름·명시된 위치·expectedType | 구조적 타입 호환성, 런타임 입력 보장 |
| field | 소유 타입의 위치/종류, 필드 이름·타입 문자열 | private 접근 제어·런타임 상태 의미 |
| condition | 명시된 kind·원문·위치 | 경로 조건, 실제 실행, 논리 정규화 지원 |
| distinct-types | 양쪽 위치·이름·kind와 서로 다른 ID | 상속 경로·구조적 동일성·업무 개념 동일성 |
| reference / property | source AST상의 본문 사용 위치 + facts의 use→target edge, property이면 property fact도 요구 | 실제 실행 여부·전체 호출 그래프·상속/모듈 경로 추론 |

`expectedType.exact`는 공백을 정규화한 타입 문자열이다. `unionMembers`는 단순 identifier/keyword 항목의 순서만 무시하는 정확한 합집합 표기 비교다. 일반 타입 동치/assignability를 계산하지 않는다. DateArg를 `never`, array 타입을 `number`로 바꾸면 mismatch다. 타입 종류를 바꿔도 correct로 남지 않는다.

reference는 명시적인 `use`와 `target`이 필요하다. TypeScript AST를 **평가기에서만** 읽어 선언/header 이름, 본문 내 선언 이름/객체 key, type 구문, 다른 중첩 함수의 사용을 제외한다. `usageKind: call`은 callee 위치여야 하고 `reference`는 일반 표현식 참조를 허용한다. dead code의 구문도 사용으로 관찰될 수 있으며 실행을 보증하지 않는다. 모든 self-target를 제거하지 않으므로 실제 재귀 호출을 인정한다. 결과에는 `useEvidence`와 `targetEvidence`를 별도 출력한다.

결과 status는 correct / missing / mislinked / mismatch / unsupported / indeterminate다. mismatch는 타입·종류·call/reference 등의 계약 위반이며 잘못된 target 연결인 mislinked와 구분한다. missing은 기대 사실/edge 부재, unsupported는 해당 선언 위치의 명시적 omission, indeterminate는 오류·모호성·불완전 계약이다. 검사별 `checks`와 `unverified`를 기계 결과에 남기며 후자는 검토표에도 표시한다. 사람이 검토했다고 자동 기록하지 않는다.

## 해석과 한계

두 버전 모두 22 correct / 2 unsupported지만 동일한 평가가 아니다. 특히 R4의 타입 검사와 R5의 정확한 사용 위치 검사는 강화됐고, 코어가 표현하지 않는 generic/클래스 소속/상속 등은 claim에서 분리했다. 개수의 동일성을 성능 불변 또는 향상으로 해석하지 않는다. V1의 약한 평가를 다시 실행할 수 있는 것과 그것을 현재 유효한 평가기로 권장하는 것은 다르다.

10개 actual-scan/변형 fact 회귀 검사는 R4/R5, 선언과 실제 사용의 좌표 차이, parameter/local declaration, 재귀/import/동명 shadow, 단순 참조와 call, 중첩 함수, source/target/use anchor, diagnostic gate, property, unverified를 확인한다. 기존 mock 중심 V1 테스트는 당시 계약의 기록이며 V2 검증을 대체하지 않는다.

업무 의미 승인·사람의 과업 시간·검색/LSP 대비 효용은 여전히 미검증이다. 후속 제품 실험은 utility label 검토와 구분하며 [업무 개념 탐색 실험 초안](../../../docs/experiments/concept-exploration-protocol.md)을 따른다.
