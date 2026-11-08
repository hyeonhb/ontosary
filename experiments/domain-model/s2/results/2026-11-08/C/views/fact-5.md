# fact-5

status: "Found"
value:
 id: "source-V06"
 evidence:
  항목 1:
   id: "source-V06/e0"
   file: "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts"
   symbol: "select() {"
   offset: 2254
   end: 2264
   line: 69
   anchor: "select() {"
   sha256: "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5"
 source:
  id: "source-V06"
  kind: "observed-in-source"
  author: "agent"
  method: "manual-source-reading"
  scope: "Pinned Admin UI client static source; no runtime/server policy guarantee"
  support: "manual; not a whole-function logical proof"
  claim: "orderId/lines/reason/cancelShipping 구성; cancelAll과 연동."
  evidence:
   file: "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts"
   symbol: "select() {"
   offset: 2254
   line: 69
   anchor: "select() {"
   sha256: "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5"
