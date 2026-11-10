# 개념과 클라이언트 흐름

[코드 관찰](observations.md) · [역할 후보](roles.md) · [원문과 식별 정보](evidence.md)


## status — 자료의 상태와 한계

이 자료의 내용 무결성은 "verified", 변경 전 근거 검사는 "verified"다. 업무 의미 검토는 "pending"이며, 자료의 기준은 "baseline"이다. 현재 작업 소스에 대한 평가는 "not-performed"다. 적용 범위: Purposeful S1 client model; partial app coverage; no complete impact/runtime/server policy guarantee.


## index — 찾아가기

- 주문: 항목 식별자 "order". 아래 항목 절에서 해석·근거·관련 관계를 함께 읽는다.

- 주문 항목: 항목 식별자 "line". 아래 항목 절에서 해석·근거·관련 관계를 함께 읽는다.

- 결제: 항목 식별자 "payment". 아래 항목 절에서 해석·근거·관련 관계를 함께 읽는다.

- 취소 요청: 항목 식별자 "cancel-request". 아래 항목 절에서 해석·근거·관련 관계를 함께 읽는다.

- 환불 요청: 항목 식별자 "refund-request". 아래 항목 절에서 해석·근거·관련 관계를 함께 읽는다.

- 클라이언트 취소/환불 분기: 항목 식별자 "branch". 아래 항목 절에서 해석·근거·관련 관계를 함께 읽는다.

- 대화상자 결과 → 취소 요청: 항목 식별자 "dialog-submit". 아래 항목 절에서 해석·근거·관련 관계를 함께 읽는다.

- 환불 경로의 조건부 취소 요청: 항목 식별자 "refund-also-cancels". 아래 항목 절에서 해석·근거·관련 관계를 함께 읽는다.

- 대화상자 닫기 ≠ 주문 취소: 항목 식별자 "dismiss". 아래 항목 절에서 해석·근거·관련 관계를 함께 읽는다.

- 메뉴 노출과 제출 비활성: 항목 식별자 "ui-gates". 아래 항목 절에서 해석·근거·관련 관계를 함께 읽는다.

- 취소 service → GraphQL operation: 항목 식별자 "cancel-transport". 아래 항목 절에서 해석·근거·관련 관계를 함께 읽는다.

- 환불 service → GraphQL operation: 항목 식별자 "refund-transport". 아래 항목 절에서 해석·근거·관련 관계를 함께 읽는다.


## item-0 — 주문

주문: 클라이언트의 주문 식별자·상태가 요청 경로에 참여한다.

이 항목은 "concept-candidate"이며 상태는 "pending-review", 작성 주체는 "agent"다. 의도한 정책 기록: null. 미확인 질문: "서버 상태 전이와 권한 정책은 무엇인가?".

연결된 코드 사실: ["source-V02","source-V08"]. 발견 후보 참조: []. 원문 연결은 아래 부록의 동일 식별자로 찾는다.

관계 "related-item"는 "line"에서 "order"로 향한다. 이 항목에서 본 방향은 "incoming"이며 기록 근거는 "S1.items/1/relatedItems"다.

관계 "related-item"는 "payment"에서 "order"로 향한다. 이 항목에서 본 방향은 "incoming"이며 기록 근거는 "S1.items/2/relatedItems"다.

관계 "related-item"는 "cancel-request"에서 "order"로 향한다. 이 항목에서 본 방향은 "incoming"이며 기록 근거는 "S1.items/3/relatedItems"다.

관계 "related-item"는 "branch"에서 "order"로 향한다. 이 항목에서 본 방향은 "incoming"이며 기록 근거는 "S1.items/5/relatedItems"다.


## item-1 — 주문 항목

주문 항목: 취소·환불 입력은 항목별 수량을 구성한다.

이 항목은 "concept-candidate"이며 상태는 "pending-review", 작성 주체는 "agent"다. 의도한 정책 기록: null. 미확인 질문: "부분 취소·환불의 서버 제약은 무엇인가?".

연결된 코드 사실: ["source-V07","source-refund-payload"]. 발견 후보 참조: []. 원문 연결은 아래 부록의 동일 식별자로 찾는다.

관계 "related-item"는 "line"에서 "order"로 향한다. 이 항목에서 본 방향은 "outgoing"이며 기록 근거는 "S1.items/1/relatedItems"다.

관계 "related-item"는 "cancel-request"에서 "line"로 향한다. 이 항목에서 본 방향은 "incoming"이며 기록 근거는 "S1.items/3/relatedItems"다.

관계 "related-item"는 "refund-request"에서 "line"로 향한다. 이 항목에서 본 방향은 "incoming"이며 기록 근거는 "S1.items/4/relatedItems"다.


## item-2 — 결제

결제: settled 결제 관찰과 환불 요청이 관련되지만 결제 정책 전체는 미확인이다.

이 항목은 "concept-candidate"이며 상태는 "pending-review", 작성 주체는 "agent"다. 의도한 정책 기록: null. 미확인 질문: "커스텀 결제 상태에서 분기 의도는 무엇인가?".

연결된 코드 사실: ["source-V03","source-refund-request"]. 발견 후보 참조: []. 원문 연결은 아래 부록의 동일 식별자로 찾는다.

관계 "related-item"는 "payment"에서 "order"로 향한다. 이 항목에서 본 방향은 "outgoing"이며 기록 근거는 "S1.items/2/relatedItems"다.

관계 "related-item"는 "refund-request"에서 "payment"로 향한다. 이 항목에서 본 방향은 "incoming"이며 기록 근거는 "S1.items/4/relatedItems"다.

관계 "related-item"는 "branch"에서 "payment"로 향한다. 이 항목에서 본 방향은 "incoming"이며 기록 근거는 "S1.items/5/relatedItems"다.


## item-3 — 취소 요청

취소 요청: dialog 결과를 service와 GraphQL operation에 연결한다.

이 항목은 "concept-candidate"이며 상태는 "pending-review", 작성 주체는 "agent"다. 의도한 정책 기록: null. 미확인 질문: "입력 계약 변경 시 서버·generated 타입 변경도 필요한가?".

연결된 코드 사실: ["source-V06","source-V08","source-V09"]. 발견 후보 참조: []. 원문 연결은 아래 부록의 동일 식별자로 찾는다.

관계 "related-item"는 "cancel-request"에서 "order"로 향한다. 이 항목에서 본 방향은 "outgoing"이며 기록 근거는 "S1.items/3/relatedItems"다.

관계 "related-item"는 "cancel-request"에서 "line"로 향한다. 이 항목에서 본 방향은 "outgoing"이며 기록 근거는 "S1.items/3/relatedItems"다.

관계 "related-item"는 "dialog-submit"에서 "cancel-request"로 향한다. 이 항목에서 본 방향은 "incoming"이며 기록 근거는 "S1.items/6/relatedItems"다.

관계 "related-item"는 "refund-also-cancels"에서 "cancel-request"로 향한다. 이 항목에서 본 방향은 "incoming"이며 기록 근거는 "S1.items/7/relatedItems"다.

관계 "related-item"는 "dismiss"에서 "cancel-request"로 향한다. 이 항목에서 본 방향은 "incoming"이며 기록 근거는 "S1.items/8/relatedItems"다.

관계 "related-item"는 "ui-gates"에서 "cancel-request"로 향한다. 이 항목에서 본 방향은 "incoming"이며 기록 근거는 "S1.items/9/relatedItems"다.

관계 "related-item"는 "cancel-transport"에서 "cancel-request"로 향한다. 이 항목에서 본 방향은 "incoming"이며 기록 근거는 "S1.items/10/relatedItems"다.


## item-4 — 환불 요청

환불 요청: 환불 요청과 함께 조건부 취소 입력을 준비할 수 있다.

이 항목은 "concept-candidate"이며 상태는 "pending-review", 작성 주체는 "agent"다. 의도한 정책 기록: null. 미확인 질문: "취소 없는 환불의 허용 범위는 무엇인가?".

연결된 코드 사실: ["source-V11","source-refund-payload","source-refund-mutation"]. 발견 후보 참조: []. 원문 연결은 아래 부록의 동일 식별자로 찾는다.

관계 "related-item"는 "refund-request"에서 "payment"로 향한다. 이 항목에서 본 방향은 "outgoing"이며 기록 근거는 "S1.items/4/relatedItems"다.

관계 "related-item"는 "refund-request"에서 "line"로 향한다. 이 항목에서 본 방향은 "outgoing"이며 기록 근거는 "S1.items/4/relatedItems"다.

관계 "related-item"는 "refund-also-cancels"에서 "refund-request"로 향한다. 이 항목에서 본 방향은 "incoming"이며 기록 근거는 "S1.items/7/relatedItems"다.

관계 "related-item"는 "dismiss"에서 "refund-request"로 향한다. 이 항목에서 본 방향은 "incoming"이며 기록 근거는 "S1.items/8/relatedItems"다.

관계 "related-item"는 "refund-transport"에서 "refund-request"로 향한다. 이 항목에서 본 방향은 "incoming"이며 기록 근거는 "S1.items/11/relatedItems"다.


## item-5 — 클라이언트 취소/환불 분기

클라이언트 취소/환불 분기: PaymentAuthorized 또는 active 또는 settled payment 없음이면 취소 경로, 그 외 환불 경로.

이 항목은 "observed-behavior-candidate"이며 상태는 "pending-review", 작성 주체는 "agent"다. 의도한 정책 기록: null. 미확인 질문: "이 분기는 서버의 완전한 허용 정책이 아니다.".

연결된 코드 사실: ["source-V02","source-V03"]. 발견 후보 참조: []. 원문 연결은 아래 부록의 동일 식별자로 찾는다.

관계 "related-item"는 "branch"에서 "order"로 향한다. 이 항목에서 본 방향은 "outgoing"이며 기록 근거는 "S1.items/5/relatedItems"다.

관계 "related-item"는 "branch"에서 "payment"로 향한다. 이 항목에서 본 방향은 "outgoing"이며 기록 근거는 "S1.items/5/relatedItems"다.


## item-6 — 대화상자 결과 → 취소 요청

대화상자 결과 → 취소 요청: modal 열기, 입력 생성, 결과 존재 확인, service 호출을 별개 단계로 검토한다.

이 항목은 "relationship-candidate"이며 상태는 "pending-review", 작성 주체는 "agent"다. 의도한 정책 기록: null. 미확인 질문: "RxJS 실제 실행·오류 처리 정책은 별도 검증이 필요하다.".

연결된 코드 사실: ["source-V04","source-V06","source-V08"]. 발견 후보 참조: []. 원문 연결은 아래 부록의 동일 식별자로 찾는다.

관계 "related-item"는 "dialog-submit"에서 "cancel-request"로 향한다. 이 항목에서 본 방향은 "outgoing"이며 기록 근거는 "S1.items/6/relatedItems"다.


## item-7 — 환불 경로의 조건부 취소 요청

환불 경로의 조건부 취소 요청: 두 경로는 취소 service를 공유한다. 취소 입력 변경 검토에 refundOrder도 포함한다. 이미 원문에서 알려진 연결이다.

이 항목은 "relationship-candidate"이며 상태는 "pending-review", 작성 주체는 "agent"다. 의도한 정책 기록: null. 미확인 질문: "모든 환불에 취소가 필수인 것은 아니다."; "다른 화면의 호출은 이 모델의 완전성 범위 밖이다.".

연결된 코드 사실: ["source-refund-cancel","source-refund-request","source-refund-payload"]. 발견 후보 참조: ["candidate:formal-5"]. 원문 연결은 아래 부록의 동일 식별자로 찾는다.

관계 "related-item"는 "refund-also-cancels"에서 "cancel-request"로 향한다. 이 항목에서 본 방향은 "outgoing"이며 기록 근거는 "S1.items/7/relatedItems"다.

관계 "related-item"는 "refund-also-cancels"에서 "refund-request"로 향한다. 이 항목에서 본 방향은 "outgoing"이며 기록 근거는 "S1.items/7/relatedItems"다.


## item-8 — 대화상자 닫기 ≠ 주문 취소

대화상자 닫기 ≠ 주문 취소: 두 dialog의 cancel()은 resolveWith()를 인자 없이 호출한다. 주문 취소 요청으로 합치지 않는다.

이 항목은 "observed-behavior-candidate"이며 상태는 "pending-review", 작성 주체는 "agent"다. 의도한 정책 기록: null. 미확인 질문: "modal 서비스의 runtime 종료 동작은 이 정적 관찰 밖이다.".

연결된 코드 사실: ["source-V10","source-refund-close"]. 발견 후보 참조: ["candidate:formal-4"]. 원문 연결은 아래 부록의 동일 식별자로 찾는다.

관계 "related-item"는 "dismiss"에서 "cancel-request"로 향한다. 이 항목에서 본 방향은 "outgoing"이며 기록 근거는 "S1.items/8/relatedItems"다.

관계 "related-item"는 "dismiss"에서 "refund-request"로 향한다. 이 항목에서 본 방향은 "outgoing"이며 기록 근거는 "S1.items/8/relatedItems"다.


## item-9 — 메뉴 노출과 제출 비활성

메뉴 노출과 제출 비활성: HTML 메뉴/버튼 조건은 수동 원문 근거이며 TS 자동 분석 결과가 아니다.

이 항목은 "observed-behavior-candidate"이며 상태는 "pending-review", 작성 주체는 "agent"다. 의도한 정책 기록: null. 미확인 질문: "서버 권한·요청 성공을 UI 조건으로 증명할 수 없다.".

연결된 코드 사실: ["source-V01","source-V05"]. 발견 후보 참조: []. 원문 연결은 아래 부록의 동일 식별자로 찾는다.

관계 "related-item"는 "ui-gates"에서 "cancel-request"로 향한다. 이 항목에서 본 방향은 "outgoing"이며 기록 근거는 "S1.items/9/relatedItems"다.


## item-10 — 취소 service → GraphQL operation

취소 service → GraphQL operation: CANCEL_ORDER 문서와 input 전달을 관찰한다.

이 항목은 "relationship-candidate"이며 상태는 "pending-review", 작성 주체는 "agent"다. 의도한 정책 기록: null. 미확인 질문: "GraphQL/서버 실행 결과는 확인하지 않았다.".

연결된 코드 사실: ["source-V08","source-V09"]. 발견 후보 참조: []. 원문 연결은 아래 부록의 동일 식별자로 찾는다.

관계 "related-item"는 "cancel-transport"에서 "cancel-request"로 향한다. 이 항목에서 본 방향은 "outgoing"이며 기록 근거는 "S1.items/10/relatedItems"다.


## item-11 — 환불 service → GraphQL operation

환불 service → GraphQL operation: REFUND_ORDER 요청은 취소 operation과 구분한다.

이 항목은 "relationship-candidate"이며 상태는 "pending-review", 작성 주체는 "agent"다. 의도한 정책 기록: null. 미확인 질문: "서버 환불 정책과 취소 선행 조건은 미확인이다.".

연결된 코드 사실: ["source-refund-mutation","source-V11"]. 발견 후보 참조: []. 원문 연결은 아래 부록의 동일 식별자로 찾는다.

관계 "related-item"는 "refund-transport"에서 "refund-request"로 향한다. 이 항목에서 본 방향은 "outgoing"이며 기록 근거는 "S1.items/11/relatedItems"다.
