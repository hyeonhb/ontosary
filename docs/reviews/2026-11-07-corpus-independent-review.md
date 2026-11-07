# 실제 corpus 관찰 보고서 독립 리뷰 — 2026-11-07

**판정: 원시 관찰과 재현성은 확인했다. 실험 평가기에는 Medium 결함 2건이 있어 보완을 요청한다. 제품 코어의 새 false proof는 확인하지 않았다.** 사용자와 방향을 논의한 결과 다음 제품 실험은 **업무 개념·관련 코드 탐색 우선**으로 결정했다. utility library의 라벨 검토만을 다음 제품 가치 검증으로 삼지 않는다.

## 검토본과 실제 검증

대상은 [관찰 보고서](2026-11-07-corpus-observation.md) 및 [PR #5](https://github.com/hyeonhb/ontosary/pull/5)가 병합된 `a58a88b2cd61e0cd2396656d4e12e2cac841a21d`이다. fetch 후 로컬/원격 main 일치와 깨끗한 작업 상태를 확인했다. 개발 기준 `c1a542c` 대비 src와 lockfile은 동일하다. 기존 NEXT_PLAN의 고정 corpus·라벨·실패 보존·기준선·역사적 증거 보존 요구를 대조했다.

직접 수행한 검증:

- `pnpm check`: 6개 파일, **89개 테스트**, 타입 검사·예제 빌드 통과.
- `pnpm experiment`: 기존 인공 비교 **4/4** 통과, 기존 결과 diff 없음.
- `pnpm experiment:corpus:prepare`: 기존 cache 20개 파일의 SHA-256/크기를 검증했다. 새 다운로드는 하지 않았다. 원격 원본과의 새로운 대조나 최초 다운로드 시간을 측정한 것은 아니다.
- `pnpm experiment:corpus work/corpus-independent-review-20261107`: 원본 코드를 실행하지 않고 새 정적 분석을 수행했다. 저장된 2026-11-07 결과와 **비시간 산출물 14개가 byte 단위로 일치**했다. [대조 결과](evidence/2026-11-07-corpus-review-reproduction.json).
- 24개 라벨이 가리키는 선언·조건·참조의 원본을 읽었다. DateArg의 실제 union과 lowerBound의 실제 배열 매개변수도 원본과 raw facts에서 확인했다. 이는 별도 agent의 코드 근거 대조이며 사람의 업무 의미 승인이나 사용자 과업 검증이 아니다.
- [평가기 probe](evidence/2026-11-07-corpus-evaluator-check.mjs)와 [결과](evidence/2026-11-07-corpus-evaluator-results.json): 진단 0인 자체 fixture 및 메모리상의 결과 변형으로 아래 두 문제를 재현했다. 원본 corpus나 저장된 raw 결과는 변경하지 않았다.

| 범위 | 재현한 주요 결과 |
| --- | --- |
| p-queue 원래 config | 수집하지 않은 shared tsconfig 때문에 scan 실패 |
| p-queue production | predicate 0/103, condition 10/148, FCA 103×188 입력 상한 초과 |
| p-queue priority-queue | predicate 0/15, FCA 후보 23개, 잘림 없음 |
| date-fns weekday | predicate 0/5, 비교 0/2, FCA 후보 3개, 잘림 없음 |
| 라벨 평가기 출력 | correct 22 / unsupported 2, human-reviewed 0 |

보고서가 원래 설정 실패·상한 초과·미지원·분모 중복과 utility 표본의 한계를 공개하고, 후보 수나 22/24를 의미 정확도·전체 precision/recall로 해석하지 않은 점은 타당하다. 다만 “첫 scan 전에 작성”은 개발 세션의 기록과 frozen 필드에 근거한 진술이며, 이 리뷰가 작성 순서를 독립적인 사전 커밋/타임스탬프로 증명한 것은 아니다.

## R4 — Medium: 라벨의 주장보다 약한 조건으로 correct 판정

위치: `experiments/corpus/evaluate-labels.mjs:16–19`; 관련 라벨 `date-fns-10`, `p-queue-02`.

`kind=type/function`은 이름·선언 위치만 맞으면 즉시 correct이고 parameter는 이름의 존재만 확인한다. 하지만 검토표의 주장은 그 이상이다.

- date-fns-10: “DateArg retains the date, number, string union alias.” 실제 raw TypeFact.type은 `string | number | DateType`이다. 복사본에서 이를 `never`로 바꿔도 correct가 유지됐다.
- p-queue-02: “lowerBound has an array parameter named array.” 복사본에서 array 매개변수 타입을 `number`로 바꿔도 correct가 유지됐다.
- generic alias/function, 클래스 소속 등의 문구 역시 어떤 부분을 자동 검증하는지 명시해야 한다. 현재 FunctionFact가 표현하지 않는 정보까지 자동 승인한 것처럼 보여서는 안 된다.

**영향:** 22개의 자동 통과가 22개의 자연어 주장 전체를 검증했다고 읽힐 수 있고, 이후 분석 결과가 잘못되어도 측정기가 놓친다. 이번 실제 DateArg/array 값이 틀렸다는 발견은 아니다. 현 수치는 재현되지만 평가 계약이 불완전하다.

**권장:** 주장에 독립적인 expected type/kind/usage 등 검증 필드를 추가하거나, 실제 검사하는 선언 존재만을 claim으로 좁히고 나머지는 별도 미검증 항목으로 나눈다. 가능한 정보만을 정확히 판정하는 방법을 선택하면 된다. 타입 정보를 의도적으로 틀리게 한 mutation test에서 더 이상 같은 full-claim correct가 나오지 않아야 한다. 과거 라벨·raw 결과는 보존하고 새 버전으로 재판정한다.

## R5 — Medium: 선언 이름의 위치와 선언 시작 위치를 혼동한 자기 참조 제외

위치: `experiments/corpus/evaluate-labels.mjs:35–37`; 회귀 테스트 `tests/corpus-evaluation.test.ts`의 수작업 reference mock.

평가기의 자기 선언 제외는 use evidence의 시작 offset이 target 선언 시작과 같은지만 검사한다. 실제 AST에서는 함수 선언 이름의 시작 위치와 전체 선언 시작 위치가 다르다.

```ts
export function unused() { return true; }
export function recursive(): boolean { return recursive(); }
```

실제 scan 진단 0개인 fixture에서 unused의 유일한 reference는 선언 이름(offset 16) → 전체 선언(offset 0)이다. 본문에서 unused를 참조하지 않는데 “이 함수가 자기 선언을 사용한다”는 reference 라벨이 correct가 된다. recursive에는 이름(offset 58) 외에 본문의 실제 호출(offset 88)이 별도로 있다.

**영향:** 선언을 사용 관계로 오인하지 않는다는 README/보고서의 계약이 일반적으로 성립하지 않는다. 기존 테스트는 use와 declaration evidence를 동일하게 만든 mock이라 실제 함수를 재현하지 못한다. 현재 corpus의 comparator 매개변수 라벨은 실제 use를 제거하면 missing이 됐으므로, 이 문제 때문에 기존 22개 중 특정 값이 틀렸다고 주장하지 않는다.

**권장:** 원문에서 작성한 사용 위치를 라벨에 포함해 use evidence와 target identity를 함께 대조하거나 실제 AST의 declaration-name 여부를 구분한다. `target.id === function.id`를 일괄 제거하면 진짜 재귀 사용까지 놓치므로 피한다. 사용하지 않는 함수의 자기 선언/매개변수 선언은 거부하고 실제 재귀·import 사용·동명 다른 심볼은 구분하는 실제 scan fixture가 필요하다. 코어의 references는 호출 그래프가 아니라 선언 이름도 포함하는 계약이므로 이번 결함은 우선 평가기 층의 문제다.

## 제품·연구 방향 평가

### 표본이 알려주는 것과 알려주지 않는 것

두 utility library는 정적 분석의 적응 비용·한계·오류 처리 관찰에 적절하다. 호출·숫자·복수 문장·상태 코드에서 현재 predicate가 지원되지 않는다는 결과는 유효하다. 그러나 주문·권한·상담·결제 등 실제 프론트엔드 업무 개념에서 관련 구현을 찾는 어려움을 대표하지 않는다.

따라서 숫자 지원 하나나 SMT를 추가하면 제품 가치가 생긴다는 결론도, 논리 비교가 항상 쓸모없다는 결론도 나오지 않는다. 사람의 24개 라벨 확인은 측정 품질 검토이며, 설치할 가치가 있는지를 검증하는 사용자 과업과 구분해야 한다. 업무 개념에서 탐색하는 경험을 검증하려면 그 개념·사용자 질문·정답 근거가 있는 실제 애플리케이션 범위를 골라야 한다.

### FCA에 대한 추가 관찰

같은 raw facts의 함수 집합(extent)을 대조했다.

| 범위 | 단순 그룹 수 / 중복 제거 extent | FCA 후보 | 단순 그룹에도 있는 FCA extent | 추가 FCA extent |
| --- | --- | --- | --- | --- |
| date-fns weekday | 6 / 3 | 3 | 3 | 0 |
| p-queue priority-queue | 16 / 13 | 23 | 13 | 10 |

요일 범위에서는 모든 FCA 후보 extent를 단순 그룹에서도 찾을 수 있다. 그러나 이것만으로 FCA를 제거하지 않는다. 같은 extent라도 intent 설명·관계 표시가 과업에 도움이 되는지는 미측정이고, 큐에는 10개의 추가 조합도 있다. 반대로 추가 조합 10개를 가치로 계산해서도 안 된다. 후보의 검토 비용과 정확한 관련 코드 도달 여부를 기준으로 비교한다.

### 사용자와 확인한 결정

2026-11-07 이 리뷰 중 “업무 개념·관련 코드 탐색 우선 / 분산 규칙 비교 우선 / 두 방향을 작은 과업으로 비교”를 제시했다. 사용자는 **업무 개념·관련 코드 탐색 우선**을 선택했다.

이 선택은 다음 제품 실험의 우선순위다. 논리 분석을 삭제하거나 자동 의미 승격을 허용한 것이 아니다. 현재 facts/근거를 활용하여 업무 질문에 관련된 코드·조건 위치를 찾는 경험부터 검증하고, 논리 비교는 정당화된 입력과 지원 범위가 맞을 때 보조 근거로 사용한다. 프레임워크 플러그인·LLM·온톨로지 포맷을 자동으로 도입하는 결정도 아니다.

사용자는 앞으로도 중간에 기술적·철학적 판단 또는 방향 확인/변경이 필요하면 요청해 달라고 했다. 리뷰어는 타깃 사용자/과업 변경, 근거·사람 검토 원칙 변경, 주요 기술 추가/제거와 비용·지원 범위의 큰 전환에서 구체적인 근거·선택지·권고안을 제시한다. 통상적인 정확성 수정·검증·이미 승인된 원격 반영을 매번 재승인 대상으로 만들지는 않는다.

## Gate와 다음 작업

- Gate 1: 제품 코어는 이전 제한된 범위의 통과 판단을 유지한다. src가 같고 새 false proof를 확인하지 않았다. **측정 평가기의 신뢰성에는 R4/R5 보완이 필요하다.**
- Gate 2/3: 여전히 미검증. library 그룹/코드 사실 판정은 업무 이해·기존 탐색 대비 효용의 증명이 아니다.
- Gate 4: 설정 변경·상한 초과·지원 0건이라는 도입 장벽을 실제로 관찰했다. 전체 유지 비용은 미측정이므로 통과로 올리지 않는다.
- Gate 5: 미통과. 실험 재현성만으로 Public Beta를 권하지 않는다.

**바로 다음 작은 개발 작업:** R4/R5의 라벨 계약·사용 위치 판정을 고쳐 새 버전의 결과를 만든다. 코어 기능 확장은 제외한다. [독립적인 개발 지시문](2026-11-07-corpus-review-next-plan.md)에 완료 조건을 적었다.

**그 뒤 첫 제품 실험:** 사용자가 선택한 업무 개념 탐색을 실제 애플리케이션의 한 개념·한 과업으로 구체화한다. 사용자 질문 → 관련 코드/조건 근거 목록 → 사람의 설명/확인이라는 흐름을 검색/LSP 및 같은 facts의 단순 그룹과 비교한다. “개념”의 의미를 자동 확정하지 않는다. 이 비교를 시작하기 전에 대상·과업·정답 근거·비교 순서/학습 효과·시간 기록 방법을 정하고, 참가자나 사람 검토가 없으면 정량 효용을 꾸며내지 않는다.
