# fact-15

status: "Found"
value:
 id: "source-refund-mutation"
 evidence:
  항목 1:
   id: "source-refund-mutation/e0"
   file: "packages/admin-ui/src/lib/core/src/data/providers/order-data.service.ts"
   symbol: "refund-mutation"
   offset: 3577
   end: 3623
   line: 123
   anchor: "refundOrder(input: Codegen.RefundOrderInput) {"
   sha256: "27ddd40b2430caebc5f0defc901d1e42aa54f1cb29038fe4e7657a2448c03811"
 source:
  id: "source-refund-mutation"
  kind: "observed-in-source"
  author: "agent"
  method: "manual-source-reading"
  scope: "Pinned Admin UI client static source; no runtime/server policy guarantee"
  support: "manual; not a whole-function logical proof"
  claim: "환불 service는 REFUND_ORDER 문서와 input으로 mutation을 전달한다."
  evidence:
   file: "packages/admin-ui/src/lib/core/src/data/providers/order-data.service.ts"
   symbol: "refund-mutation"
   offset: 3577
   line: 123
   anchor: "refundOrder(input: Codegen.RefundOrderInput) {"
   sha256: "27ddd40b2430caebc5f0defc901d1e42aa54f1cb29038fe4e7657a2448c03811"
