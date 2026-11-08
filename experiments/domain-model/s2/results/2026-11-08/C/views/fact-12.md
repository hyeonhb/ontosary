# fact-12

status: "Found"
value:
 id: "source-refund-request"
 evidence:
  항목 1:
   id: "source-refund-request/e0"
   file: "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts"
   symbol: "refund-request"
   offset: 25321
   end: 25348
   line: 647
   anchor: "if (input.refunds.length) {"
   sha256: "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede"
 source:
  id: "source-refund-request"
  kind: "observed-in-source"
  author: "agent"
  method: "manual-source-reading"
  scope: "Pinned Admin UI client static source; no runtime/server policy guarantee"
  support: "manual; not a whole-function logical proof"
  claim: "앞선 결과 input이 있고 refunds 길이가 있을 때 각 refund의 service 호출식을 구성한다. 모든 환불에 취소가 필수라는 뜻은 아니다."
  evidence:
   file: "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts"
   symbol: "refund-request"
   offset: 25321
   line: 647
   anchor: "if (input.refunds.length) {"
   sha256: "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede"
