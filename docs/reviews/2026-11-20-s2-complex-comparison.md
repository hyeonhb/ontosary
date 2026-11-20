# Vendure 복합 수정 과업 A/B/C 비교 · 2026-11-20

**첫 패치의 완전 성공은 A 6/6, B 4/6, C 6/6이었다.** 공통 소스와 요구만 받은 A가 두 과업의 세 반복을 모두 통과했다. B에서 줄어든 두 건은 화면 동기화 패치가 적용되지 않은 경우다. C는 A와 성공 수가 같았다. 이 표본에서 B와 C 모두 추가 성공이 없어 추가 성공당 비용은 산출할 수 없다.

## 첫 제출과 비용

| 조건과 제공 자료 | 완전 성공 / 예정 | 입력 토큰 | 출력 토큰 | 경과 시간 합계(초) |
| --- | ---: | ---: | ---: | ---: |
| A · 공통 소스·요구 | 6/6 | 226,482 | 3,827 | 108.047 |
| B · 구조화 뷰 추가 | 4/6 | 388,386 | 3,888 | 117.742 |
| C · 서술 문서·근거 추가 | 6/6 | 415,338 | 3,924 | 112.960 |

| 과업 | 반복 | A | B | C |
| --- | ---: | --- | --- | --- |
| 잔여 수량 | 1 | [성공](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/score/7191b15de681/submission/grade.json) | [성공](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/score/febb90d181da/submission/grade.json) | [성공](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/score/dca25caa663b/submission/grade.json) |
| 잔여 수량 | 2 | [성공](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/score/549281da9b3b/submission/grade.json) | [성공](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/score/8d3f8fb5ac5a/submission/grade.json) | [성공](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/score/cf7b4cb0ca6a/submission/grade.json) |
| 잔여 수량 | 3 | [성공](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/score/7a6839cc8fcf/submission/grade.json) | [성공](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/score/3b500191af52/submission/grade.json) | [성공](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/score/0efd37761e96/submission/grade.json) |
| 화면 동기화 | 1 | [성공](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/score/aa7cad93ba82/submission/grade.json) | [패치 적용 실패](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/score/0ce09bb5cb1c/submission/grade.json) | [성공](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/score/465a0e1eb892/submission/grade.json) |
| 화면 동기화 | 2 | [성공](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/score/070748728096/submission/grade.json) | [성공](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/score/b9772ea92abd/submission/grade.json) | [성공](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/score/7c8e9b39ca5a/submission/grade.json) |
| 화면 동기화 | 3 | [성공](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/score/edf60fb1a0a5/submission/grade.json) | [패치 적용 실패](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/score/633350eaf92a/submission/grade.json) | [성공](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/score/2abff69c1b26/submission/grade.json) |

| 비교 | 완전 성공 차이 | 입력 차이 | 출력 차이 | 경과 시간 차이(초) | 추가 성공 1건당 입력 / 출력 / 초 |
| --- | ---: | ---: | ---: | ---: | --- |
| B−A | -2 | 161,904 | 61 | 9.695 | 추가 성공 없음 |
| C−A | +0 | 188,856 | 97 | 4.913 | 추가 성공 없음 |

18개 독립 세션에서 첫 응답 18개를 봉인한 뒤 전체 소스로 채점했다. 표의 입력·출력과 경과 시간에는 실패한 제출도 포함한다. 총 입력 1,030,206토큰, 출력 11,639토큰, 세션 경과 시간 합계 338.749초였다. 입력·출력·시간 누락과 회당 예산 초과는 각각 0건이다. B는 A보다 입력을 71.5%, C는 83.4% 더 사용했다. 캐시 입력은 0이고 추론 출력 298토큰은 출력 합계에 포함된다. 모델 작성·사람의 검토·유지 시간은 미측정이다. [시도별 사용량과 전체 집계](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/score/summary.json) · [첫 응답·이벤트·봉인](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/attempts/)

## 소스와 실행에서 확인한 차이

**잔여 수량.** 원래 대화상자는 실패하지 않은 환불 이력으로 편집 가능 여부를 정하면서, 수량 편집 시에는 입력값을 그대로 저장했다. 주문 당시 6개 중 3개가 이미 환불된 항목에 5개를 입력한 사례에서 원본은 취소 요청에도 5개를 보냈다. A의 첫 반복은 같은 이력으로 상한을 계산해 선택 수량과 취소 요청을 3개로 맞췄다. 이 사례와 환불 전용 선택 보존을 포함해 수량 제출 9개 모두 8/8을 통과했다. [Vendure 편집 메서드](https://github.com/vendure-ecommerce/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts#L127-L140) · [원본 관측](../../experiments/domain-model/s2/results/2026-11-19-complex-grading-v3/controls/quantity/baseline/evaluation.json.gz) · [A 첫 제출의 관측](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/score/7191b15de681/submission/evaluation.json.gz)

**화면 동기화.** 원본에서는 취소 뒤 두 결제를 환불하면 취소 응답 직후와 마지막 환불 응답 뒤에 이력·주문을 각각 갱신했다. 반면 선행 취소가 거절되면 이력만 갱신했다. A의 첫 반복은 기존 `refetchOrder`를 재사용했고, C의 첫 반복은 이력 신호와 주문 재조회를 수행하는 메서드를 추가했다. 두 제출 모두 혼합 성공에서 세 번째 응답 뒤에만 갱신했고, 취소 거절에서는 환불 요청 없이 이력과 주문을 각 한 번 갱신했다. 적용된 화면 제출 7건의 결과는 모두 24/24였다. [Vendure 혼합 흐름](https://github.com/vendure-ecommerce/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts#L601-L690) · [원본 관측](../../experiments/domain-model/s2/results/2026-11-19-complex-grading-v3/controls/refresh/baseline/evaluation.json.gz) · [A 패치](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/attempts/aa7cad93ba82/aa7cad93ba82/answer.txt) · [C 패치](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/attempts/465a0e1eb892/465a0e1eb892/answer.txt) · [C 실행 관측](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/score/465a0e1eb892/submission/evaluation.json.gz)

**B의 두 실패.** 첫째와 셋째 반복의 원응답은 각각 주문 상세 화면 소스 634행과 635행에서 패치 적용에 실패했다. 실행기는 고정된 방식으로 hunk 줄 수를 다시 계산한 뒤에도 패치를 적용할 수 없었다. 이 두 제출은 타입·업무 동작을 관측할 수 없었다. 둘째 반복은 같은 구조화 뷰를 받고 적용·타입·동작 검사를 모두 통과했다. 따라서 관측된 조건 간 성공 차이는 제출 패치의 적용 단계에서 발생했다. [첫째 적용 오류](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/score/0ce09bb5cb1c/submission/grade.json) · [셋째 적용 오류](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/score/633350eaf92a/submission/grade.json) · [둘째 실행 관측](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/score/b9772ea92abd/submission/evaluation.json.gz)

## 해석 범위

독립 반복은 조건마다 과업별 3회이고 업무 과업은 2개다. 두 과업 모두 A가 이미 3/3을 통과해 이 표본의 성공 수에는 개선 여지가 없었다. 구조화 뷰 때문에 패치 적용이 실패했다거나, 다른 업무에서도 도메인 지식이 불필요하다고 결론내릴 근거는 부족하다. B/C 자료는 1,511개 값과 30개 소스 인용의 대응을 확인했다. 두 표현이 업무상 같은 의미를 전달하는지에 대한 사람의 최종 검토는 남아 있다. FCA의 모델 구축 기여는 이 실행의 측정 대상에 포함되지 않는다. [준비 독립 리뷰](2026-11-19-s2-complex-grading-v3-independent-review.md)

## 봉인 응답으로 결과 재현

기준 커밋 `ccdbdb3`에서 승인된 기존 ChatGPT 로그인 CLI로 `gpt-6.2-astra`, 추론 강도 `medium`을 사용했다. 기존 실행 흔적은 준비 단계의 합성 대조임을 확인했다. 두 과업의 실제 입력 지문·도구 0개를 로컬 사전 검사로 대조한 뒤, 동결 순서대로 18회 수집했다. 중단·재호출·수동 패치 보정은 0건이다. 평가기는 도구 없는 참가 세션 밖에서 전체 소스로 v3 타입·동작 검사를 실행했다. [승인 지시](2026-11-20-s2-complex-comparison-instructions.md) · [계약](../../experiments/domain-model/s2/results/2026-11-19-complex-grading-v3/contract.json) · [실행 직전 점검](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/preflight/)

준비 때 사용한 전체 Vendure 원본과 macOS 평가 환경에서 아래 명령을 실행한다. 검증기는 패킷을 다시 조립하고, 예정된 18개 ID·배정·봉인을 확인한 뒤 `score`만 실행한다. 시도별 등급·압축된 관측 JSON·비용표를 공개 기록과 대조한다. [환경 복원 기록](2026-11-18-s2-fixed-input-pilot.md) · [재현 검증기](../../experiments/domain-model/s2/verification/2026-11-20-complex-comparison/verify.py)

```sh
pnpm s2:build
python3 -B experiments/domain-model/s2/verification/2026-11-20-complex-comparison/verify.py work/s2-contract-workspace-a/source work/s2-fixed-pilot/env
```
