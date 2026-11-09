# fact-11

status: "Found"
value:
 id: "source-refund-cancel"
 evidence:
  항목 1:
   id: "source-refund-cancel/e0"
   file: "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts"
   symbol: "refund-cancel"
   offset: 23612
   end: 23645
   line: 615
   anchor: "if (input.cancel.lines?.length) {"
   sha256: "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede"
 source:
  id: "source-refund-cancel"
  kind: "observed-in-source"
  author: "agent"
  method: "manual-source-reading"
  scope: "Pinned Admin UI client static source; no runtime/server policy guarantee"
  support: "manual; not a whole-function logical proof"
  claim: "환불 준비 경로도 cancel.lines 길이가 있을 때 cancelOrder(input.cancel) 호출을 포함한다."
  evidence:
   file: "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts"
   symbol: "refund-cancel"
   offset: 23612
   line: 615
   anchor: "if (input.cancel.lines?.length) {"
   sha256: "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede"
