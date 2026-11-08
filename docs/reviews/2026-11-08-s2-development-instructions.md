# 개발 세션 지시 — S2 준비 구현과 독립 리뷰 인계

작성: 2026-11-08. 기준 main `0e422a7ba22563a3c585ac7c53b9088513658f61`. 실제 작업은 **이 지시가 반영된 최신 main**에서 시작한다. 이 문서는 평가·개발용이며 비교 agent의 제공 자료에 포함하지 않는다.

## 1. 목표와 승인 범위

사용자는 S2에서 **변경 전 도메인 모델이 agent의 코드 수정에 도움이 되는지** 먼저 검증하기로 했고, [제안 아키텍처](2026-11-08-s2-architecture-proposal.md)를 승인했다. 이번 작업은 그 구조로 실험 준비물을 구현·검증해 독립 리뷰에 넘기는 것이다. 완료를 ‘S2 효용 입증’이나 ‘본 비교 실행 완료’로 표시하지 않는다.

최종 목표는 기존 프로젝트를 agent가 도메인을 이해하고 수정하기 좋은 프로젝트로 점진적으로 전환하도록 돕는 것이다. 온톨로지는 명시적 지식의 수단, FCA는 구축 비용을 줄일 후보 발견 수단이다. S2는 모델 사용 효과 H-O를 본다. FCA의 추가 기여 H-F를 이 결과로 입증하지 않는다.

합의한 구조:

1. 준비 단계의 단일 baseline 분석 세션: Program/Checker/진단/소스 근거를 배치 안에서 재사용하고 종료한다.
2. 불변 모델 묶음과 Compiler API·파일시스템에 의존하지 않는 순수 조회 계층.
3. 조회 결과를 파일로 사전 생성한다. A/B/C agent는 동일한 파일 읽기·검색·수정 도구를 사용한다.
4. 새 모듈은 타입 검사를 받는 S2 실험 내부에 둔다. 제품 core/public API로 승격하지 않는다.

**이번 완료 지점:** 선행 부채 정리, 준비 세션/모델/조회 구현, 실제 B/C 제공 자료, 평가 과업·fixture/oracle·실행 절차의 검토 가능한 초안, 재현·부정 검증과 인계 보고서. 본 비교는 독립 리뷰와 실행 조건 동결 후 별도 진행한다. 과업/모델 버전·예산 등 미정 내용을 임의로 확정하거나 사람 검토를 대행한 것으로 표시하지 않는다.

## 2. 먼저 복원할 맥락

PROGRESS → ARCHITECTURE → ROADMAP → DECISIONS ADR-020~024 → 아래 자료 순으로 읽는다.

- [현재 구조 제안](2026-11-08-s2-architecture-proposal.md), [구현 감사와 측정](2026-11-08-architecture-audit.md).
- [S1 보완 독립 리뷰](2026-11-08-domain-model-contract-independent-review.md).
- `experiments/domain-model/v2/README.md`, `v2/agent-input-manifest.json`, `v1/manifest.json`.
- `experiments/domain-model/results/2026-11-08-v2/`의 모델·facts·FCA·navigation·validation 결과.
- `experiments/domain-model/evaluation/S2-PROTOCOL.md`: 역사적 미실행 초안이며 그대로 보존한다.
- AGENTS.md / CONTRIBUTING.md의 검증·저장소 반영 규칙.

기존 상태: 174테스트, S1 12개 검토 대기 항목/승인 지식 0, 78메서드×6역할, unknown 0, FCA 8개 형식 개념/5후보. 5후보 전부 단순 그룹과 extent가 같고 추가 의미는 0이다. 전체 core scan은 327파일/2,264함수/4,288속성이므로 이 전체 context를 S2에서 다시 FCA에 넣지 않는다.

입력은 Vendure v3.5.0 revision `534e6003534f74761e82de1b8c6061cba89945d1`, 준비 cache `/tmp/ontosary-vendure-preparation-20261108/vendure`, 설정 `packages/admin-ui/ontosary.scope.json`이다. 경로는 CLI/명세 인자로 받아 코드에 박지 않는다. 기존 관찰 환경은 Node 22.19.0 / TypeScript 5.9.3 / pnpm 11.19.0이다. 실제 사용 버전과 입력 지문을 보고한다.

cache는 읽기 전용으로 사용한다. 없거나 지문이 다르면 작은 fixture 기반 구현·검증은 계속할 수 있지만 실제 Vendure 준비 완료는 주장하지 않는다. 종료된 설치/빌드 준비 예산을 다시 열지 않고, 이미 존재하는 올바른 cache를 찾는 수준을 넘는 환경 투자가 필요하면 이유·선택지·권고를 인계한다.

## 3. 선행 부채와 제외 범위

| 먼저 정리 | 구현 범위 |
|---|---|
| snapshot/모델/배포 정체성 부재 | baselineId/modelId/bundleId와 버전·지문 계약 |
| 실험 JSON의 약한 입력 계약 | 런타임 구조 검사, 참조 무결성, 근거 검사, 의미 승인 상태 분리 |
| 탐색/근거 의존 혼용 | navigation links와 fact/candidate refs 분리, 자동 변경 전파는 제외 |
| agent 자료의 결합/평가 자료 유입 위험 | allowlist 포장, B/C 명제 대응표, 제공 영역과 평가 영역 분리 |
| 특정 로컬 cache 의존 회귀 | 항상 실행되는 자체 소유 TS fixture와 명시적 Vendure 통합 검증 |
| 준비 단계의 중복 Program/I/O | 한 Program 및 세션 내 SourceTable 재사용, 전체 입력 감사 유지 |

core/CLI 공개 계약, 기존 strict/미지원 경계, FCA 상한·속성·알고리즘, 논리 지원 범위, V1/V2 코드·입력·역사적 결과는 바꾸지 않는다. S3의 근거 재연결·정밀 stale 전파·안정 ID 매칭·증분 cache·승인 workflow를 넣지 않는다. graph DB/OWL/RDF/MCP/동적 agent 전용 도구/LLM 호출/새 제3자 의존성·대규모 core 리팩터링은 범위 밖이다.

`package.json`의 실험 build/typecheck/명령 추가, 별도 실험 tsconfig, tests와 새 fixture, 현재 상태 문서 갱신은 허용한다. 기존 검사 범위를 줄이지 않는다. 성능 정리 때문에 범위가 커지면 정확성/배포 계약을 먼저 완료하고, 중복 비용과 남긴 이유를 명시한다.

## 4. 구현 순서

### 단계 0 — 입력과 계약 목록을 먼저 고정

원격/브랜치/사용자 변경을 확인하고 짧은 작업 브랜치에서 시작한다. 기준 HEAD·S1 artifact 지문·기존 입력 감사 분모를 기록한다. 파일/함수 수준 설계 메모와 공개할 내부 타입·명령·실패 상태를 먼저 작성한다. 아래 확정 구조 안의 이름/파일 분할 등은 개발 판단으로 처리하며 반복 승인을 요청하지 않는다.

입력 명세에는 source revision, TS/도구 버전, config/extends·해석 입력, 기존 inventory/Program manifest, S1 artifact hash, 정책/스키마 버전을 포함한다. 과업 정답이나 평가 기대값을 bundle builder의 입력으로 연결하지 않는다.

레코드 수와 근거 closure의 byte 크기를 읽기 전용으로 집계한 후 `limits.json`에 item/edge/fact/candidate/evidence/개별 view/총 비압축 byte 한도를 숫자로 고정한다. 현재 입력 크기·여유폭·선정 이유를 기록한다. **최종 제공 결과를 보고 일부를 삭제해 한도에 맞추거나, 초과 시 자동으로 상한을 올리지 않는다.** 시작 전 한도 검사가 실제 실행 경로에 있어야 한다. 12개 항목과 그 참조를 모두 보존할 수 없는 경우 명시적 실패로 보고한다.

### 단계 1 — 타입 검사되는 실험 모듈과 작은 fixture

기본 배치:

```text
experiments/domain-model/s2/
  lib/analysis-session.ts
  lib/model.ts
  lib/validate.ts
  lib/query.ts
  lib/bundle.ts
  prepare.ts
  vendure-baseline.ts
  README.md
  limits.json
  evaluation/                    # agent 배포에서는 제외
tests/fixtures/domain-model-s2/   # 자체 소유, 외부 설치 없이 동작
```

별도 tsconfig로 새 TS 코드를 검사하고 `pnpm check`에서 해당 검사를 실행한다. 작은 TS fixture는 호출 지점 파일, 대상 선언 파일, import/설정 의존, 실패·누락 사례를 재현할 수 있어야 한다. 새 타입을 `any`로 우회하거나 `.mjs` 구현을 타입 검사 밖에 두지 않는다. 기존 JS 재현 자료와의 경계는 명시적 parser/타입 가드로 처리한다.

### 단계 2 — BaselineAnalysisSession

`openBaselineSession(spec)` → `inspectInputs()` → `verifyEvidence()` → `seal()` → `dispose()`의 수명주기를 구현한다. 구체 이름은 조정할 수 있지만 아래 계약은 유지한다.

- Program은 한 준비 세션에서 한 번 생성하고 진단 결과를 공유한다. V2→V1 subprocess wrapper를 새 준비 경로에서 다시 감싸지 않는다. `scan()` 전체를 호출한 뒤 별도 Program을 또 만들지 않는다.
- Vendure adapter가 고정 경로·정책·artifact 명세를 공급한다. 일반 세션은 Vendure 업무 의미나 원래 6개 역할을 내장하지 않는다.
- 기존 원문 inventory 4,735개와 준비 Program 1,638파일의 지문/구성원, 설정·관련 저장소 입력·진단 검사를 보존한다. 실제 분모와 누락을 보고하며 근거 파일 7개만 확인하는 것으로 대체하지 않는다.
- `SourceTable`은 canonical path별 hash/필요한 text/lineStarts를 재사용한다. 전체 inventory 원문을 모두 메모리에 중복 보관하지 않는다. CompilerHost/TS 내부 읽기와 명시적 근거 검증 읽기는 계측에서 구분한다.
- TS offset는 UTF-16, end는 배타적, 표시 좌표는 1-based다. Unicode·CRLF 경계도 검증한다. hash는 분석·근거 검사에 사용한 실제 텍스트/bytes 계약과 일치해야 한다.
- seal 시 입력 내용/목록을 다시 확인해 준비 도중 변경을 거부한다. 이 확인을 기존 cache hash만 재조회하는 것으로 대체하지 않는다. 이 때문에 필요한 재읽기는 정상 비용이며 Program 재생성을 뜻하지 않는다.
- 세션 상태는 `open/sealed/rejected/disposed` 등 명시적으로 표현한다. 실패 후 verified 결과를 만들지 않고 dispose 후 접근을 거부한다. 종료는 try/finally로 보장한다.
- 내부 verified 객체와 외부 JSON에 적힌 `verified: true`를 구분한다. 외부 artifact는 형식/참조/지문을 다시 검사한다. 저장된 과거 validation JSON만 믿고 현재 baseline 입력 검사를 건너뛰지 않는다.

S2는 S1 모델/관찰 artifact를 검증·포장한다. 매번 observer/FCA를 재실행할 필요는 없다. artifact 내용의 진실성을 hash만으로 새로 증명한다고 주장하지 말고, 독립 검토된 S1 결과를 재사용한다는 provenance를 남긴다. 임의 live workspace의 원자적 snapshot이나 새 코드 분석 성공을 주장하지 않는다.

### 단계 3 — 모델 계약과 검증

기존 12항목의 ID/kind/label/interpretation/unverified/intendedPolicy/author/검토 상태와 fact/candidate 참조를 손실 없이 옮긴다. 기존 `relatedItems`는 방향 있는 `NavigationLink(kind: related-item)`로 보존한다. 업무 의미를 추가하지 않고 원래 항목/필드의 provenance를 기록한다.

fact와 candidate를 별도 컬렉션으로 둔다. agent 수동 작성 관찰과 자동 역할 관찰, yes/no/unknown, 원문 영역/미지원 계약을 유지한다. candidate는 검토 보조 자료이며 독립된 업무 의미의 증명으로 취급하지 않는다. 탐색 링크에 존재하지 않던 fact 근거를 붙이지 않는다.

필수 검증 순서: JSON 타입/필수 필드·enum/ID 중복 → 참조 대상과 종류 → 원문 지문/구간/좌표 → 상태·승인 metadata 정합성. malformed 입력은 진단 코드·레코드/필드 위치를 가진 실패로 반환하고, 예외로 빠져 성공 산출물을 남기지 않는다. 형식상 human metadata가 있다고 실제 사람 승인을 인증하지 않는다. 정상 S1 산출물의 approvedKnowledge는 계속 0이다.

baselineId는 분석 입력, modelId는 의미 내용·관계·근거, bundleId는 배포 파일/포장 버전을 식별한다. 정렬·인코딩·줄바꿈·상대 경로·자기 hash/시각 제외 규칙을 문서화한다. 실제 JSON 배열의 의미 있는 순서를 임의로 정렬해 의미를 바꾸지 않는다. 같은 입력과 명세는 같은 ID/결과를, 해석 변경은 다른 modelId를 만들어야 한다.

출력 상태는 최소한 integrity, baselineEvidence, semanticReview, sourceVersion=baseline, currentWorkspaceAssessment=not-performed, partial coverage를 구분한다. baseline 검사 실패는 배포 실패다. 이후 별도 편집 코드가 바뀌어도 동결 bundle은 기준 코드 자료로 남으며, 그 좌표를 현재 파일의 좌표라고 제공하지 않는다.

### 단계 4 — 순수 조회와 사전 생성 view

`indexBundle`, `listItems`, `getItem`, `neighbors`, `getEvidence`를 구현한다. query 모듈은 Compiler API/파일시스템/프로세스/LLM에 의존하지 않는다. ID Map, incoming/outgoing adjacency, evidence/source index를 구축한다. 반환값을 수정해 내부 모델이 바뀌지 않도록 소유권/복사/불변 처리 방식을 정한다.

neighbors는 한 단계만 제공하며 direction과 원래 from/to를 보존한다. 기존 R6의 order→branch, cancel-request→dialog-submit/cancel-transport/refund-also-cancels/dismiss, refund-request→refund-transport/refund-also-cancels/dismiss가 유지되어야 한다. order에서 refund-transport로 임의 전이하지 않는다. 없는 ID는 구조화된 NotFound이고 빈 성공 결과와 구분한다.

12항목에서 fact/candidate/evidence 참조를 queue+visited로 따라 필요한 자료를 포장한다. candidate 구성원/속성의 해석에 필요한 선언·정의/근거까지 연결한다. 이 지시에서는 참조된 후보를 조용히 미제공으로 바꾸지 말고, 원래 참조를 유지할 수 없으면 실패시킨다. 전체 23MB scan dump는 배포하지 않는다. 선택/제외 레코드와 이유를 평가자용 manifest에 남긴다.

목록·항목 상세·1-hop 연결·근거 view를 동일 query 함수로 사전 생성한다. 원문 구간은 동결 baseline에서 읽고 hash/위치/버전을 표시한다. 변환 과정이 근거 hash를 불일치시키지 않도록 원문과 표시 포맷을 구분한다. 파일 이름은 ID를 안전하게 매핑하고 경로 충돌·root 밖 쓰기를 거부한다. 출력 경로가 이미 있으면 덮어쓰지 않으며 준비 실패 시 완료 bundle로 보이지 않게 한다.

### 단계 5 — 실제 A/B/C 배포 자료와 정보 대응 검토표

A/B/C의 공통 입력은 baseline 소스·기존 upstream 문서·동일 과업 문장·동일 도구다. B에는 동결 모델 view, C에는 같은 명제/근거/미확인 질문/검토 상태/범위 한계를 담은 일반 Markdown을 추가한다. C를 B의 정답 힌트를 누락한 축약판으로 만들지 않는다. C에도 동등한 목차/파일 단위를 둔다.

평가자용 `information-parity.json`에 semantic unit별 ID, B의 파일/구간, C의 파일/구간, source evidence, 미확인/검토 상태, 대응 여부를 기록한다. 자동 참조/coverage 대조와 사람이 읽고 판단할 의미 동등성을 구분한다. 자동 검사 통과를 사람 검토 완료로 표시하지 않는다. byte 수, 사용 tokenizer가 확정된 경우 token 수, 미확정이면 null과 이유를 기록한다. 길이를 맞추려고 의미 없는 padding을 넣지 않는다.

제공 경로 allowlist를 명시하고 파일·hash·크기·라이선스/출처 고지를 동결한다. 전체 Ontosary checkout, 기존 MODEL.md의 변경 예시, 리뷰 문서, 평가 명세/oracle/참조 구현, 원시 실행 로그/제작 경로를 agent에게 노출하지 않는다. README만 제외하고 import·symlink·source map·절대 경로로 접근 가능하게 남기지 않는다. 파일 manifest의 `evaluationIncluded:false`만으로 격리를 증명하지 않는다.

실제 비교용 workspace에 evaluator 파일을 복사하지 않는 builder와 접근 경계 명세를 만든다. 같은 권한의 다른 폴더는 격리가 아니다. 현재 실행 도구로 평가자 파일 접근을 제한할 수 없다면 `isolation: unverified`로 보고하고 본 실험 준비 완료와 구분한다. 이번 세션에서 비교용 agent/chat을 생성하거나 메시지를 보내지 않는다.

### 단계 6 — 과업·fixture/oracle와 실행 명세를 검토 가능하게 준비

역사적 S2-PROTOCOL의 reason 과업을 **검토용 후보**로 구체화한다. 원문과 요구의 차이, 적용 범위, 입력 실패 처리, 검증 방법을 새 문서에 적는다. 실제 Vendure의 승인된 정책으로 표현하지 않는다. generated/server schema 변경을 요구하지 않는 클라이언트 로컬 과업이라는 초안 경계를 유지한다.

과업 문장은 A/B/C에 동일하게 제공하되 함수명/정답 변경 위치를 특정하지 않는다. API 경계에서 빈 reason을 어떻게 거부할지, 오류 후 요청/환불을 어떻게 처리할지 등 결과 판정에 필요한 미정 사항은 대안과 권고를 제시해 리뷰할 수 있게 한다. 허용 구현 방식과 필수 관찰 동작을 구분하고 특정 helper 이름/정확한 diff를 정답으로 강제하지 않는다.

평가 하네스는 **제출 workspace의 수정된 코드를 실제로 평가**해야 한다. 원문/제출 코드의 대상 동작을 직접 실행하거나, 원문에서 결정적으로 추출한 코드와 필요한 의존을 실행한다. 고정 fixture 복사본만 평가해 제출 diff가 바뀌어도 결과가 같은 하네스는 허용하지 않는다. 새 helper/import를 사용한 정당한 해법도 지원하거나 명확한 미지원 상태로 처리한다. 미지원 추출/실행을 과업 성공으로 세지 않는다.

Angular/DB 전체 환경을 새로 구축하지 않는다. 외부 서비스·UI 효과를 double로 대체한다면 정확한 seam과 범위를 기록하고, 취소/환불 분기·입력 변환·오류 처리는 double 안에 재구현하지 않는다. source→fixture 대응표와 원문 anchor/hash, 포함/제외 동작을 만든다. faithful한 평가가 어려우면 이유와 작은 과업 대안을 보고하고, 임의로 다른 프로그램의 실험으로 바꾸지 않는다.

검토용 사례에는 정상/앞뒤 공백/빈 문자열/공백만/null/undefined reason, 직접 취소, 환불+일부 취소, 환불만, 두 dialog dismiss, active 주문의 lines 생략/부분 취소 양수 lines, 취소 실패 후 환불 분기를 포함한다. 호출 인자·횟수·순서·실패 결과를 관찰한다. HTML 조건은 별도 검토 항목이며 자동 TS coverage라고 세지 않는다.

원래 동작 보존 테스트와 새 가상 요구 테스트를 분리한다. baseline은 전자에서 통과하고 새 요구 중 미충족 사례는 실패해야 한다. 임시 복제의 검증용 참조 수정과 의도적 결함 변형으로 oracle를 시험한다. 최소한 직접 취소만 수정, trim 없이 빈 값만 검사, 모든 환불에 취소 강제, dismiss에서 요청 발생, 취소 실패 후 환불 진행을 구별해야 한다. 실제 cache와 upstream 원문은 수정하지 않고, 이 참조 수정은 평가자 전용이며 배포 자료에 포함하지 않는다.

`run-plan.json`에 다음을 기록한다: 정확한 agent 모델 ID/버전·reasoning·도구, 공통 입력과 B/C hash, source/environment fingerprint, 시간/token 예산, 반복/배정 seed, 격리 방법, 공개/비공개 테스트 경계, 제출/evaluation 명령, 수집 지표, 누락/중단 처리. 미정은 null과 사유로 남긴다. 반복 3회/조건은 기존 pilot 권고이며 실제 실행 전 고정할 대상으로 구분한다. 모델의 semanticReview와 실험 자료 동등성/원문 충실성 검토는 별개의 상태다.

`readiness.json`은 구현 검증, 실제 baseline 검증, B/C 자동 대조, 사람 검토, oracle 충실성 검토, 격리 검증, 실행 조건 동결을 나눠 보고한다. 필수 실행 조건이 미정이면 `readyForTrial:false`여야 한다. 준비 구현 완료와 본 비교 실행 가능 판정을 구분한다. 준비 비용·fixture 검증 시간은 기록하되 agent 효용/재작업 수치는 아직 null이다.

## 5. 검증 행렬

| 대상 | 최소 정상/부정 사례 | 기대 |
|---|---|---|
| Session | 정상·source/target-only/config/의존 입력 변경·누락·진단·seal 전 변경·dispose 뒤 호출 | 실제 검사 실패/미확인 상태를 verified로 반환하지 않음 |
| Model | 잘못된 JSON 타입/enum·중복 ID·참조 종류 불일치·깨진 참조·anchor/좌표/hash 불일치·잘못된 승인 metadata | 구조화된 실패, 실제 의미 승인은 별도 |
| Snapshot | baseline 고정 후 편집본 변경, 다른 baseline과 bundle 혼합, model 내용만 변경 | 역사적 근거와 현재 코드 구분, 잘못된 결합 거부, 적절한 ID 변경 |
| Query | 전체 12 ID·R6 경로·방향·없는 ID·무관한 전이·반환값 변조 | 정확한 1-hop/근거, 내부 자료 불변 |
| Packaging | 누락 참조·중복/경로 충돌·root 밖 경로·상한 초과·기존 출력 경로·중간 실패 | 실패를 완료 artifact로 표시하지 않음, 조용한 잘림 없음 |
| B/C | 명제/근거/질문/상태 대조·평가 내용/symlink/import 경유 유입 점검 | 동등성/격리 증거와 남은 미검증 항목 명시 |
| Oracle | 원래 동작·새 요구의 baseline 실패·참조 수정·결함 변형·제출 코드 변경에 따른 결과 변화 | 정답 문자열/고정 fixture만 검사하지 않음 |
| Reproduction | 새 두 출력 경로·정상화 규칙 동일·실행 순서/경로 차이 | 비시간 배포 bytes와 세 ID 동일 |

작은 fixture 테스트는 Vendure cache 유무로 skip하지 않는다. 실제 Vendure 통합 명령은 cache를 명시적 인자로 받고 부재를 성공으로 처리하지 않는다. 실제 기록 12항목의 의미·근거·검토 상태와 V2 navigation을 변환 전후 대조한다. 원시 S1 artifact와 역사적 코드는 수정하지 않는다.

전체 `pnpm check`와 `pnpm experiment`를 실행한다. 새 fixture/evaluation 경로를 추가하므로 기존 비교 4/4도 확인한다. 새 실험 명령은 README와 실제 package scripts/인자에 맞춰 제공하고, 없는 명령을 보고서에 적지 않는다. 실제 prepare의 두 번 재현, 작은 자체 fixture 검증, oracle 검증 명령을 각각 남긴다.

성능은 같은 환경의 준비 단계별 wall time, 전체 wall time, Program 생성 횟수, 명시적 근거 read/hash 수, 입력/출력 크기와 메모리 측정 범위를 기록한다. 숫자형 속도 목표는 두지 않는다. 1회 Program/세션내 캐시를 검증하고 seal 재검사 비용을 숨기지 않는다. 이전 8.25초는 추출까지 수행한 V2이고 이번은 기존 결과 포장이라는 차이가 있으므로 동일 작업의 순수 가속 배수로 홍보하지 않는다.

## 6. 완료 조건

다음 모두 충족해야 **S2 준비 구현 완료**로 인계한다. 리뷰/본 실험이 끝났다는 의미는 아니다.

1. 합의된 모듈 경계가 실제 코드에 있고, 새 TS 코드가 전체 check에 포함된다. query의 순수성/기준 자료 불변성이 검증된다.
2. 실제 Vendure baseline의 기존 감사 범위와 S1 provenance가 검증되고 새 준비 경로에서 자료를 만들 수 있다. 입력이 없으면 이 항목은 미완료로 보고한다.
3. 12항목 의미·링크·참조·미확인 질문·승인 상태가 보존되고 필요한 근거가 모두 연결된다. 자동 지식 승인/새 FCA 발견 주장이 없다.
4. 실제 B 구조화 view와 C 일반 문서, 공통 입력 manifest, allowlist/hash/고지, 명제 대응표가 있다. 사람 동등성 검토 결과가 없으면 pending으로 남긴다.
5. 과업/평가 하네스가 제출 코드에 연결되고 원문 대응표와 정상·부정 oracle 증거가 있다. 과업·원문 충실성의 독립 검토가 필요한 사항은 구체적으로 인계한다.
6. 격리·실행 조건·측정 항목이 run-plan/readiness에 있고, 미정 조건이 있는 본 비교는 실행하지 않았다. 모형 agent 실행으로 실험 효과 수치를 만들지 않았다.
7. 새 작은 회귀/실제 통합/2회 재현, `pnpm check`, `pnpm experiment`가 통과하고 원시 결과와 정확한 명령을 남겼다. 과거 자료는 그대로다.
8. 인계 보고서와 현재 상태 문서가 실제 결과를 반영하고 저장소 반영 절차를 완료했다.

코드만 끝내고 배포 자료·평가 연결·재현을 ‘후속 예정’으로 남긴 상태는 전체 준비 완료가 아니다. 반대로 아직 수행하지 않은 사람 검토/독립 리뷰를 완료로 꾸며 이 조건을 맞추지 않는다. 구현 완료와 실행 승인 대기 상태를 정확히 병기한다.

## 7. 산출물·원격 반영·리뷰 인계

최소 산출물: 위 모듈/fixture/테스트, 준비·검증 명령 README, 새로운 limits/spec 및 의미 보존 대조, 실제 B/C 배포와 hashes, evaluation 전용 과업/fixture/oracle/원문 대응표/결함 변형 결과, information-parity/run-plan/readiness, 시간·크기·재현 원시 증거다. 큰 캐시/빌드/비밀은 커밋하지 않고, 새 날짜/버전 경로를 쓴다.

`docs/reviews/<완료일>-s2-preparation.md`에 기준 revision, 변경 목록, 완료 조건별 근거 경로, 실제 명령·통과/실패/skip 수, 두 출력 비교, 준비 비용, 기존 의미 보존, 평가 격리 경계, 미정 사항과 권고를 적는다. agent 본 비교는 아직 미실행임을 명시한다. PROGRESS/ARCHITECTURE/ROADMAP/REVIEW_CONTEXT를 실제 구현 상태로 갱신하고 중요한 계약 선택은 DECISIONS에 남긴다. 연구 가설의 상태를 기능 완료만으로 올리지 않는다.

정상 경로에서는 독립 리뷰에 필요한 산출물까지 완성하고 인계한다. 사용자 판단이 필요한 것은 업무 의미 변경, 과업의 필수 행동/실험 범위 변경, 새 기술 투자·환경 예산, 격리/원문 충실성을 만족시킬 수 없는 경우다. 그때도 선택과 무관한 이미 승인된 구현·검증은 진행한다. 사소한 파일명/타입명/테스트 배치/빌드 명령 선택은 자체 판단한다.

AGENTS/CONTRIBUTING의 지속 승인에 따라 검증 → staged diff 자체 검토 → Conventional Commit → 작업 브랜치 push → PR 생성·자체 검토 → 필수 검사와 정확한 head 확인 후 merge → 로컬 main 동기화까지 진행한다. 별도 사람의 리뷰로 표현하지 않고 보호 규칙을 우회하지 않는다. 보고서와 PR 링크를 이 리뷰 세션에 전달할 수 있게 최종 응답에 포함한다.
