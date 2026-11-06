# 다음 개발 계획 — 2026-11-04 독립 리뷰 기준

## 가장 중요한 다음 작업

**논리 정규화가 잘못된 확정 판정을 내리는 두 경로를 차단한다.** 기능 확장보다 근거의 신뢰성이 먼저다. [첫 리뷰](2026-11-04-poc-review.md)의 R1/R2가 선정 근거다.

현재 Gate 1은 미통과다. 기존 `pnpm check` 41개 및 인공 예제 비교 4개 통과와 이 결론은 모순되지 않는다. 기존 검증 집합 밖의 올바른 TypeScript 입력에서 잘못된 Equivalent가 재현됐다.

R1/R2를 수정하고 다시 검증한 뒤, R3의 파일 집계 계약을 정리하고 실제 corpus 실험으로 진행한다. 아래는 바로 다음 한 작업만을 위한 지시문이다.

## 개발 세션에 복사할 지시문

---

당신은 `/Users/hyeon/toys/ontosary`의 구현 담당 개발 세션이다. 이번 작업은 **TypeScript→논리 IR 경계의 false proof를 막는 정확성 수정**이다. 새 분석 기능을 추가하는 단계가 아니다.

### 작업 목표

컴파일 오류가 없는 코드에 대해 실제 실행과 다른 동치/차이를 성공으로 확정하는 두 결함을 제거한다. Ontosary는 기존 코드의 도메인 지식을 근거와 함께 이해하도록 돕는 도구이며, 코드 사실·발견 후보·승인 지식을 구분한다. 잘못된 확정 결과는 이 제품의 신뢰성을 훼손한다. 지원하기 어려우면 명시적 이유가 있는 Unsupported로 거부해도 된다.

### 현재 상태와 근거

먼저 AGENTS.md, docs/PROGRESS.md, ARCHITECTURE, ROADMAP, 그리고 docs/reviews/2026-11-04-poc-review.md를 읽고 git 상태와 현재 소스를 확인한다. 리뷰 시점에는 `main`에 커밋이 없고 기존 프로젝트 전체가 untracked였다. 기존 파일을 새 파일로 오인해 덮어쓰거나 정리하지 않는다. 이후 다른 세션의 변경이 있을 수 있으므로 현재 상태가 우선이다.

리뷰 당시 Node 22.19.0, pnpm 11.19.0, TypeScript 5.9.3이다. `pnpm check` 41개 테스트와 인공 예제 비교 4개는 통과했다. FCA의 4×3 관계 4,096개 독립 대조와 올바른 IR의 256개 순서쌍 비교도 통과했다. 다음 두 결함은 모두 TypeScript 진단 0개이며 CLI에서 Equivalent/종료 0으로 재현됐다.

**R1: enum receiver 평가가 사라진다.**

```ts
export enum E { A = 'a', B = 'b' }
export function optionalEnum(e?: typeof E) { return e?.A === 'a'; }
export function always(e?: typeof E) { return true; }
export function getEnum(): typeof E { throw new Error('not total'); }
export function callEnum(e?: typeof E) { return getEnum().A === 'a'; }
```

- `src/core/logic.ts`의 `literal()`은 EnumMember 심볼만 보고 상숫값을 반환한다(리뷰본 45–53행). equality constant folding은 양쪽 값을 바로 계산한다(68–70행).
- optionalEnum은 constant true로 정규화되고 always와 Equivalent다. 실제 undefined 입력에서는 false 대 true다.
- callEnum도 constant true인데 실제 실행은 예외다. 현재 명시적 미지원인 호출을 enum 접근 뒤에 숨겼을 때 통과한다.
- `variable()`의 optional/accessor 방어만 보완하면 이 경로를 막지 못한다.

**R2: 타입 전용 this 매개변수가 argN을 이동시킨다.**

```ts
type S = 'a' | 'b';
export function withThis(this: void, a: S, b: S) { return a === 'a'; }
export function first(a: S, b: S) { return a === 'a'; }
export function second(a: S, b: S) { return b === 'a'; }
```

- `logic.ts`가 AST parameters index를 런타임 argN에 사용한다(리뷰본 17–18, 40행). predicateExpression도 this를 거부하지 않는다.
- withThis의 a가 arg1이 되어 second와 Equivalent다. 실제 동일 인자 `('a','b')`에서는 true/false다.
- first와는 실제 동치인데 Different와 가짜 반례를 낸다.
- TypeScript의 this 타입 매개변수는 emit 시 제거된다. 함수·메서드의 표시/분석에서 런타임 인자 순서와 구분해야 한다.

독립 재현:

```sh
pnpm build
node docs/reviews/evidence/2026-11-04-independent-check.mjs
```

스크립트는 결함의 관찰값을 출력하며 exit 0도 가능하다. 회귀 테스트의 대체물이 아니다. 당시 JSON은 같은 폴더의 `2026-11-04-independent-results.json`, 검토본 SHA-256은 `2026-11-04-source-fingerprints.json`에 있다.

### 구현 범위

1. 두 최소 재현을 기존 테스트 체계에서 먼저 실패하는 테스트로 추가한다. 실제 TS Program의 진단이 0인지 확인해 컴파일 오류로 일괄 거부돼 테스트가 우연히 통과하지 않게 한다.
2. enum 상수로 인정할 표현식/receiver의 허용 경계를 명확하게 한다. optional chain, 함수 호출, 타입 단언 등 미지원 평가가 상수 추출 경로를 통해 성공하지 않게 한다. 관련 receiver 중첩 사례도 검사한다. 직접 enum 멤버와 이미 지원 중인 문자열/숫자 enum의 정상 비교를 유지한다.
3. explicit this를 런타임 인자 인덱스에서 분리하거나 해당 함수/조건을 Unsupported로 거부한다. 더 작고 신뢰할 수 있는 방법을 선택하되 JSON의 argN과 CLI 설명이 일치해야 한다. 런타임 this 본문 해석을 새로 도입할 필요는 없다.
4. 지원됐다고 내보내는 표현식의 IR 평가를 실제 실행 결과와 대조하는 테스트를 추가한다. enum constant와 direct input이 만나거나, 미지원 문법이 지원 문법 아래 감춰지는 조합을 포함한다. 임의 프로젝트 코드를 실행하는 제품 기능을 만들지 말고 통제된 테스트 fixture만 실행한다.
5. core와 CLI 두 경로를 확인한다. Unsupported를 택하면 이유·종료 코드 2·평가 0회가 일관돼야 한다. 개별 condition과 전체 predicate의 허용 정책도 확인한다.

### 제외 범위

FCA 알고리즘 교체/랭킹, SMT, LLM, React/Next 플러그인, UI, 승인 워크플로, 의미 자동 확정, optional 문법/호출의 일반적 지원, 광범위한 리팩터링, npm 배포는 제외한다. R3(mixed JS files 집계)는 corpus 측정 전 별도 작은 작업으로 남긴다. 현재 목적은 false proof 차단이다.

### 완료 조건

- optionalEnum 및 callEnum 같은 미지원 receiver 사례는 Unsupported이며 `Equivalent` 등 확정 결과를 반환하지 않는다. TypeScript 진단은 0개다.
- withThis/second는 잘못된 Equivalent를 반환하지 않는다. this를 지원하면 실제 런타임 arg0/arg1 대응으로 Different 및 실행 가능한 반례가 나온다. 보수적으로 거부하면 명시적 Unsupported가 나온다.
- withThis/first는 가짜 Different를 반환하지 않는다. 지원 시 Equivalent, 거부 시 Unsupported다.
- 이 입력 전제는 실제 런타임 위치를 뜻하며 사용자가 입력을 잘못 대응시킨 것이라는 추가 전제로 결함을 회피하지 않는다.
- 기존 직접 enum 비교, 문자열 union, 부정/중첩, 동일 입력 전제, domain mismatch, 4,096조합 경계, 컴파일 오류 거부 테스트가 유지된다.
- 정상 사례의 IR/실행 대조와 확정 판정의 반례 재실행이 통과한다. 테스트의 기대 결과를 현재 IR에서 다시 계산해 정답으로 삼지 않는다.
- CLI의 JSON/종료 코드와 API 상태가 일치한다. 기존 `pnpm check`와 `pnpm experiment`가 통과한다.

### 검증 방법

실패 재현 → 최소 수정 → targeted regression → `pnpm check` → `pnpm experiment` 순으로 진행한다. 정상 사례와 거부 사례를 분리하고, 잘못된 Equivalent뿐 아니라 잘못된 Different도 검사한다. 테스트 개수보다 다음 세 가지를 보고한다.

1. 실제 TypeScript 실행과 IR 의미의 일치 또는 명시적 거부.
2. 지원 밖 표현식을 성공으로 해석하는 우회 경로가 제거됐는지.
3. 기존 지원 범위·출력 전제·입력 상한이 유지됐는지.

독립 리뷰 스크립트를 재실행하고 수정 전/후 상태를 비교해도 된다. 기존 리뷰의 날짜별 원시 JSON은 과거 증거로 보존하고 새 결과는 별도 이름으로 기록한다. 모든 문법에 대한 보편적 건전성을 증명했다고 주장하지 않는다.

### 문서화 및 인계

PROGRESS에 실제 검사 결과, 지원/거부 선택, 남은 제한을 기록한다. ARCHITECTURE/README의 지원 경계를 구현과 맞춘다. enum receiver/this 계약처럼 중요한 선택은 DECISIONS에 이유와 트레이드오프를 기록한다. ROADMAP에는 정확성 수정이 corpus 실험보다 먼저였다는 근거와 후속 실험 순서를 남긴다. RESEARCH에서는 “정상 사례의 계산 검증”과 “지원 판정 경계의 수정”을 구분한다.

리뷰 문서의 과거 관찰을 수정 완료 상태로 덮어쓰지 않는다. 개발 인계에는 변경 파일, 재현별 전후 상태, 실행한 검사, 남은 위험, R3 처리 여부(이번에는 후속), 다음 리뷰가 확인할 근거를 적는다. 커밋/배포는 별도 기존 사용자 지침을 따른다.

---

## 이 작업 이후의 판단 기준

- R1/R2가 재현되면 Gate 1은 계속 미통과다. 다음 기능으로 넘어가지 않는다.
- 수정된 지원 범위에서 독립 검증이 통과하면 Gate 1을 그 범위에 한해 재평가한다. 이것만으로 Gate 2~4를 올리지 않는다.
- 이후 R3 계약 정리 → 실제 작은 corpus 2개/수동 라벨 20~30개 → 검색/LSP·단순 속성 그룹과 FCA/논리의 순증분 비교를 권장한다.
- FCA가 단순 그룹보다 검토 시간을 줄이지 못하거나 잘못된 의미 해석을 늘리면 기본 노출을 축소한다. 반례 비교가 더 큰 효용이면 첫 제품 범위를 그 과업으로 좁힌다.
