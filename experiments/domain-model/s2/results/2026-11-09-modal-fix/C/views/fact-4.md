# fact-4

status: "Found"
value:
 id: "source-V05"
 evidence:
  항목 1:
   id: "source-V05/e0"
   file: "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.html"
   symbol: "[disabled]=\"!reason || (!order.active && selectionCount === 0)\""
   offset: 3463
   end: 3526
   line: 88
   anchor: "[disabled]=\"!reason || (!order.active && selectionCount === 0)\""
   sha256: "308499c673a3cf4fc514210e6ab9aef74e8b89c877cea72d25b371db5fa97dc3"
 source:
  id: "source-V05"
  kind: "observed-in-source"
  author: "agent"
  method: "manual-source-reading"
  scope: "Pinned Admin UI client static source; no runtime/server policy guarantee"
  support: "manual; not a whole-function logical proof"
  claim: "사유와 선택 수에 의한 제출 비활성 조건. Angular template 의미는 자동 추출하지 못한다."
  evidence:
   file: "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.html"
   symbol: "[disabled]=\"!reason || (!order.active && selectionCount === 0)\""
   offset: 3463
   line: 88
   anchor: "[disabled]=\"!reason || (!order.active && selectionCount === 0)\""
   sha256: "308499c673a3cf4fc514210e6ab9aef74e8b89c877cea72d25b371db5fa97dc3"
