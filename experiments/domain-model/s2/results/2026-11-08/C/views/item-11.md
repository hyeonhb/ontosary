# item-11

item:
 status: "Found"
 value:
  id: "refund-transport"
  kind: "relationship-candidate"
  factRefs:
   항목 1:
"source-refund-mutation"
   항목 2:
"source-V11"
  candidateRefs:

  source:
   id: "refund-transport"
   kind: "relationship-candidate"
   label: "환불 service → GraphQL operation"
   status: "pending-review"
   author: "agent"
   factRefs:
    항목 1:
"source-refund-mutation"
    항목 2:
"source-V11"
   candidateRefs:

   relatedItems:
    항목 1:
"refund-request"
   interpretation: "REFUND_ORDER 요청은 취소 operation과 구분한다."
   unverified:
    항목 1:
"서버 환불 정책과 취소 선행 조건은 미확인이다."
   intendedPolicy: null
neighbors:
 status: "Found"
 value:
  항목 1:
   from: "refund-transport"
   to: "refund-request"
   kind: "related-item"
   provenance: "S1.items/11/relatedItems"
   direction: "outgoing"
