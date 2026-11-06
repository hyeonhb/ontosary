# R1/R2 개발 수정 인계 — 2026-11-06

구현 담당 세션의 보고이며 새 독립 리뷰 판정은 아니다. 기준은 [2026-11-04 리뷰](2026-11-04-poc-review.md)와 [NEXT_PLAN](NEXT_PLAN.md)이다. 이 과거 문서와 날짜별 원시 증거는 변경하지 않았다.

## 변경 기반

- 원격 초기 커밋 `5d33ab6` 위에 기존 PoC·리뷰·기여 규칙을 `a054f4f`로 보존했다(`chore/initial-poc`).
- 수정 브랜치 `fix/normalization-soundness`는 이 미병합 초기 작업에 의존한다.
- 수정 대상은 소스→논리 IR의 지원 판정 경계다. FCA·SMT·LLM·UI·R3는 변경하지 않았다.

## 재현별 전후 상태

모든 재현 프로젝트의 TypeScript 진단은 0개다.

| 비교 | 수정 전 확정 판정 | 실제 실행 | 수정 후 |
| --- | --- | --- | --- |
| optionalEnum / always | Equivalent, CLI 0 | undefined에서 false / true | Unsupported, CLI 2, 평가 0 |
| callEnum / always | Equivalent | 호출이 예외를 던짐 / true | Unsupported, CLI 2, 평가 0 |
| withThis / second | Equivalent, CLI 0 | ('a','b')에서 true / false | Unsupported, CLI 2, 평가 0 |
| withThis / first | Different + 가짜 반례 | 4개 유한 입력에서 실제 동치 | Unsupported, CLI 2, 평가 0 |

`sameInput`의 뜻을 바꾸어 회피하지 않았다. `argN`은 런타임 인자 위치다. explicit this는 타입 전용 매개변수이므로 현재는 함수/메서드와 그 개별 조건 모두를 거부한다. 소스의 parameters 정보에는 this를 그대로 기록한다.

## 허용 경계

enum은 receiver가 실제 enum 선언에 해소되는 직접 식별자인 경우만 상수로 추출한다. `E.A`, `(E).A`, named import alias는 지원한다. enum 객체 타입의 매개변수, 변수 별칭, shadowing, optional chain, 호출, 타입 단언, non-null assertion, getter, 중첩·namespace receiver는 거부한다. 조건의 `&&`·`!` 아래 또는 항상 false인 가지에 숨겨진 경우에도 미지원 평가를 지우지 않는다.

namespace·실제로 안전한 객체 별칭도 보수적으로 제외된다. enum 선언의 상수값이 런타임에도 유지된다는 기존 타입/값 전제는 필요하다. 일반적인 control-flow·side effect·runtime this 분석을 구현하지 않았다.

## 코드와 검증

- `src/core/logic.ts`: normalize 진입부의 explicit-this 거부와 literal 추출 전 receiver identity 확인.
- `src/cli/index.ts`: argN/this 지원 경계 도움말.
- `tests/fixtures/soundness`: 진단 없는 재현·정상·한도 fixture.
- `tests/normalization-soundness.test.ts`: core/condition/CLI 일치, 실제 실행 대조, 반례 재실행.
- README, ARCHITECTURE, DECISIONS, RESEARCH, ROADMAP, PROGRESS: 계약·근거·남은 작업.

실행 순서와 결과:

1. 수정 전 새 테스트 34개: **29 실패 / 5 통과**. [원시 red 로그](evidence/2026-11-06-normalization-red.txt). 실패 원인은 diagnostics가 아니라 잘못된 supported/확정 판정 및 CLI 0이었다.
2. 최소 소스 수정 후 기본 4,096 한도 테스트를 추가: targeted **35개 통과**.
3. `pnpm check`: 타입 검사, **4개 파일/76개 테스트 통과**, Vite production build 성공.
4. `pnpm experiment`: 기존 4개 기대 비교 통과. 생성 JSON은 초기 스냅샷과 동일했다.
5. 기존 독립 probe 재실행: [새 날짜의 원시 결과](evidence/2026-11-06-independent-results.json). 144회 실행/IR 대조, 256개 순서쌍, 방향별 반례 336개 재실행, 4×3 FCA 관계 4,096개 대조 및 열거 경계 검증 통과. R1/R2 관찰값은 모두 Unsupported로 바뀌었다.
6. probe 종료 0만 믿지 않고 새 JSON의 diagnostics 0, 두 CLI exit 2, 네 비교 status Unsupported와 평가 0을 별도 assert로 확인했다. 영구 회귀 테스트도 같은 조건을 검사한다.

새 회귀 테스트는 9개 정상 함수의 81개 순서쌍을 **실제 함수 진리표**로 판정하고, 반환된 반례를 해당 함수에 다시 입력한다. 현재 IR을 다시 계산해서 정답으로 사용하지 않는다. 테스트 fixture만 실행하며 제품 분석기에는 임의 코드 실행 기능을 추가하지 않았다.

재현:

```sh
pnpm build
pnpm exec vitest run tests/normalization-soundness.test.ts
pnpm check
pnpm experiment
node docs/reviews/evidence/2026-11-04-independent-check.mjs
```

probe는 여전히 관찰 스크립트다. 종료 0을 일반적인 건전성 증명이나 Gate 1 통과로 읽지 않는다.

## 남은 위험과 다음 리뷰

이번 범위의 R1/R2 우회 경로와 기존 정상 사례를 확인했다. 모든 TS 문법에 대한 보편적 건전성을 주장하지 않는다. 독립 검토자는 receiver 허용 경계, named import 해소, predicate/condition 정책 일치, explicit this의 소스/런타임 구분, 실행 반례를 다시 확인해야 한다. Gate 1은 이 좁아진 지원 범위에 한해 재평가할 수 있고 Gate 2~4는 미검증이다.

**R3는 미수정**이다. 새 probe도 `files`에 ignored.js가 있지만 함수는 tsFunction만 있는 관찰을 보존한다. 다음 구현은 mixed TS/JS 파일 집계 계약과 회귀 테스트이며, 그 뒤 corpus 2개/수동 라벨 20~30개 및 검색·LSP/단순 속성 그룹 대비 순증분 평가를 진행한다.
