# 검토용 reason 과업·평가 계약 v2 (평가자 전용)

2026-11-09 R8/R9/R10 보완 구현이다. 실제 Vendure 정책 승인이 아니며 `readyForTrial:false`다. 가상 요구는 **취소 payload의 reason만** trim/nonblank로 제한한다. invalid 취소 입력의 요청/연쇄 환불을 억제하는 대안(a)을 교정한다. 동기 예외/stream error 대안(b), UI 표시/닫힘, 사람의 원문 충실성·B/C 의미 동등성, 실제 격리·agent 조건은 별도 검토/동결 전이다. generated/server schema는 바꾸지 않는다.

## 적용 범위와 기대 요청

직접 취소·service 직접 호출은 취소 reason을 정규화한다. 환불과 실제 일부 취소가 함께 있는 경우 취소 lines 유무를 원래 메서드에서 확인해 취소 payload에만 적용한다. invalid 취소이면 후속 환불도 억제한다. **취소 없는 환불 및 혼합 경로의 환불 reason은 원래 값 그대로 보존**한다. 정상/앞뒤 공백/공백만 환불 reason을 모두 보존 검사한다. dialog dismiss는 요청0, 취소 오류 결과 뒤에는 환불0이다.

`behavior.ts`의 두 fixture는 서로 다른 주문·line·결제 ID, 양수 수량1/2와3/4, 환불 금액10/75, 배송 취소 true/false를 사용한다. 양수/0/음수 및 취소 선택·미선택 line, 선택/미선택/0금액 payment를 구분한다. 기대값은 이 fixture와 계약에서 독립적으로 작성하며 제출 결과나 참조 함수로 계산하지 않는다.

취소의 요청 종류/orderId/reason/lines(ID·수량)/cancelShipping, 환불의 종류/paymentId/amount/lines/reason/shipping/adjustment를 대조한다. 요청 배열은 순서와 횟수를 비교하며 추가 요청도 실패다. 객체 key와 lines 순서는 무시하지만 lines 중복·누락·수량은 보존한다. undefined 객체 필드와 부재는 JSON 전송상 같은 것으로 취급하고 null은 별개다. 호출 시점에 structuredClone하여 이후 변조가 관찰 기록을 바꾸지 않게 한다.

총52사례는 보존16 + 가상 요구36이다. reason 여섯 값(정상/앞뒤 공백/빈문자/공백만/null/undefined)을 직접 취소·환불중취소·service 경계에서 두 fixture로 검사한다. null/undefined/빈문자는 메서드 강제 주입이며 원래 UI의 truthiness 조건과 구별해 기록한다. 공백만 문자열은 원래 reason truthiness를 통과한다. HTML·금액 등 전체 UI 허용 조건을 검증했다는 의미가 아니다.

## 제출 타입 검사와 동일 소스 결합

일반 CLI는 **원본 inventory를 포함한 완전한 제출 source root**를 받는다. node_modules/.git만 제외하고 파일을 읽어 메모리 snapshot을 만든다. 누락된 원본을 환경 원문으로 복구하지 않는다. 교정 runner만 `explicit-baseline-delta`를 명시해 고정 baseline과 추가/수정/삭제 집합을 합친다. 과거 네 파일뿐인 디렉터리를 완전한 제출로 인정하지 않는다.

`submission.ts`는 고정 환경의 설정/의존성 위에 제출 snapshot을 올린 CompilerHost로 **원래 클래스·모듈·호출자**를 검사한다. strict/설정/진단을 완화하지 않는다. 설정 JSON 변경은 지원하지 않고 고정 설정을 사용한다. 추가 helper는 import 해석을 통해 Program에 들어가야 한다. 삭제, 변경한 HTML/비TS, 범위 밖 또는 실제 Program에 없는 변경은 미지원이다. baseline1,638파일은 기준 분모이며 helper 제출은1,639다. 새 제출마다 새 Program/SourceFile/진단을 만들고 baseline 환경 감사만 배치에서 재사용한다.

실행기도 같은 메모리 snapshot을 읽는다. submittedManifest·실제 Program 파일/내용·executedFiles를 hash로 대조하며 sourceBinding이 참이어야 전체 통과다. 실제 진단(code/file/line/column/message), 설정/Node/TS, 전체 제출/입력 지문, 변경 파일의 검사 포함 여부, 원문 메서드 anchor/구간을 결과에 남긴다. 환경은 batch 시작과 각 평가 뒤 고정 지문으로 확인한다.

`typecheck` 실패/미지원이면 `behavior:not-run`과 사유를 남기고 합격 수는 null이다. 실행 의존/구문/seam/예외 한계는 `unsupported`, 기대 요청 불일치는 `failed`로 구분한다. `overall:passed`는 타입 검사·동작·동일 소스 결합 모두 통과할 때만 가능하다. CLI exit0은 보고서 수집 완료이며 실패 제출도 포함한다. 설정/입력 준비 자체의 오류는 not-run 보고와 exit1이다.

## 실행 seam과 참조 수정

원래 클래스의 MethodDeclaration/get/set, 같은 파일의 함수/상수 및 지원 상대 helper를 실행한다. constructor/field/inheritance/decorator 변경은 거부하며 Angular 생성/DI·UI·서버 응답·gql metadata·번역·getOrder 외부 효과는 명시 대역이다. 분기·reason 변환·오류 결과 처리를 대역에 재구현하지 않는다. RxJS는 기존 환경의 실제 라이브러리이고 runtime module hash를 기록한다. Promise/async/await·미검토 operator는 여전히 미지원이다. VM/동일 호스트 폴더는 보안 격리가 아니다.

검토용 참조 수정은 취소 service의 실제 Observable 반환 타입을 유지하고 invalid 입력에서 빈 stream을 반환한다. 환불 dialog는 실제 취소 lines가 있을 때만 guard를 적용하고 취소 payload만 trim한다. 이는 정답 diff가 아니다. 별도 상대 helper 해법도 실제 타입/동작 검사에서 통과한다. baseline은 보존16/16·요구6/36, 참조와 helper는52/52다. 역사적 참조의 TS 진단5개는 보존되며 v2에서 전체 합격을 거부한다.

`variants.ts`의22제출 교정은 baseline/참조/helper, 역사적 참조·helper 타입/구문/누락·삭제·범위 밖 변경, 기존6동작 결함 및 주문 ID·결제 ID·금액·취소 line ID/수량·환불만 guard·환불 reason trim을 각각 독립적으로 만든다. 동작 결함13종은 타입 검사 통과 후 기대/관찰 요청 불일치로 검출한다. 참조 패치·교정 결과는 평가자 전용이고 A/B/C allowlist에 포함하지 않는다.

원래2026-11-08 결과와 독립 probe는 역사적 증거다. 새 교정은 `verification/2026-11-09/`와 인계 보고를 따른다. 정책/원문 충실성/의미 동등성 검토는 구현자가 대신 승인하지 않는다.
