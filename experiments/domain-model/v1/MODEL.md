# Vendure 취소·환불 모델 초안 읽기

**12개 항목 모두 agent 작성·검토 대기다. 승인된 지식은 없다.** [FCA 전 모델](model-before.json)은 소스를 읽어 작성한 기준선이다. [후 모델](../results/2026-11-08/model-after.json)은 이미 알던 두 항목에 후보 근거 링크만 추가한다. 단순 그룹과 동일한 연결이며 업무 의미를 새로 발견·승인한 것이 아니다.

| 개념 후보 | 관련 동작/관계 | 확인할 근거 | 남은 질문 |
| --- | --- | --- | --- |
| 주문 (`order`) | 클라이언트 취소/환불 분기 (`branch`) | source-V02, V03 | 서버 상태 전이·권한·커스텀 정책은? |
| 주문 항목 (`line`) | 취소 수량과 환불 dialog의 cancel 입력 | source-V07, refund-payload | 서버의 부분 취소/환불 수량 제약은? |
| 결제 (`payment`) | settled 결제 확인과 환불 요청 | source-V03, refund-request | 결제 상태별 실제 허용 정책은? |
| 취소 요청 (`cancel-request`) | dialog-submit, cancel-transport, refund-also-cancels | source-V04/V06/V08/V09, refund-cancel | 다른 화면의 취소 호출과 서버 계약은? |
| 환불 요청 (`refund-request`) | refund-transport, refund-also-cancels | source-V11, refund-payload/refund-mutation | 취소 없는 환불, 서버 오류·권한 정책은? |

나머지 두 항목 `dismiss`, `ui-gates`는 닫기와 요청 취소의 구분, HTML 조건의 한계를 명시한다. 관찰된 클라이언트 동작과 의도한 업무 정책은 다르며 `intendedPolicy`는 모두 null이다. `observed-in-source`는 정적 원문 관찰이며 런타임 성공을 뜻하지 않는다.

## 다음 agent가 따라갈 예

“취소 입력의 reason 계약이 바뀐다”는 과업을 받으면 먼저 `cancel-request`에서 `dialog-submit`과 `cancel-transport`의 factRefs를 따라 파일 hash/anchor를 확인한다. `refund-also-cancels`로 이동하면 `OrderDetailComponent.refundOrder`도 `input.cancel.lines?.length` 아래 `cancelOrder(input.cancel)`을 포함함을 찾을 수 있다. 환불 dialog가 별도의 cancel 입력을 만든다는 `source-refund-payload`도 읽는다. 모든 환불이 취소를 먼저 한다는 규칙은 도출하지 않는다.

`dismiss`의 `source-V10`과 `source-refund-close`는 두 dialog의 `cancel()`이 `resolveWith()`를 인자 없이 호출함을 가리킨다. 이 이름을 주문 취소 요청과 합치지 않는다. `ui-gates`의 HTML 두 근거는 수동 확인이며 UI 노출 조건으로 서버 권한이나 성공을 확정하지 않는다.

사용 순서: 개념 ID → relatedItems → factRefs/candidateRefs → 파일·심볼·offset·anchor → unverified 질문. [`validate-input.mjs`](validate-input.mjs)가 실패하거나 원문과 모델이 충돌하면 모델을 stale/재검토 대상으로 취급하고 원문을 다시 읽는다. 검증 성공은 근거 연결의 정합성만 뜻한다. 모델에 없는 호출부도 검색하고 “이것만 수정하면 충분하다”고 판단하지 않는다. revision 기반 ID는 편집 후 안정적이지 않다.

S2에 제공할 자료의 후보는 이 안내, model-after.json, facts.json.gz, fca.json 및 원문 접근이다. 평가자 전용 `evaluation/`과 결과 정답·실패 oracle는 포함하지 않는다. S2 실행 전 독립 리뷰와 제공 파일 hash 동결을 별도로 수행한다.
