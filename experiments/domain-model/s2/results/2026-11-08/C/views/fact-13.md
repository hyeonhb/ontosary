# fact-13

status: "Found"
value:
 id: "source-refund-payload"
 evidence:
  항목 1:
   id: "source-refund-payload/e0"
   file: "packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts"
   symbol: "refund-payload"
   offset: 7259
   end: 7304
   line: 196
   anchor: "cancel: {\n                lines: cancelLines,"
   sha256: "d9ea112f17bff650686842306bef46fa6f7564278b1166762a7c9b7a8473a6fb"
 source:
  id: "source-refund-payload"
  kind: "observed-in-source"
  author: "agent"
  method: "manual-source-reading"
  scope: "Pinned Admin UI client static source; no runtime/server policy guarantee"
  support: "manual; not a whole-function logical proof"
  claim: "환불 dialog select는 refunds와 별도로 cancel 입력(orderId/lines/reason/cancelShipping)을 구성한다."
  evidence:
   file: "packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts"
   symbol: "refund-payload"
   offset: 7259
   line: 196
   anchor: "cancel: {\n                lines: cancelLines,"
   sha256: "d9ea112f17bff650686842306bef46fa6f7564278b1166762a7c9b7a8473a6fb"
