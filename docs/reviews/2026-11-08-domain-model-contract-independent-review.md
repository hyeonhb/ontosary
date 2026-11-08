# S1 R6/R7 보완 독립 리뷰 — 2026-11-08

**R6/R7은 이번 지시·검증 범위에서 해결됐다. 추가 수정 필요 결함은 확인하지 않았으며, S1 보완 작업 완료를 인정한다.** 최종 목표와 방향을 유지한다. S2는 아직 미실행이고, 다음 단계의 큰 아키텍처·구현 범위는 사용자와 대화해 정한 뒤 착수한다. 이번 리뷰는 다음 단계 구현 지시가 아니다.

## 대상과 검증

[개발 보고](2026-11-08-domain-model-contract-fix.md), [PR #17](https://github.com/hyeonhb/ontosary/pull/17), main `f991fc72a7a9439aacd814078ce39c517ae84450`을 검토했다. 기준은 `2cd6e72`이며 V2의 입력 검사·탐색·검증·runner·제공 manifest·회귀 테스트와 실제 산출물을 대조했다. 제품 core/CLI·의존성·V1 코드/입력/원시 결과는 변경되지 않았다.

- `pnpm check`: 타입 검사·**10파일/174테스트**·예제 production build 통과. cache 조건부 CLI 회귀도 이번 환경에서 실행됐다.
- `pnpm experiment`: 기존 비교 **4/4** 통과.
- 기존 설치 cache에서 V2를 새 디렉터리에 실행했다. **비시간 15파일이 저장 결과와 byte 일치**, 그중 기존 12파일은 V1과도 동일했다. 설치/다른 플랫폼의 독립 재현은 아니다.
- 별도 probe로 **12개 시작 ID 전체의 실제 탐색 CLI**를 호출해 원래 모델의 incoming/outgoing 관계·선언 방향·근거 ID와 대조했다. 없는 ID는 exit 1이었다.
- **실제 standalone CLI 5상황**(정상, anchors-only, target 선언만 변경, 실제 scoped 설정 삭제, occurrence source 변경)을 별도 실행했다. 변조는 필요한 고정 파일만 복사한 임시 디렉터리에서 했으며 upstream cache는 그대로다.
- 제공 manifest의 **9개 파일 hash**를 확인했다. 이것은 S1 파일 목록의 정합성 검사이며 격리된 S2 배포 묶음의 검증은 아니다.

재현 증거: [독립 검사](evidence/2026-11-08-domain-model-v2-review.py), [결과 JSON](evidence/2026-11-08-domain-model-v2-review-results.json). 실행은 `python3 docs/reviews/evidence/2026-11-08-domain-model-v2-review.py <준비된 Vendure root> <새 V2 결과 디렉터리>`다.

## R6 · 해결

`v2/navigate.mjs`는 모델 내용을 바꾸지 않고 한 단계 incoming/outgoing 경로를 반환한다. `direction`과 `declaredEdge`로 조회 방향과 원래 관계 방향을 구분한다. order→branch, cancel-request→dialog-submit/cancel-transport/refund-also-cancels/dismiss, refund-request→refund-transport/refund-also-cancels/dismiss가 실제 CLI에서 확인됐다.

각 경로의 factRefs는 대상 모델 항목과 같고 모두 facts에 존재했다. order에서 refund-transport까지 무조건 전이 탐색하지 않으며 없는 ID도 연결을 만들지 않는다. 역방향 조회를 업무 관계의 대칭성이나 새로운 의미 발견으로 바꾸지 않았다. 문서·소비 함수·실행 결과가 이번 계약에서 일치한다.

## R7 · 해결

`v2/inputs.mjs`의 고정 원문/설정·Program 입력 hash/구성원·live 진단 검사를 새 runner와 standalone 검증기가 공유한다. 별도 검증은 anchorValid와 analysisInputsValid를 구분하고 둘 다 참일 때만 전체 valid/exit 0을 반환한다.

| 독립 실행 | anchorValid | analysisInputsValid | 결과 |
| --- | --- | --- | --- |
| 정상 고정 cache | true | true | valid=true, exit 0 |
| anchors-only | true | false | partial, exit 1, 재검토 |
| ModalService.fromComponent 선언만 변경 | true | false | target 파일 변경을 특정, exit 1, 재검토 |
| ontosary.scope.json 삭제 | true | false | 입력 누락, exit 1, 재검토 |
| order-detail source 변경 | false | false | 근거/입력 변경, exit 1, 재검토 |

입력 실패/미검사에서는 자동 역할 근거 468개·후보 5개·모델 12개를 보수적으로 재검토시켰다. source 변경은 수동 근거까지 포함해 staleFacts 473개였다. 정확한 영향 집합을 계산한다고 주장하지 않으며, 업무 의미나 실제 사람 승인을 인증하지도 않는다. V1의 `validation.json`은 과거 anchor 결과이고 최신 전체 판정은 `validation-v2.json`임을 안내한다.

## 방향성 및 지시 범위

이번 수정은 agent가 모델을 실제로 탐색하고 오래된 분석 전제를 구분하도록 만드는 보완이다. 최종 목표인 agent의 도메인 이해·수정 지원에 필요한 연결이며, 탐색 자체를 최종 제품 목표로 바꾸지 않았다.

모델 의미·78×6 context·후보 5개/단순 그룹 동일·새 의미 0·승인 지식 0이 보존됐다. R6의 조회 개선을 FCA의 성과로 집계하지 않았고, R7의 검증 성공을 업무 정책의 진실로 확대하지 않았다. H-O(모델의 agent 효과), H-F(FCA의 모델 구축 기여), 사람 작성/검토/유지 비용은 여전히 미검증이다.

역사적 V1 runner를 호출하므로 입력 검사가 중복되는 구현 비용은 보고서에 공개돼 있다. 현재 고정 실험에서는 재현 보존을 위한 선택으로 수용하며 이번 보완의 추가 결함으로 판단하지 않는다. cache가 없으면 일부 CLI 테스트가 skip하는 제약도 공개돼 있다. 이를 일반 환경 검증 성공이나 제품 아키텍처 확정으로 해석하지 않는다.

## 다음 단계 전에 정할 것

사용자 요청에 따라 **큰 아키텍처 고민은 새로운 단계의 구현 전에 대화로 결정**한다. 현재는 S1 보완 완료 판정까지이며 S2 fixture/oracle·자료 배포나 새 공통 계층을 구현하지 않았다. 다음 대화에서는 S2에서 검증할 변경 과업, 원문과 fixture의 경계, agent에게 제공할 모델/일반 문서/검증 경로의 범위를 구체화한다. 기존 reason 과업과 A/B/C 설계는 검토할 초안이다.

기존 core의 제한된 Gate 1 판정과 R1~R5 해결 범위는 유지한다. R6/R7은 닫되 모든 입력의 건전성·업무 의미 품질·agent 효용·제품화 완료를 주장하지 않는다. 과거 실패 증거는 그대로 보존한다.
