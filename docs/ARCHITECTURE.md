# 현재 아키텍처

2026-11-10 S2 실행 전 준비: **자료·평가·계측 준비 구현, 전체 실행 환경은 차단 상태**. [인계](reviews/2026-11-10-s2-trial-preparation.md). 사용자 후속 결정에 따라 token hard cap을 필수 조건에서 제외하고30분 제한·raw usage/누락/참고선 초과 기록을 채택했다. 동일 TASK/공개 안내, 일반 문서 C와68view·1511단위 대응/사람 검토 묶음, 공개 타입 검사, 실행/수집 대역을 구현했다.252테스트(skip0)·비교4/4,29제출60파일·새 준비157비시간 파일 재현, A/B/C 실제 배포를 확인했다. 모델12항목/16링크·승인0과 B68view는 유지했고 agent 자료는84파일·새 bundleId다. macOS 파일/네트워크 거부와 package.json 예외의 명시적 차단을 검증했지만 **분리된 자식 프로세스의 종료 탈출**이 남아 실제 실행과 불변 제출 보장을 차단한다. 실제 모델 호출0·본 비교0, trialAuthorized/readyForTrial=false·results=null·사람 동등성/의미 검토 pending이다. 다음은 종료 경계 보완과 독립/사람 리뷰이며 API·새 플랫폼 투자는 하지 않았다. 아래는 각 시점 기록이다.

전체 구조와 설계 이유를 먼저 이해하려면 [사람을 위한 아키텍처 안내](guide/architecture.md)를 읽는다. 이 문서는 세부 지원 범위와 구현 계약을 관리한다.

## 구성과 의존성

단일 private npm 패키지 `ontosary`를 사용한다. 작은 PoC에 workspace 패키지·플러그인 시스템·서버를 추가하지 않았다. `src/core`의 런타임 의존성은 TypeScript뿐이다. Node 내장 API로 tsconfig와 CLI를 처리한다. React·Vite·Vitest는 예제·개발 의존성이다. Vite 없이 `node dist/cli/index.js` 또는 코어 API를 실행할 수 있다.

```text
TS project / tsconfig
  → TypeScript Program + TypeChecker
  → Code Facts (declaration IDs + source evidence + diagnostics)
      → function attributes → Formal Context → NextClosure → unreviewed candidates
      → restricted condition IR → finite enumeration → comparison + witnesses
CLI: inputs and JSON only          React example: analysis target only
```

## 데이터 계약

`src/core/model.ts`가 공개 TypeScript/JSON 계약이다. 스키마 버전은 1이다. R3 수정은 문서화된 files 계약의 오류 수정이며 필드 구조는 변경하지 않는다. 제외 파일 집계는 omissions의 파일 근거를 사용하고, 누락 레코드 수 자체를 파일 수로 해석하지 않는다(다른 종류의 누락도 존재한다).

- **Code Facts**: 타입/인터페이스/enum, 필드, 함수 입력·출력, 타입·속성·심볼 참조, 조건의 텍스트·정규화 상태. `scan`과 `compare` 출력의 `category`는 `code-facts`다. 참조 목록에는 선언 이름의 심볼 연결도 포함하므로 호출 그래프가 아니다.
- **Discovered Candidates**: FCA extent(함수 ID)와 intent(공유 속성), 근거, `reviewStatus: unreviewed`. 이름은 `formal-N`이며 업무 개념명을 부여하지 않는다.
- **Approved Knowledge**: `approvedKnowledge: []`로 별도 구분한다. 승인·병합·버전 관리는 아직 없다.

ID는 `<project-relative file>:<start offset>:<symbol name>`이다. 동명 심볼과 구조적으로 같은 타입을 합치지 않으며 import alias는 실제 선언으로 해소한다. 편집 후에도 유지되는 영구 ID가 아니다. 위치는 1-based line/column, UTF-16 offset이며 end는 배타적이다. 모든 함수·타입·조건에 근거가 있고, 참조는 대상 선언과 사용 위치를 함께 기록한다. FCA incidence는 이 ID로 선언 근거와 함수 근거를 추적한다.

## TS 추출 범위

지정한 tsconfig의 Compiler Program에 포함된 TS/TSX/MTS/CTS 구현 파일을 탐색한다. `ScanResult.files`는 실제 방문하는 구현 파일 목록이며 이 목록 자체로 AST 순회한다. 따라서 실험의 `files.length`도 실제 분석 파일 수다. 로컬 JS/JSX/MJS/CJS 등 미지원 구현 파일은 `omissions`에 각 파일의 근거 위치와 제외 사유를 기록한다. allowJs 설정만으로 누락을 보고하지 않는다. TypeScript Program은 수정하지 않으므로 제외 파일의 타입 해석·심볼 참조·컴파일 진단은 유지된다. JS만 있는 프로젝트는 files/types/functions가 비어 있고 제외 근거가 있는 결과를 반환한다. `.d.ts`와 외부 라이브러리는 선언 참조 대상으로 사용하되 분석 파일 목록에는 포함하지 않는다. 함수 선언·함수 표현식·arrow·메서드·접근자·생성자를 기록한다. 중첩 함수는 개별 객체이며 바깥 함수의 본문 참조에 합치지 않는다.

인터페이스/객체 alias의 필드와 enum 멤버를 기록한다. primitive/union alias는 타입 문자열을 기록하며 필드 구조를 펼치지 않는다. 타입 참조는 명시적 타입 구문, 입력·반환·속성 receiver의 직접 심볼을 수집하며 전이적 타입 그래프는 아니다. 클래스 필드·switch·계산된 속성 접근은 `omissions`로 보고한다. 함수 안의 if/삼항/while/do/for 조건 및 반환식은 상태와 이유를 기록한다. 최상위 실행문의 조건은 추출 대상이 아니다.

컴파일 진단을 출력한다. 하나라도 컴파일 오류가 있으면 모든 정규화 결과를 unsupported로 바꾸고 CLI 비교·FCA를 거부한다. 코어 API `discoverConcepts`는 사실 그룹화 함수이므로 호출자가 진단을 확인해야 한다. `strictNullChecks`가 꺼진 프로젝트는 거부한다. tsconfig project references는 재귀 탐색하지 않고 누락을 보고한다. class type modeling, JS, 프레임워크 의미도 현재 한계다.

## 제한된 논리 IR

`eq`, `neq`, `and`, `or`, `not`, boolean `constant`를 사용한다. 정규화는 구문을 제한된 IR로 옮기는 작업이며, 동치는 IR 문자열의 같음이 아니라 진리표 열거로 판단한다.

- 지원: 엄격 동등 비교, `&&`, `||`, `!`, 괄호, 문자열 리터럴과 그 union, 상수 string/numeric enum 멤버.
- enum 상수 receiver: `E.A`의 E가 enum 선언에 직접 해소되는 식별자여야 한다. 괄호와 named import alias는 허용한다. enum 타입을 가진 매개변수/객체 별칭은 선언 identity가 아니므로 거부한다. optional chain, 호출, 타입 단언, non-null assertion, getter, 중첩/namespace receiver는 상수 folding 전에 거부한다. `E['A']`도 미지원이다.
- explicit this: 타입 전용 `this` 매개변수가 있는 함수/메서드의 전체 predicate와 개별 condition을 Unsupported로 거부한다. 본문의 런타임 this 해석이나 인자 재배치는 구현하지 않는다. `FunctionFact.parameters`는 소스 선언 순서를 보존하므로 this도 기록하지만, 그 인덱스를 런타임 인자라고 해석하면 안 된다. 지원된 정규화의 argN만 런타임 위치를 뜻한다.
- 입력: 필수 매개변수 또는 한 단계의 필수 속성. 도메인은 사용 지점의 narrowed type이 아니라 선언된 매개변수/속성 타입에서 읽는다.
- 보수적 거부: 타입 단언·호출·산술·일반 string/number·동적/선택적/중첩 접근·getter·객체 union·destructuring·기본값/나머지 매개변수·외부 변수.
- 함수 전체 비교: 동기/non-generator 함수의 단일 반환식 또는 expression arrow만 지원한다. 다른 문장이 있으면 해당 함수는 unsupported다. 분기에서 추출한 조건은 식 단독 사실이며 경로 제약을 반영한 함수 의미가 아니다.

비교는 명시적 `sameInput: true`가 필요하다. 변수 키는 `argN[.property]`이며 양쪽에 등장한 동일 키의 도메인은 정확히 같아야 한다. 한쪽에만 등장하는 변수도 함께 열거한다. 모든 입력이 선언 도메인을 지키고, 속성 읽기가 안정적이며, 필드들이 독립적이라는 전제를 출력한다. 타입이 같다고 같은 업무 정책이라고 판단하지 않는다.

최대 4,096 조합을 **열거 전** 확인한다. 일치하면 Equivalent, 한 방향 함의만 성립하면 Implies, 둘 다 아니면 Different이다. 논리적 비동치는 Implies에도 존재한다. 상한/전제/도메인 문제는 Unknown, 문법 문제는 Unsupported다. 각 방향의 반례와 전체 평가 횟수를 반환한다. 공집합 증명·숫자 범위·SMT·프로그램 전체 정형 검증은 구현하지 않는다.

## FCA

Formal Context `(G, M, I)`에서 G는 함수, M은 `type:<declaration ID>`, `property:<declaration ID>`, `returns:<type string>`, `condition:<input declaration ID>`다. I는 해당 함수의 관찰 속성이다. 조건 필드 속성은 정규화 가능한 조건에서만 추출한다. 이름만 같은 필드를 합치지 않는다.

`B′`는 B의 모든 속성을 가진 객체, `A′`는 A의 모든 객체에 공통인 속성이다. NextClosure가 `B = B′′`인 폐집합 intent와 대응 extent를 열거한다. 빈 extent에서 모든 속성이 공통이라는 수학적 정의도 유지한다.

기본 상한: 128 객체, 64 속성, 256 개념. 입력 상한 초과는 오류이고 개념 수 초과는 정확한 prefix와 `truncated: true`를 반환한다. 후보에는 최소 2개 함수와 반환 타입 외 공유 속성이 있어야 한다. 전체 formal concepts도 수학적 검토를 위해 한도 내 함께 출력한다. 관계는 반환된 후보 사이의 **모든 엄격 intent 포함 관계**이며 Hasse cover edge가 아니다. 일부 후보가 필터링되거나 잘렸을 때도 명시한 두 후보 간 포함 관계 자체는 유효하다.

## 확장 지점

[S1 도메인 모델 실험](../experiments/domain-model/README.md)은 별도 경로에 구현됐다. 12개 검토 대기 모델 항목·근거 검증·네 클래스 78메서드×6직접 호출 역할의 단순 그룹/FCA를 제공한다. **제품 core/CLI 계약에는 통합하지 않았다.** 전체 Program을 유지하고 callback 호출식을 소속 메서드의 원문 영역 속성으로 집계하는 별도 계약이다. 위 core의 중첩 함수 facts와 같지 않다. 개념→동작 탐색과 standalone 분석 입력 검증의 R6/R7은 V2에서 보완했고 [독립 재검토](reviews/2026-11-08-domain-model-contract-independent-review.md)를 통과했다.

기본 FCA 상한은 현재 PoC의 계산·결과 관리 예산이며 수학적 최대 크기나 제품의 영구 한계가 아니다. S1에서는 상한을 유지하고 의미 있는 범위에서도 넘으면 실패를 보존한다. 상한 조정이나 다른 열거 전략은 비용·완전성 근거를 갖춘 후속 결정이다.

정적 사실의 coverage 측정, 범위 선택, 비교 전제에 대한 명시적 변수 매핑, 소스 변경에 대한 ID 전략은 후속 후보로 남긴다. React/Next 전용 메타데이터는 공통 facts 위에 추가할 후보이며 현재 플러그인 인터페이스는 없다. 승인 워크플로·LLM 해석·SMT·온톨로지 포맷은 [ROADMAP](ROADMAP.md)의 미래 항목이다.

S1 후속 [V2](../experiments/domain-model/v2/README.md)는 모델 참조의 incoming/outgoing 한 단계 조회와 공통 입력 무결성 검사를 추가한다. anchor-only는 부분 검사이며 분석 입력을 검증하지 않으면 전체 valid를 반환하지 않는다. 제품 core/CLI에는 통합하지 않았다. V1의 역사적 실행/판정은 유지한다.

## S2 준비 구현 — 실험 내부 모듈

2026-11-08 ADR-024/025의 [S2 모듈](../experiments/domain-model/s2/README.md)은 별도 tsconfig로 전체 check에 포함된다. `analysis-session`이 고정 입력/CompilerHost를 검증하고 Program을 한 번 생성한다. 원문 hash와 필요한 text/lineStarts를 재사용하고 seal에서 입력·root/해석 lookup을 재검사한 뒤 dispose한다. `vendure-baseline`이 공개 앱별 입력 명세를 공급한다.

`model`/`validate`는 unknown JSON의 타입·참조·원문 좌표·상태를 검사한다. `query`는 복제한 자료와 ID/방향 adjacency/evidence 색인만 소유하며 compiler/fs/process에 의존하지 않는다. `bundle`은 12항목의 fact22/candidate2 참조 closure와 구성원 선언/역할 정의를 포장한다. baselineId/modelId/bundleId가 입력·해석·배포 파일을 구분하며 baseline 근거를 현재 편집 코드의 사실로 표현하지 않는다.

`prepare`는 B JSON/C Markdown view·대응표·실행 계획을 생성하고 `workspace`는 조건별 allowlist와 원문 inventory만 복사한다. `evaluation`은 제출 클래스 본문/지원 helper를 실행하고 DI/UI/서버 등 제외 seam을 명시한다. Promise/async와 미검토 operator는 unsupported다. evaluator 자료는 workspace에 복사하지 않지만 실제 OS 격리는 unverified다.

제품 core/public API·S1/V1/V2는 유지한다. [독립 리뷰](reviews/2026-11-09-s2-preparation-independent-review.md)의 R8/R9/R10에 따라 평가 경계를 보완했다. `submission`은 고정 설정/의존성에 완전한 제출 snapshot을 반영해 원래 클래스/호출자와 추가 helper를 검사한다. 삭제·범위 밖 변경은 전체 합격이 아니며 교정 runner의 baseline+명시적 delta와 일반 제출을 구분한다. `evaluate`는 typecheck/behavior/overall과 입력·실행 hash 결합을 관리하고 `behavior`는 독립 기대 payload·순서·횟수를 비교한다. 참조 수정은 취소 reason만 바꾸고 환불 reason을 보존한다. 평가 baseline과 제출별 Program은 준비 Program1회와 별도 계측한다.

[독립 재검토](reviews/2026-11-09-s2-contract-independent-review.md)의 R9 잔여에 따라 `modal` 대역을 보완했다. 부모가 실제 전달한 component는 executor가 로드한 constructor 참조로 식별하고 options.locals를 dialog에 전달한다. 별도 사용자 선택 상태는 locals/resolveWith를 덮어쓸 수 없다. 구독 시 실제 select/cancel을 실행하고 resolve를 해당 Observable의 next/complete로 연결한다. 비API 사례의1호출·1구독·1동기 resolve 경계를 벗어나면 unsupported다. 호출별 component/locals/행동/resolve/전달 trace와 기존 payload assertion을 함께 남긴다. sourceBinding만으로 흐름의 충실성을 주장하지 않는다.

[modal 보완 인계](reviews/2026-11-09-s2-modal-fix.md)는 [2026-11-10 독립 재검토](reviews/2026-11-10-s2-modal-independent-review.md)에서 R9 잔여 해결·R8/R10 유지로 판정했다. 제한된 지원 범위의 준비 구현 보완을 완료했다. constructor/field/ngOnInit/HTML/전체 UI 계산·비동기 overlay/네트워크는 여전히 대역/제외 범위다. 과업 정책·B/C 의미 동등성·실제 격리/agent 실행 조건은 미동결, readyForTrial=false다. 본 비교·S3는 실행하지 않았다.

2026-11-10 ADR-028로 [비교 실행 전 준비](reviews/2026-11-10-s2-trial-preparation-instructions.md)를 승인했다. C를 동등 지식의 설명 문서로 바꾸고 공통 과업/공개 검사·실행기 격리/계측·불변 제출/배포 동결을 실험 내부에서 준비한다. 위 구현은 현재 상태이며 이 준비는 아직 구현 전이다. 공개 과업의 무요청 종료 정책은 확정됐고, 정확한 실행 설정·새 C 대응 검토·실제 환경 검증은 후속 개발/리뷰 대상이다. 본 비교는 그 리뷰 뒤 별도로 진행한다.

2026-11-10 실행 전 준비는 `trial/`의 공통 과업·public type check·macOS profile·계측/수집·동결 명세와 `lib/prose.ts`의 C 문서/단위 대응으로 구현됐다. [독립 리뷰](reviews/2026-11-10-s2-trial-preparation-independent-review.md)에서 자료/평가 회귀를 확인했으나 process-group의 detached 자손 종료(R11)와 usage turn 완료 판정(R12)은 보완 대상이다. token hard cap 부재는 차단 사유가 아니며 관측 합계/누락을 정확히 구분해야 한다. 실제 CLI 세션 전체 격리·사람 대응 승인은 미완료이고 실행 진입점은 계속 거부한다. 앞의 구현 전 기록은 당시 합의다.
