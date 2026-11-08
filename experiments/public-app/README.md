# Public business-app suitability — 2026-11-08

[개발 지시](../../docs/reviews/2026-11-08-public-app-next-plan.md)에 따른 **원문 과업 준비와 제한된 적합성 점검**이다. 이번에는 분석 표본을 확정하지 못했다. Saleor/Vendure의 설정·의존성 실패를 보존했으며 실패를 없애려고 원문이나 코어 전제를 바꾸지 않았다. 사람 실험·LSP 비교·탐색 시간 개선은 수행하지 않았다.

## 고정 입력과 원문 근거

- [manifest](v1/manifest.json): immutable revision/archive SHA-256, 설정 변경, 도구 예산, 라이선스/메타데이터 경로.
- [Saleor 과업](v1/saleor-task.json): 일반 주문 취소 메뉴 → fulfillment 분기 → 확인/차단 UI → provider/generated hook → GraphQL 요청. 원문 근거 18개와 불확실 항목.
- [Vendure 과업](v1/vendure-task.json): Angular Admin UI 취소/환불 분기 → 취소 dialog → 입력 구성 → API 요청. 원문 근거 11개. 두 HTML 근거는 TS 추출 범위 밖임을 명시했다.

과업 파일은 각 후보의 첫 scan 전에 작성했고 첫 실행부터 hash/원문 anchor를 검증했다. 작성자는 agent이며 사람 검토는 pending이다. 독립 사전등록·완전한 정답셋이 아니다. 실제 라이브 문서의 버전과 고정 소스 revision을 구분했다. draft 삭제·fulfillment 취소·환불·dialog 닫기를 주문 취소와 같다고 보지 않는다. UI 조건에서 서버의 최종 정책을 추론하지 않는다.

## 관찰 결과

| 후보 / 설정 | 실제 분석 구현 파일 | 컴파일 오류 | 판정 |
| --- | ---: | ---: | --- |
| Saleor 원래 tsconfig | 미실행 | Program 생성 전 거부 | strict=false, strictNullChecks 전제 불충족 |
| Saleor 7 진입 + 원래 ambient 8파일, strictNullChecks=true | 806 | 1,713 | 의존성 미설치/변경된 null 전제 아래 실패 |
| Vendure Admin UI 원래 tsconfig | 581 | 2,372 | 의존성·workspace build 산출물 부재 상태의 실패 |
| Vendure 4 진입, strict 그대로 | 327 | 1,058 | 동일 의존 경계가 남음 |

파일 수는 실제 방문한 TS 구현 파일 수이며 전체 앱 coverage 비율이 아니다. 컴파일 오류가 있는 facts로 단순 그룹/FCA를 만들지 않았다. 그룹/후보 수·잘림은 **미측정**이며 0이나 성공이 아니다. 실패 원시 scan, 실제 Program 파일/해시/import resolution, 모든 진단/omissions는 [날짜별 결과](results/2026-11-08)에 있다. 입력 상한을 올리거나 잘 되는 함수만 골라 새 범위로 바꾸지 않았다.

미설치 표본의 진단 수는 upstream 앱 자체가 잘못됐다는 증명이 아니다. 이번 준비 예산은 후보 2개, 후보별 원래 설정과 과업 진입 설정 각 1개, process당 120초/heap 4GiB이며 전체 앱 의존성 설치·빌드·codegen·서비스 기동은 수행하지 않았다. 기존 Ontosary 의존성을 우연히 빌려 오류를 숨기지 않도록 `node_modules` 조상이 없는 임시 cache에서 실행한다. 이 제한을 넘는 준비 비용은 미측정이다.

## 재현

Ontosary의 고정 의존성과 빌드, Node 22.19.0/TypeScript 5.9.3, `tar`와 `rg`를 사용했다. 다른 플랫폼/버전에서 같은 진단을 보장하지 않는다. byte 재현은 동일 절대 cache 경로에서 새 출력 경로 두 개로 대조한다. 서로 다른 길이의 cache 경로는 TypeChecker의 타입 표시 생략 위치까지 바꿀 수 있다. 새 cache/output 경로를 사용한다. upstream 코드는 실행하지 않으며 `prepare`는 archive 다운로드·hash 확인·압축 해제만 수행한다.

```sh
pnpm install --frozen-lockfile
pnpm build
node experiments/public-app/v1/prepare.mjs /tmp/ontosary-public-app-repro-a
node experiments/public-app/v1/run.mjs saleor /tmp/ontosary-public-app-repro-a work/public-app-repro/saleor-a
node experiments/public-app/v1/run.mjs saleor /tmp/ontosary-public-app-repro-a work/public-app-repro/saleor-b
node experiments/public-app/v1/run.mjs vendure /tmp/ontosary-public-app-repro-a work/public-app-repro/vendure-a
node experiments/public-app/v1/run.mjs vendure /tmp/ontosary-public-app-repro-a work/public-app-repro/vendure-b
node experiments/public-app/v1/verify.mjs work/public-app-repro/saleor-a work/public-app-repro/saleor-b
node experiments/public-app/v1/verify.mjs work/public-app-repro/vendure-a work/public-app-repro/vendure-b
node experiments/public-app/v1/search-baseline.mjs saleor /tmp/ontosary-public-app-repro-a work/public-app-repro/saleor-a
node experiments/public-app/v1/search-baseline.mjs vendure /tmp/ontosary-public-app-repro-a work/public-app-repro/vendure-a
pnpm check
pnpm experiment
```

`run`은 원문 inventory/task hash·고유 UTF-16 anchor를 확인하고 원래 설정부터 실행한다. `input.json`에 설정·버전·도구/core/lockfile fingerprint를 기록한다. `process.json`의 exit 0은 관찰 수집의 완료이며 앱 분석 성공이 아니다. `outcome.json`을 읽어야 한다. `verify`는 시간/준비 측정을 제외한 byte 일치와 오류 시 그룹 미생성·predicate unsupported를 assert한다. 원래 설정 실패도 재현 대상이다. 별도 다운로드 cache와 비교한 [불일치 기록](results/2026-11-08/cross-cache-differences.json)에는 Saleor 타입 문자열 2개, Vendure 원래/과업 설정의 문자열 9개/6개 차이가 있다. 경로 prefix를 직렬화 후 치환해도 TypeChecker가 이미 생략한 문자를 복원할 수 없다. 원문 inventory와 다른 관찰 값은 같았지만 이를 이식성 통과로 표시하지 않는다. `config.json`의 `scanEvidenceBase`를 기준으로 scan의 상대 경로를 해석하고, Program 경로는 archive root 기준으로 해석한다.

`program.json.gz`의 unresolved literal import에는 ambient CSS/이미지 모듈도 포함될 수 있으므로 그 개수를 컴파일 오류 수로 취급하지 않는다. 실제 Program 파일에는 TS 표준 라이브러리도 별도 표시한다. import closure는 확보된 소스와 선언에 한정되며 없는 외부 패키지의 전이 의존성·동적 import·프레임워크 plugin 실행을 완전히 표현하지 않는다.

## 라이선스와 범위

원본은 cache에 두고 archive 전체 파일 inventory를 기록했다. 원시 scan과 task anchor에 포함된 원문 조각은 각 upstream 라이선스를 유지하며 Ontosary Apache-2.0으로 재라이선스하지 않는다. 후보별 `source-notice.json`, `metadata.json`, `licenses/`에 원문 출처와 원래 고지를 보존했다.

Saleor는 BSD-3-Clause다. 확인된 생성 파일은 동일 archive의 `src/graphql/{types,hooks,typePolicies}.generated.ts`와 `.featureFlags/generated.tsx`다. 생성 설정/입력도 inventory에 고정했다. 새 codegen을 하지 않았으며 `.gitmodules`의 cloud extension 서브모듈은 다운로드하지 않았다. 이번 scoped Program에는 cloud extension 소스가 포함되지 않았다.

Vendure는 고정 v3.5.0의 Angular `@vendure/admin-ui`를 점검했다(최신 버전 또는 React Dashboard 분석이 아님). 패키지의 GPL-3.0-or-later 표시와 repository LICENSE의 상용 대안/plugin exception을 함께 보존했다. 기존 `generated-types.ts`를 사용하며 `@vendure/common/lib/*` 같은 workspace 빌드 의존은 누락 상태로 기록한다. HTML template와 Angular DI/실행 연결은 TypeScript Compiler API의 추출 성공으로 표시하지 않는다. 두 후보 모두 외부 의존 패키지를 새로 설치·재배포하지 않았으므로 전체 의존성 라이선스 검토 완료를 주장하지 않는다.

## 다음 판단

[개발 인계](../../docs/reviews/2026-11-08-public-app-suitability.md)의 권고는 **Vendure의 고정 Admin UI에 대해 의존성·common 빌드 준비 비용만 한 번 더 제한적으로 검증**하는 것이다. strict 전제를 유지할 수 있다는 이점이 있지만 현재 사용할 수 있는 표본은 아니다. 성공 여부를 확인하기 전 사람 비교용 A/B/C 자료를 배포하지 않는다. 기존 [실험 절차 초안](../../docs/experiments/concept-exploration-protocol.md)은 미실행으로 유지한다.
