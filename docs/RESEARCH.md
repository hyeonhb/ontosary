# 연구 가설과 첫 실험

## 미검증 가설

TypeScript 정적 분석의 구조적·논리적 사실에 FCA와 제한된 논리 검증을 추가하면, 기존 코드에서 도메인 개념과 규칙의 후보를 더 신뢰할 수 있는 근거와 함께 찾을 수 있을 것이다. **현재 결과는 이 유용성 가설의 증명이 아니다.**

FCA는 공유 속성으로 그룹을 만드는 명시적·재현 가능한 기준을 제공한다. 논리 열거는 지원 범위 안에서 조건 차이에 대한 구체적 입력을 제공한다. 둘 다 사람의 업무 의미 해석을 대신하지 않는다.

## 2026-11-03 실험

데이터: `examples/react-vite/src`의 인공 Vehicle/Listing/ConsultationRequest 예제. 코드 수준의 기대값은 `experiments/cases.json`에 고정했다. 재현: `pnpm check && pnpm experiment`. 기계 판독 결과: `experiments/results/{scan,concepts,comparisons,summary}.json`.

| 관찰 | 근거 | 해석 가능한 범위 |
| --- | --- | --- |
| 타입 6, 함수 13, 정규화 가능한 predicate 6, 미지원 7 | `results/summary.json` | 이 예제에서의 추출·지원 개수. 일반 코드 coverage 추정치가 아님 |
| 13 객체 × 26 속성에서 형식 개념 20, 후보 8, 일반화 관계 8 | `results/concepts.json` | 제한 내에서 폐포·포함 관계 계산 가능 |
| 카드 조건 ⇒ 상세 조건, 역함의 실패, `arg0.status=reserved` | `results/comparisons.json` | 동일 입력·유한 도메인 등 전제하의 논리 차이 |
| 부정형 등가 표현은 Equivalent, 서로 배타적인 조건은 Different | 비교 사례 및 Vitest | IR 문자열이 아닌 입력 전수 열거로 판정 |
| 고가 여부 `price > ...`는 Unsupported | 비교 사례, `rules.ts` | 숫자 범위/산술을 임의로 근사하지 않음 |
| User와 Customer, 두 파일의 Item/status가 별도 ID | `analysis.test.ts` | 구조/이름 유사성으로 선언을 병합하지 않음 |
| 512개 3×3 incidence matrix의 NextClosure가 독립 완전탐색과 일치 | `fca.test.ts` | 작은 Formal Context에서 구현 정확성 확인 |
| 세 상태의 실제 함수 결과와 IR 평가 일치 | `analysis.test.ts` | 이 예제의 실행 의미와 정규화 의미 일치 |

검증 당시 자동 테스트 41개/3개 파일 통과. 코어·예제 타입 검사와 production build 통과. 브라우저에서 available의 두 버튼 활성화, reserved의 카드만 비활성화, sold의 두 버튼 비활성화, 상담 요청 표시를 확인했다. 브라우저 확인은 자동 회귀 테스트가 아닌 세션 내 smoke check다.

## 실패 사례·제약

- `formatPrice`와 `isPremium`은 `Listing.price`를 공유해 후보로 묶인다. 하나는 표시, 하나는 판정이므로 같은 업무 개념이라는 결론은 나오지 않는다.
- `Listing` 타입만 공유하는 일반 후보는 UI·상담 조건·가격 함수를 폭넓게 포함한다. 수학적으로 올바른 그룹도 도메인 발견에는 지나치게 넓을 수 있다.
- 반대로 함수에 직접 드러나지 않은 `ConsultationRequest.listingId → Listing.id`의 업무 관계는 이 FCA가 자동 해석하지 못한다. 참조 필드와 실제 관계의 의미를 구분해야 한다.
- React Element 등 프레임워크/공통 타입도 속성에 포함되어 기술적 묶음을 만들 수 있다. 조건 필드를 공유하는 좁은 그룹은 관찰되지만 후보 순위나 유용성을 평가하지 않았다.
- 13개 함수 중 7개는 전체 predicate로 비교할 수 없다. JSX 반환, 함수 호출, 숫자 비교, 복수 문장 등 의도된 미지원 영역이다. 이 수치는 결함률이 아니다.
- enum/문자열 도메인, plain data, 입력 독립성의 전제가 깨지면 증명이 실제 동작을 보장하지 않는다. 동일 입력은 사용자의 명시적 주장이고 독립적으로 검증하지 않는다.
- 컴파일러 오류, 선택적 입력, getter, 객체 union, 비동기·변이·기본값 함수는 정확성을 우선해 거부한다. 전체 JS 형식 검증은 아니다.
- 큰 프로젝트 성능, 개념 수 폭증, ID의 코드 편집 안정성, path/dependency 설치 구조 차이에 따른 스냅샷 변동은 아직 실험하지 않았다.

## 아직 검증하지 않은 것

실제 비즈니스 개념 precision/recall, 규칙 위반 탐지 정확성, 후보의 검토 시간 단축, LLM 대비 우수성, 문서와 코드의 정합성, 운영 프로젝트의 유지 비용은 측정하지 않았다. 인공 예제를 설계한 사람이 기대 그룹을 아는 편향도 있다. 후보 8개를 정답 8개로 세면 안 된다. 업무 정답 라벨을 만들기 전에는 의미 정확도 점수를 보고하지 않는다.

## 후속 비교 실험

동일한 공개/허가된 코드·문서·정답셋, 모델/프롬프트/버전, 입력 범위와 비용 한도를 고정한다. 모델 실행 간 변동을 측정하고, 평가자는 가능하면 방법을 모르게 한다.

- A: LLM 코드·문서 분석
- B: TypeScript 정적 분석 + LLM
- C: B + FCA 후보
- D: C + 논리 검증

평가: 개념 precision/recall, 관계·규칙 정확도, 잘못된 의미 해석 비율, 근거 위치 정확성, 검토·승인 소요 시간, 생성·유지 비용. 누락·미지원·오해를 따로 기록하고 실패 사례를 보존한다. 초기에는 작은 두 도메인 corpus와 사람이 작성한 코드 사실/업무 의미 분리 라벨부터 만든다.

## 참고 자료

아래는 방법의 근거이며 Ontosary의 제품 효과를 입증한 자료가 아니다.

- [TypeScript: Using the Compiler API](https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API) — Program/TypeChecker/AST 사용. [TypeScript 소스](https://github.com/microsoft/TypeScript).
- [Universität Kassel: Closure Systems and Implications, Next-Closure](https://www.kde.cs.uni-kassel.de/lehre/ss2005/formale_begriffsanalyse/folien/4_Closure_Systems.pdf) — 폐포·lectic 순서·NextClosure의 정의와 절차.
- [Ganter, Hanika, Hirth: Scaling Dimension](https://arxiv.org/abs/2302.09101) — FCA의 conceptual scaling 연구 맥락. 이 PoC의 속성 설계가 검증됐다는 근거는 아님.
- [Wollbold, Guthke, Ganter: Constructing a Knowledge Base ... by Formal Concept Analysis Methods](https://arxiv.org/abs/0807.3287) — 전문가 검토를 동반한 attribute exploration 연구 예시. 도메인과 평가 환경은 이 프로젝트와 다름.
- [Vite 시작 안내](https://vite.dev/guide/), [Vitest 시작 안내](https://vitest.dev/guide/) — 실행 환경·호환성 확인. 실제 고정 버전은 package.json/lockfile 참조.


## 2026-11-06 · 계산 검증과 지원 판정 경계의 수정

2026-11-04 독립 리뷰는 기존의 작은 예제 성공과 별개로 소스→IR의 R1/R2를 반증했다. 과거 결과는 당시 관찰로 유지한다. 이번에는 지원 밖 receiver가 enum constant folding을 통해 통과하던 경로를 차단하고 explicit this를 명시적으로 거부했다.

새 회귀 집합은 컴파일 진단 0개를 전제로 한다. 최초 34개 중 29개 실패/5개 통과를 먼저 관찰했다. 수정 후 4,096 조합 경계 테스트를 추가한 35개가 통과했다. 거부된 식에 대해 predicate/condition/API/CLI의 상태·이유·평가 0회·종료 코드 2를 확인했다. 정상 string/numeric enum, named import alias, 부정/중첩 논리의 실제 실행을 IR과 대조하고, 9개 함수의 81개 순서쌍을 실행 진리표로 판정하며 방향별 반례를 재실행했다.

이는 **지원 판정 경계의 수정**이다. 올바른 IR에서의 기존 FCA/열거 계산 검증과 구분한다. 모든 TypeScript 구문에 대한 건전성 증명이나 Gate 2~4의 제품 효과 검증이 아니다. 새 독립 probe 결과와 개발 인계는 `docs/reviews/evidence/2026-11-06-independent-results.json`, `docs/reviews/2026-11-06-normalization-fix.md`에 보존한다. R3 파일 집계 계약은 이번에 수정하지 않았으며 실제 corpus 측정 전에 처리해야 한다.


## 2026-11-06 후속 · R3 파일 집계 계약

R1/R2 수정 후 별도 작업으로 R3를 해결했다. 독립 probe의 mixed-JS 관찰은 files=[ignored.js,input.ts]에서 files=[input.ts]로 바뀌고, ignored.js는 위치가 있는 제외 사유로 남는다. 실제 분석 대상만 분모로 쓰도록 기존 계약을 복원했다. 전체 Program coverage를 새로 측정한 것이 아니다.

새 regression 6개와 기존 76개가 모두 통과했다. 타입 해석/참조를 위해 imported JS는 Program에 남고, 제외 파일의 컴파일 오류도 계속 보고·proof 거부에 반영된다. 최신 원시 결과는 `docs/reviews/evidence/2026-11-06-file-manifest-results.json`이며 앞선 날짜별 증거는 보존했다. 코드 사실의 집계 정확성이 업무 개념의 precision/recall이나 사람의 검토 시간 개선을 입증하지 않는다.


## 2026-11-07 · 실제 corpus 관찰

[관찰 보고서](reviews/2026-11-07-corpus-observation.md), [고정 입력/재현 절차](../experiments/corpus/README.md), [원시 요약](../experiments/corpus/results/2026-11-07/summary.json).

**관찰:** 공개 p-queue/date-fns 원문을 고정하고 첫 scan/FCA 전에 코드 사실 라벨 24개를 agent가 작성했다. 자동 대조 22개 일치/2개 명시적 클래스 모델링 미지원이다. 함수 전체 predicate는 production queue 0/103, 작은 queue 0/15, weekday 0/5이며 사전 비교는 0/2다. p-queue 원래 설정 실패와 production FCA의 188속성 상한 초과를 보존했다. 작은 queue 후보 23개, weekday 후보 3개가 한도 내에서 나왔다. 동일 facts의 단순 type/property 그룹도 각각 16개/6개를 제공한다. 두 재실행에서 비시간 산출물 14개가 byte 단위로 일치했다.

**해석/추정:** 실제 원문의 호출·상태·숫자·여러 문장 때문에 현재 논리 비교 범위가 좁다는 관찰이다. 날짜 FCA의 요일 함수 extent는 단순 getDay/in 공유 그룹에서도 나타나므로 후보 수를 순증분으로 평가할 수 없다. 두 utility library의 목적 표본은 업무 애플리케이션 coverage나 precision/recall을 추정할 표본이 아니다. 함수 분모에는 nested 함수·접근자·overload도 포함한다. 두 p-queue 실행은 겹친다.

**미검증:** 모든 라벨의 사람 검토, 업무 의미 승인, 실제 사용자 검토 시간, 검색/LSP 대비 효용, 설치 레이아웃이 다른 환경의 재현성. wall time은 단일 로컬 관찰이며 agent 작성 노력/사람 시간을 대체하지 않는다. Gate 2~4는 올라가지 않았다. 다음 한 실험은 사람이 관련 규칙 위치 찾기/그룹 검토/차이 설명 과업을 수행하는 것이다. 기능 지원 확대는 이 자료만으로 선정하지 않는다.

## 2026-11-07 후속 · corpus 독립 재검토와 사용자 과업 선택

[독립 리뷰](reviews/2026-11-07-corpus-independent-review.md)에서 같은 환경의 새 실행과 기존 결과 14개 비시간 파일의 byte 일치를 확인했다. 그러나 평가기가 type/function 선언 존재만으로 더 강한 타입·generic claim을 correct로 내보내고(R4), 함수 선언 이름을 실제 사용으로 오인하는 경우(R5)를 재현했다. 현재 DateArg/array의 원본 타입이 틀렸거나 기존 22개 중 특정 결과가 거짓이라고 결론 낸 것은 아니다. 자동 판정의 검사 범위를 보완해야 한다.

추가 extent 대조에서 date-fns의 FCA 후보 3개 모두 단순 그룹에서도 나타났다(6그룹/중복 제거 extent 3개). 작은 p-queue의 FCA 23개 중 13개는 단순 그룹에 있고 10개는 추가 조합이다(단순 16그룹/extent 13개). 동일 extent라고 설명 가치가 없다는 뜻도, 추가 extent라고 유용하다는 뜻도 아니다. 과업 검토가 필요하다.

사용자는 다음 제품 실험을 업무 개념·관련 코드 탐색 우선으로 선택했다(ADR-014). utility 표본의 기술적 관찰은 유지하되 실제 업무 애플리케이션의 질문·관련 코드 근거·탐색 비용을 평가하는 과업으로 진행한다. 사람의 라벨 검토와 제품 효용 검증을 분리한다. Gate 2~4를 통과로 올리지 않는다.


## 2026-11-08 · R4/R5 측정 계약 보완

[수정 인계](reviews/2026-11-08-corpus-contract-fix.md), [V2 전후 라벨 대조](../experiments/corpus/results/2026-11-08-v2/label-changes.json).

V1의 22 correct / 2 unsupported는 약한 계약의 당시 출력으로 보존했다. V2는 DateArg union·array 타입을 실제 대조하고, 사용 위치/target의 별도 근거와 AST 역할을 검사한다. 타입을 never/number로 변형하거나 사용 없는 선언 이름을 use로 제시하면 correct가 아니다. 실제 재귀/import는 허용한다. 원문에서 보이는 generic/클래스 소속/상속 설명 중 자동 검증하지 않는 부분은 별도 unverified다.

V2도 22 correct / 2 unsupported지만 일부 claim과 검사 범위가 달라졌다. 정확도 전후 변화로 계산하지 않는다. 실제 source 타입이 잘못됐다는 발견이 아니고 측정 도구가 잘못된 fact를 놓치던 결함의 수정이다. source/분석 산출물 11개는 V1과 byte 동일하며, V1 재현 14개/V2 재현 16개 비시간 파일도 각각 일치했다. 전체 99개 자동 테스트·인공 비교 4/4는 측정/구현 검사이지 사람의 제품 효용 검증이 아니다.

후속 [업무 개념 탐색 실험 초안](experiments/concept-exploration-protocol.md)은 대상·정답·참가자 미확정/미실행이다. 같은 과업을 같은 참가자가 반복하며 학습한 시간을 독립적인 개선으로 계산하지 않도록 첫 노출 배정과 비용·정답 평가를 분리할 예정이다. Gate 2~4와 사람 승인은 여전히 미검증이다.
