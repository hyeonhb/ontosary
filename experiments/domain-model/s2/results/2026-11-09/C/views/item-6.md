# item-6

item:
 status: "Found"
 value:
  id: "dialog-submit"
  kind: "relationship-candidate"
  factRefs:
   항목 1:
"source-V04"
   항목 2:
"source-V06"
   항목 3:
"source-V08"
  candidateRefs:

  source:
   id: "dialog-submit"
   kind: "relationship-candidate"
   label: "대화상자 결과 → 취소 요청"
   status: "pending-review"
   author: "agent"
   factRefs:
    항목 1:
"source-V04"
    항목 2:
"source-V06"
    항목 3:
"source-V08"
   candidateRefs:

   relatedItems:
    항목 1:
"cancel-request"
   interpretation: "modal 열기, 입력 생성, 결과 존재 확인, service 호출을 별개 단계로 검토한다."
   unverified:
    항목 1:
"RxJS 실제 실행·오류 처리 정책은 별도 검증이 필요하다."
   intendedPolicy: null
neighbors:
 status: "Found"
 value:
  항목 1:
   from: "dialog-submit"
   to: "cancel-request"
   kind: "related-item"
   provenance: "S1.items/6/relatedItems"
   direction: "outgoing"
