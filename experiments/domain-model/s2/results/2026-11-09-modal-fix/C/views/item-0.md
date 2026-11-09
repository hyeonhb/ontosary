# item-0

item:
 status: "Found"
 value:
  id: "order"
  kind: "concept-candidate"
  factRefs:
   항목 1:
"source-V02"
   항목 2:
"source-V08"
  candidateRefs:

  source:
   id: "order"
   kind: "concept-candidate"
   label: "주문"
   status: "pending-review"
   author: "agent"
   factRefs:
    항목 1:
"source-V02"
    항목 2:
"source-V08"
   candidateRefs:

   relatedItems:

   interpretation: "클라이언트의 주문 식별자·상태가 요청 경로에 참여한다."
   unverified:
    항목 1:
"서버 상태 전이와 권한 정책은 무엇인가?"
   intendedPolicy: null
neighbors:
 status: "Found"
 value:
  항목 1:
   from: "line"
   to: "order"
   kind: "related-item"
   provenance: "S1.items/1/relatedItems"
   direction: "incoming"
  항목 2:
   from: "payment"
   to: "order"
   kind: "related-item"
   provenance: "S1.items/2/relatedItems"
   direction: "incoming"
  항목 3:
   from: "cancel-request"
   to: "order"
   kind: "related-item"
   provenance: "S1.items/3/relatedItems"
   direction: "incoming"
  항목 4:
   from: "branch"
   to: "order"
   kind: "related-item"
   provenance: "S1.items/5/relatedItems"
   direction: "incoming"
