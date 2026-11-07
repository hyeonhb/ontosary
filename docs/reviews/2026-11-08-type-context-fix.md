# R5 타입 선언 문맥 수정 인계 — 2026-11-08

[개발 지시](2026-11-08-contract-review-next-plan.md)의 잔여 R5를 평가기 V3에서 보완했다. 기준 main은 `c5676e42ff98c0f1b6b29e1521695d9c503e676a`, 작업 브랜치는 `codex/type-declaration-context`다. 이 문서는 구현 세션의 자체 검증이며 독립 리뷰나 사람 의미 승인이 아니다.

## 문제와 수정

V2는 함수 본문 안 `type Box<TypeParam>`의 TypeParam과 `interface Local { member: string }`의 member 선언 이름을 runtime-expression reference로 인정했다. 실제 scan의 진단과 use/target anchor가 모두 정상이어도 use의 타입 전용 문맥을 놓쳤다.

V3의 변경은 sourceUse 조상 검사에 TypeAliasDeclaration, InterfaceDeclaration, TypeParameterDeclaration을 추가하는 것이다. TypeNode 검사와 함께 타입 전용 선언의 자손을 거부하며 구체적인 이유를 출력한다. 인터페이스 property/method/call/construct/index signature 및 computed key, class generic과 mapped/infer/type-query 인접 사례를 검사했다. 범용 AST 의미 분석기나 실제 실행 가능성 판정으로 확장하지 않았다.

검사는 **사용 위치**에만 적용한다. runtime property/method 사용의 target이 타입 signature인 경우는 유효하다. 재귀/import 사용, 매개변수/지역 변수 읽기, 일반 참조와 call 구별, shadow된 동명 target identity는 유지했다. self-target를 일괄 삭제하지 않았고 core references 추출은 변경하지 않았다. R4 matcher와 claim/unverified 분리도 그대로다.

## 전후 검증

| 검사 | 수정 전 | V3 결과 |
| --- | --- | --- |
| 원래 독립 probe의 동일 source/label 9개 | 기대 일치 7/9 | 9/9 |
| 인접 문맥 actual-scan 27개 | 18 통과 / 9 실패 | 27 통과 |
| V2 계약 회귀 10개 | 기존 V2 통과 | V2/V3 각각 10개 통과 |
| 전체 pnpm check | 직전 99개 | 8파일 / 136개, 타입 검사·예제 build 통과 |
| pnpm experiment | 기존 비교 4/4 | 4/4 유지 |

새 회귀를 수정 전에 실행한 [실패 로그](evidence/2026-11-08-type-context-red.txt)를 보존했다. 모든 새 fixture는 실제 scanner를 사용하고 진단 0을 요구한다. use/target anchor는 원문에서 작성하며 edge 위치와 정상 결과의 양쪽 evidence를 확인한다. fixture 소스는 실행하지 않는다.

[역할 probe 결과](evidence/2026-11-08-type-context-results.json)는 보관된 독립 probe source/label을 새 scan에 넣고 V2 결과가 원래 관찰과 완전히 같은지 assert한다. 그 뒤 V3의 모든 기대값을 assert했다. 보고된 TypeParam/member는 이제 `mismatch`이며 타입 전용 선언 문맥이라는 이유가 있다. 27개 인접 fixture의 전후 판정도 같은 파일에 포함했다. 단순 exit 0에 의존하지 않는다.

## 버전과 과거 자료 보존

- V1/V2 평가기·runner·입력 라벨·과거 raw 결과·리뷰 원시 증거는 그대로다. V2 README에는 역사적 실행 방법을 안내하는 배너만 추가했다.
- V3는 **evaluatorVersion=3 / labelVersion=2**다. V2 입력 24개를 재사용하며 claim/anchor/expected 변경이 없다. 같은 22 correct / 2 unsupported를 정확도 상승으로 해석하지 않는다.
- [새 summary](../../experiments/corpus/results/2026-11-08-v3/summary.json)에 V1/V2/V3 코드·입력·분석기 fingerprint와 환경을 기록했다. [24개 전후 대조](../../experiments/corpus/results/2026-11-08-v3/label-changes.json)와 [검토표](../../experiments/corpus/results/2026-11-08-v3/review.md)를 별도 경로에 추가했다.
- V2와 V3의 [분석 산출물 11개](../../experiments/corpus/results/2026-11-08-v3/analysis-unchanged.json)는 byte 동일하다. 원본 corpus·manifest·제품 core/CLI·지원 문법·FCA 상한·의존성은 변경하지 않았다.
- [V1 재현 14개](evidence/2026-11-08-type-context-v1-reproduction.json), [V2 재현 16개](evidence/2026-11-08-type-context-v2-reproduction.json), [V3 반복 재현 16개](../../experiments/corpus/results/2026-11-08-v3-reproduction.json)의 비시간 파일이 각각 byte 일치했다. 같은 workspace/dependency layout에서의 재현이며 이식성·성능 검증은 아니다.

기본 `pnpm experiment:corpus <새 경로>`는 V3다. 과거 버전은 `pnpm experiment:corpus:v1` / `pnpm experiment:corpus:v2`로 실행한다. 실행 명령과 지원 경계는 [V3 README](../../experiments/corpus/v3/README.md), 구현 선택은 ADR-016을 참조한다.

## 남은 경계와 다음 작업

이번 근거는 보고된 역할 분류 오류와 인접 사례에 한정된다. 모든 TypeScript 문법의 건전성·사람의 업무 의미 승인·검색/LSP 대비 효용·Gate 상승을 뜻하지 않는다. [업무 개념 탐색 초안](../experiments/concept-exploration-protocol.md)은 변경 없이 미실행으로 유지했다. 실제 앱/revision·한 개념/과업·정답 근거·참가자와 시간 절차를 구체화하는 후속 준비가 남아 있다. 앱 선정·참가자 모집·연락·npm 배포는 이번 수정에 포함하지 않았다.
