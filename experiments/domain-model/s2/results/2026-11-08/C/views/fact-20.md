# fact-20

status: "Found"
value:
 id: "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts:2469:closes-dialog-empty"
 evidence:
  항목 1:
   id: "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts:2469:closes-dialog-empty/e0"
   file: "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts"
   symbol: "CallExpression"
   offset: 2488
   end: 2506
   line: 79
   anchor: "this.resolveWith()"
   sha256: "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5"
 source:
  id: "cell:534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts:2469:closes-dialog-empty"
  kind: "observed-in-source"
  author: "automated-observer"
  method: "typescript-ast-symbol-identity"
  scope: "Direct member call expressions in lexical method region, including nested callbacks/functions, excluding nested classes; no reachability/transitive-call claim"
  support: "supported-static-role"
  claim: "dialog 인자 없이 닫기"
  object: "534e6003534f74761e82de1b8c6061cba89945d1:packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts:2469"
  attribute: "closes-dialog-empty"
  value: "yes"
  reasons:

  evidence:
   항목 1:
    file: "packages/admin-ui/src/lib/order/src/components/cancel-order-dialog/cancel-order-dialog.component.ts"
    symbol: "CallExpression"
    offset: 2488
    end: 2506
    line: 79
    anchor: "this.resolveWith()"
    sha256: "a47e7000b222454302c8a0dfc374555f78616517fdc3ec03621a199ecf234cc5"
