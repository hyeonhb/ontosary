# 숫자 enum 반례와 컴파일러 선택 실패 재검산

**4.9.4와 5.9.3 모두 숫자 enum 입력을 선언된 멤버만으로 열거할 수 없다.** 리뷰의 두 함수는 두 컴파일러에서 진단 없이 컴파일되며, 같은 입력 99에서 각각 false와 true를 반환했다. 보완 후에는 기본 CLI와 명시적 5.9.3, 명시적 4.9.4가 모두 Unsupported와 종료 코드 2를 반환한다. [독립 리뷰](2026-11-28-typescript-494-independent-review.md) · [실행한 반례와 분기](../../tests/fixtures/open-numeric-enum/input.ts)

## 반례에서 달라진 판정

Stage의 선언값은 Pending(0), Confirmed(1)다. 5.9.3은 리터럴 99를 직접 대입하면 거부하지만, 타입이 number인 변수에서 Stage로 대입하는 코드는 허용한다. `s === Stage.Pending`과 `s !== Stage.Confirmed`는 0과 1에서만 일치한다. 기존 판정이 놓친 입력은 타입 단언이나 any 없이 전달됐다.

| CLI 설정 | PR 기존 head 4d33591 · 상태 / 열거 횟수 / 종료 | 보완 후 · 상태 / 열거 횟수 / 종료 |
| --- | --- | --- |
| 4.9.4 명시 | Unsupported / 0 / 2 | Unsupported / 0 / 2 |
| 5.9.3 명시 | Equivalent / 2 / 0 | Unsupported / 0 / 2 |
| 기본 5.9.3 | Equivalent / 2 / 0 | Unsupported / 0 / 2 |

함수 predicate와 if 조건에 같은 입력 도메인 검사를 적용했다. 기존 숫자 enum 정상 대조도 멤버 목록에 한정한 동치 기대를 철회했다. 문자열 리터럴 기반 check 대조는 두 버전에서 3개 입력 중 reserved를 동치의 반례로 찾았고, 문자열 enum 비교는 두 버전에서 모두 2개 입력에 대해 Equivalent였다. 기존 소형 정상 사본의 FCA 후보는 각각 5개였다. 실제 타입 오류를 넣은 사본은 두 버전 모두 b.ts 3행 14열에서 TS2322를 보고하고 concepts·compare를 중단했다. [정규화 구현](../../src/core/logic.ts) · [두 컴파일러와 공개 CLI 회귀 검사](../../tests/compiler-version.test.ts)

## 기본 패키지가 없는 설치

CLI가 요청 버전을 정한 뒤 오류 처리 범위 안에서 해당 패키지를 로드한다. 빌드 결과와 4.9.4 패키지만 둔 임시 설치에서 5.9.3 명시·버전 생략을 각각 검산했다. 둘 다 종료 1, stdout 0바이트, stderr는 오류 JSON 하나이며 `compiler.requested`는 5.9.3, `compiler.used`는 null이었다. 정상 설치의 기본 scan JSON은 명시적 5.9.3에서 버전 메타데이터를 뺀 출력과 바이트 단위로 일치했다. 공개 코어의 scan(projectPath)는 계속 기본 컴파일러를 사용한다. [CLI 진입점](../../src/cli/index.ts) · [사용법](../../README.md)

## 고정 프로젝트와 저장소 검사

기존 의존성이 설치된 같은 Excalidraw 사본 `3bdaafe4b5ecde577fe9b5c69a5d1819e37c4ccb`에 공개 CLI scan을 다시 실행했다. 동결된 소스·설정·lockfile 해시, 두 선언의 파일·시작·끝 좌표와 5.9.3의 진단 원문을 기존 검산기로 대조했다. [자료 준비와 전체 명령](2026-11-28-typescript-494-compatibility.md#재현) · [동결 자료 검산기](../../experiments/compiler-compatibility/verify-scans.mjs)

| 실제 사용 버전 | scan 종료 / 진단 | 파일 / 함수 | eraserTest | intersectElementWithLineSegment |
| --- | --- | --- | --- | --- |
| 4.9.4 | 0 / 0 | 370 / 4,475 | 179행 20열 | 204행 48열 |
| 5.9.3 | 1 / 7 | 370 / 4,475 | 179행 20열 | 204행 48열 |

저장소 루트에서 다음 명령으로 반례를 다시 확인할 수 있다. 첫 테스트 명령은 각 버전의 tsc로 검증용 반례만 컴파일·실행해 실제 반환값을 대조한 뒤 공개 CLI를 검사한다. 스캔 대상 프로젝트의 코드는 분석 중에 실행하지 않는다.

```sh
pnpm build
pnpm exec vitest run tests/compiler-version.test.ts
node dist/cli/index.js compare tests/fixtures/open-numeric-enum isPending notConfirmed --assume-same-input
```

`pnpm check`는 17개 파일에서 308개 통과, 기존 Vendure 캐시 의존 5개 건너뜀, 예제 빌드 성공이었다. 305개에서 늘어난 세 건은 두 컴파일러의 실제 99 반례 각 한 건과 기존 숫자 enum 양성 한 건을 두 함수의 거부 사례로 분리한 결과다. `pnpm experiment`는 기존 비교 4/4였다. 참가 모델 호출은 0회이며 PR #135를 재검토로 인계한다.
