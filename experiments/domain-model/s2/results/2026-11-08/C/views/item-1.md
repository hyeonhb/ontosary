# item-1

item:
 status: "Found"
 value:
  id: "line"
  kind: "concept-candidate"
  factRefs:
   항목 1:
"source-V07"
   항목 2:
"source-refund-payload"
  candidateRefs:

  source:
   id: "line"
   kind: "concept-candidate"
   label: "주문 항목"
   status: "pending-review"
   author: "agent"
   factRefs:
    항목 1:
"source-V07"
    항목 2:
"source-refund-payload"
   candidateRefs:

   relatedItems:
    항목 1:
"order"
   interpretation: "취소·환불 입력은 항목별 수량을 구성한다."
   unverified:
    항목 1:
"부분 취소·환불의 서버 제약은 무엇인가?"
   intendedPolicy: null
neighbors:
 status: "Found"
 value:
  항목 1:
   from: "line"
   to: "order"
   kind: "related-item"
   provenance: "S1.items/1/relatedItems"
   direction: "outgoing"
  항목 2:
   from: "cancel-request"
   to: "line"
   kind: "related-item"
   provenance: "S1.items/3/relatedItems"
   direction: "incoming"
  항목 3:
   from: "refund-request"
   to: "line"
   kind: "related-item"
   provenance: "S1.items/4/relatedItems"
   direction: "incoming"
