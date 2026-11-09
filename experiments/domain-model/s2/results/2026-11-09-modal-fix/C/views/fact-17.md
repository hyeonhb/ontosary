# fact-17

status: "Found"
value:
 id: "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379:opens-modal"
 evidence:
  항목 1:
   id: "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379:opens-modal/e0"
   file: "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts"
   symbol: "CallExpression"
   offset: 22437
   end: 22626
   line: 577
   anchor: "this.modalService\n            .fromComponent(CancelOrderDialogComponent, {\n                size: 'xl',\n                locals: {\n                    order,\n                },\n            })"
   sha256: "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede"
 source:
  id: "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379:opens-modal"
  kind: "observed-in-source"
  author: "automated-observer"
  method: "typescript-ast-symbol-identity"
  scope: "Direct member call expressions in lexical method region, including nested callbacks/functions, excluding nested classes; no reachability/transitive-call claim"
  support: "supported-static-role"
  claim: "modal component 열기"
  object: "534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts:22379"
  attribute: "opens-modal"
  value: "yes"
  reasons:

  evidence:
   항목 1:
    file: "packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts"
    symbol: "CallExpression"
    offset: 22437
    end: 22626
    line: 577
    anchor: "this.modalService\n            .fromComponent(CancelOrderDialogComponent, {\n                size: 'xl',\n                locals: {\n                    order,\n                },\n            })"
    sha256: "e3e35dc4f03757e43aa5ec2780119ca00db104b65bf46d5e204c6f16d2314ede"
