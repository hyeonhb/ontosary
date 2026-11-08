# item-10

item:
 status: "Found"
 value:
  id: "cancel-transport"
  kind: "relationship-candidate"
  factRefs:
   항목 1:
"source-V08"
   항목 2:
"source-V09"
  candidateRefs:

  source:
   id: "cancel-transport"
   kind: "relationship-candidate"
   label: "취소 service → GraphQL operation"
   status: "pending-review"
   author: "agent"
   factRefs:
    항목 1:
"source-V08"
    항목 2:
"source-V09"
   candidateRefs:

   relatedItems:
    항목 1:
"cancel-request"
   interpretation: "CANCEL_ORDER 문서와 input 전달을 관찰한다."
   unverified:
    항목 1:
"GraphQL/서버 실행 결과는 확인하지 않았다."
   intendedPolicy: null
neighbors:
 status: "Found"
 value:
  항목 1:
   from: "cancel-transport"
   to: "cancel-request"
   kind: "related-item"
   provenance: "S1.items/10/relatedItems"
   direction: "outgoing"
