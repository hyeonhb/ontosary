# 원문과 재현 메타데이터

[개념과 흐름](guide.md) · [코드 관찰](observations.md)

아래 원문·식별자·좌표·조회 상태는 변경 전 자료의 재현 정보를 보존한다.


## status — status 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /baseline/baselineId | "7707db72b46a21570152b2b8920e6526996952abaac1574642d6638c477ba0d8" |
| /baseline/revision | "534e6003534f74761e82de1b8c6061cba89945d1" |
| /baseline/inputs | 6386 |
| /baseline/programFiles | 1638 |
| /baseline/sourceVersion | "baseline" |
| /baseline/currentWorkspaceAssessment | "not-performed" |
| /modelId | "2ba6c772263da8814256efaa5491c69f723d79157a7f8aad7f22d898e297e5cf" |

## item-0 — item-0 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /item/status | "Found" |
| /item/value/id | "order" |
| /item/value/kind | "concept-candidate" |
| /item/value/source/id | "order" |
| /item/value/source/factRefs/0 | "source-V02" |
| /item/value/source/factRefs/1 | "source-V08" |
| /item/value/source/candidateRefs | [] |
| /item/value/source/relatedItems | [] |
| /neighbors/status | "Found" |

## item-1 — item-1 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /item/status | "Found" |
| /item/value/id | "line" |
| /item/value/kind | "concept-candidate" |
| /item/value/source/id | "line" |
| /item/value/source/factRefs/0 | "source-V07" |
| /item/value/source/factRefs/1 | "source-refund-payload" |
| /item/value/source/candidateRefs | [] |
| /item/value/source/relatedItems/0 | "order" |
| /neighbors/status | "Found" |

## item-2 — item-2 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /item/status | "Found" |
| /item/value/id | "payment" |
| /item/value/kind | "concept-candidate" |
| /item/value/source/id | "payment" |
| /item/value/source/factRefs/0 | "source-V03" |
| /item/value/source/factRefs/1 | "source-refund-request" |
| /item/value/source/candidateRefs | [] |
| /item/value/source/relatedItems/0 | "order" |
| /neighbors/status | "Found" |

## item-3 — item-3 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /item/status | "Found" |
| /item/value/id | "cancel-request" |
| /item/value/kind | "concept-candidate" |
| /item/value/source/id | "cancel-request" |
| /item/value/source/factRefs/0 | "source-V06" |
| /item/value/source/factRefs/1 | "source-V08" |
| /item/value/source/factRefs/2 | "source-V09" |
| /item/value/source/candidateRefs | [] |
| /item/value/source/relatedItems/0 | "order" |
| /item/value/source/relatedItems/1 | "line" |
| /neighbors/status | "Found" |

## item-4 — item-4 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /item/status | "Found" |
| /item/value/id | "refund-request" |
| /item/value/kind | "concept-candidate" |
| /item/value/source/id | "refund-request" |
| /item/value/source/factRefs/0 | "source-V11" |
| /item/value/source/factRefs/1 | "source-refund-payload" |
| /item/value/source/factRefs/2 | "source-refund-mutation" |
| /item/value/source/candidateRefs | [] |
| /item/value/source/relatedItems/0 | "payment" |
| /item/value/source/relatedItems/1 | "line" |
| /neighbors/status | "Found" |

## item-5 — item-5 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /item/status | "Found" |
| /item/value/id | "branch" |
| /item/value/kind | "observed-behavior-candidate" |
| /item/value/source/id | "branch" |
| /item/value/source/factRefs/0 | "source-V02" |
| /item/value/source/factRefs/1 | "source-V03" |
| /item/value/source/candidateRefs | [] |
| /item/value/source/relatedItems/0 | "order" |
| /item/value/source/relatedItems/1 | "payment" |
| /neighbors/status | "Found" |

## item-6 — item-6 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /item/status | "Found" |
| /item/value/id | "dialog-submit" |
| /item/value/kind | "relationship-candidate" |
| /item/value/source/id | "dialog-submit" |
| /item/value/source/factRefs/0 | "source-V04" |
| /item/value/source/factRefs/1 | "source-V06" |
| /item/value/source/factRefs/2 | "source-V08" |
| /item/value/source/candidateRefs | [] |
| /item/value/source/relatedItems/0 | "cancel-request" |
| /neighbors/status | "Found" |

## item-7 — item-7 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /item/status | "Found" |
| /item/value/id | "refund-also-cancels" |
| /item/value/kind | "relationship-candidate" |
| /item/value/source/id | "refund-also-cancels" |
| /item/value/source/factRefs/0 | "source-refund-cancel" |
| /item/value/source/factRefs/1 | "source-refund-request" |
| /item/value/source/factRefs/2 | "source-refund-payload" |
| /item/value/source/candidateRefs/0 | "candidate:formal-5" |
| /item/value/source/relatedItems/0 | "cancel-request" |
| /item/value/source/relatedItems/1 | "refund-request" |
| /neighbors/status | "Found" |

## item-8 — item-8 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /item/status | "Found" |
| /item/value/id | "dismiss" |
| /item/value/kind | "observed-behavior-candidate" |
| /item/value/source/id | "dismiss" |
| /item/value/source/factRefs/0 | "source-V10" |
| /item/value/source/factRefs/1 | "source-refund-close" |
| /item/value/source/candidateRefs/0 | "candidate:formal-4" |
| /item/value/source/relatedItems/0 | "cancel-request" |
| /item/value/source/relatedItems/1 | "refund-request" |
| /neighbors/status | "Found" |

## item-9 — item-9 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /item/status | "Found" |
| /item/value/id | "ui-gates" |
| /item/value/kind | "observed-behavior-candidate" |
| /item/value/source/id | "ui-gates" |
| /item/value/source/factRefs/0 | "source-V01" |
| /item/value/source/factRefs/1 | "source-V05" |
| /item/value/source/candidateRefs | [] |
| /item/value/source/relatedItems/0 | "cancel-request" |
| /neighbors/status | "Found" |

## item-10 — item-10 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /item/status | "Found" |
| /item/value/id | "cancel-transport" |
| /item/value/kind | "relationship-candidate" |
| /item/value/source/id | "cancel-transport" |
| /item/value/source/factRefs/0 | "source-V08" |
| /item/value/source/factRefs/1 | "source-V09" |
| /item/value/source/candidateRefs | [] |
| /item/value/source/relatedItems/0 | "cancel-request" |
| /neighbors/status | "Found" |

## item-11 — item-11 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /item/status | "Found" |
| /item/value/id | "refund-transport" |
| /item/value/kind | "relationship-candidate" |
| /item/value/source/id | "refund-transport" |
| /item/value/source/factRefs/0 | "source-refund-mutation" |
| /item/value/source/factRefs/1 | "source-V11" |
| /item/value/source/candidateRefs | [] |
| /item/value/source/relatedItems/0 | "refund-request" |
| /neighbors/status | "Found" |

## fact-0 — fact-0 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-V01" |
| /value/evidence/0/id | "source-V01/e0" |
| /value/evidence/0/file | "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.html" |
| /value/evidence/0/symbol | "*ngIf=\"order.type !== 'Aggregate' && order.nextStates.includes('Cancelled')\"" |
| /value/evidence/0/offset | 2330 |
| /value/evidence/0/end | 2406 |
| /value/evidence/0/line | 51 |
| /value/evidence/0/anchor | "*ngIf=\"order.type !== 'Aggregate' && order.nextStates.includes('Cancelled')\"" |
| /value/evidence/0/sha256 | "fecfd12fc47bb2f2d862b618a73e0c98104b87225436046d96938d3bc3220d89" |
| /value/source/id | "source-V01" |
| /value/source/evidence/file | "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.html" |
| /value/source/evidence/symbol | "*ngIf=\"order.type !== 'Aggregate' && order.nextStates.includes('Cancelled')\"" |
| /value/source/evidence/offset | 2330 |
| /value/source/evidence/line | 51 |
| /value/source/evidence/anchor | "*ngIf=\"order.type !== 'Aggregate' && order.nextStates.includes('Cancelled')\"" |
| /value/source/evidence/sha256 | "fecfd12fc47bb2f2d862b618a73e0c98104b87225436046d96938d3bc3220d89" |

## fact-1 — fact-1 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-V02" |
| /value/evidence/0/id | "source-V02/e0" |
| /value/evidence/0/file | "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts" |
| /value/evidence/0/symbol | "cancelOrRefund(order: OrderDetailFragment) {" |
| /value/evidence/0/offset | 18542 |
| /value/evidence/0/end | 18586 |
| /value/evidence/0/line | 466 |
| /value/evidence/0/anchor | "cancelOrRefund(order: OrderDetailFragment) {" |
| /value/evidence/0/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |
| /value/source/id | "source-V02" |
| /value/source/evidence/file | "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts" |
| /value/source/evidence/symbol | "cancelOrRefund(order: OrderDetailFragment) {" |
| /value/source/evidence/offset | 18542 |
| /value/source/evidence/line | 466 |
| /value/source/evidence/anchor | "cancelOrRefund(order: OrderDetailFragment) {" |
| /value/source/evidence/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |

## fact-2 — fact-2 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-V03" |
| /value/evidence/0/id | "source-V03/e0" |
| /value/evidence/0/file | "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts" |
| /value/evidence/0/symbol | "orderHasSettledPayments(order: OrderDetailFragment): boolean {" |
| /value/evidence/0/offset | 22238 |
| /value/evidence/0/end | 22300 |
| /value/evidence/0/line | 572 |
| /value/evidence/0/anchor | "orderHasSettledPayments(order: OrderDetailFragment): boolean {" |
| /value/evidence/0/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |
| /value/source/id | "source-V03" |
| /value/source/evidence/file | "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts" |
| /value/source/evidence/symbol | "orderHasSettledPayments(order: OrderDetailFragment): boolean {" |
| /value/source/evidence/offset | 22238 |
| /value/source/evidence/line | 572 |
| /value/source/evidence/anchor | "orderHasSettledPayments(order: OrderDetailFragment): boolean {" |
| /value/source/evidence/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |

## fact-3 — fact-3 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-V04" |
| /value/evidence/0/id | "source-V04/e0" |
| /value/evidence/0/file | "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts" |
| /value/evidence/0/symbol | "private cancelOrder(order: OrderDetailFragment) {" |
| /value/evidence/0/offset | 22379 |
| /value/evidence/0/end | 22428 |
| /value/evidence/0/line | 576 |
| /value/evidence/0/anchor | "private cancelOrder(order: OrderDetailFragment) {" |
| /value/evidence/0/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |
| /value/source/id | "source-V04" |
| /value/source/evidence/file | "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts" |
| /value/source/evidence/symbol | "private cancelOrder(order: OrderDetailFragment) {" |
| /value/source/evidence/offset | 22379 |
| /value/source/evidence/line | 576 |
| /value/source/evidence/anchor | "private cancelOrder(order: OrderDetailFragment) {" |
| /value/source/evidence/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |

## fact-4 — fact-4 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-V05" |
| /value/evidence/0/id | "source-V05/e0" |
| /value/evidence/0/file | "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.html" |
| /value/evidence/0/symbol | "[disabled]=\"!reason &#124;&#124; (!order.active && selectionCount === 0)\"" |
| /value/evidence/0/offset | 3463 |
| /value/evidence/0/end | 3526 |
| /value/evidence/0/line | 88 |
| /value/evidence/0/anchor | "[disabled]=\"!reason &#124;&#124; (!order.active && selectionCount === 0)\"" |
| /value/evidence/0/sha256 | "308499c673a3cf4fc514210e6ab9aef74e8b89c877cea72d25b371db5fa97dc3" |
| /value/source/id | "source-V05" |
| /value/source/evidence/file | "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.html" |
| /value/source/evidence/symbol | "[disabled]=\"!reason &#124;&#124; (!order.active && selectionCount === 0)\"" |
| /value/source/evidence/offset | 3463 |
| /value/source/evidence/line | 88 |
| /value/source/evidence/anchor | "[disabled]=\"!reason &#124;&#124; (!order.active && selectionCount === 0)\"" |
| /value/source/evidence/sha256 | "308499c673a3cf4fc514210e6ab9aef74e8b89c877cea72d25b371db5fa97dc3" |

## fact-5 — fact-5 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-V06" |
| /value/evidence/0/id | "source-V06/e0" |
| /value/evidence/0/file | "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts" |
| /value/evidence/0/symbol | "select() {" |
| /value/evidence/0/offset | 2254 |
| /value/evidence/0/end | 2264 |
| /value/evidence/0/line | 69 |
| /value/evidence/0/anchor | "select() {" |
| /value/evidence/0/sha256 | "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5" |
| /value/source/id | "source-V06" |
| /value/source/evidence/file | "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts" |
| /value/source/evidence/symbol | "select() {" |
| /value/source/evidence/offset | 2254 |
| /value/source/evidence/line | 69 |
| /value/source/evidence/anchor | "select() {" |
| /value/source/evidence/sha256 | "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5" |

## fact-6 — fact-6 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-V07" |
| /value/evidence/0/id | "source-V07/e0" |
| /value/evidence/0/file | "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts" |
| /value/evidence/0/symbol | "private getLineInputs(): OrderLineInput[] &#124; undefined {" |
| /value/evidence/0/offset | 2519 |
| /value/evidence/0/end | 2574 |
| /value/evidence/0/line | 82 |
| /value/evidence/0/anchor | "private getLineInputs(): OrderLineInput[] &#124; undefined {" |
| /value/evidence/0/sha256 | "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5" |
| /value/source/id | "source-V07" |
| /value/source/evidence/file | "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts" |
| /value/source/evidence/symbol | "private getLineInputs(): OrderLineInput[] &#124; undefined {" |
| /value/source/evidence/offset | 2519 |
| /value/source/evidence/line | 82 |
| /value/source/evidence/anchor | "private getLineInputs(): OrderLineInput[] &#124; undefined {" |
| /value/source/evidence/sha256 | "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5" |

## fact-7 — fact-7 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-V08" |
| /value/evidence/0/id | "source-V08/e0" |
| /value/evidence/0/file | "packages/admin-ui/src/lib/core/src/data/providers/order-data.service.ts" |
| /value/evidence/0/symbol | "cancelOrder(input: Codegen.CancelOrderInput) {" |
| /value/evidence/0/offset | 3319 |
| /value/evidence/0/end | 3365 |
| /value/evidence/0/line | 114 |
| /value/evidence/0/anchor | "cancelOrder(input: Codegen.CancelOrderInput) {" |
| /value/evidence/0/sha256 | "27ddd40b2430caebc5f0defc901d1e42aa54f1cb29038fe4e7657a2448c03811" |
| /value/source/id | "source-V08" |
| /value/source/evidence/file | "packages/admin-ui/src/lib/core/src/data/providers/order-data.service.ts" |
| /value/source/evidence/symbol | "cancelOrder(input: Codegen.CancelOrderInput) {" |
| /value/source/evidence/offset | 3319 |
| /value/source/evidence/line | 114 |
| /value/source/evidence/anchor | "cancelOrder(input: Codegen.CancelOrderInput) {" |
| /value/source/evidence/sha256 | "27ddd40b2430caebc5f0defc901d1e42aa54f1cb29038fe4e7657a2448c03811" |

## fact-8 — fact-8 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-V09" |
| /value/evidence/0/id | "source-V09/e0" |
| /value/evidence/0/file | "packages/admin-ui/src/lib/core/src/data/definitions/order-definitions.ts" |
| /value/evidence/0/symbol | "mutation CancelOrder($input: CancelOrderInput!) {" |
| /value/evidence/0/offset | 7598 |
| /value/evidence/0/end | 7647 |
| /value/evidence/0/line | 373 |
| /value/evidence/0/anchor | "mutation CancelOrder($input: CancelOrderInput!) {" |
| /value/evidence/0/sha256 | "26a6b81368d53a731b2847e0587eeb94463ec706bb8df73bee13d304fb770701" |
| /value/source/id | "source-V09" |
| /value/source/evidence/file | "packages/admin-ui/src/lib/core/src/data/definitions/order-definitions.ts" |
| /value/source/evidence/symbol | "mutation CancelOrder($input: CancelOrderInput!) {" |
| /value/source/evidence/offset | 7598 |
| /value/source/evidence/line | 373 |
| /value/source/evidence/anchor | "mutation CancelOrder($input: CancelOrderInput!) {" |
| /value/source/evidence/sha256 | "26a6b81368d53a731b2847e0587eeb94463ec706bb8df73bee13d304fb770701" |

## fact-9 — fact-9 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-V10" |
| /value/evidence/0/id | "source-V10/e0" |
| /value/evidence/0/file | "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts" |
| /value/evidence/0/symbol | "cancel() {" |
| /value/evidence/0/offset | 2469 |
| /value/evidence/0/end | 2479 |
| /value/evidence/0/line | 78 |
| /value/evidence/0/anchor | "cancel() {" |
| /value/evidence/0/sha256 | "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5" |
| /value/source/id | "source-V10" |
| /value/source/evidence/file | "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts" |
| /value/source/evidence/symbol | "cancel() {" |
| /value/source/evidence/offset | 2469 |
| /value/source/evidence/line | 78 |
| /value/source/evidence/anchor | "cancel() {" |
| /value/source/evidence/sha256 | "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5" |

## fact-10 — fact-10 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-V11" |
| /value/evidence/0/id | "source-V11/e0" |
| /value/evidence/0/file | "packages/admin-ui/src/lib/core/src/data/definitions/order-definitions.ts" |
| /value/evidence/0/symbol | "mutation RefundOrder($input: RefundOrderInput!) {" |
| /value/evidence/0/offset | 7854 |
| /value/evidence/0/end | 7903 |
| /value/evidence/0/line | 384 |
| /value/evidence/0/anchor | "mutation RefundOrder($input: RefundOrderInput!) {" |
| /value/evidence/0/sha256 | "26a6b81368d53a731b2847e0587eeb94463ec706bb8df73bee13d304fb770701" |
| /value/source/id | "source-V11" |
| /value/source/evidence/file | "packages/admin-ui/src/lib/core/src/data/definitions/order-definitions.ts" |
| /value/source/evidence/symbol | "mutation RefundOrder($input: RefundOrderInput!) {" |
| /value/source/evidence/offset | 7854 |
| /value/source/evidence/line | 384 |
| /value/source/evidence/anchor | "mutation RefundOrder($input: RefundOrderInput!) {" |
| /value/source/evidence/sha256 | "26a6b81368d53a731b2847e0587eeb94463ec706bb8df73bee13d304fb770701" |

## fact-11 — fact-11 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-refund-cancel" |
| /value/evidence/0/id | "source-refund-cancel/e0" |
| /value/evidence/0/file | "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts" |
| /value/evidence/0/symbol | "refund-cancel" |
| /value/evidence/0/offset | 23612 |
| /value/evidence/0/end | 23645 |
| /value/evidence/0/line | 615 |
| /value/evidence/0/anchor | "if (input.cancel.lines?.length) {" |
| /value/evidence/0/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |
| /value/source/id | "source-refund-cancel" |
| /value/source/evidence/file | "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts" |
| /value/source/evidence/symbol | "refund-cancel" |
| /value/source/evidence/offset | 23612 |
| /value/source/evidence/line | 615 |
| /value/source/evidence/anchor | "if (input.cancel.lines?.length) {" |
| /value/source/evidence/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |

## fact-12 — fact-12 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-refund-request" |
| /value/evidence/0/id | "source-refund-request/e0" |
| /value/evidence/0/file | "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts" |
| /value/evidence/0/symbol | "refund-request" |
| /value/evidence/0/offset | 25321 |
| /value/evidence/0/end | 25348 |
| /value/evidence/0/line | 647 |
| /value/evidence/0/anchor | "if (input.refunds.length) {" |
| /value/evidence/0/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |
| /value/source/id | "source-refund-request" |
| /value/source/evidence/file | "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts" |
| /value/source/evidence/symbol | "refund-request" |
| /value/source/evidence/offset | 25321 |
| /value/source/evidence/line | 647 |
| /value/source/evidence/anchor | "if (input.refunds.length) {" |
| /value/source/evidence/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |

## fact-13 — fact-13 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-refund-payload" |
| /value/evidence/0/id | "source-refund-payload/e0" |
| /value/evidence/0/file | "packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts" |
| /value/evidence/0/symbol | "refund-payload" |
| /value/evidence/0/offset | 7259 |
| /value/evidence/0/end | 7304 |
| /value/evidence/0/line | 196 |
| /value/evidence/0/anchor | "cancel: {\n                lines: cancelLines," |
| /value/evidence/0/sha256 | "d9ea112f17bff650686842306bef46fa6f7564278b1166762a7c9b7a8473a6fb" |
| /value/source/id | "source-refund-payload" |
| /value/source/evidence/file | "packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts" |
| /value/source/evidence/symbol | "refund-payload" |
| /value/source/evidence/offset | 7259 |
| /value/source/evidence/line | 196 |
| /value/source/evidence/anchor | "cancel: {\n                lines: cancelLines," |
| /value/source/evidence/sha256 | "d9ea112f17bff650686842306bef46fa6f7564278b1166762a7c9b7a8473a6fb" |

## fact-14 — fact-14 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-refund-close" |
| /value/evidence/0/id | "source-refund-close/e0" |
| /value/evidence/0/file | "packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts" |
| /value/evidence/0/symbol | "refund-close" |
| /value/evidence/0/offset | 7491 |
| /value/evidence/0/end | 7529 |
| /value/evidence/0/line | 205 |
| /value/evidence/0/anchor | "cancel() {\n        this.resolveWith();" |
| /value/evidence/0/sha256 | "d9ea112f17bff650686842306bef46fa6f7564278b1166762a7c9b7a8473a6fb" |
| /value/source/id | "source-refund-close" |
| /value/source/evidence/file | "packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts" |
| /value/source/evidence/symbol | "refund-close" |
| /value/source/evidence/offset | 7491 |
| /value/source/evidence/line | 205 |
| /value/source/evidence/anchor | "cancel() {\n        this.resolveWith();" |
| /value/source/evidence/sha256 | "d9ea112f17bff650686842306bef46fa6f7564278b1166762a7c9b7a8473a6fb" |

## fact-15 — fact-15 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-refund-mutation" |
| /value/evidence/0/id | "source-refund-mutation/e0" |
| /value/evidence/0/file | "packages/admin-ui/src/lib/core/src/data/providers/order-data.service.ts" |
| /value/evidence/0/symbol | "refund-mutation" |
| /value/evidence/0/offset | 3577 |
| /value/evidence/0/end | 3623 |
| /value/evidence/0/line | 123 |
| /value/evidence/0/anchor | "refundOrder(input: Codegen.RefundOrderInput) {" |
| /value/evidence/0/sha256 | "27ddd40b2430caebc5f0defc901d1e42aa54f1cb29038fe4e7657a2448c03811" |
| /value/source/id | "source-refund-mutation" |
| /value/source/evidence/file | "packages/admin-ui/src/lib/core/src/data/providers/order-data.service.ts" |
| /value/source/evidence/symbol | "refund-mutation" |
| /value/source/evidence/offset | 3577 |
| /value/source/evidence/line | 123 |
| /value/source/evidence/anchor | "refundOrder(input: Codegen.RefundOrderInput) {" |
| /value/source/evidence/sha256 | "27ddd40b2430caebc5f0defc901d1e42aa54f1cb29038fe4e7657a2448c03811" |

## fact-16 — fact-16 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379:calls-cancel" |
| /value/evidence/0/id | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379:calls-cancel/e0" |
| /value/evidence/0/file | "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts" |
| /value/evidence/0/symbol | "CallExpression" |
| /value/evidence/0/offset | 22747 |
| /value/evidence/0/end | 22788 |
| /value/evidence/0/line | 587 |
| /value/evidence/0/anchor | "this.dataService.order.cancelOrder(input)" |
| /value/evidence/0/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |
| /value/source/id | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379:calls-cancel" |
| /value/source/evidence/0/file | "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts" |
| /value/source/evidence/0/symbol | "CallExpression" |
| /value/source/evidence/0/offset | 22747 |
| /value/source/evidence/0/end | 22788 |
| /value/source/evidence/0/line | 587 |
| /value/source/evidence/0/anchor | "this.dataService.order.cancelOrder(input)" |
| /value/source/evidence/0/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |

## fact-17 — fact-17 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379:opens-modal" |
| /value/evidence/0/id | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379:opens-modal/e0" |
| /value/evidence/0/file | "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts" |
| /value/evidence/0/symbol | "CallExpression" |
| /value/evidence/0/offset | 22437 |
| /value/evidence/0/end | 22626 |
| /value/evidence/0/line | 577 |
| /value/evidence/0/anchor | "this.modalService\n            .fromComponent(CancelOrderDialogComponent, {\n                size: 'xl',\n                locals: {\n                    order,\n                },\n            })" |
| /value/evidence/0/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |
| /value/source/id | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379:opens-modal" |
| /value/source/evidence/0/file | "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts" |
| /value/source/evidence/0/symbol | "CallExpression" |
| /value/source/evidence/0/offset | 22437 |
| /value/source/evidence/0/end | 22626 |
| /value/source/evidence/0/line | 577 |
| /value/source/evidence/0/anchor | "this.modalService\n            .fromComponent(CancelOrderDialogComponent, {\n                size: 'xl',\n                locals: {\n                    order,\n                },\n            })" |
| /value/source/evidence/0/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |

## fact-18 — fact-18 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:23185:calls-cancel" |
| /value/evidence/0/id | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:23185:calls-cancel/e0" |
| /value/evidence/0/file | "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts" |
| /value/evidence/0/symbol | "CallExpression" |
| /value/evidence/0/offset | 23677 |
| /value/evidence/0/end | 23725 |
| /value/evidence/0/line | 616 |
| /value/evidence/0/anchor | "this.dataService.order.cancelOrder(input.cancel)" |
| /value/evidence/0/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |
| /value/source/id | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:23185:calls-cancel" |
| /value/source/evidence/0/file | "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts" |
| /value/source/evidence/0/symbol | "CallExpression" |
| /value/source/evidence/0/offset | 23677 |
| /value/source/evidence/0/end | 23725 |
| /value/source/evidence/0/line | 616 |
| /value/source/evidence/0/anchor | "this.dataService.order.cancelOrder(input.cancel)" |
| /value/source/evidence/0/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |

## fact-19 — fact-19 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:23185:opens-modal" |
| /value/evidence/0/id | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:23185:opens-modal/e0" |
| /value/evidence/0/file | "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts" |
| /value/evidence/0/symbol | "CallExpression" |
| /value/evidence/0/offset | 23243 |
| /value/evidence/0/end | 23432 |
| /value/evidence/0/line | 602 |
| /value/evidence/0/anchor | "this.modalService\n            .fromComponent(RefundOrderDialogComponent, {\n                size: 'xl',\n                locals: {\n                    order,\n                },\n            })" |
| /value/evidence/0/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |
| /value/source/id | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:23185:opens-modal" |
| /value/source/evidence/0/file | "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts" |
| /value/source/evidence/0/symbol | "CallExpression" |
| /value/source/evidence/0/offset | 23243 |
| /value/source/evidence/0/end | 23432 |
| /value/source/evidence/0/line | 602 |
| /value/source/evidence/0/anchor | "this.modalService\n            .fromComponent(RefundOrderDialogComponent, {\n                size: 'xl',\n                locals: {\n                    order,\n                },\n            })" |
| /value/source/evidence/0/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |

## fact-20 — fact-20 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts:2469:closes-dialog-empty" |
| /value/evidence/0/id | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts:2469:closes-dialog-empty/e0" |
| /value/evidence/0/file | "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts" |
| /value/evidence/0/symbol | "CallExpression" |
| /value/evidence/0/offset | 2488 |
| /value/evidence/0/end | 2506 |
| /value/evidence/0/line | 79 |
| /value/evidence/0/anchor | "this.resolveWith()" |
| /value/evidence/0/sha256 | "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5" |
| /value/source/id | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts:2469:closes-dialog-empty" |
| /value/source/evidence/0/file | "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts" |
| /value/source/evidence/0/symbol | "CallExpression" |
| /value/source/evidence/0/offset | 2488 |
| /value/source/evidence/0/end | 2506 |
| /value/source/evidence/0/line | 79 |
| /value/source/evidence/0/anchor | "this.resolveWith()" |
| /value/source/evidence/0/sha256 | "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5" |

## fact-21 — fact-21 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts:7491:closes-dialog-empty" |
| /value/evidence/0/id | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts:7491:closes-dialog-empty/e0" |
| /value/evidence/0/file | "packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts" |
| /value/evidence/0/symbol | "CallExpression" |
| /value/evidence/0/offset | 7510 |
| /value/evidence/0/end | 7528 |
| /value/evidence/0/line | 206 |
| /value/evidence/0/anchor | "this.resolveWith()" |
| /value/evidence/0/sha256 | "d9ea112f17bff650686842306bef46fa6f7564278b1166762a7c9b7a8473a6fb" |
| /value/source/id | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts:7491:closes-dialog-empty" |
| /value/source/evidence/0/file | "packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts" |
| /value/source/evidence/0/symbol | "CallExpression" |
| /value/source/evidence/0/offset | 7510 |
| /value/source/evidence/0/end | 7528 |
| /value/source/evidence/0/line | 206 |
| /value/source/evidence/0/anchor | "this.resolveWith()" |
| /value/source/evidence/0/sha256 | "d9ea112f17bff650686842306bef46fa6f7564278b1166762a7c9b7a8473a6fb" |

## candidate-0 — candidate-0 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /candidate/status | "Found" |
| /candidate/value/id | "candidate:formal-4" |
| /candidate/value/factRefs/0 | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts:2469:closes-dialog-empty" |
| /candidate/value/factRefs/1 | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts:7491:closes-dialog-empty" |
| /candidate/value/source/id | "candidate:formal-4" |
| /candidate/value/source/extent/0 | "534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts:2469" |
| /candidate/value/source/extent/1 | "534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts:7491" |
| /candidate/value/source/intent/0 | "closes-dialog-empty" |
| /candidate/value/source/factRefs/0 | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts:2469:closes-dialog-empty" |
| /candidate/value/source/factRefs/1 | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts:7491:closes-dialog-empty" |
| /objects/0/id | "534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379" |
| /objects/0/class | "OrderDetailComponent" |
| /objects/0/name | "cancelOrder" |
| /objects/0/evidence/file | "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts" |
| /objects/0/evidence/symbol | "cancelOrder" |
| /objects/0/evidence/offset | 22379 |
| /objects/0/evidence/end | 23179 |
| /objects/0/evidence/line | 576 |
| /objects/0/evidence/anchor | "private cancelOrder(order: OrderDetailFragment) {" |
| /objects/0/evidence/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |
| /objects/1/id | "534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:23185" |
| /objects/1/class | "OrderDetailComponent" |
| /objects/1/name | "refundOrder" |
| /objects/1/evidence/file | "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts" |
| /objects/1/evidence/symbol | "refundOrder" |
| /objects/1/evidence/offset | 23185 |
| /objects/1/evidence/end | 26909 |
| /objects/1/evidence/line | 601 |
| /objects/1/evidence/anchor | "private refundOrder(order: OrderDetailFragment) {" |
| /objects/1/evidence/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |
| /objects/2/id | "534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts:2469" |
| /objects/2/class | "CancelOrderDialogComponent" |
| /objects/2/name | "cancel" |
| /objects/2/evidence/file | "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts" |
| /objects/2/evidence/symbol | "cancel" |
| /objects/2/evidence/offset | 2469 |
| /objects/2/evidence/end | 2513 |
| /objects/2/evidence/line | 78 |
| /objects/2/evidence/anchor | "cancel() {" |
| /objects/2/evidence/sha256 | "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5" |
| /objects/3/id | "534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts:7491" |
| /objects/3/class | "RefundOrderDialogComponent" |
| /objects/3/name | "cancel" |
| /objects/3/evidence/file | "packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts" |
| /objects/3/evidence/symbol | "cancel" |
| /objects/3/evidence/offset | 7491 |
| /objects/3/evidence/end | 7535 |
| /objects/3/evidence/line | 205 |
| /objects/3/evidence/anchor | "cancel() {" |
| /objects/3/evidence/sha256 | "d9ea112f17bff650686842306bef46fa6f7564278b1166762a7c9b7a8473a6fb" |
| /attributes/0/id | "calls-cancel" |
| /attributes/0/declarations/0/file | "packages/admin-ui/src/lib/core/src/data/providers/order-data.service.ts" |
| /attributes/0/declarations/0/symbol | "cancelOrder" |
| /attributes/0/declarations/0/offset | 3319 |
| /attributes/0/declarations/0/end | 3571 |
| /attributes/0/declarations/0/line | 114 |
| /attributes/0/declarations/0/anchor | "cancelOrder(input: Codegen.CancelOrderInput) {\n        return this.baseDataService.mutate&lt;Codegen.CancelOrderMutation, Codegen.CancelOrderMutationVariables&gt;(\n            CANCEL_ORDER,\n            {\n                input,\n            },\n        );\n    }" |
| /attributes/0/declarations/0/sha256 | "27ddd40b2430caebc5f0defc901d1e42aa54f1cb29038fe4e7657a2448c03811" |
| /attributes/1/id | "opens-modal" |
| /attributes/1/declarations/0/file | "packages/admin-ui/src/lib/core/src/providers/modal/modal.service.ts" |
| /attributes/1/declarations/0/symbol | "fromComponent" |
| /attributes/1/declarations/0/offset | 1985 |
| /attributes/1/declarations/0/end | 2882 |
| /attributes/1/declarations/0/line | 68 |
| /attributes/1/declarations/0/anchor | "fromComponent&lt;T extends Dialog&lt;any&gt;, R&gt;(\n        component: Type&lt;T&gt; & Type&lt;Dialog&lt;R&gt;&gt;,\n        options?: ModalOptions&lt;T&gt;,\n    ): Observable&lt;R &#124; undefined&gt; {\n        return from(this.overlayHostService.getHostView()).pipe(\n            mergeMap(hostView =&gt; {\n                const modalComponentRef = hostView.createComponent(ModalDialogComponent);\n                const modalInstance: ModalDialogComponent&lt;any&gt; = modalComponentRef.instance;\n                modalInstance.childComponentType = component;\n                modalInstance.options = options;\n\n                return new Observable&lt;R&gt;(subscriber =&gt; {\n                    modalInstance.closeModal = (result: R) =&gt; {\n                        modalComponentRef.destroy();\n                        subscriber.next(result);\n                        subscriber.complete();\n                    };\n                });\n            }),\n        );\n    }" |
| /attributes/1/declarations/0/sha256 | "d4096905f43f3134d12aa2567a2a0a6d1deb25b985222de877d7057fc336f365" |
| /attributes/2/id | "closes-dialog-empty" |
| /attributes/2/declarations/0/file | "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts" |
| /attributes/2/declarations/0/symbol | "resolveWith" |
| /attributes/2/declarations/0/offset | 695 |
| /attributes/2/declarations/0/end | 744 |
| /attributes/2/declarations/0/line | 22 |
| /attributes/2/declarations/0/anchor | "resolveWith: (result?: CancelOrderInput) =&gt; void;" |
| /attributes/2/declarations/0/sha256 | "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5" |
| /attributes/2/declarations/1/file | "packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts" |
| /attributes/2/declarations/1/symbol | "resolveWith" |
| /attributes/2/declarations/1/offset | 1047 |
| /attributes/2/declarations/1/end | 1137 |
| /attributes/2/declarations/1/line | 30 |
| /attributes/2/declarations/1/anchor | "resolveWith: (result?: { cancel: CancelOrderInput; refunds: RefundOrderInput[] }) =&gt; void;" |
| /attributes/2/declarations/1/sha256 | "d9ea112f17bff650686842306bef46fa6f7564278b1166762a7c9b7a8473a6fb" |

## candidate-1 — candidate-1 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /candidate/status | "Found" |
| /candidate/value/id | "candidate:formal-5" |
| /candidate/value/factRefs/0 | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379:calls-cancel" |
| /candidate/value/factRefs/1 | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379:opens-modal" |
| /candidate/value/factRefs/2 | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:23185:calls-cancel" |
| /candidate/value/factRefs/3 | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:23185:opens-modal" |
| /candidate/value/source/id | "candidate:formal-5" |
| /candidate/value/source/extent/0 | "534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379" |
| /candidate/value/source/extent/1 | "534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:23185" |
| /candidate/value/source/intent/0 | "calls-cancel" |
| /candidate/value/source/intent/1 | "opens-modal" |
| /candidate/value/source/factRefs/0 | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379:calls-cancel" |
| /candidate/value/source/factRefs/1 | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379:opens-modal" |
| /candidate/value/source/factRefs/2 | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:23185:calls-cancel" |
| /candidate/value/source/factRefs/3 | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:23185:opens-modal" |
| /objects/0/id | "534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379" |
| /objects/0/class | "OrderDetailComponent" |
| /objects/0/name | "cancelOrder" |
| /objects/0/evidence/file | "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts" |
| /objects/0/evidence/symbol | "cancelOrder" |
| /objects/0/evidence/offset | 22379 |
| /objects/0/evidence/end | 23179 |
| /objects/0/evidence/line | 576 |
| /objects/0/evidence/anchor | "private cancelOrder(order: OrderDetailFragment) {" |
| /objects/0/evidence/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |
| /objects/1/id | "534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:23185" |
| /objects/1/class | "OrderDetailComponent" |
| /objects/1/name | "refundOrder" |
| /objects/1/evidence/file | "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts" |
| /objects/1/evidence/symbol | "refundOrder" |
| /objects/1/evidence/offset | 23185 |
| /objects/1/evidence/end | 26909 |
| /objects/1/evidence/line | 601 |
| /objects/1/evidence/anchor | "private refundOrder(order: OrderDetailFragment) {" |
| /objects/1/evidence/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |
| /objects/2/id | "534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts:2469" |
| /objects/2/class | "CancelOrderDialogComponent" |
| /objects/2/name | "cancel" |
| /objects/2/evidence/file | "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts" |
| /objects/2/evidence/symbol | "cancel" |
| /objects/2/evidence/offset | 2469 |
| /objects/2/evidence/end | 2513 |
| /objects/2/evidence/line | 78 |
| /objects/2/evidence/anchor | "cancel() {" |
| /objects/2/evidence/sha256 | "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5" |
| /objects/3/id | "534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts:7491" |
| /objects/3/class | "RefundOrderDialogComponent" |
| /objects/3/name | "cancel" |
| /objects/3/evidence/file | "packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts" |
| /objects/3/evidence/symbol | "cancel" |
| /objects/3/evidence/offset | 7491 |
| /objects/3/evidence/end | 7535 |
| /objects/3/evidence/line | 205 |
| /objects/3/evidence/anchor | "cancel() {" |
| /objects/3/evidence/sha256 | "d9ea112f17bff650686842306bef46fa6f7564278b1166762a7c9b7a8473a6fb" |
| /attributes/0/id | "calls-cancel" |
| /attributes/0/declarations/0/file | "packages/admin-ui/src/lib/core/src/data/providers/order-data.service.ts" |
| /attributes/0/declarations/0/symbol | "cancelOrder" |
| /attributes/0/declarations/0/offset | 3319 |
| /attributes/0/declarations/0/end | 3571 |
| /attributes/0/declarations/0/line | 114 |
| /attributes/0/declarations/0/anchor | "cancelOrder(input: Codegen.CancelOrderInput) {\n        return this.baseDataService.mutate&lt;Codegen.CancelOrderMutation, Codegen.CancelOrderMutationVariables&gt;(\n            CANCEL_ORDER,\n            {\n                input,\n            },\n        );\n    }" |
| /attributes/0/declarations/0/sha256 | "27ddd40b2430caebc5f0defc901d1e42aa54f1cb29038fe4e7657a2448c03811" |
| /attributes/1/id | "opens-modal" |
| /attributes/1/declarations/0/file | "packages/admin-ui/src/lib/core/src/providers/modal/modal.service.ts" |
| /attributes/1/declarations/0/symbol | "fromComponent" |
| /attributes/1/declarations/0/offset | 1985 |
| /attributes/1/declarations/0/end | 2882 |
| /attributes/1/declarations/0/line | 68 |
| /attributes/1/declarations/0/anchor | "fromComponent&lt;T extends Dialog&lt;any&gt;, R&gt;(\n        component: Type&lt;T&gt; & Type&lt;Dialog&lt;R&gt;&gt;,\n        options?: ModalOptions&lt;T&gt;,\n    ): Observable&lt;R &#124; undefined&gt; {\n        return from(this.overlayHostService.getHostView()).pipe(\n            mergeMap(hostView =&gt; {\n                const modalComponentRef = hostView.createComponent(ModalDialogComponent);\n                const modalInstance: ModalDialogComponent&lt;any&gt; = modalComponentRef.instance;\n                modalInstance.childComponentType = component;\n                modalInstance.options = options;\n\n                return new Observable&lt;R&gt;(subscriber =&gt; {\n                    modalInstance.closeModal = (result: R) =&gt; {\n                        modalComponentRef.destroy();\n                        subscriber.next(result);\n                        subscriber.complete();\n                    };\n                });\n            }),\n        );\n    }" |
| /attributes/1/declarations/0/sha256 | "d4096905f43f3134d12aa2567a2a0a6d1deb25b985222de877d7057fc336f365" |
| /attributes/2/id | "closes-dialog-empty" |
| /attributes/2/declarations/0/file | "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts" |
| /attributes/2/declarations/0/symbol | "resolveWith" |
| /attributes/2/declarations/0/offset | 695 |
| /attributes/2/declarations/0/end | 744 |
| /attributes/2/declarations/0/line | 22 |
| /attributes/2/declarations/0/anchor | "resolveWith: (result?: CancelOrderInput) =&gt; void;" |
| /attributes/2/declarations/0/sha256 | "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5" |
| /attributes/2/declarations/1/file | "packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts" |
| /attributes/2/declarations/1/symbol | "resolveWith" |
| /attributes/2/declarations/1/offset | 1047 |
| /attributes/2/declarations/1/end | 1137 |
| /attributes/2/declarations/1/line | 30 |
| /attributes/2/declarations/1/anchor | "resolveWith: (result?: { cancel: CancelOrderInput; refunds: RefundOrderInput[] }) =&gt; void;" |
| /attributes/2/declarations/1/sha256 | "d9ea112f17bff650686842306bef46fa6f7564278b1166762a7c9b7a8473a6fb" |

## evidence-0 — source-V01/e0

원문 "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.html", 51행 21열, UTF-16 구간 [2330, 2406)의 "baseline" 인용:

~~~text
*ngIf="order.type !== 'Aggregate' && order.nextStates.includes('Cancelled')"
~~~


## evidence-0 — evidence-0 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-V01/e0" |
| /value/symbol | "*ngIf=\"order.type !== 'Aggregate' && order.nextStates.includes('Cancelled')\"" |
| /value/anchor | "*ngIf=\"order.type !== 'Aggregate' && order.nextStates.includes('Cancelled')\"" |
| /value/sha256 | "fecfd12fc47bb2f2d862b618a73e0c98104b87225436046d96938d3bc3220d89" |

## evidence-1 — source-V02/e0

원문 "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts", 466행 5열, UTF-16 구간 [18542, 18586)의 "baseline" 인용:

~~~text
cancelOrRefund(order: OrderDetailFragment) {
~~~


## evidence-1 — evidence-1 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-V02/e0" |
| /value/symbol | "cancelOrRefund(order: OrderDetailFragment) {" |
| /value/anchor | "cancelOrRefund(order: OrderDetailFragment) {" |
| /value/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |

## evidence-2 — source-V03/e0

원문 "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts", 572행 5열, UTF-16 구간 [22238, 22300)의 "baseline" 인용:

~~~text
orderHasSettledPayments(order: OrderDetailFragment): boolean {
~~~


## evidence-2 — evidence-2 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-V03/e0" |
| /value/symbol | "orderHasSettledPayments(order: OrderDetailFragment): boolean {" |
| /value/anchor | "orderHasSettledPayments(order: OrderDetailFragment): boolean {" |
| /value/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |

## evidence-3 — source-V04/e0

원문 "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts", 576행 5열, UTF-16 구간 [22379, 22428)의 "baseline" 인용:

~~~text
private cancelOrder(order: OrderDetailFragment) {
~~~


## evidence-3 — evidence-3 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-V04/e0" |
| /value/symbol | "private cancelOrder(order: OrderDetailFragment) {" |
| /value/anchor | "private cancelOrder(order: OrderDetailFragment) {" |
| /value/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |

## evidence-4 — source-V05/e0

원문 "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.html", 88행 9열, UTF-16 구간 [3463, 3526)의 "baseline" 인용:

~~~text
[disabled]="!reason || (!order.active && selectionCount === 0)"
~~~


## evidence-4 — evidence-4 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-V05/e0" |
| /value/symbol | "[disabled]=\"!reason &#124;&#124; (!order.active && selectionCount === 0)\"" |
| /value/anchor | "[disabled]=\"!reason &#124;&#124; (!order.active && selectionCount === 0)\"" |
| /value/sha256 | "308499c673a3cf4fc514210e6ab9aef74e8b89c877cea72d25b371db5fa97dc3" |

## evidence-5 — source-V06/e0

원문 "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts", 69행 5열, UTF-16 구간 [2254, 2264)의 "baseline" 인용:

~~~text
select() {
~~~


## evidence-5 — evidence-5 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-V06/e0" |
| /value/symbol | "select() {" |
| /value/anchor | "select() {" |
| /value/sha256 | "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5" |

## evidence-6 — source-V07/e0

원문 "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts", 82행 5열, UTF-16 구간 [2519, 2574)의 "baseline" 인용:

~~~text
private getLineInputs(): OrderLineInput[] | undefined {
~~~


## evidence-6 — evidence-6 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-V07/e0" |
| /value/symbol | "private getLineInputs(): OrderLineInput[] &#124; undefined {" |
| /value/anchor | "private getLineInputs(): OrderLineInput[] &#124; undefined {" |
| /value/sha256 | "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5" |

## evidence-7 — source-V08/e0

원문 "packages/admin-ui/src/lib/core/src/data/providers/order-data.service.ts", 114행 5열, UTF-16 구간 [3319, 3365)의 "baseline" 인용:

~~~text
cancelOrder(input: Codegen.CancelOrderInput) {
~~~


## evidence-7 — evidence-7 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-V08/e0" |
| /value/symbol | "cancelOrder(input: Codegen.CancelOrderInput) {" |
| /value/anchor | "cancelOrder(input: Codegen.CancelOrderInput) {" |
| /value/sha256 | "27ddd40b2430caebc5f0defc901d1e42aa54f1cb29038fe4e7657a2448c03811" |

## evidence-8 — source-V09/e0

원문 "packages/admin-ui/src/lib/core/src/data/definitions/order-definitions.ts", 373행 5열, UTF-16 구간 [7598, 7647)의 "baseline" 인용:

~~~text
mutation CancelOrder($input: CancelOrderInput!) {
~~~


## evidence-8 — evidence-8 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-V09/e0" |
| /value/symbol | "mutation CancelOrder($input: CancelOrderInput!) {" |
| /value/anchor | "mutation CancelOrder($input: CancelOrderInput!) {" |
| /value/sha256 | "26a6b81368d53a731b2847e0587eeb94463ec706bb8df73bee13d304fb770701" |

## evidence-9 — source-V10/e0

원문 "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts", 78행 5열, UTF-16 구간 [2469, 2479)의 "baseline" 인용:

~~~text
cancel() {
~~~


## evidence-9 — evidence-9 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-V10/e0" |
| /value/symbol | "cancel() {" |
| /value/anchor | "cancel() {" |
| /value/sha256 | "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5" |

## evidence-10 — source-V11/e0

원문 "packages/admin-ui/src/lib/core/src/data/definitions/order-definitions.ts", 384행 5열, UTF-16 구간 [7854, 7903)의 "baseline" 인용:

~~~text
mutation RefundOrder($input: RefundOrderInput!) {
~~~


## evidence-10 — evidence-10 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-V11/e0" |
| /value/symbol | "mutation RefundOrder($input: RefundOrderInput!) {" |
| /value/anchor | "mutation RefundOrder($input: RefundOrderInput!) {" |
| /value/sha256 | "26a6b81368d53a731b2847e0587eeb94463ec706bb8df73bee13d304fb770701" |

## evidence-11 — source-refund-cancel/e0

원문 "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts", 615행 21열, UTF-16 구간 [23612, 23645)의 "baseline" 인용:

~~~text
if (input.cancel.lines?.length) {
~~~


## evidence-11 — evidence-11 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-refund-cancel/e0" |
| /value/symbol | "refund-cancel" |
| /value/anchor | "if (input.cancel.lines?.length) {" |
| /value/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |

## evidence-12 — source-refund-request/e0

원문 "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts", 647행 21열, UTF-16 구간 [25321, 25348)의 "baseline" 인용:

~~~text
if (input.refunds.length) {
~~~


## evidence-12 — evidence-12 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-refund-request/e0" |
| /value/symbol | "refund-request" |
| /value/anchor | "if (input.refunds.length) {" |
| /value/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |

## evidence-13 — source-refund-payload/e0

원문 "packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts", 196행 13열, UTF-16 구간 [7259, 7304)의 "baseline" 인용:

~~~text
cancel: {
                lines: cancelLines,
~~~


## evidence-13 — evidence-13 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-refund-payload/e0" |
| /value/symbol | "refund-payload" |
| /value/anchor | "cancel: {\n                lines: cancelLines," |
| /value/sha256 | "d9ea112f17bff650686842306bef46fa6f7564278b1166762a7c9b7a8473a6fb" |

## evidence-14 — source-refund-close/e0

원문 "packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts", 205행 5열, UTF-16 구간 [7491, 7529)의 "baseline" 인용:

~~~text
cancel() {
        this.resolveWith();
~~~


## evidence-14 — evidence-14 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-refund-close/e0" |
| /value/symbol | "refund-close" |
| /value/anchor | "cancel() {\n        this.resolveWith();" |
| /value/sha256 | "d9ea112f17bff650686842306bef46fa6f7564278b1166762a7c9b7a8473a6fb" |

## evidence-15 — source-refund-mutation/e0

원문 "packages/admin-ui/src/lib/core/src/data/providers/order-data.service.ts", 123행 5열, UTF-16 구간 [3577, 3623)의 "baseline" 인용:

~~~text
refundOrder(input: Codegen.RefundOrderInput) {
~~~


## evidence-15 — evidence-15 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "source-refund-mutation/e0" |
| /value/symbol | "refund-mutation" |
| /value/anchor | "refundOrder(input: Codegen.RefundOrderInput) {" |
| /value/sha256 | "27ddd40b2430caebc5f0defc901d1e42aa54f1cb29038fe4e7657a2448c03811" |

## evidence-16 — cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379:calls-cancel/e0

원문 "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts", 587행 32열, UTF-16 구간 [22747, 22788)의 "baseline" 인용:

~~~text
this.dataService.order.cancelOrder(input)
~~~


## evidence-16 — evidence-16 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379:calls-cancel/e0" |
| /value/symbol | "CallExpression" |
| /value/anchor | "this.dataService.order.cancelOrder(input)" |
| /value/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |

## evidence-17 — cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379:opens-modal/e0

원문 "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts", 577행 9열, UTF-16 구간 [22437, 22626)의 "baseline" 인용:

~~~text
this.modalService
            .fromComponent(CancelOrderDialogComponent, {
                size: 'xl',
                locals: {
                    order,
                },
            })
~~~


## evidence-17 — evidence-17 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379:opens-modal/e0" |
| /value/symbol | "CallExpression" |
| /value/anchor | "this.modalService\n            .fromComponent(CancelOrderDialogComponent, {\n                size: 'xl',\n                locals: {\n                    order,\n                },\n            })" |
| /value/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |

## evidence-18 — cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:23185:calls-cancel/e0

원문 "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts", 616행 32열, UTF-16 구간 [23677, 23725)의 "baseline" 인용:

~~~text
this.dataService.order.cancelOrder(input.cancel)
~~~


## evidence-18 — evidence-18 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:23185:calls-cancel/e0" |
| /value/symbol | "CallExpression" |
| /value/anchor | "this.dataService.order.cancelOrder(input.cancel)" |
| /value/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |

## evidence-19 — cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:23185:opens-modal/e0

원문 "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts", 602행 9열, UTF-16 구간 [23243, 23432)의 "baseline" 인용:

~~~text
this.modalService
            .fromComponent(RefundOrderDialogComponent, {
                size: 'xl',
                locals: {
                    order,
                },
            })
~~~


## evidence-19 — evidence-19 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:23185:opens-modal/e0" |
| /value/symbol | "CallExpression" |
| /value/anchor | "this.modalService\n            .fromComponent(RefundOrderDialogComponent, {\n                size: 'xl',\n                locals: {\n                    order,\n                },\n            })" |
| /value/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |

## evidence-20 — cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts:2469:closes-dialog-empty/e0

원문 "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts", 79행 9열, UTF-16 구간 [2488, 2506)의 "baseline" 인용:

~~~text
this.resolveWith()
~~~


## evidence-20 — evidence-20 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts:2469:closes-dialog-empty/e0" |
| /value/symbol | "CallExpression" |
| /value/anchor | "this.resolveWith()" |
| /value/sha256 | "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5" |

## evidence-21 — cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts:7491:closes-dialog-empty/e0

원문 "packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts", 206행 9열, UTF-16 구간 [7510, 7528)의 "baseline" 인용:

~~~text
this.resolveWith()
~~~


## evidence-21 — evidence-21 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts:7491:closes-dialog-empty/e0" |
| /value/symbol | "CallExpression" |
| /value/anchor | "this.resolveWith()" |
| /value/sha256 | "d9ea112f17bff650686842306bef46fa6f7564278b1166762a7c9b7a8473a6fb" |

## evidence-22 — object:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379

원문 "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts", 576행 5열, UTF-16 구간 [22379, 23179)의 "baseline" 인용:

~~~text
private cancelOrder(order: OrderDetailFragment) {
        this.modalService
            .fromComponent(CancelOrderDialogComponent, {
                size: 'xl',
                locals: {
                    order,
                },
            })
            .pipe(
                switchMap(input => {
                    if (input) {
                        return this.dataService.order.cancelOrder(input);
                    } else {
                        return of(undefined);
                    }
                }),
                switchMap(result => this.refetchOrder(result)),
            )
            .subscribe(result => {
                if (result) {
                    this.notificationService.success(_('order.cancelled-order-success'));
                }
            });
    }
~~~


## evidence-22 — evidence-22 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "object:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379" |
| /value/symbol | "cancelOrder" |
| /value/anchor | "private cancelOrder(order: OrderDetailFragment) {" |
| /value/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |

## evidence-23 — object:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:23185

원문 "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts", 601행 5열, UTF-16 구간 [23185, 26909)의 "baseline" 인용:

~~~text
private refundOrder(order: OrderDetailFragment) {
        this.modalService
            .fromComponent(RefundOrderDialogComponent, {
                size: 'xl',
                locals: {
                    order,
                },
            })
            .pipe(
                switchMap(input => {
                    if (!input) {
                        return of(undefined);
                    }

                    if (input.cancel.lines?.length) {
                        return this.dataService.order.cancelOrder(input.cancel).pipe(
                            map(res => {
                                const result = res.cancelOrder;
                                switch (result.__typename) {
                                    case 'Order':
                                        this.refetchOrder(result).subscribe();
                                        this.notificationService.success(
                                            _('order.cancelled-order-items-success'),
                                            {
                                                count: summate(input.cancel.lines, 'quantity'),
                                            },
                                        );
                                        return input;
                                    case 'CancelActiveOrderError':
                                    case 'QuantityTooGreatError':
                                    case 'MultipleOrderError':
                                    case 'OrderStateTransitionError':
                                    case 'EmptyOrderLineSelectionError':
                                        this.notificationService.error(result.message);
                                        return undefined;
                                }
                            }),
                        );
                    } else {
                        return [input];
                    }
                }),
                switchMap(input => {
                    if (!input) {
                        return of(undefined);
                    }
                    if (input.refunds.length) {
                        return forkJoin(
                            input.refunds.map(refund =>
                                this.dataService.order.refundOrder(refund).pipe(map(res => res.refundOrder)),
                            ),
                        );
                    } else {
                        return [undefined];
                    }
                }),
            )
            .subscribe(results => {
                for (const result of results ?? []) {
                    if (result) {
                        switch (result.__typename) {
                            case 'Refund':
                                if (result.state === 'Failed') {
                                    this.notificationService.error(_('order.refund-order-failed'));
                                } else {
                                    this.notificationService.success(_('order.refund-order-success'));
                                }
                                break;
                            case 'AlreadyRefundedError':
                            case 'NothingToRefundError':
                            case 'PaymentOrderMismatchError':
                            case 'RefundOrderStateError':
                            case 'RefundStateTransitionError':
                                this.notificationService.error(result.message);
                                break;
                        }
                    }
                }
                this.refetchOrder(results?.[0]).subscribe();
            });
    }
~~~


## evidence-23 — evidence-23 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "object:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:23185" |
| /value/symbol | "refundOrder" |
| /value/anchor | "private refundOrder(order: OrderDetailFragment) {" |
| /value/sha256 | "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede" |

## evidence-24 — object:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts:2469

원문 "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts", 78행 5열, UTF-16 구간 [2469, 2513)의 "baseline" 인용:

~~~text
cancel() {
        this.resolveWith();
    }
~~~


## evidence-24 — evidence-24 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "object:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts:2469" |
| /value/symbol | "cancel" |
| /value/anchor | "cancel() {" |
| /value/sha256 | "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5" |

## evidence-25 — object:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts:7491

원문 "packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts", 205행 5열, UTF-16 구간 [7491, 7535)의 "baseline" 인용:

~~~text
cancel() {
        this.resolveWith();
    }
~~~


## evidence-25 — evidence-25 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "object:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts:7491" |
| /value/symbol | "cancel" |
| /value/anchor | "cancel() {" |
| /value/sha256 | "d9ea112f17bff650686842306bef46fa6f7564278b1166762a7c9b7a8473a6fb" |

## evidence-26 — attribute:calls-cancel:0

원문 "packages/admin-ui/src/lib/core/src/data/providers/order-data.service.ts", 114행 5열, UTF-16 구간 [3319, 3571)의 "baseline" 인용:

~~~text
cancelOrder(input: Codegen.CancelOrderInput) {
        return this.baseDataService.mutate<Codegen.CancelOrderMutation, Codegen.CancelOrderMutationVariables>(
            CANCEL_ORDER,
            {
                input,
            },
        );
    }
~~~


## evidence-26 — evidence-26 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "attribute:calls-cancel:0" |
| /value/symbol | "cancelOrder" |
| /value/anchor | "cancelOrder(input: Codegen.CancelOrderInput) {\n        return this.baseDataService.mutate&lt;Codegen.CancelOrderMutation, Codegen.CancelOrderMutationVariables&gt;(\n            CANCEL_ORDER,\n            {\n                input,\n            },\n        );\n    }" |
| /value/sha256 | "27ddd40b2430caebc5f0defc901d1e42aa54f1cb29038fe4e7657a2448c03811" |

## evidence-27 — attribute:opens-modal:0

원문 "packages/admin-ui/src/lib/core/src/providers/modal/modal.service.ts", 68행 5열, UTF-16 구간 [1985, 2882)의 "baseline" 인용:

~~~text
fromComponent<T extends Dialog<any>, R>(
        component: Type<T> & Type<Dialog<R>>,
        options?: ModalOptions<T>,
    ): Observable<R | undefined> {
        return from(this.overlayHostService.getHostView()).pipe(
            mergeMap(hostView => {
                const modalComponentRef = hostView.createComponent(ModalDialogComponent);
                const modalInstance: ModalDialogComponent<any> = modalComponentRef.instance;
                modalInstance.childComponentType = component;
                modalInstance.options = options;

                return new Observable<R>(subscriber => {
                    modalInstance.closeModal = (result: R) => {
                        modalComponentRef.destroy();
                        subscriber.next(result);
                        subscriber.complete();
                    };
                });
            }),
        );
    }
~~~


## evidence-27 — evidence-27 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "attribute:opens-modal:0" |
| /value/symbol | "fromComponent" |
| /value/anchor | "fromComponent&lt;T extends Dialog&lt;any&gt;, R&gt;(\n        component: Type&lt;T&gt; & Type&lt;Dialog&lt;R&gt;&gt;,\n        options?: ModalOptions&lt;T&gt;,\n    ): Observable&lt;R &#124; undefined&gt; {\n        return from(this.overlayHostService.getHostView()).pipe(\n            mergeMap(hostView =&gt; {\n                const modalComponentRef = hostView.createComponent(ModalDialogComponent);\n                const modalInstance: ModalDialogComponent&lt;any&gt; = modalComponentRef.instance;\n                modalInstance.childComponentType = component;\n                modalInstance.options = options;\n\n                return new Observable&lt;R&gt;(subscriber =&gt; {\n                    modalInstance.closeModal = (result: R) =&gt; {\n                        modalComponentRef.destroy();\n                        subscriber.next(result);\n                        subscriber.complete();\n                    };\n                });\n            }),\n        );\n    }" |
| /value/sha256 | "d4096905f43f3134d12aa2567a2a0a6d1deb25b985222de877d7057fc336f365" |

## evidence-28 — attribute:closes-dialog-empty:0

원문 "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts", 22행 5열, UTF-16 구간 [695, 744)의 "baseline" 인용:

~~~text
resolveWith: (result?: CancelOrderInput) => void;
~~~


## evidence-28 — evidence-28 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "attribute:closes-dialog-empty:0" |
| /value/symbol | "resolveWith" |
| /value/anchor | "resolveWith: (result?: CancelOrderInput) =&gt; void;" |
| /value/sha256 | "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5" |

## evidence-29 — attribute:closes-dialog-empty:1

원문 "packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts", 30행 5열, UTF-16 구간 [1047, 1137)의 "baseline" 인용:

~~~text
resolveWith: (result?: { cancel: CancelOrderInput; refunds: RefundOrderInput[] }) => void;
~~~


## evidence-29 — evidence-29 식별·참조·조회·원문 좌표

| 기록 경로 | 보존 값 |
| --- | --- |
| /status | "Found" |
| /value/id | "attribute:closes-dialog-empty:1" |
| /value/symbol | "resolveWith" |
| /value/anchor | "resolveWith: (result?: { cancel: CancelOrderInput; refunds: RefundOrderInput[] }) =&gt; void;" |
| /value/sha256 | "d9ea112f17bff650686842306bef46fa6f7564278b1166762a7c9b7a8473a6fb" |
