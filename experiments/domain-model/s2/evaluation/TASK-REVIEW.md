# 검토용 reason 과업 및 oracle 계약 (평가자 전용)

실제 Vendure 정책 승인이 아니다. 후보 요구는 클라이언트 취소 요청의 reason을 trim한 nonblank 문자열로 제한하는 것이다. GraphQL generated 타입/서버 schema는 바꾸지 않는다. 다른 클라이언트까지 강제할 정책이면 서버 변경이 별도 필요하다.

공통 과업 문장은 A/B/C의 TASK.txt에 동일하며 함수명·정답 위치를 주지 않는다. 아직 실패 처리 확정 전이므로 본 비교를 실행할 수 없다. 두 선택은 (a) invalid 입력을 반환하지 않고 요청/연쇄 환불을 중지, (b) 타입화된 오류/observable error를 반환하고 UI와 후속 체인에서 처리다. 현 oracle/참조 수정은 **검토를 위한 (a) 권고안**이다. service 직접 호출도 invalid일 때 네트워크 요청이 없어야 하며 이번 초안의 자동 판정은 예외 없는 요청 억제만 다루며 동기 예외/stream error 해법은 지원 범위 검토가 필요하다. UI 오류 표시·접근성·서버 반환 계약은 미확정/미평가다. 의미 있는 정책 결정 없이 이 draft 테스트를 본 실험 합격 조건으로 고정하지 않는다.

## 제출 코드 실행과 seam

run.ts는 인자로 받은 **제출 source root**에서 네 클래스의 실제 MethodDeclaration/get/set 본문과 같은 파일의 함수/상수 및 실행되는 상대 import helper를 transpile하여 실행한다. 파일명/클래스 이름이 사라지거나 지원하지 않는 runtime 의존성이 실행되면 unsupported/실패다. 새 상대 helper import는 자체 소유 fixture로 검증했다. 클래스 필드/constructor/상속/decorator 변경은 baseline과 비교하여 미지원으로 거부한다. 지원하지 않는 수정이 통과한 것처럼 표시하지 않는다.

제외 seam: Angular 생성/DI·field initialization, gql metadata, 번역 marker, notification/UI, getOrder 결과/서버 mutation 응답. 주문·항목·결제 입력과 dialog resolver/modal 결과는 명시 fixture 값이다. cancelOrRefund, 두 dialog select/cancel, line 입력 helper/accessor, parent cancel/refund 및 service cancelOrder/refundOrder 본문은 제출 코드 그대로 실행한다. refetchOrder도 원문이며 fetchHistory/getOrder의 외부 효과만 대역이다. summate는 일반 합계 helper 대역이다. RxJS는 준비된 고정 환경의 실제 라이브러리를 사용한다. 대역 안에 취소/환불 분기나 trim/검증 정책을 재구현하지 않는다.

constructor/초기값·Angular HTML·실제 서버/권한·비동기 네트워크 scheduling·전체 UI는 자동 coverage 밖이다. HTML 두 조건은 별도 수동 검토다. 동기 RxJS 흐름의 error-result 분기는 검증하지만 실제 네트워크/stream error 정책은 리뷰가 필요하다. VM은 **untrusted-code security sandbox가 아니다**. 본 제출 실행은 별도 OS/container 경계가 필요하며 현재 isolation=unverified다.

## 사례와 교정

정상/공백포함/빈문자/공백만/null/undefined를 직접 취소·환불중취소·service 경계에서 확인한다(18 draft 사례). 원래 동작 6개는 환불만, 두 dismiss, 취소 오류 뒤 환불 중지, active lines 생략, 양수 lines 보존이다. 호출 인자·횟수·순서와 반환 입력을 raw 결과에 기록한다.

baseline: 보존6/6, draft3/18. 임시 참조 수정: 보존6/6, draft18/18. 직접취소만 수정·trim 누락·모든 환불에 취소 강제·dismiss 요청·취소 실패 후 환불 진행·정상 취소 뒤 환불 누락 변형은 각각 관련 사례에서 실패해야 한다. oracle-check.ts가 제출 복제본을 만들고 실제 run.ts에 전달하며 hash/실패 사례를 남긴다. 참조 수정과 oracle는 agent 자료에 포함하지 않는다. 정답 문자열/정확한 diff를 채점하지 않는다.

모델 의미 검토, B/C 명제 동등성 검토, 원문→실행 seam 충실성 검토, 과업 정책 동결은 서로 다른 pending 항목이다. 이 사례를 이미 아는 known-case pilot이며 일반화 성능을 주장하지 않는다.

실행 하네스는 Promise/async/await 및 검토하지 않은 RxJS operator/scheduler를 명시적 미지원으로 거부한다. 지연 작업 완료 전에 호출 수를 읽어 잘못 통과시키지 않기 위한 범위 제한이다. 더 넓은 비동기 해법은 별도 harness 확장이 필요하며 과업 실패로 단정하지 않는다.
