# item-3

item:
 status: "Found"
 value:
  id: "cancel-request"
  kind: "concept-candidate"
  factRefs:
   항목 1:
"source-V06"
   항목 2:
"source-V08"
   항목 3:
"source-V09"
  candidateRefs:

  source:
   id: "cancel-request"
   kind: "concept-candidate"
   label: "취소 요청"
   status: "pending-review"
   author: "agent"
   factRefs:
    항목 1:
"source-V06"
    항목 2:
"source-V08"
    항목 3:
"source-V09"
   candidateRefs:

   relatedItems:
    항목 1:
"order"
    항목 2:
"line"
   interpretation: "dialog 결과를 service와 GraphQL operation에 연결한다."
   unverified:
    항목 1:
"입력 계약 변경 시 서버·generated 타입 변경도 필요한가?"
   intendedPolicy: null
neighbors:
 status: "Found"
 value:
  항목 1:
   from: "cancel-request"
   to: "order"
   kind: "related-item"
   provenance: "S1.items/3/relatedItems"
   direction: "outgoing"
  항목 2:
   from: "cancel-request"
   to: "line"
   kind: "related-item"
   provenance: "S1.items/3/relatedItems"
   direction: "outgoing"
  항목 3:
   from: "dialog-submit"
   to: "cancel-request"
   kind: "related-item"
   provenance: "S1.items/6/relatedItems"
   direction: "incoming"
  항목 4:
   from: "refund-also-cancels"
   to: "cancel-request"
   kind: "related-item"
   provenance: "S1.items/7/relatedItems"
   direction: "incoming"
  항목 5:
   from: "dismiss"
   to: "cancel-request"
   kind: "related-item"
   provenance: "S1.items/8/relatedItems"
   direction: "incoming"
  항목 6:
   from: "ui-gates"
   to: "cancel-request"
   kind: "related-item"
   provenance: "S1.items/9/relatedItems"
   direction: "incoming"
  항목 7:
   from: "cancel-transport"
   to: "cancel-request"
   kind: "related-item"
   provenance: "S1.items/10/relatedItems"
   direction: "incoming"
