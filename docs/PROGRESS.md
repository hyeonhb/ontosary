# 현재 작업 상태 — 새 세션은 이 문서부터 읽기

마지막 갱신: **2026-11-06, Asia/Seoul**.

## 현재 단계

첫 PoC의 구성 요소 구현 후, 독립 리뷰가 발견한 **R1/R2 false proof 차단을 완료**했다. 좁아진 지원 범위의 독립 재검토가 가능하다. 모든 TS 문법에 대한 건전성이나 제품 유용성을 입증한 상태는 아니다. R3(mixed TS/JS 파일 집계 계약)도 수정·회귀 검증했다. NEXT_PLAN의 직접 수정·검증 지시와 명시된 후속 결함 R3까지 완료했으며, 이후 실제 corpus/사용자 과업 비교는 후속 연구 단계다.

[R1/R2 개발 인계](reviews/2026-11-06-normalization-fix.md)와 [NEXT_PLAN 이행 점검·R3 인계](reviews/2026-11-06-next-plan-completion.md)에 전후 판정·검증·남은 위험을 정리했다. 과거 [리뷰](reviews/2026-11-04-poc-review.md)와 [NEXT_PLAN](reviews/NEXT_PLAN.md)은 당시 지시와 관찰로 보존했다. 이 문서가 최신 구현 상태다.

## 저장소와 개발 규칙

- `origin`: `https://github.com/hyeonhb/ontosary.git`.
- 원격 초기 LICENSE 커밋 `5d33ab6` 기반으로 `chore/initial-poc`에 기존 작업을 `a054f4f`로 커밋했다.
- 기존 두 커밋은 [PR #1](https://github.com/hyeonhb/ontosary/pull/1)로 원격 main에 병합했다(`7671a1a`). main은 origin/main을 추적한다. R3는 그 main에서 만든 `fix/analyzed-file-manifest`에서 구현했다.
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
- Gate 1은 수정된 지원 범위로 재평가할 수 있다. 독립 리뷰의 승인이나 Gate 2~4 효과를 주장하지 않는다.

## 다음 작업

1. git 상태·CONTRIBUTING·본 문서와 새 개발 인계를 읽고 기존 사용자 변경을 확인한다.
2. 공개/허가된 corpus 2개를 revision/라이선스·분석 범위와 함께 고정한다.
3. 코드 사실·업무 의미를 분리한 수동 라벨 20~30개를 준비하고 별도 검토를 받는다.
4. 검색/LSP·단순 속성 그룹 기준선과 FCA/논리 검증의 과업별 순증분을 측정한다. 실제 사람의 검토 시간이나 업무 의미 승인을 자동 테스트 결과로 대신하지 않는다.

핵심 코드: `src/core/{analyzer,logic,fca,model}.ts`, `src/cli/index.ts`. 회귀: `tests/normalization-soundness.test.ts`, 기존 tests. 최신 증거: `docs/reviews/evidence/2026-11-06-*`. 지원 경계는 [ARCHITECTURE](ARCHITECTURE.md), 결정은 [DECISIONS](DECISIONS.md), 실험 해석은 [RESEARCH](RESEARCH.md), 순서는 [ROADMAP](ROADMAP.md)를 따른다.
