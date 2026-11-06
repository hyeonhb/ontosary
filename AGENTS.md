# Ontosary 개발 지침

먼저 [docs/PROGRESS.md](docs/PROGRESS.md)를 읽고 [ARCHITECTURE](docs/ARCHITECTURE.md),
[ROADMAP](docs/ROADMAP.md)에서 현재 구현과 다음 실험을 확인한다.

- 기존 코드베이스의 도메인 지식을 발견·이해·관리하는 개발자 도구다. 온톨로지 전환을 강요하지 않는다.
- Developer Value First, Codebase First, Ontology as a Means, Incremental Adoption,
  Evidence Based, Human Verified, Framework Agnostic Core, Empirical Validation을 유지한다.
- 코드 사실, 발견 후보, 승인된 지식을 분리한다. 구조적 타입 호환성은 업무 개념의 동일성이 아니다.
- 조건의 차이는 버그의 증명이 아니다. 동일 입력·도메인 등 전제와 근거·불확실성을 명시한다.
- 코어는 TypeScript Compiler API만 의존한다. CLI·React·Vite는 코어 밖에 둔다.
- 미지원 문법은 이유를 보고한다. 불확실한 분석을 성공으로 표현하지 않는다.
- 유한 비교와 FCA는 명시적 상한을 둔다. 핵심 알고리즘·부정 사례·심볼 충돌에 회귀 테스트를 둔다.
- 변경 전 기존 코드와 git 상태를 확인한다. 사용자 변경을 덮어쓰지 않는다.
- 완료 전 `pnpm check`와 필요시 `pnpm experiment`를 실행하고 PROGRESS를 실제 결과로 갱신한다.
- 중요한 결정은 DECISIONS, 우선순위 변경은 ROADMAP에 기록한다. 연구 가설은 RESEARCH에서 관리한다.
- 장기 기능을 이미 구현된 것처럼 기술하지 않는다. LLM·SMT·프레임워크 플러그인은 실험 근거가 생긴 뒤 검토한다.
- 이름은 Ontosary / ontosary로 통일한다. 의존성·라이선스를 확인하고 비밀·사적 데이터를 넣지 않는다.

- 브랜치·커밋은 [CONTRIBUTING.md](CONTRIBUTING.md)를 따른다: GitHub Flow, 짧은 작업 브랜치, Conventional Commits.
- 작업 전 원격/브랜치/사용자 변경을 확인하고, 커밋 전 staged diff를 검토한다. 의존 브랜치는 기준 브랜치를 기록한다.
- 로컬 커밋과 원격 게시·PR·merge 권한을 구분한다. 과거 리뷰 원시 증거는 보존하고 새 검증 결과는 날짜별로 추가한다.
