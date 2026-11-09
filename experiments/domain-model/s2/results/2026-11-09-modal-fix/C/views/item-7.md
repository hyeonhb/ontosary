# item-7

item:
 status: "Found"
 value:
  id: "refund-also-cancels"
  kind: "relationship-candidate"
  factRefs:
   항목 1:
"source-refund-cancel"
   항목 2:
"source-refund-request"
   항목 3:
"source-refund-payload"
  candidateRefs:
   항목 1:
"candidate:formal-5"
  source:
   id: "refund-also-cancels"
   kind: "relationship-candidate"
   label: "환불 경로의 조건부 취소 요청"
   status: "pending-review"
   author: "agent"
   factRefs:
    항목 1:
"source-refund-cancel"
    항목 2:
"source-refund-request"
    항목 3:
"source-refund-payload"
   candidateRefs:
    항목 1:
"candidate:formal-5"
   relatedItems:
    항목 1:
"cancel-request"
    항목 2:
"refund-request"
   interpretation: "두 경로는 취소 service를 공유한다. 취소 입력 변경 검토에 refundOrder도 포함한다. 이미 원문에서 알려진 연결이다."
   unverified:
    항목 1:
"모든 환불에 취소가 필수인 것은 아니다."
    항목 2:
"다른 화면의 호출은 이 모델의 완전성 범위 밖이다."
   intendedPolicy: null
neighbors:
 status: "Found"
 value:
  항목 1:
   from: "refund-also-cancels"
   to: "cancel-request"
   kind: "related-item"
   provenance: "S1.items/7/relatedItems"
   direction: "outgoing"
  항목 2:
   from: "refund-also-cancels"
   to: "refund-request"
   kind: "related-item"
   provenance: "S1.items/7/relatedItems"
   direction: "outgoing"
