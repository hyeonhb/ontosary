# 연구 가설과 첫 실험

## 미검증 가설

2026-11-08 사용자 목표 정렬(ADR-020)에 따라 두 가설을 분리한다. **현재 결과는 어느 쪽의 유용성도 입증하지 않았다.**

- **H-O · 도메인 모델의 사용 효과:** 코드 근거와 연결한 개념·관계·규칙을 제공하면 같은 agent가 코드+충분한 기존 문서만 사용할 때보다 변경 누락·잘못된 수정·회귀를 줄이고 총비용을 개선할 수 있다. agent 모델·버전/도구/소스 접근/예산을 맞추고, 일반 문서와 정보량·정답 누출 차이를 통제한다.
- **H-F · FCA의 구축 기여:** 같은 코드 사실에서 FCA 후보를 추가하면 직접 탐색·단순 그룹·수동/AI 모델링만 할 때보다 모델 구축·검토 품질이나 비용이 개선된다. 후보 수보다 실제로 추가/수정/기각된 모델 항목과 근거 정확성·불필요한 검토량을 본다. 시간·사람 비용을 측정하지 않았으면 개선이라고 쓰지 않는다.

H-O는 모델을 만드는 방법과 별개이고, H-F는 모델이 agent에게 유용한지와 별개다. 수동 초안에 유용성이 있어도 FCA의 효과를 증명하지 않는다. 기존 “구조적·논리적 사실에 FCA/논리 검증을 더하면 신뢰할 만한 후보를 찾을 수 있다”는 가설은 H-F를 구성하는 하위 연구 질문으로 유지한다.

FCA는 공유 속성으로 그룹을 만드는 명시적·재현 가능한 기준을 제공한다. 논리 열거는 지원 범위 안에서 조건 차이에 대한 구체적 입력을 제공한다. 둘 다 사람의 업무 의미 해석을 대신하지 않는다.

최종 평가는 변경 과업의 검증 성공·누락·회귀·전제 위반·사람 재작업과 token/time, 모델 작성·검토·갱신 비용을 함께 사용한다. 초기에는 [S1](reviews/2026-11-08-domain-model-next-plan.md)의 모델/근거 계약과 기여 기록을 만들고 S2에서 agent 비교를 진행한다. 알려진 Vendure 사례는 개발용 pilot이며 독립 일반화 표본이 아니다. 사람이 읽기 좋은 기존 코드가 agent에게 불리하다는 가정도 하지 않는다.

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

아래 초기 A/B/C/D는 모델 구축 방법을 비교할 H-F의 후속 후보이며 지금 실행 중인 실험이 아니다. 현재 우선순위는 ADR-020의 S1→S2→S3다.

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

## 2026-11-08 후속 · V2 독립 검토

[독립 리뷰](reviews/2026-11-08-corpus-contract-independent-review.md)에서 99개 테스트·인공 비교 4/4·V1 14개/V2 16개 비시간 산출물 재현 및 두 버전 분석 결과 11개 동일성을 확인했다. R4는 명시 계약 범위에서 해결됐다. R5는 기존 함수 선언 이름 오인을 차단했지만 지역 타입 매개변수/인터페이스 필드 선언 이름은 여전히 실제 사용으로 승인했다. 진단 0인 독립 fixture의 9개 역할 사례 중 2개 잘못된 correct이며, 기존 24개 라벨의 특정 판정 오류나 core false proof를 발견한 것은 아니다.

탐색 실험 초안은 ADR-014와 맞는다. 대상·한 개념·근거 목록·현재 분석 가능 범위를 먼저 구체화하는 준비는 작은 R5 보완과 독립적으로 진행할 수 있다. 사람의 조건별 비교·시간·모집은 여전히 미실행이고 Gate 2~4를 올릴 근거는 없다.


## 2026-11-08 후속 · 타입 선언 문맥 수정

V3는 변경 없는 V2 입력 계약을 평가하면서 타입 전용 use 문맥을 거부한다. 원래 독립 probe의 기대 일치 7/9 → 9/9, 인접 실제 scan 18/27 → 27/27을 확인했다. 전체 136개 테스트·인공 비교 4/4·V1/V2/V3 비시간 14/16/16개 재현이 통과했다. 기존 corpus는 그대로 22 correct / 2 unsupported이며 이는 정확도 상승 수치가 아니다. 분석 산출물 11개는 V2와 동일하다.

[수정 인계](reviews/2026-11-08-type-context-fix.md)는 측정 도구의 제한된 역할 분류 검증이다. 사람 승인·업무 의미·효용·Gate 2~4를 갱신하지 않는다. 기존 탐색 초안과 미실행 상태는 유지하며 실제 앱의 한 개념/과업 및 정답 근거를 구체화하는 후속 준비가 남아 있다.

## 2026-11-08 후속 · V3 독립 검증과 공개 앱 표본 준비

[독립 리뷰](reviews/2026-11-08-type-context-independent-review.md)에서 R5의 보고된 잔여 오류를 해결로 판정했다. 136개 테스트·기존 비교 4/4, 원래 사례 9/9·인접 사례 27/27·새 독립 경계 8/8, V1/V2/V3 비시간 14/16/16개 재현을 확인했다. R4 해결 상태와 core의 제한적 Gate 1 통과를 유지한다. 보고된 범위의 근거이며 모든 TS 역할 분류나 제품 효용을 증명하지 않는다.

사용자는 공개 TypeScript 업무 앱 후보부터 조사하기로 선택했다(ADR-017). [초기 후보 조사](reviews/2026-11-08-public-app-candidates.md)는 Saleor의 주문 취소 UI/조건/API 근거를 확인했지만 strict=false·codegen/의존 경계가 있어 현 분석 성공은 미검증이다. Medusa의 조사 revision은 해당 화면의 별도 라이선스 대상 hook 의존을 확인했다. 두 앱을 설치·scan하거나 사람 과업을 실행하지 않았다. 다음 작은 작업은 원문 근거/범위를 고정하고 실제 적합성·준비 비용을 확인하는 것이며 Gate 2~4는 여전히 미검증이다.


## 2026-11-08 공개 앱 과업 준비 · 표본 미선정

Saleor 일반 주문 취소 원문 근거 18개, 추가 Vendure Admin UI 취소 분기 근거 11개를 각 첫 scan 전에 agent가 작성했다. 업무 의미의 사람 승인 정답은 아니다. Saleor 원래 설정은 strictNullChecks 전제에서 거부됐고, 명시적 과업 설정의 import closure는 806개 구현 파일/오류 1,713개였다. Vendure는 원래 설정 581개/오류 2,372개, 과업 설정 327개/오류 1,058개였다. 의존성을 설치하지 않은 격리 환경의 결과이며 upstream의 전체 결함을 증명하지 않는다.

단순 그룹/FCA·LSP·사람 시간은 측정하지 않았다. 이름 검색의 파일 도달과 특정 조건의 이해를 분리해 기록했다. 준비 비용과 분석 실패도 Gate 4 관련 관찰이며 Gate 2~4 통과 근거가 아니다. 다음 검증 가설은 “Vendure의 strict를 유지하고 고정 의존성/common 빌드를 준비하면 원문 과업의 오류 없는 분석 범위를 확보할 수 있는가”다. [자료와 불확실성](reviews/2026-11-08-public-app-suitability.md).

## 2026-11-08 공개 앱 독립 재현과 투자 한도

[독립 리뷰](reviews/2026-11-08-public-app-independent-review.md)에서 136개 테스트·비교 4/4, 새 다운로드 원문 inventory·Program·outcome·검색 기준선 일치와 같은 cache의 비시간 13개/17개 재현을 확인했다. 경로 간 타입 표시 문자열 차이도 재확인했으므로 이식성 통과를 주장하지 않는다. 새 결함은 확인하지 않았으며 실패/과업 준비 완료와 실제 분석 표본 확보를 구분한다.

사용자는 Vendure 준비를 총 30분 한도로 한 번 더 검증하기로 선택했다(ADR-019). 검증할 가설은 기존 의존성/common 빌드로 오류 없는 입력을 얻을 수 있는지다. 그것만으로 유용한 FCA 범위를 얻는다는 가설까지 검증되지 않는다. 네 진입 파일의 함수 inventory도 129개로 기본 객체 상한을 넘으며 HTML 두 근거는 수동이다. 설치·진단·범위의 결과를 나눠 보고하고, 실패나 범위 부적합이면 다음 투자/분석 계약을 재판단한다. Gate 2~4와 사람 정답 승인은 미검증으로 유지한다.

## 2026-11-08 후속 · Vendure 의존성 준비와 범위 상한

[준비 인계](reviews/2026-11-08-vendure-preparation.md)에서 고정 의존성/common 빌드 후 기존 4진입 설정의 진단 1,058→0을 관찰했다. 총 359.668초로 30분 마감 내 종료했다. 원래 설정에는 test 이름 오류 495개가 남는다. 원문 4,735개 항목과 11개 anchor는 그대로이며 strict/paths/lock/generated source를 수정하지 않았다. 설치 lifecycle은 생략하고 full app/native runtime은 검증하지 않았다.

오류 없는 과업 입력 확보 가설은 해당 설정에서 지지되지만 유용한 FCA 범위를 얻었다는 뜻은 아니다. 전체 context 2,264객체/4,288속성이 기본 128/64를 모두 넘는다. 네 진입 파일 자체도 129함수다. 단순 그룹/FCA는 미실행이며 작은 성공 함수 선택이나 상한 확대를 하지 않았다. 같은 설치 cache에서 관찰 9파일은 byte 일치했고, 설치/빌드 독립 재현 및 다른 경로의 타입 표시 재현은 미검증이다.

다음 권고는 질문에 따른 과업 범위 선택 계약 검토다. 탐색 facts와 논리 검증 전제의 분리 또는 표본 전략 재검토도 대안이며 이번에 구현하지 않았다. HTML 두 근거는 계속 수동이고 사람 과업/정답 승인·Gate 2~4는 미검증이다. 준비 비용과 분석 가능성의 관찰을 제품 효용으로 바꾸지 않는다.

## 2026-11-08 S1 · 도메인 모델 연결과 FCA 기여 관찰

[실험](../experiments/domain-model/README.md)은 기존 준비 cache를 읽기만 하며 agent 작성 원문 fact 16개·모델 12항목을 FCA 전에 고정했다. 네 클래스 78메서드×6직접 호출 역할에서 468개 셀(yes43/no425/unknown0)을 자동 관찰했다. 형식 개념8/후보5/관계1, 잘림 없음이다. 후보5개 모두 동일 사실의 단순 그룹에 있고 추가 교집합은 0이다. 두 모델 항목의 후보 링크 추가 외 의미 변경은 없다. 해당 표본/속성에서 H-F의 추가 기여를 관찰하지 못했다.

이미 알려진 취소/환불 연결과 선택된 역할을 사용한 목적 pilot이다. mutation·modal 기술 그룹이 업무 동일성을 뜻하지 않으며 callback 집계는 실행/호출 그래프가 아니다. 역할·source 설명·모델·해석은 agent가 수동 작성했다. 자동 runner 3.033/2.768초는 작성/검토 비용을 포함하지 않고 사람 시간/agent token·H-O는 미측정이다.

전체163테스트/기존4비교·12비시간파일 재현과 근거/참조/승인 변조 거부는 구현·측정 계약의 검사다. 사람 업무 의미 승인과 agent 변경 효용은 별개다. S1 독립 리뷰 후 로컬 취소 reason 입력의 작은 변경 pilot을 코드+문서/모델/동등 정보 문서 조건으로 비교하는 [S2 설계](../experiments/domain-model/evaluation/S2-PROTOCOL.md)를 남겼다. 실제 변경·fixture 구현·비교·S3·Gate 2~4 상승은 하지 않았다.

## 2026-11-08 S1 독립 검토 · 계산 재현과 인계 계약

새 실행의 12비시간 파일 일치, 독립적인 6속성/64부분집합 폐포 대조가 통과했다. 후보 5개 모두 단순 그룹과 같다. 지지 집합은 mutation28/modal8/cancel2/refund1/결과반환2/닫기2다. 비어 있지 않은 쌍 교집합 세 가지는 모두 cancel/refund/modal의 포함 관계이며 나머지는 분리돼 있다. 이 역할 설계는 새로운 교차 묶음을 발견할 여지가 적으므로 H-F를 강하게 반증한 표본으로 해석하지 않는다. 수동 모델의 존재도 H-O를 입증하지 않는다.

[독립 리뷰](reviews/2026-11-08-domain-model-independent-review.md)는 개념→동작의 기계적 탐색 불일치(R6), standalone validator의 target/분석 입력 변경 미검출(R7)을 재현했다. 전체 runner는 입력 변경을 거부하므로 과거 고정 결과의 무효를 뜻하지 않는다. agent 인계 계약을 보완하고 S2의 자료/fixture 동결을 준비하며, 사람 승인·유지 비용·agent 효용은 미검증으로 유지한다.

## 2026-11-10 S2 비교 실행 전 준비 합의

ADR-028에 따라 무요청 종료의 가상 취소 사유 과업과 제한된 메서드 평가를 채택하고, A/B/C 각각3회 비교를 위한 준비를 승인했다. B–A는 구조화된 도메인 지식의 추가 제공 효과, B–C는 동등 지식의 일반 설명 문서 대비 표현 효과, C–A는 일반 문서 제공 효과를 관찰한다. 현재 C의 필드 나열을 재구성하고 양방향 의미 대응·근거/불확실성 보존을 검토한다. 표현 차이의 효과를 온톨로지 자체 또는 FCA 구축 기여의 증명으로 확대하지 않는다.

[개발 지시](reviews/2026-11-10-s2-trial-preparation-instructions.md)는 계약·자료·격리/계측·새 배포 동결과 리뷰 인계까지만 포함한다. 실제 비교는 미실행이며 성능·사용 token/time·사람 재작업 수치는 미측정이다. 52개 동작 사례는 실행별 진단이고 독립 실험 표본52개가 아니다. 과업 하나의9회 실행으로 일반적 우월성을 판단하지 않으며, 미지원/중단과 환경 장애를 별도 보고한다. 준비 검증·실행 정책 합의는 모델 업무 의미 승인이나 H-O/H-F 효과 검증을 대신하지 않는다.
