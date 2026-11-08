# 공개 업무 앱 적합성·한 탐색 과업 준비 — 2026-11-08

**이번 완료물은 과업/원문 근거 준비와 근거 있는 표본 보류 판정이다. 분석 가능한 표본을 확정하지 못했다.** [개발 지시](2026-11-08-public-app-next-plan.md)에 따라 Saleor를 먼저 점검하고, 준비 전제에 맞지 않아 추가 후보 Vendure 하나를 조사했다. 기준 main `87398ba6b61e9524dfb81f8063a19e1018933469`, 작업 브랜치 `codex/public-app-suitability`다. 제품 core/CLI·기존 평가기/corpus·의존성·상한은 변경하지 않았다.

## 후보와 채택 판단

| 후보 / 고정 revision | 원문 라이선스·설정/의존 경계 | 이번 판단 |
| --- | --- | --- |
| Saleor Dashboard `2e1776949e8cae747da480ec3712692554f3284c` | BSD-3-Clause. strict=false, Node >=24 <25 / TS 5.8.3 / pnpm 11.13.1을 표시. 직접 dependencies 72/dev 74. GraphQL 생성 파일·schema·codegen 설정은 archive에 있음 | 보류. 원래 분석 전제 불일치와 명시적 null 전제 아래의 진단/큰 import 범위 |
| Vendure v3.5.0 Angular Admin UI `534e6003534f74761e82de1b8c6061cba89945d1` | `@vendure/admin-ui`는 GPL-3.0-or-later. repository LICENSE에 상용 대안과 plugin exception도 명시. strict=true, root Node >=18 / TS 5.8.2. Admin UI 직접 dependencies 48/dev 34. npm workspaces·package-lock, `@vendure/common/lib/*` 빌드 의존 | 이번 환경에서는 보류. strict는 맞지만 패키지/빌드 의존이 미준비이며 Angular template는 수동 근거로 남음 |
| Medusa `0f901465…` | [이전 조사](2026-11-08-public-app-candidates.md)의 Enterprise Materials hook 경계 | 이전 보류 유지. 이번에는 재다운로드·scan하지 않음 |

Vendure는 고정된 과거 release를 사용했으며 최신 버전이나 React Dashboard의 평가가 아니다. 주문 취소가 명시된 기존 Angular Admin UI로 범위를 정했다. [태그](https://github.com/vendurehq/vendure/releases/tag/v3.5.0)의 commit을 고정했고, 실제 자료는 [manifest](../../experiments/public-app/v1/manifest.json)의 immutable archive/hash로 검증한다.

각 원본 archive의 전체 파일 inventory(Saleor 6,419파일, Vendure 4,735파일), 필요한 config/package/lock/codegen/license hash, 실제 Program 파일/해시를 결과에 남겼다. upstream 코드는 cache에 있으며 새 설치·codegen·서비스 기동·submodule checkout은 수행하지 않았다. 라이선스 원문과 출처는 후보별 `licenses/`, `metadata.json`, `source-notice.json`에 있다. 원시 추출물의 원문 조각에 upstream 라이선스가 적용됨을 명시했으며 Ontosary Apache-2.0으로 바꾸지 않았다. 전체 외부 의존성의 재배포 검토를 끝낸 것은 아니다.

## 도구 출력 전에 작성한 과업과 예비 근거

각 후보의 첫 scan 전에 원문을 읽어 JSON 질문/근거를 작성했고, 첫 실행부터 task hash·파일 hash·고유 UTF-16 anchor/행을 검증했다. Git에 사전등록한 독립 정답셋은 아니며 **agent 작성 / 사람 검토 pending**이다. 후보 출력으로 정답을 역작성하지 않았다.

**Saleor 질문:** 일반 주문의 취소 메뉴에서 API 요청까지 어떤 코드·조건을 확인하며, fulfilled fulfillment가 있을 때 어떤 UI 분기로 이어지는가? [예비 근거 18개](../../experiments/public-app/v1/saleor-task.json)는 required 14 / allowed 2 / unrelated 2 및 불확실 항목으로 구성했다.

- `OrderDetailsPage`의 `status !== CANCELED` 메뉴 조건과 onOrderCancel, `OrderNormalDetails`의 `openModal("cancel")` 연결.
- `FULFILLED` fulfillment 존재 여부와 cancel action에 따른 차단/확인 dialog 분기. optional chaining의 order 누락까지 완전한 정책으로 확정하지 않음.
- 확인 버튼 → `orderCancel.mutate({ id })` → OrderOperations/provider → generated `useOrderCancelMutation`/OrderCancelDocument → 원문 mutation의 연결.
- draft 삭제와 fulfillment 취소는 비관련 동작으로 분리. 오류 표시·후처리는 허용 근거이며 서버 최종 허용 정책과 구분.

[공식 orderCancel 문서](https://docs.saleor.io/api-reference/orders/mutations/order-cancel)는 id 입력·order/errors 결과와 MANAGE_ORDERS 권한을 설명한다. 조회한 문서는 schema 3.23.43이며 Dashboard 고정 revision의 서버 정책을 완전히 규정하는 자료로 취급하지 않았다.

**Vendure 질문:** 관리자 주문 화면의 취소/환불 동작 중 직접 취소로 가는 조건과 dialog 제출에서 API 요청까지의 근거는 무엇인가? [예비 근거 11개](../../experiments/public-app/v1/vendure-task.json)는 required 9 / allowed 1 / unrelated 1 및 불확실 항목이다.

- template의 비-Aggregate·`nextStates.includes('Cancelled')`와 cancelOrRefund 연결.
- PaymentAuthorized/active/settled payment 여부로 취소와 환불을 구분하고, dialog의 사유·선택 수 조건과 입력 구성을 확인.
- dialog 입력이 있을 때만 data service → CANCEL_ORDER mutation으로 전달. dialog 닫기는 업무 취소가 아님.
- HTML 두 파일의 근거는 core의 TS facts 밖이다. 서버 nextStates 계산/커스텀 order process·최종 정책은 이 클라이언트 질문의 확정 답에서 제외.

[공식 주문 lifecycle 설명](https://docs.vendure.io/current/framework/core-concepts/orders)은 상태 기계와 설정 가능성을 설명하지만 조회 시 current 3.8.1 문서였다. 고정 3.5.0 클라이언트의 세부 정책을 대신하지 않는다.

## 원래 설정부터 실행한 결과

Ontosary 실행 환경은 Node 22.19.0, pnpm 11.19.0, TypeScript 5.9.3, macOS arm64다. upstream 앱의 지원 환경을 설치해 build한 결과가 아니다. 특히 Saleor의 요구 Node/TS 버전과 다르다. 조상 `node_modules`가 없는 `/tmp` cache로 호스트의 React/Node 타입이 우연히 해석되는 것을 막았다. 코어의 null 전제/진단 정책은 그대로다.

| 실행 | root 설정 | 실제 구현 파일 / 함수 | 오류 / omissions | 결과 |
| --- | --- | ---: | ---: | --- |
| Saleor original | 원래 tsconfig | Program 생성 전 거부 | 미산출 | strictNullChecks 필요 오류 |
| Saleor scoped | 원래 config 상속, 7 TS/TSX 진입 + 원래 ambient 8개, strictNullChecks=true | 806 / 4,205 | 1,713 / 506 | 컴파일 오류, 모든 predicate unsupported |
| Vendure original | 원래 Admin UI tsconfig | 581 / 4,379 | 2,372 / 751 | 컴파일 오류, 모든 predicate unsupported |
| Vendure scoped | 원래 config 상속, 4 TS 진입, strict 그대로 | 327 / 2,264 | 1,058 / 440 | 컴파일 오류, 모든 predicate unsupported |

원시 근거: [Saleor original](../../experiments/public-app/results/2026-11-08/saleor/original/outcome.json), [Saleor scoped](../../experiments/public-app/results/2026-11-08/saleor/scoped/outcome.json), [Vendure original](../../experiments/public-app/results/2026-11-08/vendure/original/outcome.json), [Vendure scoped](../../experiments/public-app/results/2026-11-08/vendure/scoped/outcome.json). 각 디렉터리에 process/config와 가능한 경우 무손실 gzip의 전체 scan/Program이 있다. `process.exitCode=0`은 실패 관찰을 저장했다는 뜻이며 분석 성공이 아니다.

설정과 원문은 수정하지 않고 별도 `ontosary.scope.json`만 cache에 작성했다. scope 축소는 도구 결과 전에 고정한 진입점으로 했고, 잘 되는 작은 함수만 사후 선택하지 않았다. Saleor 원래 any/scalar any와 ambient 선언은 보존했지만 새 any/stub은 작성하지 않았다. strict plugin이나 gql plugin을 Compiler API가 자동 실행한다고 가정하지 않는다.

Saleor scoped Program 896파일 중 실제 분석 TS 구현은 806개다. `src/graphql/{types,hooks,typePolicies}.generated.ts` 및 `.featureFlags/generated.tsx`가 포함됐다. 생성 출처와 입력은 고정 archive에 있으며 새 생성은 하지 않았다. `.gitmodules`의 cloud extension 소스는 이번 Program에 포함되지 않았다. missing-module 오류 2307은 916개, JSX runtime 부재 2875는 308개다. null 관련 오류도 보존했지만, 외부 타입이 누락된 상태여서 설치 후 남는 오류 수로 단정하지 않는다.

Vendure scoped Program 364파일 중 실제 분석 TS 구현은 327개다. 기존 generated-types는 확보됐지만 Angular/RxJS/GraphQL과 `@vendure/common/lib/*` 등의 의존 경계가 남았다. missing-module 오류 2307은 788개, tslib helper 관련 2354는 226개다. 없는 lib를 소스로 임의 alias하거나 생성 타입을 재작성하지 않았다. 필요한 common 소스가 archive에 있는 것과 빌드된 모듈이 해석되는 것은 다르다.

이 파일 수는 전체 앱 coverage가 아니다. `program.json.gz`는 실제 Program과 literal import 해석을 기록하지만 없는 외부 패키지의 전이 closure나 비리터럴 동적 import를 완전히 표현하지 않는다. unresolved import에는 ambient CSS/이미지도 있으므로 그 수를 오류 수로 쓰지 않는다. 컴파일 오류 때문에 **단순 그룹/FCA는 모두 미실행**, 상한/잘림은 미측정이다. 함수 수가 현 128 객체 한도보다 크지만 오류가 해결된 이후의 FCA 결과나 비용을 실제 관찰한 것으로 쓰지 않는다.

## 재현·기준선·비용

- `pnpm check`: 8파일/136테스트·타입 검사·예제 production build 통과. `pnpm experiment`: 기존 비교 4/4 유지.
- 같은 절대 cache 경로에서 새 output 경로로 실행한 비시간 파일은 [Saleor 13개](../../experiments/public-app/results/2026-11-08/saleor-reproduction.json), [Vendure 17개](../../experiments/public-app/results/2026-11-08/vendure-reproduction.json)가 byte 일치했다. 두 설정의 오류 상태/진단 수/predicate unsupported/그룹 미생성도 assert했다.
- 별도 archive 다운로드 cache의 inventory는 같았지만 다른 길이의 절대 경로에서 타입 표시 문자열 2개(Saleor), 9개/6개(Vendure original/scoped)가 달라졌다. [전체 필드 차이와 hash](../../experiments/public-app/results/2026-11-08/cross-cache-differences.json)를 보존했다. TypeChecker의 표시 길이 생략 후 경로 치환으로는 복원할 수 없으므로 이식성 성공을 주장하지 않는다. 제품 코어를 이 과제에서 바꾸지 않았다.
- [Saleor 이름 검색](../../experiments/public-app/results/2026-11-08/saleor-search.json)은 806파일 중 17파일/96행, required 14개 모두의 **파일**에 도달했고 anchor 시작 행은 8개가 직접 일치했다. [Vendure](../../experiments/public-app/results/2026-11-08/vendure-search.json)는 TS 327 + HTML 2파일 중 10파일/37행, required 9개 모두의 파일에 도달했고 anchor 시작 행은 4개가 일치했다. 답을 이미 읽은 agent가 선택한 검색어이므로 blind baseline이나 사람의 과업 완수가 아니다. 이름 검색으로 관련 파일을 찾기 쉬운 표본이라는 관찰만 남긴다. 조건 이해·연결 검토·LSP 효용은 미측정이다.

| 기계 준비/관찰 비용 | Saleor | Vendure |
| --- | ---: | ---: |
| archive 다운로드 bytes | 10,106,870 | 45,557,011 |
| 다운로드·hash·압축 해제·inventory wall time | 2,784ms | 5,392ms |
| 원래 설정 관찰 wall time | 448ms | 4,912ms |
| scoped 관찰 wall time | 9,178ms | 3,393ms |

위 시간은 보관한 첫 정식 실행의 도구 측정값이며 일반 성능 benchmark가 아니다. 조사·스크립트 작성·수정/반복 실행을 포함한 전체 agent 작업 비용은 미계측이고 사람 준비/과업 시간은 null이다. 전체 의존성 설치·workspace build·새 codegen 비용도 미측정이다. 초기 harness 메타데이터의 lockfile 경로는 실제 Vendure package-lock.json으로 교정한 뒤 정식 결과를 새 경로에 생성했다. 과거 리뷰·기존 corpus 원시 증거는 덮어쓰지 않았다.

## 다음 판단 한 가지

**다음에는 고정 Vendure Admin UI의 의존성 및 common 빌드 준비 비용만 제한적으로 확인할 것을 권한다.** Saleor는 원래 null 전제까지 다르지만 Vendure는 기존 strict를 유지할 수 있다. 이것은 앱 채택 권고가 아니라 다음 준비 실험 순서다. 설치가 성공해도 HTML 근거는 수동으로 동일하게 제공하고, 오류 없는 범위와 FCA 입력 상한을 별도로 확인해야 한다. 또 원문 변경/core 전제 완화가 필요해지면 실패를 보존하고 비용·선택지로 판단한다.

이번 점검은 후보 최대 2개, 각 original/scoped 관찰 1개, process당 120초/heap 4GiB, bulk 앱 설치 없음의 명시적 예산이었다. 준비되지 않은 의존성 실패를 앱의 영구 부적합으로 일반화하지 않는다. 참가자 모집·연락, 사람 정답 승인·첫 노출 배정·시간 절차, A/B/C 비교 자료 동결은 아직 미완료다. 선택 가능한 분석 표본이 없어 조건별 자료를 배포하지 않았다. [절차 초안](../experiments/concept-exploration-protocol.md)은 미실행으로 유지하며 탐색 시간 개선이나 Gate 2~4 통과를 주장하지 않는다.

재현 명령·출처·지원 경계는 [실험 README](../../experiments/public-app/README.md), 구현/준비 결정은 ADR-018에 정리했다.
