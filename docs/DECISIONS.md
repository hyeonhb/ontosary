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

**ADR-019 실행 결과(2026-11-08):** 30분 중 359.668초에 설치/common 빌드와 기존 과업 설정의 진단 0을 확보했다. 전체 context 2,264객체/4,288속성이 기본 128/64를 넘어 추가 준비 없이 종료했다. 원래 설정의 test 이름 오류 495개도 보존했다. 같은 cache의 관찰만 반복했고 설치/빌드 독립 재현이나 사람 효용 검증을 주장하지 않는다. 다음 과업 범위 선택 계약 검토는 권고이며 승인된 새 구현으로 취급하지 않는다. [실행 인계](reviews/2026-11-08-vendure-preparation.md).

## ADR-020 · agent 중심의 최종 목표와 작은 도메인 모델 실험 — 2026-11-08

**사용자 목표 정렬:** 최종 목표는 기존 프론트엔드 프로젝트를 AI agent가 도메인을 이해하고 수정하기 좋은 프로젝트로 점진적으로 전환하도록 돕는 것이다. 온톨로지는 개념·관계·규칙을 agent가 참조할 수 있게 하는 수단이고, FCA는 코드의 공유 속성에서 후보를 찾아 모델 구축 부담을 줄이기 위한 방법이다. ADR-014의 탐색 우선은 첫 사용 경로로 유지하되 최종 목표 전체로 해석하지 않는다. 사용자가 단기 목표·개발 지시 작성을 요청했다.

**유지할 원칙:** 사람 친화적인 코드를 agent에게 불리하다고 전제하지 않는다. 기존 코드 옆에 근거와 연결한 모델을 두는 것부터 시작한다. 전면 재작성·특정 OWL/RDF 형식·의미 자동 승격을 강제하지 않는다. 사용자의 예시 그림은 역할 설명이며 확정 아키텍처가 아니다. 코드 사실·발견 후보·사람 승인 지식, 관찰된 동작·의도한 업무 정책을 분리한다.

**다음 한 작업:** [S1 개발 지시](reviews/2026-11-08-domain-model-next-plan.md)에 따라 고정 Vendure 취소·환불의 모델 초안·근거 검증기·FCA 기여 대조를 별도 실험으로 만든다. 의미 있는 객체/역할 속성 계약을 사전 고정하고 같은 context의 단순 그룹과 FCA를 비교한다. 기존 전체 Program/원문·논리 전제·core/CLI 계약은 유지한다. 현재 기본 FCA 상한은 PoC 예산이며 영구 제품 한계가 아니지만, 이번에 상한을 늘려 성공 표본을 만들지 않는다. unknown·상한 초과·기여 없음도 관찰 결과다.

**분리할 가설:** H-O는 도메인 모델이 agent의 변경 품질/총비용을 개선하는지, H-F는 FCA가 모델 구축·검토에 추가 가치가 있는지다. FCA 전 모델과 후 모델의 차이를 기록하며 수동 작성한 지식을 FCA 자동 발견으로 세지 않는다. 이후 S2는 같은 agent의 작은 변경 과업 비교, S3는 효과가 관찰된 경우 변경 후 모델 갱신 비용 검증이다. 지금은 둘 다 미검증이다.

**보류할 결정:** 사람의 업무 의미 승인, 장기 모델 표준/영구 ID, 코어 계약·상한 확장, 전체 프로젝트 구조 변경은 별도 근거와 사용자 판단이 필요하다. S1 구현의 일상적 선택과 지속 승인된 저장소 반영은 반복 승인을 만들지 않는다. 기존 사람 탐색 프로토콜은 보조 연구 후보로 보존한다.

## ADR-021 · S1 파생 역할 context와 근거 검증 경계 — 2026-11-08

**결정:** core/전체 Program과 별개로 네 클래스의 자체 이름 있는 메서드 전체와 직접 멤버 호출 6역할을 실험 안에 고정했다. 중첩 callback 호출은 소속 메서드 원문 영역으로 집계하고 생성자/접근자/필드/익명 객체/HTML 등은 제외한다. 호출식 역할과 정확한 선언 identity를 대조하고 불확실하면 unknown으로 중단한다. 같은 incidence의 단순 그룹에도 공유 intent/근거를 제공한다. 기본 상한과 core 계약은 유지한다.

**모델 계약:** FCA 전 agent 초안 12항목을 보존하고 모든 업무 의미는 검토 대기로 둔다. validator는 연결/출처 정합성·원문 만료·승인 메타데이터만 검사한다. 실제 사람 결정이나 업무 의미를 인증하지 않는다. revision 기반 ID와 보수적 stale 전파는 이번 실험용이며 제품 API/영구 ID 전략이 아니다.

**관찰:** 78×6에서 unknown 0, 후보 5개는 모두 단순 그룹과 동일하다. 기존 두 항목에 후보 링크만 추가했고 새 의미 발견은 0이다. 다음은 S1 독립 리뷰 후 S2 계약/fixture 동결 권고이며 H-O·H-F 일반 효과나 Gate 상승으로 해석하지 않는다. [인계](reviews/2026-11-08-domain-model-prototype.md).

**ADR-021 독립 검토 후속(2026-11-08):** 계산·고정 결과는 재현됐으나 R6(탐색 방향 계약)·R7(standalone 분석 입력 검증) 보완이 필요하다. [현재 지시](reviews/2026-11-08-domain-model-review-next-plan.md)는 V1 보존과 새 버전 검증을 요구하며 S2 실행보다 우선한다. 최종 목표/상한/코어를 바꾸는 결정은 아니다. 역방향 조회의 구현 선택과 입력 검사 재사용은 개발 범위 내에서 정하되 근거 검사와 업무 의미 승인은 계속 분리한다.

## ADR-022 · S1 V2 소비 계약 보완 — 2026-11-08

R6은 모델 의미를 변경하지 않고 incoming/outgoing 한 단계 조회로 보완한다. direction/declaredEdge를 출력하며 역방향 조회는 대칭 업무 관계가 아니다. R7은 V1 runner의 고정 입력 검사 로직을 V2 공통 함수로 분리하여 새 runner/standalone 경로가 공유한다. V1은 역사적 재현을 위해 수정하지 않는다. 전체 입력 미검증/변경 시 모든 자동 역할 fact/candidate와 모델 항목을 보수적으로 재검토시킨다. anchor-only는 partial/exit1이며 승인/전체 성공이 아니다. [V2 사용 경로](../experiments/domain-model/v2/README.md). S2 비교·core 확장은 하지 않았다.

## ADR-023 · S2는 변경 전 모델의 수정 지원 효과부터 검증 — 2026-11-08

**사용자 결정:** S2는 변경 전 모델이 agent의 수정 작업에 도움이 되는지 먼저 검증한다. 변경 후 모델 갱신·근거 재연결·승인 승계는 이번 실험 범위에 넣지 않는다. 이 범위에서 선행 기술 부채와 분석 세션·도메인 모델·조회 계층의 구조를 제안하고, 구조 합의 후 개발 지시를 작성한다.

**미확정 사항:** [아키텍처 제안](reviews/2026-11-08-s2-architecture-proposal.md)은 검토안이다. 준비 단계의 단일 분석 세션, 동결 bundle/순수 조회, 사전 생성 view와 동일한 파일 도구, 실험 내부 모듈 배치를 권고하지만 아직 사용자가 확정한 구현 구조가 아니다. reason 과업·fixture/oracle·A/B/C 제공물·모델/예산·반복 횟수도 별도 동결이 필요하다. 이번 결정은 S2 실행 또는 제품 core 변경 착수 지시가 아니다.

## ADR-024 · S2 준비 세션·동결 모델·조회 구조 합의 — 2026-11-08

**사용자 결정:** [제안 구조](reviews/2026-11-08-s2-architecture-proposal.md)로 진행하고 구체적 개발 지시를 작성한다. 준비 배치의 단일 baseline 분석 세션, 동결 모델과 순수 조회, 사전 생성 view를 동일 파일 도구로 소비하는 방식, 타입 검사되는 S2 실험 내부 모듈 배치를 채택한다. 제품 core/public API 통합과 S3 지식 갱신은 이번 범위 밖이다.

**다음 작업:** [S2 준비 구현 지시](reviews/2026-11-08-s2-development-instructions.md)에 따라 선행 부채·실험 배포·평가 하네스·재현 근거를 준비해 독립 리뷰에 넘긴다. 현재 리뷰 세션은 지시/맥락 문서만 작성했으며 구현·본 비교를 실행하지 않았다. 과업의 필수 행동·fixture 원문 충실성·B/C 동등성·agent 버전/예산·격리/실행 조건은 검토 가능한 자료로 만든 뒤 동결한다. 구조 합의가 미정 실험 조건이나 실제 업무 정책의 승인을 대신하지 않는다.

## ADR-025 · S2 준비 구현의 검증·배포·평가 경계 — 2026-11-08

**구현 선택:** S1의 고정 산출물을 runtime 타입 검사와 원문 입력 감사로 검증한 뒤 단일 Program 세션의 내부 seal 객체만 포장에 사용한다. 입력 baselineId, 모델 의미 modelId, 배포 bundleId를 분리하고 key 정렬/배열 순서 보존으로 결정성을 유지한다. query는 소유 복제와 순수 색인만 제공한다. 승인 ingest는 미지원이며 원래 검토 대기 상태를 유지한다. 관련 후보의 구성원 선언/속성 정의를 포함하고 무관한 cell 참조 제외는 selection에 기록한다. 제품 API 승격/새 FCA 의미 발견은 아니다.

**평가 선택:** allowlist workspace에는 원문과 조건별 사전 생성 자료만 넣는다. evaluator/참조 수정은 별도이며 같은 호스트 폴더를 격리라고 주장하지 않는다. 제출 본문/상대 helper를 실제 실행하고 변경된 constructor/field/inheritance/decorator 및 Promise/async/미검토 RxJS 연산자는 unsupported로 보고한다. 제한된 fixture가 전체 Angular/서버 동작을 증명하지 않는다.

**미결 사항:** invalid reason에서 요청과 연쇄 환불을 중단하는 참조 수정은 검토용 권고이며 제품 정책 승인이 아니다. 사람의 정보 동등성/원문 충실성 검토, 정책·agent 모델/예산·격리 동결 전 readyForTrial=false다. 이번 결과는 준비 구현·oracle 교정이며 H-O/H-F 효과나 Gate를 올리지 않는다. [실제 결과](reviews/2026-11-08-s2-preparation.md).

## ADR-026 · 제출 타입 문맥·동일 소스 결합·취소 요청 보존 계약 — 2026-11-09

**근거/범위:** 독립 리뷰 R8/R9/R10과 [보완 지시](reviews/2026-11-09-s2-contract-fix-instructions.md)에 따라 S2 평가기를 보완한다. 준비 세션·모델/조회·제품 API는 유지한다.

**선택:** 일반 제출은 완전한 source inventory를 읽은 메모리 snapshot이다. 교정에만 고정 baseline+명시적 delta를 사용한다. 원래 클래스/호출자와 새 helper를 고정 설정/의존성의 CompilerHost로 검사하며 사라진 원문을 복구하지 않는다. 타입/검사 범위가 실패·미지원이면 동작은 not-run이다. 실행기는 같은 snapshot을 읽고 Program·제출·실행 hash를 대조한다. 설정/비TS/삭제·검사 범위 밖 변경, 기존 실행 seam/비동기 한계는 합격이 아니다.

**판정:** 기대 요청은 fixture/명시 계약에서 독립 작성한다. 전체 취소·환불 payload, 호출 수/순서를 비교하고 기록 시점에 복제한다. 객체 key/line 순서는 무시하되 line 중복·누락은 유지한다. undefined 필드 부재는 JSON 전송과 동일하게 처리한다. 취소 reason만 trim/nonblank를 적용하며 환불만·혼합 경로의 환불 reason은 보존한다. 별도 helper 해법도 통과하므로 정확한 참조 diff를 요구하지 않는다.

**보류:** 빈 stream 기반 참조 수정은 초안(a)의 검토 자료다. 최종 제품 정책, UI·stream error 대안, 사람의 원문 충실성/B-C 동등성, OS 격리·agent 실행 조건을 승인하지 않는다. readyForTrial=false이고 본 비교·H-O/H-F 효과·S3는 미검증이다. [실제 결과](reviews/2026-11-09-s2-contract-fix.md).

## ADR-027 · 실제 modal 입력과 동기 resolve를 잇는 평가 대역 — 2026-11-09

**근거:** R8/R10 독립 해결 뒤 R9의 부모→dialog 입력 우회를 발견했다. [보완 지시](reviews/2026-11-09-s2-modal-fix-instructions.md)에 따라 평가 대역만 보완한다. 제출 타입/snapshot/전체 payload 비교와 준비·모델·조회 구조는 유지한다.

**선택:** 사전 실행 dialog/고정 반환값을 제거한다. executor가 로드한 실제 constructor 참조를 식별하고 부모의 options.locals.order를 복구 없이 적용한다. 사용자 선택·제외된 UI 계산 상태는 별도 fixture이며 locals/resolveWith와 충돌하면 미지원이다. 구독 시 dialog를 생성해 제출 select/cancel을 실행하고 resolve 즉시 해당 구독의 next/complete로 전달한다. 호출별 identity/입력/행동/resolve/전달 trace를 보존한다.

**지원 경계:** 비API 시나리오마다1modal·1구독·1동기 resolve다. undefined 닫기는 실제 전달하지만 미해결을 임의 dismiss로 바꾸지 않는다. 미해결/다중 resolve/재구독/추가 호출·알 수 없는 component·잘못된 locals 형식/옵션은 unsupported다. 정상 형식의 잘못된 ID/active는 실행 후 독립 payload assertion으로 검출한다. 함수/절대 경로 대신 상대 선언 정보와 안전한 trace 값을 남긴다.

**보류:** Angular 생성/field/ngOnInit/HTML/전체 UI 계산·비동기 overlay와 네트워크는 대역/제외 상태다. 구현 선택은 최종 닫힘/invalid 정책·사람 충실성/동등성·격리/agent 조건의 승인이 아니다. readyForTrial=false이며 본 비교·효용/S3는 미검증이다. [실제 결과](reviews/2026-11-09-s2-modal-fix.md).

## ADR-028 · S2 과업 정책과 비교 실행 전 준비 승인 — 2026-11-10

**사용자 결정:** R8/R9/R10 독립 검증 뒤 제안한 조합을 승인했다. invalid 취소 입력은 요청과 연쇄 환불 없이 종료하며, dialog는 undefined resolve, service는 값 방출/예외 없이 완료한다. 정상 취소 사유만 trim하고 환불만/혼합 경로의 환불 사유와 기존 요청 값을 보존한다. 실제 Vendure 최종 제품 UX 정책이 아닌 실험용 클라이언트 로컬 요구다.

**비교 조건:** A는 코드/기존 문서/공통 과업, B는 A와 구조화된 변경 전 모델, C는 A와 같은 지식을 담은 일반 설명 문서다. 현재 C의 필드 나열을 재구성하고 명제·관계·근거·미확인 사항·검토 상태의 양방향 대응을 검토한다. 자료 동등성 승인과 업무 의미 승인은 별개이며, 아직 작성되지 않은 새 C를 사람이 승인했다고 기록하지 않는다.

**실행 계획:** 현재 개발에 사용된 동일 모델/추론 설정의 정확한 식별자를 확인해 고정하고 새 세션으로 조건별3회, 총9회를 계획한다. 순서 균형/무작위 배정, 실행당30분·누적 입력/출력100,000토큰, 동일 파일/셸/공개 검증 도구, 서브에이전트·외부 검색·중간 힌트 없음이다. 실제 강제·계측 가능성과 정확한 runtime은 준비에서 확인한다. 지원 불가한 조건은 임의로 대체하지 않고 인계한다. 평가 범위는 현재의 제한된 메서드/동기 modal 실행으로 유지한다.

**승인 범위:** [개발 지시](reviews/2026-11-10-s2-trial-preparation-instructions.md)에 따라 과업/실행 계약·C 대응 검토 자료·실제 격리/계측·새 배포 동결까지 준비한다. 기존 교정과 실제 모델을 호출하지 않는 대역 검증을 수행할 수 있다. 본 비교는 준비 결과의 독립 리뷰 후 별도 진행하며 이번에 비교 agent를 생성하거나 과업을 실행하지 않는다. 기술 준비가 끝나도 trialAuthorized/readyForTrial=false, 결과 null을 유지한다. H-O/H-F·S3는 미실행이다.

## ADR-029 · 기존 CLI·macOS 준비와 관측 토큰 계약 — 2026-11-10

**사용자 후속 결정:** 이번 준비는 기존 Codex CLI와 검증 가능한 macOS 격리로 한정하며 API 실행기로 확대하지 않는다. 누적100,000토큰 hard cap은 이번 탐색 비교의 필수 통과 조건에서 제외한다.30분 시간 제한, usage 원시 기록과 계측 범위·누락·초과 보고를 준비한다.100,000은 참고선이고 임의로 숨긴 새로운 예산이 아니다. 토큰 강제 상한 부재만으로 준비를 차단하지 않되 격리·공정한 자료·제출 평가 결함은 계속 차단한다. 실제 모델 호출과 비교는 준비 결과 리뷰 이후의 별도 승인이다. 이 결정이 [원래 지시](reviews/2026-11-10-s2-trial-preparation-instructions.md) §5의 엄격한 토큰 조건을 대체하며 과거 지시는 보존한다.

**구현 선택:** 새 공통 TASK와 안내, B를 유지한 C 설명 문서·양방향 leaf inventory, 고정 환경의 공개 타입 검사, macOS Codex permission profile/usage 대역/전체 source·auxiliary 수집을 실험 내부에 둔다. leaf 일치와 문서 drift 검사는 자연어 동등성 증명이 아니다. 사용자/독립 agent를 사람이 승인한 것으로 기록하지 않는다. 정적 bundle과 자기 hash를 제외한 execution manifest를 분리하고 환경 증거 hash로 연결한다.

**실제 차단:** 기본 최소 권한의 package.json 읽기 예외를 별도 Node 복제와 명시적 deny로 보완했다. 그러나 process-group 종료에서 탈출한 detached 자손 반례가 남아 전체 격리/불변 snapshot의 기술 준비를 완료로 표시하지 않는다. 실제 세션의 도구/인증/전역 지시 격리, backend immutable model version, 자원 상한도 별도 확인이 필요하다. 현재 run entry는 모델 dispatch를 거부한다. C 사람 대응 검토·업무 의미 승인·본 비교·H-O/H-F·S3는 수행하지 않았다. [완료 부분·남은 차단 인계](reviews/2026-11-10-s2-trial-preparation.md).

## ADR-030 · R11 미확인 종료의 production 차단과 R12 관찰 합계 — 2026-11-10

기존 CLI/macOS의 process-group 정리로 모든 writer 종료를 증명할 수 없고 kqueue NOTE_TRACK 최소 재현도 ENOTSUP였다. [선택 기록](../experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix/SELECTION.md)에 근거·대안·비용을 남겼다. 추가 권한/플랫폼이나 셸 계약 변경을 자동 채택하지 않는다. R11은 unresolved이며 bounded 진단 실행 결과로 정상 제출 권한을 발급하지 않는다. production 수집/평가를 거부하고 진단/known reference 교정을 명시적으로 분리한다.

usage는 순차 turn 상태와 이벤트 identity, EOF/종료/절단을 결합한다. 모순된 turn은 합계에서 철회하고 전체가 불완전하면 total=null이다. 정상 subtotal도 공급자 소비 하한이라고 부르지 않는다. 현재 runtime의 종료 미확인 역시 전체 확정을 차단한다. 합성 fixture만 확정 경로를 검증한다. ADR-029의 token hard cap 제외와 실제 호출 금지를 유지하며, 이 보완은 독립 리뷰나 사람 승인·본 비교 승인이 아니다.

## ADR-031 · S2 일회성 컨테이너 경계 타당성 검증 승인 — 2026-11-10

**사용자 결정:** R12 독립 검증과 R11 미해결 확인 후, 일회성 컨테이너 경계를 우선 검토하면서 기존 Codex CLI·셸 사용 방식을 유지하기로 했다. 개발 세션은 [타당성 검증 지시](reviews/2026-11-10-s2-container-feasibility-instructions.md)에 따라 최소 실행/평가 경계·환경 재현·비용을 확인한다. ADR-029/030의 macOS 한정·컨테이너 미채택 범위를 이번 로컬 Linux 컨테이너 검토에 한해 확장한다. 특정 런타임의 채택이나 R11 해결을 미리 확정하지 않는다.

**운영 상한:** 지시에서 총4시간, 환경 준비 합산90분, 마지막30분 검증/정리/인계, 후보1개·원인 확인 후 환경 재시도1회, 신규 유료 비용0으로 정했다. 설치·이미지/의존성 준비와 대기도 포함한다. 원본 cache는 보존하고 Linux 복사본의 필요한 고정 의존성 준비만 허용한다. 추가 권한/유료 약관·CLI 포크/API 실행기·큰 프로젝트 재구축이 필요하면 중단하고 인계한다. 준비 실패도 유효한 조사 결과이며 검증 생략을 성공으로 기록하지 않는다.

**유지할 계약:** agent 실행과 제출 코드 평가에 각각 일회성 경계를 두는 타당성을 검증하며 제품 코어·과업·모델/B/C 지식·평가기 지원 범위는 유지한다. 전체 단위 종료 확인 전에 정상 제출을 수집하지 않는다. timeout 뒤 수집 코드는 진단용이며 정상 성공으로 계산하지 않고 실제 정지 시각을 기록한다. token hard cap 제외·100,000 참고선과30분 과업 제한은 유지한다. 준비의4시간 상한과 과업의30분 제한은 별개다.

**완료/보류:** feasible-for-next-preparation·conditional·blocked/inconclusive와 근거/비용을 인계하고 결과를 독립 리뷰한다. 기존 macOS 차단 경로와 live 거부는 유지하며 fixture 검증으로 실제 모델/인증을 검증했다고 표현하지 않는다. 실제 모델 호출·연결 시험·본 비교는 이번 범위 밖이다. trialAuthorized/readyForTrial=false·results=null·사람 검토 pending을 유지한다. 새 구조의 도입·본 비교 실행은 결과 리뷰 이후에 정한다.

## ADR-032 · 한정 컨테이너 조사 중단과 결과 범위 — 2026-11-10

ADR-031의 후보1개/환경 수정·재시도1회 상한을 적용했다. Lima 2.3.0/VZ와 준비 image build는 성공했지만, repo@manifest 실행 실패 후 Docker 호환 config ID로 바꾼 한 번의 시도도 실패했다. [인계](reviews/2026-11-10-s2-container-feasibility.md)의 판정은 inconclusive이며 런타임 자체의 부적합이나 R11 해결을 뜻하지 않는다. 남은 시간이 있어도 두 번째 수정을 자동 시도하지 않고 소유 VM/image/cache를 정리했다.

다음 결정 대상은 동일 후보의 native image identity 연결을 확인할 별도 작은 예산이다. 사용자에게 새 플랫폼/권한 확대를 이미 승인받았다고 가정하지 않는다. worker 종료·불변 수집·별도 평가 단위 및 Linux 의미 동등성의 모든 미실행 항목을 남기고, 기존 macOS production/live 차단·R12 계약·정적 자료를 보존한다. 초기 CLI stderr와 수정 실패 원문·재귀 manifest/cleanup을 보존하며 실제 모델/provider/본 비교는0회다.

## ADR-033 · 동일 후보 이미지 연결과 최소 실행의30분 재검증 — 2026-11-10

**사용자 결정:** inconclusive 결과 분석 후 동일 Lima/VZ + containerd/nerdctl 후보의 이미지 식별자 수정과 모델 없는 최소 실행을30분 한도로 재검증하기로 했다. [개발 지시](reviews/2026-11-10-s2-container-smoke-instructions.md)에 따라 image target과 실제 container의 대응, 비특권 셸·Node·공식 CLI version/help, 새 단위 반복과 정리를 확인한다. 결과를 리뷰한 뒤 후속 범위를 정하며 Vendure 준비·R11 adapter/평가·실제 모델/본 비교는 이번에 진행하지 않는다.

**운영 선택:** 이전의 고정 수정·재시도1회 규칙은 이미지 호출 오류에도 전체 중단을 유발했다. 이번 회차에서는 같은 후보의 원인이 확인된 국소 수정은 시간 안에서 허용하고, 새 근거 없는 반복·후보/버전 교체·권한 확대는 중단한다. 읽기/재준비/대기를 포함해30분,20분부터 새 탐색을 멈추고 마지막10분은 검증·정리·최소 보고에 쓴다. 유료 비용0이며 이전/이번/누적 비용을 구분한다. 기존90분/4시간을 초기화하거나 잔여 예산을 자동 사용하는 승인이 아니다.

**판정 경계:** smoke-passed는 최소 실행 확인에만 사용한다. 이전 manifest/config는 과거 증거이고 새 build의 실행 identity는 다시 관찰한다. R11 unresolved·R12 기존 검증 범위·trialAuthorized/readyForTrial=false·results=null을 유지한다. 실제 모델/provider/본 비교0회이며 CLI help를 실제 모델 도구/인증 경로의 검증으로 해석하지 않는다. ADR-031/032와 이전 원시 증거는 보존한다.

## ADR-034 · 최소 smoke의 native image 연결과 판정 한계 — 2026-11-10

ADR-033 회차에서 같은 Lima/VZ·nerdctl 후보를 유지하고 현재 target digest를 native metadata에서 조회해 `--pull=never` create에 사용했다. config digest/개별 diff ID/누적 chain ID를 분리하고 실제 container의 image target 및 snapshot parent로 연결을 확인한다. Docker 호환 RootFS.Layers와 개별 diff ID가 같다는 첫 검증의 잘못된 가정은 원시 metadata로 진단해 국소 수정했으며 실패 실행본을 보존했다. [smoke 결과](reviews/2026-11-10-s2-container-smoke.md)는4개 유한 최소 실행과 자원 정리의 통과다.

이를 전체 격리/자손 종료·불변 수집·Linux Vendure 평가·실제 모델 사용의 성공으로 확대하지 않는다. 이번 회차는 성공 후 종료하며 후속 경계/환경 준비의 범위·비용을 결과 리뷰 뒤 정한다. R11 unresolved, R12 기존 검증 범위와 production/live 거부를 유지한다.

## ADR-035 · 독립 감독자와 cgroup을 이용한 fixture 종료·수집 검증 — 2026-11-10

**사용자 결정:** 최소 smoke 독립 검토 이후 호스트 래퍼와 독립된 게스트 감독자, 실행별 cgroup, 전체 종료 확인 뒤 관리자 전용 수집 구조와 새3시간 상한을 승인했다. [개발 지시](reviews/2026-11-10-s2-lifecycle-fixture-instructions.md)에 따라 작은 셸·Node fixture로 정상 종료·timeout·래퍼/감독자 사망과 수집 실패를 확인한다. 이후 단계는 결과 리뷰 뒤 정한다.

**구조:** VM 내부 임시 systemd service가 시한과 생존 신호를 소유하며 worker와 별도 cgroup에서 실행한다. 작업별 상위 cgroup의 배치/이동 권한·전체 종료 상태를 확인한 뒤 source/auxiliary 전체를 manager staging으로 수집하고 원자적으로 결과를 공개한다. supervisor 사망에는 종료 후 별도 정리를 사용하고 정상 결과 발급을 금지한다. 상태 확인 불가·미완료 시작 요청·복사 실패에는 결과 확정과 다음 실행을 차단한다. 일반 파일/디렉터리와 유한 크기만 지원하는 fixture 전용 수집이며 범용 제출 권한/저장소를 만들지 않는다.

**운영 상한:** 읽기·환경 재준비·구현/대기·검증·보고를 포함한180분, 환경20분·정상/timeout 핵심 경로90분·새 탐색150분을 중간 한도로 둔다. 근거 있는 국소 재시도는 시간 내 허용하고 후보/버전 교체·호스트 권한 확대·새 유료 비용은 제외한다. 이전 회차와 비용을 분리·누적 기록하며 과거90분/4시간 잔여 예산은 재개하지 않는다. 정상·timeout·래퍼 사망의 핵심 사례는 새 단위로 각2회, 나머지 부정 경계는 유한 fixture로 검증한다.

**판정 한계:** fixture-boundary-passed는 선택 환경/fixture의 확인이며 아직 구현된 상태가 아니다. 독립 리뷰 전 R11 unresolved·R12 기존 범위·production/live 거부·trialAuthorized/readyForTrial=false·results=null을 유지한다. Vendure 준비·CLI helper 경고/실제 도구 연결·인증/provider·평가 재현·본 비교는 이번에 진행하지 않는다. 실제 모델/provider/본 비교0회다.


## ADR-036 · Fixture cgroup 종료와 service 성공에 연결한 결과 공개 — 2026-11-11

ADR-035의 한 후보/원래3시간 범위에서 [실제 fixture 결과](reviews/2026-11-11-s2-lifecycle-fixture.md)를 얻었다. worker는 비특권 container, 감독자는 별도 systemd service, 종료 authority는 manager 소유 persistent parent slice다. parent cgroup.kill/populated=0·runtime task/pending 요청·실제 PID/namespace를 결합하고 no-follow 일반 파일 전체 수집과 원자 rename을 사용한다. worker가 제공한 경로나 manifest는 권한이 아니다.

실제 supervisor SIGKILL에서 남은 exec client가 cleanup을 지연시켜 늦은 쓰기를 허용했으므로 service KillSignal=SIGKILL을 채택했다. systemd 성공 결과 전 수동 cleanup은 admission을 열지 않는다. 공개 직후 supervisor 사망은 결과를 격리하고 blocked/next 거부로 남긴다. 최종 self-review에서 발견한 이 경로는 같은 후보를 재준비하여 실제 SIGKILL과25개 전체 fixture로 확인했고 추가 준비249.555초도 원래 회차에 합산했다. 불명확한 runtime 요청·cleanup 실패를 빈 cgroup이나 안정된 hash만으로 복구하지 않는다.

결과는 fixtureOnly=true, validSubmission=false이며 정상 exit0/확인된 종료만 정상 fixture다. timeout/wrapper loss/nonzero는 진단, 감독/관리/수집 실패는 차단이다. 최종25개 통과는 독립 리뷰 대상이고 R11 unresolved·R12 기존 판정·production/live 거부를 유지한다. 실제 CLI/provider, Linux Vendure 평가와 본 비교의 범위/비용은 이후 리뷰에서 별도로 정한다.

## ADR-037 · Linux Vendure의 알려진 제출 평가 재현과 출력 수집 — 2026-11-11

**사용자 결정:** lifecycle fixture 독립 검토 이후 같은 경계에서 Linux Vendure baseline/reference 평가를 재현하는 구조와 새3시간 상한을 승인했다. [개발 지시](reviews/2026-11-11-s2-linux-evaluation-instructions.md)에 따라 알려진 제출/평가의 환경 재현을 먼저 확인한다. 실제 CLI·인증/provider 연결과 본 비교는 결과 리뷰 뒤 별도로 진행한다.

**구조 선택:** Linux에서 고정 lockfile/scope로 의존성/common을 준비하고 기존 Program 입력 검증을 먼저 통과시킨다. 환경·완전 소스·도구는 관리자 소유 RO 입력이고, 실행마다 새 container의 고정 Node entrypoint를 PID1로 사용한다. 기존 독립 감독자·persistent cgroup·pending/runtime 종료·service 성공 확인을 재사용한 뒤 출력만 수집한다. Vendure 전체 source는 약76.7MB여서 작은 fixture 수집 한도를 확대하는 대신 이미 알려진 입력으로 다룬다. collector128파일/16MiB와 비생산 결과 경계를 유지하며 임의 agent 제출 수집기나 범용 runner를 구현하지 않는다.

**검증/비용:** baseline/reference complete-root 각2회, 기존 타입/동작 부정2종, reference explicit delta1회의7단위와 공개 타입 검사·짧은 timeout 통합·영향 범위 회귀를 확인한다. macOS/새 Linux 반복/입력 방식의 의미·소스 identity 차이를 각각 대조한다. 시간/run ID/명시적 root 외의 차이를 숨기거나 Program hash를 자동 재고정하지 않는다. 환경45분·핵심90분·탐색150분·총180분, 새 유료 비용0이며 이전 예산은 재개하지 않는다. 평가 단위180초·종료10초·수집10초·외부240초를 상한으로 둔다.

**판정 한계:** linux-evaluation-reproduced/inconclusive/blocked로 인계한다. baseline의 예상 overall failed와 인프라 실패를 구분한다. 성공도 R11 전체 해결/실제 agent 독립성 전체·H-O/H-F·본 비교 준비 완료를 뜻하지 않는다. R12 기존 검증 범위·production/live 거부·trialAuthorized/readyForTrial=false·results=null·실제 모델/provider/본 비교0회를 유지한다. 이 결정은 다음 작업 승인이고 Linux 재현이 이미 구현됐다는 기록이 아니다.

## ADR-038 · Linux 교정 job과 정확한 경로 대응 — 2026-11-11

ADR-037의 같은 후보/새3시간 안에서 [Linux 알려진 제출 재현](reviews/2026-11-11-s2-linux-evaluation.md)을 확인했다. 관리자 불변 환경·완전 소스·도구의 RO bind와 실행별 새 Node PID1/출력만 수집하는 작은 job 분기를 채택했다. 최초 create 직전180초·lease5초·service210초·외부240초를 기존 작은 fixture 설정과 구분한다. 기존 종료/수집/성공 cleanup 권한을 재사용하고 runtime exit·평가기 판정·기대 교정값을 각각 기록한다. Production/live 경로는 열지 않는다.

첫 원문 대조에서 common 선언9개의 경로 표기가 달랐다. macOS의 `/tmp`→`/private/tmp` 해석을 거친 외부 경로는 기존 evaluator에서 `<typescript>/<basename>`으로 표기되고 Linux는 `packages/common/lib/…`를 기록한다. 역사적 Program 감사 자료, 원본 cache의 canonical path, 양쪽 실제9개 hash가 일대일로 일치했다. 의미·입력 hash 변경이 아니므로 원래 evaluator를 수정하지 않고 **정확한9개 경로/해시와 두 필드 위치의 대응**을 새 검증 전에 고정했다. 중복·충돌·해시 차이는 거부하고 파일 집합의 정렬만 대응 후 다시 한다. 광범위한 문자열 치환이나 해시 제외는 하지 않는다. 최초2개와 환경 전용 지문을 쓰던 중간1개를 최종7개 분모와 분리하고 원문 실패를 보존한다.

필수7단위·공개 타입4회·같은 entrypoint의 timeout/유한 대조2개·공유 lifecycle5회귀가 통과했고17개 등록 단위/소유 VM/cache를 정리했다. 이 교정은 R11 전체 해결, 실제 agent 실행 독립성 전체, H-O/H-F 또는 본 비교 준비 완료의 근거가 아니다. 기존 R12 범위와 readyForTrial/trialAuthorized=false·results=null을 유지하며 다음 CLI/인증/provider/usage·C 사람 의미 검토는 결과 리뷰 뒤 정한다.

## ADR-039 · CLI 비모델 연결 타당성과 가짜 인증 경계 — 2026-11-11

**사용자 결정:** Linux 평가 독립 검토 후 같은 container 안에서 CLI 본체와 도구 실행의 권한을 분리하는 구조·가짜 인증/내부 서버 검증과 새90분 상한을 승인했다. [개발 지시](reviews/2026-11-11-s2-cli-feasibility-instructions.md)에 따라 최소 구현·비모델 probe·증거/보고까지만 진행한다. 실제 자격 증명 전달과 모델 호출은 결과 리뷰 뒤 결정한다.

**구조 선택:** 외부는 기존 일회성 container/cgroup, 내부는 고정 CLI의 native 명령 sandbox를 사용한다. 실행별 CODEX_HOME/설정/상태와 셸 HOME/source/scratch를 분리하고, parent에서 읽을 수 있는 가짜 인증 표식의 직접/환경/FD 접근을 셸에서 거부한다. 실제 credential/호스트 home/키체인을 제공하지 않는다. 외부 egress 없이 내부 서버에 parent 문맥의 양성 대조와 CLI sandbox의 네트워크 거부를 확인한다. 실제 provider transport·turn의 tool inventory는 이 대조로 증명되지 않는다. 기존 감독/전체 종료/수집/cleanup을 재사용하며 production/live 권한은 열지 않는다.

**검증과 비용:** 동일 후보·CLI0.167.0-alpha.3.2를 유지하고 정상 새2단위·설정/파일/가짜 인증/내부 네트워크·timeout/유한 대조와 영향 범위 회귀를 확인한다. 최초 시계부터 환경20분/핵심45분/탐색70분/총90분, 신규 유료 비용0이다. privileged/광범위한 권한 확대·후보 교체·큰 proxy/broker/API runner가 필요하거나 경계가 성립하지 않으면 중단하고 인계한다. 작은 fixture만 사용하며 Vendure 설치/평가 전체 반복과 임의 수정 소스 수집기를 확대하지 않는다.

**판정 한계:** ready-for-live-connection-review/inconclusive/blocked로 인계한다. 첫 판정도 다음 연결 시험 설계의 근거일 뿐 실제 credential·로그인/갱신/provider/model 호출·본 비교 승인이 아니다. R11 unresolved·R12 기존 범위·trialAuthorized/readyForTrial=false·results=null을 유지한다. 이 결정은 다음 구현 승인이고 이미 CLI 내부 경계가 확인됐다는 기록이 아니다.
