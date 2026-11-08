# 결정 기록

모든 항목의 최초 결정일: 2026-11-03. 변경 시 이전 이유와 새 실험 근거를 남긴다.

## ADR-001 · Ontosary와 개발자 가치

**결정:** 이름을 Ontosary / `ontosary`로 통일하고 Code Facts, Candidates, Approved Knowledge를 구분한다. 온톨로지 기반 아키텍처로의 전환을 요구하지 않는다.
**이유:** 기존 코드의 이해·검토 비용을 줄이는 것이 제품 목표다. 이름은 특정 포맷을 강제하지 않는다.
**상태:** 적용. 승인 워크플로는 미구현.

## ADR-002 · TypeScript Compiler API와 단일 패키지

**결정:** TS 5.9.3의 공개 Compiler API를 직접 사용한다. 런타임 의존성은 TS 하나이고 코어/CLI를 폴더로 분리한다.
**이유:** 타입·심볼 해석을 기존 컴파일러에 맡기며 별도 파서를 재구현하지 않는다. 현재 AST 작업량에는 ts-morph 추가 의존성이 필요하지 않았다. 최신 메이저 자동 추종 대신 확인된 JS Compiler API 버전을 고정했다.
**결과:** 프레임워크 독립 실행. TS 신버전 구문은 추후 호환성 corpus로 검증 후 업데이트한다.

## ADR-003 · React + Vite 실험 대상

**결정:** React 19.3.1 / Vite 8.3.5를 개발 의존성으로 사용하고, `react-jsx`와 Vite 기본 TSX 변환을 사용한다. HMR 고도화를 위한 React 전용 플러그인은 필요하지 않아 추가하지 않았다.
**이유:** 프론트엔드 도메인의 타입·함수·UI 연결을 작은 앱으로 보여줄 수 있다. Next.js의 Server/Client·서버 함수 의미는 별도 검증이 필요해 후속 단계다.
**검증:** Node 22.19.0에서 타입 검사·빌드·브라우저 동작 확인. Vitest 5.1.0 사용.

## ADR-004 · NextClosure와 한도

**결정:** 폐포 연산과 NextClosure를 작은 구현으로 제공하고, 128 객체 / 64 속성 / 256 개념 상한을 기본값으로 둔다. 출력 관계는 후보 간 전체 엄격 포함 관계이며 cover edge는 아니다.
**이유:** 최소 수학 정의를 코드·테스트로 투명하게 검토할 수 있다. 별도 FCA 패키지가 필요한 성능/기능 요구는 아직 없다. 512개 작은 context에 독립적인 exhaustive oracle을 사용해 재구현의 정확성 부담을 확인했다.
**결과:** 큰 context는 거부, 개념 폭증은 불완전 상태를 명시한다. 실무 후보 ranking은 미구현.

## ADR-005 · 유한 열거, 명시적 입력 전제, SMT 보류

**결정:** 문자열 union/상수 enum을 최대 4,096 조합까지 열거하고 양방향 함의·반례를 계산한다. `--assume-same-input`을 요구한다. 조건의 비동치만으로 버그를 선언하지 않는다.
**이유:** 첫 사례는 solver 없이 정확한 결과를 구할 수 있다. 임의 JS의 제어 흐름·부작용·상관관계를 해결하려 하지 않는다.
**결과:** 단일 반환식, 필수 입력, 제한된 논리 연산만 지원. 숫자 범위·복잡한 제약의 실제 필요와 비교 이득이 확인될 때 SMT/Z3를 검토한다.

## ADR-006 · LLM·의미 확정 보류

**결정:** 첫 PoC는 결정적 분석만 구현한다. LLM·문서 해석·승인·OWL/RDF·MCP·DevTools·자동 수정은 구현하지 않는다.
**이유:** 코드 사실·수학 계산의 정확성을 먼저 확인하고 의미 추론은 후속 A/B/C/D 실험에서 평가한다.
**결과:** 자동 출력은 공식 업무 정책이 아니다. [RESEARCH](RESEARCH.md)에 미검증 가정을 별도로 유지한다.

## ADR-007 · private 패키지와 라이선스

**결정:** 루트 package name은 `ontosary`, `private: true`, 프로젝트 라이선스는 MIT로 둔다. pnpm 11.19.0과 정확한 직접 의존성 버전을 기록한다.
**근거:** 2026-11-03 npm registry에서 `npm view ontosary name version --json`이 E404를 반환했다. 이는 당시 조회 결과이며 이름 예약·향후 등록 가능성을 보장하지 않는다. 공개 전 이름/권리·npm 정책을 다시 확인한다.
**결과:** npm 배포·Git 원격 생성은 하지 않는다. 설치된 전이 의존성의 라이선스는 [DEPENDENCIES](DEPENDENCIES.md)에 기록한다. pnpm이 생성한 특정 Vitest 버전의 release-age 예외는 lockfile과 함께 유지하며 전역 정책을 바꾸지 않았다.


## ADR-008 · GitHub Flow, Conventional Commits와 원격 연결 — 2026-11-06

**결정:** 원격 `origin`을 `https://github.com/hyeonhb/ontosary.git`로 설정한다. GitHub Flow와 Conventional Commits 1.0.0을 채택하고 상세 규칙은 CONTRIBUTING.md, 작업 지침은 AGENTS.md에 유지한다.
**이유:** 작은 단일 제품에서 짧은 변경 단위와 한 통합 브랜치로 검토·되돌리기를 단순하게 유지한다. 영구 develop/release 브랜치는 현재 필요하지 않다. 공식 자료와 프로젝트 자체 선택을 CONTRIBUTING에서 구분한다.
**적용:** 원격의 `5d33ab6` 초기 LICENSE 커밋을 기반으로 `chore/initial-poc`에 기존 작업을 기록한다. 이어지는 정확성 수정은 해당 초기 작업에 의존하는 `fix/normalization-soundness`에서 진행한다. main에는 원격 이력을 유지한다. 원격 보호 규칙/CI를 구성했다고 주장하지 않는다.

## ADR-009 · 원격 저장소의 Apache-2.0 유지 — 2026-11-06

**결정:** 사용자 확인에 따라 GitHub의 기존 Apache-2.0 LICENSE를 그대로 유지하고 package.json/README의 프로젝트 라이선스를 통일한다.
**맥락:** 최초 PoC는 MIT로 초기화됐지만 이후 사용자가 생성한 원격에는 Apache-2.0이 있었다. ADR-007은 당시의 결정 기록으로 보존하며 현재 라이선스 선택은 이 항목이 대체한다. 전이 의존성의 개별 라이선스는 바뀌지 않는다.


## ADR-010 · enum 상수 receiver와 explicit this의 보수적 경계 — 2026-11-06

**근거:** 독립 리뷰 R1/R2에서 진단 0개인 코드에 대한 false Equivalent와 false Different가 확인됐다. 계산기의 올바른 열거가 잘못된 소스→IR 변환을 보정하지 못한다.
**결정:** enum 멤버 심볼만으로 constant folding하지 않고, receiver가 enum 선언으로 해소되는 직접 식별자인지 먼저 검사한다. 괄호와 named import alias는 유지한다. optional/call/assertion/non-null/nested receiver, enum 객체 변수·namespace 경로는 Unsupported로 거부한다. 전자가 enum 타입이라는 사실만으로 실행을 생략하지 않는다.
**결정:** explicit this는 전체 predicate와 개별 condition에 같은 정책으로 거부한다. TS가 this 매개변수를 emit에서 제거하기 때문에 AST 인덱스를 런타임 인자로 쓸 수 없다. 새로운 this 의미·인자 메타데이터·지원 기능을 도입하는 대신 좁은 거부를 택했다. 소스 signature는 그대로 보존한다.
**트레이드오프:** 안전한 namespace 경로나 실제로 같은 enum 객체를 가리키는 별칭도 미지원이 된다. 선언 기반 허용 경계를 확장하려면 별도 사례·실행 대조가 필요하다. 임의 프로젝트 코드는 실행하지 않으며 통제된 테스트 fixture만 실행한다.
**근거 링크:** [TypeScript this parameters](https://www.typescriptlang.org/docs/handbook/2/classes.html#this-parameters), [TypeScript enums](https://www.typescriptlang.org/docs/handbook/enums.html), [2026-11-04 리뷰](reviews/2026-11-04-poc-review.md).


## ADR-011 · 실제 분석 파일 목록과 제외 근거 — 2026-11-06

**근거:** R3는 allowJs 프로젝트에서 방문하지 않는 JS가 ScanResult.files에 포함되어 실험 파일 분모를 부풀렸다.
**결정:** Compiler Program의 로컬 구현 파일을 지원 확장자와 제외 파일로 먼저 분리한다. files에 넣는 배열만 AST 방문에 사용한다. 제외 파일은 각각 evidence.file/위치/reason을 가진 omissions로 남긴다. Program·checker·diagnostics는 원래 입력을 유지한다.
**트레이드오프:** 전체 Program 파일 manifest나 새로운 coverage 스키마를 추가하지 않는다. files는 실제 분석 파일 수이고 프로젝트 전체 coverage 비율은 아니다. 선언 파일/외부 라이브러리는 기존 범위대로 미열거다. allowJs만 켜져 있고 JS가 없으면 누락도 없다. 기존 문서 계약을 복원한 버그 수정이므로 schemaVersion 1을 유지한다.
**검증:** mixed TS/TSX/MTS/CTS와 JS/JSX/MJS/CJS, 선언 파일, imported JS 타입/참조, JS-only, 제외 파일 진단, CLI JSON을 회귀 검증한다.

## ADR-012 · 검증 후 자동 원격 반영 — 2026-11-06

**결정:** 사용자의 지속 승인에 따라 작업 완료 시 로컬 커밋에 그치지 않고 branch push, PR 생성·검토, 검사 충족 후 merge와 main 동기화까지 수행한다. CONTRIBUTING/AGENTS에 유지한다. 원격 보호 규칙은 우회하지 않고 검증한 head SHA를 확인한다.
**적용:** 초기 두 커밋은 서로 독립적인 이력을 보존하도록 PR #1을 merge 방식으로 반영했다. 후속 focused PR은 기본 squash 정책을 따른다. 구현 담당자의 self-review를 독립 리뷰 승인으로 표시하지 않는다. 현재 저장소에 원격 CI가 구성돼 있다고 주장하지 않는다.


## ADR-013 · 코어를 고정한 실제 corpus 관찰 — 2026-11-07

**결정:** 공개 원본 소스의 revision·MIT 고지·파일 hash와 분석 범위를 고정하고, 제품 코드 실행/의존성 추가 없이 정적 관찰한다. source/lockfile fingerprint로 분석기 변경을 감지한다. 라벨은 첫 scan/FCA 전에 소스를 읽어 작성하며 agent 작성·사람 pending으로 표시한다. 원시 결과와 해석, 코드 사실과 업무 의미, 함수 predicate와 개별 condition의 지원을 분리한다.

**이유:** 인공 예제 밖에서의 실패·설정 비용·상한을 관찰하는 동안 지원 문법을 바꾸면 측정 대상과 정답을 혼동하게 된다. 원래 config 실패를 보존하고 별도 config의 변경을 manifest에 명시한다. FCA 상한을 높이지 않고 전체와 작은 구성요소 결과를 따로 저장한다.

**트레이드오프:** 원본 p-queue 개발 환경의 shared config/Node 26/TS 6까지 설치하지 않고 현재 고정된 TS 5.9/Node 22 타입으로 분석한다. date-fns는 전체 프로젝트가 아니라 import closure다. 별도 설정과 목적 표본의 결과를 upstream build나 전체 프로젝트 coverage로 일반화하지 않는다. 외부 타입 ID는 의존성 상대 경로에 영향을 받는다. JSON 원시는 무손실 gzip으로 저장하고 사람이 읽을 라벨·검토표·실패·요약을 별도 제공한다. 후보·라벨을 사람 승인으로 올리지 않으며, 다음 우선순위는 사용자 과업 검토다.

## ADR-014 · 다음 제품 실험은 업무 개념·관련 코드 탐색 우선 — 2026-11-07

**근거:** 실제 corpus 관찰은 재현됐지만 p-queue/date-fns는 utility 표본이고 사전 논리 비교는 0/2 지원이다. 코드 사실 라벨의 확인만으로 프론트엔드 업무 이해의 개선을 입증할 수 없다. 독립 리뷰 중 탐색 우선/규칙 비교 우선/두 방향 비교를 사용자에게 제시했다.
**사용자 결정:** “업무 개념·관련 코드 탐색 우선”을 선택했다. 다음 제품 실험은 실제 업무 개념 하나에서 관련 코드·조건의 근거에 도달하는 과업으로 구성한다. 논리 비교는 지원·입력 전제가 맞을 때 보조 근거로 유지한다. 자동 의미 확정이나 온톨로지 전환을 요구하지 않는다.
**순서:** 먼저 측정 평가기의 R4/R5를 작은 별도 작업으로 보완하고, 검색/LSP·동일 facts의 단순 그룹 대비 탐색 과업을 설계한다. FCA/LLM/SMT의 채택·확대·삭제를 이 선택에 포함하지 않는다. 후보 수나 지원 문법 수는 사용자 가치의 대체 지표가 아니다.
**지속 협업:** 사용자는 앞으로도 중간에 기술적·철학적 판단 또는 방향 확인/변경이 필요하면 요청해 달라고 했다. 주요 사용자 과업·근거/승인 원칙·기술 투자 방향 전환은 근거·선택지·권고를 제시해 확인한다. 일상적인 오류 수정·검증 및 이미 승인된 원격 반영에 반복 승인을 추가하지 않는다.
**관련:** [corpus 독립 리뷰](reviews/2026-11-07-corpus-independent-review.md), [후속 지시](reviews/2026-11-07-corpus-review-next-plan.md).


## ADR-015 · 평가 계약 V2와 역사적 V1의 병존 — 2026-11-08

**결정:** R4/R5는 제품 코어를 바꾸지 않고 버전이 분리된 corpus 평가기에서 해결한다. 타입·종류는 원문에서 작성한 명시적 expected 값으로 대조하고, FunctionFact에 없는 generic/소속·상속 의미는 claim을 좁혀 unverified로 남긴다. reference/property에는 use와 target 근거를 모두 요구하며 평가기에서 TypeScript AST로 선언 이름·실제 본문 사용·call 구문을 구분한다. 재귀 target를 일괄 제거하지 않는다.

**이유와 비용:** 과거 라벨·평가기·runner를 바꾸면 이전의 약한 판정/재현 hash를 소급 수정하게 된다. 작은 V2 runner를 별도로 유지하는 중복 비용을 감수한다. 현재 기본 명령은 V2이고 V1은 별도 명령으로 과거 재현에만 쓴다. 모든 라벨의 전후 claim/status/checks/unverified와 변경 이유를 기록한다. 같은 22/24라도 검사 범위가 바뀌었으므로 성능 개선 지표가 아니다.

**한계:** type text/단순 union 비교는 일반 타입 동치가 아니며 AST use 확인은 실제 실행/전체 호출 그래프의 증명이 아니다. 사람 승인과 시간은 미측정으로 유지한다. 다음 제품 실험은 ADR-014의 업무 개념 탐색 방향이며, 이번 수정은 측정 품질 보완이다.


## ADR-016 · 타입 전용 use 문맥과 평가기 V3 — 2026-11-08

**결정:** R5 잔여 오류는 use의 조상에서 TypeNode와 함께 TypeAliasDeclaration / InterfaceDeclaration / TypeParameterDeclaration을 거부한다. 개별 signature 이름 목록을 늘리는 대신 타입 전용 선언 문맥 전체를 확인한다. 실제 표현식이 타입 선언의 signature를 target으로 가리키는 것은 허용하며 self-target 제거로 대체하지 않는다.

**버전:** 입력 계약과 24개 라벨은 V2 그대로, 평가기만 V3다. V1/V2 코드·입력·과거 결과를 실행 가능하게 보존하고 V3 코드/hash/새 결과를 별도로 기록한다. 기본 명령은 V3, 과거 V2는 명시적 `experiment:corpus:v2`다. 작은 runner/evaluator 복제 비용을 감수해 역사적 판정을 소급 변경하지 않는다.

**근거와 한계:** 독립 probe 7/9 → 9/9, 인접 actual-scan 18/27 → 27/27, 정상 재귀/import/읽기/속성·메서드 target를 확인했다. core/CLI·의존성·문법 지원·분석 상한은 그대로다. 일반 AST 의미 분석이나 제품 가치 증명이 아니며 ADR-014의 후속 탐색 실험 방향을 유지한다. [검증 인계](reviews/2026-11-08-type-context-fix.md).

## ADR-017 · 첫 업무 탐색 표본은 공개 앱 후보부터 조사 — 2026-11-08

**사용자 결정:** V3 독립 리뷰 중 공개 TypeScript 업무 앱 후보 조사와 사용자가 지정할 익숙한 코드베이스 중 전자를 선택했다. ADR-014의 업무 개념·관련 코드 탐색 우선 방향을 유지하며 재현·공유 가능한 표본부터 준비한다.

**현재 권고:** [후보 조사](reviews/2026-11-08-public-app-candidates.md)에 고정 revision과 원문/설정/라이선스 근거를 남겼다. Saleor Dashboard를 첫 적합성 점검 후보로 권하지만 strict=false·codegen/의존 경계가 있어 아직 채택하지 않는다. Medusa의 조사 revision은 주문 화면의 별도 라이선스 대상 hook 의존을 확인해 우선 보류한다. 이는 리뷰어의 후보 순서 권고이며 사용자가 특정 앱을 확정한 결정은 아니다.

**전제와 범위:** 원래 설정 실패·비용을 공개하고 core의 strictNullChecks 전제는 유지한다. 별도 분석 설정은 변경 조건과 한계를 드러내야 한다. 앱 선정/분석 성공/사람 승인/효용 검증은 미완료다. 다음 작업은 [적합성 및 한 과업 준비](reviews/2026-11-08-public-app-next-plan.md)이며 주요 사용자 문제·기술 투자·근거 원칙 변경은 사용자 판단을 요청한다.


## ADR-018 · 공개 앱의 실패를 보존하는 제한된 적합성 점검 — 2026-11-08

**결정:** 각 후보의 원문 과업/anchor를 scan 전에 작성하고, 고정 archive의 원래 설정 → 명시적 과업 진입 설정을 차례로 관찰한다. 후보는 Saleor와 추가 Vendure 1개로 제한한다. 조상 node_modules 없는 cache에서 관찰하며 미설치 의존성을 임의 any/stub으로 대체하지 않는다. Saleor는 별도 설정에서 strictNullChecks를 켜되 upstream와 동일하다고 주장하지 않고, Vendure는 원래 strict를 유지한다.

**결과:** 두 후보 모두 이번 준비 예산에서 오류 없는 입력을 확보하지 못했다. 이 상태의 facts로 단순 그룹/FCA·제품 효용 결과를 만들지 않는다. 원본/범위/의존 경계/원시 진단과 실패 재현을 완료물로 인정한다. 원래 generated source와 원문 any는 보존하되 정밀도 한계로 기록한다. Vendure HTML template는 수동 과업 근거이며 core TS coverage로 세지 않는다.

**후속 권고:** 원래 strict가 켜진 고정 Vendure Admin UI의 의존성/common 빌드 준비 비용만 제한적으로 추가 검증한다. 이는 아직 앱 채택·새 기술 투자·사용자 실험 승인이 아니며 core 전제 완화나 원문 변경이 필요해지면 별도 판단 근거를 마련한다. ADR-014/017의 업무 탐색/공개 앱 방향은 유지한다. [결과 인계](reviews/2026-11-08-public-app-suitability.md).

## ADR-019 · Vendure 환경 준비는 30분 한도로 한 번 더 검증 — 2026-11-08

**근거:** PR #11 독립 리뷰에서 실패 관찰을 재현했고 새 결함은 발견하지 않았다. 의존성을 설치하지 않아 실제 준비 비용과 오류 없는 분석 가능성은 미측정이다. 동시에 Vendure 네 진입 파일의 함수 inventory도 129개로 기본 FCA 객체 상한 128을 넘으며 HTML 두 근거는 TS facts 밖이다.

**사용자 결정:** 제한된 환경 준비와 탐색/논리 검증 전제 분리 설계를 제시했고, 사용자는 “Vendure 준비를 30분 한도로 한 번 더 검증”을 선택했다. 업무 개념 탐색/공개 앱 방향은 유지하며 이번에 코어 계약을 분리·완화하지 않는다.

**실행 경계:** 고정 v3.5.0의 기존 의존성/common 빌드·최초 재분석을 하나의 30분 마감으로 제한한다. 설치 성공, 진단 해소, 탐색/FCA 범위 적합성을 별도 판정한다. 실패/시간 초과/범위 부적합이면 중단하고 근거를 남긴다. 원문/lockfile 패치·stub·상한 증가·추가 후보 탐색·사람 효용 실험은 포함하지 않는다. 이후 과업 범위 또는 분석 전제 변경은 이 결과를 보고 다시 결정한다. [독립 리뷰](reviews/2026-11-08-public-app-independent-review.md), [다음 개발 지시](reviews/2026-11-08-vendure-preparation-next-plan.md).
