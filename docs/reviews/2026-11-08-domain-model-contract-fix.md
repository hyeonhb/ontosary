# S1 R6/R7 V2 보완 인계 — 2026-11-08

**R6 탐색과 R7 standalone 입력 검사를 V2로 보완했다. 독립 재검토는 대기 상태다.** 기준 main `2cd6e72d553ae61954f8469c31f0d6e41ef0a883`, 작업 브랜치 `codex/domain-model-contracts`이며 미병합 의존 브랜치는 없다. [지시](2026-11-08-domain-model-review-next-plan.md), [V2 실행/사용 안내](../../experiments/domain-model/v2/README.md), [새 원시 검증](../../experiments/domain-model/verification/2026-11-08-v2)을 참조한다.

## R6 전후

V1의 outgoing relatedItems만 따라가면 시작 개념에서 동작으로 갈 수 없었다. V2 `navigate(model,id)`는 원래 모델을 바꾸지 않고 한 단계 incoming/outgoing 참조를 명시적으로 반환한다. direction과 실제 declaredEdge, 대상 항목 종류 및 fact/candidate ID를 함께 제공한다. 업무 관계가 대칭이라는 주장은 아니다.

실제 소비 함수와 CLI로 order→branch, cancel-request→dialog-submit/cancel-transport/refund-also-cancels/dismiss, refund-request→refund-transport/refund-also-cancels/dismiss를 확인했다. 경로는 incoming이며 원래 선언 방향은 동작→개념이다. 없는 ID는 found=false/exit1이고 order→refund-transport 같은 무관한 전이 경로는 반환하지 않는다. 환불 중 조건부 취소와 입력 없는 닫기는 별개 항목으로 유지한다. [조회 결과](../../experiments/domain-model/results/2026-11-08-v2/navigation.json).

## R7 전후

V1 standalone은 anchor 파일만 검사해 타깃 선언 변경을 놓쳤다. V2 `inputs.mjs`는 V1 runner의 원문 inventory/manifest/설정/hash·준비 Program 파일/hash·현재 Program 구성원·live 컴파일 진단 검사를 분리한 공통 함수다. 새 runner와 standalone CLI가 공유한다. 역사적 V1은 그대로이며 wrapper가 V1 추출/FCA를 호출할 때 기존 guard도 중복 실행된다.

| 실제 CLI 사례 | anchorValid | analysisInputsValid | valid / exit / 재검토 |
| --- | --- | --- | --- |
| 정상 고정 cache | true | true | true / 0 / 불필요(의미 승인 아님) |
| target 선언만 임시 복제에서 변경 | true | false | false / 1 / 필요 |
| 해석 설정 파일 누락 | true | false | false / 1 / 필요 |
| source 수정 | false | false | false / 1 / 필요 |
| 명시적 anchors-only | true | false | false / 1 / partial·필요 |

정확한 영향 집합을 새로 계산하지 않고 자동 역할 fact 468개·candidate 5개와 전체 모델 12개를 보수적으로 무효화/재검토시킨다. 입력 일부만 있을 때 anchor 성공을 전체 사용 가능으로 표시하지 않는다. 형식/원문/분석 입력 검사이지 런타임 정책·업무 의미·실제 사람 승인 인증이 아니다. 원문 cache에는 쓰지 않았으며 변조는 임시 복제에서만 했다.

## 검증·보존

- 새 회귀 11개, 전체 `pnpm check` **10파일/174테스트**, 타입 검사·Vite build 통과. `pnpm experiment` 기존 **4/4** 통과.
- pinned cache를 사용하는 CLI 회귀 5개는 cache가 없으면 skip한다. 이번 환경에서는 11개 모두 실행했고 별도 CLI 원시 증거도 남겼다. 순수 탐색 회귀와 기존 anchor/참조/승인/unknown 회귀는 유지된다.
- 새 출력 두 곳의 **비시간 15파일 byte 일치**, timing.json만 제외. 그중 기존 12파일은 V1 저장 결과와도 동일하다. 원문 4,735개·Program 1,638파일과 진단 0을 재확인했다.
- 78×6 context, 후보5/단순 그룹 동일, 추가 의미0·승인0을 보존했다. 탐색 연결의 개선은 FCA의 새 발견이 아니다.
- V1 코드/입력/결과·기존 독립 probe/원시 증거·제품 core/CLI·기존 corpus·의존성·상한은 수정하지 않았다. 설치 예산도 재개하지 않았다.

최신 full validation은 validation-v2.json이고 validation.json은 재사용된 V1 anchor 결과다. [V2 제공 파일 목록](../../experiments/domain-model/v2/agent-input-manifest.json)은 실제 경로/hash를 가리킨다. 아직 S2용 격리 배포 묶음은 아니며 exclude 목록만으로 평가 자료 격리를 주장하지 않는다.

다음 권고는 보완 독립 재검토 후 S2 reason 계약·고정 fixture/oracle와 A/B/C 제공 자료 동결이다. 평가 자료 없는 별도 묶음과 동등 정보 일반 문서를 실제로 마련해야 한다. 알려진 사례의 pilot이라는 한계를 유지하며 이번에 S2 비교나 실제 앱 정책 변경은 실행하지 않았다. 사람 비용·agent 효용·Gate 2~4는 미검증이다.
