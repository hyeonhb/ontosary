# 일부 출고된 주문의 추가 출고

Vendure v3.5.0 Angular Admin UI에서 확인했다. 주문 상세의 **Fulfill order** 버튼은 남은 수량과 주문 조건으로 활성화된다. 버튼을 누르면 대화상자가 남은 수량에 재고 추적 설정을 적용해 주문 라인별 입력 상한을 계산한다. 따라서 버튼이 활성화되어도 모든 라인의 상한이 0이면 출고를 생성할 수 없다.

## 주문 상세에서 시작할 수 있는 조건

- 주문을 불러온 뒤 `Aggregate` 유형을 제외하고 버튼을 표시한다. 표시된 버튼은 `canAddFulfillment(order)`가 참일 때 활성화된다. [주문 상세 템플릿 L32–39](vendure/packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.html#L32)
- 주문 라인 ID별로 `Cancelled`를 제외한 기존 fulfillment 수량을 합산한다. 합계가 주문 수량보다 작은 라인이 하나 이상 있어야 한다. `Pending` 수량도 합산한다. 여기에 미정산 변경(`isSettled === false`인 변경)이 없고, 미결제액이 **정확히 0**이며, `order.nextStates`에 `Shipped`, `PartiallyShipped`, `Delivered` 중 하나 이상이 포함되어야 한다. 미결제액은 세금 포함 주문 총액에서 결제 인정액을 뺀 값이다. 결제 인정액은 `Cancelled`·`Declined`·`Error` 결제를 제외하고 각 결제액에서 `Failed`를 제외한 환불액을 차감해 합산한다. [`canAddFulfillment` 및 결제 검사 L310–355](vendure/packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts#L310)
- `nextStates`는 서버의 주문 상태 머신에서 온다. 기본 주문 프로세스에서 현재 상태가 `PartiallyShipped`이면 다음 상태에 `Shipped`가 있어 위 조건을 충족한다. [`OrderEntityResolver.nextStates` L127–130](vendure/packages/core/src/api/resolvers/entity/order-entity.resolver.ts#L127) · [기본 주문 전이 L201–203](vendure/packages/core/src/config/order/default-order-process.ts#L201)

## 대화상자에서 라인별로 몇 개까지 입력할 수 있나

- `getUnfulfilledCount`는 주문 라인 수량에서 같은 라인 ID의 취소되지 않은 fulfillment 수량 합계를 뺀다. `getFulfillableCount`는 유효 재고 추적이 켜져 있으면 `min(남은 수량, stockOnHand)`, 꺼져 있으면 남은 수량을 그대로 반환한다. 상품 변형의 `TRUE`는 켜짐, `FALSE`는 꺼짐, `INHERIT`는 전역 `trackInventory`를 따른다. 이 결과가 입력의 초기값이자 상한이다. [`ngOnInit`, `getFulfillableCount`, `getUnfulfilledCount` L38–82](vendure/packages/admin-ui/src/lib/order/src/components/fulfill-order-dialog/fulfill-order-dialog.component.ts#L38)
- 남은 수량이 0인 라인은 입력을 비활성화한다. 생성 버튼을 활성화하려면 각 입력값이 상한 이하여야 하고, 입력 합계가 0보다 커야 하며, fulfillment handler 설정과 폼 컨트롤이 유효해야 한다. [대화상자 템플릿 L26–36, L55–59](vendure/packages/admin-ui/src/lib/order/src/components/fulfill-order-dialog/fulfill-order-dialog.component.html#L26) · [`canSubmit` L84–98](vendure/packages/admin-ui/src/lib/order/src/components/fulfill-order-dialog/fulfill-order-dialog.component.ts#L84)

## 주문 예와 확인 방법

기본 주문 프로세스에서 일반 주문이 `PartiallyShipped` 상태라고 가정한다. 세금 포함 주문 총액과 환불 없는 정상 결제액은 각각 10,000이고, 미정산 변경은 없다. 전역 재고 추적은 켜져 있다.

| 라인 | 주문 수량 | 기존 fulfillment 수량 | 남은 수량 | 재고 추적 / `stockOnHand` | 초기값 및 상한 |
| --- | ---: | --- | ---: | --- | ---: |
| A | 5 | `Shipped` 2, `Pending` 1, `Cancelled` 1 | 2 | `INHERIT` / 1 | 1 |
| B | 3 | `Shipped` 1 | 2 | `FALSE` / 0 | 2 |

주문 상세 버튼이 활성화되고, 유효한 handler를 전제로 대화상자에서 A 1개와 B 2개를 제출할 수 있다. A를 2개로 올리면 생성 버튼이 비활성화된다. 같은 주문에서 A의 재고를 0으로 바꾸고 B의 재고 추적을 `TRUE`로 바꾸면 상세 버튼은 계속 활성화되지만 두 상한이 0이 되어 제출할 수 없다. 반대로 원래 재고를 유지해도 미결제액이 1,000이면 상세 버튼부터 비활성화된다. 이 예는 위 TypeScript 메서드를 추출해 주문 데이터와 유효한 handler 대역으로 확인했다.

업무 의도는 이미 출고에 배정된 수량을 중복 배정하지 않으면서 재고 추적 대상의 이번 출고량을 제한하려는 것으로 해석했다. 실제 생성 시에는 서버가 `UpdateOrder` 권한을 요구하고 수량·재고를 다시 검사한다. 브라우저와 실제 API를 연결한 재현, 배포 환경의 주문 프로세스·권한 설정, 조직의 정책 승인은 미확인이다. [`addFulfillmentToOrder` L95–103](vendure/packages/core/src/api/resolvers/admin/order.resolver.ts#L95) · [`OrderService.createFulfillment` L1509–1529](vendure/packages/core/src/service/services/order.service.ts#L1509)
