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

## ADR-040 · CLI native namespace 차단에서 탐색 중단 — 2026-11-11

ADR-039의 [비모델 검증](reviews/2026-11-11-s2-cli-feasibility.md)은 **blocked**다. 같은 pinned CLI/후보·비특권 보안 설정에서 parent source 작업은 성공하지만 명시적 권한 profile의 native sandbox는 namespace 생성 전에 실패했다. 실제 OCI seccomp의 unshare/clone 제한과 보조 unshare EPERM을 확인했으며 AppArmor의 독립 기여는 분리하지 않았다. 현재 문서와 고정 CLI 명령 형식 차이를 수정한 국소 확인도 같은 실패다.

환경 단계에서 후속 경계 구현/실행을 중단했다. sandbox를 끄거나 권한/정책을 완화하지 않았고 API·proxy·새 후보를 추가하지 않았다. 준비2컨테이너/CLI10회를 정상2단위나 lifecycle 종료·수집 검증으로 계산하지 않는다. 초기 helper까지 실행 전 snapshot을 남기고 실제 실패·unsupported 옵션·미검증 항목과 비용/정리를 보존했다. 공유 lifecycle/evaluator/제품 계약은 그대로다.

다음은 독립 리뷰와 재개 조건 선택이다. namespace 정책의 최소 변경조차 별도 위협 검토·승인·예산을 정해야 하며 이 ADR이 변경을 승인하지 않는다. 후속 정책에서는 파일/가짜 인증/proc/FD/네트워크와 lifecycle 영향 회귀를 다시 확인해야 한다. 실제 credential 전달·로그인/갱신/provider/model·본 비교는 각각0이며 결과 리뷰 전 시작하지 않는다. R11 unresolved·R12 기존 범위·production/live 거부·trialAuthorized/readyForTrial=false·results=null을 유지한다.


## ADR-041 · 정책을 적용하지 않는 namespace 원인 진단 — 2026-11-11

**사용자 결정:** CLI blocked 결과 독립 검토 후 동일 후보에서 최소 정책 변경의 타당성을 새60분 한도로 진단한다. [개발 지시](reviews/2026-11-11-s2-namespace-diagnosis-instructions.md)에 따라 원인 확인·변경안 제시까지만 진행하고 실제 정책 변경·credential 전달·provider/model·본 비교는 결과 리뷰 뒤 결정한다.

**범위:** 기존 OCI/원시 증거와 고정 버전 구현을 먼저 대조하고 필요할 때만 같은 제한 아래 유한 비모델 관찰을 추가한다. 추적을 위한 권한 확대도 하지 않는다. 특정 syscall의 정책상 거부와 bwrap 최초 실패의 직접 관찰을 구분하고 seccomp·AppArmor 등 독립 계층의 미확인을 남긴다. 정책 후보는 문서/실행 경로 밖의 비활성 diff이며 적용 단위·권한 영향·남는 차단·후속 검증/복구·예상 비용을 포함한다. 제안의 최소성/충분성이 입증되지 않았다면 명시한다.

**상한:** 최초 시계부터 읽기/준비/대기/진단/검사/정리/보고60분, 계획10분·동적 환경25분·원인/후보40분·새 탐색 종료50분·총60분이다. 필요할 때만 소유 VM1개/준비 container 최대2개, 근거 있는 기계적 국소 수정 총2회, 신규 유료 비용0이다. 각 동적 payload15초/외부120초다. 후보/CLI 교체·정책 완화·새 실행 플랫폼은 제외하며 필요 시 미확인/차단으로 인계한다.

**판정 한계:** proposal-ready는 후속 정책 시험을 검토할 자료가 준비됐다는 뜻이다. inconclusive/blocked도 근거·정리·인계가 충족되면 유효한 회차 결과다. 성공 실행을 강제하지 않는다. R11 unresolved·R12 기존 범위·production/live 거부·trialAuthorized/readyForTrial=false·results=null을 유지한다. 이번 결정은 진단 승인이고 실행 완료나 정책 적용 승인이 아니다.

## ADR-042 · 관찰된 첫 namespace clone에 한정한 비활성 후보 — 2026-11-11

ADR-041의 [진단](reviews/2026-11-11-s2-namespace-diagnosis.md)은 proposal-ready로 인계한다. 같은 보안 정책의 untraced 기준/strace 진단2단위를 비교했고 첫 namespace clone flags `0x78020011`이 실제 seccomp의 namespace mask0 허용 조건에 맞지 않음을 확인했다. tagged bwrap raw_clone 구현과 관찰을 연결했으나 AppArmor의 독립 기여와 후속 mount/syscall 경계는 미확인이다. 원래 이미지에 추적 도구 레이어만 추가했고 정책·공유 lifecycle·제품/평가 입력은 변경하지 않았다.

[후보](reviews/2026-11-11-s2-namespace-policy-proposal.md)는 그 정확한 clone 조합만 추가 허용하는 **비활성 문서**다. 모든 자식과 ARM compat에도 미치는 영향, 남은 seccomp/mount/LSM 제약, 승인 후 시험·음성 대조·전체 경계 회귀·복구·추정 비용을 명시했다. 충분성이나 전체 최소 집합을 입증하지 않았고 실제 적용 승인도 아니다. 먼저 제한된 첫 차단점 시험의 가치를 독립 리뷰에서 결정하며 전체 runner 구현으로 바로 확대하지 않는다.

준비2단위·비모델 CLI4회, 로그 조회 옵션 국소 수정1회/runtime 재시도0이다. 전체 config 미열람이라는 직전 문구는 새 보고서에서 전체 TOML 파싱/허용값만 기록으로 정정했다. 과거 보고/증거는 보존하고 이번 호스트 인증 조사는0회다. 소유 자원 정리·pnpm check304·증거5테스트를 확인했다. 새 정책·credential 전달·로그인/갱신/provider/model/본 비교 각각0, R11 unresolved·R12 기존 범위·production/live 거부·trialAuthorized/readyForTrial=false·results=null을 유지한다.


## ADR-043 · 관찰한 clone 조합 한 행의45분 대조 시험 — 2026-11-12

**사용자 결정:** namespace 진단 독립 리뷰 후 [단일 정책 시험 지시](reviews/2026-11-12-s2-single-policy-test-instructions.md)에 따라 동일 후보에 clone arg0=2013397009의 SCMP_CMP_EQ/ALLOW 한 행만 추가하는 시험을 승인했다. 추가 권한 확대·자격 증명 전달·provider/model·본 비교는 결과 리뷰 뒤 별도로 결정한다.

**구조:** 원래 기본 정책과 일회성 container 전용 복제 profile을 같은 image/trace/합성 명령에서 각1회 비교한다. 후보 start 전 실제 OCI에서 추가 행 외의 seccomp/default/architecture·AppArmor/capability/NNP·자원·mount 권한 보존을 확인한다. clone 성공은 직접 반환값/자식 관계로 확인하며 다음 syscall/LSM 차단에서 정책을 더 넓히지 않는다. 성공해도 전체 내부 경계의 검증이 아니며 새 자손의 종료/정리 확인 없이 결과를 수집하지 않는다.

**감사 보완:** 이전11개 감사와 최종12개 snapshot의 차이를 과거 원시 증거 변경 없이 새 메타데이터로 설명한다. 감사 대상 ID/hash 목록을 고정해 결과를 재현하고 이후 종료/포장 기록도 최종 전체 index로 검증한다. 미분류 추가 자료를 묵인하거나 모든 후속 자료를 감사했다고 표현하지 않는다.

**상한과 한계:** 최초 시계부터 읽기·준비·구현·실패·검증·정리·보고45분, 계획10분/환경·대조20분/후보 관찰30분/새 탐색 종료35분/마감45분이다. VM1개·container 최대2개·후보 시작1회, 실행 전 근거 있는 기계적 수정1회, 신규 유료 비용0, payload15초/단위 외부120초다. 정책/기준 차이·종료 확인 불가·추가 권한 필요 시 실행하지 않거나 중단한다. 근거 있는 부정/미확인 결과도 유효하며 R11 unresolved·R12 기존 범위·production/live 거부·trialAuthorized/readyForTrial=false·results=null을 유지한다. 이번 기록은 시험 승인이고 실제 적용 완료가 아니다.


## ADR-044 · 단일 정책 회차의 부팅 전 중단과 고정 감사 범위 — 2026-11-12

[회차 보고](reviews/2026-11-12-s2-single-policy-test.md)의 관찰은 **inconclusive**다. 유일한 Lima 시작이 Ubuntu 이미지 다운로드 중450초 명령 상한으로 종료됐다. 이 이전 helper 상한은 승인된 환경20분보다 짧았고 환경 전체의 실패 증거가 아니다. 재시도/다른 후보 없이 정리·인계했다. VM 부팅/container/원래 정책/후보 적용/실제 CLI 및 model 각각0회이며 정책의 충분성이나 새 차단점을 판단하지 않는다.

분석 snapshot ID·manifest/archive hash를 실행 전에 고정하고 뒤의 close/포장 증거는 별도 분류한다. 과거11+1을 원본 변경 없이 재현했고 최종 index는 전체 파일/archive 내부를 검사한다. 새 회귀13개와 pnpm check304, 기존 trial/verification1,682파일 불변을 확인했다. 정확한 정책 한 행 검증은 과거 OCI fixture의 오프라인 검사이며 적용 성공이 아니다. 미실행 실행기 초안은 최종 도구에서 제외하고 snapshot에만 보존했다.

소유 stopped 등록·전용 root·불완전 다운로드 cache를 제거했다. 새 준비의 명령/환경 시간 상한과 예산은 결과 리뷰 뒤 정하며 자동 재개하지 않는다. 추가 권한·credential/provider/model·본 비교는 확대하지 않는다. R11 unresolved·R12 기존 범위·production/live 거부·trialAuthorized/readyForTrial=false·results=null이다.


## ADR-045 · 감사 분류·환경 deadline 보완 뒤 단일 정책 재개 — 2026-11-12

**사용자 결정:** 독립 리뷰에서 확인한 미분류 snapshot 자동 편입과 준비 시간 제한을 보완한 뒤 동일한 clone allow 한 행 시험을 재개한다. [개발 지시](reviews/2026-11-12-s2-policy-retry-instructions.md)는 기존45분 상한을 새 회차 전체에 유지한다. 추가 권한 확대·자격 증명 전달·provider/model·본 비교는 결과 리뷰 뒤 결정한다.

**수정 계약:** closing은 실행 시 정확한 허용 명령/단계와 snapshot ID/hash를 등록하고 package가 분석+closing 집합 밖 항목을 거부한다. 과거 audit/index는 보존하고 실제 package 부정 테스트를 추가한다. wrapper·다운로드·Lima의 제한은 최초 환경20분 절대 마감에서 잔여를 전달하며, 각 단계가 새 예산을 시작하거나 과거450초를 숨은 제한으로 유지하지 않는다. 두 보완을 검증한 뒤 동일 이미지/trace의 원래1회·후보1회를 수행하고 실제 OCI 한 행 차이 및 전체 소유 자원 종료/정리를 확인한다.

**비용/중단:** 최초부터45분(국소 보완/계획10·환경/대조20·후보 관찰30·새 탐색 종료35·최종45), VM1개/container 최대2개·후보 시작1회·유료0을 유지한다. 실패 후보 재시작과 두 번째 정책 변경은 하지 않는다. 보완 테스트/준비/종료 계약을 마련하지 못하면 근거 있는 부분 인계로 종료한다. 같은 후보의 추가 미세 조정은 자동 반복하지 않고 다음 결과에서 구조/운영 투자 여부를 사용자와 결정한다.

**한계:** 이번 결정은 보완·시험 재개 승인이고 성공 결과가 아니다. 영구 cache/VM·새 실행 경계·API/proxy 구축은 별도 논의다. R11 unresolved·R12 기존 범위·production/live 거부·trialAuthorized/readyForTrial=false·results=null을 유지한다.


## ADR-046 · 보완 검증과 후보 시작 전 차단·삭제 지연 인계 — 2026-11-12

[재시도](reviews/2026-11-12-s2-policy-retry.md)의 두 보완은 검증했다. closing은 허용 command/args/phase의 생성 시 등록만 인정하고 실제 package가 미분류/위조/중복/누락/변조를 거부한다. 검증 후 staging/한 번 공개로 실패 출력이 남지 않는다. 준비는 동일 UTC/host monotonic20분 절대 마감에서 잔여를 전달해 과거450초를 넘어538.536초에 끝났다.

원래 정책1회에서 parent 양성 동작과 namespace clone EPERM을 재현했다. 후보 created Spec의 seccomp는 승인된 한 행만 다르지만, 감독자 hook의 MEMORY_PRESSURE_WATCH 경로가 미리 허용한 identity 치환에 없어서 시작 전 거부했다. 그 항목을 사후 허용하거나 재시도하지 않았다. 후보 Spec 할당1/시작·커널 적용0이며 효과는 inconclusive다. 독립 cleanup의 종료 확인0.275초와 container 삭제181.412초를 구분한다. 삭제는120초 외부 계약 위반이므로 시험 상태를 blocked로 유지한다.

소유 자원은 모두 제거했다. pnpm check304·새31+기존13 Python회귀, 실제 과거11+1/6+6와 새 고정 분석/closing 감사, 기존 S2 입력2,385파일 불변을 확인했다. 실제 모델/provider/본 비교0, 공유 lifecycle·제품·평가기·모델/B/C 불변이다. 다음은 부분 결과/추가 투자 가치 리뷰이며 같은 후보의 미세 조정은 자동 반복하지 않는다. 새로운 실행 경계·영구 cache/VM·추가 권한·실자격 증명/모델 연결로 확대하지 않는다. R11 unresolved·R12 기존 범위·production/live 거부·trialAuthorized/readyForTrial=false·results=null을 유지한다.

## ADR-047 · 준비물 재사용과 공통 실행 운영 보완 승인 — 2026-11-14

**사용자 결정:** [개발 지시](reviews/2026-11-14-s2-execution-lifecycle-instructions.md)에 따라 검증된 준비물 재사용, 실패 경로를 포함한 공통 실행 수명주기, 정책과 실행 식별자의 비교 기준을 새3시간 안에 구현·검증한다. 실제 자격 증명 전달·로그인/갱신·provider/model·본 비교는 결과 리뷰 뒤 결정한다.

**근거와 구조:** 직전 후보는 커널 적용 전 동적 감독자 경로 차이로 거부됐고 실패 container 삭제가120초를 넘었다. 현재 경계의 불가능성을 입증한 결과가 아니므로 같은 Lima/VZ·containerd/nerdctl을 유지한다. 공개 불변 준비물만 hash/입력 검증 후 보관하고 회차 VM·실행 상태는 새로 만든다. 정지/삭제의 책임을 독립 공통 종료 경로에 두고 outcome·종료·삭제·수집을 분리한다. 전체 Spec은 사전 지정한 위치에서 검증된 소유 identity만 치환하며 후보 정책 차이는 기존 clone allow 한 행으로 제한한다. 기존 감사/시간 제한/collector를 재사용하고 공유 lifecycle의 영향 회귀를 수행한다.

**상한과 순서:** 60분까지 로컬 구현/회귀,100분까지 준비,150분까지 실제 관찰,180분까지 검증·정리·보고다. 환경 준비 진입 시 한 번만 `min(진입+20분, 회차+100분)`을 고정한다. VM1개·준비물10GiB·fixture 최대8+원래/후보2·단위120초(80/30/10 배분)·유료0이다. 필수7단위와 로컬 실패 차단 회귀 후에만 정책 대조하며, 선택적인 실제 정리 실패 주입은 모든 다른 관찰 뒤 마지막에 둔다. 실패한 실제 단위의 자동 재시도/시간 초기화는 하지 않는다.

**판정과 제외:** 구현 완료와 근거 있는 중단/회차 종료를 구분하고 정책 성공을 강제하지 않는다. 새 권한 차단에서 중단하며 준비물 보관을 상시 VM/세션 상태 재사용으로 확대하지 않는다. 제품/모델/B/C/평가 의미·배포 ID는 유지한다. R11 unresolved·R12 기존 범위·production/live 거부·trialAuthorized/readyForTrial=false·results=null이다. 이 ADR은 다음 작업 승인이고 구현 완료나 후속 연결 승인이 아니다.



## ADR-048 · 준비물 보관·공통 종료의 부분 구현과 보안 설정 차이 차단 — 2026-11-14

사용자가 지정한 [ADR-047 승인 지시](https://github.com/hyeonhb/ontosary/blob/191211d21942137932d189e4229ddfb5d330fece/docs/reviews/2026-11-14-s2-execution-lifecycle-instructions.md)는 별도 docs 브랜치에 있다. main f621521에서 [새3시간 회차](reviews/2026-11-14-s2-execution-lifecycle.md)를 수행했고 그 worktree/과거 증거는 수정하지 않았다.

공개 불변 archive의 전용10GiB 저장소와 실행별 독립 service/ExecStopPost·공통 삭제/수집, 소유 identity 검증 뒤 전체 Spec 비교를 실험 내부에 구현했다. 기존 cgroup/collector·snapshot/deadline/package를 재사용하며 과거 caller의 기본값과 회귀를 유지했다. 준비물4개의 실제 hash·입력 manifest 및 두 번째 다운로드/빌드 생략과 image import identity를 확인했다. VM/writable 상태를 보관하지 않는다. 이전 round 전용5개 retry entrypoint는 새 실행을 거부한다.

최소 환경은 nerdctl의 중복 PATH/systemd 환경 문제를 피했지만 첫 정상 단위의 created Spec에 AppArmor가 없고3개 mount가 rro에서 ro로 바뀌었다. 보안 차이를 identity 예외로 정규화하지 않고 시작을 거부했다. 생성1/start0, 삭제0.854초/단위 봉인1.236초와 결과/다음 실행 차단을 확인했다. 필수7개 중 기대 결과 통과0이므로 **구현 완료로 판정하지 않는다**. 나머지6개·원래/후보 정책·실행 바이너리 identity는 미실행이며 같은 단위를 고쳐 재시도하지 않았다. 현재 outcome의 supervisor-death는 실제 SIGKILL 주입이 아니라 비교 예외에 따른 service 실패 분류라는 한계도 보존한다.

Python116·production/live 거부·예제 build는 통과했다. pnpm check는 시작 때와 같은 기존 Vendure cache13파일 누락으로300통과/4실패이며 테스트 skip이나 cache 임의 복구를 하지 않았다. 따라서 결과는 개발 인계/독립 리뷰 대상으로 게시하고 필수 검사 미완료 상태에서 병합하지 않는다. 소유 VM/전용 임시 경로는 제거하고 검증된 준비물1.59GiB만 의도적으로 보관한다. 분석 동결 뒤 host 정리의 stdout/stderr 판독만 보완했으며 새 runtime 작업은 없다.

다음은 최소 runtime 환경의 기능 보존과 남은 실제 실패 경로를 검토하는 것이다. 추가 권한·다른 backend·영구VM·API/proxy·실자격 증명·provider/model·본 비교를 자동 시작하지 않는다. R11 unresolved·R12 기존 범위·production/live 거부·fixtureOnly=true/validSubmission=false·trialAuthorized/readyForTrial=false·results=null을 유지한다.

## ADR-049 · R13 R14 R15 보완과 기본 정책 검증 범위 — 2026-11-14

**요청과 범위:** 사용자는 독립 리뷰에서 발견한 R13~R15의 보완 지시를 요청했다. [후속 지시](reviews/2026-11-14-s2-execution-lifecycle-fix-instructions.md)는 기존 구조 안에서 빌드 전 입력 key 조회, 고정 runtime PATH와 알려진 hook 환경의 정확한 대조, 검증된 collector 산출물·허용 관리자 진단만 export하는 경로를 정한다. PR #54의 ADR-048/과거 원시 증거는 보존하며 구현 기준은 f6fc386이다.

**검증과 상한:** 직전과 같은3시간을 이번 보완의 상한으로 적용한다. 60분 로컬 회귀/100분 준비/150분 관찰/180분 정리·인계, 환경 진입 후20분 이내·VM1개·기본 정책 필수7단위·단위120초·보관10GiB·유료0이다. 준비 진입점에서 build 금지 cache hit와 collector 거부→export의 부정 회귀를 먼저 통과한다. 선택적8번째 실제 실패 주입과 원래/후보 정책 대조는 이번 범위에서 제외하고 결과 리뷰 뒤 결정한다.

**한계:** 이번은 지시 작성이며 보완 구현·실제 시험 완료가 아니다. 보완 구현 PR은 게시 후 독립 리뷰를 기다린다. R11 unresolved·R12 기존 범위·production/live 거부·trialAuthorized/readyForTrial=false·results=null을 유지한다. 추가 권한/backend·실제 credential/provider/model·본 비교는 진행하지 않는다.


## ADR-050 · R13–R15 부분 보완과 봉인·export 실패에서 중단 — 2026-11-15

[ADR-049 승인 회차](reviews/2026-11-14-s2-execution-lifecycle-fix-instructions.md)를 PR #54 위에서 수행했다. [결과](reviews/2026-11-15-s2-execution-lifecycle-fix.md)는 빌드 입력 key 선행 조회와 검증된 옛 출력 연결, 고정 runtime PATH/정확한 hook 배열, collector 결과·관리자 allowlist만 export하는 구현을 담는다. R14의 별도 회차 준비 진입점 회귀와 실제 build/download0·새 VM import identity는 확인했다. 과거 ADR-048의 같은 회차 재조회는 회차 간 build 생략의 근거가 아니었으며 이 보완에서 분리했다.

첫 정상 단위는 start1/exit0·삭제1.566초 뒤 service 비활성 시각을 확인하지 못해 결과가 철회됐다. 이어 export가 관리자 소유가 아닌 전달 image metadata를 거부해 guest 진단 archive도 남기지 못했다. 실제 raw Spec/도구 증거가 부족한 R13과 실제7단위 export가 미완료인 R15는 부분 완료로 남긴다. 필수7 중 시도1/기대통과0이며 실패 뒤 같은 단위 재시도/기대값 확대/실행 코드 수정은 하지 않았다.

pnpm check304·Python146(새30 포함)을 검증하고 소유 VM/임시 실행 경로를 제거했다. 공개 archive4개와 추가 입력-key 연결만 유지한다. 후속 service 증거 보존과 metadata 소유권/진단 export는 독립 리뷰 뒤 범위·예산을 결정한다. 이 결과는 다음 실행 승인이나 R11 해결이 아니며 production/live 거부·fixtureOnly=true·validSubmission=false·trialAuthorized/readyForTrial=false·results=null을 유지한다. PR #54는 갱신 후 독립 리뷰를 기다리고 이번에 병합하지 않는다.

## ADR-051 · 실패 진단과 service 봉인 및 최종 정리 보완 — 2026-11-17

**요청:** 사용자는 R15 잔여·R16·R17 보완 지시를 요청하고, 앞으로 추가 논의가 필요 없는 작업은 리뷰와 함께 개발 지시문을 제공하도록 했다. 주요 방향/아키텍처·범위/비용/권한 확대는 먼저 논의하며 별도 개발 실행/보류 시험의 포괄 승인은 아니다.

**구조:** [지시](reviews/2026-11-17-s2-seal-recovery-instructions.md)는 회수 예외와 VM 최종 정리를 분리하고, 전달 metadata를 검증한 뒤 관리자 소유로 게시한다. 정상 결과와 실패 진단은 상태를 구분하되 같은 누적 상한을 쓰며 거부 파일은 제외하고 허용 진단을 보존한다. 기존 독립 관리자가 service reference를 시작 전부터 봉인까지 유지하고, 원시 조회와 invocation/종료 시각을 연결한 뒤 해제한다. 검증된 도구 안에서 최소 표현을 선택하며 새로운 backend/상주 플랫폼/의존성을 도입하지 않는다. GC는 이전 실패의 확정 원인이 아니라 검증할 가설이다.

**상한과 인계:** 직전과 같은3시간·60/100/150/180분 gate·환경 진입20분·VM1개·기본 정책7단위·단위120초·cache10GiB·build0·유료0이다. 회수는 최대30초로 제한하고 회차 정리에90초를 남긴다. 실패 뒤 자동 재시도 없이 진단/정리/부분 인계하며 실제 정책 대조·권한 확대·인증/model·본 비교는 결과 리뷰 뒤 결정한다. PR #54 보완은 게시 후 독립 리뷰를 기다린다. PR #54의 ADR-050과 과거 증거는 보존한다. 이 기록은 지시이며 구현·실제 검증 완료가 아니다.


## ADR-052 · 진단 보존·service reference·독립 정리와 기본 정책 7단위 검증 — 2026-11-17

[ADR-051 지시](reviews/2026-11-17-s2-seal-recovery-instructions.md)에 따라 PR #54의 기존 실행 경계 안에서 보완했다. [결과](reviews/2026-11-17-s2-seal-recovery.md)는 metadata의 FD/hash/schema/UID 검증 후 관리자 원자 게시, 동일 누적 상한의 정상 결과/실패 진단/오류 receipt, 증거 회수와 최종 자원 정리 분리를 담는다. 회수 실패가 stop/delete를 건너뛰는 기존 결함을 먼저 재현하고 실제 Round.cleanup 회귀로 확인했다.

service 수명 보유자는 기존 독립 observer에 BindsTo로 연결한 active target이며 After 참조만 worker에 둔다. 시작 전에 획득하고 InvocationID·raw systemd 상태·finalizer/종료/삭제를 연결한 durable seal 또는 blocked receipt 뒤 해제한다. worker를 재시작하는 의존성을 추가하지 않았고 이전 실패의 GC를 확정 원인으로 단정하지 않는다.

새 VM1개·기본 정책 필수7단위가 기대 결과와120초 외부 상한을 통과했다. raw Spec7개와 service seal7개를 오프라인 재대조했고 준비/각 단위/최종 회수9개를 보존했다. 실제 UID501→root/mode0600 게시, cache build/download/save0·import1, VM/소유 process/관리 root 제거를 확인했다. pnpm check304·Python174(새28 포함)·과거 두 verifier·새 verifier가 통과했다. 공개 archive4개만 의도적으로 보관하며 과거 실패/증거는 수정하지 않았다.

R13/R14 유지와 R15/R16/R17은 이 fixture 검증 범위에서 결과 리뷰에 제출한다. 실제 observer 사망·transport 장애 주입은 새 VM 추가 없이 로컬 회귀로 검증한 범위다. 이번은 R11 전체 해결·CLI native sandbox·모델 효용 증명이나 본 비교 승인이 아니다. PR #54는 갱신 후 독립 리뷰를 기다리고 병합하지 않는다. R11 unresolved·R12 기존 범위·production/live 거부·fixtureOnly=true·validSubmission=false·trialAuthorized/readyForTrial=false·results=null을 유지한다.


## ADR-053 · 최상위 감사 실패와 소유 정리 호출 분리 — 2026-11-17

[국소 보완 지시](reviews/2026-11-17-s2-cleanup-dispatch-instructions.md)의 R17 잔여를 host main 안에서 해결했다. [결과](reviews/2026-11-17-s2-cleanup-dispatch-fix.md)는 감사 기록 try와 cleanup finally의 단일 호출, 최초/감사/정리/출력 오류의 보존, 제한된 실패 진단과 미등록 cleanup의 seal 거부를 담는다. 감사 등록 실패를 성공으로 봉합하지 않으며 기존 registry/orphan을 보존한다. 하위 recovery·guest·정책/cache·공유 감사/package는 변경하지 않는다.

기준 head에서 기록 오류6개가 cleanup을 건너뛰는 것을 재현했고, 실제 main 회귀19개와 기존 회귀를 합쳐 Python193·pnpm check304를 통과했다. 기존 cleanup 연결의 stop/delete/부재 확인은 가짜 외부 명령으로 확인했다. 과거3회차 저장 verifier와 실제7단위 증거를 오프라인 재대조했으며 새 VM/runtime은0회다. 독립 리뷰 뒤 다음 단계의 범위·예산을 결정하고 PR #54는 이번에 병합하지 않는다. R11 unresolved·R12 기존 범위·production/live 거부·fixtureOnly=true·validSubmission=false·trialAuthorized/readyForTrial=false·results=null을 유지한다.


2026-11-17 독립 검토 추가: [리뷰](reviews/2026-11-17-s2-cleanup-dispatch-independent-review.md)에서 실제 main의 감사 실패→cleanup 연결과 기존 증거를 재검증해 R17 해결로 판정했다. PR #54는7f2f179로 병합했다. 기존 구조를 유지하며 [동일 후보의 제한된 대조 재개](reviews/2026-11-17-s2-policy-pair-resume-instructions.md)를 다음 작업으로 권고한다. 이 추가 기록은 새 정책 실행 결과나 인증/model/본 비교 승인이 아니다.


## ADR-054 · 고정 clone 한 행 대조와 다음 mount 차단 관찰 — 2026-11-17

[R13~R17 완료 리뷰 뒤 승인한 제한 대조](reviews/2026-11-17-s2-policy-pair-resume-instructions.md)를 같은 Lima/VZ·고정 이미지·공통 unit에서 원래1/후보1만 수행했다. [결과](reviews/2026-11-17-s2-policy-pair.md)의 pair 진입점은 명시적 목적/분모/고정 RULE/cacheOnly와 과거7단위 hash를 확인한다. baseline 봉인·회수·기준 관찰 뒤에만 후보로 진행하고 pair 예외도 기존 감사/cleanup 경로를 거친다. guest/engine/reference/recovery/collector나 추가 권한 집합을 바꾸지 않았다.

원래 두 namespace clone은 EPERM, 후보 원문은 사전 검사41→42·명령 준비43→44의 clone 통과 후 두 자식의 mount(MS_SLAVE) EPERM이다. 실제 전체 Spec 차이는 승인된 clone arg0=2013397009 allow 한 행이다. 정확한 seccomp/AppArmor/kernel 기여는 분리하지 않았다. 자동 parser는 첫 clone 줄의 strace attach 안내와 다음 줄 반환값 연결을 지원하지 못해 inconclusive로 보존했다. 원문 검토의 first-clone-passed-next-blocked와 자동 결과를 구분하고 동결 코드 수정/실제 재시도는 하지 않았다.

두 단위 종료·service 봉인·reference 해제와 회수4개, VM/임시 root 정리를 확인했다. pnpm check304·Python208(기존193+새15)·과거3/새 verifier 통과다. 다음은 결과와 저장 trace 판독의 독립 리뷰이며 mount 허용/다른 후보/CLI 전체 경계의 범위·예산은 별도로 결정한다. 새 PR은 리뷰 전 병합하지 않는다. R11 unresolved·R12 기존 범위·production/live 거부·fixtureOnly=true·validSubmission=false·trialAuthorized/readyForTrial=false·results=null·실제 인증/model/본 비교 보류를 유지한다.


2026-11-17 독립 검토 추가: [리뷰](reviews/2026-11-17-s2-policy-pair-independent-review.md)에서 원문 clone 통과→mount EPERM과 전체 Spec/봉인/회수 근거를 확인해 PR #61을ee7ac98로 병합했다. 자동 inconclusive는 보존하며 저장 trace의 제한된 오프라인 판독만 후속 지시한다. 다음 실제 정책 시험은 외부/내부 경계의 책임과 권한을 사용자와 논의한 뒤 정한다. 이번 리뷰에서 새 runtime이나 권한 변경은 하지 않았다.


## ADR-055 · 일회성 VM 직접 CLI 실행의 90분 타당성 검증 — 2026-11-17

**합의:** 사용자는 외부 VM에서 CLI를 직접 실행하고 내부 sandbox를 유지하는 C안을 총90분 안에서 검증하도록 승인했다. [개발 지시](reviews/2026-11-17-s2-vm-cli-feasibility-instructions.md)는 이미 검증한 준비물·고정 CLI와 기존 Linux 평가기를 유지하면서 중첩 컨테이너의 호환성 비용을 줄일 수 있는지 확인한다. 이는 후보 타당성 검증이며 전체 전환의 확정이나 실행 결과가 아니다.

**보장과 책임:** 실행 간 상태 분리, 숨겨진 평가/제어 상태 보호, 모든 writer 종료 후 수집, 생성된 명령의 인증·통신 제한을 유지한다. 호스트 관리자는 VM/외부 마감, guest 감독자는 worker service/cgroup 종료/수집, CLI 내부 sandbox는 명령 접근 제한을 맡는다. worker는 관리 사용자와 분리하고 sudo·관리 소켓·추가 capability를 주지 않는다. 기존 컨테이너의 OCI/RO root/종료 검증을 직접 VM의 보장으로 전용하지 않는다.

**상한과 판단:** 순차 VM 최대2개, 실제 fixture 최대4개(정상·timeout·wrapper 사망·새 VM 정상 반복), 준비물 download/build/save0·실제 인증/provider/model0이다. 15/30/50/65/75/90분 gate로 준비·sandbox 시작·접근·종료·반복·정리/검증/보고를 제한한다. 권한 완화나 대규모 재구축, 예상 밖 접근, 종료 불명, 단계 시간 초과면 새 실행을 중단하고 진단/정리/보고로 전환한다. 다른 후보로 자동 전환하지 않는다.

**후속:** 실제4단위와 검증/정리가 확인되면 다음 통합 검토가 가능한 타당성으로만 판정한다. 실제 turn 도구 경계·인증 전달/갱신·Vendure 연결·전체 수집은 별도 남는다. 구현 PR은 독립 결과 리뷰 전에 병합하지 않는다. R11 unresolved·production/live 거부·trialAuthorized/readyForTrial=false·results=null·H-O/H-F 미검증을 유지한다.


## ADR-057 · 직접 VM CLI의 첫 호환성 관측을 위한 60분 축소 시험 — 2026-11-17

ADR-056은 미병합 PR #67의 중단 인계에 사용된 번호로 보존한다. 사용자는 [독립 리뷰](reviews/2026-11-17-s2-vm-cli-feasibility-independent-review.md)의 권고를 승인하고 [새 개발 지시](reviews/2026-11-17-s2-vm-cli-smoke-instructions.md)를 요청했다. 총60분·새 VM1개·실제 CLI sandbox 명령1회로 고정 도구의 직접 VM 실행 호환성을 먼저 확인한다. 직전90분 회차의15분 완료 gate와4단위 검증은 적용하지 않는다.

15분은 중간 점검,45분은 새 준비/실험 종료,60분은 정리/검증/보고 완료 상한이다. 최소 마감/소유 VM 폐기 수단과 비특권·외부 통신 차단은 유지하고, source 읽기/쓰기·materials 읽기의 실제 실행/종료 결과만 유한 진단으로 남긴다. 전체 실행기·새 봉인/제출 수집·인증/socket 부정 대조·VM2 반복은 후속으로 둔다. R19는 이번에 재사용하는 호스트 경로만 보완하고 미사용 초안의 결함을 해결했다고 표현하지 않는다.

고정 공개 cache/도구를 재사용하며 새 권한·패키지·후보·실제 인증/provider/model 호출을 도입하지 않는다. 실제 명령은 재시도하지 않고 관측 또는 차단 근거를 얻으면 정리한다. 새 PR을 독립 결과 리뷰 전에 병합하지 않으며 PR #67을 자동 병합/폐기하지 않는다. 이번은 지시 작성이고 runtime 관측은 없다. R11 unresolved·production/live 거부·본 비교/H-O/H-F 미검증을 유지하며 C안 채택과 후속 통합/예산은 결과 리뷰 뒤 정한다.


## ADR-058 · 직접 VM의 단일 native CLI EROFS 관측 — 2026-11-17

[ADR-057 축소 지시](reviews/2026-11-17-s2-vm-cli-smoke-instructions.md)를 새60분·VM1·실제 sandbox1 상한으로 수행했다. [결과](reviews/2026-11-17-s2-vm-cli-smoke.md)는 blocked-before-payload다. 전용 UID/GID22002·capability0/NNP·CPU2/4GiB/Tasks256와 별도 network namespace/loopback만 존재/외부 route 없음 확인 뒤 고정 CLI0.167.0-alpha.3.2가 bubblewrap 명령 구성 중 EROFS/exit1로 끝났다. Node22.19.0·실제 argv/hash/PID/service 연결은 확인했지만 payload 표식과 출력은 없다. 정확한 경로·syscall·LSM 원인을 추정해 확정하지 않고 실제 실패 뒤 수정/재시도/추가 trace를 하지 않았다.

기존 공개 cache·절대 마감·소유 stop/delete/부재 확인을 사용하고 OS transient worker service 외 새 봉인/제출 수집 프로토콜은 만들지 않았다. PR #67의 선택 추출 함수와 해당 합성 회귀만 출처를 기록해 가져왔다. 첫 준비의 정상 OCI `.` 디렉터리 과잉 거부는 VM 생성 전 로컬 보완으로 처리하고 원문/전후 patch를 보존했다. 동일 최초 시각을 유지했으며 실제 sandbox 재시도가 아니다. R19의 재사용 host API는 설치돼 있던 Python3.13.13을 고정해 실제 함수/명령으로 검사했다. 미사용 socket 결함을 포함한 R19 전체 해결은 주장하지 않는다.

실제 VM stop/delete/list exit0·소유 process/root와 watchdog 부재를 확인했다. service 추가 stop의 not-loaded/exit5와 초기 VM 미생성 준비의 stop exit1은 별도 원문으로 보존한다. 이번 VM 폐기는 모든 writer 종료→불변 제출 수집 보장의 대체가 아니다. pnpm check304·로컬 Python17·오프라인 부정4건을 확인했으며 공유 코드/제품/평가 의미·과거 증거는 불변이다. download/build/save·Vendure 재설치와 실제 모델 credential/login/refresh/provider/model/본 비교는0회다.

다음은 최초 차단의 독립 리뷰다. 필요한 쓰기 경로 진단과 권한/구조 변경은 구분하고 다음 범위·예산을 별도로 정한다. 새 PR은 독립 리뷰 전 미병합이며 PR #67도 자동 병합/폐기하지 않는다. R11 unresolved·R12 기존 범위·production/live 거부·fixtureOnly=true·validSubmission=false·trialAuthorized/readyForTrial=false·results=null·H-O/H-F 미검증을 유지한다.

## ADR-059 · 목적과 완료 기준 중심의 개발 지시 — 2026-11-18

ADR-058은 미병합 PR #70의 smoke 관측에 사용된 번호로 보존한다. 사용자는 반복된 실패에 지시의 과도한 방법 통제가 기여했을 가능성을 지적하고, 목표와 필요한 기준을 제시하되 개발 세션의 자율성을 높이도록 요청했다. 앞선 15분 준비 완료 gate는 실제 VM 관측 전에 작업을 중단시켰다. 실행 환경의 실제 결함과 별도로, 첫 관측 전에 요구한 구현 범위와 제약도 검토자의 책임으로 평가한다.

앞으로 지시하는 세션은 목적·범위·필수 제약·완료 기준을 정하고, 개발 세션은 구현·진단·검증 방법과 순서를 선택한다. 합의 범위 안의 국소 수정은 자율적으로 진행하며 중요한 방향·아키텍처·비용·권한 변경은 논의한다. 방법 제안은 참고임을 명시하고, 결과 리뷰는 목표 달성·근거·구현 품질을 기준으로 한다. 실패 시 개발 결과뿐 아니라 지시의 현실성도 함께 검토한다.

기간은 난이도·의존성과 개발 세션의 추정을 고려해 정하고, 중간 점검을 근거 없는 자동 중단 조건으로 만들지 않는다. 타당성 검증에서는 핵심 불확실성을 먼저 확인하되 실제 위험에 필요한 보호는 유지한다. [AGENTS.md](../AGENTS.md)에 운영 원칙을 반영하며 별도 필수 보고 양식은 추가하지 않는다. 과거 지시와 원시 증거는 보존한다. 기존 합의한 예산·실행 횟수·보안 경계나 보류된 시험의 승인 상태를 자동 변경하지 않는다.

## ADR-060 · 진단 저장 실패와 소유 정리 실행 분리 — 2026-11-18

[R20 결과 중심 지시](reviews/2026-11-18-s2-r20-outcome-instructions.md)에 따라 smoke 정리 경로만 보완했다. safety 명령은 기존 최대1MiB/stream 메모리와 명령별 마감 안에서 초과 출력을 버리며 실행하고, 이후 남은 진단 용량에 맞춰 저장한다. 일반 실험 명령의 출력 초과 중단은 유지한다. 로그 예산을 늘리거나 공유 runtime·guest 권한·평가 의미를 바꾸지 않고 정리와 관측의 결합을 끊는 선택이다.

소유권 확인과 기존 파일의 배타 잠금 뒤 stop/delete/list를 실행한다. 명령 상태·진단 상태·자원 부재를 각각 보고하며, 앞선 오류와 나중의 부재 확인을 함께 보존한다. 실패·timeout·잘린 조회나 파싱 불능은 unconfirmed이며, 진단 receipt/marker 저장 실패는 완료한 자원 정리를 되돌려 실패로 표현하지 않는다. 쓰기 실패 때 영구 기록을 보장하지는 않으며 호출자에게 receiptWritten=false와 오류를 반환한다.

[반례와 회귀](reviews/2026-11-18-s2-r20-cleanup.md)는 실제 로컬 대체 프로세스의 완료와 외부 상태 파일 제거로 확인했다. 당시 코드2008351과 과거 증거는 보존하고 별도 임시 Git snapshot으로 당시 verifier를 실행한다. 새 VM/실제 CLI/trace/model 호출 없이 PR #70만 갱신하며 독립 보완 리뷰 전 미병합이다. EROFS·R11·C안 전체 통합·H-O/H-F의 기존 판단은 변경하지 않는다.


2026-11-18 독립 검토 추가: [R20 리뷰](reviews/2026-11-18-s2-r20-cleanup-independent-review.md)에서 합의한 로컬 정리 계약의 보완을 확인하고 PR #70을ca576e4로 병합했다. Python32·pnpm check304·독립 복합 실패3개/무한 출력·과거 verifier/99파일 보존을 재검증했다. 추가 보완은 요구하지 않으며 후속 EROFS 진단의 범위·예산은 별도 합의한다. 새 실제 실행·권한 변경·본 비교 승인은 없다.


## ADR-061 · EROFS 경로를 좁히는 읽기 전용 진단 — 2026-11-18

사용자는 R20 완료 리뷰 후 EROFS의 정확한 쓰기 경로를 좁히는 개발 지시를 요청했다. [지시](reviews/2026-11-18-s2-erofs-diagnosis-instructions.md)는 당시 고정 바이너리와 대응 소스·저장 환경·정책을 연결해 쓰기 경로/연산 후보를 설명하는 조사다. 정적 근거와 실제 관측을 구분하고, 소스 대응이나 경로를 확정할 수 없으면 미확정 이유와 최소 후속 관측을 인계한다.

조사 방법은 개발 세션이 선택한다. 30~60분은 계획을 위한 참고 예상이며 사용자 합의된 시간 상한이 아니다. 착수 시 난이도와 예상 시간을 공유하고 의미 있는 범위·비용 확대는 논의한다. 새 VM·실제 CLI/trace·정책 변경·자격 증명/model 호출·본 비교는 수행하지 않으며 후속 실행은 결과 리뷰 뒤 결정한다. 이번 결정은 지시 작성으로 EROFS 해결이나 C안 채택의 근거가 아니다.


2026-11-18 ADR-061 독립 검토 추가: [리뷰](reviews/2026-11-18-s2-erofs-diagnosis-independent-review.md)에서 정적 진단 완료를 인정했다. 실제 실패 경로는 미확정이며 다음 관측/조건부 조치의 범위·예산은 별도로 합의한다. 사용자는 앞으로 결과 리뷰에 잘한 점과 관리자로서 개선할 부분도 포함하도록 요청했다. AGENTS에 반영하며, 과업 결과와 관리 세션의 지시·관측 설계·의사결정 비용을 함께 평가하되 개선 제안을 결함 수정 요구와 구분한다.


## ADR-062 · EROFS 관측과 가설 확인 시 최소 조치의 한 과업 인계 — 2026-11-18

사용자는 다음 제안의 개발 지시를 요청했다. [지시](reviews/2026-11-18-s2-erofs-observation-instructions.md)는 일회성 VM1개·기준 native 관측1회와 조건부 대조1회로 실패 path/errno와 최소 조치 효과를 확인한다. 예상 daemon 경로 생성의 EROFS가 확인된 경우에만 관리자가 해당 디렉터리를 사전 준비한다. 원래 worker/서비스 정책은 유지하고 추가 권한·전체 tmp 쓰기 허용·본 비교로 확대하지 않는다. 조사 도구와 구현 순서는 개발 세션이 선택하며 60~90분은 착수 시 조정할 참고 예상이다. 실제 시험은 이 작성에서 실행하지 않았고 변경/결과의 PR은 독립 리뷰 전 병합하지 않는다.

사용자는 앞선 리뷰 구분 요청이 가독성을 위한 것임을 명확히 했다. 잘한 점/개선점을 매번 만들거나 개선 제안을 매번 수정 과업으로 만들지 않는다. 실제 구현의 자료구조·오류 처리·성능과 프로젝트 방향을 검토하고 필요한 문제만 영향·우선순위에 따라 바로잡도록 AGENTS를 정정한다.

## ADR-063 · Vendure 고정 입력 패치 파일럿 우선 — 2026-11-18

사용자는 loopback 조사를 보류하고 [고정 입력 패치 파일럿 지시](reviews/2026-11-18-s2-fixed-input-pilot-instructions.md)에 따라 조건별 한 번의 독립 모델 실행과 기존 평가기를 통한 외부 채점을 진행하기로 했다. 공통 입력 위에 B는 구조화 지식, C는 대응 서술 자료를 제공한다. 빠르게 변경 정확성의 경향을 확인하는 범위로, 도구를 갖춘 본 비교와 별도 결과로 보관한다.

## ADR-064 · Vendure 복합 수정의 난이도 교정과 평가 분리 — 2026-11-19

첫 고정 입력 과업에서 세 조건의 첫 패치가 모두 만점이었다. 사용자는 기존 환경을 재사용해 복합 수정 후보를 고르고, 별도 예비 과업으로 난이도를 가늠한 뒤 평가 과업과 성공·비용 기준을 확정하기로 했다. A의 성공도 포함해 같은 실행 예산에서 변경과 보존을 모두 만족한 패치와 실제 추가 비용을 비교한다. 실제 평가 과업 실행은 준비 결과를 독립 리뷰한 뒤 결정한다. [개발 지시](reviews/2026-11-19-s2-complex-task-preparation-instructions.md)

2026-11-19 준비 결과에서 조건별 예정된 첫 제출 6건을 성공 비교의 분모로 고정하고, 실패를 포함한 모든 시도의 입력·출력 비용을 집계하기로 했다. 두 업무 가정과 최대 18회 비교 예산은 독립 리뷰 후 결정한다. [과업과 비교 계약](reviews/2026-11-19-s2-complex-task-preparation.md)

2026-11-20 사용자는 두 실험용 업무 정책과 v3 동결 예산으로 고정 입력 비교 18회를 승인했다. 과업·조건별 첫 제출과 실제 사용량을 개발 세션에서 수집하고 결과를 독립 리뷰한다. [실행 지시](reviews/2026-11-20-s2-complex-comparison-instructions.md)

2026-11-20 Astra의 A가 6/6을 기록한 뒤, 다음 실험은 같은 입력·평가기를 사용해 Sol의 A/B/C를 비교하기로 했다. 기존 배정과 예산을 준용하고 Sol 내부의 자료 효과와 과거 Astra+A에 대한 성공·비용 비교를 따로 보고한다. [Sol 실행 지시](reviews/2026-11-20-s2-sol-comparison-instructions.md)

## ADR-065 · 업무 요청에서 출발한 영향 범위 탐색 비교 — 2026-11-22

사용자는 기존 환경에서 측정 가능한 범위부터 확인하기로 했다. Vendure 환불 잔액 과업에서 A는 일반 코드·문서 검색, B는 모델 조회 추가, C는 대응 서술 자료 조회 추가로 구성한다. 수정 전 탐색 결과를 기록하고, 같은 조건에서 변경 소스를 수집할 수 있을 때 최종 수정도 평가한다. 이번에는 참가 모델을 호출하지 않는다. 별도 실행 환경 투자와 Sol 최대 9세션의 실제 실행·예산은 준비 결과를 본 뒤 결정한다. [개발 지시](reviews/2026-11-22-s2-refund-discovery-preparation-instructions.md)

2026-11-24 실제 복합 변경 후보는 참가 모델의 성적을 보기 전에 선정한다. 첫 후보 Vendure #4728은 변경 전 같은 구현의 B/C 자료와 부분 수정을 실제로 구별하는 대조가 모두 성립할 때 채택을 권고한다. [후보 선정 지시](reviews/2026-11-24-s2-modified-order-task-selection-instructions.md)

2026-11-24 #4728의 자료 부적합을 확인한 뒤, 동결된 Angular B/C가 설명하는 구현을 첫 필터로 삼기로 했다. 그 범위의 실제 변경에서 업무상 복합성과 독립 대조 가능성으로 후보를 고른다. 모델의 정답 포함 여부나 A의 예상 실패를 선호 기준으로 삼지 않는다. [개발 지시](reviews/2026-11-24-s2-angular-candidate-selection-instructions.md)

2026-11-22 준비 단계에서는 호스트가 조건별 텍스트 조회와 수정 전 1회 제출을 중계하고, 같은 소스 사본에서 메뉴 문구와 클릭 후 실제 모달 호출을 함께 판정할 수 있음을 확인했다. 발견 성공과 변경 성공의 분모는 각각 조건별 예정 3회로 제안한다. 실제 비용 집행은 독립 리뷰 뒤 결정한다. [모의 결과와 운영 상한](reviews/2026-11-22-s2-refund-discovery-preparation.md)

2026-11-26 변경 전 자료와 실제 두 취소 경로가 대응하고 세금 별도 주문의 회귀를 판별할 수 있어 Vendure #4348을 채택했다. 먼저 참가 호출 없이 서로 다른 정상 구현까지 같은 채점 경로에서 확인한다. 이후 A/B/C 각 한 세션의 예산은 준비 결과를 리뷰한 뒤 결정한다. [개발 지시](reviews/2026-11-26-s2-shipping-submission-grading-instructions.md)

2026-11-26 채점 준비 종료 후 다음 지시문은 조건별 1회, 총 3개 독립 세션으로 작성했다. 요청 모델과 세션당 운영값은 앞선 탐색 준비안을 준용하고, 수정 전 발견·최종 수정·실패 포함 비용을 각각 기록한다. [파일럿 지시와 예산](reviews/2026-11-26-s2-shipping-pilot-instructions.md)

## ADR-066 · 공개 코드에서 도메인 기록 한 건을 만들고 인계하는 첫 사용 검증 — 2026-11-26

기존 S2는 준비된 지식을 쓰는 효과를 관찰했다. 첫 공개에서 중요한 작성·인계 비용을 알아보기 위해 Vendure v3.5.0 부분 출고에서 시작한다. 기존 유지보수자 섭외가 어려워 해당 코드에 익숙하지 않은 작성자를 기준으로 준비한다. 공개 코드에서 확인한 동작, 업무 의미의 검토 상태, agent에게 전달된 지식, Ontosary의 기여를 구별한다. 다음 범위는 자료 준비와 독립 리뷰까지다. [준비 지시문](reviews/2026-11-26-first-use-partial-fulfillment-instructions.md)

2026-11-27 첫 실행은 사용자가 선택한 작성 agent 한 세션과 독립된 후속 agent 한 세션의 대리 인계로 진행한다. 두 세션 사이에는 첫 제출 기록만 전달한다. 사람의 첫 사용성·소요 시간·업무 승인은 미측정으로 둔다. [실행 지시](reviews/2026-11-27-first-use-partial-fulfillment-run-instructions.md)

## ADR-067 · 첫 공개의 약속을 실제 변경 과업 제출로 확인 — 2026-11-27

Vendure에서 agent 간 기록 재사용을 관찰했지만 Ontosary가 작성 비용을 줄였는지는 미측정이다. 비교 과업을 추가하기 전에, 처음 보는 TypeScript 개발자에게 검산된 기록의 견본을 보여 주고 자기 과업을 가져오는지 관찰한다. 수요, 작성 비용, 후속 사용의 이득은 별개로 판정하며 Vendure는 견본과 교정에 사용한다. [개발 지시](reviews/2026-11-27-domain-note-demand-instructions.md)

## ADR-068 · 작업 agent가 필요할 때 기록을 요청하는 비교 — 2026-11-27

강제로 전달된 기록이 재사용된 사실과 자발적으로 기록을 요청할 이유를 분리한다. 미리 선정한 과업에서 독립 A/B를 실행하고 B의 명시적 요청이 있을 때만 작성 agent를 투입한다. 관찰 단위는 선택, 변경 계획의 업무 판단, 작성 비용을 포함한 과업 총비용이다. 사람의 사용 의향은 별도 가설로 남긴다. [개발 지시](reviews/2026-11-27-optional-domain-note-pilot-instructions.md)

## ADR-069 · 분석 컴파일러를 정확한 버전으로 선택 — 2026-11-28

호환성 검증용 CLI는 기본 TypeScript 5.9.3과 명시적 4.9.4를 Ontosary 의존성으로 고정한다. 한 분석의 설정 해석, Program, 심볼·AST 추출, 조건 정규화는 같은 컴파일러를 사용한다. 명시적으로 요청하면 요청값과 실제 분석 버전을 기록한다. 4.9.4에서 숫자 enum 입력은 선언 밖의 정수도 허용하므로 유한 도메인 증명을 보류한다. 이번 지원 권고는 두 고정 버전에서 검증한 경로에 한정한다. [근거와 회귀 대조](reviews/2026-11-28-typescript-494-compatibility.md)

2026-11-28 독립 리뷰의 number 변수 반례를 확인해 숫자 enum 입력의 유한 열거를 5.9.3에서도 보류한다. 99를 리터럴로 직접 대입한 결과만으로 입력 도메인의 폐쇄성을 판단할 수 없다. [보완 검산](reviews/2026-11-28-typescript-494-soundness-fix.md)
