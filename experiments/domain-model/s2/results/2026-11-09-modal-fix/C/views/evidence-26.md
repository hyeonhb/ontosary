# evidence-26

status: "Found"
value:
 id: "attribute:calls-cancel:0"
 file: "packages/admin-ui/src/lib/core/src/data/providers/order-data.service.ts"
 symbol: "cancelOrder"
 offset: 3319
 end: 3571
 line: 114
 anchor: "cancelOrder(input: Codegen.CancelOrderInput) {\n        return this.baseDataService.mutate<Codegen.CancelOrderMutation, Codegen.CancelOrderMutationVariables>(\n            CANCEL_ORDER,\n            {\n                input,\n            },\n        );\n    }"
 sha256: "27ddd40b2430caebc5f0defc901d1e42aa54f1cb29038fe4e7657a2448c03811"
 text: "cancelOrder(input: Codegen.CancelOrderInput) {\n        return this.baseDataService.mutate<Codegen.CancelOrderMutation, Codegen.CancelOrderMutationVariables>(\n            CANCEL_ORDER,\n            {\n                input,\n            },\n        );\n    }"
 column: 5
 sourceVersion: "baseline"
