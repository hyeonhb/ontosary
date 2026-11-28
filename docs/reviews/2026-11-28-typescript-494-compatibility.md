# Excalidraw로 검산한 TypeScript 4.9.4 분석 호환성

**정확히 4.9.4를 명시해 분석하는 CLI 경로를 추가 지원하도록 권고한다.** 같은 Excalidraw 사본을 4.9.4와 5.9.3으로 읽었을 때 분석 파일 수·함수 수와 두 선언의 소스 위치는 일치했고, 진단은 각각 0개와 7개였다. 작은 사본에서 실제 타입 오류 하나를 넣자 두 버전 모두 그 위치를 보고하고 후보 생성과 조건 비교를 중단했다. 검증 범위는 두 고정 버전과 아래 입력이다. [개발 지시](2026-11-27-typescript-494-compatibility-instructions.md) · [원래 독립 검산](2026-11-27-excalidraw-eraser-independent-review.md)

## 어떤 컴파일러가 무엇을 읽었는가

Excalidraw 자료 시점은 `3bdaafe4b5ecde577fe9b5c69a5d1819e37c4ccb`다. Yarn lockfile의 SHA-256은 `033a69ccfaea9b182a18502b98899d361587e7cf8b100b6395cf1c5a24d286f6`이고 설치된 프로젝트 컴파일러는 4.9.4였다. 실행 후 추적 파일 1,145개의 Git blob을 고정 트리와 대조했다. 분석에 쓰인 Ontosary의 4.9.4와 대상에 설치된 4.9.4의 `lib/typescript.js` SHA-256도 일치했다. [대상의 버전 선언](https://github.com/excalidraw/excalidraw/blob/3bdaafe4b5ecde577fe9b5c69a5d1819e37c4ccb/package.json#L37) · [Ontosary의 잠긴 의존성](../../pnpm-lock.yaml)

대상 버전은 사용자가 프로젝트에서 확인한다. CLI는 `--typescript-version`으로 요청받은 패키지를 Ontosary의 의존성에서 로드하고 실제 버전을 확인한다. 설정 해석부터 Program·타입 검사기 생성, SyntaxKind·타입 플래그·심볼 참조·조건 정규화까지 그 객체를 전달한다. 비교와 FCA는 추출된 사실을 소비한다. 두 컴파일러 패키지의 라이선스는 Apache-2.0이다. [선택 코드](../../src/cli/compiler.ts) · [분석기](../../src/core/analyzer.ts) · [조건 정규화](../../src/core/logic.ts)

| 동일 사본의 관측값 | 선택 4.9.4 | 선택 5.9.3 |
| --- | ---: | ---: |
| 대상에 설치된 버전 | 4.9.4 | 4.9.4 |
| CLI가 보고한 실제 사용 버전 | 4.9.4 | 5.9.3 |
| 독립 tsc 종료 / 오류 | 0 / 0 | 2 / 7 |
| 공개 CLI scan 종료 / 오류 | 0 / 0 | 1 / 7 |
| 구현 파일 / 함수 / 타입 | 370 / 4,475 / 455 | 370 / 4,475 / 455 |
| eraserTest (행, 열) | 179, 20 | 179, 20 |
| intersectElementWithLineSegment (행, 열) | 204, 48 | 204, 48 |

위 좌표는 각각 변수에 대입한 화살표 함수 식이 시작하는 여는 괄호다. 검산기는 각 심볼이 한 번 나오고 파일·이름·시작과 끝 좌표가 과거 기록과 같은지, 실제 파일에서 그 시작점 앞에 해당 변수 선언이 있는지 확인한다. 5.9.3의 오류 일곱 개는 이전 자료와 코드·위치·메시지가 모두 일치했다. [지우개 소스](https://github.com/excalidraw/excalidraw/blob/3bdaafe4b5ecde577fe9b5c69a5d1819e37c4ccb/packages/excalidraw/eraser/index.ts#L179) · [선분 충돌 소스](https://github.com/excalidraw/excalidraw/blob/3bdaafe4b5ecde577fe9b5c69a5d1819e37c4ccb/packages/element/src/collision.ts#L204) · [동결된 위치](../../experiments/first-use/excalidraw-eraser/source-check.json) · [기존 오류 7건](../../experiments/first-use/excalidraw-eraser/installed-cli.json)

## 실제 오류, 타입 기반 판단, 기존 사용자 대조

| 검산 입력 | 결과 |
| --- | --- |
| 같은 이름의 check 함수와 Item 타입이 있는 a.ts·b.ts, a.ts를 별칭으로 가져오는 cases.ts | 두 버전 모두 별칭은 a.ts의 선언 ID를 가리키고 두 함수의 status 속성은 각자 파일의 선언을 가리켰다. 두 check를 전체 ID로 비교하면 입력 3개에서 왼쪽이 오른쪽을 함의하며 동치의 반례는 reserved다. 작은 정상 사본의 concepts는 두 버전 각각 후보 5개였다. |
| 정상 사본 b.ts에 `export const invalid: string = 7;` 한 줄 추가 | 두 버전 모두 scan 종료 1, 오류 하나 TS2322, b.ts 3행 14열. 함수 조건은 unsupported였다. concepts·compare 각각 종료 1, stdout 0바이트였고 stderr에는 컴파일 오류와 실제 선택 버전이 있었다. |
| 숫자 enum의 선언 밖 정수 | 멤버값이 0·1·2인 Stage에 99를 직접 대입하면 4.9.4는 진단 0, 5.9.3은 TS2322였다. 4.9.4에서는 숫자 enum 변수를 선언 멤버로만 열거해 결론 내릴 수 없어 해당 정규화를 Unsupported로 둔다. |
| 4.9.5 선택, 4.9.4 패키지 누락, 잘못 설치된 5.9.3을 4.9.4로 요청 | 세 경우 모두 종료 1, stdout 0바이트. 오류 JSON에는 요청 버전 및 used=null이 남는다. |
| 옵션을 생략한 기본 CLI와 기준 커밋 4dabcf0 | 같은 React 예제의 scan·concepts·compare 성공(0), 전제 없는 compare(2), 없는 프로젝트 scan(1)의 stdout·stderr를 기준 커밋의 빌드와 바이트 단위로 대조해 모두 일치했다. 기존 코어 scan(projectPath)도 5.9.3을 쓴다. |

소형 대조는 기존 a.ts·b.ts·cases.ts를 복사하고 4.9.4가 지원하는 Node 모듈 해석으로 설정했다. 정상 사본의 선언 출력 전용 옵션은 켰다. 세 소스와 설정 외에 출력 파일이 생성되지 않았음을 검사했다. [실행 가능한 CLI 회귀 테스트](../../tests/compiler-version.test.ts) · [소형 입력 원본](../../tests/fixtures)

## 재현

Ontosary 저장소 루트에서 실행한다. Node 22.19.0, pnpm 11.19.0, Excalidraw 설치에는 Yarn 1.22.22를 사용했다. 아래 두 디렉터리는 실행마다 새로 만든다.

```sh
pnpm install --frozen-lockfile
pnpm build
project_dir=$(mktemp -d)
results_dir=$(mktemp -d)
rev=3bdaafe4b5ecde577fe9b5c69a5d1819e37c4ccb
curl -fsSL "https://codeload.github.com/excalidraw/excalidraw/tar.gz/$rev" |
  tar -xz --strip-components=1 -C "$project_dir"
(cd "$project_dir" && git init -q && npx --yes --package=yarn@1.22.22 -c 'yarn install --frozen-lockfile --non-interactive')
config="$project_dir/packages/excalidraw/tsconfig.json"
node "$project_dir/node_modules/typescript/bin/tsc" --version
node "$project_dir/node_modules/typescript/bin/tsc" -p "$config" --emitDeclarationOnly false --noEmit --pretty false
node node_modules/typescript/bin/tsc -p "$config" --emitDeclarationOnly false --noEmit --pretty false || test "$?" -eq 2
node dist/cli/index.js scan "$config" --typescript-version 4.9.4 > "$results_dir/scan-4.9.4.json"
node dist/cli/index.js scan "$config" --typescript-version 5.9.3 > "$results_dir/scan-5.9.3.json" || test "$?" -eq 1
node experiments/compiler-compatibility/verify-scans.mjs "$project_dir" "$results_dir"
pnpm exec vitest run tests/compiler-version.test.ts
```

외부 tsc 대조는 프로젝트의 선언 전용 출력을 끄고 noEmit을 켠다. 공개 CLI는 프로그램에 대해 emit을 호출하지 않는다. 특히 4.9.4는 noEmit과 emitDeclarationOnly를 함께 지정하면 옵션 충돌을 보고하므로, 선언 전용 프로젝트에서는 원래 선언 설정으로 진단을 수집한다. 이 검산에서 전체 패키지 FCA는 실행하지 않았다. `pnpm check`는 17개 파일, 305개 테스트 통과·기존 Vendure 캐시 의존 5개 건너뜀, 예제 빌드 성공이었다. `pnpm experiment`는 기존 비교 4/4를 재현했다. 참가 모델 호출은 0회다.
