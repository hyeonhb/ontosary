# item-2

item:
 status: "Found"
 value:
  id: "payment"
  kind: "concept-candidate"
  factRefs:
   항목 1:
"source-V03"
   항목 2:
"source-refund-request"
  candidateRefs:

  source:
   id: "payment"
   kind: "concept-candidate"
   label: "결제"
   status: "pending-review"
   author: "agent"
   factRefs:
    항목 1:
"source-V03"
    항목 2:
"source-refund-request"
   candidateRefs:

   relatedItems:
    항목 1:
"order"
   interpretation: "settled 결제 관찰과 환불 요청이 관련되지만 결제 정책 전체는 미확인이다."
   unverified:
    항목 1:
"커스텀 결제 상태에서 분기 의도는 무엇인가?"
   intendedPolicy: null
neighbors:
 status: "Found"
 value:
  항목 1:
   from: "payment"
   to: "order"
   kind: "related-item"
   provenance: "S1.items/2/relatedItems"
   direction: "outgoing"
  항목 2:
   from: "refund-request"
   to: "payment"
   kind: "related-item"
   provenance: "S1.items/4/relatedItems"
   direction: "incoming"
  항목 3:
   from: "branch"
   to: "payment"
   kind: "related-item"
   provenance: "S1.items/5/relatedItems"
   direction: "incoming"
