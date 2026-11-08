# Vendure prepared-input observation V1

2026-11-08의 **환경 준비 성공 / 탐색 비교 범위 미확보** 기록이다. [보고서](../../../docs/reviews/2026-11-08-vendure-preparation.md), [고정 준비 manifest](manifest.json), [원시 결과](../results/2026-11-08-prepared/budget-result.json)를 함께 읽는다. 기존 미설치 V1 runner/verifier와 과거 결과는 그대로다.

## 고정 환경과 실행 기록

- Ontosary 기준 main `ed32955e65f801cf3d511f446badf9b5e3b3383d`; Node 22.19.0, npm 10.9.3, pnpm 11.19.0, Darwin arm64. 분석 TypeScript 5.9.3, upstream common 빌드 TypeScript 5.8.2.
- Vendure v3.5.0 revision `534e6003534f74761e82de1b8c6061cba89945d1`. [기존 manifest](../v1/manifest.json)의 archive/hash/설정과 [11개 과업 근거](../v1/vendure-task.json)를 재사용한다. 원본 inventory·라이선스는 [기존 결과](../results/2026-11-08/vendure)에 보존되어 있다.
- 시작 14:37:37 KST, 마감 15:07:37 KST, 종료 14:43:37 KST. 총 359.668초. `command.py`는 manifest의 단일 마감까지 남은 시간으로 명령과 하위 프로세스를 제한한다. 종료 기록이 있으므로 현재 실행은 재개할 수 없다.
- `02-install`은 user/global npm config를 모두 `/dev/null`로 지정한 harness 오류로 124ms 만에 종료됐다. 서로 다른 빈 파일로 고친 `03-install`은 동일 마감 안에서 성공했다. 현재 helper는 수정된 버전이며 최초 실패 로그도 보존한다.
- 게시 로그는 호스트 경로를 치환했으며 common build 로그의 끝 빈 줄 하나를 제거했다. 종료 코드와 명령 출력 내용은 유지했다.
- [명령별 JSON/log](../results/2026-11-08-prepared)는 argv, cwd, 시작/종료, wall time, 종료 코드/signal을 기록한다. `.log`만 설치 명령의 옵션 효과를 완전히 설명하지 않으므로 JSON도 확인한다. `10-effective-npm-config`의 기본 `ignore-scripts=false`는 설치 때 명시한 `--ignore-scripts`를 취소하지 않는다.

## 재실행 방법과 경계

아래는 실제 실행의 명령/입력 레시피다. **현재 세션의 예산을 다시 시작하는 명령이 아니다.** 새 설치 재현은 별도 실행으로 시작/마감·새 cache/output을 먼저 기록하고 하나의 30분 마감을 모든 명령에 적용해야 한다. 원래 cache/output과 manifest를 덮어쓰지 않는다. 이 세션에서는 설치·빌드를 한 번만 수행했으며 독립 설치 재현을 주장하지 않는다.

Ontosary 의존성은 `pnpm install --frozen-lockfile`, `pnpm build`로 준비한다. archive는 다음 방식으로 가져왔고, 설치는 두 workspace와 root 도구만 요청했다(전체 workspace install 아님).

```sh
node experiments/public-app/v1/prepare.mjs <fresh-cache> vendure
# <fresh-cache>/vendure 에서, public registry / 서로 다른 빈 user·global npmrc / 격리 npm cache 사용
npm ci --ignore-scripts --no-audit --no-fund --workspace=@vendure/admin-ui --workspace=@vendure/common --include-workspace-root
npm run build --workspace=@vendure/common
```

`<fresh-cache>`는 실제 새 절대 경로로 바꾸는 표기다. `command.py`가 이번 실행에서 사용한 npm 환경 설정과 시간 제한의 원본이다. 설치 전후 전체 원문 inventory의 파일 hash/심볼릭 링크와 task anchors를 대조해야 한다. `audit.py`는 이번 manifest의 cache를 대상으로 기존 원문/의존성/common 산출물 경계를 확인하는 전용 기록기다. 다른 cache의 독립 실행에서는 별도 manifest/출력과 함께 경로를 명시해야 하며 이 역사적 manifest를 수정하지 않는다.

과업 설정은 `../v1/manifest.json`의 Vendure `scopedConfig`를 **변경 없이** `packages/admin-ui/ontosary.scope.json`에 직렬화한다. 기존 원본 파일이 아니며 strict/paths를 원래 tsconfig에서 상속한다. 분석 전에 아래 두 출력 디렉터리를 새로 만든다. `<app-root>`는 준비한 cache의 `vendure` 디렉터리다.

```sh
node --max-old-space-size=4096 experiments/public-app/prepared-v1/observe.mjs <app-root> packages/admin-ui/tsconfig.json <new-output>/original
node --max-old-space-size=4096 experiments/public-app/prepared-v1/observe.mjs <app-root> packages/admin-ui/ontosary.scope.json <new-output>/scoped
# 같은 cache/절대 경로에서 다른 출력으로 같은 두 명령을 반복한 뒤:
node experiments/public-app/prepared-v1/verify.mjs <new-output> <repeat-output>
```

`observe.mjs`는 원본 TS 분석기와 buildContext만 사용한다. 오류가 있으면 context를 만들지 않고, 오류가 없어도 크기/기본 한도를 기록한 뒤 FCA를 열거하지 않는다. 그룹과 개념 후보는 미실행이다. 함수 2,264개/속성 4,288개에서 중단하며 성공한 함수만 고르지 않는다. 원래 설정은 495개 test 이름 오류가 남는다.

실제 동일 cache의 최초/반복 결과 9개는 byte 일치했다. 보관된 [reproduction.json](../results/2026-11-08-prepared/reproduction.json)은 파일별 hash를 포함한다. 캐시 경로 길이에 따른 TypeChecker 타입 표시 문자열 차이는 기존 제한이다. 다른 경로/설치/운영체제의 byte 일치는 검증하지 않았다.

## 기록의 해석

- `program.json.gz`: 실제 Program 파일/hash와 구현 파일의 literal import 해석이다. 외부 선언 파일의 모든 import edge를 수집한 전체 의존 그래프는 아니다.
- 이번 macOS `/tmp` → `/private/tmp` realpath 차이로 원래 기록기의 의존성 경로가 `<external>/basename`으로 축약됐다. 원시 결과를 보존하고 **보고 단계**의 `program-path-audit.mjs`로 Program 파일 순서/hash 전체 일치와 실제 경계를 확인했다. [보충 기록](../results/2026-11-08-prepared/program-path-audit.json.gz)은 원본/과업 각각 1,715/1,265개 경로를 복원한다. 모든 파일은 격리 앱 cache 또는 의도한 분석기 TS 표준 lib 안에 있다. 이 검증은 scan/context/설치/build를 재실행하지 않는다.
- `input-audit/`: 전체 설치 파일 hash/용량, 실제 설치된 패키지 버전·lock integrity·package JSON hash·license 선언/파일 hash, 새 common 출력과 링크를 분리한다. 라이선스 법률 검토 완료를 뜻하지 않으며 설치 바이너리/common lib는 저장소에 배포하지 않는다.
- Vendure 원문/scan의 소스 조각은 기존 [라이선스 고지](../results/2026-11-08/vendure/source-notice.json)를 유지한다. GPL-3.0-or-later 원문을 Ontosary Apache-2.0으로 재라이선스하지 않는다. 기존 generated source는 수정하지 않았고 새 codegen도 실행하지 않았다.
- install lifecycle은 생략하고 common의 `rimraf lib && tsc -p ./tsconfig.build.json`만 명시 실행했다. 전체 Angular build, native runtime, 서비스/DB/브라우저 앱은 검증하지 않았다.
- HTML 근거 두 개는 계속 수동 원문이다. 사람 준비/탐색 시간·업무 의미 승인·Gate 2~4는 미검증이다.
