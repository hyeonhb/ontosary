# Corpus V2 수정 독립 리뷰 — 2026-11-08

**판정: R4 해결, R5 부분 해결. 평가기 사용 역할 판정에 Medium 잔여 결함 1건이 있다. 현 제품 방향은 유지한다.** 원래 unused 함수 선언 오인은 차단됐지만 함수 내부의 타입 매개변수·인터페이스 필드 선언 이름이 여전히 runtime-expression reference로 통과한다. 현재 24개 corpus 판정이 틀렸다는 발견은 아니다.

## 검토 범위와 재현

[개발 보고서](2026-11-08-corpus-contract-fix.md)와 [PR #7](https://github.com/hyeonhb/ontosary/pull/7)의 병합 커밋 `76712363fa6304b9bb716b4f9f50fc2c0a3780a0`을 검토했다. 시작 시 깨끗한 main과 fetch 후 origin/main 일치를 확인했다. 기준 `7adf2d1` 대비 제품 src·lockfile, V1 평가기/runner/common/manifest/라벨 및 과거 2026-11-07 결과는 동일하다. V2 구현·24개 명시 계약과 미검증 항목·회귀 검사·runner·후속 실험 절차를 읽었다.

- `pnpm check`: **7개 파일 / 99개 테스트**, 코어·예제 타입 검사와 production build 통과.
- `pnpm experiment`: 기존 인공 비교 **4/4** 통과, 기존 산출물 변경 없음.
- build 후 V1/V2 runner를 각각 새 `work/review-contract-v1-20261108`, `work/review-contract-v2-20261108` 경로에 실행했다. 각 runner가 고정 원본 hash/설정/anchor를 확인했으며 새 다운로드는 하지 않았다.
- V1 비시간 **14개**, V2 비시간 **16개** 파일이 각각 저장 결과와 byte 일치했다. [V1 대조](evidence/2026-11-08-contract-review-v1-reproduction.json), [V2 대조](evidence/2026-11-08-contract-review-v2-reproduction.json). V2 runner의 V1 대비 분석 산출물 **11개 동일성 검사**도 통과했다. 같은 로컬 의존성 배치의 재현이며 이식성·성능 검증이 아니다.
- 구현 세션의 `node experiments/corpus/v2/check-mutations.mjs`를 재실행했다. DateArg→never 및 array→number는 V1 correct / V2 mismatch, unused 이름은 V2 mismatch, 실제 재귀 호출은 correct였다.
- 별도로 작성한 [독립 probe](evidence/2026-11-08-contract-independent-check.mjs)는 진단 **0개**의 실제 scan으로 9개 역할 사례를 관찰했다. **7개 기대 일치, 2개 잘못된 correct**. [전체 원문·라벨·결과](evidence/2026-11-08-contract-independent-results.json). 원본 corpus나 facts를 변형하지 않은 두 선언 이름 사례에서 실패했다. probe는 관찰용이므로 exit 0을 통과로 읽지 않는다.

## R5 잔여 — Medium: 타입 선언 내부의 이름을 본문 사용으로 승인

위치: `experiments/corpus/v2/evaluate-labels.mjs:44–54` (`sourceUse`).

```ts
export function localTypes() {
  type Box<TypeParam> = { value: TypeParam };
  interface Local { member: string }
  return true;
}
```

이 함수에 대해 다음 두 `kind: reference, usageKind: reference` 라벨이 모두 **correct**다.

| use와 target으로 지정한 위치 | 실제 구문 역할 | 기대 |
| --- | --- | --- |
| `TypeParam> =`의 TypeParam | 지역 타입 별칭의 타입 매개변수 선언 이름 | 실제 표현식 사용으로 승인하지 않음 |
| `member: string`의 member | 지역 인터페이스의 PropertySignature 선언 이름 | 실제 표현식 사용으로 승인하지 않음 |

두 위치는 함수 body 범위 안에 있고 core references에는 자기 선언 edge가 존재한다. 그러나 TypeParameterDeclaration/PropertySignature 및 이 사례의 선언 조상은 `ts.isTypeNode` 검사에 걸리지 않으며, 아래 declaration-name 목록에도 두 종류가 없다. 그래서 원문 anchor와 정확한 edge가 모두 맞더라도 **구문 역할이 잘못 승인**된다. V2 README의 “type 구문·본문 내 선언 이름을 제외한다”는 계약과 다르다.

**영향:** 새 업무 앱에 지역 타입/인터페이스 라벨을 추가할 때 타입 선언을 코드 사용 관계로 오판할 수 있다. 현재 22 correct / 2 unsupported에 영향을 줬다는 결론은 아니며, 코어 논리 비교의 새 false proof도 아니다. 심각도는 평가 계층의 Medium으로 유지하고 R5를 완전 해결로 닫지 않는다.

**수정 권고:** 평가기의 AST 역할 판정에서 타입 전용 선언 문맥과 선언 이름을 분리해 거부한다. 누락된 두 구문 종류와 인접한 타입 전용 signature/선언 문맥을 작은 actual-scan 회귀 묶음으로 점검한다. 재귀·import·매개변수 읽기·지역 변수 읽기 같은 실제 표현식 사용은 유지한다. 코어 references 자체를 호출 그래프로 바꾸거나 모든 self-target를 삭제할 필요는 없다.

## 해결 확인과 구현 평가

**R4는 V2의 명시 계약 범위에서 해결됐다.** DateArg의 종류와 union, array 매개변수의 위치·타입을 검사하고 원문에서 확인한 기대값과 대조한다. generic/클래스 소속/상속 등 모델이 검증하지 않는 설명은 unverified로 드러난다. 순서만 무시하는 단순 union 비교를 일반 타입 동치로 주장하지 않는다. 22/24 수치가 같아도 검사 범위가 달라졌다는 보고는 정확하다.

**R5의 기존 대표 사례와 주요 양성 사례는 개선됐다.** 함수 이름·매개변수 header·지역 변수 선언은 거부하고 실제 재귀/변수 읽기를 보존했다. 정확한 use→target과 source 역할을 함께 보는 설계는 적절하다. 이번 두 실패는 그 역할 분류의 누락이며 설계 전체를 다시 만들 근거는 아니다.

V1의 소스/실행 경로/결과를 보존하고 V2에 fingerprint와 라벨별 변경 사유를 기록한 점은 타당하다. 대가로 작은 runner 중복이 있지만, 이 리뷰에서는 일반화나 리팩터링을 다음 우선순위로 올리지 않는다. 후속 수정 시 기존 V2 결과와 fingerprint도 과거 관찰로 보존해야 한다.

## 제품 방향과 Gate

[탐색 실험 초안](../experiments/concept-exploration-protocol.md)은 ADR-014에 맞는다. 검색/LSP, 같은 facts의 단순 그룹, FCA를 비교하고 첫 노출·학습 효과·불확실한 의미·미완수·설정 비용을 구분한다. 주문 취소는 아직 후보 질문이고 대상·정답·참가자가 확정됐다는 과장은 없다.

다음 제품 준비에서는 먼저 **실제 앱 한 개념의 근거 목록을 작성할 수 있는지와 현재 분석 범위가 들어오는지** 확인한다. 소규모 사전 실행으로 범위와 자료를 준비할 수 있지만 agent 시간이나 한 사람의 반복 실행을 사용자 효용으로 계산하지 않는다. 조건별 2명/15분은 초안 수치로 유지하며 모집 현실에 맞춰 사람 실험 전에 확정한다. 해당 실험의 준비는 작은 R5 보완과 독립적으로 진행할 수 있다.

- **Gate 1:** 제품 코어의 이전 제한적 통과 유지. R4 해결, R5 평가기 계약은 잔여 보완 필요.
- **Gate 2 / 3:** 미검증. 재현성과 평가기 수정은 의미적 유용성·검색/LSP 대비 효용 증거가 아니다.
- **Gate 4:** 기존 설정/지원/상한 장벽 관찰 유지. 낮은 도입·유지 비용 통과 근거 부족.
- **Gate 5:** 미통과. Public Beta를 권할 새 사용자 근거 없음.

다음 작은 구현은 **R5 타입 선언 문맥 오인 보완**이다. [개발 세션 지시](2026-11-08-contract-review-next-plan.md)에 완료 기준과 역사적 결과 보존 요구를 적었다. 탐색 우선 결정은 유지하며 주요 대상 과업·기술 투자·근거/승인 원칙을 바꿀 필요가 생기면 사용자에게 근거·선택지·권고를 제시한다.
