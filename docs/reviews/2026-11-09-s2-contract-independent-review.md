# S2 평가 계약 보완 독립 리뷰 — 2026-11-09

**R8과 R10은 검증한 범위에서 해결됐다. R9는 요청 인자 비교 자체는 보완됐지만, 부모→dialog 데이터 전달을 하네스가 우회해 부분 해결이다.** 이 잔여 결함을 고치기 전에는 준비 전체 완료를 인정하거나 본 비교로 넘어갈 수 없다. 합의한 S2 구조·방향은 유지한다.

대상은 PR [#26](https://github.com/hyeonhb/ontosary/pull/26), main `4ed405baf1311dc51f8aac285ca70172a4a18c0f`다. [개발 인계](2026-11-09-s2-contract-fix.md), [보완 지시](2026-11-09-s2-contract-fix-instructions.md), [이전 독립 리뷰](2026-11-09-s2-preparation-independent-review.md)를 코드·새 실행과 대조했다. 작업 브랜치는 `codex/s2-contract-fix-review`, 미병합 의존 브랜치는 없다. 제품/실험 구현·Vendure cache·과거 원시 자료는 수정하지 않았다.

## R9 잔여 · High — 실제 modal 입력을 무시해 잘못된 주문 요청도 합격한다

위치: `experiments/domain-model/s2/evaluation/behavior.ts:69–76`, 특히75행.

하네스는 부모를 실행하기 전에 fixture의 주문으로 dialog를 만들고 `select()`/`cancel()`을 호출한다. 이후 부모의 `modalService.fromComponent`는 인자를 받지 않고 이미 계산한 `returned`를 반환한다. 따라서 제출 코드가 선택한 component와 `options.locals.order`는 dialog 실행에 반영되지 않는다. 최종 payload를 정확히 비교해도, 그 payload가 실제 부모 입력으로 만들어진 값이 아닌 경우를 놓친다.

유효한 새 참조 수정에 다음 변경을 각각 독립 적용했다. 변경 위치는 부모의 `private cancelOrder()`에서 `fromComponent`에 넘기는 `locals.order`뿐이다. 서비스의 payload, dialog 변환, 기대값은 변경하지 않았다.

```ts
// 원래
locals: { order }
// 변형 1
locals: { order: { ...order, id: 'wrong-modal-order' } }
// 변형 2
locals: { order: { ...order, active: true } }
```

| 제출 | 현재 evaluator | 실제 component/locals를 전달해 같은 제출 메서드를 연결한 관찰 |
|---|---|---|
| 새 참조 수정 | 타입 진단0·52/52·overall passed | 주문 `o-one`, 부분 취소 lines 유지: 기대와 일치 |
| 잘못된 modal 주문 ID | 타입 진단0·52/52·overall passed | 취소 payload의 orderId가 `wrong-modal-order`: 실패 |
| 잘못된 modal active | 타입 진단0·52/52·overall passed | inactive 주문의 부분 취소 lines가 생략됨: 실패 |

세 제출 모두 현재 `sourceBinding:true`다. 독립 연결 실행에서도 실제 사용한 파일 hash는 타입 검사 파일과 일치했다. **파일 내용이 같다는 검사만으로는 대역이 데이터 흐름을 보존했는지 알 수 없다.** 이 반례는 타입 검사 실패나 새 미지원 문법 때문에 생긴 것이 아니다.

독립 probe는 Angular를 설치/구동하지 않았다. 제출 부모의 `cancelOrRefund()`에서 시작해 실제 `fromComponent(component, options)` 호출을 받고, 전달된 component의 prototype 및 `options.locals`로 dialog를 준비했다. fixture는 사용자의 reason/항목 선택과 외부 UI/서비스 효과만 공급했다. 실제 dialog `select()` 결과를 부모 Observable에 반환하고 제출 service가 만든 요청을 기록했다. 동일한 연결에서 참조 수정은 기대와 일치하고 두 변형만 달라지므로 하네스의 데이터 전달 단절을 분리해 확인했다. 실제 네트워크나 전체 Angular UI 검증을 뜻하지 않는다.

R9의 원래 service/환불 payload 변형은 이제 검출된다. 남은 문제는 **동일한 잘못된 요청이 부모→dialog 경계에서 만들어지면 여전히 성공으로 측정된다는 것**이다. R9를 전체 해결로 올리지 않고 부분 해결로 유지한다.

## 확인된 해결과 범위

**R8 해결:** 원래 클래스·모듈·호출자 문맥으로 실제 제출을 검사한다. 고정 baseline 진단0, 새 참조와 helper 진단0, 역사적 참조 진단5 거부를 재현했다. helper 타입/구문/누락과 삭제는 실패, Program 밖 변경은 미지원이며 behavior는 not-run이다. 완전한 제출 디렉터리를 만들어 문서의 CLI도 실행했다. 참조 수정은 타입/동작/sourceBinding 통과, 명시적 delta와 submissionId가 같았다. 타입 검사/실행 소스 결합은 개선됐지만 위의 실행 연결 문제까지 해결했다는 의미는 아니다.

**R9 부분 해결:** 독립 기대 payload, 호출 시점 복사, 주문·결제 ID/금액/lines/배송 flag·사유/호출 횟수·순서 검사를 확인했다. 제출된13개 동작 결함은 모두 타입 진단0 후 assertion에서 실패했다. 단, 위 modal 경계 반례2개는52/52로 통과한다.

**R10 해결:** 참조 수정은 실제 취소 lines가 있을 때 guard를 적용하고 취소 payload만 trim한다. 환불만 정상/앞뒤 공백/공백만 reason과 혼합 경로의 환불 reason 보존을 재현했다. `guard-refund-only`·`trim-refund-reason` 변형도 타입 통과 후 검출된다. 이 검증은 가상 과업의 적용 범위에 관한 것이며 실제 Vendure 정책이나 최종 invalid 입력 처리 승인이 아니다.

## 재현·방향성·남은 한계

- `pnpm check`:214테스트(skip0)·타입 검사·예제 빌드 통과. `pnpm experiment`: 기존 비교4/4 통과.
- 새22제출 교정의46개 파일을 커밋된 결과와 대조했다. gzip을 해제하고 wallTimeMs만 제외한 진단·판정·호출·지문이 모두 같다. baseline은 보존16/16·요구6/36, 새 참조/helper는52/52다.
- 새 준비의 비시간147파일이 커밋된2026-11-09 결과와 같다. 2026-11-08 manifest와도 같고, A/B/C 제공142파일과 세 ID를 그대로 유지한다.
- 실제 A/B/C workspace를 다시 생성해 원문4,735개와 자료2/70/70개의 파일 목록·hash를 대조했다. symlink0이며 평가 파일은 복사되지 않았다. 동일 호스트 폴더를 OS 격리 증거로 보지는 않는다.
- 새 독립 반례는 세 제출(reference·modal ID·modal active)의 원래 evaluator 결과와 실제 modal 입력 연결 결과, 완전한 제출 CLI 결과를 보존했다. 환경 지문 재검사도 통과했다.

새 기능의 위치는 S2 실험 내부이며 제품 core/CLI·FCA/논리 지원 범위·S1/V1/V2·모델 의미를 바꾸지 않았다. 준비 Program1회와 제출 평가 Program을 구분하고, 타입/동작/미지원 상태를 나눈 구조는 합의에 맞는다. 기존 코드와 도메인 지식이 agent 수정에 도움이 되는지 알아보려면 평가가 실제 코드의 데이터 흐름도 보존해야 한다. 이번 잔여 결함은 그 측정 경계를 보완할 일이며 온톨로지/FCA 전략이나 큰 아키텍처를 다시 정할 근거는 아니다.

본 비교·H-O/H-F·사람 의미 승인·S3는 미실행/미검증이다. B/C 사람 동등성, oracle 원문 충실성, 과업 실패 처리, 실제 격리·agent 버전/도구/예산/배정 조건은 여전히 미동결이다. `readyForTrial:false` 유지가 맞다. 명시된 constructor/field/HTML/DI/서버·실제 네트워크 scheduling의 제외 범위를 새로 검증했다고 주장하지 않는다.

## 다음 보완과 재검토 조건

수정 범위는 `behavior`의 modal 대역과 관련 fixture/교정 사례다. 기존 제출 타입 검사나 모델·조회 구조를 다시 만들 필요는 없다.

1. 부모 흐름에서 시작해 실제 `fromComponent` 호출 시 전달된 component와 locals를 dialog 실행에 연결한다. 사용자의 선택/dismiss와 외부 효과는 fixture로 대체하되, 부모가 넘긴 order를 별도의 정상 fixture order로 덮어쓰지 않는다.
2. dialog를 사전 실행한 뒤 고정 결과를 반환하는 우회를 없앤다. 지원하지 않는 component/입력/호출 방식이면 명시적 미지원으로 처리한다. 가능한 전달값을 검증/실행할 수 없다면 전체 성공으로 세지 않는다.
3. 이번 modal ID/active 변형은 타입 검사 통과 후 요청 인자 검사에서 실패해야 한다. 실제 전달값 및 생성된 요청을 함께 기록한다. 부모의 component/locals 전달, dialog 선택/dismiss, 부모의 후속 요청까지 연결한 자체 소유 fixture도 추가한다.
4. 기존 참조/helper·보존/새 요구 및13개 동작 결함, 타입 실패/미지원 사례를 유지한다. 기존 교정 결과를 고쳐 쓰지 말고 새 버전에서 실제 상태/분모와 비시간 재현을 남긴다.

이 보완의 독립 재검토 후에 과업/실행 조건 동결로 넘어간다. 현재의 입력 실패 정책 대안을 바꾸거나 새 프레임워크 환경을 설치할 필요는 확인되지 않았다.

## 근거와 실행 방법

[근거 디렉터리](evidence/2026-11-09-s2-contract-review/)의 `probes.json`은 새 반례/연결 관찰/CLI 요약, `probe-reports.json.gz`는 세 제출 및 완전한 CLI의 원시 보고다. `oracle-reproduction.json`은46파일 지문, `oracle-summary.json`은22제출 재실행, `preparation-reproduction.json`은147파일 지문, `deployment-audit.json`은 배포/ID 감사, check/experiment 로그는 기존 검사 결과다. [독립 probe 소스](evidence/2026-11-09-s2-contract-review-probes.mjs)는 원래 cache를 수정하지 않는다.

저장소 root에서 실행하고 각 출력은 새 경로를 사용한다. 검증 환경은 Node22.19.0/TypeScript5.9.3이다.

```sh
pnpm check
pnpm experiment
pnpm s2:build
node work/s2-build/evaluation/oracle-check.js /tmp/ontosary-vendure-preparation-20261108/vendure work/s2-contract-review-20261109/oracle
node work/s2-build/evaluation/verify.js experiments/domain-model/s2/verification/2026-11-09/oracle work/s2-contract-review-20261109/oracle work/s2-contract-review-20261109/oracle-reproduction.json
node work/s2-build/prepare.js /tmp/ontosary-vendure-preparation-20261108/vendure work/s2-contract-review-20261109/prepared
node work/s2-build/verify.js experiments/domain-model/s2/results/2026-11-09 work/s2-contract-review-20261109/prepared work/s2-contract-review-20261109/preparation-reproduction.json
node docs/reviews/evidence/2026-11-09-s2-contract-review-probes.mjs /tmp/ontosary-vendure-preparation-20261108/vendure work/s2-contract-review-20261109/independent
```

workspace는 README의 명령을 A/B/C 각각에 실행하고 inventory/manifest와 파일 목록/SHA-256을 별도 대조했다. 자체 검증의 재현과 새 반례를 함께 보고하며, 이번 리뷰가 추가한 것은 리뷰 문서·독립 probe·검증 증거와 현재 상태 갱신이다.
