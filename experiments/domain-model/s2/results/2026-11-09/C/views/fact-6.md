# fact-6

status: "Found"
value:
 id: "source-V07"
 evidence:
  항목 1:
   id: "source-V07/e0"
   file: "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts"
   symbol: "private getLineInputs(): OrderLineInput[] | undefined {"
   offset: 2519
   end: 2574
   line: 82
   anchor: "private getLineInputs(): OrderLineInput[] | undefined {"
   sha256: "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5"
 source:
  id: "source-V07"
  kind: "observed-in-source"
  author: "agent"
  method: "manual-source-reading"
  scope: "Pinned Admin UI client static source; no runtime/server policy guarantee"
  support: "manual; not a whole-function logical proof"
  claim: "active이면 lines 생략, 아니면 양수 quantity만 포함."
  evidence:
   file: "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts"
   symbol: "private getLineInputs(): OrderLineInput[] | undefined {"
   offset: 2519
   line: 82
   anchor: "private getLineInputs(): OrderLineInput[] | undefined {"
   sha256: "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5"
