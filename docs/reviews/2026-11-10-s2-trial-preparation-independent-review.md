# S2 실행 전 준비 독립 리뷰 — 2026-11-10

**방향과 자료·평가 준비는 적절하다. 전체 실행 준비는 미완료이며 비교 실행 차단을 유지한다.** 개발자가 보고한 종료 경계 결함을 재현했고, usage의 불완전한 이벤트 기록을 완전한 계측으로 표시하는 결함을 추가 확인했다. API 실행기 확대나 token hard cap 복원은 필요하지 않다.

대상: PR #32/main `c6d0933`의 [인계](2026-11-10-s2-trial-preparation.md), [개발 지시](2026-11-10-s2-trial-preparation-instructions.md)와 ADR-029의 후속 합의. 별도 문서 worktree에서 검증했고 원래 개발 checkout은 clean detached 상태로 유지했다. 제품/실험 구현·고정 cache·역사적 증거를 수정하지 않았다. 실제 모델 호출과 비교 실행은 모두0회다.

## R11 · High · 알려진 자손 프로세스 종료 차단 재현

위치: [`runtime.ts` 24–31행](../../experiments/domain-model/s2/trial/runtime.ts). `runTool`은 새 process group으로 실행한 뒤 `process.kill(-pid, SIGKILL)`로 해당 그룹을 종료한다. 별도 세션/그룹을 만든 자손은 이 종료 대상에서 빠진다.

기존 `trial/probe.ts`를 새 경로에 재실행했다. 허용 파일 읽기/편집·외부 canary/상위 경로/symlink/control·외부 TCP/Unix socket 거부 및 snapshot 쓰기 거부는 통과했다. 그러나350ms 제한에서 실행기 그룹은 약355ms에 끝나도 detached 자손이 이후 파일을 작성했다. `detachedDescendantContained:false`가 재현됐다. 이는 개발자가 이미 보고한 문제이며 새로 발견한 결함으로 부풀리지 않는다.

살아 있는 writer가 남아 있으면 마감 뒤 원본 변경·후속 실행 자원 사용을 막지 못하고 수집 시점의 안정성을 보장할 수 없다. 복사 전후 hash 검사는 관찰된 변경을 거부하지만 모든 writer의 정지를 증명하지 않는다. 따라서 현재 `trialAuthorized/readyForTrial:false`와 실제 실행 진입점의 거부는 적절하다.

**보완 기준:** 정상 종료·timeout 모두에서 허용되지 않은 잔존 writer/자손이 없고, deadline 이후 source/auxiliary를 변경하거나 다음 실행에 접근할 수 없음을 같은 권한의 실제 반례로 확인한다. 프로세스 목록 한 번 조회나 chmod만으로 완료 판정하지 않는다. 기존 CLI/macOS 범위 안의 종료·수집 경계 보완을 우선 검토하되, 새로운 플랫폼/권한 투자가 필요하면 비용과 대안을 사용자와 결정한다. 이번 리뷰는 어떤 native 방법이 모든 자손을 강제 종료할 수 있다고 단정하지 않는다.

## R12 · Medium · usage 완료 판정이 turn 상태 대신 이벤트 개수를 사용

위치: [`telemetry.ts` 19–29행](../../experiments/domain-model/s2/trial/telemetry.ts). started 횟수와 고유 usage ID 개수만 비교하므로, 완료 이벤트가 어느 turn을 끝냈는지와 마지막 turn이 실제 완료됐는지를 검증하지 않는다. JSON 문법이 맞는 null도 구조 검사 없이 `.type`을 읽어 예외를 낸다.

[독립 probe](evidence/2026-11-10-s2-trial-review-probes.mjs)의 작은 JSONL 입력으로 다음을 확인했다. 실제 공급자 로그에서 발생했다는 주장은 아니며, 불완전/모순 로그를 처리하는 계측 계약의 부정 사례다.

| 입력 | 현재 결과 | 필요한 처리 |
|---|---|---|
| started → completed(input10/output2) | complete=true, total12 | 정상 |
| started → completed → started | complete=false, total=null | 정상적으로 누락 검출 |
| started 없이 completed만 있음 | complete=true, total12 | 누락/비정상 수명주기를 표시하고 전체 비용 확정 금지 |
| 첫 turn 뒤 서로 다른 ID의 completed2개 → 둘째 started만 있음 | complete=true, total24 | 모순 완료를 탐지하고 미완료 둘째 turn의 비용을 unknown으로 유지 |
| JSON null | TypeError로 집계 중단 | 구조 오류를 기록하고 가능한 원시 관찰은 보존 |

두 완료 이벤트가 같은 turn에 나타나는 경우를 새로운 두 소비량이라고 합산하면, 후속 미완료 turn의 누락이 가려지고 신뢰할 수 없는24가 전체 비용으로 보고된다. 이는 hard cap 부재의 문제가 아니다. 관측 비용의 완전성과 불확실성을 잘못 표시하는 문제다.

**보완 기준:** 공개된 실제 이벤트 계약에 맞춰 turn 시작/완료/실패 상태를 추적한다. 고유 event ID와 turn identity를 혼동하지 않고, ID가 없는 경우에도 활성 turn의 상태를 관리한다. 중복/상충 완료·시작 누락·끝나지 않은 turn·구조 오류·로그 절단/timeout 정보를 구분한다. 불완전하면 total=null이며 신뢰 가능한 관찰 합계/하한과 원시 증거만 남긴다. 모순된 중복을 관찰 하한에도 무조건 더하지 않는다. 정상 완료와 동일 이벤트 재전달 회귀를 유지한다. API 호출이나 새 token 제한은 필요하지 않다.

## 검증된 구현과 자료

- `pnpm check`: **252테스트 통과, skip0**, 타입 검사·예제 production build 통과. `pnpm experiment`: 기존 비교4/4 통과.
- 복제된 read-only 평가 환경에서 새29제출 교정을 실행했다. 커밋된 결과와 gzip 해제 후 **60파일**이 wallTimeMs만 제외하고 일치했다. baseline 보존16/16·새 요구6/36, reference/helper52/52이며 기존15개와 종료 정책5개, 총20개 동작 결함은 타입 통과 후 실패한다. R8/R9/R10을 유지한다.
- 새 배포를 생성해 커밋 결과와 **157비시간 파일**을 대조했다. 기존 baselineId/modelId, 모델12항목/16링크·승인0, B68view의 bytes가 유지됐다. TASK/C 변화에 따른 새 bundleId와 agent84파일은 타당하다. 이전142파일 수를 억지로 유지하지 않았다.
- 기존 cache를 읽어 새 public 환경을 구성했다. source4735파일과 dependency85416항목의 지문을 확인했고 새 설치/빌드는 하지 않았다. 실제 A/B/C workspace에서 공통 TASK/RUN·정확한 배포 hash·원문·공개 타입 검사·읽기 전용 자료·다른 조건/checkout/cache 접근 거부를 확인했다.
- 공개 타입 검사7제출을 다시 실행해 같은 제출의 private 타입 진단 code/file/line/message 및 Program 분모와 대조했다. baseline/reference/helper는 통과, 타입/구문/helper 누락/모듈 삭제는 실패했다. 공개 타입 검사 통과가 private 지원 범위/동작 합격을 뜻하지 않는다.
- 참조 수정의 완전한 source와 auxiliary를 snapshot으로 수집해 제한된 `evaluate-snapshot` CLI로 평가했다. 새 delta 교정의 submissionId·52개 사례/요청/modal/종료 관찰·sourceBinding·evaluatorId와 대조했다. 알려진 유한 참조 제출의 결과이며 R11의 전체 종료 문제를 해결하지 않는다.
- 실행 명세의9개 항목은 모두 not-run이고 조건별3회·블록/위치 균형을 유지한다. hard cap은 false,100,000은 관측 참고선이다. 원시 usage의 cache/추론 중복 합산을 피한 정상 fixture는100,004로 재현됐다. `s2:trial:run`은 거부하도록 구현돼 있다.

새 [검증 근거](evidence/2026-11-10-s2-trial-review/)에 로그, 교정 요약/60파일 hash, 준비157파일 hash, 실제 접근 probe, 독립 반례, 공개/private 대조와 배포/참조 제출 감사를 보존한다. 29제출 원시는 커밋된 [v4 교정](../../experiments/domain-model/s2/verification/2026-11-10-trial-preparation/oracle/)과 비교 hash로 연결한다. 새 배치/준비 각각1회를 커밋 결과와 비교했으며 독립 반복2회를 실행했다고 표현하지 않는다.

## C 의미 대응과 아키텍처 평가

C는 네 개의 개념/관찰/역할/근거 문서로 바뀌어 이전 필드 목록보다 읽기 좋아졌다. 변경 전12개 해석·미확인 질문,22개 코드 주장,2개 후보의 멤버/역할,32개 방향 있는 이웃 표시(고유 링크16개의 양쪽 조회),30개 원문 인용을 기존 B와 대조했다. 확인한 업무 문장/관계/근거에서 의미 손실이나 새 과업 해법 주입은 발견하지 않았다. 승인0·pending/부분 coverage를 유지한다. 이는 **독립 agent 검토**이며 사람의 의미 동등성 승인으로 바꾸지 않는다.

1511개 leaf 대응과 `auditProse`는 누락/변경을 추적하는 데 유용하다. 같은 renderer로 기대 문서를 재생성해 비교하므로 템플릿 자체의 의미 오류를 독립 증명하는 검사는 아니다. 이번 구현/보고서는 그 한계를 명시했고 사람 검토를 pending으로 남겼다. 고정 자료의 drift 검증과 별도 문장/원문 대조를 함께 유지하면 된다. 토큰 수를 맞추기 위한 정보 삭제나 모델 내용을 변경할 근거는 발견하지 않았다.

`trial`을 제품 core 밖에 둔 선택과 API 실행기를 추가하지 않은 범위는 합의에 맞는다. 종료/계측·source 수집·public type check의 책임도 구분돼 있다. 다만 `prose.ts`의 `Record<string, any>`와 telemetry의 `any` JSON은 입력 계약을 타입으로 표현하기에 약하다. 지금 범용 계층을 추가하기보다, R12 보완 때 이벤트를 unknown에서 검증하고 C renderer는 실제 view union으로 좁히는 정도를 권한다. 현재 유한 자료에서 성능 최적화나 새 데이터베이스가 필요하다는 근거는 없다.

## 다음 단계

우선 R11 종료/수집 경계와 R12 계측 상태를 보완한다. C 사람 대응 검토 묶음은 그와 독립적으로 검토할 수 있다. 실제 CLI의 도구 inventory·인증 경로·전역 지시/플러그인 유입 배제, 정확한 모델 버전의 관측 가능 범위와 자원 정책은 아직 미검증/미동결이다. 도구 대역의 접근 거부를 실제 모델 세션 전체의 검증으로 확대하지 않는다.

이번 단계의 비용 절감 결정은 유지한다. strict token cap·API 실행기·전체 Angular 실행을 새 요구로 추가하지 않는다. 종료 문제의 해결이 큰 인프라 투자로 번지면 구체적 최소 대안과 한계를 먼저 논의한다. 기술 보완·사람 대응 검토·남은 환경 확인 뒤 준비 결과를 다시 리뷰하며, 실제 모델 연결 점검/비교는 별도 승인 전에 수행하지 않는다. `trialAuthorized:false`, `readyForTrial:false`, H-O/H-F 미검증·S3 미착수를 유지한다.
