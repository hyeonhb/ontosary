# 코드 관찰과 범위

[개념과 흐름](guide.md) · [원문과 식별 정보](evidence.md)


## fact-0 — source-V01

메뉴 노출 조건과 cancelOrRefund click. HTML은 core가 읽는 TS facts 밖이며 모든 조건에 원문을 제공해야 한다.

관찰 종류는 "observed-in-source", 주체는 "agent", 방법은 "manual-source-reading"다. 지원 수준: manual; not a whole-function logical proof. 범위와 한계: Pinned Admin UI client static source; no runtime/server policy guarantee.


## fact-1 — source-V02

PaymentAuthorized 또는 active 또는 settled payment 없음이면 취소, 그 외 refund 분기.

관찰 종류는 "observed-in-source", 주체는 "agent", 방법은 "manual-source-reading"다. 지원 수준: manual; not a whole-function logical proof. 범위와 한계: Pinned Admin UI client static source; no runtime/server policy guarantee.


## fact-2 — source-V03

Settled payment 존재 판정. 서버 최종 정책은 아님.

관찰 종류는 "observed-in-source", 주체는 "agent", 방법은 "manual-source-reading"다. 지원 수준: manual; not a whole-function logical proof. 범위와 한계: Pinned Admin UI client static source; no runtime/server policy guarantee.


## fact-3 — source-V04

취소 dialog를 열고 입력이 있을 때 dataService.order.cancelOrder 호출; 닫기는 undefined.

관찰 종류는 "observed-in-source", 주체는 "agent", 방법은 "manual-source-reading"다. 지원 수준: manual; not a whole-function logical proof. 범위와 한계: Pinned Admin UI client static source; no runtime/server policy guarantee.


## fact-4 — source-V05

사유와 선택 수에 의한 제출 비활성 조건. Angular template 의미는 자동 추출하지 못한다.

관찰 종류는 "observed-in-source", 주체는 "agent", 방법은 "manual-source-reading"다. 지원 수준: manual; not a whole-function logical proof. 범위와 한계: Pinned Admin UI client static source; no runtime/server policy guarantee.


## fact-5 — source-V06

orderId/lines/reason/cancelShipping 구성; cancelAll과 연동.

관찰 종류는 "observed-in-source", 주체는 "agent", 방법은 "manual-source-reading"다. 지원 수준: manual; not a whole-function logical proof. 범위와 한계: Pinned Admin UI client static source; no runtime/server policy guarantee.


## fact-6 — source-V07

active이면 lines 생략, 아니면 양수 quantity만 포함.

관찰 종류는 "observed-in-source", 주체는 "agent", 방법은 "manual-source-reading"다. 지원 수준: manual; not a whole-function logical proof. 범위와 한계: Pinned Admin UI client static source; no runtime/server policy guarantee.


## fact-7 — source-V08

CANCEL_ORDER 문서와 input으로 BaseDataService.mutate를 호출.

관찰 종류는 "observed-in-source", 주체는 "agent", 방법은 "manual-source-reading"다. 지원 수준: manual; not a whole-function logical proof. 범위와 한계: Pinned Admin UI client static source; no runtime/server policy guarantee.


## fact-8 — source-V09

order detail 또는 error result를 받는 취소 요청.

관찰 종류는 "observed-in-source", 주체는 "agent", 방법은 "manual-source-reading"다. 지원 수준: manual; not a whole-function logical proof. 범위와 한계: Pinned Admin UI client static source; no runtime/server policy guarantee.


## fact-9 — source-V10

대화상자 닫기는 resolveWith()로 입력을 반환하지 않는다. 업무 취소와 구별.

관찰 종류는 "observed-in-source", 주체는 "agent", 방법은 "manual-source-reading"다. 지원 수준: manual; not a whole-function logical proof. 범위와 한계: Pinned Admin UI client static source; no runtime/server policy guarantee.


## fact-10 — source-V11

환불 요청은 연결된 별도 분기이며 취소 요청과 같은 규칙으로 취급하지 않는다.

관찰 종류는 "observed-in-source", 주체는 "agent", 방법은 "manual-source-reading"다. 지원 수준: manual; not a whole-function logical proof. 범위와 한계: Pinned Admin UI client static source; no runtime/server policy guarantee.


## fact-11 — source-refund-cancel

환불 준비 경로도 cancel.lines 길이가 있을 때 cancelOrder(input.cancel) 호출을 포함한다.

관찰 종류는 "observed-in-source", 주체는 "agent", 방법은 "manual-source-reading"다. 지원 수준: manual; not a whole-function logical proof. 범위와 한계: Pinned Admin UI client static source; no runtime/server policy guarantee.


## fact-12 — source-refund-request

앞선 결과 input이 있고 refunds 길이가 있을 때 각 refund의 service 호출식을 구성한다. 모든 환불에 취소가 필수라는 뜻은 아니다.

관찰 종류는 "observed-in-source", 주체는 "agent", 방법은 "manual-source-reading"다. 지원 수준: manual; not a whole-function logical proof. 범위와 한계: Pinned Admin UI client static source; no runtime/server policy guarantee.


## fact-13 — source-refund-payload

환불 dialog select는 refunds와 별도로 cancel 입력(orderId/lines/reason/cancelShipping)을 구성한다.

관찰 종류는 "observed-in-source", 주체는 "agent", 방법은 "manual-source-reading"다. 지원 수준: manual; not a whole-function logical proof. 범위와 한계: Pinned Admin UI client static source; no runtime/server policy guarantee.


## fact-14 — source-refund-close

환불 dialog cancel은 결과 인자 없이 닫는다.

관찰 종류는 "observed-in-source", 주체는 "agent", 방법은 "manual-source-reading"다. 지원 수준: manual; not a whole-function logical proof. 범위와 한계: Pinned Admin UI client static source; no runtime/server policy guarantee.


## fact-15 — source-refund-mutation

환불 service는 REFUND_ORDER 문서와 input으로 mutation을 전달한다.

관찰 종류는 "observed-in-source", 주체는 "agent", 방법은 "manual-source-reading"다. 지원 수준: manual; not a whole-function logical proof. 범위와 한계: Pinned Admin UI client static source; no runtime/server policy guarantee.


## fact-16 — cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379:calls-cancel

주문 취소 service 호출

관찰 종류는 "observed-in-source", 주체는 "automated-observer", 방법은 "typescript-ast-symbol-identity"다. 지원 수준: supported-static-role. 범위와 한계: Direct member call expressions in lexical method region, including nested callbacks/functions, excluding nested classes; no reachability/transitive-call claim.

멤버 "534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379"에 대해 역할 "calls-cancel"의 관찰값은 "yes"다. 추가 사유 기록: [].


## fact-17 — cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379:opens-modal

modal component 열기

관찰 종류는 "observed-in-source", 주체는 "automated-observer", 방법은 "typescript-ast-symbol-identity"다. 지원 수준: supported-static-role. 범위와 한계: Direct member call expressions in lexical method region, including nested callbacks/functions, excluding nested classes; no reachability/transitive-call claim.

멤버 "534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379"에 대해 역할 "opens-modal"의 관찰값은 "yes"다. 추가 사유 기록: [].


## fact-18 — cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:23185:calls-cancel

주문 취소 service 호출

관찰 종류는 "observed-in-source", 주체는 "automated-observer", 방법은 "typescript-ast-symbol-identity"다. 지원 수준: supported-static-role. 범위와 한계: Direct member call expressions in lexical method region, including nested callbacks/functions, excluding nested classes; no reachability/transitive-call claim.

멤버 "534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:23185"에 대해 역할 "calls-cancel"의 관찰값은 "yes"다. 추가 사유 기록: [].


## fact-19 — cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:23185:opens-modal

modal component 열기

관찰 종류는 "observed-in-source", 주체는 "automated-observer", 방법은 "typescript-ast-symbol-identity"다. 지원 수준: supported-static-role. 범위와 한계: Direct member call expressions in lexical method region, including nested callbacks/functions, excluding nested classes; no reachability/transitive-call claim.

멤버 "534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:23185"에 대해 역할 "opens-modal"의 관찰값은 "yes"다. 추가 사유 기록: [].


## fact-20 — cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts:2469:closes-dialog-empty

dialog 인자 없이 닫기

관찰 종류는 "observed-in-source", 주체는 "automated-observer", 방법은 "typescript-ast-symbol-identity"다. 지원 수준: supported-static-role. 범위와 한계: Direct member call expressions in lexical method region, including nested callbacks/functions, excluding nested classes; no reachability/transitive-call claim.

멤버 "534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts:2469"에 대해 역할 "closes-dialog-empty"의 관찰값은 "yes"다. 추가 사유 기록: [].


## fact-21 — cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts:7491:closes-dialog-empty

dialog 인자 없이 닫기

관찰 종류는 "observed-in-source", 주체는 "automated-observer", 방법은 "typescript-ast-symbol-identity"다. 지원 수준: supported-static-role. 범위와 한계: Direct member call expressions in lexical method region, including nested callbacks/functions, excluding nested classes; no reachability/transitive-call claim.

멤버 "534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts:7491"에 대해 역할 "closes-dialog-empty"의 관찰값은 "yes"다. 추가 사유 기록: [].
