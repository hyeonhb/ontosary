# 현재 아키텍처

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

`src/core/model.ts`가 공개 TypeScript/JSON 계약이다. 스키마 버전은 1이다.

- **Code Facts**: 타입/인터페이스/enum, 필드, 함수 입력·출력, 타입·속성·심볼 참조, 조건의 텍스트·정규화 상태. `scan`과 `compare` 출력의 `category`는 `code-facts`다. 참조 목록에는 선언 이름의 심볼 연결도 포함하므로 호출 그래프가 아니다.
- **Discovered Candidates**: FCA extent(함수 ID)와 intent(공유 속성), 근거, `reviewStatus: unreviewed`. 이름은 `formal-N`이며 업무 개념명을 부여하지 않는다.
- **Approved Knowledge**: `approvedKnowledge: []`로 별도 구분한다. 승인·병합·버전 관리는 아직 없다.

ID는 `<project-relative file>:<start offset>:<symbol name>`이다. 동명 심볼과 구조적으로 같은 타입을 합치지 않으며 import alias는 실제 선언으로 해소한다. 편집 후에도 유지되는 영구 ID가 아니다. 위치는 1-based line/column, UTF-16 offset이며 end는 배타적이다. 모든 함수·타입·조건에 근거가 있고, 참조는 대상 선언과 사용 위치를 함께 기록한다. FCA incidence는 이 ID로 선언 근거와 함수 근거를 추적한다.

## TS 추출 범위

지정한 tsconfig의 Compiler Program에 포함된 TS/TSX/MTS/CTS 구현 파일을 탐색한다. `.d.ts`와 외부 라이브러리는 선언 참조 대상으로 사용하되 분석 파일 목록에는 포함하지 않는다. 함수 선언·함수 표현식·arrow·메서드·접근자·생성자를 기록한다. 중첩 함수는 개별 객체이며 바깥 함수의 본문 참조에 합치지 않는다.

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

정적 사실의 coverage 측정, 범위 선택, 비교 전제에 대한 명시적 변수 매핑, 소스 변경에 대한 ID 전략부터 실험한다. React/Next 전용 메타데이터는 공통 facts 위에 추가할 후보이며 현재 플러그인 인터페이스는 없다. 승인 워크플로·LLM 해석·SMT·온톨로지 포맷은 [ROADMAP](ROADMAP.md)의 미래 항목이다.
