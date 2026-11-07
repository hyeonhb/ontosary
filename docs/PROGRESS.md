# 현재 작업 상태 — 새 세션은 이 문서부터 읽기

마지막 갱신: **2026-11-08, Asia/Seoul**.

## 현재 단계

최신 독립 판정: 원시 corpus 결과는 재현됐지만 평가기 R4/R5 보완이 필요하다. 사용자는 다음 제품 실험을 **업무 개념·관련 코드 탐색 우선**으로 선택했다. [corpus 독립 리뷰](reviews/2026-11-07-corpus-independent-review.md)와 [현재 개발 지시](reviews/2026-11-07-corpus-review-next-plan.md)가 최신 판단이며, 아래 관찰 자료는 과거 실행으로 보존한다.

2026-11-07 새 NEXT_PLAN의 **실제 corpus 관찰 자료 구축을 완료**했다. 공개 TS corpus 2개를 revision·라이선스·20개 파일 hash로 고정하고, 첫 scan 전에 코드 사실 라벨 24개를 작성했다. 라벨 22개 일치/2개 클래스 모델링 미지원, 함수 전체 predicate 지원 0건, 사전 날짜 비교 0/2 지원을 관찰했다. p-queue 전체 FCA는 속성 상한 초과이며 작은 범위 결과와 함께 보존했다. 사람의 업무 의미 승인·검토 시간·검색/LSP 대비 효과는 아직 미검증이다. [관찰 보고서](reviews/2026-11-07-corpus-observation.md)와 [검토표](../experiments/corpus/results/2026-11-07/review.md)는 구현 세션의 관찰 인계다.

첫 PoC의 구성 요소 구현 후, 독립 리뷰가 발견한 **R1/R2 false proof 차단을 완료**했다. 2026-11-07 독립 재검토에서 R1/R2/R3 해결을 확인했고 Gate 1을 제한된 지원·검증 범위에서 통과로 재평가했다. 모든 TS 문법에 대한 건전성이나 제품 유용성을 입증한 상태는 아니다. R3(mixed TS/JS 파일 집계 계약)도 수정·회귀 검증했다. NEXT_PLAN의 직접 수정·검증 지시와 명시된 후속 결함 R3까지 완료했으며, 이후 실제 corpus 관찰은 아래와 같이 수행했고 사용자 과업 비교는 후속 연구 단계다.

[R1/R2 개발 인계](reviews/2026-11-06-normalization-fix.md)와 [NEXT_PLAN 이행 점검·R3 인계](reviews/2026-11-06-next-plan-completion.md)에 전후 판정·검증·남은 위험을 정리했다. 과거 [리뷰](reviews/2026-11-04-poc-review.md)와 [NEXT_PLAN](reviews/NEXT_PLAN.md)은 당시 지시와 관찰로 보존했다. 이 문서가 최신 구현 상태다.

## 저장소와 개발 규칙

- `origin`: `https://github.com/hyeonhb/ontosary.git`.
- 원격 초기 LICENSE 커밋 `5d33ab6` 기반으로 `chore/initial-poc`에 기존 작업을 `a054f4f`로 커밋했다.
- 기존 두 커밋은 [PR #1](https://github.com/hyeonhb/ontosary/pull/1)로 원격 main에 병합했다(`7671a1a`). main은 origin/main을 추적한다. R3는 그 main에서 만든 `fix/analyzed-file-manifest`에서 구현하고, [PR #2](https://github.com/hyeonhb/ontosary/pull/2)를 2026-11-07 squash 병합했다(`b894137`). 로컬 main도 해당 원격 커밋까지 fast-forward 동기화했다.
- 사용자는 이후 작업도 검증 후 branch push → PR 생성·검토 → merge → main 동기화까지 자동 수행하도록 지속 승인했다. 별도 지시가 없으면 반복 승인 없이 이 절차를 따른다.
- [CONTRIBUTING](../CONTRIBUTING.md)의 GitHub Flow와 Conventional Commits를 준수한다. 작업 브랜치·작은 커밋·PR 검토·검증 기록이 기준이다. GitHub 보호 규칙이나 CI를 설정했다고 가정하지 않는다.
- 사용자 선택으로 원격 Apache-2.0 LICENSE를 유지하고 패키지·README를 통일했다. ADR-009가 최초 MIT 선택을 대체한다.

## 실제 구현된 기능

- TypeScript 타입·필드·함수·참조·조건·소스 근거와 진단을 JSON으로 추출.
- 작은 Formal Context/NextClosure, 후보 필터, 일반화 관계, 결과 상한.
- 제한된 논리 IR, 유한 열거·동치·양방향 함의·반례·Unknown/Unsupported.
- JSON CLI `scan`, `concepts`, `compare`.
- Vehicle/Listing/ConsultationRequest의 React+Vite 예제.
- 맥락 문서, 회귀 테스트, 재사용 가능한 실험·리뷰 증거.

이번 수정: enum 멤버의 타입만 보고 receiver 실행을 생략하던 경로를 차단했다. 직접 enum 선언 식별자(괄호·named import alias 포함)만 허용하고 optional/call/assertion/non-null/nested receiver·enum 객체 별칭을 거부한다. explicit this는 전체 predicate와 개별 condition 모두 Unsupported다. parameters는 원래 소스 signature이며, 지원된 IR의 argN만 런타임 인자 위치다.

## 실행 명령

```sh
pnpm install --frozen-lockfile
pnpm build
pnpm ontosary scan examples/react-vite --json
pnpm ontosary concepts examples/react-vite --json
pnpm ontosary compare examples/react-vite canConsultFromCard canConsultFromDetail --assume-same-input --json
pnpm exec vitest run tests/normalization-soundness.test.ts
pnpm check
pnpm experiment
node docs/reviews/evidence/2026-11-04-independent-check.mjs
pnpm example:dev
```

동명 함수는 전체 ID로 지정한다. Unknown/Unsupported 종료 코드 2, 프로젝트/컴파일/인수 오류는 1이다. probe 스크립트는 관찰 결과를 출력하므로 exit 0만으로 Gate 통과를 판단하지 않는다.

## 최신 검증 결과

환경: Node 22.19.0, pnpm 11.19.0, TypeScript 5.9.3. 새 의존성을 추가하지 않았다.

2026-11-07 중단 복구: PR #2 생성 후 병합 전 상태에서 재개했다. 구현 변경 없이 검증한 head `bb2dfe2`를 확인했고 `pnpm check`를 다시 실행해 82개 테스트·타입 검사·production build가 모두 통과했다. 원격 검사 목록은 비어 있었으며 CI 통과를 주장하지 않는다. 기존 실험·독립 probe 증거는 같은 구현에 대한 이전 실행 결과로 유지했다.

- 수정 전 targeted regression: 진단 0개인 fixture에서 34개 중 29 실패/5 통과.
- 수정 후 targeted regression: 한도 검사 추가 후 **35개 통과**.
- `pnpm check`: 코어/예제 타입 검사, **5개 파일/82개 테스트 통과**, Vite production build 성공.
- `pnpm experiment`: 기존 4개 비교 기대값 통과. 타입 6, 함수 13, 지원 predicate 6/미지원 7; FCA 13×26, 형식 개념 20/후보 8/관계 8, 잘림 없음. 실험 수치·비교 결과는 동일하며 scan JSON의 파일 범위 설명만 갱신했다.
- 새 회귀 테스트: 20개 거부 receiver 사례, 함수/메서드/branch의 explicit this, 정상 9개 함수/81쌍 실제 진리표 및 반례 재실행, named import·문자열/숫자 enum, 4,096/8,192 경계, core/CLI 상태 일치.
- 기존 독립 probe: 정상 144회 실행·IR 대조, 256쌍, 반례 336개, FCA 4×3 관계 4,096개 대조 통과. R1 optional/call, R2 first/second 비교가 모두 Unsupported/평가 0으로 바뀜. CLI 재현은 종료 2.
- R3 targeted regression은 수정 전 6개 모두 실패, 수정 후 6개 모두 통과했다. TS/TSX/MTS/CTS·JS/JSX/MJS/CJS·선언 파일, imported JS 참조, JS-only, allowJs만 설정한 경우, 제외 JS의 오류 진단, CLI/API manifest 일치를 검사했다.
- 독립 probe를 R3 적용 후 다시 실행하여 files=[input.ts], 제외 근거 ignored.js, 기존 R1/R2 거부와 정상 계산 검증을 확인했다. 새 증거는 `2026-11-06-file-manifest-results.json`이다.
- 초기 PoC의 브라우저 smoke check는 2026-11-03 기록이다. 이번 수정은 UI를 변경하지 않았으며 브라우저 확인을 반복하지 않았다.

## 남은 문제와 제약

- **R3 해결:** files는 실제 방문하는 TS/TSX/MTS/CTS 구현 파일만 포함한다. 제외된 구현 파일은 각각 omissions의 근거 경로·위치·이유로 보고한다. 타입 해석·참조·진단은 유지한다. 이 파일 수를 프로젝트 전체 coverage 비율로 해석하면 안 된다.
- enum namespace 경로·값 별칭·explicit this를 보수적으로 거부한다. 지원 확대는 별도 실행 대조가 필요하다.
- 기존 단일 반환식·필수 유한 입력·한 단계 속성 제한, strictNullChecks, 런타임 타입 준수·안정적인 plain data·입력 독립성 전제는 유지된다.
- 소스 ID의 편집 안정성, 재귀 project references, 최상위 조건·클래스 필드·프레임워크 의미, 큰 프로젝트 비용은 미해결/미검증이다.
- 승인 워크플로·LLM·SMT·MCP·자동 수정은 미구현이다. FCA 후보가 업무 개념이거나 조건 차이가 버그라는 뜻은 아니다.
- Gate 1은 2026-11-07 독립 리뷰에서 제한된 지원·검증 범위로 통과 판정했다. 모든 TS 입력의 건전성이나 Gate 2~4의 제품 효과를 입증한 것은 아니다.

## 2026-11-07 독립 재검토

PR #1~#3가 반영된 main `c6e0fc7`을 별도 리뷰 세션에서 재검증했다. **R1/R2/R3 해결, 검토 범위 내 추가 결함 없음**으로 판정했다. `pnpm check` 82개·타입 검사·예제 빌드와 `pnpm experiment` 4개 비교가 통과했다. 기존 독립 probe와 새 receiver/this/import/file 경계 probe도 통과했다. Gate 1은 제한된 지원·검증 범위에서 통과로 재평가했으며 Gate 2~4의 제품 효과는 여전히 미검증이다. 원격 check-runs/status 목록은 비어 있어 CI 성공을 주장하지 않는다.

[독립 리뷰](reviews/2026-11-07-post-merge-review.md), [당시 다음 개발 지시](reviews/2026-11-07-next-plan.md), [리뷰 맥락](reviews/REVIEW_CONTEXT.md)을 참조한다. 초기 NEXT_PLAN과 과거 원시 증거는 이행된 지시·관찰로 보존했다. 아래 corpus 연구 방향을 유지하며 이번 리뷰에서 제품 소스·테스트·설정을 수정하지 않았다.

## 2026-11-07 실제 corpus 관찰 검증

- 기준 main `c1a542c`에서 `codex/corpus-observation`으로 작업했다. 제품 소스·기존 지원 경계·FCA/논리 상한·의존성은 그대로다.
- p-queue `7f272ab5`의 production 5파일 및 priority-queue 4파일, date-fns v4.1.0 `313b902b`의 요일 함수와 local imports 9파일을 분석했다. 원래 p-queue 설정의 shared config 부재 실패도 기록했다.
- 라벨 24개 중 22개 일치, 2개 명시적 클래스/필드 모델 미지원. 사람 검토 0개, 승인 지식 0개. 조건 원문 추출의 일치와 정규화 지원을 구분했다.
- predicate 지원: p-queue production 0/103, 구성요소 0/15, date-fns 0/5. 범위 간 중복을 합산하지 않는다. 사전 날짜 비교 2쌍 모두 Unsupported/평가 0회.
- FCA: production은 103×188로 입력 상한 초과; 구성요소 15×31의 후보 23개, weekday 5×13의 후보 3개, 둘 다 잘림 없음. 같은 facts의 단순 그룹도 저장했다. 후보 수는 품질 점수가 아니다.
- `pnpm check`: 6파일/89테스트·타입 검사·예제 production build 통과. `pnpm experiment`: 기존 4/4 비교 통과, 과거 결과 변경 없음.
- 두 새 scanner 실행의 비시간 파일 14개 byte 일치. 재현 환경·hash·wall time·원시 결과는 `experiments/corpus/results/2026-11-07*`에 있다. 다운로드 준비 4,773ms, 사람의 준비 노력·검토 시간 미측정.
- 새 입력/runner/해석 보고는 날짜별 기존 리뷰·NEXT_PLAN을 보존한 채 추가했다. 정적 관찰만 수행했으며 원본 corpus 코드를 실행하지 않았다.

## 2026-11-07 corpus 독립 리뷰

main `a58a88b`을 독립 검토해 `pnpm check` 89개·기존 실험 4/4 및 새 corpus 실행의 비시간 파일 14개 일치를 확인했다. 원시 관찰은 재현됐으나 평가기가 라벨의 주장보다 약한 조건으로 correct를 내는 R4와 선언 이름을 사용 참조로 오인하는 R5(Medium 2건)를 재현했다. 제품 코어의 새 false proof는 확인하지 않았다. 기존 22/24는 현 평가기 판정이며 자연어 주장 전체가 자동 검증됐다는 의미로 확대하지 않는다.

사용자는 다음 제품 실험으로 **업무 개념·관련 코드 탐색 우선**을 선택했다. [독립 리뷰](reviews/2026-11-07-corpus-independent-review.md), [현재 개발 지시](reviews/2026-11-07-corpus-review-next-plan.md), ADR-014를 참조한다. 원래 corpus 보고서·라벨·raw 결과는 당시 관찰로 보존했다.

## 다음 작업

2026-11-08 중단 복구: 리뷰 문서가 staged 상태인 `docs/corpus-independent-review`에서 재개했다. fetch 후 기준 main `a58a88b`에 원격 추가 변경이 없고 제품 소스·테스트·실험 원본이 그대로임을 확인했다. 위 2026-11-07 검증은 동일 구현의 실행 기록으로 유지하며, 문서 전달 재개를 새 실험 수행으로 표시하지 않는다.

1. 평가기 R4/R5의 claim 계약·실제 사용 위치 판정을 보완하고 새 버전 결과를 만든다. 제품 코어·지원 문법·한도는 바꾸지 않는다.
2. 실제 업무 애플리케이션의 한 개념에서 관련 코드·조건 근거를 찾는 과업을 정의한다. 검색/LSP·동일 facts의 단순 그룹을 기준선으로 두고 FCA의 추가 가치와 검토 비용을 측정할 준비를 한다.
3. 코드 사실 라벨의 사람 검토와 제품 효용 검증을 구분한다. 참가자·학습 효과·시간 측정 절차 없이 사람이 검토했다거나 탐색 시간이 줄었다고 주장하지 않는다.
4. 주요 기술적·철학적/방향성 선택이 필요하면 관찰·선택지·권고를 사용자에게 제시한다. 이 지침은 작은 수정과 이미 승인된 원격 반영을 반복 승인 대상으로 만들지 않는다.

핵심 코드: `src/core/{analyzer,logic,fca,model}.ts`, `src/cli/index.ts`. 최신 실험: [corpus README](../experiments/corpus/README.md), [관찰 보고서](reviews/2026-11-07-corpus-observation.md). 지원 경계는 [ARCHITECTURE](ARCHITECTURE.md), 결정은 [DECISIONS](DECISIONS.md), 실험 해석은 [RESEARCH](RESEARCH.md), 순서는 [ROADMAP](ROADMAP.md)를 따른다.
