# S2 modal 연결 독립 재검토 — 2026-11-10

**R9 잔여 해결, R8/R10 해결 유지. 검토한 지원 범위에서 추가 수정이 필요한 결함은 확인하지 않았다.** S2 준비 구현의 보완은 완료로 인정한다. 본 비교 실행 준비 전체 완료나 모델 효용 입증은 아니며 `readyForTrial:false`를 유지한다.

대상은 PR #29/main `5bd30c73e1e604b5aea0f52fb900f704ebe6222f`의 [완료 보고](2026-11-09-s2-modal-fix.md)와 실제 구현이다. [보완 지시](2026-11-09-s2-modal-fix-instructions.md)의 연결 계약·검증 행렬·완료 조건을 대조했다. 원래 개발 checkout은 clean detached 상태로 유지했고 별도 기존 문서 worktree에서 검증했다. 제품 구현·테스트·과거 결과·고정 Vendure cache는 변경하지 않았다.

## R9 해결 근거

[`behavior.ts`](../../experiments/domain-model/s2/evaluation/behavior.ts)의 비API 사례는 제출 부모 `cancelOrRefund`를 먼저 실행한다. 실제 `fromComponent`의 constructor를 같은 executor가 로드한 두 constructor와 비교하고, 전달된 `locals.order`로 dialog를 실행한다. 시나리오가 정상 dialog 결과를 미리 만들어 돌려주는 종전 경로는 제거됐다.

[`modal.ts`](../../experiments/domain-model/s2/evaluation/modal.ts)는 호출별 상태를 소유하며 구독 시 실제 select/cancel을 호출한다. resolve 값을 해당 구독의 next/complete로 전달하고, 실제 요청을 독립 기대 payload와 비교한다. order 형식 검사는 잘못된 ID/active를 정상값으로 복구하지 않는다. 사용자 상태가 locals나 resolver를 덮어쓰지 못한다. [`execute.ts`](../../experiments/domain-model/s2/evaluation/execute.ts)의 component 조회도 기존 source snapshot·제외 seam 검사 경로를 사용한다. 새 modal.js는 evaluator 지문에 포함됐다.

이전 [독립 probe](evidence/2026-11-09-s2-contract-review-probes.mjs)를 수정 없이 현재 평가기에 재실행했다. 참조 수정과 두 반례를 같은 제출 메서드의 별도 직접 연결 관찰과도 대조했다.

| 제출 | 타입 진단 | 보존 / 새 요구 | 새 평가기와 별도 연결 관찰 |
|---|---|---|---|
| reference | 0 | 16/16 · 36/36 | 둘 다 정상 요청 |
| wrong-modal-order | 0 | 12/16 · 32/36 | 둘 다 wrong-modal-order로 취소 요청, assertion 실패 |
| wrong-modal-active | 0 | 14/16 · 32/36 | 둘 다 inactive 주문의 취소 lines 누락, assertion 실패 |

두 반례의 sourceBinding은 true이고 전체 판정은 failed다. 타입 오류나 일반 unsupported로 반례를 우회하지 않았다. [독립 관찰](evidence/2026-11-10-s2-modal-review/probes.json)에 실제 locals·기대/관찰 요청·modal trace가 있다.

## 검증 결과와 재현 범위

- `pnpm check`: **230테스트 통과, skip 0**, 코어·예제·S2 타입 검사와 예제 production build 통과. 새 연결 fixture16개는 외부 cache 없이 실행됐다.
- `pnpm experiment`: 기존 비교 **4/4** 통과.
- 새 경로에서 24제출 교정을 실행했다. baseline은 타입 진단0·보존16/16·요구6/36, reference/helper는 진단0·52/52다. 기존13개와 새 modal2개, 총15개 동작 결함은 모두 타입 통과 후 요청 assertion에서 실패한다. 역사적 참조 진단5 및 helper 타입/구문/누락·삭제·범위 밖 gate도 유지됐다.
- 새 교정과 커밋된 v3 교정의 **50파일**을 gzip 해제 후 wallTimeMs만 제외해 비교했다. 진단·요청·실패 사례·modal trace·소스/평가기 지문 모두 일치했다. 이번 독립 리뷰는 새 배치1회와 커밋 결과를 비교했고, 개발자의 두 반복 실행을 새 배치2회로 표현하지 않는다.
- 완전한 제출 source root의 CLI를 실제 실행했다. delta와 submissionId·전체 판정·52개 사례의 요청 assertion/modal trace가 일치하고 sourceBinding=true다.
- 실제 고정 RxJS를 사용하는 별도 [감사 코드](evidence/2026-11-10-s2-modal-review-audit.mjs)에서 select, undefined dismiss, 미해결, 다중 resolve, 재구독 5상황을 확인했다. 미해결을 dismiss로 바꾸지 않고 두 번째 resolve/구독이 추가 값을 전달하지 않으며 미지원 상태를 남긴다. 이는 자체 테스트의 간단한 Observable 대역 외에 실제 RxJS로 확인한 경계다.
- 새 준비 결과와 커밋된 modal-fix 결과의 **147비시간 파일**이 일치했다. 이전 v2 배포와도 manifest·agent142파일 hash·baseline/model/bundle ID가 동일했다. 모델12항목/16링크·승인0·근거 내용 유지다. 준비/포장 코드는 바뀌지 않아 workspace 복사를 다시 실행하지 않았고 OS 격리를 검증했다고 주장하지 않는다.
- 실제 cache의 ModalService/ModalDialogComponent 원문 hash·저장된 구간이 일치했다. locals 전달과 resolve→next/complete 대응을 원문과 대조했다. Angular overlay/뷰 lifecycle의 동기·비동기 전체 동등성은 확인 대상이 아니다.

[검증 증거](evidence/2026-11-10-s2-modal-review/)에는 check/experiment 로그, 교정 요약·50파일 hash, 준비147파일 hash, probe 요약과 네 전체 평가 보고의 gzip, 실제 RxJS/CLI/배포/원문 감사 결과를 보존했다. 전체 교정 원시는 커밋된 [v3 교정](../../experiments/domain-model/s2/verification/2026-11-09-modal-fix/oracle/)과 위 hash 비교로 연결한다. 과거 실패 근거는 그대로다.

재현 명령은 저장소 root에서 실행하며 출력 경로는 새로 정한다.

```sh
pnpm check
pnpm experiment
pnpm s2:oracle-check /tmp/ontosary-vendure-preparation-20261108/vendure work/s2-modal-review-20261110/oracle
pnpm s2:verify-evaluation experiments/domain-model/s2/verification/2026-11-09-modal-fix/oracle work/s2-modal-review-20261110/oracle work/s2-modal-review-20261110/evaluation-reproduction.json
node docs/reviews/evidence/2026-11-09-s2-contract-review-probes.mjs /tmp/ontosary-vendure-preparation-20261108/vendure work/s2-modal-review-20261110/independent
pnpm s2:prepare /tmp/ontosary-vendure-preparation-20261108/vendure work/s2-modal-review-20261110/prepared
pnpm s2:verify experiments/domain-model/s2/results/2026-11-09-modal-fix work/s2-modal-review-20261110/prepared work/s2-modal-review-20261110/preparation-reproduction.json
node docs/reviews/evidence/2026-11-10-s2-modal-review-audit.mjs /tmp/ontosary-vendure-preparation-20261108/vendure work/s2-modal-review-20261110
```

## 아키텍처·방향 평가와 다음 판단

합의된 단일 준비 세션·동결 모델·순수 조회 구조를 유지하면서 평가기 내부의 작은 modal 모듈만 추가했다. constructor identity의 Map 조회와 호출별 상태·trace 분리는 현재 두 component/시나리오당1호출 상한에 적합하다. 일반 UI simulator나 프레임워크 의존성을 코어에 넣을 이유는 이번 결과에서 생기지 않았다. trace 복사는 관찰 시점의 값을 보존하는 비용이며 현재 유한 fixture 범위에서 별도 최적화를 요구할 근거는 없다.

이번 성과는 agent가 실제 수정한 코드의 결과를 더 충실하게 판정할 준비를 갖춘 것이다. **도메인 모델이 agent 수정에 도움이 됐다는 H-O 결과는 아직 없다.** FCA의 모델 구축 기여 H-F도 별개이고, 모델 지식은 여전히 사람 검토 대기다. 평가기의 정확성 보완을 온톨로지/FCA의 효과로 해석하지 않는다.

검증 경계는 제출 메서드/helper와 명시된 동기 modal 연결이다. constructor/field 초기화·ngOnInit·HTML·UI 계산·실제 overlay/네트워크·비동기 전체 실행은 제외돼 있다. 미지원 제출의 수와 이유도 본 비교에서 별도로 보고해야 하며 성공률 분모에서 조용히 제거하면 안 된다.

다음은 새 구조 구현보다 **사용자와 S2 실행 계약을 확정하는 단계**다. 가상 취소 reason 과업의 invalid 처리/채점 범위, B/C 자료의 의미 동등성·검토 대기 지식 취급, 이 제한된 평가 범위의 수용 여부, 실제 격리·agent 모델/도구/예산·배정과 성공/미지원 보고 방식을 함께 정한다. 이번 리뷰에서 정책·사람 의미·전체 oracle 충실성 승인을 대신 기록하거나 본 비교를 실행하지 않았다. `readyForTrial:false`, H-O/H-F 미검증, S3 미착수를 유지한다.
