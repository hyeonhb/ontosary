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
