# evidence-27

status: "Found"
value:
 id: "attribute:opens-modal:0"
 file: "packages/admin-ui/src/lib/core/src/providers/modal/modal.service.ts"
 symbol: "fromComponent"
 offset: 1985
 end: 2882
 line: 68
 anchor: "fromComponent<T extends Dialog<any>, R>(\n        component: Type<T> & Type<Dialog<R>>,\n        options?: ModalOptions<T>,\n    ): Observable<R | undefined> {\n        return from(this.overlayHostService.getHostView()).pipe(\n            mergeMap(hostView => {\n                const modalComponentRef = hostView.createComponent(ModalDialogComponent);\n                const modalInstance: ModalDialogComponent<any> = modalComponentRef.instance;\n                modalInstance.childComponentType = component;\n                modalInstance.options = options;\n\n                return new Observable<R>(subscriber => {\n                    modalInstance.closeModal = (result: R) => {\n                        modalComponentRef.destroy();\n                        subscriber.next(result);\n                        subscriber.complete();\n                    };\n                });\n            }),\n        );\n    }"
 sha256: "d4096905f43f3134d12aa2567a2a0a6d1deb25b985222de877d7057fc336f365"
 text: "fromComponent<T extends Dialog<any>, R>(\n        component: Type<T> & Type<Dialog<R>>,\n        options?: ModalOptions<T>,\n    ): Observable<R | undefined> {\n        return from(this.overlayHostService.getHostView()).pipe(\n            mergeMap(hostView => {\n                const modalComponentRef = hostView.createComponent(ModalDialogComponent);\n                const modalInstance: ModalDialogComponent<any> = modalComponentRef.instance;\n                modalInstance.childComponentType = component;\n                modalInstance.options = options;\n\n                return new Observable<R>(subscriber => {\n                    modalInstance.closeModal = (result: R) => {\n                        modalComponentRef.destroy();\n                        subscriber.next(result);\n                        subscriber.complete();\n                    };\n                });\n            }),\n        );\n    }"
 column: 5
 sourceVersion: "baseline"
