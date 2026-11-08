# V3 타입 선언 문맥 수정 독립 리뷰 — 2026-11-08

**판정: 보고된 R5 잔여 오류는 해결됐다. R4 해결 상태도 유지하며, 이번 변경의 검토 범위에서 추가 수정이 필요한 결함은 발견하지 않았다.** 현 방향을 유지하고 실제 공개 업무 앱의 탐색 과업 준비로 이동한다. 모든 TypeScript 문법에 대한 보장이나 제품 효용 검증 완료는 아니다.

## 검토본과 확인한 변경

[개발 보고](2026-11-08-type-context-fix.md), [PR #9](https://github.com/hyeonhb/ontosary/pull/9)의 병합 main `2dba3e2e52a3e085fcfe35fdee87a1fd16aa1365`를 검토했다. 시작 시 작업 트리는 깨끗했고 fetch 후 origin/main과 일치했다.

V2 대비 평가기 동작 변경은 `sourceUse` 조상 검사에 TypeAliasDeclaration / InterfaceDeclaration / TypeParameterDeclaration을 추가한 것이다. 타입 전용 선언 전체를 거부하되 검사 대상은 use 위치이므로, 실제 속성/메서드 접근의 target이 타입 signature인 경우는 유지된다. R4 타입 matcher, 원본 24개 V2 라벨 계약, core/CLI, 의존성·lockfile, 지원 문법·상한은 그대로다.

V1/V2 평가기와 runner·입력·raw 결과 및 이전 독립 증거가 보존된 것을 diff와 재실행으로 확인했다. V2 README의 역사적 버전 안내 추가는 과거 실행 코드를 바꾸지 않는다. V3 runner의 버전/입력 hash, V2 대비 라벨별 대조, 분석 산출물 동일성 검사를 읽었다.

## 직접 검증한 결과

| 검사 | 결과 |
| --- | --- |
| `pnpm check` | 8파일 / 136개 테스트, 타입 검사·예제 production build 통과 |
| `pnpm experiment` | 기존 비교 4/4, 기존 산출물 변경 없음 |
| 원래 독립 source/label 재실행 | V2 7/9 → V3 9/9 기대 일치 |
| 구현 세션의 인접 문맥 27개 | V2 18/27 → V3 27/27 기대 일치 |
| 새 독립 use/target 경계 fixture | 진단 0, 8/8 기대 일치 |
| V1 / V2 / V3 새 corpus 실행 | 저장 결과와 각각 비시간 14 / 16 / 16파일 byte 일치 |
| V2 / V3 core 분석 산출물 | 11개 동일성 검사 통과 |

`node experiments/corpus/v3/check-roles.mjs`를 재실행했고 출력 전체가 개발 보고의 역할 probe JSON과 byte 동일했다. TypeParam/member 선언 이름은 이유가 있는 mismatch이며 재귀/import/실제 읽기는 correct다. 기존 계약 회귀 10개는 V2/V3 양쪽에서 통과했다.

추가로 [독립 fixture](evidence/2026-11-08-type-context-independent-check.mjs)에서 타입 기본값의 typeof, interface computed key와 제약 타입 매개변수는 거부하고, 실제 객체의 computed key·generic 함수 호출·값/속성 읽기는 허용함을 확인했다. [원문·라벨·결과](evidence/2026-11-08-type-context-independent-results.json), [검증·재현 hash 요약](evidence/2026-11-08-type-context-review-verification.json).

새 fixture의 같은 이름 interface/const 라벨은 처음 const 선언을 target으로 예상해 mislinked였다. 변경 없는 analyzer의 `reference`는 병합된 symbol의 `declarations[0]`를 대표 근거로 사용하므로 라벨을 그 규칙에 맞춰 명시했고 그 사실을 결과 JSON에도 남겼다. 이 검사는 실제 use가 타입 선언 target 때문에 차단되지 않는지 확인하는 것이며, 값 선언·데이터 흐름을 추적한다고 해석하지 않는다. 이번 수정으로 생긴 회귀가 아니고 이 사례를 업무 의미 동일성의 증거로 사용해서도 안 된다.

원본 corpus 코드를 실행하지 않았고 기존 cache의 hash/설정/anchor를 runner에서 검증했다. 새 다운로드·다른 의존성 배치의 이식성·사람 검토 시간은 측정하지 않았다. 새 실행 경로는 `work/type-context-independent-v1-20261108`, `-v2-`, `-v3-`이며 과거 결과를 덮어쓰지 않았다.

## 제품·기술 판단

R1~R5의 보고된 결함은 각 명시된 지원·검토 범위에서 해결로 추적한다. 같은 역할 분류를 무한히 일반화하거나 새 평가기 버전을 만드는 것을 다음 목표로 잡지 않는다. 실제 업무 과업에서 추가 실패가 나타나면 그 최소 재현과 영향에 따라 다시 우선순위를 정한다.

작은 evaluator/runner 복제를 통한 V1/V2/V3 보존은 현재 재현 요구를 충족한다. 향후 공통화가 필요해도 과거 결과의 코드/입력/fingerprint를 재현할 수 있어야 하며, 지금은 이를 별도 리팩터링 과제로 확대하지 않는다.

- **Gate 1:** 제품 코어의 이전 제한적 통과 유지. R4/R5 평가 계약 문제도 보고된 범위에서 닫는다.
- **Gate 2 / 3:** 미검증. 업무 의미 이해와 검색/LSP·단순 그룹 대비 추가 효용이 다음 질문이다.
- **Gate 4:** 실제 도입/유지 비용 통과 근거 부족. 후보 앱의 설정·의존성 제약을 다음 단계에서 기록한다.
- **Gate 5:** 미통과. 현재 근거로 Public Beta를 권하지 않는다.

## 사용자 결정과 다음 작업

사용자는 이번 리뷰 중 **“공개 TypeScript 업무 앱 후보부터 조사”**를 선택했다. ADR-014의 업무 개념·관련 코드 탐색 우선 방향을 유지한 표본 준비 결정이다. 특정 앱이나 분석 전제 완화를 승인한 것은 아니다.

[공개 앱 후보 조사](2026-11-08-public-app-candidates.md)에서 Saleor Dashboard와 Medusa의 고정 revision·업무 흐름·설정/라이선스 제약을 확인했다. Saleor를 첫 **적합성 점검 후보**로 권하지만 strict=false라는 현 분석 전제 불일치가 있어 분석 표본 확정이나 scan 성공을 주장하지 않는다. Medusa는 읽은 주문 화면이 별도 라이선스 대상 권한 hook을 import하므로 그대로 공개 재현 표본으로 선정하지 않는다.

다음 한 작업은 [공개 앱 적합성·한 탐색 과업 고정](2026-11-08-public-app-next-plan.md)이다. 원문 기반 근거 목록을 먼저 만들고 원래 설정 실패·필요 준비 비용을 기록한다. 사람 실험·기능 확장 전에 실제 사용 가능한 범위가 있는지 판단한다. 주요 전제·타깃 과업·기술 투자 방향을 바꿔야 할 때는 구체적인 관찰과 선택지를 사용자에게 제시한다.
