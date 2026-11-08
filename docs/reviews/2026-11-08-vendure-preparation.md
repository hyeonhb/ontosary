# Vendure 환경 준비 후속 — 2026-11-08

**환경 준비 성공 / 탐색 비교 범위 미확보로 중단했다.** 고정 의존성 설치와 common 빌드 후 기존 4진입 과업 설정의 진단이 1,058개에서 0개가 됐다. 전체 context는 2,264객체 × 4,288속성이어서 기본 상한 128/64를 모두 넘었다. 함수 선택이나 상한 변경 없이 종료했다. [개발 지시](2026-11-08-vendure-preparation-next-plan.md)의 근거 있는 중단 조건을 충족한 구현 세션의 인계이며, 독립 리뷰나 사람 효용 승인 결과가 아니다.

## 입력과 별도 판정

Ontosary 기준은 main `ed32955e65f801cf3d511f446badf9b5e3b3383d`(PR #12), 작업 브랜치는 `codex/vendure-preparation`이다. Vendure v3.5.0 revision `534e6003534f74761e82de1b8c6061cba89945d1`, archive·lock·원문 inventory·11개 과업 근거는 이전 V1 그대로다. [준비 manifest](../../experiments/public-app/prepared-v1/manifest.json), [재실행 명령/환경](../../experiments/public-app/prepared-v1/README.md), [fingerprints](../../experiments/public-app/results/2026-11-08-prepared/provenance.json)를 참조한다.

| 판정 대상 | 관찰 | 결과 |
| --- | --- | --- |
| 고정 의존성 설치 | 선택 workspace 2개 + root 도구, 2,230패키지 | 성공, lifecycle 생략 |
| common 빌드 | upstream TS 5.8.2, 원래 build script | 성공 |
| 원래 Admin UI 설정 | 581구현 파일 / 4,379함수 / 495오류 | 오류 잔존, context 미생성 |
| 기존 4진입 과업 설정 | 327구현 파일 / 2,264함수 / 진단 0 | 오류 없는 분석 입력 확보 |
| 과업 context 적합성 | 2,264객체 / 4,288속성, 기본 128/64 | 부적합, 그룹/FCA 미실행 |
| 동일 설치 cache 반복 관찰 | 원래/과업 출력 총 9파일 byte 일치 | 관찰 재현 확인 |
| 독립 설치·빌드 재현 | 추가 설치/빌드 없음 | 미검증 |

원래 설정의 495오류는 전부 `.spec.ts`의 test 전역 이름이다(TS2304 292개, TS2582 203개). 이름 빈도는 expect 266, it 166, describe 37, beforeEach 18, fail 5, jasmine 2, spyOn 1이다. 이를 upstream 앱 결함으로 판정하지 않으며 테스트 설정/타입/설치 배치를 추가 변경하지 않았다. 원래 Program 2,342파일·타입 1,641개·omissions 751개, 과업 Program 1,638파일·타입 1,577개·omissions 440개다. 과업 구현 소스의 unresolved literal import는 0개다.

과업 진입 파일 자체의 함수 수는 82+14+33+0=129개다. import closure를 제외해도 객체 상한을 넘으며 속성 상한은 별도로 적용된다. 과업 predicate 지원 7개/미지원 2,257개는 함수 전체의 제한된 논리 지원 현황이지 업무 규칙 정확도/효용 점수가 아니다. 단순 그룹·FCA 후보 수·잘림은 미측정이며 0이나 통과로 표시하지 않는다. 원래 설정의 모든 predicate는 오류로 미지원이다.

## 예산과 실제 비용

준비는 **14:37:37.919 KST 시작 → 14:43:37.587 종료, 359.668초(약 6분)**였다. 단일 마감은 15:07:37.919 KST(UTC 06:07:37.919)였고 실패 재시도·사전 환경 점검·스크립트 작성·대기·반복 관찰까지 포함했다. 설치 명령 시간만 30분 예산으로 계산하지 않았다. [종료 기록](../../experiments/public-app/results/2026-11-08-prepared/budget-result.json)이 남아 있어 현재 helper는 재개/예산 재설정을 거부한다.

| 명령 | wall time | 종료 |
| --- | ---: | --- |
| archive 준비 | 5.999초 | 0 |
| 최초 install harness 오류 | 0.124초 | 1 |
| 수정 후 npm ci | 17.499초 | 0 |
| common build | 1.591초 | 0 |
| 원래 / 과업 최초 관찰 | 10.895 / 5.023초 | 각 0 |
| 설치·원문 inventory 감사 | 19.306초 | 0 |
| 원래 / 과업 반복 관찰 | 9.779 / 4.986초 | 각 0 |

이 명령들의 일부는 읽기 전용 병행 실행이므로 합계가 총 wall clock은 아니다. 최초 설치 실패는 npm user/global config가 같은 `/dev/null`을 중복 로드한 **기록 도구 설정 오류**였다. 서로 다른 빈 npmrc로 수정한 뒤 같은 마감 안에서 재시도했으며 upstream 설치 실패로 세지 않는다. 개별 argv/종료/signal/timeout/시간과 원시 로그는 [결과 디렉터리](../../experiments/public-app/results/2026-11-08-prepared)에 있다. signal/timeout은 발생하지 않았다.

Node 22.19.0, npm 10.9.3, Darwin arm64, 분석 TypeScript 5.9.3을 사용했다. 설치는 public npm registry의 lockfile v3 기반 `npm ci --ignore-scripts --no-audit --no-fund --workspace=@vendure/admin-ui --workspace=@vendure/common --include-workspace-root`다. 전체 workspace 설치는 요구되지 않았으나 root 개발 도구의 전이 의존성도 포함한다. lock 존중/명시 workspace/스크립트 옵션의 의미는 [npm v10 문서](https://docs.npmjs.com/cli/v10/commands/npm-ci/)를 따른다. legacy-peer-deps/force/override는 사용하지 않았다. install lifecycle은 제외했고 common의 원래 `rimraf lib && tsc -p ./tsconfig.build.json`만 실행했다.

의존성 파일 85,192개, 논리 용량 656,572,522 bytes(약 626MiB)다. 새 common lib는 36파일/489,571 bytes이고 과업 설정 1파일은 별도로 기록했다. 다운로드 cache·디스크 할당량·상주 메모리 전체 비용은 이 값에 포함하지 않는다. 전체 Angular 앱 build, codegen, native module 실행, 서비스/DB/브라우저 기동은 수행하지 않았으므로 운영 환경 준비 완료를 뜻하지 않는다.

준비 종료 이후 문서 정리·Ontosary 회귀 검사·기록 검토·PR 반영은 별도 단계다. [validation.json](../../experiments/public-app/results/2026-11-08-prepared/validation.json)에 회귀 로그의 종료 시간/결과와 보고 단계의 검증 시각을 기록한다. Git 전달 시간은 PR 생성/병합 시각으로 별도 추적한다. 자동화 wall time이며 사람 준비/탐색 시간으로 환산하지 않는다.

## 원문·의존성 경계와 재현

원본 inventory 4,735개가 설치 전후·빌드 후·준비 종료 때 변하지 않았고 11개 anchor도 일치했다. 원래 strict/paths/tsconfig/lockfile/generated source를 유지했다. 기존 과업 설정 JSON은 V1과 byte 내용/유효 설정 대조까지 같고 새 common lib는 원래 generated source와 분리한다. [input-audit](../../experiments/public-app/results/2026-11-08-prepared/input-audit/summary.json)는 설치된 패키지 버전·lock integrity·라이선스 선언/파일 hash·전체 설치 파일 hash를 제공한다. 모두 license 선언이 있었지만 완전한 법률 검토를 뜻하지 않는다. 의존성 바이너리나 새 lib는 저장소에 배포하지 않는다. 원시 scan의 원문 조각은 [기존 Vendure 고지](../../experiments/public-app/results/2026-11-08/vendure/source-notice.json)의 GPL-3.0-or-later 등 원래 라이선스를 유지한다.

같은 설치 cache/절대 경로에서 새 출력으로 반복한 [9파일 재현](../../experiments/public-app/results/2026-11-08-prepared/reproduction.json)이 일치했다. 다른 길이의 cache 경로에서는 TypeChecker의 생략된 타입 표시가 달라질 수 있다는 기존 제한은 유지한다. 설치/빌드 자체는 독립 재현하지 않았다.

자체 검토에서 macOS `/tmp` → `/private/tmp` realpath 때문에 원시 Program의 일부 의존성 경로가 `<external>/basename`으로 축약됐음을 확인했다. 원래 9개 결과는 보존했다. **보고 단계**에 추가한 [경로 감사](../../experiments/public-app/results/2026-11-08-prepared/program-path-audit.json.gz)는 scan/context를 재실행하지 않고 Program 파일 순서·hash 전체 일치와 실제 경계를 검증한다. 원래/과업 각각 1,715/1,265개 경로를 복원했으며 모두 준비 cache 안이다. 그 밖에는 의도한 분석기 TS 표준 lib만 있다. 호스트 Ontosary의 앱 의존성을 빌린 파일은 없었다. 원시 import edge의 basename 표기는 이 제한이 남으므로 전체 의존 그래프로 해석하지 않는다.

## 회귀 확인과 다음 판단

- `pnpm check`: 타입 검사, 8파일/136테스트, Vite production build 통과.
- `pnpm experiment`: 기존 비교 4/4, context 13×26, 개념 20/후보 8/관계 8, 잘림 없음.
- 원문·과업·core/CLI·기존 corpus·V1 runner와 과거 원시 결과는 변경하지 않았다. 준비용 기록기와 날짜별 증거만 추가했다.

이번 가설은 “원래 strict 전제를 유지한 오류 없는 과업 입력을 준비할 수 있는가”였고 기존 4진입 설정에서 가능함을 확인했다. 그 입력의 FCA 탐색 비교 범위 적합성은 실패했다. HTML 두 필수 근거는 여전히 수동이며 사람 정답/업무 의미 승인·탐색 시간·Gate 2~4는 미검증이다.

다음에는 **과업 범위 선택 계약을 먼저 검토할 것을 권고**한다. 질문에서 출발한 포함/제외 기준, import 근거와 context 참여 함수의 구분, 선택 편향 공개, 객체·속성 상한의 사전 검사를 정해야 한다. 이는 성공 함수만 골라 통과시키는 이번 실행의 수정이 아니라 별도 설계 판단이다. 탐색 사실과 논리 검증 전제 분리, 표본 전략 재검토도 대안으로 남긴다. 이번에 이 설계를 구현하거나 추가 설치/후보 탐색을 진행하지 않았다.
