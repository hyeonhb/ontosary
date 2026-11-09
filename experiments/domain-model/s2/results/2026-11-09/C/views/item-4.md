# item-4

item:
 status: "Found"
 value:
  id: "refund-request"
  kind: "concept-candidate"
  factRefs:
   항목 1:
"source-V11"
   항목 2:
"source-refund-payload"
   항목 3:
"source-refund-mutation"
  candidateRefs:

  source:
   id: "refund-request"
   kind: "concept-candidate"
   label: "환불 요청"
   status: "pending-review"
   author: "agent"
   factRefs:
    항목 1:
"source-V11"
    항목 2:
"source-refund-payload"
    항목 3:
"source-refund-mutation"
   candidateRefs:

   relatedItems:
    항목 1:
"payment"
    항목 2:
"line"
   interpretation: "환불 요청과 함께 조건부 취소 입력을 준비할 수 있다."
   unverified:
    항목 1:
"취소 없는 환불의 허용 범위는 무엇인가?"
   intendedPolicy: null
neighbors:
 status: "Found"
 value:
  항목 1:
   from: "refund-request"
   to: "payment"
   kind: "related-item"
   provenance: "S1.items/4/relatedItems"
   direction: "outgoing"
  항목 2:
   from: "refund-request"
   to: "line"
   kind: "related-item"
   provenance: "S1.items/4/relatedItems"
   direction: "outgoing"
  항목 3:
   from: "refund-also-cancels"
   to: "refund-request"
   kind: "related-item"
   provenance: "S1.items/7/relatedItems"
   direction: "incoming"
  항목 4:
   from: "dismiss"
   to: "refund-request"
   kind: "related-item"
   provenance: "S1.items/8/relatedItems"
   direction: "incoming"
  항목 5:
   from: "refund-transport"
   to: "refund-request"
   kind: "related-item"
   provenance: "S1.items/11/relatedItems"
   direction: "incoming"
