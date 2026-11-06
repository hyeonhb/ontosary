# 현재 작업 상태 — 새 세션은 이 문서부터 읽기

마지막 갱신: **2026-11-06, Asia/Seoul**.

## 현재 단계

첫 PoC 구성 요소는 구현됐으나 2026-11-04 독립 리뷰가 R1(enum receiver)·R2(explicit this)의 false proof를 확인했다. Gate 1은 미통과이며 [NEXT_PLAN](reviews/NEXT_PLAN.md)에 따른 정확성 수정이 corpus 실험보다 우선이다.

## 마지막으로 완료한 작업

비어 있던 폴더에 로컬 Git(main), private `ontosary` 패키지, pnpm lockfile, 코어/CLI/React 예제/테스트/맥락 문서를 구성했다. 기존 사용자 코드는 없었다. 2026-11-06 기존 GitHub 원격을 origin으로 연결하고, 원격 초기 커밋 위 chore/initial-poc에 현재 작업을 기록한다. GitHub Flow/Conventional Commits를 CONTRIBUTING에 명시하고 사용자 선택으로 Apache-2.0을 유지한다.

| 완료 조건 | 현재 상태 |
| --- | --- |
| 기본 구조와 Ontosary 명명 | 완료 |
| AGENTS + PRODUCT/ARCHITECTURE/RESEARCH/ROADMAP/DECISIONS/PROGRESS | 완료 |
| TS 타입·필드·함수·참조·조건·위치 JSON | 완료, 제한사항 명시 |
| Formal Context 및 NextClosure | 완료, 입력/출력 상한과 후보 필터 |
| 제한된 논리 IR | 완료, 미지원 이유 출력 |
| 유한 비교·함의·반례 | 완료, 동일 입력 명시 전제 |
| React+Vite 예제 | 완료, Vehicle/Listing/ConsultationRequest 및 두 UI |
| scan/concepts/compare CLI | 완료, JSON·종료 코드 |
| 알고리즘·부정 사례 자동 테스트 | 완료, 41개 |
| README·실험 결과·다음 단계 | 완료 |

## 실제 실행 명령

저장소 루트에서 실행한다.

```sh
pnpm install --frozen-lockfile
pnpm build
pnpm ontosary scan examples/react-vite --json
pnpm ontosary concepts examples/react-vite --json
pnpm ontosary compare examples/react-vite canConsultFromCard canConsultFromDetail --assume-same-input --json
pnpm check
pnpm experiment
pnpm example:dev
```

`compare`의 함수 이름이 중복되면 `scan`의 전체 ID를 사용한다. 입력 전제가 없으면 Unknown(종료 코드 2), 문법 미지원도 2, 잘못된 프로젝트/컴파일 오류/인수는 1이다.

## 검증 결과

환경: Node 22.19.0, pnpm 11.19.0, TypeScript 5.9.3, React 19.3.1, Vite 8.3.5, Vitest 5.1.0.

- `pnpm install --frozen-lockfile`: 성공.
- `pnpm check`: 코어+예제 타입 검사, 테스트 3개 파일/41개, Vite production build 통과.
- 마지막 타입 별칭 출력 보완 후 `pnpm test`: 41개 전부 재통과. 예제 코드는 이전 check 이후 바뀌지 않음.
- `pnpm build` 후 `./dist/cli/index.js --help`: 실행 권한을 포함한 직접 CLI 실행 확인.
- `pnpm experiment`: 4개 고정 비교 기대값 모두 일치. 타입 6, 함수 13, 지원 predicate 6, 미지원 7; FCA 객체 13/속성 26, 형식 개념 20, 후보 8, 포함 관계 8, 잘림 없음.
- 대표 결과: 카드 조건은 상세 조건을 함의하고 역은 불성립. `arg0.status = reserved` 반례. 같은 정책을 구현해야 한다는 추가 근거가 없으므로 버그로 판정하지 않음.
- FCA 구현: 512개 3×3 incidence matrix를 독립 완전탐색과 대조, 모든 폐포·extent 일치.
- 브라우저 수동 smoke check: available 두 버튼 활성, reserved 카드만 비활성, sold 둘 다 비활성. 상세 상담 클릭 시 요청 표시. 콘솔 warn/error 없음. 테스트용 서버는 확인 후 종료.
- 설치된 45개 패키지의 라이선스 메타데이터 확인. [DEPENDENCIES](DEPENDENCIES.md) 참조.

## 알려진 제약과 미해결 문제

기존 41개 테스트는 통과하지만 그 밖의 정상 TypeScript 입력에서 R1/R2가 재현됐다. 먼저 회귀 테스트와 정확성 수정을 수행해야 한다. R3(mixed JS 파일 집계)는 그 뒤 별도 작업이다. 다음은 그 외 제한이다.

- 유한 문자열/상수 enum, 직접 입력/한 단계 속성, 단일 반환식에 한정한다. 호출·복수 문장·변이·기본값·optional·객체 union·숫자 범위 등은 미지원이다.
- 런타임 타입 준수, 안정적인 plain data, 필드 독립성을 가정한다. `sameInput` 전제는 사용자가 확인하며 자동으로 보장하지 않는다.
- TS strictNullChecks가 필요하고 컴파일 오류가 있으면 proof를 거부한다. 근거 ID는 소스 이동·의존성 설치 레이아웃에 따라 바뀐다.
- top-level 조건, 클래스 필드 모델, 재귀 project references, 전이적 타입 그래프, React/Next 특화 의미는 미구현이다. 일부는 omissions, 범위 전반은 limitations에 기록한다.
- FCA는 큰 프로젝트에 상한 오류를 낼 수 있다. 공통 타입으로 너무 넓게 묶거나 표시 함수/판정 함수를 같은 그룹으로 묶을 수 있다.
- 승인 워크플로, LLM, SMT, MCP, 자동 코드 수정, 배포는 이번 범위 밖이다.
- 스냅샷은 인공 데이터다. 실무 도메인 정확성·검토 시간·유지 비용을 아직 측정하지 않았다.

## 다음에 할 구체적인 작업

1. [NEXT_PLAN](reviews/NEXT_PLAN.md)의 R1/R2를 실패 테스트로 고정한 뒤 최소 수정한다.
2. core/CLI 및 통제된 fixture의 실제 실행과 IR 평가를 대조한다.
3. 전체 check/experiment와 독립 리뷰 probe를 실행하고 새 날짜의 증거로 보존한다.
4. R3 파일 집계 계약 정리 후 실제 corpus/수동 라벨 실험을 진행한다.

## 코드·근거 안내

- `src/core/analyzer.ts`, `logic.ts`, `fca.ts`, `model.ts`: 현재 핵심 구현.
- `src/cli/index.ts`: CLI. `examples/react-vite/src`: 인공 실험 대상.
- `tests/analysis.test.ts`, `fca.test.ts`, `cli.test.ts`: 정확성/부정/CLI 검증.
- `experiments/cases.json`, `run.mjs`, `results/*.json`: 재사용 사례와 관찰 결과.
- [ARCHITECTURE](ARCHITECTURE.md): 정확한 지원 경계. [RESEARCH](RESEARCH.md): 관찰·가설·실패 사례.
- [DECISIONS](DECISIONS.md): 기술 선택 이유. [ROADMAP](ROADMAP.md): 현재 완료와 미래 계획의 구분.
