# 개발 세션 지시 — R9 modal 데이터 전달 보완

작성: 2026-11-09. 기준 main `346439c0e168d625e1da8f5060a841cef4a0a024`(독립 재검토 PR #27). 실제 작업은 **이 지시가 반영된 최신 main**에서 시작한다. 이 문서는 개발·평가자 전용이며 A/B/C agent 자료에 포함하지 않는다.

## 1. 목표와 작업 경계

사용자는 R9의 남은 modal 데이터 전달 문제 보완을 승인했다. 목표는 **제출 부모가 실제로 선택한 component와 locals로 dialog를 실행하고, 그 결과로 만들어진 요청을 판정하는 평가 하네스**를 구현해 독립 재검토에 넘기는 것이다.

현재 R8(제출 타입 검사)과 R10(취소 정책 범위·환불 사유 보존)은 검증 범위에서 해결됐다. R9의 payload 비교도 보완됐지만 부모→dialog 연결이 끊겨 잘못된 주문 전달을 놓친다. 이 연결을 고치며 기존 검증을 유지한다. S2 목적은 변경 전 모델의 agent 수정 지원 효과(H-O) 검증이고 FCA 구축 기여(H-F)는 별개다. 이번 작업은 본 비교·효용 입증·S3가 아니다. `readyForTrial:false`를 유지한다.

수정의 중심은 `experiments/domain-model/s2/evaluation/behavior.ts`의 modal 대역이다. 필요하면 작은 타입 검사 대상 helper 모듈로 분리하고, 실제 component 식별/인스턴스화에 필요한 최소한의 `execute.ts` 변경을 할 수 있다. 관련 `variants.ts`/교정 runner, 테스트·자체 fixture, 평가 계약/README·현재 문서와 새 결과를 갱신한다. 파일 분할·함수명은 개발자가 정한다.

제출 타입 검사·source snapshot·전체 payload 비교를 약화하거나 다시 설계하지 않는다. 제품 core/CLI, 준비 세션/모델/조회 구조, S1/V1/V2, FCA/논리 알고리즘·상한, 모델12항목/16링크·승인0, 기존 agent 제공 자료를 바꾸지 않는다. Angular/DB 실행 환경·새 의존성·범용 UI simulator·비동기 지원 확대·성능 리팩터링·S3는 범위 밖이다. 실제 Vendure 소스는 참조/결함 교정용 복제나 delta에서만 변경한다.

## 2. 먼저 복원할 근거

PROGRESS → ARCHITECTURE → ROADMAP → AGENTS/CONTRIBUTING → 아래 자료를 읽는다.

- [최신 독립 재검토](2026-11-09-s2-contract-independent-review.md), [반례 코드](evidence/2026-11-09-s2-contract-review-probes.mjs), [반례/CLI 요약](evidence/2026-11-09-s2-contract-review/probes.json).
- [직전 보완 지시](2026-11-09-s2-contract-fix-instructions.md), [개발 인계](2026-11-09-s2-contract-fix.md).
- `experiments/domain-model/s2/evaluation/{behavior,execute,evaluate,submission,variants,oracle-check}.ts`, `evaluation/TASK-REVIEW.md`, S2 README와 `tests/s2*.test.ts`.
- 준비된 Vendure의 `OrderDetailComponent` 취소/환불 흐름, 두 dialog의 `select/cancel`, `ModalService.fromComponent`와 locals/resolve 연결 원문.

현재 기준은214테스트(skip0)·기존 비교4/4,22제출 교정46파일 재현, 준비147파일 재현·agent142파일/세 ID 유지다. baseline은 보존16/16·새 요구6/36, 새 참조/helper는 타입 진단0·52/52다. 이 숫자는 출발점이며 사례를 추가할 때 분모를 고정하려고 검사를 빼지 않는다.

원격/브랜치/사용자 변경을 확인하고 새 작업 브랜치에서 시작한다. 입력은 Vendure v3.5.0 revision `534e6003534f74761e82de1b8c6061cba89945d1`, cache `/tmp/ontosary-vendure-preparation-20261108/vendure`, 설정 `packages/admin-ui/ontosary.scope.json`이다. 경로는 CLI 인자로 받고 실제 Node/TS·입력 지문을 기록한다. cache는 읽기 전용이며 설치 예산을 다시 열지 않는다. cache가 없거나 지문이 다르면 자체 fixture 작업은 진행하되 실제 통합 완료를 주장하지 않는다.

## 3. 수정 전 반례와 기대 변화

먼저 기존 명령과 독립 probe를 새 출력 경로에서 실행한다. 유효한 참조 수정의 부모 `private cancelOrder()`에서 modal에 전달하는 order만 각각 바꾼 두 사례다.

| 변형 | 수정 전 판정 | 실제 전달값으로 연결한 관찰 | 수정 후 요구 |
|---|---|---|---|
| `order: { ...order, id: 'wrong-modal-order' }` | 진단0·52/52·overall passed | 잘못된 주문 ID로 취소 요청 | 타입 통과 후 payload assertion 실패 |
| `order: { ...order, active: true }` | 진단0·52/52·overall passed | inactive 주문의 부분 취소 lines 누락 | 타입 통과 후 payload assertion 실패 |

두 변형은 새 참조 수정에 각각 독립 적용한다. 서비스/기대값을 함께 바꾸지 않는다. 두 사례를 타입 오류나 일반 미지원으로 차단한 결과를 R9 해결 증거로 세지 않는다. 이 입력들은 현재 지원하는 component와 정상 형식의 locals이며, 잘못된 업무 값이 요청에 미치는 결과를 관찰해야 한다.

역사적 probe/원시 결과는 그대로 보존한다. 인터페이스가 바뀌면 새 runner/회귀로 동등한 사례를 옮기고 이전 관찰과 연결한다.

## 4. 구현해야 할 연결 계약

실행 순서는 다음과 같아야 한다. 이는 메서드/모듈 설계 지시이며 새 제품 아키텍처를 도입하는 요구가 아니다.

```text
공통 fixture의 부모 입력·사용자 행동
  → 제출 부모 cancelOrRefund / 실제 취소·환불 분기
  → 실제 fromComponent(component, options) 호출
  → 전달된 component + options.locals로 dialog 준비
  → 지정한 사용자 select 또는 dismiss 행동
  → 제출 dialog의 resolveWith 결과
  → 부모 Observable 후속 흐름
  → 제출 service의 요청 → 독립 기대 payload/순서/횟수와 비교
```

### 부모 입력과 실제 component/locals

- 부모 흐름을 먼저 실행한다. 기존처럼 dialog를 사전 실행하고 `fromComponent: () => of(returned)`로 고정 결과를 돌려주는 우회를 제거한다. service 직접 호출 사례는 기존 API 경계를 그대로 검사한다.
- 시나리오 mode는 사용자의 과업/행동과 독립 기대값을 정할 수 있다. **실제로 실행할 dialog는 호출 인자의 component가 결정**해야 한다. mode에 맞는 정상 component로 치환하지 않는다.
- 지원하는 두 dialog는 같은 제출 snapshot에서 로드한 실제 constructor/prototype identity로 식별한다. 이름 문자열만 같다는 이유로 임의 component를 승인하지 않는다. 현재 executor의 제외 seam 검사와 실행 파일 hash 수집이 계속 적용돼야 한다. 검증·추적 경로를 우회한 별도 원문 실행기를 만들지 않는다.
- 실제 `options.locals`를 dialog에 전달한다. 부모가 넘긴 `order.id/active/lines` 등을 fixture의 정상 order로 복원하거나 값의 오류를 정규화하지 않는다. 부모에 공급할 원래 주문 fixture는 dialog에 필요한 필드까지 갖추되 dialog 단계에서 따로 업무 데이터를 만들어 보충하지 않는다.
- locals, 사용자 입력, 외부 UI/DI 대역의 필드 소유권을 구분한다. reason/사용자의 line 선택 등은 fixture가 제공할 수 있지만 부모가 전달한 order를 덮어쓰는 수단으로 사용하지 않는다. 기존에 제외한 constructor/field 초기화·ngOnInit/HTML·화면 계산 전체를 이번에 검증했다고 주장하지 말고 남은 fixture 상태의 의미와 한계를 명시한다.

### 사용자 행동·resolve·Observable

- 실제 제출 dialog의 `select()` 또는 `cancel()`을 실행한다. 대역이 취소/환불 payload를 직접 만들거나 reason 정규화·업무 분기를 대신 수행하지 않는다.
- 각 modal 호출의 반환 Observable과 해당 dialog의 `resolveWith`를 연결한다. 구독/사용자 행동/resolve/반환 전달 순서와 지원하는 동기 실행 계약을 명시한다. 결과 유실·중복 실행·다른 호출의 반환값 재사용을 막고, 모든 상태를 호출별로 소유한다.
- `resolveWith(undefined)`와 아직 resolve하지 않은 상태를 구분한다. 값 없음으로 닫힌 경우 부모에 실제 `undefined`를 전달하고, resolve가 없는데 임의의 dismiss 결과를 만들어서는 안 된다. 미해결·다중 resolve·추가 modal 호출의 지원 여부를 명시하며, 지원하지 않는 경우 이유 있는 미지원으로 남긴다. 이 구현 선택으로 UI 닫힘 방식이나 invalid 입력 처리의 최종 정책을 확정하지 않는다.
- 모르는 component, 필수 locals 누락/잘못된 형식, 지원하지 않는 호출 방식은 성공 fixture로 fallback하지 않는다. 기존 `typecheck/behavior/overall`의 실패·미지원·미수행 구분을 유지한다. 정상 형식의 잘못된 주문 ID/active는 위 반례처럼 실행해 assertion 실패로 구별한다.
- 기존 Promise/async·미검토 operator·제외 seam 제한을 유지한다. 단순히 대기 시간을 늘려 실제 네트워크/Angular 비동기 전체를 지원한다고 표현하지 않는다.

### 관찰·판정

요청 기대값은 계속 공통 fixture/계약에서 독립적으로 정한다. 잘못 전달된 locals를 기대값으로 삼아 그 잘못된 요청을 정답으로 만들지 않는다. 현재 전체 payload·호출 순서/횟수 비교, 호출 시점 복사, lines 순서/중복·undefined 처리 규칙을 유지한다.

결과에는 modal 호출별 실제 component 식별 근거, 전달 locals의 호출 시점 관찰, 사용자 행동, resolve 횟수/값/미해결 여부, 부모에 전달된 결과와 최종 요청을 추적할 수 있게 남긴다. 함수 객체/절대 경로를 그대로 직렬화하지 말고 결정적인 상대 소스/선언 정보와 안전한 값 표현을 사용한다. 진단과 미지원 사유도 호출/사례에 연결한다. 기존 sourceBinding은 파일 내용 결합의 근거이며 이 trace와 연결 검증을 대신하지 않는다.

## 5. 검증 행렬과 완료 판정 방식

| 대상 | 필수 검증 | 기대 |
|---|---|---|
| 자체 소유 정상 fixture | 부모가 받은 두 서로 다른 입력을 locals로 넘기고 dialog가 결과를 돌려줌 | 실제 전달값이 반환/요청까지 이어짐 |
| 실제 component 선택 | 같은 반환 interface를 가진 자체 fixture의 두 component를 각각 전달 | mode/이름 기반 강제 선택 없이 실제 component 동작 구별 |
| 사용자 선택/dismiss | 실제 select/cancel 실행, resolve 값/undefined를 부모에 전달 | 선택은 원래 요청, dismiss는 요청0 |
| 경계·호출별 상태 | 알 수 없는 component·누락/잘못된 locals, 연속된 서로 다른 호출, resolve 없는 상태 | 명시한 지원/미지원 상태, 정상값 fallback·이전 결과 재사용 없음 |
| Vendure 두 잔여 변형 | 잘못된 modal 주문 ID, 잘못된 modal active | 각각 진단0 후 실제 잘못된 요청 관찰 및 assertion 실패 |
| baseline/참조/helper | 기존 입력·새 연결로 실제 타입/동작 평가 | baseline 보존 통과·새 요구 일부 실패, 참조/helper는 전체 통과 |
| 기존13동작 결함 | 새 참조에 각각 독립 적용 | 진단0 후 관련 assertion 실패 유지 |
| R8/R10 회귀 | 역사적 참조/타입·구문·누락/삭제/범위 밖 입력, 환불만/혼합 reason 보존과 두 회귀 변형 | 기존 gate와 과업 범위 유지 |
| complete-root CLI | 완전한 참조 제출과 명시적 delta를 각각 평가 | 같은 submissionId·관련 판정/요청/trace, 경로 차이로 성공 여부가 바뀌지 않음 |

자체 fixture는 외부 Vendure cache 없이 항상 실행한다. 실행 횟수/resolve 순서·값의 전파를 직접 확인하며 내부 코드와 똑같은 함수로 기대값을 재계산하는 테스트는 피한다. 새로운 전체 프레임워크 테스트가 아닌 작은 부모→modal→dialog→부모 연결 테스트로 만든다.

Vendure 교정에는 기존22제출과 두 잔여 변형을 포함한다. 추가 variant/case가 있으면 실제 분모와 이유를 기록한다. 단순히 “전체 테스트 통과”만 남기지 말고 정상/결함별 타입·동작·전체 상태, 실패한 assertion과 기대/관찰값을 제시한다. 이미 해결된 R8/R10을 다시 미지원으로 만들거나 기존 검사를 삭제해 새 사례를 통과시키지 않는다.

## 6. 실행·재현·인계

수정 전 반례 → 작은 연결 fixture → 실제 Vendure 교정 → 전체 검사 → 반복/배포 보존 확인 순으로 진행한다.

- `pnpm check`와 `pnpm experiment`를 실행한다. 새 모듈과 fixture를 기존 타입 검사/테스트에 포함하고 통과/실패/skip 수를 기록한다.
- 실제 교정을 새 두 출력 경로에서 반복하고, 기존 `s2:verify-evaluation` 또는 필요한 최소 보완으로 비교한다. 시간 등 허용된 비결정 필드만 제외하며 modal trace/진단/요청/실패 사례/hash를 제외해 일치를 만들지 않는다.
- `s2:evaluate`의 완전한 제출 CLI도 실제 실행한다. cache/원문은 수정하지 않으며 baseline·제출·실행 파일·평가기 지문을 보존한다. 평가기 변경 버전/ID와 run-plan의 평가 계약 참조를 갱신한다.
- 새 준비를 실행해 agent 제공142파일·세 ID와 모델/근거가 유지되는지 확인한다. 이번에는 공통 TASK와 B/C 내용을 바꿀 필요가 없다. evaluator metadata만 바뀌는 경우 그 차이를 분리한다. 준비/포장 코드를 바꾸지 않았다면 동일 배포 파일·manifest/hash/allowlist 보존 검사를 하고, 그 코드를 변경했다면 준비 두 번 재현과 실제 workspace 검사도 반복한다.
- 새 로그/교정/trace는 `verification/<완료일>-modal-fix/` 등 기존에 없는 경로에 저장한다. 필요시 새 results 버전을 만들고 과거2026-11-08/2026-11-09 결과·독립 probe/리뷰를 덮어쓰지 않는다. 평가자 전용 자료가 agent allowlist에 들어가지 않아야 한다.

다음 모두 충족하면 **R9 modal 보완 구현 완료·독립 재검토 대기**로 인계한다.

1. 실제 component/locals→dialog 동작→resolve→부모 후속 흐름이 연결되고, 사전 실행/고정 반환/정상 order 복구가 없다.
2. 두 잔여 변형을 실제 Vendure에서 타입 검사 통과 후 payload assertion으로 거부하며, trace로 원인과 결과를 확인할 수 있다.
3. baseline·유효한 참조/helper와 기존13동작 결함, R8/R10·미지원 경계, complete-root CLI의 결과가 계약에 맞는다.
4. 항상 실행되는 연결 fixture·전체 check·비교4/4·교정 반복·모델/배포 보존 검증과 새 원시 증거가 있다. 미완료 통합을 skip/성공으로 숨기지 않는다.
5. README/평가 계약과 현재 문서에 실제 지원 경계·미지원/미정 사항·정확한 재현 명령을 남겼다. 독립 reviewer의 해결 판정을 대신 기록하지 않는다.
6. 본 비교, 최종 과업 정책/사람 의미·B/C 동등성·oracle 충실성 승인, OS 격리·agent 모델/도구/예산/배정 동결, H-O/H-F·S3는 수행하지 않았고 `readyForTrial:false`를 유지한다.

`docs/reviews/<완료일>-s2-modal-fix.md`에 수정 전후 두 반례, 실제 연결 순서/필드 소유권·Observable 계약, 변경 모듈, 교정 행렬과 trace, 타입/실행 지문, 검사 수·재현·남은 한계를 작성한다. PROGRESS/ARCHITECTURE/ROADMAP/REVIEW_CONTEXT와 S2 README/평가 계약을 실제 상태로 갱신한다. 기존 합의 안의 중요한 실행 계약 선택은 DECISIONS에 기록하되 미정 제품 정책을 승인으로 올리지 않는다.

새 프레임워크 실행 환경/의존성 투자가 필요하거나, 기존 가상 과업의 실패 처리·환불 정책을 바꿔야 한다고 판단하면 근거·선택지·권고를 사용자에게 요청한다. 그 선택과 무관한 승인된 수정/검증은 계속한다. 단순한 함수 분리·명령 이름·fixture 구성은 자체 판단한다.

AGENTS/CONTRIBUTING의 지속 승인에 따라 검증 → staged diff 자체 검토 → Conventional Commit → 작업 브랜치 push → PR 생성·자체 검토 → 필수 검사/정확한 head 확인 후 merge → 로컬 main 동기화까지 진행한다. 보호 규칙을 우회하지 않는다. 최종 응답에 완료 보고와 PR 링크를 남겨 이 리뷰 세션에 재검토를 요청할 수 있게 한다.
