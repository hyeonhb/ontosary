# 공개 업무 앱 후보 조사 — 2026-11-08

사용자는 첫 탐색 실험의 표본을 **공개 TypeScript 업무 앱 후보부터 조사**하기로 선택했다. 아래는 공식 저장소의 source/config/license를 읽은 소규모 적합성 조사다. 설치·앱 실행·Ontosary scan·정답셋 동결·사람 실험은 수행하지 않았다. revision은 조사 시점의 고정 스냅샷이며 이후 최신 버전을 뜻하지 않는다.

## 후보와 우선순위

| 후보 | 조사 revision | 업무 근거 | 현 제약 / 판단 |
| --- | --- | --- | --- |
| Saleor Dashboard | `2e1776949e8cae747da480ec3712692554f3284c` | 주문 취소 메뉴 → fulfillment 조건 → 확인창 → GraphQL mutation | 첫 적합성 점검 후보. 기본 strict=false, codegen/path alias/외부 의존성 확인 필요. 분석 성공 미검증 |
| Medusa Admin | `0f9014650066193280e0cbc4f3898c02319fffc6` | 주문 취소 동작 → 확인 → hook → 성공/오류 표시 | 보류 후보. monorepo와 project references, 해당 화면의 별도 라이선스 대상 권한 hook 의존 경계 확인 필요 |

## Saleor Dashboard: 프론트엔드 주문 취소 근거가 명확함

공식 [저장소](https://github.com/saleor/saleor-dashboard)와 고정 [LICENSE](https://github.com/saleor/saleor-dashboard/blob/2e1776949e8cae747da480ec3712692554f3284c/LICENSE)는 BSD-3-Clause를 표시한다. 이 조사는 표본의 표시 라이선스와 의존 경계를 확인한 것이며 전체 의존성의 재배포 조건을 확정한 검토가 아니다.

직접 읽은 관련 위치:

- [OrderDetailsPage:154](https://github.com/saleor/saleor-dashboard/blob/2e1776949e8cae747da480ec3712692554f3284c/src/orders/components/OrderDetailsPage/OrderDetailsPage.tsx#L154): 주문 상태에 따른 취소 메뉴 후보 조건과 `onOrderCancel` 연결(208–212행).
- [OrderNormalDetails:202](https://github.com/saleor/saleor-dashboard/blob/2e1776949e8cae747da480ec3712692554f3284c/src/orders/views/OrderDetails/OrderNormalDetails/index.tsx#L202): fulfilled fulfillment 여부를 계산한다. [309행 이후](https://github.com/saleor/saleor-dashboard/blob/2e1776949e8cae747da480ec3712692554f3284c/src/orders/views/OrderDetails/OrderNormalDetails/index.tsx#L309)에서 취소 불가 안내와 취소 확인창을 나누고 제출을 `orderCancel.mutate({id})`에 연결한다.
- [OrderCancelDialog](https://github.com/saleor/saleor-dashboard/blob/2e1776949e8cae747da480ec3712692554f3284c/src/orders/components/OrderCancelDialog/OrderCancelDialog.tsx): 확인·오류 표시와 제출 콜백의 UI 근거.
- [mutations.ts:3](https://github.com/saleor/saleor-dashboard/blob/2e1776949e8cae747da480ec3712692554f3284c/src/orders/mutations.ts#L3): `OrderCancel` GraphQL 요청. 같은 파일의 draft 삭제·fulfillment 취소는 별도 동작이므로 단어 일치만으로 같은 업무 규칙으로 묶지 않는다.

**후보 질문:** “일반 주문의 취소 메뉴에서 실제 취소 요청까지 어떤 코드·조건을 확인해야 하며, 배송 완료 항목이 있을 때 어떤 UI 분기로 이어지는가?” UI에서 확인한 조건과 서버가 최종 허용하는 정책은 구분한다. 위 목록은 예비 근거이며 완전한 정답이나 사람 승인으로 표시하지 않는다.

**도입 경계:** [tsconfig](https://github.com/saleor/saleor-dashboard/blob/2e1776949e8cae747da480ec3712692554f3284c/tsconfig.json)는 strict=false이며 strictNullChecks를 켜지 않는다. 현 Ontosary `src/core/analyzer.ts:22–24`의 진입 전제와 맞지 않으므로 원래 설정으로 곧바로 분석 가능한 표본이라고 추천할 수 없다. 이는 설정과 코드 대조에 따른 판단이며 실제 전체 checkout scan을 실행한 결과는 아니다. strict plugin이 Compiler API의 전제를 자동으로 충족한다고 가정하지 않는다.

[package.json](https://github.com/saleor/saleor-dashboard/blob/2e1776949e8cae747da480ec3712692554f3284c/package.json)은 GraphQL codegen을 포함하고, [gitmodules](https://github.com/saleor/saleor-dashboard/blob/2e1776949e8cae747da480ec3712692554f3284c/.gitmodules)는 cloud extension 서브모듈을 가리킨다. 실제 필요한 generated 파일과 import closure, 외부 소스/의존성 라이선스, 설정 비용은 후속 확인 대상이다. 별도 분석 설정을 시도한다면 변경 조건·진단·범위를 모두 기록하며 upstream와 동일한 의미/전체 coverage라고 주장하지 않는다. 실패를 없애기 위해 core의 strictNullChecks 전제를 완화하지 않는다.

## Medusa: 업무 흐름은 있지만 현재 revision의 의존 경계가 복잡함

[주문 화면](https://github.com/medusajs/medusa/blob/0f9014650066193280e0cbc4f3898c02319fffc6/packages/admin/dashboard/src/routes/orders/order-detail/components/order-general-section/order-general-section.tsx#L34)은 `useCancelOrder`와 확인창, 성공/오류 표시를 연결하고 88행에서 취소 상태에 따라 동작을 비활성화한다. [Admin 설정](https://github.com/medusajs/medusa/blob/0f9014650066193280e0cbc4f3898c02319fffc6/packages/admin/dashboard/tsconfig.json)은 별도 project reference를 포함한다. 전체 저장소 트리 조회는 연결 오류로 완료하지 못했으며 위 디렉터리와 파일을 개별 조회했다.

고정 [LICENSE](https://github.com/medusajs/medusa/blob/0f9014650066193280e0cbc4f3898c02319fffc6/LICENSE)는 MIT의 적용에서 Enterprise Materials를 제외한다. [별도 목록](https://github.com/medusajs/medusa/blob/0f9014650066193280e0cbc4f3898c02319fffc6/ENTERPRISE-LICENSE.md#L72)에 `packages/admin/dashboard/src/hooks/use-resource-permissions.tsx`가 있고, 위 주문 화면은 이 hook을 import한다. 따라서 저장소 전체를 단순 MIT 표본으로 취급하거나 이 의존성을 포함한 공개 재현 자료를 바로 만들지 않는다. 별도 자료 사용·재배포 판단 없이 우선 보류하고 더 단순한 후보를 찾는 편이 이번 작은 실험에 적절하다.

## 다음 확인

Saleor의 작은 원문 범위와 import closure가 현 core 전제 아래 진단·상한을 충족할 수 있는지 먼저 점검한다. 어렵다면 실패와 비용을 남기고 공개 TS 업무 앱 후보 하나를 대체 조사한다. 두 후보 모두 조건을 충족하지 않으면 “적합한 표본 미선정”이 유효한 결과다. 실행 가능한 예제처럼 보이게 원문 업무 로직을 재작성하거나 generated/stub 타입으로 의미를 축소하지 않는다. 후보/범위 선택 근거와 원래 설정 실패를 모두 보존한다.
