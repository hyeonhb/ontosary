# fact-0

status: "Found"
value:
 id: "source-V01"
 evidence:
  항목 1:
   id: "source-V01/e0"
   file: "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.html"
   symbol: "*ngIf=\"order.type !== 'Aggregate' && order.nextStates.includes('Cancelled')\""
   offset: 2330
   end: 2406
   line: 51
   anchor: "*ngIf=\"order.type !== 'Aggregate' && order.nextStates.includes('Cancelled')\""
   sha256: "fecfd12fc47bb2f2d862b618a73e0c98104b87225436046d96938d3bc3220d89"
 source:
  id: "source-V01"
  kind: "observed-in-source"
  author: "agent"
  method: "manual-source-reading"
  scope: "Pinned Admin UI client static source; no runtime/server policy guarantee"
  support: "manual; not a whole-function logical proof"
  claim: "메뉴 노출 조건과 cancelOrRefund click. HTML은 core가 읽는 TS facts 밖이며 모든 조건에 원문을 제공해야 한다."
  evidence:
   file: "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.html"
   symbol: "*ngIf=\"order.type !== 'Aggregate' && order.nextStates.includes('Cancelled')\""
   offset: 2330
   line: 51
   anchor: "*ngIf=\"order.type !== 'Aggregate' && order.nextStates.includes('Cancelled')\""
   sha256: "fecfd12fc47bb2f2d862b618a73e0c98104b87225436046d96938d3bc3220d89"
