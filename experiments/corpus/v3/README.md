# Corpus evaluator V3 — R5 타입 선언 문맥

2026-11-08의 [독립 리뷰](../../../docs/reviews/2026-11-08-corpus-contract-independent-review.md)에 대한 작은 수정이다. **V2 라벨 계약과 24개 입력을 그대로 재사용**하며 평가기 버전만 3이다. 제품 core/CLI·의존성·원본 corpus·분석 범위·한도는 바꾸지 않았다.

## 변경한 판정

V2의 `isTypeNode`만으로는 TypeParameterDeclaration, InterfaceDeclaration 내부의 signature 이름 등을 모두 거르지 못했다. V3는 use 토큰부터 해당 함수까지 조상을 확인할 때 기존 TypeNode 외에 **TypeAliasDeclaration / InterfaceDeclaration / TypeParameterDeclaration** 문맥도 거부한다. 타입 매개변수·인터페이스의 property/method/call/construct/index signature와 computed key를 타입 전용 문맥 전체로 처리한다. 선언 이름 목록에 누락된 종류를 계속 더하는 대신 해당 선언의 자손을 함께 거부한다.

이 검사는 **사용 위치**에 적용한다. runtime property/method의 target이 interface/type literal의 signature라고 해서 거부하지 않는다. 재귀/import·매개변수/지역 변수 읽기·일반 참조와 call 구분·정확한 target identity는 유지한다. 거부는 이유가 있는 mismatch이며 불확실한 입력·컴파일 오류의 indeterminate와 구분한다. 일반 AST 의미 분석기나 실제 실행 여부 판정기로 확장하지 않는다. R4의 type matcher와 V2의 명시 claim/unverified 계약은 그대로다.

## 실행과 버전 보존

기본 corpus 명령은 V3다. V1/V2 코드·라벨·raw 결과·리뷰 증거는 과거 관찰로 유지하며 각각 명시적인 명령으로 실행한다. 준비 cache는 기존 immutable source hash 검증 절차를 사용한다. 원본 프로젝트 코드를 실행하거나 새 의존성을 설치하지 않는다.

```sh
pnpm experiment:corpus:prepare
pnpm experiment:corpus:v1 work/type-context-v1
pnpm experiment:corpus:v2 work/type-context-v2
node experiments/corpus/verify-reproduction.mjs experiments/corpus/results/2026-11-07 work/type-context-v1
node experiments/corpus/verify-reproduction.mjs experiments/corpus/results/2026-11-08-v2 work/type-context-v2
pnpm experiment:corpus work/type-context-v3-a
pnpm experiment:corpus work/type-context-v3-b
node experiments/corpus/verify-reproduction.mjs work/type-context-v3-a work/type-context-v3-b
node experiments/corpus/v3/check-roles.mjs
pnpm check
pnpm experiment
```

출력은 존재하지 않는 새 디렉터리를 사용한다. `check-roles.mjs`는 원래 독립 probe JSON의 **동일 source/label 9개**를 다시 scan하고 V2 결과가 보관본과 같은지 확인한 뒤 V3 기대값을 assert한다. 별도 `role-cases.mjs`의 27개 adjacent fixture도 실제 진단 0/정확한 use/target으로 검증한다. fixture를 실행하지 않는다.

[새 결과](../results/2026-11-08-v3/summary.json)는 evaluatorVersion=3, labelVersion=2와 양쪽 코드/입력 hash를 기록한다. [전후 대조](../results/2026-11-08-v3/label-changes.json)는 V2와 동일한 24개 claim/status를 연결하며 라벨 변경이 없음을 설명한다. [분석 산출물 대조](../results/2026-11-08-v3/analysis-unchanged.json)의 raw 11개는 V2와 동일하다. [반복 재현](../results/2026-11-08-v3-reproduction.json)은 비시간 16개 파일의 byte 일치를 확인한다. 설치 레이아웃이 다른 환경까지의 재현이나 성능 benchmark는 아니다.

## 검증 범위와 해석

- 보고된 타입 매개변수/인터페이스 필드 이름 및 인접한 signature/type parameter/key의 오인을 차단한다.
- 실제 재귀/import/매개변수/지역 변수/속성/메서드 사용과 동명 shadow target를 확인한다.
- V2 계약 회귀 10개를 V2/V3 양쪽에 실행해 R4·기존 use 판정과 실패 분리를 유지한다.
- 코드 사실 라벨은 여전히 22 correct / 2 unsupported다. 이 corpus 숫자만으로 역할 분류가 같았다거나 제품 정확도가 향상됐다고 해석하지 않는다. 원래 독립 사례는 7/9 → 9/9, 인접 사례는 18/27 → 27/27이다.

수정의 정확성 범위와 증거는 [개발 인계](../../../docs/reviews/2026-11-08-type-context-fix.md)에 있다. 사람 승인·검토 시간·업무 개념 탐색 효용은 여전히 미측정이다. [후속 실험 초안](../../../docs/experiments/concept-exploration-protocol.md)은 그대로 미실행이며 이번에는 앱 선정·참가자 모집을 진행하지 않았다.
