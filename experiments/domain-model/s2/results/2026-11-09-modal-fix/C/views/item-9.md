# item-9

item:
 status: "Found"
 value:
  id: "ui-gates"
  kind: "observed-behavior-candidate"
  factRefs:
   항목 1:
"source-V01"
   항목 2:
"source-V05"
  candidateRefs:

  source:
   id: "ui-gates"
   kind: "observed-behavior-candidate"
   label: "메뉴 노출과 제출 비활성"
   status: "pending-review"
   author: "agent"
   factRefs:
    항목 1:
"source-V01"
    항목 2:
"source-V05"
   candidateRefs:

   relatedItems:
    항목 1:
"cancel-request"
   interpretation: "HTML 메뉴/버튼 조건은 수동 원문 근거이며 TS 자동 분석 결과가 아니다."
   unverified:
    항목 1:
"서버 권한·요청 성공을 UI 조건으로 증명할 수 없다."
   intendedPolicy: null
neighbors:
 status: "Found"
 value:
  항목 1:
   from: "ui-gates"
   to: "cancel-request"
   kind: "related-item"
   provenance: "S1.items/9/relatedItems"
   direction: "outgoing"
