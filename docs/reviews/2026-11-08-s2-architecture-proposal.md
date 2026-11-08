# S2 분석 세션·모델·조회 아키텍처 제안

상태: **구조 합의 전 제안**. 기준 main `e49f705`. 사용자가 확정한 것은 S2가 **변경 전 모델이 agent의 수정 작업에 도움이 되는지** 검증한다는 범위다. 이 문서의 모듈/API/배포 선택은 아직 승인된 구현 지시가 아니다. 기존 S1/V2·core와 역사적 결과는 그대로다.

## 1. 범위와 우선순위

S2는 기준 revision의 모델을 참고해 수정하는 효과 H-O를 본다. 수정 후 모델 재생성·근거 재연결·승인 승계·정밀 stale 전파는 S3로 미룬다. 모델은 수정 작업 중에도 기준 소스에 관한 자료로 읽을 수 있으며, 수정된 코드의 현재 사실이라고 표시하지 않는다. 기존 전역 validator를 수정 작업마다 돌려 전체 모델 사용을 막는 방식은 S2 소비 계약으로 채택하지 않는다. 실행 전 전체 입력 검증은 유지한다.

| 구분 | 항목 | 이유 |
|---|---|---|
| 선행 필수 | baseline/model/bundle 식별자와 불변 자료 계약 | 어느 코드의 지식인지와 artifact 무결성이 있어야 실험 결과를 해석할 수 있음 |
| 선행 필수 | 모델/근거의 런타임 구조·참조 검사, 형식 유효성과 의미 승인 분리 | broken reference나 미검토 지식의 승인 오인을 막음 |
| 선행 필수 | 1-hop 조회와 근거 조회, 탐색 링크와 근거 참조 구분 | 기존 R6를 유지하고 23MB 전체 scan 읽기를 피함 |
| 선행 필수 | agent용 allowlist 배포와 B/C 정보 대조 | 평가 자료 유입과 추가 정보량 효과를 통제 |
| 선행 필수 | cache 없는 fixture 회귀, 고정 평가 oracle와 원문 대응 검토 | 특정 로컬 환경에서만 되는 검증과 잘못된 실험 판정 방지 |
| 작은 정리로 포함 권고 | 준비 과정의 단일 Program/진단·파일 hash 재사용 | 세 차례 중복 실행을 제거하고 동일한 입력 상태에서 검사 |
| 보류 | core `scan` 전체 재설계, 공개 API 통합 | S2는 기존 S1 artifact를 검증·포장할 수 있어 필수 아님 |
| 보류 | 실행 간 증분 cache, 안정 ID 재매칭, dependency 기반 invalidation | 변경 후 지식 유지 범위 |
| 보류 | FCA bitset/In-Close, 논리 열거 최적화·지원 확대 | 현 S2의 성능/지원 병목이라는 근거 없음 |
| 보류 | graph DB, OWL/RDF, MCP/서버, 검색 임베딩, 승인 workflow | 현재 12항목 소비에 필요한 투자 아님 |

단일 Program은 편리한 준비 구조의 권고이며 실험 효용 검증을 위한 필수 성능 문턱은 아니다. 이를 위해 core 대규모 이관이 필요해지면 준비 최적화를 따로 미뤄도 된다. 필수인 것은 입력 검증의 완전성과 같은 baseline을 사용한다는 계약이다.

## 2. 두 개의 수명주기

```text
준비자 영역
고정 Vendure 입력 + 검토된 S1 artifact + 분석/포장 명세
  → BaselineAnalysisSession (Program 1개, 진단, 파일 근거)
  → 기존 artifact 대조 + 구조/참조/근거 검사
  → 불변 ModelBundle + 순수 QueryIndex
  → B 구조화 view / C 동등 정보 서술 자료
  → session 종료

agent 영역 (독립 실행마다)
같은 baseline에서 시작한 수정용 코드 + 공통 요구/도구
  A: upstream 자료
  B: A + 동결된 구조화 view
  C: A + 동등 정보 서술 자료
  → agent 수정 → 별도 평가자가 제출 diff와 oracle로 판정
```

준비 세션은 한 baseline을 포장하는 배치 동안만 살아 있다. 모델 조회에는 Compiler API가 필요하지 않다. 준비 완료 후 Program/Checker/AST를 조회 객체나 JSON에 붙잡아 두지 않는다. 준비 비용과 agent 작업 시간은 분리 기록한다.

## 3. 분석 세션

역할은 **기준 입력의 일관된 읽기와 검증**이다. 도메인 의미 승인, agent 변경의 correctness 판정, 현재 작업 디렉터리의 자동 재분석은 수행하지 않는다.

제안 인터페이스(구조 논의를 위한 의사 타입):

```ts
openBaselineSession(input: BaselineSpec): BaselineSession
// 내부 소유: Program, TypeChecker, diagnostics, SourceTable
session.inspectInputs(): InputReport
session.verifyEvidence(ref: EvidenceRef): EvidenceCheck
session.seal(): VerifiedBaseline | RejectedBaseline
session.dispose(): void
```

`VerifiedBaseline`은 caller가 넘긴 boolean이 아니라 실제 입력 검사를 마친 결과다. 외부 JSON 입력은 다시 검증한다. `dispose()`는 소유한 참조/자원을 해제한다는 계약이며 TypeScript에 특정 destroy API가 있다는 뜻이 아니다. dispose 뒤 세션 호출은 거부한다.

세션 생성 시 config/extends·해석 입력·준비 dependency manifest와 원문 inventory를 확인하고 Program을 한 번 생성한다. 기존 1,638 Program 파일/4,735 inventory 감사 범위를 임의로 축소하지 않는다. Vendure 특유의 hash/경로/역할 조건은 `BaselineSpec`과 adapter가 소유한다. 일반 소스 세션에 Vendure 경로를 내장하지 않는다. 기존 strict/diagnostic 실패 경계를 유지한다.

`SourceTable`은 canonical path별로 content hash, 필요한 원문, lineStarts, source identity를 보유한다. 모든 inventory 내용을 메모리에 영구 보관하지 않고, 전체 감사용 hash와 Program/모델 근거에 필요한 텍스트를 구분한다. 근거 hash/offset는 실제 분석에 사용한 텍스트와 대조한다. config·해석에 영향을 준 입력도 baseline fingerprint에 연결한다. 한 파일을 읽고 hash한 결과를 세션 내에서 재사용해 484회 읽기를 줄인다.

S2 준비는 고정된 입력 디렉터리를 사용한다. seal 직전 입력 목록/내용을 재확인해 준비 중 변경을 거부한다. 이 확인은 Program 재생성을 의미하지 않는다. 일반 live workspace에 대한 완전한 원자적 snapshot 보장은 이번 범위가 아니다. 준비 완료 bundle은 별도 경로에 동결한다.

**기존 S1 결과를 사용한다.** S2마다 역할 추출/FCA를 다시 실행하거나 해석 항목을 새로 만들 필요가 없다. artifact hash와 provenance를 고정하고, 입력 동일성·근거를 확인하여 포장한다. 별도 재현 검증 때만 기존 observer/FCA를 호출한다. 추후 관찰 재사용이 필요하면 같은 Program을 넘길 수 있지만 core의 함수 경계와 S1의 callback 포함 메서드 경계를 합치지 않는다.

## 4. 불변 도메인 모델 묶음

제안은 기존 12항목의 의미를 보존하는 정규화된 JSON이다. 새 업무 관계를 추론하거나 모든 항목을 별도 concept/assertion 계층으로 분해하는 작업은 이번에 하지 않는다.

| 레코드 | 내용/규칙 |
|---|---|
| `Manifest` | schema/producer 버전, baselineId, modelId, bundleId, scope, coverage/limitations, artifact hash 목록 |
| `Items` | 기존 ID·kind·label·interpretation·unverified·intendedPolicy·author·reviewStatus |
| `NavigationLinks` | from/to, `kind: related-item`, 원래 선언 위치. 기존 relatedItems를 손실 없이 옮김 |
| `FactRefs` | 항목이 참조하는 코드 관찰과 그 근거. 자동 추출/agent 수동 작성 출처를 보존 |
| `CandidateRefs` | FCA 검토 보조 후보. 독립적인 업무 의미 증명으로 승격하지 않음 |
| `Facts / Candidates` | 기존 claim·역할 범위·yes/no/unknown·extent/intent·provenance와 참조 연결 |
| `Evidence / Sources` | baseline의 file/hash/UTF-16 offset/end·line 및 원문 구간. 중복은 ID로 공유 |

`NavigationLinks`에는 임의의 `causes`, `requires`, `is-a` 의미를 추가하지 않는다. 기존 링크에 독립된 사실 근거가 없다면 해당 항목의 사실을 edge의 증명으로 복제하지 않는다. 링크의 출처는 기존 모델의 선언이라는 점을 기록한다. 별도의 업무 관계를 구조화하는 것은 의미 변경이므로 S2 전환과 분리해 검토한다.

근거 참조와 탐색 링크를 구조적으로 분리하되, S2에서는 자동 stale 전파 엔진을 만들지 않는다. 현재 fact/candidate 참조만 검증한다. 모델 ID는 계속 관리 가능한 기존 명칭을 유지하고 snapshot 간 동일성 매칭은 하지 않는다. FCA의 `formal-N`도 baseline/model 범위 안에서만 사용한다.

세 식별자는 구분한다. baselineId는 분석 입력 명세/파일 지문, modelId는 해석·관계·근거를 포함한 동결 모델 내용, bundleId는 배포 파일·포장 버전의 지문이다. 같은 코드에 다른 해석을 붙인 모델은 다른 modelId다. 정렬된 직렬화와 제외 필드(자기 hash/관찰 시각 등)를 명시한다.

유효성을 하나의 `valid`로 압축하지 않는다.

```text
integrity: verified | invalid
baselineEvidence: verified | invalid | not-checked
semanticReview: pending | approved  (기존 항목별 상태 보존)
sourceVersion: baseline
currentWorkspaceAssessment: not-performed
coverage: explicitly-partial
```

S1 항목은 계속 pending이다. 형식 검사에 통과해도 승인 지식이 되지 않는다. agent가 코드를 수정해도 동결 baseline 자료 자체가 틀린 artifact가 되는 것은 아니다. 다만 근거의 좌표/주장은 baseline에 대한 것이므로 현재 파일에 그대로 적용할 수 없다. 조회 결과에 이 의미를 유지하고 현재 소스를 다시 확인하도록 사용 계약에 적는다. 현재 작업 파일과의 자동 차이 판정은 하지 않는다.

## 5. 조회 계층

입력은 검증된 JSON bundle, 출력은 JSON view다. 파일시스템·Compiler API·FCA·네트워크·LLM에 의존하지 않는 순수 모듈로 둔다. 타입은 TS로 작성하되 runtime의 JSON 구조 검사도 수행한다. 승인/현재성 상태를 조회가 변경하지 않는다.

```ts
indexBundle(bundle): QueryIndex
listItems(index): ItemSummary[]
getItem(index, id): ItemView | NotFound
neighbors(index, id, direction): OneHopView
getEvidence(index, evidenceId): BaselineEvidenceView | NotFound
```

`getItem`은 해석·미확인 질문·검토 상태와 사실/FCA 후보의 별도 참조를 반환한다. `neighbors`는 한 단계 incoming/outgoing만 제공하고 원래 from/to를 보존한다. 역방향 탐색은 대칭 업무 관계를 뜻하지 않는다. `getEvidence`는 원문 구간과 파일/hash/좌표 및 baselineId를 반환하며, 수정 중인 파일에서 그 구간을 다시 읽어 원문인 것처럼 섞지 않는다.

내부 자료구조는 `Map<id, record>`, `Map<itemId, outgoing[]>`, `Map<itemId, incoming[]>`, `Map<evidenceId, sourceRef>`다. 구축은 전체 레코드/참조 수에 선형, ID 조회는 기대 O(1), 이웃 조회는 O(차수+반환량)이다. 출력 순서는 고정 ID 순으로 결정한다. 12항목 전체 목록을 제공하며 embedding·의미 검색·경로 추천·전이 폐쇄는 넣지 않는다.

전체 scan은 모델에 넣지 않는다. 동결 12항목과 그 탐색 링크, 참조한 fact/candidate/evidence의 전이적 참조 집합만 포장한다. 참조 closure는 queue+visited로 각 레코드를 한 번 방문한다. 이것은 자료 연결의 누락 방지이고 업무 관계의 전이 추론이 아니다. referenced candidate에 필요한 구성원/속성 의미·근거도 포함하거나 그 후보를 명시적으로 미제공으로 처리해 dangling reference를 만들지 않는다.

S2 초기에는 일반적인 pagination 서버를 만들 필요가 없다. 포장 시 item/edge/원문/총 byte 한도를 검사하고 초과하면 명시적으로 실패시켜 범위를 다시 논의한다. 몰래 자르거나 중요한 조건을 요약해 없애지 않는다. 필요한 원문 분할은 근거 레코드의 의미와 모든 구간을 유지한 채 수행한다. 한도 값은 실제 bundle 크기를 확인한 후 동결한다.

## 6. agent 소비 경로와 실험 공정성

**권고: S2에서는 조회 모듈을 준비 과정에서 실행해 고정 view 파일로 배포한다.** B agent에게 전용 동적 도구를 추가하지 않는다. 12항목에서는 listing, item, 1-hop neighbor, evidence 파일을 미리 생성하는 것이 충분하다. agent는 모든 조건에서 동일한 파일 읽기·검색·수정 도구를 쓴다. 동적 CLI는 향후 필요가 확인되면 같은 query API의 얇은 adapter로 추가할 수 있다.

이 선택으로 S2는 준비 세션의 속도나 전용 도구의 효과보다 제공된 도메인 모델의 효용에 집중할 수 있다. B/C 사이에서는 명제·근거·열린 질문·coverage/승인 상태가 같아야 한다. C도 동등한 내용을 찾을 수 있는 목차/파일 단위를 제공해 숨겨진 검색 편의 차이를 줄이고, 실제 byte/token 및 찾아 읽은 양의 차이는 기록한다. 동일 정보가 일반 서술로 제공됐을 때와 구조화됐을 때의 패키지 효과를 보는 pilot이지 순수 그래프 표현만의 인과 효과를 완전히 분리했다고 주장하지 않는다.

기존 `MODEL.md` 같은 문서 전체나 Ontosary 저장소를 agent에게 주지 않는다. 과업별 해법 예시·oracle·리뷰·제작 스크립트로 이어지는 파일을 allowlist로 차단한다. agent 배포 자료는 baseline/domain 정보에서만 생성하고 과업 정답을 입력으로 받지 않는다. baseline 소스/기존 upstream 문서는 A/B/C 공통이며 편집 workspace는 매 실행 같은 초기 상태로 준비한다. 배포 hash와 시작 시 코드/환경 일치를 실험 harness가 확인한다. agent 수정 중에는 baseline 자료를 갱신하지 않는다.

묶음에 포함한 upstream 원문/구간의 라이선스와 출처 고지를 보존한다. 평가 전용 내용이 섞인 안내 문서 대신 이 배포에 필요한 고지와 사용 계약을 별도로 제공한다.

평가 자료는 agent가 읽을 수 없는 별도 저장/실행 영역에 둔다. 같은 접근 권한의 다른 폴더에 놓고 ‘보지 말라’는 지시만 하는 것은 격리가 아니다. 기존 fixture 초안의 원문 충실성과 B/C 동등성 검토는 별도 준비 과제로 남아 있다. 공개 테스트와 숨긴 oracle의 경계를 정하고 제출 후 별도 평가자가 평가한다. 전체 앱/Angular/서버 runtime 성공과 fixture의 성공은 구분한다.

제공 모델은 S1에서 이미 알려진 취소/환불 연결을 포함하는 agent 작성 초안이다. 반복은 독립 세션에서 수행하고 이전 실행의 대화/diff/평가를 전달하지 않는다. H-O는 이 모델 패키지의 지원 효과이고, H-F/FCA의 증분 가치는 이 실험으로 입증하지 않는다.

## 7. 배치 위치와 검증 경계

단일 패키지를 유지한다. 다음은 아직 확정되지 않은 디렉터리 후보다.

```text
src/core/                         # 기존 추출·논리·FCA와 공개 계약 유지
experiments/domain-model/s2/
  lib/analysis-session.ts         # 준비 입력/Program/SourceTable 수명주기
  lib/model.ts                   # 동결 모델의 내부 계약
  lib/validate.ts                # 구조/참조/근거 검증, 상태 분리
  lib/query.ts                   # 순수 index와 조회
  lib/bundle.ts                  # B view·C 자료 인벤토리, hash/allowlist
  prepare.ts                     # 준비 조립, 정책/경로 주입
  vendure-baseline.ts             # 기존 고정 입력/아티팩트 adapter
```

실험 TS도 별도 tsconfig/typecheck 대상으로 포함할 후보다. 라이브러리와 타입은 현재 실험 내부로 한정하고 제품 공개 export로 승격하지 않는다. `analysis-session`은 TS에, query/model은 직렬화 가능한 자료에 의존하며 core가 실험 계층을 import하지 않는다. V1/V2를 다시 쓰지 않고, 기존 결과와 변환 후 명제/근거/상태를 대조한다. S2 결과가 다음 재사용 요구를 뒷받침하면 이때 core 또는 별도 도메인 계층으로 옮긴다.

구조 검증에는 작은 자체 fixture로 ID 중복/깨진 참조/잘못된 JSON 타입·소스 불일치/target-only 변경/config 변경/누락 입력/한 단계 방향/없는 ID/승인 오인/기준 근거와 편집본 혼합을 검사한다. 로컬 Vendure cache가 없어도 실행돼야 한다. 실제 Vendure 재현은 명시적인 별도 통합 검증으로 보존한다. 최적화는 필수 통과 조건이 아니며 입력 감사 축소로 빨라진 결과는 인정하지 않는다.

## 8. 합의할 구조 선택

권고안은 다음 세 가지다.

1. 분석 세션은 **준비 단계의 단일 baseline 배치**로 한정하고 실행 간 증분 처리는 하지 않는다.
2. 도메인 모델은 **기존 의미를 유지한 동결 bundle**, 조회는 **TS/파일시스템과 분리된 순수 모듈**로 둔다. 배포는 사전 생성 view와 동일한 파일 도구를 사용한다.
3. 재사용 모듈을 **타입 검사되는 S2 실험 계층**에 두고, 제품 core/public API로의 승격은 효용 검증 이후 판단한다.

사용자가 위 구조를 합의한 뒤에만 개발 지시와 완료 조건/구체 한도를 작성한다. reason 과업·fixture/oracle·모델 ID/예산·반복 횟수 등 기존 S2 초안의 미정 항목은 범위 결정만으로 자동 확정하지 않는다.

문서 반영 검증: 기존 `pnpm check`의 10파일/174테스트·타입 검사·예제 build 통과. 제안 모듈을 구현/검증했다는 뜻이 아니다. 분석 동작과 fixture 변경이 없어 `pnpm experiment`는 반복하지 않았다.
