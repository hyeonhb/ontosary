# 후보별 추가 검토 — agent 작성, 사람 의미 승인 없음

| 후보 | extent / 공유 역할 | 단순 그룹 대조 | 모델 처리와 해석 보류 |
| --- | --- | --- | --- |
| formal-1 | service 28메서드 / mutation | sends-mutation과 동일 | 주문 취소·환불·쿠폰·주소 등 서로 다른 동작이 섞인다. 넓은 기술 그룹이므로 업무 개념으로 새 항목을 만들지 않는다. 사전 >8개 휴리스틱도 표시한다. |
| formal-2 | 두 dialog select / 결과 인자 반환 | returns-dialog-payload와 동일 | 반환 구조는 서로 다르다. 같은 업무 개념이라는 근거가 아니다. 기존 수동 입력 설명을 유지하고 새 연결을 추가하지 않는다. |
| formal-3 | 상세 화면 8메서드 / modal 열기 | opens-modal과 동일 | 메모 수정·주문 상태 그림도 포함한다. 객체 수 휴리스틱은 경고하지 않지만 의미상 넓은 UI 기술 역할이다. 업무 동일성 해석을 보류한다. |
| formal-4 | 두 dialog cancel / 인자 없는 resolveWith | closes-dialog-empty와 동일 | 기존 dismiss 항목에 후보 참조만 추가한다. 원문에서 이미 알던 닫기 관찰이며 주문 취소 요청으로 해석하지 않는다. |
| formal-5 | 상세 화면 cancelOrder/refundOrder / cancel service + modal | calls-cancel과 동일 | 기존 refund-also-cancels에 후보 참조만 추가한다. 단순 그룹에도 두 공유 속성과 같은 셀 근거를 제공했다. 직접 심볼 참조 검색으로도 보이는 연결이다. |

추가 교집합 후보 0, 새 업무 항목 0, semantic 변경 0. formal-3 → formal-5의 포함 관계는 intent 포함이며 “취소는 modal의 업무 하위 개념”이 아니다. 환불 호출 역할은 지지 객체 하나여서 후보 필터(extent≥2)에 들지 않지만 raw context/단순 그룹/형식 개념에는 남는다. 필터를 바꿔 결과를 늘리지 않았다.

이 결과는 목적 표본의 6역할에서 FCA가 고유한 추가 연결을 주지 않았다는 관찰이다. 다른 속성/표본에서의 FCA 효과나 모델 자체의 H-O를 반증하지 않는다. 후보를 본 뒤 속성을 추가/축소하거나 한도를 바꾸지 않았다. 사람의 검토 시간/모델 품질 개선은 미측정이다.
