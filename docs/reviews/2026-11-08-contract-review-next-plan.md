# 개발 세션 지시 — R5 타입 선언 문맥 보완

2026-11-08 [독립 리뷰](2026-11-08-corpus-contract-independent-review.md) 후속. 사용자 방향은 업무 개념·관련 코드 탐색 우선(ADR-014)이다. 이번 한 작업은 평가기 잔여 오류를 고치는 작은 수정이다.

## 작업 목표

함수 안의 타입 전용 선언 이름이 runtime-expression reference로 승인되지 않게 한다. core references는 선언 이름을 포함하는 현 계약을 유지한다.

## 현재 상태와 근거

AGENTS/CONTRIBUTING/PROGRESS와 독립 리뷰를 읽고 원격·브랜치·사용자 변경을 확인한다. 검토 구현은 PR #7/main `76712363fa6304b9bb716b4f9f50fc2c0a3780a0`이며 이후 리뷰 문서가 추가될 수 있다.

독립 검증에서 99개 테스트·기존 비교 4/4·V1 비시간 14개/V2 16개 재현이 통과했다. R4는 V2 계약 범위에서 해결됐다. 기존 unused 함수 이름과 header/지역 변수 선언은 거부되지만 아래 지역 타입의 TypeParam 선언 이름과 member 선언 이름은 둘 다 correct다.

```ts
export function localTypes() {
  type Box<TypeParam> = { value: TypeParam };
  interface Local { member: string }
  return true;
}
```

`experiments/corpus/v2/evaluate-labels.mjs:44–54`의 isTypeNode/선언 이름 목록은 이 문맥을 거르지 못한다. 진단 0의 실제 scan에서 source/use/target anchor와 self-edge가 모두 맞는 라벨로 재현했다. [독립 probe](evidence/2026-11-08-contract-independent-check.mjs)와 [결과](evidence/2026-11-08-contract-independent-results.json)를 참조한다. exit 0은 성공 판정이 아니며 `matchesExpectation`을 읽어야 한다.

## 구현 범위

1. 두 사례를 먼저 실패하는 actual-scan 회귀 검사로 만든다. 원문에서 작성한 use/target anchor와 진단 0을 확인한다.
2. sourceUse의 타입 전용 선언 문맥·선언 이름 판정을 보완한다. 인접한 타입 매개변수/인터페이스 signature 문맥을 함께 검사해 같은 누락을 줄이되 범용 AST 의미 분석기로 확장하지 않는다.
3. 재귀/import 사용, 매개변수 읽기, 지역 변수 읽기와 call/reference 구분을 유지한다. 모든 self-target를 제거하거나 코어 추출 범위를 바꾸지 않는다.
4. 기존 V1/V2 라벨·raw 결과·리뷰 증거는 당시 관찰로 보존한다. 평가기 변경으로 fingerprint가 달라진 새 결과를 별도 경로에 남기고 사용한 버전/해시·명령을 연결한다. 과거 V2를 실행할 수 있는 코드와 방법도 보존한다. 구체적 버전 배치는 개발 세션이 선택하되 과거 결과를 새 평가기의 출력으로 표시하지 않는다.

## 제외 범위

R4 재설계, core/CLI·문법 지원·FCA 상한 변경, LLM/SMT/플러그인, UI, 사람 의미 승인, 실험 참가자 모집/연락, npm 배포는 이번 정확성 수정에 포함하지 않는다.

## 완료 조건

- 두 선언 이름과 인접한 타입 전용 문맥이 correct로 통과하지 않고 이유가 출력된다.
- 실제 표현식의 재귀/import/매개변수/지역 변수 사용과 정확한 target identity가 유지된다.
- 기존 24개 라벨이 유지되거나 변경됐다면 항목별 이유를 보고한다. 동일한 판정 수를 정확도 변화로 해석하지 않는다.
- 과거 자료 보존과 새 evaluator fingerprint·재현을 확인한다. 기존 원본 source와 core 분석 산출물은 그대로다.
- `pnpm check`, `pnpm experiment`, 과거 버전 재현 및 새 평가기 결과 재현을 통과한다. 사람 승인/효용/Gate 상승을 자동으로 기록하지 않는다.

## 검증 방법

새 actual-scan 실패 재현 → 역할 분류 수정 → 양성/부정·동명 target 검사 → 고정 corpus 재판정 순서로 수행한다. 독립 probe의 해당 실패가 해소됐는지 명시적으로 대조한다. 이전 결과 파일을 덮어쓰지 않는다.

## 문서화 및 인계

PROGRESS와 평가기 README에 정확한 지원 경계·버전·명령을 기록하고 날짜별 개발 보고에 수정 전후 관찰을 남긴다. 중요한 구현 선택은 DECISIONS에 기록한다. 검증·staged diff 검토 후 지속 승인된 PR/merge/main 동기화를 진행한다.

후속 제품 준비는 [탐색 실험 초안](../experiments/concept-exploration-protocol.md)을 유지한다. 실제 업무 앱 후보의 라이선스·revision·개념 근거·현 지원 범위·설정 비용을 조사해 한 개념/과업을 구체화하는 일은 이 작은 수정과 독립적으로 준비할 수 있다. 분석이 성공하는 표본만 고르고 실패를 숨기지 않는다. 참가자/정답/절차 확정 전에는 사용자 실험을 완료했다고 하지 않는다. 사용자 문제나 주요 기술 투자 방향이 바뀌어야 할 때는 구체적인 후보와 근거를 먼저 마련한 뒤 사용자 판단을 요청한다.
