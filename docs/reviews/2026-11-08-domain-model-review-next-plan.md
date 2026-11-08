# 다음 개발 지시 — S1 탐색·검증 계약 R6/R7 보완

작성: 2026-11-08. [독립 리뷰](2026-11-08-domain-model-independent-review.md)에 따른 다음 한 작업이다. 최종 목표와 S1→S2→S3 방향(ADR-020)은 유지한다. 이번에는 S2 agent 비교를 실행하거나 FCA/제품 core를 확장하지 않는다.

## 작업 목표와 현재 상태

agent가 시작 개념에서 관련 동작과 근거를 안내대로 찾고, 분석 입력이 바뀐 모델을 그대로 유효하다고 사용하지 않도록 인계 계약 두 곳을 보완한다.

검토 기준은 PR #15/main `4480438b462609971cac35aea61e4aa0a2a95d6f`다. 실제 작업은 이 지시가 반영된 최신 main에서 시작한다. 163개 테스트·기존 비교 4/4·같은 cache의 비시간 12파일·독립 64부분집합 FCA 검증이 통과했다. 78×6 context의 후보 5개는 모두 단순 그룹과 같고, 12개 모델의 새 의미 항목은 0이다. 원시 결과는 유효한 당시 관찰이며 덮어쓰지 않는다.

## 구현 범위

### R6: 문서와 일치하는 개념→동작 탐색

현재 `cancel-request.relatedItems`를 따라가면 order/line만 도달하고 안내에 적힌 dialog-submit/cancel-transport/refund-also-cancels는 도달하지 않는다. 관계 항목에서 개념으로 가는 incoming 링크만 있다. order와 refund-request도 같은 문제가 있다.

작은 조회 함수/색인으로 incoming과 outgoing 참조를 명시적으로 조회하거나, 모델의 필요한 outgoing 링크를 보완한다. 실제 소비자가 쓸 한 가지 탐색 계약을 고정하고 JSON·Markdown 안내·실행 예를 맞춘다. 탐색의 역방향 조회를 업무 관계의 대칭성으로 바꾸지 않는다. 기존 근거 없는 의미 관계를 새로 승인하지 않는다.

개념 ID를 입력하면 관련 동작과 fact/candidate 근거 ID를 추적할 수 있게 한다. 무관한 항목까지 모두 연결하지 않는다. 취소 요청에서 환불 중 취소를 찾을 수 있어야 하며, 닫기와 요청 취소의 구분을 유지한다. 역방향 참조를 훑는 방식이면 그 규칙과 경로를 결과에 보여준다.

### R7: 분석 입력의 유효성과 anchor 검사의 구분

독립 probe는 ModalService.fromComponent 대상 선언을 메모리에서 바꿨다. fresh 역할 판정은 opens-modal 78셀을 unknown으로 만들었지만 standalone validator는 valid=true/requiresReview=false였다. 전체 runner의 manifest/Program 검사는 이 변경을 거부한다. 별도 검증 경로가 그 전제를 공유하게 한다.

우선 기존 runner의 고정 입력/Program 무결성 검사를 재사용 가능한 함수로 분리해 새로운 standalone 검증 경로에도 적용하는 방식을 권한다. 원문 전체 재설치나 새로운 분석 알고리즘이 필요하지 않다. 다른 방법을 택한다면 target 선언·심볼 해석 입력의 변경을 어떤 범위에서 검출하는지 분명히 하고, 검사하지 않은 범위를 통과로 내보내지 않는다.

원문 일부만 있어 anchor 검사만 가능한 경우는 부분 검사 상태다. `anchorValid`와 `analysisInputsValid` 같은 구분 또는 동등한 상태 표현으로, 전체 모델 사용 가능/재검토 불필요로 오해할 성공을 방지한다. target·분석 입력 변경은 관련 fact/candidate/item을 재검토 상태로 만든다. 정확한 영향 집합을 계산하지 못하면 전체 자동 역할 근거를 보수적으로 무효화해도 된다. 런타임 정책·업무 의미를 인증한다는 주장은 추가하지 않는다.

## 보존과 제외 범위

V1 실행 코드·입력·과거 결과·기존 독립 증거는 당시 재현 자료로 보존한다. V2 등 별도 경로에 보완 계약/검증·결과를 추가하고 명시적으로 최신 경로를 안내한다. 변하지 않은 추출/FCA 코드는 기존 버전을 재사용할 수 있다. 불필요한 범용 스키마 엔진이나 파일 복제를 늘리지 않는다.

Vendure 고정 revision과 설치 cache는 읽기 전용으로 사용한다. 변조는 임시 복제/메모리 fixture만 사용한다. 종료된 환경 준비 예산을 다시 열지 않는다. core/CLI·strict·논리 지원·기본 FCA 상한·새 속성/표본·의존성·업무 의미 승인은 이번 범위 밖이다. R6의 탐색 연결 보완은 FCA가 새 업무 개념을 발견한 것으로 집계하지 않는다.

## 완료 조건과 검증

1. 실제 제공될 탐색 함수를 사용해 order→branch, cancel-request→dialog-submit/cancel-transport/refund-also-cancels, refund-request→refund-transport/refund-also-cancels 경로와 근거 도달을 확인한다. 모델 밖 무관한 항목/존재하지 않는 ID도 확인한다. 단순 JSON 스냅샷 재기록으로 대체하지 않는다.
2. 실제 제공될 validator 명령에서 정상 고정 입력은 성공하고, target 선언 변경·source 변경·해석 입력 누락은 실패 또는 명확한 부분/재검토 상태가 된다. 특히 occurrence 파일을 그대로 둔 target 변경을 검증한다. API 내부 검사만 고치고 CLI/사용 안내는 이전 경로를 가리키지 않게 한다.
3. 기존 broken reference·중복 ID·anchor·승인 메타데이터 부정 사례와 unknown 경계를 유지한다. 실제 사람 승인 여부나 업무 의미는 계속 별도다.
4. 새 결과를 두 출력 경로에서 재현한다. 기존 V1 관찰의 78×6·후보 5개/단순 그룹 동일·추가 의미 0을 보존하고 새 결과와 바뀐 부분을 구분한다. agent 제공 파일 목록/hash도 실제 새 경로와 맞춘다.
5. `pnpm check`와 `pnpm experiment`를 실행한다. 독립 리뷰의 원래 probe 결과를 고쳐서 성공으로 만들지 말고, 보완 버전에 대한 별도 회귀·재현 결과를 제시한다.

## 문서화와 인계

새 날짜별 인계에 R6/R7 각각의 전후 상태, 명령·재현·원시 증거·변경 범위·남은 한계를 남긴다. PROGRESS/REVIEW_CONTEXT/ROADMAP의 다음 경로를 실제 상태로 맞추고 중요한 계약 결정은 DECISIONS에 추가한다. README/ARCHITECTURE의 실험 구현과 제품 core 구분도 유지한다.

수정 후 다음 권고는 S2 reason 계약·고정 fixture/oracle와 A/B/C 제공 자료 동결이다. 아직 실제 앱 요구로 승인된 정책이 아니며 이 작업에서 비교 실행까지 확대하지 않는다. S2에는 평가 자료가 들어 있지 않은 별도 제공 묶음, 동등 정보 일반 문서, known-case pilot 한계를 명시해야 한다.

AGENTS/CONTRIBUTING에 따라 상태 확인·짧은 브랜치·검증·커밋·push·PR 자체 검토·필수 검사 충족 후 검증한 head로 merge·main 동기화까지 진행한다. 별도 업무 의미/제품 방향 결정이 필요할 때만 관찰·선택지·권고를 사용자에게 제시한다.
