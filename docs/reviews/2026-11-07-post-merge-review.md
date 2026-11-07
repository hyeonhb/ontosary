# 병합 후 독립 리뷰 — 2026-11-07

**결론: 검토한 변경에서 추가 수정이 필요한 결함을 발견하지 못했다. 이전 R1/R2/R3를 해결로 판정한다. Gate 1은 문서화된 제한과 이번 검증 범위에 한해 통과로 재평가하며, 다음 작업은 실제 corpus의 coverage·정답셋 실험을 권장한다.** 모든 TypeScript 입력에 대한 건전성 증명이나 제품 유용성 승인이 아니다.

## 검토본과 범위

- 저장소: `hyeonhb/ontosary`, 로컬/원격 main 모두 `c6e0fc7babb28ac37fde6fdd68f416af7add8e78`. 시작 시 사용자 변경 없음. fetch 후 일치를 확인했다.
- [PR #1](https://github.com/hyeonhb/ontosary/pull/1): 초기 PoC와 R1/R2 수정. head `8d4f527107f18667b3bc3f5bd49634b354e174db`, merge `7671a1a96dd2bf4841a9f80a1737e37143b296b4`.
- [PR #2](https://github.com/hyeonhb/ontosary/pull/2): R3 파일 목록 수정. head `bb2dfe281433440e4af80f720c64e0acc9912287`, squash `b8941373102cde382428c5526c8d3c2209e57c98`.
- [PR #3](https://github.com/hyeonhb/ontosary/pull/3): 원격 반영·복구 검증 기록. squash `c6e0fc7babb28ac37fde6fdd68f416af7add8e78`.
- GitHub 연결 도구로 세 PR의 병합 상태와 메타데이터를 확인했다. 로컬 Git으로 `a054f4f..c6e0fc7`의 구현·테스트·문서 차이를 검토했다. 초기 PoC 전체를 변경으로 보는 PR #1 diff와 실제 R1/R2 수정 delta를 구분했다.
- PROGRESS → ARCHITECTURE → ROADMAP, AGENTS/CONTRIBUTING, 두 개발 인계, 새 테스트·fixture, 기존 리뷰·재현 스크립트를 읽었다.
- 제품 소스·테스트·설정은 수정하지 않았다. 날짜별 리뷰 증거와 현재 리뷰 맥락·진행 상태만 갱신한다. 과거 리뷰와 NEXT_PLAN, 원시 JSON은 보존한다.

## 이전 지적의 처리 결과

| 지적 | 독립 재검토 결과 | 판단 |
| --- | --- | --- |
| R1: enum receiver 평가 생략 | optional/call receiver가 Unsupported, 평가 0. CLI 재현은 종료 2. 직접 enum 선언에 해소되는 식별자만 상수 경로 통과 | 해결 |
| R2: explicit this의 argN 이동 | 전체 predicate와 개별 condition에서 거부. first/second 비교 모두 Unsupported, 가짜 동치·반례 없음 | 해결 |
| R3: 건너뛴 JS를 files에 포함 | 실제 AST 순회에 사용하는 목록과 files가 동일. 제외 구현 파일은 근거·이유 포함, JS 타입 해석·진단은 유지 | 해결 |

R1은 optional token만 검사하는 임시 수정이 아니라 receiver의 구문과 심볼 identity를 제한한다(`src/core/logic.ts:49–66`). 본문에 호출·타입 단언 등이 숨겨져도 성공으로 지우지 않는다. 실제로 안전할 수 있는 enum 객체 별칭과 namespace 경로도 거부하는 비용은 문서에 공개되어 있고 이번 정확성 수정의 적절한 선택이다.

R2는 새 runtime this 모델을 도입하는 대신 normalize 진입부에서 거부한다(`logic.ts:13–14`). 그러므로 branch와 반환식에 같은 정책을 적용한다. `FunctionFact.parameters`가 소스 signature를 보존한다는 설명과 지원된 IR의 argN만 실제 인자 위치라는 설명도 일치한다.

R3는 사전에 분리한 files 배열로 JSON 목록과 AST 순회를 수행한다(`src/core/analyzer.ts:45–52`, `:135` 부근). 이는 두 필터가 어긋나는 원인을 없앤다. Program을 줄이지 않아 imported JS 참조·타입과 제외 파일의 오류 진단도 보존한다. schemaVersion 1 유지도 기존 계약 복원이라는 변경 범위와 맞는다.

## 직접 수행한 검증

환경: Node 22.19.0, pnpm 11.19.0, TypeScript 5.9.3. 새 의존성을 설치하거나 추가하지 않았다.

1. `pnpm check`: **5개 파일/82개 테스트**, 코어·예제 타입 검사, Vite production build 통과. 새 테스트는 TypeScript 진단 0을 별도로 확인하며, 컴파일 오류에 따른 일괄 거부로 결함을 가리지 않는다. 정상 비교의 oracle은 실행 진리표이고 반례도 다시 실행한다.
2. `pnpm experiment`: **4/4** 비교 통과. 파일 4, 타입 6, 함수 13, supported 6/unsupported 7, FCA 13×26, 형식 개념 20/후보 8/관계 8, 잘림 없음. 실행 후 기존 추적 파일에 diff가 없음을 확인했다.
3. 원래 독립 probe를 그대로 재실행하고 [2026-11-07 결과](evidence/2026-11-07-independent-results.json)를 새 파일로 저장했다. 144회 실행/IR 대조, 256쌍 비교, 336개 반례 재실행, FCA 4×3 관계 4,096개, 4,096/8,192 열거 경계 검증 통과. JSON을 별도로 검사해 R1/R2의 네 비교가 Unsupported/평가 0이며 두 CLI 재현이 종료 2인지 확인했다. mixedJs.files는 input.ts만 포함하고 ignored.js는 제외 근거에 남는다. probe의 exit 0만으로 결론을 내리지 않았다.
4. 기존 개발 fixture와 별개로 [새 경계 probe](evidence/2026-11-07-boundary-check.mjs)를 작성·실행했다. [원시 결과](evidence/2026-11-07-boundary-results.json):
   - 12가지 receiver 형태를 단독/부정/`true ||` 내부에 넣은 **36개 거부 사례** 모두 Unsupported. satisfies, comma, 조건식, non-null, assertion, optional, nested, 값 별칭, call, 매개변수, computed receiver 포함.
   - function expression, object method, class method, branch의 explicit this **4건** 모두 predicate/조건에서 거부.
   - 재노출 barrel→named import alias, 괄호, const enum, 음수 numeric enum 등 **6개 정상 함수/12회 실행값 대조**, 정상 비교 3쌍 통과.
   - 빈 JS, 주석만 있는 JS, imported JSON은 files에서 제외되고 위치·이유가 남는다. TS 분석 파일 4개, CLI/API JSON 일치, 진단 0.
5. 첫 추가 probe에서는 조건식 receiver에 별도 conditional fact가 생긴다는 점을 놓쳐 “조건이 1개”라고 가정한 assert가 실패했다. 제품 문제로 기록하지 않고 반환식 fact만 비교하도록 검증 코드를 바로잡은 뒤 위 전체 검사를 통과했다. 식별된 결과를 통과시키기 위해 제품 코드를 수정한 것은 아니다.
6. `a054f4f`와 현재 main 사이에서 2026-11-04 상세 리뷰·NEXT_PLAN·독립 스크립트·원시 결과가 변경되지 않았음을 확인했다. 기존 역사적 관찰을 수정 완료 결과로 덮어쓰지 않았다.
7. GitHub CLI로 검토 head의 check-runs와 commit statuses를 조회했다. 둘 다 빈 배열이다. statuses 응답의 집계 state는 pending이지만 등록된 status가 없으므로 이를 실행 중 검사나 CI 성공으로 표현하지 않는다. 이 리뷰의 검증 근거는 직접 실행한 로컬 검사다.

재현:

```sh
pnpm check
pnpm experiment
node docs/reviews/evidence/2026-11-04-independent-check.mjs
node docs/reviews/evidence/2026-11-07-boundary-check.mjs
```

새 경계 스크립트도 통제된 자체 fixture만 실행하며 제품 분석기에 프로젝트 코드 실행 기능을 추가하지 않는다. 과거 raw JSON을 출력 리다이렉션으로 덮어쓰지 않는다.

## 남은 위험과 Gate 판단

**새 확인 결함: 없음.** 위 판단은 해당 수정과 명시한 검증 사례에 한정한다. 정적 분석기의 완전한 건전성·완전성을 증명한 것은 아니다.

| Gate | 이번 판정 | 남은 근거 |
| --- | --- | --- |
| 1. 기술적 정확성 | 제한된 지원·검증 범위에서 통과, 통제된 corpus 실험 진행 가능 | 새로운 문법/프로젝트에서 soundness 실패가 생기면 재개방 |
| 2. 의미적 유용성 | 미검증 | 독립 정답셋과 후보 검토 |
| 3. 기존 방법 대비 효용 | 미검증 | 검색/LSP·단순 속성 그룹 대비 비교 |
| 4. 도입·유지 비용 | 부분 확인, 통과 근거 부족 | 실제 프로젝트 설정 시간·미지원 비율·편집 후 ID 유지 비용 |
| 5. 공개 배포 가능성 | 미통과 | 사용 과업 근거·배포 준비. 정확성 수정만으로 Beta 권고하지 않음 |

enum namespace/값 별칭/explicit this의 거부는 공개된 한계다. strictNullChecks와 실제 타입 준수, 안정적인 plain data, 입력 독립성, 동일 입력 assertion도 여전히 필요하다. TS Program 로딩 비용, FCA 입력/출력 상한, 편집에 취약한 ID, project references, 최상위 조건·프레임워크 의미는 해결됐다고 볼 수 없다.

이번에 사용자 과업·새 corpus·의미 라벨·시장 비교·브라우저 동작을 새로 평가하지 않았다. 초기 예제에서의 의미적 잡음이나 제품 차별성에 관한 2026-11-04 판단은 자동으로 개선되지 않는다. Apache-2.0은 현재 LICENSE/package 설정과 기존 사용자 결정에 따른 상태이며 이번 변경에서 새로운 라이선스 선택을 하지 않았다.

## 제품 방향과 다음 작업

**정확성 보완을 반복하는 데만 머물지 말고 실제 corpus의 관찰 자료를 확보할 시점이다.** 다만 새로운 지원 문법을 동시에 넓히면 측정 대상이 바뀌므로 이번 다음 작업에서는 코어를 고정한다.

다음 하나는 “공개/허가된 작은 TS corpus 2개를 고정하고, 코드 사실 라벨 20~30개와 coverage·미지원·후보 검토 자료를 만든다”이다. 업무 의미의 승인이나 실제 사람의 검토 시간은 agent의 판단·자동 실행 시간으로 대체하지 않는다. FCA의 가치는 같은 facts에서 만든 단순 속성 그룹 기준선과 분리해 볼 수 있도록 자료를 준비한다.

복사 가능한 지시는 [2026-11-07-next-plan.md](2026-11-07-next-plan.md)에 있다. 초기 [NEXT_PLAN](NEXT_PLAN.md)은 이행된 과거 지시로 보존한다. [REVIEW_CONTEXT](REVIEW_CONTEXT.md)는 이번 판정과 미검증 상태를 반영한다.
