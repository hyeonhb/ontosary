# S2 준비 구현 독립 리뷰 — 2026-11-09

**방향과 분석 세션·모델·조회·배포 구조는 유지한다. 평가 하네스의 R8/R9와 참조 수정의 R10을 보완하기 전에는 준비 전체의 완료를 인정하거나 본 비교로 넘어갈 수 없다.** 본 비교를 실행하지 않고 readyForTrial=false로 남긴 판단은 적절했다.

대상은 PR [#23](https://github.com/hyeonhb/ontosary/pull/23), main `8007771cb9a248a5040565d96a58d4b6e177087c`다. [개발 보고](2026-11-08-s2-preparation.md)와 [개발 지시](2026-11-08-s2-development-instructions.md)를 실제 코드·새 실행·독립 반례에 대조했다. 이 리뷰는 제품/실험 구현을 고치지 않았고 원래 Vendure cache와 과거 증거를 보존했다. 작업 브랜치는 `codex/s2-preparation-review`, 미병합 의존 브랜치는 없다.

## 수정이 필요한 발견

### R8 · High — 타입 오류가 있는 참조 수정을 모든 사례 통과로 인정한다

위치: `experiments/domain-model/s2/evaluation/execute.ts:51`, `evaluation/oracle-check.ts:31`.

executor는 `transpileModule`로 실행할 JavaScript를 만들며 제출의 TypeScript 진단을 검사하지 않는다. 현재 참조 수정은 service의 invalid reason 처리에 `of(undefined)`를 추가한다. 이 수정은 실제 고정 RxJS/호출자 타입 문맥에서 반환 타입을 바꾸고, 부모의 `.pipe(map(...))` 및 후속 환불 흐름에 타입 오류를 만든다.

동일 준비 설정/Program 1,638파일을 사용하고 네 파일의 내용만 메모리에서 참조 수정으로 교체해 검사했다. baseline 진단은 **0개**, 참조 수정은 **5개**다. 실제 override된 본문도 대조했다. TS2554(617행), TS18046(618행), TS2339(647·649행), TS2488(659행)이 `OrderDetailComponent`에서 발생한다. 그런데 기존 oracle는 참조 수정을 **보존6/6·새 요구18/18**로 인정한다. Ontosary의 `pnpm check`는 실험 모듈을 검사하므로 이 제출 코드 문제를 대신 찾지 못한다.

이 상태로 비교하면 agent가 빌드할 수 없는 수정을 만들어도 성공 수치가 올라갈 수 있다. 참조 수정 자체를 실제 지원 타입 문맥에서 유효하게 고치고, 평가 결과에 **제출의 타입/구문 검증과 동작 검증을 별도 상태로 기록**해야 한다. 고정 baseline의 진단0을 기준으로 새 오류를 거부하며, 제출에 추가한 helper도 검사 범위에 포함한다. 타입 검사 범위를 마련할 수 없는 제출은 미검증/미지원으로 남긴다. 이는 제출 평가 단계의 검사이며 준비 단계의 단일 Program 원칙을 바꿀 이유는 없다. 새 Angular/DB 설치도 필요하지 않았다.

### R9 · High — 잘못된 주문·결제·금액을 보내도 oracle를 전부 통과한다

위치: `experiments/domain-model/s2/evaluation/run.ts:52–60`, `:89`.

현재 판정은 대부분 호출 수/종류/순서와 reason만 검사한다. 직접 취소의 두 보존 사례는 lines도 보지만 주문 ID는 보지 않고, 환불만 사례는 refund 호출 수만 본다. 기록된 인자가 있다는 것과 인자를 판정한다는 것은 다르다.

참조 수정에서 각각 다음 한 가지 결함을 추가해 원래 평가기를 그대로 실행했다.

| 독립 결함 변형 | 실제 관찰 | 원래 oracle |
|---|---|---|
| 취소 대상 ID 변경 | `orderId: 'o'` 대신 `'wrong-order'` 전송 | 보존6/6·새 요구18/18 |
| 환불 대상·금액 변경 | `paymentId: 'p', amount: 10` 대신 `'wrong-payment', 999999` 전송 | 보존6/6·새 요구18/18 |

두 변형은 기존 참조 수정에 결함을 추가한 것이며 별도 타입 검사 통과를 주장하지 않는다. 핵심은 **현재 동작 판정이 잘못된 외부 요청을 관찰하고도 실패시키지 않는다는 것**이다. R8을 고치는 것과 별개로 보완해야 한다.

기대 요청의 주문/결제 ID, 취소·환불 lines의 ID/수량, amount/shipping/adjustment/cancelShipping 등 과업 중 보존해야 할 인자를 명시하고 대조한다. 새 reason 요구가 적용되는 필드와 보존할 필드를 구분한다. 호출 수·순서·불필요한 추가 요청도 함께 확인한다. 위 두 변형과 환불중취소 lines 변형을 부정 교정에 추가해 모두 거부해야 한다. 모든 프로그램 오류를 잡으라는 요구가 아니라, 이번 fixture가 이미 관찰하는 핵심 요청 계약을 검사하라는 요구다.

### R10 · Medium — 참조 수정이 취소 없는 환불의 기존 동작도 바꾼다

위치: `experiments/domain-model/s2/evaluation/oracle-check.ts:27–31`, `evaluation/run.ts:71`.

가상 요구는 취소 요청의 reason을 trim/nonblank로 제한하고 기존 환불 동작을 보존하는 것이다. 그러나 참조 수정은 `RefundOrderDialogComponent.select()` 시작에서 취소 항목 유무와 관계없이 공백 reason을 거부한다. 원래의 `canSubmit()`은 reason의 truthiness를 검사하므로 공백 문자열 자체는 이 조건을 통과한다.

원래 runner에 `refund-only` + `'   '` 보존 사례 하나만 추가했다. baseline은 **7/7**, 참조 수정은 **6/7**이며 이 추가 사례에서 환불 요청이 사라진다. 원래 oracle는 refund-only를 `'normal'` 한 값으로만 검사해 이를 놓쳤다. 이는 미확정 invalid 취소 처리 방식과는 별개인 **요구 적용 범위의 회귀**다.

현재 범위에서는 취소가 실제로 포함될 때만 새 취소 정책을 적용하고 환불만 경로를 보존하는 것을 권한다. 환불 reason까지 함께 강화하려면 과업 범위를 바꾸는 결정이므로 사용자와 먼저 합의해야 한다. 참조 수정·과업 문장·보존 사례가 같은 범위를 가리키도록 맞추고, 환불만 경로에 공백 포함/공백만 입력을 추가한다. 이번 리뷰가 실제 Vendure 정책을 승인하는 것은 아니다.

## 목표·아키텍처 적합성

이번 구현은 기존 코드를 모델에 맞게 재작성하거나 온톨로지 형식을 강요하지 않는다. S1 근거를 동결해 agent 수정에 도움이 되는지 시험하는 S2 범위에 맞는다. FCA를 다시 돌려 효과를 꾸미지 않았고, 모델 사용 효과 H-O와 구축 기여 H-F도 분리했다. 방향 전환이나 새 코어 아키텍처는 필요하지 않다. 지금 우선할 일은 **효과를 측정할 평가기의 정확성**이다.

확인한 구조는 단일 준비 Program, 입력 재검사 후 seal/dispose, 코드 사실/후보/의미 검토의 분리, baseline/model/bundle ID, 순수 조회와 복사 소유권, 방향을 보존한 1-hop, 사전 생성 B/C view다. S1의 12항목 모든 source 필드와 16링크를 원본에 대조했고 전체 1-hop 출력도 일치했다. 선택된 fact22/candidate2와 근거 view30개를 제공하며 승인 지식은 계속 0이다. 제품 core/CLI와 과거 S1/V1/V2를 변경하지 않았다.

| 완료 조건 | 독립 판정 |
|---|---|
| 타입 검사되는 모듈·조회 경계 | 충족. 단, 제출 코드의 타입 검사는 R8 별개 |
| 실제 baseline 감사·S1 재사용 | 충족. 동일 준비 cache에서 원문4,735·Program1,638·진단0, Program1회 |
| 모델 의미 필드·관계·근거 보존 | 검토한 고정 입력에서 충족. 업무 의미 승인은 pending |
| 실제 B/C·manifest·allowlist·대응표 | 산출물/파일 무결성 확인. 사람 의미 동등성은 pending 유지 |
| 제출 코드와 연결된 oracle·교정 | 연결은 실제 구현됐으나 **R8/R9/R10 보완 필요** |
| 실행 명세·readiness | 미정 조건을 명시하고 readyForTrial=false 유지, 적절 |
| 회귀·통합·재현 | 기존 검사와 보고된 재현 통과. 독립 반례는 위 3문제 검출 |
| 인계·저장소 반영 | 개발 PR #23 병합 확인. 완료 판정은 이 리뷰로 갱신 |

## 배포·정보 동등성·실행 경계

새 A/B/C workspace를 각각 만들고 **원문4,735개 + 자료 A2/B70/C70개**가 예상 파일 목록/hash와 정확히 같은지 다시 검사했다. symlink는 0개이고 평가 파일은 복사되지 않았다. 동일 호스트에서 만들었다는 사실은 OS 격리 증명이 아니므로 isolation=unverified를 유지한다.

B/C 68쌍이 실제로 존재하며 B 133,134 bytes/C 120,100 bytes다. 같은 값 트리로 렌더하는 코드와 대표 C 문서의 항목·근거·상태를 읽었다. 사람이 의미 동등성을 승인했다고 기록하지 않는다. C는 아직 label/들여쓰기 중심의 데이터 전개다. 일반 문서 대조군을 동결하기 전에는 빈 목록의 명시, 실제 Markdown 렌더의 계층/가독성, ID에서 파일을 찾는 안내를 검토할 필요가 있다. B/C 비교가 의미 정보의 추가 효과와 표현 형식의 차이를 혼동하지 않도록 같은 명제·근거·질문을 계속 유지해야 한다.

constructor/field/Angular HTML/DI/서버/실제 비동기 네트워크를 평가하지 않는 제한은 명시돼 있다. 동기 예외/stream error 해법의 정책, agent 모델·버전·도구·예산·배정·공개 테스트·격리는 아직 미확정이다. 이 미정 상태 자체를 신규 결함으로 세지 않았다. 다만 oracle 충실성은 위 반례 때문에 승인할 수 없다. 사람 의미 검토, B/C 검토, oracle 검토는 각각 별도다.

## 성능과 남긴 구현 부채

새 준비 2회의 비시간147파일 및 세 ID가 서로 일치하고, 커밋된 결과와도 byte 단위로 일치했다. 각 준비 Program은 1회다. 첫 준비 약4.52초, seal 약222ms, 종료 RSS710,230,016 bytes였다. peak 메모리나 이전 V2 대비 순수 가속 배수는 아니다. 전체 oracle 교정 8변형은 약3.18초다.

이번 고정 규모에서 성능 실패는 관찰하지 않았다. 다음은 **본 실험을 막는 세 결함과 구분한 후속 정리 후보**다.

- `closure()`는 queue+visited가 있지만 매번 `shift()`와 fact/candidate `.find()`를 사용한다. 범위를 넓힐 때 ID Map과 배열 cursor로 바꾸면 반복 선형 탐색을 줄일 수 있다. `query` adjacency 구성도 배열 spread로 기존 목록을 반복 복사한다. 지금의 12항목/16링크 때문에 대규모 자료구조를 도입할 이유는 없다.
- `position()`은 lineStarts를 선형 탐색한다. 큰 파일의 근거 수가 늘면 이진 탐색을 검토한다. 전체 inventory hash 단계에서 불필요한 text/lineStarts 계산도 분리할 수 있다. 현재 우선순위는 준비 시간 최적화보다 oracle다.
- `metrics.hashes`는 explicit read와 CompilerHost read의 hash만 증가시키고, Program source 배열의 hash 재계산은 더하지 않는다. seal은 별도 count다. 이를 전체 hash 호출 수로 해석하면 안 된다. 지표 이름/분모를 명확히 하거나 모든 경로를 계측해야 한다.
- `RecordData`와 여러 동작을 한 줄에 합친 함수가 많아 타입 검사 통과만으로 세부 계약이 읽기 쉬워진 것은 아니다. runtime adapter 이후의 item/fact/candidate 상태를 더 구체적인 타입으로 표현하고 parser/renderer/평가 시나리오의 가독성을 개선할 여지가 있다. 제품 API 승격은 여전히 후속 판단이다.

## 검증과 재검토 조건

환경은 Node v22.19.0 / TypeScript5.9.3이며 기존 준비 의존성을 재사용했다. `pnpm check`의 전체196테스트(skip0)·타입 검사·예제 빌드, `pnpm experiment`의 비교4/4를 확인했다. 원래 oracle의 baseline/참조/6결함 결과도 재현했다. 독립 probe는 기존 evaluator와 한 사례를 추가한 evaluator를 구분해 저장했고, 참조 수정 타입 검사는 실제 준비 설정을 사용했다. agent 비교·새 설치·업무 의미 승인·S3는 수행하지 않았다.

재현 명령(저장소 root, 새 출력 디렉터리 사용):

```sh
pnpm check
pnpm experiment
pnpm s2:build
node work/s2-build/prepare.js /tmp/ontosary-vendure-preparation-20261108/vendure work/s2-review-20261109/prepared-a
node work/s2-build/prepare.js /tmp/ontosary-vendure-preparation-20261108/vendure work/s2-review-20261109/prepared-b
node work/s2-build/verify.js work/s2-review-20261109/prepared-a work/s2-review-20261109/prepared-b work/s2-review-20261109/reproduction.json
node work/s2-build/verify.js experiments/domain-model/s2/results/2026-11-08 work/s2-review-20261109/prepared-a work/s2-review-20261109/committed-reproduction.json
node work/s2-build/evaluation/oracle-check.js /tmp/ontosary-vendure-preparation-20261108/vendure work/s2-review-20261109/oracle
node docs/reviews/evidence/2026-11-09-s2-review-probes.mjs /tmp/ontosary-vendure-preparation-20261108/vendure work/s2-review-20261109/probes
```

workspace 검사는 README의 명령을 A/B/C 각각에 실행한 뒤 inventory/manifest로 파일 목록과 SHA-256을 별도 대조했다. [근거 디렉터리](evidence/2026-11-09-s2-review/): `probes.json`은 반례·타입 진단 요약, `probe-cases.json.gz`는 실제 8회 평가 원시 결과, `bundle-audit.json`은 배포/모델 대조, 두 reproduction JSON은 147파일 hash, `preparation.json`은 두 준비 측정, 나머지는 기존 검사·oracle 재실행 기록이다. [probe 소스](evidence/2026-11-09-s2-review-probes.mjs)는 baseline cache를 수정하지 않는다.

다음 보완의 완료 기준은 **타입 오류 제출 거부 + 유효한 참조 수정 + 잘못된 요청 인자 변형 거부 + 환불만 보존 사례 통과**다. 원래 6결함도 계속 구별하고 새로운 결과는 별도 날짜/버전으로 남긴다. 보완을 재검토한 뒤 과업 실패 처리·B/C 문서·실행 격리와 agent 조건을 사용자와 동결한다. 현재 합의한 구조를 새로 설계하거나 S3로 범위를 넓힐 단계는 아니다.
