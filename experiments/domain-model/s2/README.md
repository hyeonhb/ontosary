# S2 준비 구현 — R9 잔여 보완 필요, 본 비교 미실행

2026-11-09 [독립 재검토](../../../docs/reviews/2026-11-09-s2-contract-independent-review.md): **R8/R10 해결, R9 부분 해결**. 제출 타입 검사·기존 교정은 재현됐으나 실제 modal component/locals를 무시해 부모의 잘못된 주문 ID/active 전달도52/52로 통과한다. 하네스의 데이터 전달 경계 보완이 먼저이며 readyForTrial=false를 유지한다. 아래 인계는 당시 자체 검증 기록이다.

2026-11-09 **R8/R9/R10 보완 구현·검증 인계, 독립 재검토 대기**. [새 보고](../../../docs/reviews/2026-11-09-s2-contract-fix.md), [v2 평가 계약](evaluation/TASK-REVIEW.md). 제출의 원래 타입 문맥/추가 helper와 같은 snapshot의 실행을 결합하고, 전체 요청 payload를 판정한다. 취소 reason 정책을 환불 reason에 확장하지 않는다. baseline 보존16/16·요구6/36, 새 참조와 helper52/52다. 역사적 참조의 TS 오류5개는 전체 합격을 막는다. 아래2026-11-08 수치는 당시 기록이며 현재 평가는 v2/52사례를 따른다.

### v2 제출 평가·교정 명령

```sh
pnpm s2:evaluate <complete-submitted-source-root> <prepared-environment-root> <new-result.json> [repo]
pnpm s2:oracle-check /tmp/ontosary-vendure-preparation-20261108/vendure work/s2-contract-oracle-a
pnpm s2:oracle-check /tmp/ontosary-vendure-preparation-20261108/vendure work/s2-contract-oracle-b
pnpm s2:verify-evaluation work/s2-contract-oracle-a work/s2-contract-oracle-b work/s2-contract-reproduction.json
```

일반 제출은 inventory 원문 전체와 변경/추가 파일을 포함한다. 교정 runner만 baseline+명시적 delta를 사용하며 삭제는 실제 결손으로 남는다. 타입 검사/미지원 시 behavior는 not-run, 전체 판정은 비합격이다. exit0은 결과 수집 완료이며 합격은 overall을 읽는다. `*.json.gz`는 전체 진단/기대·관찰/manifest/hash/원문 대응을 보존한다. 반복 비교는 wallTimeMs만 제외하고 진단·실패를 제외하지 않는다. 준비 Program1회와 평가 baseline Program1회·제출별 Program1회 비용을 분리한다.

새 평가기 버전/지문은 run-plan과 평가 보고에 기록한다. 기존 A/B/C142파일·세 ID는 동일하며 준비147파일 중 evaluator/run-plan metadata만 갱신됐다(timing 별도). 실제 OS 격리와 정책/사람 검토/실행 조건은 미정이고 본 비교는 실행하지 않았다.

### 2026-11-08 준비 구조와 기록

단일 baseline 분석 세션으로 S1 자료를 검증하고, 동결 모델의 순수 조회로 B 구조화 view와 C 일반 문서를 생성한다. 제품 core/API가 아닌 타입 검사되는 실험 내부 모듈이다. [개발 지시](../../../docs/reviews/2026-11-08-s2-development-instructions.md), [설계 메모](DESIGN.md), [원문 고지](../SOURCE-NOTICE.md).

**준비 구현과 실행 가능 판정은 별개다.** 자료와 제출 코드 기반 oracle는 구현했으나 과업 실패 처리·사람 동등성/원문 충실성 검토·agent 버전/예산·격리는 미확정이다. [readiness](results/2026-11-08/evaluator/readiness.json)의 readyForTrial은 false다. agent/chat을 생성하거나 A/B/C 본 비교를 실행하지 않았다.

## 모듈과 계약

- `analysis-session.ts`: open → inspectInputs → verifyEvidence → seal → dispose. Program/Checker 접근과 진단은 한 세션에서 한 번 생성한 Program을 공유한다. SourceTable은 canonical path의 hash와 필요한 text/lineStarts를 재사용한다. 전체 inventory 텍스트를 영구 중복 보관하지 않는다. CompilerHost read 수와 명시 read/hash 및 seal 재읽기를 분리 계측한다.
- `vendure-baseline.ts`: CLI root와 저장소 명세에서 고정 revision, 원문 4,735개, 준비 Program 1,638개, config·repository/S1 hash를 공급한다. 감사 분모를 근거 파일로 축소하지 않는다. 새 설치/빌드는 하지 않는다. 입력 부재/변경은 실제 통합 실패다.
- `model.ts`/`validate.ts`: unknown JSON을 구조·enum·필수 필드·ID/참조 종류·원문 hash/UTF-16 구간·좌표로 검사한다. 승인 ingest는 지원하지 않으며 S1의 pending-review/approvedKnowledge=[]만 유지한다. 오류는 code/field를 가진 실패이고 완료 bundle을 만들지 않는다.
- `query.ts`: compiler/fs/process/LLM 의존 없이 복제한 데이터와 ID/adjacency/evidence index를 소유한다. listItems/getItem/neighbors/getEvidence를 제공하며 반환값도 복제한다. 없는 ID는 NotFound다. neighbors는 R6의 1-hop incoming/outgoing과 원래 from/to를 보존하고 전이 폐쇄/업무 대칭성을 만들지 않는다.
- `bundle.ts`/`prepare.ts`: limits를 적용하고 12항목에서 queue+visited로 fact/candidate 근거 closure를 만든다. 후보의 구성원 선언·역할 정의도 제공한다. 전체 scan은 배포하지 않는다. 원래 object의 무관한 cell refs는 projection에서 제외하고 선택 근거는 evaluator/selection.json에 남긴다. 검증기 통과는 업무 의미 승인이나 S1 artifact의 새로운 사실 증명이 아니다.
- `workspace.ts`: A/B/C allowlist 자료와 고정 원문 inventory만 새 workspace로 복사한다. symlink/경로 이탈/hash 불일치/기존 출력은 거부한다. evaluator/checkout/source map/실행 코드가 agent view에 유입되지 않는다. 실제 OS 접근 제한은 별개로 **unverified**다.

원문 hash는 UTF-8 bytes, TS offset/end는 UTF-16 code unit/배타적 end, line/column은 1-based다. anchor와 긴 method 영역을 구분하며 원문 구간과 표시 문자열은 별도로 보존한다. Unicode/CRLF 회귀가 있다. seal은 실제 입력을 다시 읽고 root membership·해석 중 file/directory lookup 존재 상태도 대조한다. 원자적 live workspace snapshot을 보장하지 않으며 고정 준비 입력을 검증한다. 실패/종료 뒤 verified 결과를 만들지 않는다. 내부 seal 토큰은 WeakSet에만 있고 외부 JSON의 verified=true는 인정하지 않는다.

## 정체성과 의미 보존

baselineId는 revision/policy/Node/TS 및 분석 입력 지문, modelId는 baselineId와 모델·탐색 링크·근거 내용, bundleId는 배포 버전과 allowlist 파일명/hash/bytes를 식별한다. JSON object key는 사전순, 배열 순서는 보존한다. 파일은 UTF-8/LF, 경로는 relative, timestamp/자기 hash는 ID 입력에서 제외한다. evaluator metadata/time는 배포 bundleId의 범위 밖이다. 모델 해석을 바꾸면 modelId가 바뀐다. 다른 revision의 baseline과 모델 결합, 외부 위조 seal을 거부한다.

원래 12항목의 모든 의미/질문/상태 필드를 보존하고 relatedItems는 provenance가 있는 `related-item` 방향 링크 16개로 분리했다. fact/candidate 의존과 navigation을 혼합하지 않고 S3 stale 재연결을 구현하지 않는다. 실제 선택은 fact22/candidate2와 그 구성원·역할 정의/근거다. 기존 5개 FCA 후보 전체의 의미를 바꾸지 않으며 참조되지 않은 후보는 선택 목록에서 제외된다. 두 참조 후보를 조용히 삭제하지 않았다. 승인 지식0/추가 의미0이다.

동결 자료의 상태는 integrity/baselineEvidence/semanticReview/sourceVersion/currentWorkspaceAssessment/partial coverage를 구분한다. **편집 중인 소스의 현재 좌표가 아니라 baseline 좌표**다. 이후 편집본이 바뀌었다고 이 과거 자료를 자동 갱신하거나 현재 사실로 승격하지 않는다.

## 실제 명령

저장소 root에서 Node 22.19.0 / TS 5.9.3 / pnpm 11.19.0으로 검증했다. root 경로는 모든 CLI 인자다. 새 출력 경로를 쓴다.

```sh
pnpm s2:build
pnpm s2:prepare /tmp/ontosary-vendure-preparation-20261108/vendure work/s2-prepare-a
pnpm s2:prepare /tmp/ontosary-vendure-preparation-20261108/vendure work/s2-prepare-b
pnpm s2:verify work/s2-prepare-a work/s2-prepare-b work/s2-reproduction.json
pnpm exec vitest run tests/s2.test.ts
pnpm s2:oracle-check /tmp/ontosary-vendure-preparation-20261108/vendure work/s2-oracle
pnpm s2:evaluate <complete-submitted-source-root> <prepared-environment-root> <new-result.json>
pnpm s2:workspace work/s2-prepare-a /tmp/ontosary-vendure-preparation-20261108/vendure B work/s2-agent-b
pnpm check
pnpm experiment
```

`prepare` 실패는 exit1/구조화 진단이며 publish 전에는 완료 출력이 없다. staging 쓰기 실패도 정리한다. `evaluate` exit0은 관찰 수집을 뜻하고 합격은 각 사례의 pass와 unsupported 상태를 읽어야 한다. 고정 fixture만 채점하지 않고 제출 root의 메서드/지원 helper를 실행한다. 자세한 seam·실패 처리 대안·원문 대응은 [평가자 전용 계약](evaluation/TASK-REVIEW.md), sourceMapping은 [oracle baseline](verification/2026-11-08/oracle-baseline.json)에 있다.

자체 소유 fixture 테스트는 외부 설치/cache 없이 항상 실행된다. Vendure 통합 명령은 cache 부재를 성공/skip으로 처리하지 않는다. 원래 V1/V2와 과거 raw 자료는 보존한다.

## B/C·격리와 평가 준비

[실제 자료](results/2026-11-08): A 공통 TASK/고지, B JSON views, C 동일 value tree를 label/list 단락으로 렌더한 Markdown이다. 목록·12항목·1-hop·fact/candidate·근거의 파일 단위를 맞추고, semantic unit별 양쪽 파일/line과 근거/검토 상태를 [information-parity](results/2026-11-08/evaluator/information-parity.json)에 기록했다. B 133,134 bytes/C 120,100 bytes이며 token 수는 tokenizer 미정으로 null이다. 자동 leaf/참조 coverage 통과와 사람이 읽은 의미 동등성은 구별한다. padding은 없다.

builder로 실제 A/B/C workspace 각 4,735 원문 파일과 allowlist 자료를 만들고 hash/파일 목록을 대조했다. evaluator 파일·symlink는 0이다. 그러나 같은 호스트 권한은 보안 격리가 아니며 VM도 sandbox가 아니다. 실제 비교 전 evaluator 경로와 checkout에 접근할 수 없는 OS/container 정책·공통 dependency runtime mount를 동결해야 한다. 아직 readyForTrial=false이며 workspace의 node_modules는 복사하지 않는다.

[실행 계획](results/2026-11-08/evaluator/run-plan.json)은 실제 B/C 파일 hash·세 ID와 미정 모델/예산/seed/공개-비공개 테스트/격리를 담는다. 반복3회/조건도 제안이지 확정이 아니다. 평가 oracle/참조 수정/제작 로그/과거 MODEL.md의 변경 예시는 agent 파일 allowlist에 없다.

baseline은 보존6/6·가상 요구3/18, 검토용 임시 참조 수정은24/24다. 직접 취소만 수정·trim 누락·강제 취소·dismiss 요청·오류 뒤 환불·후속 환불 누락 변형을 모두 구별했다. [oracle 교정](verification/2026-11-08/oracle-summary.json)은 agent 효용 수치가 아니다. 실패 처리 초안은 invalid 입력의 요청/연쇄 환불을 중단하는 대안이며 실제 제품 정책 승인이 아니다.

## 재현·비용·다음 검토

준비 두 실행의 비시간147파일과 baselineId/modelId/bundleId가 동일하다. timing.json만 제외한다. 첫4.274초/반복4.265초, Program1회, host read1,762, explicit read6,057, hash7,819, seal reread6,134다. RSS는 종료 시점(약683MiB)이고 peak가 아니다. 명시 reads는 전체 감사/근거를 포함하며 host reads와 중복 가능하다. 이전 V2 8.25초는 추출까지 수행했으므로 순수 가속 비율로 비교하지 않는다. 이번에는 검토된 S1 결과를 포장했다.

다음은 독립 리뷰에서 입력·모델·B/C 동등성·oracle 원문 충실성을 확인하고 과업 실패 처리와 실행 조건을 동결하는 것이다. 사람 작성/검토/재작업·agent token/time·변경 효용은 미측정이다. S2 본 비교·S3·Gate 상승을 주장하지 않는다.

실행 하네스는 Promise/async/await 및 검토하지 않은 RxJS operator/scheduler를 명시적 미지원으로 거부한다. 지연 작업 완료 전에 호출 수를 읽어 잘못 통과시키지 않기 위한 범위 제한이다. 더 넓은 비동기 해법은 별도 harness 확장이 필요하며 과업 실패로 단정하지 않는다.
