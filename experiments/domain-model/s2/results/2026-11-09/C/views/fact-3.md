# fact-3

status: "Found"
value:
 id: "source-V04"
 evidence:
  항목 1:
   id: "source-V04/e0"
   file: "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts"
   symbol: "private cancelOrder(order: OrderDetailFragment) {"
   offset: 22379
   end: 22428
   line: 576
   anchor: "private cancelOrder(order: OrderDetailFragment) {"
   sha256: "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede"
 source:
  id: "source-V04"
  kind: "observed-in-source"
  author: "agent"
  method: "manual-source-reading"
  scope: "Pinned Admin UI client static source; no runtime/server policy guarantee"
  support: "manual; not a whole-function logical proof"
  claim: "취소 dialog를 열고 입력이 있을 때 dataService.order.cancelOrder 호출; 닫기는 undefined."
  evidence:
   file: "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts"
   symbol: "private cancelOrder(order: OrderDetailFragment) {"
   offset: 22379
   line: 576
   anchor: "private cancelOrder(order: OrderDetailFragment) {"
   sha256: "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede"
