# fact-9

status: "Found"
value:
 id: "source-V10"
 evidence:
  항목 1:
   id: "source-V10/e0"
   file: "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts"
   symbol: "cancel() {"
   offset: 2469
   end: 2479
   line: 78
   anchor: "cancel() {"
   sha256: "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5"
 source:
  id: "source-V10"
  kind: "observed-in-source"
  author: "agent"
  method: "manual-source-reading"
  scope: "Pinned Admin UI client static source; no runtime/server policy guarantee"
  support: "manual; not a whole-function logical proof"
  claim: "대화상자 닫기는 resolveWith()로 입력을 반환하지 않는다. 업무 취소와 구별."
  evidence:
   file: "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts"
   symbol: "cancel() {"
   offset: 2469
   line: 78
   anchor: "cancel() {"
   sha256: "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5"
