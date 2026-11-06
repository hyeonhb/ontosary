# NEXT_PLAN 이행 점검과 R3 개발 인계 — 2026-11-06

구현 세션의 완료 점검이며 독립 리뷰 승인이 아니다. [원래 NEXT_PLAN](NEXT_PLAN.md)과 기존 리뷰 관찰은 수정하지 않았다. R1/R2 구현 이후 명시된 후속 결함 R3도 수정했다.

## 직접 지시사항 점검

| NEXT_PLAN 요구 | 상태와 근거 |
| --- | --- |
| 진단 없는 R1/R2 최소 재현을 먼저 실패 테스트로 작성 | 완료. 기존 red 로그 29 실패/5 통과, fixture diagnostics 0 검사 |
| enum receiver 허용 경계·중첩 미지원 우회 차단 | 완료. 직접 enum 선언 식별자만 허용; 20개 거부 receiver 사례 |
| explicit this의 런타임 인자 오대응 제거 | 완료. predicate/condition 모두 Unsupported, source signature는 보존 |
| 정상 식의 실제 실행/IR 대조와 반례 재실행 | 완료. 회귀 81쌍, 별도 probe 256쌍/336개 반례 |
| core/CLI 상태·이유·평가 0·종료 2 일치 | 완료. R1/R2 CLI 회귀 검사 |
| 기존 enum/union/논리·도메인·4,096 경계·컴파일 오류 거부 유지 | 완료. 기존 테스트 및 독립 probe 재실행 |
| check/experiment·현재 지원 범위·결정·연구·상태 문서 갱신 | 완료. 최종 82개 테스트/5개 파일, 4개 비교 사례 |
| 과거 리뷰 JSON 보존, 새 증거·다음 리뷰 근거 제공 | 완료. 원래 증거는 유지, 날짜·작업별 새 원시 결과와 인계 문서 |
| R1/R2 뒤 별도 작은 작업으로 R3 집계 계약 정리 | 완료. 아래 내용 및 `tests/file-manifest.test.ts` |

## R3 수정

`ScanResult.files`는 실제 AST 방문에 사용한 TS/TSX/MTS/CTS 구현 파일만 담는다. Program의 로컬 구현 파일을 먼저 지원/미지원으로 나누어, 목록과 순회 조건이 달라질 여지를 제거했다. 미지원 구현 파일마다 `omissions`에 evidence.file, 소스 범위, 제외 이유를 기록한다.

- 선언 파일·외부 라이브러리는 기존 범위처럼 미열거다.
- JS/JSX/MJS/CJS는 분석 사실을 추출하지 않지만, Program에 남아 타입 해석·심볼 참조·컴파일 진단에 참여한다.
- `allowJs: true`만 있고 JS가 없으면 가짜 누락을 내지 않는다.
- JS-only는 분석 파일/타입/함수의 빈 배열과 실제 제외 근거를 반환한다.
- 제외 파일에 오류가 있으면 기존처럼 진단과 proof 거부를 유지한다.
- JSON 필드 구조를 바꾸지 않고 schemaVersion 1의 문서화된 의미를 복원했다. 실험 files.length도 이 분모를 사용한다. omissions에는 다른 종류의 누락도 있어 그 길이가 제외 파일 수를 뜻하지는 않는다.

변경 코드: `src/core/analyzer.ts`, `src/core/model.ts`, `experiments/run.mjs`. 회귀: `tests/file-manifest.test.ts`.

## 검증

1. 수정 전 새 6개 테스트 모두 실패: 잘못된 files·누락 근거·allowJs 오보고를 재현했다.
2. 수정 후 6개 모두 통과. TS/TSX/MTS/CTS와 JS/JSX/MJS/CJS·선언 파일, imported JS, JS-only, 제외 파일 diagnostics, CLI/API JSON 일치를 검사했다.
3. `pnpm check`: 5개 파일/82개 테스트, 타입 검사·Vite build 통과.
4. `pnpm experiment`: 4개 비교 통과. 예제 분석 파일 수 4 등 지표 유지, scan JSON의 지원 범위 문구만 변경.
5. 원래 독립 probe 재실행: [새 원시 결과](evidence/2026-11-06-file-manifest-results.json). mixedJs.files는 input.ts 하나이며 ignored.js가 제외 근거에 등장한다. 기존 정상 144회 대조·256쌍·336반례·FCA 4,096 contexts·열거 한도가 유지됐다. R1/R2도 여전히 Unsupported다.

```sh
pnpm build
pnpm exec vitest run tests/file-manifest.test.ts
pnpm check
pnpm experiment
node docs/reviews/evidence/2026-11-04-independent-check.mjs
```

## 원격 반영과 후속 연구의 구분

기존 PoC와 R1/R2는 [PR #1](https://github.com/hyeonhb/ontosary/pull/1)로 main에 반영했다. 사용자는 이후 검증 완료 작업도 push·PR·merge·main 동기화까지 자동으로 처리하도록 승인했다. AGENTS/CONTRIBUTING에 지속 지침으로 기록했다. 구현 담당자의 self-review를 다른 리뷰어의 승인으로 표시하지 않는다.

NEXT_PLAN 말미의 실제 corpus 2개/수동 라벨 20~30개 및 검색·LSP/단순 그룹 대비 과업 비교는 후속 연구 권고다. 이번에 그 실험을 수행하거나 사람의 검토 시간을 측정했다고 주장하지 않는다. 현재 직접 지시한 정확성 수정과 그 다음 R3는 완료됐으며, 그 결과만으로 Gate 2~4를 통과시키지 않는다. 이후 우선순위는 PROGRESS/ROADMAP을 따른다.
