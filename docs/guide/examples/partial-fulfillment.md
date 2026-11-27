# “출고할 수 있는 품목이 없으면 운영자에게 이유를 보여 주세요.”

이 요청을 Vendure v3.5.0의 주문 관리 화면에 적용한다고 하자. agent에게 수정을 맡기기 전에 **어떤 때 ‘재고 부족’이라고 말해도 되는지** 개발자와 함께 확인하는 기록이다.

### 변경 전 코드에서 확인한 두 판단

**주문 상세에서 출고 창을 열 수 있는가?** 묶음 주문(`Aggregate`)에는 출고 버튼을 표시하지 않는다. 다른 주문은 미출고 수량이 남은 품목이 하나 이상이고, 미정산 변경이 없고, 미결제 차액이 정확히 0이어야 한다. 여기에 가능한 다음 상태 중 `Shipped`, `PartiallyShipped`, `Delivered`가 하나라도 있어야 버튼이 활성화된다. 이 단계에서는 재고를 읽지 않는다. [주문 상세 버튼](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.html#L32-L39) · [canAddFulfillment](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts#L310-L331)

**열린 창에서 품목별로 몇 개를 선택할 수 있는가?** 주문 수량에서 같은 주문 행에 이미 배정된 출고 수량을 뺀다. 대기 중인 출고도 배정량에 포함하고 취소된 출고는 제외한다. 재고 추적이 켜진 품목의 상한은 남은 수량과 현재고 중 작은 값이다. 추적이 꺼지면 남은 수량이 상한이다. 품목 설정이 ‘상속’이면 전역 설정을 따른다. 창은 처음에 각 품목의 상한만큼 선택한다. [초기 선택량 설정](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/admin-ui/src/lib/order/src/components/fulfill-order-dialog/fulfill-order-dialog.component.ts#L38-L48) · [getFulfillableCount와 getUnfulfilledCount](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/admin-ui/src/lib/order/src/components/fulfill-order-dialog/fulfill-order-dialog.component.ts#L64-L82)

### 같은 주문에서 확인할 세 장면

위의 진입 조건을 충족한 부분 출고 주문이다. **A는 5개** 중 출고 2개와 대기 1개로 2개가 남았다(취소된 출고 1개는 제외). **B는 3개** 중 1개를 출고해 2개가 남았다. 두 품목 모두 현재고는 0이고 출고 양식은 유효하다. 아래 세 장면에서 모두 출고 창을 열 수 있다.

| 창에서 본 상황 | 상한 A / B | 선택 A / B | 현재 생성 버튼 | 제안하는 재고 부족 안내 |
| --- | --- | --- | --- | --- |
| 두 품목 모두 재고 추적 | 0 / 0 | 0 / 0 | 비활성 | 표시 |
| B만 재고 추적을 끔 | 0 / 2 | 0 / 2 | 활성 | 숨김 |
| 바로 위에서 운영자가 B의 선택량만 0으로 바꿈 | 0 / 2 | 0 / 0 | 비활성 | 숨김 |

**후속 agent의 UI 제안.** 설정을 받아 상한 계산이 끝난 뒤, 미출고 수량이 남아도 어느 품목에서든 1개조차 선택할 수 없을 때 재고 부족을 안내한다. 마지막 행에서는 운영자가 B를 다시 2개까지 선택할 수 있다. 버튼이 비활성이라는 사실만 보고 같은 문구를 띄우면 잘못된 이유를 알려 주게 된다. [기존 제출 검사 canSubmit](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/admin-ui/src/lib/order/src/components/fulfill-order-dialog/fulfill-order-dialog.component.ts#L84-L98)

**제작 경위.** 작성 agent가 일반 검색으로 코드를 찾아 원문을 읽고 Ontosary의 `scan`으로 메서드 위치를 재확인했다. 공통점을 묶어 후보를 찾는 FCA는 크기 상한에서 종료됐다. 이 견본은 그 기록과 후속 제안을 편집한 문서이며, 업무 담당자의 정책 승인은 미확인이다.
