# 현재 구현 아키텍처·기술 부채 조사

기준: main `c139d95d8e19b229a04edbe9d1b434e7042499e8`, 2026-11-08. 독립 리뷰이며 제품 구현 변경, 다음 단계 아키텍처 확정, 개발 지시가 아니다. S1/R6/R7 완료 판정을 유지한다. 새 false proof를 재현한 보고서가 아니라 현재 구조의 비용과 다음 단계에서 드러날 계약 문제를 조사했다.

## 1. 종합 판단

**작은 정적 분석 PoC로는 적절하다. 반복적으로 변경되는 프로젝트의 도메인 지식을 관리하는 기반으로는 아직 실험용 연결부가 많다.** 코어를 전면 재작성하거나 FCA 알고리즘부터 교체할 근거는 없다. 먼저 분석 수명주기, 근거/관계/유효성 계약, agent가 소비할 조회 단위를 논의하는 것이 타당하다.

강점은 TypeScript 외 코어 제3자 의존성이 없고, CLI/예제가 분리되어 있으며, 논리/FCA가 작은 순수 계산에 가깝다는 점이다. 지원 불가와 불확실성을 성공과 구분하고, 사실·후보·승인 지식을 분리하는 원칙도 구현에 남아 있다. 실제 함수 실행과 비교한 논리 테스트, 작은 context의 완전 열거 대조, 심볼 충돌·부정 사례가 있어 최적화의 기준 구현으로 보존할 가치가 있다.

목표에 더 직접적인 미완성 부분은 **코드 변경 뒤 지식을 어떻게 유지하고, agent에게 어떤 근거를 얼마만큼 전달할 것인가**다. 온톨로지 표준 도입이나 FCA 속도 개선만으로 해결되지 않는다. 모델 사용 효과 H-O와 FCA의 구축 비용 절감 H-F는 여전히 미검증이다.

## 2. 실제 경계

| 계층 | 현재 책임 | 경계에서 생기는 부채 |
|---|---|---|
| `src/core/analyzer.ts` | config/파일 읽기, Program, 진단, AST 추출, 조건 정규화 | 한 번의 `scan(path)`에 수명주기 전체가 결합됨. Program을 외부 작업과 공유하거나 추출 범위만 바꾸기 어려움 |
| `src/core/logic.ts` | 제한된 표현식 → IR, 유한 입력 열거, 반례 | 함수 실행기·제어 흐름 분석기가 아님. 입력 조합 상한만으로 식 크기·재귀 깊이를 제한하지는 않음 |
| `src/core/fca.ts` | 일반 함수 속성 구성, NextClosure, 후보/관계 출력 | 속성 의미/선택 정책과 열거 결과의 소비 정책이 한 파일에 있지만 작은 규모. 현 비용의 주범은 아님 |
| `src/core/model.ts` | JSON/TypeScript 계약 | core facts에 snapshot hash/분석기 버전이 없고 ID는 좌표 기반. 도메인 모델 계약은 별도 실험 JSON |
| domain-model V1/V2 | 특정 Vendure 과업의 역할 관찰, 수동 해석, 근거 검증/탐색 | 코어와 객체 경계가 다름. V2가 V1 프로세스를 감싸며 입력 감사와 Program을 반복 생성 |
| CLI | 명령 → 전체 scan → JSON | 별도 명령마다 재분석. compiler 오류를 막는 CLI와 호출자 책임인 core FCA API의 안전 경계가 다름 |

S1의 callback 호출을 바깥 메서드의 속성으로 집계하는 계약과 core의 중첩 함수 분리 계약을 무작정 통합하면 의미가 달라진다. 공유할 부분은 Program/심볼/근거 도구이며, 객체·원문 영역 선택 정책은 명시적으로 남겨야 한다. 일반 references는 선언 이름도 포함하므로 호출 그래프나 변경 영향 그래프로 취급할 수 없다.

## 3. 측정

[재현 스크립트](evidence/2026-11-08-architecture-audit.mjs), [원시 결과](evidence/2026-11-08-architecture-audit-results.json).

Apple M1, Node 22.19.0, TypeScript 5.9.3. 기존 준비 cache를 읽기만 했으며 설치/빌드는 반복하지 않았다. 작업은 순차 실행하고 OS 파일 cache를 비우지 않았다. 세 번의 관찰 중앙값/범위이며 p95·성능 보장·다른 앱에 대한 일반화가 아니다. core/역할 관찰/입력 감사는 각각 별도 프로세스다. compiler 내부 타이머는 중첩될 수 있으므로 합하거나 scan에서 빼서 추출 시간을 계산하지 않았다.

| 측정 대상 | 결과 | 해석 |
|---|---:|---|
| V2 전체 runner | 중앙값 8,247ms; 8,213~8,695ms | 입력 감사 → V1 runner → standalone 검증의 전체 비용 |
| 위 runner 안의 V1 `timing.json` | 중앙값 2,773ms | V2 바깥 작업을 포함하지 않음. 약 3초를 전체 V2 비용으로 읽으면 안 됨 |
| standalone 전체 입력 감사 | 중앙값 2,622ms | 4,735 inventory/1,638 Program 파일·진단 확인 |
| 역할 실험 Program 생성 / 진단 | 중앙값 808ms / 1,568ms | 아래 추출보다 훨씬 큰 비용 |
| 78메서드 역할 추출 / binary 변환 / FCA | 중앙값 5.60ms / 0.20ms / 0.67ms | 별도 단계 측정. FCA는 첫 호출 포함 |
| core 전체 scan | 중앙값 3,214ms | 327파일/2,264함수/23,539 reference, 진단 0 |
| core scan JSON | 22,979,177 bytes; gzip 1,507,052 bytes | compact JSON. gzip은 저장/전송 크기이며 agent 문맥 비용을 해결하지 않음 |
| core 측정 프로세스 최대 RSS | 약 849~852MiB | import·scan·context·JSON/gzip 포함. scan 객체만의 메모리나 V2 전체 프로세스 합산이 아님 |
| 역할 측정 프로세스 최대 RSS | 약 604~606MiB | Program/진단/관찰 포함 |
| 484개 근거 검사 | 20.33ms, source read 484회 | 실제 파일은 7개/77,107 bytes인데 7,457,526 bytes를 반복 읽음 |

V2는 코드 경로상 Program을 세 번 생성하고 전체 입력 감사를 세 번 수행한다. 단일 검사 세션을 재사용할 개선 여지는 분명하지만 **재사용 구현의 속도 향상은 아직 측정하지 않았다**. 스냅샷 동일성 검사를 없애서 시간을 줄이는 제안이 아니다.

FCA 별도 microbenchmark는 한 번 예열 후 3회 측정했다. 현재 구현/기본 256개 상한을 그대로 사용했다.

| context | 중앙값 | 출력 |
|---|---:|---|
| 실제 S1 78×6 | 0.33ms | 8개, 완전 |
| 모두 참 128×64 | 2.40ms | 1개, 완전 |
| 결정적 희소 합성 128×64 | 81.35ms | 256개, 잘림 |
| 대각선만 거짓 12×12 | 1.17ms | 256개, 잘림 |
| 대각선만 거짓 64×64 | 94.61ms | 256개, 잘림 |

대각선만 거짓인 n×n context는 각 객체가 자기 속성만 갖지 않으므로 모든 속성 부분집합이 닫혀 2^n개 형식 개념을 만든다. 12×12만으로도 4,096개다. **잘린 prefix의 빠른 실행은 전체 격자 처리가 싸다는 뜻이 아니다.** 실제 S1의 빠른 열거 또한 2,264×4,288 전체 context의 상한 확대 근거가 아니다.

논리 비교는 12개의 독립 이진 입력/동일 OR 식에서 4,096조합 전체 평가에 중앙값 2.59ms였다. 입력 준비와 AST 정규화는 제외한 합성 사례다. 논리 계산 역시 현재 과업의 우선 병목이라는 증거가 없다.

새 V2 결과 중 마지막 실행의 비시간 15파일이 기존 기록과 byte 일치했다. 생성한 세 실행의 시간은 모두 보존했고, byte 대조 대상으로는 마지막 실행만 사용했다.

## 4. 기술 부채와 논의 우선순위

아래 우선순위는 조사자의 권고이며 ROADMAP 변경이나 구현 승인이 아니다. 기존 지원 경계·보수적 실패 자체를 결함으로 분류하지 않는다.

### A. 다음 단계 설계에서 먼저 합의할 것

**A1 — 분석 snapshot의 소유권과 실행 수명주기.**

근거: `analyzer.ts:11~26`, V2 `run.mjs:10~17`, `inputs.mjs:13~39`, V1 `run.mjs:21~47`. config/Program/diagnostics/파일 hash를 각 소비자가 따로 만들고 버린다. 역사적 V1을 보존하기 위해 생긴 중복은 이해할 수 있으나 앞으로 버전 wrapper를 계속 쌓으면 비용과 오류 경로가 늘어난다.

권고 후보는 한 요청/배치에서 `AnalysisSession`을 소유하고 snapshot, Program/Checker, 진단, 파일/심볼/근거 index를 재사용하는 구조다. public JSON에는 TS 객체를 넣지 않는다. 독립 validator는 세션 없이도 스스로 검사할 수 있어야 하며 단순히 `verified: true`를 매개변수로 받아 검증을 생략해서는 안 된다. 같은 세션이라도 분석 중 파일이 변하면 그 결과를 어떻게 거부/재시도할지 정한다. hash는 가능하면 분석에 사용한 `SourceFile.text`와 결합하고 디스크의 다른 시점 내용을 섞지 않는다.

한 프로세스 안의 재사용과 여러 실행에 걸친 증분 cache는 다른 투자다. 후자는 TS 버전·compiler options·tsconfig extends/references·module resolution·package metadata·의존 선언 변경까지 유효성 키에 포함해야 한다. 파일 mtime이나 함수 본문 hash만으로 안전하지 않다. 우선 전자를 논의하고 반복 편집의 필요가 확인되면 BuilderProgram을 실험한다. TypeScript의 공식 builder는 영향받은 파일의 진단/emit 재사용을 지원하지만 Ontosary facts나 도메인 모델의 갱신을 자동 처리하지 않는다. [TypeScript Compiler API](https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API).

**A2 — 근거 의존성과 도메인 관계, 탐색 연결의 분리.**

근거: V1 `validate.mjs:43~46`, V2 `navigate.mjs:4~13`. `relatedItems`는 사람이 읽는 연결이면서 stale 전파 대상으로 사용된다. 12항목 파일럿의 보수적 검토에는 가능하지만, 업무상 관련이 있다는 이유와 판단이 특정 근거에 의존한다는 이유는 다르다.

주문 취소 예로 `환불 경로 —관련 항목→ 취소 요청`을 역방향으로 탐색하는 것과, `환불 경로가 취소 호출을 포함한다`는 주장 및 그 호출 근거는 별개다. 한 관계가 바뀌었을 때 승인된 다른 모든 설명까지 폐기할지 결정하려면 edge 자체에 종류·방향·근거·검토 상태가 필요하다. `relatedTo`는 탐색에, `supportedBy/derivedFrom`은 근거 갱신에 쓰는 최소 구분을 논의한다. 업무 관계와 형식 intent 포함 관계도 섞지 않는다.

W3C PROV의 entity/activity/agent와 derivation 구분은 참고할 만하다. 도메인 관계와 출처 관계를 나누는 설계 참고이지 RDF/OWL 도입 권고는 아니다. [PROV-O](https://www.w3.org/TR/prov-o/).

**A3 — 좌표 ID, 지속적인 지식 ID, 유효성/승인의 분리.**

core ID는 `path:offset:name`, S1 객체 ID는 여기에 revision이 붙고 FCA는 `formal-N` 순서 ID다. 지금은 snapshot 내부 참조로 적절하다. 편집·이동·scope 변경 뒤 같은 업무 개념이라는 보장은 없다. 반면 수동 모델의 `order` 같은 ID만 유지한다고 근거가 자동으로 따라오지는 않는다.

`snapshot 내 사실 ID`와 `지속적으로 관리할 개념/주장 ID`를 나누는 방향을 검토한다. 새 snapshot으로의 근거 재연결은 선언 종류/소속/이름/구문 지문 등을 이용한 후보 매칭으로 취급하고 모호하면 검토를 요구한다. 이름이나 구조적 타입 일치만으로 승인 의미를 승계하지 않는다. FCA 결과 재현용 식별자를 안정화하려면 context 지문과 정렬된 extent/intent가 필요하며, 그것도 업무 개념의 영구 ID가 아니다.

현재 V2는 분석 입력 하나가 달라도 468개 자동 사실·5후보·12모델 항목을 보수적으로 무효화한다. 고정 실험의 재현 계약에는 맞지만 변경 과업을 수행한 이후에는 정상적인 코드 수정도 검토 필요가 된다. 변경 전 모델만 제공하는 S2와 변경 후 모델 유지까지 평가하는 실험을 구분해야 한다. 이 선택 없이 정교한 증분 invalidation을 선행 구현하면 범위가 커진다.

**A4 — 전체 fact dump와 agent용 근거 조회의 분리.**

23MB scan을 매번 읽히는 경로는 목표에 맞지 않는다. 선언/파일/근거를 ID로 정규화해 중복을 줄이고, `개념 → 주장/관계 → 근거 → 필요한 소스 구간`으로 필요한 정보만 반환하는 후보 구조가 적절하다. `Map<id,record>` 및 incoming/outgoing adjacency로 시작할 수 있고 graph DB는 아직 필요 근거가 없다. 출력에는 snapshot, 관찰 범위, 미지원/누락, 검토 상태가 함께 있어야 한다. 원시 JSON은 재현·감사용으로 보존한다. 비용은 byte뿐 아니라 agent가 읽은 양/토큰·누락·변경 성공으로 평가한다.

### B. 구현을 정리할 때 비용 대비 이점이 큰 부분

**B1 — 반복 파일 읽기/hash/좌표 처리와 심볼 조회.**

V1 validator는 근거마다 파일 전체를 읽고 hash하며 prefix를 잘라 줄 수를 센다. 현재 20ms라 긴급 병목은 아니지만 7파일을 484회 읽는 불필요한 반복은 확인했다. 한 검증 snapshot 안에서 `Map<file,{text,hash,lineStarts}>`로 한 번 읽고 hash한다. lineStarts 구축 O(파일 길이), offset→line은 이진 검색 O(log 줄 수) 또는 TS의 기존 line map을 쓸 수 있다. 파일 캐시는 검증 세션 밖으로 무조건 유지하지 않는다.

역할 추출기는 속성마다 호출 목록을 다시 검사한다. method의 call을 한 번 해석해 `target declaration → occurrence[]` index를 만든 후 역할에 투영할 수 있다. 현재 6속성/5.6ms이므로 일반화를 하기 위한 대규모 추출기 개발보다 작은 국소 중복 제거 후보에 가깝다. unknown은 별도로 유지하며 ‘검사하지 않음’을 no로 바꾸면 안 된다.

core는 함수 내부 방문과 전체 AST 방문을 함께 한다. 중첩 함수 경계를 끊으므로 이를 곧바로 모든 함수×전체 AST의 이차 순회라고 평가하면 잘못이다. 다만 같은 identifier/property의 reference 생성, 동일 return 식의 condition/predicate 정규화가 반복된다. Program 수명 안의 `WeakMap<Node,...>`/`Map<Symbol,...>` 캐시 후보가 있다. 타입 문자열은 문맥/format flags 영향을 받을 수 있어 타입 객체만으로 전역 memoization하면 안 된다. CPU profile 없이 Checker 호출별 절감량을 주장하지 않는다.

**B2 — 검증용 `.mjs` 계약과 실패 출력.**

실험 코드는 tsconfig의 `src/**/*.ts` 대상 밖이고 도메인 model schema가 core model과 따로 있다. validator는 provenance 존재와 참조/anchor를 확인하지만 모든 입력 필드의 런타임 타입을 완전 검증하는 범용 JSON parser는 아니다. 소유한 고정 artifact에는 테스트가 있지만 사용자가 편집하는 모델을 받을 때는 구조 검증 → 참조 무결성 → 소스 freshness → 의미 검토 상태의 층을 나누는 편이 좋다. 특정 schema 라이브러리/의존성 도입은 아직 정하지 않는다. `valid`도 ‘형식/근거 검사 통과’이지 의미 승인으로 해석하면 안 된다.

여러 문장을 한 줄에 배치한 실험 코드와 절차/정책/입출력이 섞인 runner는 작은 수정의 검토를 어렵게 한다. 다음 재사용 모듈은 읽기 쉬운 함수·명시적 반환 타입/상태로 분리하되 역사적 V1/V2와 원시 증거를 재작성하지 않는다. 새 모듈로 이관할 때 고정 결과와 부정 사례를 대조한다.

**B3 — 회귀 실행 환경과 관측 가능성.**

V2 통합 테스트 5개는 `/tmp/ontosary-vendure-preparation-20261108/vendure` 존재 여부로 skip한다. 지금 환경에서는 실행되지만 깨끗한 checkout의 `pnpm check`가 같은 보장을 주지는 않는다. 작은 자체 소유 fixture로 target-only 변경, module/config 의존, unknown, 입력 소실을 항상 실행하고, 실제 Vendure 검증은 명시적 별도 통합 작업으로 유지하는 방향을 검토한다. 전체 cache를 매 CI마다 재설치하는 것과는 구분한다. 저장소에는 `.github` workflow가 없다.

단계별 wall time, peak memory의 측정 범위, 입력/출력 크기, cache hit/miss, 전체/추출 범위, 잘림/거부 이유가 필요하다. 고정 시간 문턱을 보통 unit test에 넣기보다 별도 반복 benchmark로 관리한다. V2 전체 시간과 V1 내부 시간을 구분하는 것이 첫 관측 개선이다.

## 5. 자료구조·알고리즘 검토

기호: g=객체 수, m=속성 수, c=출력 개념 수, d=객체당 최대 속성 수(중복 없는 정상 incidence), V/E=모델 정점/간선 수, D=입력 조합 수, L=IR 노드 수, v=변수 수. 아래는 코드에서 도출한 거친 상한이지 측정된 성장 곡선이 아니다.

| 부분 | 현재 비용/구조 | 개선 후보와 조건 |
|---|---|---|
| FCA closure | 문자열 배열 `every/includes`; 대략 O(g·m·d) | attribute 정수 index와 Set이면 membership 기대 상수. 밀집/반복 closure라면 bitset 교집합 |
| NextClosure 전체 | 개념당 최대 m closure, 거친 O(c·g·m²·d), d=m이면 O(c·g·m³) | 알고리즘 유지+membership 개선부터 비교. bitset도 개념 개수의 지수 성장을 없애지 않음 |
| FCA 관계 | 모든 후보 쌍 subset, O(c²·m²) | Set/bitset으로 subset 개선. 모든 엄격 순서 쌍을 출력하는 한 출력 자체 O(c²) 가능. Hasse만 출력하면 계약 변경 |
| 후보 evidence 결합 | extent마다 `functions.find` | ID→FunctionFact Map. 작은 기본 g에서는 낮은 우선순위 |
| 함수 비교 | 재귀 식 평가 O(D·L) + 입력 spread 복사 | 반복 mixed-radix 열거, 한 입력 버퍼+반례만 복사. 대량 동일 domain 비교 시 진리표 bit-vector 재사용 검토 |
| 모델 한 단계 탐색 | 전체 항목마다 시작 항목의 배열도 검색; O(V·deg(start)+E+V) | ID Map + 양방향 adjacency 구축 O(V+E), 질의 O(인접 차수+반환 근거량) |
| stale 전파 | 변화가 없을 때까지 전체 재검사; 최악 O(V·(V+E)) | 근거 의존 역방향 adjacency + queue/visited로 O(V+E). 먼저 간선 의미를 분리해야 함 |
| 근거 검증 | 근거마다 파일 길이만큼 hash/line 계산 | snapshot별 파일 hash/line index로 반복 제거; provenance dependency는 별도 graph |

### FCA에서 지금 선택하지 말아야 할 지름길

- 128×64의 이진 incidence만 조밀하게 보관하면 1,024 bytes지만, 객체 ID/근거/결과/unknown metadata 비용은 별도다. 현재 문자열 배열을 모두 bitset으로 바꿔도 compiler 비용은 그대로다.
- JS Number의 bitwise는 32비트이므로 64속성을 Number 한 개로 처리하면 안 된다. 32-bit word array 또는 BigInt 후보를 비교하되 정렬/lectic 순서·빈 extent·제한 경계를 기존 oracle과 대조한다. sparse context는 posting list/Set이 유리할 수도 있어 밀도별 측정이 필요하다.
- In-Close 계열은 incremental closure/canonicity 검사로 계산을 줄이는 후속 후보다. 논문의 다른 언어/데이터 성능 배수를 Ontosary에 적용하지 않는다. [Andrews, In-Close](https://ceur-ws.org/Vol-483/paper1.pdf). 수직 extent bit-array 연구도 구현 선택 참고이지 지금 교체 근거는 아니다. [Zhou 외](https://arxiv.org/abs/2111.00003).
- 전체 격자 대신 과업 관련 속성의 closure만 질의하거나 최소 support 조건으로 탐색하는 방법은 가능하지만, 결과의 완전성/누락 의미가 달라진다. 단순 그룹 대비 추가 가치가 없던 S1에서 속도만 올리는 실험은 H-F를 해결하지 않는다.
- core `returns:<type string>`은 의미 identity가 아니다. 향후 속성 family·선택 버전·출처/coverage를 기록하는 투영 정책이 필요하다. 타입명이 같거나 구조가 같다는 이유로 도메인 개념을 합치지 않는다.

### 함수 평가에서 유지할 경계

현재 구현은 임의 함수를 실행하지 않고 지원 표현식의 유한 진리표를 비교한다. 수정된 코드의 동작 보장이나 전체 취소/환불 절차 검증을 제공하지 않는다. 지원 확대보다 과업에서 실제 필요한 명제와 입력 대응/독립성 전제를 먼저 정한다.

양방향 반례를 모두 찾으면 `Different`는 확정할 수 있지만, 조기 중단하면 현재의 전체 `evaluatedAssignments` 의미가 달라진다. `Equivalent` 및 성립하는 함의를 증명하려면 남은 영역 확인이 필요하다. 입력 버퍼를 재사용할 때는 반례를 복사하지 않으면 이후 열거로 오염된다.

현재 열거는 모든 조합을 배열로 저장하지 않는다는 장점이 있다. 다만 재귀의 각 단계가 길이가 늘어나는 input 객체를 복사하므로 경로상 동시에 살아 있는 입력 복사본은 최악 O(v²), 호출 깊이는 O(v)가 된다. 개선 후보의 입력 버퍼는 O(v)로 줄일 수 있지만 별도 IR 평가 재귀의 깊이 문제까지 해결하지는 않는다.

4,096 상한은 D만 제한한다. singleton domain이 많은 v, 매우 긴 식 L/깊이, 큰 소스 파일은 별도다. 향후 외부 입력/대형 반복 작업을 받을 때 IR node/depth/variable budget, 취소/deadline 상태를 함께 검토한다. 시간 초과를 Equivalent나 완전한 FCA로 표현하지 않는다. BDD/SMT는 현 병목과 지원 과업에 대한 근거가 없으므로 보류한다.

## 6. 다음 대화에서 정할 선택

아래는 구현 지시가 아니라 의사결정 안건이다.

1. **다음 단계가 고정 모델의 agent 효용만 보는 S2인가, 변경 후 지식 유지까지 보는 단계인가?** 전자면 기존 스냅샷으로 실험할 수 있고 모든 부채를 먼저 갚을 필요는 없다. 후자면 snapshot/ID/근거 갱신 계약이 선행한다. 권고는 S2에 필요한 최소 소비 계약을 먼저 정하고 지식 유지 효과는 별도로 측정하는 것이다.
2. **실험별 runner를 계속 확장할 것인가, 재사용 가능한 작은 분석 세션과 조회 계층을 만들 것인가?** 권고 후보는 현재 단일 패키지 안에서 수명주기·사실 추출·순수 분석·도메인 모델/조회 책임을 나누는 것이다. 여러 패키지/서비스/DB로 분산할 근거는 없다. S1 observer는 명시적 원문 영역 정책을 가진 adapter로 남길 수 있다.
3. **도메인 모델의 최소 관계 계약을 어디까지 할 것인가?** 탐색 연결, 근거 의존, 관찰된 동작, 검토된 정책의 구분을 우선 논의한다. 승인과 freshness는 독립 상태로 취급할 후보이며 표준 포맷은 나중에 선택할 수 있다.

그 뒤 필요한 작은 정리와 S2를 병행/선후 중 무엇으로 진행할지 정한다. 현재 권고 순서는 **계약 결정 → 필요한 중복/조회 정리 → 효용 검증 → 측정에 근거한 최적화**다. 전체 격자 확대·OWL/RDF·SMT·전면 증분 엔진·프레임워크 플러그인을 이번 조사만으로 착수하지 않는다.

## 7. 검증 및 인계

재현 명령(출력은 새 경로를 사용):

```sh
pnpm build
node docs/reviews/evidence/2026-11-08-architecture-audit.mjs /tmp/ontosary-vendure-preparation-20261108/vendure work/architecture-audit-20261108
pnpm check
```

측정은 기존 구현을 호출했으며 새 최적화를 구현하지 않았다. 원시 결과는 script SHA와 기준 revision을 포함한다. 제품 소스·기존 테스트·manifest·과거 원시 결과는 변경하지 않았다. `pnpm check`는 타입 검사·10파일/174테스트·예제 production build 모두 통과했다(이번 환경에서 cache 의존 테스트도 실행). 비교 알고리즘/fixture를 변경하지 않았으므로 이번 문서 감사에서 `pnpm experiment`는 반복하지 않았다. 직전 S1 독립 리뷰의 비교 4/4를 이번 실행으로 주장하지 않는다.
