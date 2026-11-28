# TypeScript 4.9.4 호환성 독립 리뷰와 보완 지시

**정확히 4.9.4를 명시 선택하는 분석 경로는 검산을 통과했다.** 다만 [PR #135](https://github.com/hyeonhb/ontosary/pull/135)의 새 회귀 검사는 5.9.3의 숫자 enum 입력을 일반적으로 유한 판정할 수 있다고 고정한다. 정상 컴파일되는 반례에서 잘못된 동치가 나와 병합을 보류한다. [검토한 구현 및 원래 검증 결과](https://github.com/hyeonhb/ontosary/blob/4d33591474c3623841188a9138919975b5134eb9/docs/reviews/2026-11-28-typescript-494-compatibility.md)

PR head `4d33591`을 별도 체크아웃에서 빌드했다. 고정 Excalidraw 사본에 공개 CLI 두 버전을 명시해 scan을 다시 실행하고 동결 자료와 대조했다. 두 버전 모두 파일 370개·함수 4,475개였고 두 심볼의 파일과 시작·끝 위치가 일치했다. 컴파일 진단과 종료 코드는 4.9.4에서 0개·0, 5.9.3에서 7개·1이었다. 회귀 테스트에서 작은 정상 입력의 별칭 연결, 조건 비교 반례 `reserved`, 실제 TS2322 이후 파생 분석 중단, 4.9.4 로드 실패 처리를 확인했다. `pnpm check`는 305개 통과·기존 캐시 의존 5개 건너뜀, `pnpm experiment`는 4/4였다.

## 병합 전 보완 · 숫자 enum의 입력 범위

아래 사본은 `strict: true`에서 두 버전의 `tsc`를 진단 없이 통과한다. 타입 단언이나 `any`를 사용하지 않는다.

```ts
enum Stage { Pending, Confirmed }
export const isPending = (s: Stage) => s === Stage.Pending;
export const notConfirmed = (s: Stage) => s !== Stage.Confirmed;
const fromNumber: number = 99;
const value: Stage = fromNumber;
export const results = [isPending(value), notConfirmed(value)];
```

실제 실행 결과는 `[false, true]`다. 같은 사본에 `compare ... isPending notConfirmed --assume-same-input`을 실행하면 4.9.4는 종료 2·Unsupported·평가 0회다. 명시적 5.9.3과 기본 CLI는 모두 종료 0·Equivalent·평가 2회다. PR 기준 커밋 `4dabcf0`의 CLI에서도 같은 오판이 있었다. 5.9.3이 리터럴 99의 직접 대입을 거부한다는 관측은 유효하지만, 일반 `number`를 거친 값까지 제한하지는 않는다. 이번에 추가된 버전별 분기와 회귀 단언이 그 기존 오판을 지원 계약으로 고정한다. [유한 도메인 구성](https://github.com/hyeonhb/ontosary/blob/4d33591/src/core/logic.ts#L37-L45) · [버전별 지원 단언](https://github.com/hyeonhb/ontosary/blob/4d33591/tests/compiler-version.test.ts#L44-L50)

## 오류 보고 범위 · 기본 컴파일러 누락

별도 설치 사본에 빌드 결과와 4.9.4 의존성만 두고 5.9.3을 명시적으로 요청했다. 종료 1, stdout 0바이트였으나 stderr는 Node의 `ERR_MODULE_NOT_FOUND` 스택이었다. 기본 컴파일러의 정적 import가 오류 JSON을 만드는 코드보다 먼저 실행되기 때문이다. 정상 설치에는 영향을 주지 않는다. 현재 README의 선택 실패 시 `used: null` 보장은 이 설치 상태까지 포괄한다. [컴파일러 선택 코드](https://github.com/hyeonhb/ontosary/blob/4d33591/src/cli/compiler.ts#L1-L17) · [README 설명](https://github.com/hyeonhb/ontosary/blob/4d33591/README.md#L25)

## 개발 세션에 전달할 보완 지시

1. PR #135에서 숫자 enum의 선언 멤버만 열거해 동치를 확정하는 경로를 바로잡아 주세요. 현재 계약에서 입력 범위를 닫을 수 없는 경우 두 버전 모두 보수적으로 처리하는 것이 가장 작은 수정입니다. 위 반례를 실제 컴파일러와 공개 CLI로 검증하고, 함수 predicate와 분기 조건에 같은 기준을 적용해 주세요. 버전 생략·명시적 5.9.3에서 결과가 일치해야 합니다. 기존 문자열 리터럴·문자열 enum 정상 대조와 실제 오류 대조도 유지해 주세요. 이 정확성 수정으로 달라지는 기존 숫자 enum 테스트와 지원 설명을 함께 갱신하세요.
2. 선택 실패의 JSON 보장 범위를 구현과 README에서 일치시켜 주세요. 기본 패키지 누락도 계약에 포함할 경우 해당 설치 사본에서 검증하고, 정상 설치 이후의 선택 오류만 보장한다면 그 전제를 명시해 주세요. 정상 설치의 기본 명령은 계속 기존 경로로 사용할 수 있어야 합니다.
3. 동일 Excalidraw 사본 대조와 `pnpm check`, `pnpm experiment` 결과를 보완 보고서에 남겨 주세요. 수치가 달라지는 기존 기대값은 변경 이유를 설명해 주세요. 이 두 사항을 재검토한 뒤 병합과 후속 단계로 넘어갑니다.
