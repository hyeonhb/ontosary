# Ontosary 첫 PoC 독립 기술·제품 리뷰

검토일: 2026-11-04, Asia/Seoul. 역할: 구현과 분리된 Technical & Product Reviewer.

## 1. 종합 평가

**권장 방향: 현 방향 유지. 단, 다음 작업을 실제 corpus 확장에서 논리 정규화의 정확성 수정으로 변경할 것을 제안한다.**

코드 사실·발견 후보·승인 지식을 분리하고, 타입 구조만으로 업무 의미를 확정하지 않으며, 작은 유한 분석으로 시작한 방향은 제품 목표에 맞는다. FCA와 논리 비교의 계산 기반도 확인했다. 하지만 컴파일 오류 없는 입력에서 CLI가 실행 의미와 다른 `Equivalent`를 성공(종료 코드 0)으로 반환하는 두 결함을 재현했다. 따라서 첫 PoC의 구성 요소는 구현됐으나 **Gate 1 통과로 볼 수 없다.**

이 발견은 FCA/유한 열거 접근 자체가 실패했다는 근거가 아니다. 정규화가 잘못 만든 입력을 열거기가 정확하게 계산해도 소스 코드에 대한 결론은 틀릴 수 있다는 근거다. Public Beta나 지원 문법 확장은 아직 권하지 않는다.

### 검토 대상의 고정과 변경 경계

- 로컬 `main`, 커밋 없음(`git log -1` 실패: 아직 커밋이 없음). 시작 시 프로젝트 전체가 untracked였다. 리뷰 결과도 untracked이며 커밋·배포하지 않았다.
- 요청한 AGENTS, README, PRODUCT, ARCHITECTURE, RESEARCH, ROADMAP, DECISIONS, PROGRESS가 모두 존재했다. DEPENDENCIES도 확인했다.
- `src/core` 전체, CLI 전체, 테스트 3개와 fixtures, React 예제, 실험 runner와 기존 결과를 읽었다.
- 커밋 대신 [42개 기존 파일의 SHA-256](evidence/2026-11-04-source-fingerprints.json)을 보존했다. 이 목록은 검토 중 생성된 빌드 산출물과 리뷰 파일을 제외한다.
- 기존 소스·테스트·설정·계획 문서·실험 결과는 수정하지 않았다. 이번 판단과 우선순위는 리뷰어의 변경 제안이며 기존 ROADMAP의 결정 기록을 대체하지 않는다.

## 2. 구현 상태와 직접 실행 결과

| 초기 범위 | 코드/실행으로 확인한 상태 | 실제 한계 |
| --- | --- | --- |
| 타입·함수·참조·조건·소스 위치 | 구현. TypeChecker 심볼 해소, 선언 위치 ID, 참조와 진단 포함 | 호출 그래프·전이적 타입 그래프가 아님. 최상위 조건, 클래스 필드 등 제외 |
| Formal Context/FCA | 구현. 함수 객체, 타입/속성/반환/조건 속성, NextClosure | 후보 순위·업무 의미 라벨 없음. 포함 관계는 Hasse edge가 아님 |
| 논리 IR | 구현. eq/neq/and/or/not/constant | enum 접근·this 매개변수에서 정확성 결함 확인 |
| 유한 비교·함의·반례 | 구현. 양방향 함의, 한도 사전 검사, 전제 요구 | IR이 올바르다는 조건하의 결과. 임의 JS 검증이나 버그 판정이 아님 |
| React+TS+Vite | 동작 코드와 production build 확인 | 분석 대상 데모이며 Ontosary의 탐색/검토 UI는 아님 |
| scan/concepts/compare CLI | JSON·근거·종료 코드 구현, 기존 CLI 테스트 통과 | 비교할 두 함수를 사람이 골라야 함. 승인·검색 인터페이스 없음 |
| 자동 테스트·실험·문서 | 존재하고 기존 검증 통과 | 인공 예제 편향, runtime differential 검증 범위 부족 |
| Approved Knowledge | 빈 배열로 분리 | 승인·보류·병합·버전 관리 미구현 |

### 실행 기록

환경: Node v22.19.0, pnpm 11.19.0, TypeScript 5.9.3. 설치된 직접 의존성은 package.json과 일치했다. 코어의 외부 런타임 의존성은 TypeScript 하나이며 `fs`/`path`는 Node 내장 모듈이다. React/Vite는 코어 밖에 있다.

1. 루트의 `pnpm check`: 코어/예제 타입 검사, **3개 파일·41개 테스트**, Vite production build 모두 통과. 새 기능이나 기존 코드 수정이 없으므로 같은 검사를 반복하지 않았다.
2. 기존 실험 결과를 덮어쓰지 않기 위해 `/tmp`에 소스·예제·runner·설정 복제본을 만들고 설치된 node_modules를 연결했다. 최초 `pnpm experiment`는 pnpm의 자동 의존성 재설치 확인이 비대화형 환경에서 중단됐다. 승인 제한이나 제품 오류가 아니며 설치 강행 없이 `pnpm_config_verify_deps_before_run=false pnpm experiment`로 복제본에서 재실행했다. 복제본 빌드와 4개 비교 모두 통과했다. 이 환경 변수는 해당 명령에만 적용했으며 저장소 설정은 바꾸지 않았다.
3. 실험 재현: 파일 4, 타입 6, 함수 13, 지원 predicate 6/미지원 7, context 13×26, 형식 개념 20, 후보 8, 포함 관계 8, 잘림 없음. [summary](evidence/2026-11-04-experiment-summary.json).
4. `pnpm list --depth 0`, `pnpm licenses list --json`: 설치된 45개 패키지 manifest 확인. MIT/Apache-2.0/MPL-2.0/ISC/BSD-3-Clause. 새로운 의존성을 도입하지 않았다. 모든 플랫폼 바이너리나 라이선스 법률 검토를 수행했다는 뜻은 아니다.
5. 독립 검증: [재현 스크립트](evidence/2026-11-04-independent-check.mjs), [원시 결과](evidence/2026-11-04-independent-results.json).
   - 서로 다른 논리식 16개 × 9개 입력 = **144회** runtime/IR 일치.
   - 논리식 **256개 순서쌍**의 동치·함의·차이 판정을 실제 함수 진리표와 대조. **336개 방향별 반례**를 실제 함수에 재입력해 확인.
   - 2값 인자 12개: 4,096개 전수 평가. 13개: 8,192개를 열거하기 전에 Unknown, 평가 0회.
   - **4객체×3속성 관계 행렬 4,096개**를 객체 부분집합 전수열거 oracle과 대조. 속성 순서도 사전순이 아닌 `z,a,m`을 사용. 모든 extent/intent·개념 수 일치.
   - 아래 R1/R2는 코어뿐 아니라 실제 CLI에서도 `Equivalent`, 종료 코드 0을 재현.
6. 새 설치의 재현성, 다른 OS, 대규모 프로젝트, 사용자 세션, 브라우저 UI smoke check는 이번 리뷰에서 새로 검증하지 않았다. 과거 PROGRESS의 브라우저 확인은 과거 보고로만 취급한다.

재현 명령(저장소 루트):

```sh
pnpm build
node docs/reviews/evidence/2026-11-04-independent-check.mjs
```

스크립트는 임시 프로젝트를 생성·실행한 뒤 삭제한다. 정상 사례에는 assert를 사용하지만 결함 사례는 관찰값을 출력하므로 **스크립트 종료 코드 0을 Gate 1 통과로 해석하면 안 된다.** 수정 후 개발 세션이 이 사례들을 실제 실패/성공 회귀 테스트로 옮겨야 한다.

## 3. 기술적 검토 결과

### R1 — Critical / 확인된 결함: enum 멤버 접근에서 receiver 평가를 생략

위치: `src/core/logic.ts:45–53`, `:68–70`.

`literal()`은 property의 심볼이 EnumMember이면 receiver의 문법과 평가를 검사하지 않고 선언의 상숫값을 반환한다. `variable()`에 있는 optional 접근 거부 경로를 타지 않는다.

```ts
export enum E { A = 'a', B = 'b' }
export function optionalEnum(e?: typeof E) { return e?.A === 'a'; }
export function always(e?: typeof E) { return true; }
```

- TypeScript 진단 0개.
- `optionalEnum`을 `constant true`, 변수 없음으로 정규화한다.
- CLI `compare ... optionalEnum always --assume-same-input --json` → `Equivalent`, 평가 1회, 종료 0.
- 실제 `optionalEnum(undefined) === false`, `always(undefined) === true`.
- 동일 입력을 사용했고 입력은 선언 타입에 유효하다. 상태 변이·getter·proxy가 없다. 사용자가 잘못된 동일 입력 전제를 준 사례가 아니다. 문서상 optional 접근은 거부되어야 하는데 성공으로 처리된다.

같은 원인으로 `getEnum().A === 'a'`도 constant true가 된다. 검증 fixture의 `getEnum(): typeof E`는 예외를 던지며 실제 함수도 예외를 던진다. 호출이 포함된 표현식을 unsupported로 처리하지 않고 receiver 평가를 제거한 것이다.

영향: 사용자가 비교 결과를 규칙 이해의 근거로 신뢰할 수 없고, 미지원 문법을 성공으로 표현하지 않는 원칙을 위반한다.

권장: enum 상수 판정에 허용 가능한 receiver와 심볼 해소 경계를 명시한다. 정상적인 enum 선언/허용된 import 경로는 유지하되 optional chain, 호출, 타입 단언 등 미지원 평가를 숨겨서는 안 된다. 지금 단계에서는 모델링 불가한 경우 이유가 있는 Unsupported를 반환하는 것이 충분하다. 단순히 optional 토큰 하나만 막고 동일 원인의 다른 receiver를 놓치지 않는다.

### R2 — Critical / 확인된 결함: `this` 타입 매개변수로 실제 인자 번호가 이동

위치: `src/core/logic.ts:17–18`, `:40`, `:90–97`; 관련 표시 계약 `src/core/analyzer.ts:121`.

```ts
type S = 'a' | 'b';
function withThis(this: void, a: S, b: S) { return a === 'a'; }
function first(a: S, b: S) { return a === 'a'; }
function second(a: S, b: S) { return b === 'a'; }
```

- AST 매개변수 배열의 index를 그대로 `argN`에 사용한다. `withThis`의 `a`가 arg1이 된다.
- `withThis` 대 `second`: CLI는 Equivalent/종료 0. 실제 동일 입력 `('a','b')`에서는 true 대 false다.
- `withThis` 대 `first`: 실제로 동치인데 Different로 반환한다. 잘못된 확신과 잘못된 반례를 모두 만든다.
- TypeScript 진단 0개. 이 `this: void`는 런타임 인자가 아니며 실행 코드에서도 제거되는 것을 확인했다. [TypeScript 공식 문서](https://www.typescriptlang.org/docs/handbook/2/classes.html#this-parameters)도 이 의미를 명시한다.

권장: 런타임 인자 순서와 receiver 타입 정보를 구분하거나, 당장은 explicit this 함수를 전체 Unsupported로 처리한다. 둘 중 구현 부담이 낮고 명확한 계약을 선택해도 된다. `argN`이 실제 첫/둘째 인자를 뜻한다는 CLI 설명과 일치해야 한다. 전체 predicate와 개별 condition의 정책도 일치시킨다.

### R3 — Medium / 확인된 출력 계약 불일치: 건너뛴 JS를 `files`에 포함

위치: `src/core/analyzer.ts:45–47`, `:56`, `:126–127`.

`allowJs: true` 프로젝트에서 `files`는 `["ignored.js", "input.ts"]`인데 functions는 `tsFunction` 하나뿐이다. JS 건너뜀은 omissions로 알리지만 `files`는 실제 분석 파일 목록이라는 ARCHITECTURE 설명과 다르다. `experiments/run.mjs`는 이 길이를 파일 수로 집계한다.

영향: 다음 coverage 실험에서 Program 포함 파일과 실제 분석 파일을 같은 분모로 사용할 위험이 있다. JS를 지원하지 않는 것 자체가 결함은 아니다.

권장: 실제 방문한 파일만 files에 넣거나 Program 파일·분석 파일·제외 파일을 명시적으로 구분하고 문서와 집계의 계약을 맞춘다. mixed TS/JS fixture로 확인한다. R1/R2 뒤, corpus 측정 전에 수행할 작은 후속 작업이다.

### 결함과 구분해야 할 설계 한계 및 긍정 결과

- FCA의 폐포 계산, extent/intent, strict intent 포함에 대응하는 반대 방향 extent 포함은 검토·독립 실험 범위에서 올바르다. 빈 context와 잘림 경계는 기존 테스트가 다룬다. 수학적 정확성을 업무 의미 정확성으로 확대하지 않는다.
- 핵심 비교 루프는 검증한 올바른 IR들에서 정확했다. `Implies`도 비동치일 수 있으며 방향과 두 반례가 구분된다. 같은 키의 서로 다른 도메인은 Unknown, 동일 입력 전제가 없을 때도 Unknown이다.
- 동명 심볼/import alias/구조적으로 같은 User와 Customer의 구분은 소스와 기존 테스트에서 확인했다. 구조적 타입 호환성을 업무 개념 동일성으로 직접 승격하지 않는다.
- 모든 후보가 unreviewed, approvedKnowledge는 빈 배열이다. 업무 정책 위반이라는 단정도 출력하지 않는다.
- 컴파일 오류 시 정규화를 거부하고 CLI concepts/compare도 실패한다. 코어 discoverConcepts의 진단 확인 책임은 호출자에게 있다는 문서가 존재한다. 이는 현 계약이며 이번 리뷰에서 새로운 결함으로 세지 않았다.
- 128객체/64속성/256개념 한도와 논리 4,096조합 한도는 실제 구현돼 있다. 이것이 전체 TypeScript Program 로딩의 시간·메모리를 제한하지는 않는다. 대규모 성능은 미측정 위험이다.
- 함수 내부의 조건 추출은 경로·변이 이전 상태를 복원하지 않는 식 단독 분석이다. 코드가 출력하는 전제 안에서 해석해야 한다.
- `sameInput`은 사용자 assertion이다. 업무적으로 가능한 입력/필드 상관관계, 같은 정책이어야 하는지 여부는 별도 검증 사항이다.
- 작은 파일에 여러 책임이 압축된 표현은 유지보수 위험이 있으나 취향만으로 리팩터링을 우선하지 않는다. 이번 실패를 방지하는 테스트·지원 경계가 먼저다.

## 4. 연구 가설 검증 결과

| 명제 | 판단 | 근거/추가로 필요한 것 |
| --- | --- | --- |
| TS에서 제한된 사실을 추출할 수 있다 | 확인한 범위에서 검증 | 예제·심볼 테스트·실행 결과. 실무 coverage는 별도 |
| FCA로 정확한 형식 개념을 열거할 수 있다 | 작은 bounded context에서 강한 근거 | 기존 512개 3×3 + 독립 4,096개 4×3 oracle 대조 |
| 지원됐다고 출력한 predicate가 원래 함수 의미를 보존한다 | **현재 구현에 대한 보편적 주장은 반증됨** | R1/R2. 알고리즘 전체나 향후 수정 가능성을 반증한 것은 아님 |
| 올바른 IR의 유한 비교가 동치·함의·반례를 계산한다 | 확인한 범위에서 검증 | 256쌍, 336개 실행 반례, 한도 경계 |
| FCA 그룹이 유용한 비즈니스 개념이다 | 미검증 | 후보를 정답으로 삼지 않은 라벨과 검토 필요 |
| 기존 도구/LLM보다 유용하다 | 미검증 | 동일 과업·예산·정답에 대한 비교 없음 |
| 도메인 이해 시간·변경 위험·유지 비용을 줄인다 | 미검증 | 개발자 과업 관찰과 반복 사용 필요 |

FCA 의미 가설이 실패했다고 결론 내릴 근거도 아직 없다. 넓은 후보는 실패 모드의 관찰이지 정량 precision/recall 측정값이 아니다.

## 5. 제품 가치와 차별성

### 현재 사용자 과업에 제공하는 경험

| 과업 | 지금 가능한 일 | 부족한 부분 |
| --- | --- | --- |
| 특정 업무 개념 관련 코드 탐색 | 타입/속성 공유 그룹과 소스 근거에서 탐색 시작 | 업무 용어 검색·의미 매핑·랭킹 없음 |
| 유사 도메인 로직 찾기 | shared condition/property 후보를 사람이 검토 | 구조가 다른 동의 로직은 놓칠 수 있음. 비관련 기능도 섞임 |
| 분산 조건 비교 | 선택한 두 함수를 CLI에서 비교하고 차이 입력 확인 | 지원 범위 좁음, R1/R2 수정 필요, 입력 대응 수작업 |
| 규칙 구현 위치 파악 | 함수·조건 위치 제공 | 호출 경로/영향 전체/정책과 코드의 대응 증명 없음 |
| 기존 도메인 이해·지식 유지 | 결정적 JSON을 근거 자료로 활용 가능 | 승인·변경 추적·유지 워크플로 없음 |

예제의 `formal-17`은 상담 조건 4개를 같은 status 필드로 묶어 검토 시작점으로 사용할 가능성이 있다. 반면 `formal-3`은 Listing을 사용하는 UI·가격·조건 등 10개 함수를 포함하고, `formal-7`은 `formatPrice`와 `isPremium`을 묶는다. 이는 개념 이름을 자동 승인하지 않은 설계가 필요한 이유다. 아직 유용한 후보 비율이나 검토 시간을 측정하지 않았다.

### 최소 경쟁 확인 및 설치 이유에 대한 판단

2026-11-04 공식 문서로 제한된 확인을 수행했다. Semgrep은 구조 패턴·import 등가 처리·상수 전파를 이미 제공한다. [Semgrep 문서](https://docs.semgrep.dev/writing-rules/pattern-syntax). CodeQL은 JS/TS의 지역·전역 데이터 흐름과 경로 기반 분석을 제공한다. [CodeQL 문서](https://codeql.github.com/docs/codeql-language-guides/analyzing-data-flow-in-javascript-and-typescript/).

따라서 정적 분석·참조 연결·그룹 JSON 자체를 독점적 차별성으로 주장할 수 없다. 위 두 도구가 Ontosary의 정확한 업무 흐름을 대체하거나 못 한다고 단정할 비교 실험도 하지 않았다. 범용 AI 에이전트의 최신 성능·가격·우열은 검증하지 않았다.

**설치 이유의 유망한 가설**은 “관련 규칙 후보를 적은 설정으로 모으고, 각 판단을 소스·전제·실행 가능한 차이 입력까지 연결해 반복 검토 비용을 줄인다”이다. 현재는 이 경험의 재료를 만든 단계이며 독립 도구를 추가로 설치할 이유가 입증된 단계는 아니다.

FCA의 순증분도 따로 확인해야 한다. 같은 facts에서 필드별 역색인/간단한 공유 속성 그룹만 보여주는 기준선이 비슷한 효과라면, FCA를 기본 경로로 유지할 이유가 약해진다. 반례 생성이 더 큰 가치라면 제품의 첫 사용 경험을 “선택한 규칙 비교” 중심으로 좁힐 수 있다.

## 6. Gate 판단과 다음 단계

| Gate | 상태 | 이유 |
| --- | --- | --- |
| 1 기술적 정확성 | **미통과** | 서로 다른 실행 결과를 Equivalent로 확정하는 R1/R2 |
| 2 의미적 유용성 | **미검증, 통과 근거 없음** | 인공 예제의 후보 관찰만 있음 |
| 3 기존 방법 대비 효용 | **미검증, 통과 근거 없음** | 비교 과업 실험 없음 |
| 4 도입·유지 비용 | **부분 확인, 미통과** | 로컬 clone/tsconfig/CLI는 작동. 실제 2개 프로젝트 설정 시간·미지원률·ID 유지 비용 미측정 |
| 5 공개 배포 가능성 | **미통과** | MIT·문서·CLI 기반은 있으나 private/미배포, 정확성 결함, 사용자 과업 근거 부족 |

**바로 다음 작업 하나: 정규화의 두 잘못된 확정 판정을 차단하고 실행 의미 대조 회귀 검증을 추가한다.** 세부 지시와 완료 조건은 [NEXT_PLAN](NEXT_PLAN.md)에 독립적으로 작성했다. 범위를 넓히는 작업이 아니며, Unsupported로 좁히는 해결도 허용한다.

그 뒤의 후속 후보는 다음 순서다.

1. R3 파일 분모를 정리하고 공개/허가된 작은 TS corpus 2개, revision·라이선스·분석 범위를 고정한다. 초기 ROADMAP의 방향은 여전히 타당하지만 정확성 수정 뒤로 이동한다.
2. 사람이 코드 사실과 업무 의미를 나눠 작성한 20~30개 라벨을 만든다. 출력 후보를 그대로 정답으로 사용하지 않는다. 누락/오연결/미지원과 과업 실패를 구분한다.
3. 구체 과업을 “관련 규칙 위치 찾기 / 유사 규칙 후보 검토 / 두 조건 차이 설명”으로 고정한다. 동일 facts의 단순 속성 그룹, +FCA, 선택한 비교에 +논리 검증을 분리 평가한다. 일반 검색/LSP도 기준선에 포함한다.
4. 준비 시간·정답 도달률·근거 위치 정확성·잘못된 확신·검토 시간을 측정한다. 후보 검토 부담과 미지원으로 끝난 과업도 분모에서 빼지 않는다. 과업 순서를 바꾸고 가능하면 별도 평가자가 라벨을 검토한다. 작은 표본은 탐색적 결과로 보고한다.
5. 개선이 없으면 FCA 기본 노출을 축소/보류한다. 반례의 가치가 반복 관찰되면 제한된 규칙 비교를 먼저 제품화한다. 실제 막힌 사례가 모인 뒤 문법 하나를 넓힌다. 모델/예산/프롬프트를 고정한 LLM 비교는 그 이후며, 현재 A→B→C→D 순차 비교만으로 모든 요소의 독립 효과와 상호작용이 증명되는 것은 아니다.

유용성 평가의 목표치와 시간 예산은 결과를 보기 전에 고정한다. 이번 리뷰에는 실제 과업 데이터가 없으므로 임의의 성공률을 달성했다고 적지 않는다. 모든 Gate가 전체 연구를 직렬로 막는 절차는 아니며, corpus 선정·라벨 설계는 정확성 작업과 독립적으로 준비할 수 있다.

## 7. 개발 세션 전달용 지시문

[NEXT_PLAN.md의 “개발 세션에 복사할 지시문”](NEXT_PLAN.md#개발-세션에-복사할-지시문)을 사용한다. 이 지시문은 이 리뷰 대화를 모르는 개발 세션에서도 실행하도록 목표·근거·최소 재현·범위·제외 범위·완료 조건·검증·문서 인계를 포함한다. 별도 세션으로 메시지를 보내거나 구현을 수행하지 않았다.

## 8. 리뷰 문서 인계

- [REVIEW_CONTEXT.md](REVIEW_CONTEXT.md): 역할, 검증된 사실, 미검증 가설, 미해결 문제, 다음 판단 기준.
- [NEXT_PLAN.md](NEXT_PLAN.md): 현재 최우선 작업과 독립적인 개발 지시.
- [독립 검증 코드](evidence/2026-11-04-independent-check.mjs)와 [관찰 JSON](evidence/2026-11-04-independent-results.json): 결함 재현과 정상 사례 확인.
- [소스 fingerprint](evidence/2026-11-04-source-fingerprints.json): 커밋 없는 검토본의 식별.
- [실험 summary](evidence/2026-11-04-experiment-summary.json): 복제본에서 재실행한 기존 실험 결과.

다음 리뷰는 문서상 “완료”가 아니라 수정된 소스·실행 결과로 R1/R2 상태를 재판정한다. 실제 프로젝트/사용자 비교가 없으면 Gate 2~4를 통과로 올리지 않는다.
