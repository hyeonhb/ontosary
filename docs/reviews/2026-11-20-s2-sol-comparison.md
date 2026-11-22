# Vendure 복합 수정 과업 · Sol 고정 입력 비교 (2026-11-20)

**Sol+A가 실행된 업무 검사에서 놓친 요구를 B나 C가 충족한 사례는 확인되지 않았다.** 첫 패치의 완전 성공은 A 4/6, B 5/6, C 5/6이었다. A의 두 실패는 모두 화면 동기화 패치 적용 단계에서 발생했다. B와 C는 각각 한 건 더 성공했지만, 어느 조건도 기존 Astra+A의 6/6에 도달하지 못했다. Sol은 18건 모두 요청 모델 기준이며 서버 모델명은 미확인이다.

## 패치와 검사에서 갈린 지점

| 과업 | 반복 | Sol+A | Sol+B | Sol+C |
| --- | ---: | --- | --- | --- |
| 잔여 수량 | 1 | [완전 성공](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/20d851b3c2d2/submission/grade.json) | [적용 실패](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/d4f89b80b202/submission/grade.json) | [완전 성공](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/e13964e9e2a0/submission/grade.json) |
| 잔여 수량 | 2 | [완전 성공](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/87ff4baf236f/submission/grade.json) | [완전 성공](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/2a40e094921e/submission/grade.json) | [완전 성공](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/14a23169606a/submission/grade.json) |
| 잔여 수량 | 3 | [완전 성공](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/8193fa129e6d/submission/grade.json) | [완전 성공](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/b2bbe0d63a1b/submission/grade.json) | [완전 성공](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/271942e40574/submission/grade.json) |
| 화면 동기화 | 1 | [적용 실패](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/a333c8080d58/submission/grade.json) | [완전 성공](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/8b825862e51c/submission/grade.json) | [완전 성공](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/7f2954014706/submission/grade.json) |
| 화면 동기화 | 2 | [완전 성공](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/002d2edb2c6b/submission/grade.json) | [완전 성공](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/39644b13a1bc/submission/grade.json) | [완전 성공](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/26aaeebe25dc/submission/grade.json) |
| 화면 동기화 | 3 | [적용 실패](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/b6230cce66ea/submission/grade.json) | [완전 성공](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/c810abbe1fa8/submission/grade.json) | [타입 실패](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/40e15d2a65cf/submission/grade.json) |

**화면 동기화 첫 반복.** A는 대화상자를 닫을 때 흐름을 끝내고 환불 뒤 재조회하는 변경을 제시했지만, 주문 상세 화면 561행에서 패치 적용이 거부됐다. B와 C의 패치는 적용됐고 각각 24/24였다. 두 제출 모두 선행 취소가 거절되면 취소 요청 하나만 보냈으며, 그 결과가 결정된 뒤 이력과 주문을 한 번씩 갱신했다. 취소 뒤 환불 두 건이 성공하는 경우에는 세 번째 결과가 온 뒤에만 갱신했다. A가 실제로 이 동작을 어겼는지는 측정할 수 없다. [A 패치](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/attempts/a333c8080d58/a333c8080d58/answer.txt) · [A 적용 오류](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/a333c8080d58/submission/grade.json) · [B 패치](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/attempts/8b825862e51c/8b825862e51c/answer.txt) · [B 관측](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/8b825862e51c/submission/evaluation.json.gz) · [C 관측](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/7f2954014706/submission/evaluation.json.gz)

**수량과 취소 선택.** 수량 과업은 A만으로 3/3이었다. 첫 반복 A는 여러 결제의 이력을 합산해 5개 입력을 잔여량 3개로 맞췄다. 사용자가 취소 선택을 해제한 뒤 다시 편집한 사례에서는 수량을 2개로 제한하고 취소 선택을 해제한 채로 제출했다. C도 같은 검사에 통과했다. B의 첫 반복은 환불 대화상자 124행에서 적용이 거부됐다. [A 수량 패치](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/attempts/20d851b3c2d2/20d851b3c2d2/answer.txt) · [A 관측](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/20d851b3c2d2/submission/evaluation.json.gz) · [C 관측](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/e13964e9e2a0/submission/evaluation.json.gz)

**화면 동기화 셋째 반복.** A는 주문 상세 화면 563행에서 적용에 실패했다. B는 24/24였다. C는 적용됐지만 취소 결과에서 `cancelOrder.message`를 읽는 줄이 타입 검사 TS2339로 실패했다. 그 분기에서 TypeScript가 `message` 없는 주문 타입을 배제할 수 없어 업무 검사를 실행하지 않았다. [C 원패치](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/attempts/40e15d2a65cf/40e15d2a65cf/answer.txt) · [C 타입 진단](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/40e15d2a65cf/submission/evaluation.json.gz) · [B 관측](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/c810abbe1fa8/submission/evaluation.json.gz)

전체 18건 중 완전 성공 14건, 패치 적용 실패 3건, 타입 실패 1건이었다. 실행된 업무 검사 실패와 인프라 중단은 각각 0건이다. 같은 과업·반복의 A–B, A–C 총 12쌍 중 양쪽에서 업무 검사를 실행한 7쌍은 모든 사례가 일치했다. 나머지 5쌍은 한쪽 이상의 업무 관측이 없다. B/C의 추가 성공을 특정 업무 지식의 인과 효과로 해석하기에는 근거가 부족하다. [짝별 관측 가능 사례와 비교표](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/comparison.json)

## 실패를 포함한 비용과 Astra+A 비교

| 모델·조건 | 잔여 수량 | 화면 동기화 | 완전 성공 | 입력 토큰 | 출력 토큰 | 누적 초 | 표준 단가 환산 크레딧 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Astra+A | 3/3 | 3/3 | 6/6 | 226,482 | 3,827 | 108.047 | 49.1234 |
| Sol+A | 3/3 | 1/3 | 4/6 | 226,482 | 11,004 | 245.754 | 14.0751 |
| Sol+B | 2/3 | 3/3 | 5/6 | 388,386 | 11,149 | 246.042 | 22.2066 |
| Sol+C | 3/3 | 2/3 | 5/6 | 415,338 | 11,002 | 244.817 | 23.5174 |

Sol 18건의 총 입력은 1,030,206토큰, 출력은 33,155토큰, 누적 시간은 736.613초였다. 토큰·시간 결측, 시간 초과, 토큰·응답 바이트 예산 초과는 각각 0건이다. 출력에 포함된 추론 토큰은 19,931개다.

| Sol 내부 비교 | 완전 성공 차이 | 추가 성공 1건당 입력 차이 | 출력 차이 | 누적 초 차이 | 환산 크레딧 차이 |
| --- | ---: | ---: | ---: | ---: | ---: |
| B−A | +1 | +161,904 | +145 | +0.288 | +8.1315 |
| C−A | +1 | +188,856 | −2 | −0.937 | +9.4423 |

두 비교 모두 예정된 6건의 총비용 차이를 추가 성공 1건으로 나눴다. C의 음수는 C 여섯 세션의 출력·시간 합계가 A보다 조금 작았다는 뜻이다.

| Astra+A 대비 | 완전 성공 차이 | 입력 토큰 차이 | 출력 토큰 차이 | 누적 초 차이 | 환산 크레딧 차이 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Sol+A | −2 | 0 | +7,177 | +137.707 | −35.0483 |
| Sol+B | −1 | +161,904 | +7,322 | +137.995 | −26.9169 |
| Sol+C | −1 | +188,856 | +7,175 | +136.770 | −25.6060 |

과업별로 같은 3/3에 도달한 경우의 비용도 다르다. **잔여 수량은 Sol+A만으로** 입력 113,217·출력 4,602토큰(6.8114 환산 크레딧), Sol+C는 207,645·4,396토큰(11.4813)이었다. 같은 과업의 Astra+A는 113,217·1,514토큰(24.1574)이었다. **화면 동기화는 Sol+B만** 3/3이었고 입력 194,217·출력 7,486토큰(11.5824)이었다. Astra+A는 113,265·2,313토큰(24.9660)이었다. 두 과업 합계 6/6을 달성한 Sol 조건이 없어 그 품질에 도달하는 데 드는 총비용은 이번 실행에서 관측되지 않았다. [Sol 시도별 원자료](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/summary.json) · [Astra 기준 원자료](../../experiments/domain-model/s2/results/2026-11-20-complex-comparison/score/summary.json)

환산 기준일은 2026-11-20이다. OpenAI의 ChatGPT 로그인 Codex Standard 공개 단가에서 100만 토큰당 일반 입력·캐시 입력·출력은 Sol 50·2.5·250, Astra 200·10·1,000크레딧이다. 입력 중 캐시 적중량을 분리해 해당 단가를 곱하고 출력은 한 번만 더한다. 양쪽 모두 캐시 적중·쓰기 토큰은 0이었다. 표의 값은 요청 모델의 공개 단가를 적용한 추정치다. 구독에서 실제 차감된 크레딧이나 금액 절감은 확인할 수 없다. [OpenAI Codex 요금표](https://learn.chatgpt.com/docs/pricing#token-rates)

## 실행 조건과 재현

기준 리비전은 `198bf52`, 첫 호출 전 Sol 계약과 사전 검사를 고정한 커밋은 `ac71ba7`이다. Vendure 원본 `534e6003534f74761e82de1b8c6061cba89945d1`, 과업·조건·반복 순서, 참가자용 여섯 패킷의 바이트, v3 평가기와 회당 예산은 Astra 비교와 같다. ChatGPT 로그인 CLI에 `gpt-6.2-sol`·`medium`을 요청했고 로컬 사전 검사에서 참가자 도구 0개를 확인했다. [실행 지시](2026-11-20-s2-sol-comparison-instructions.md) · [Sol 계약과 사전 검사](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/) · [Astra 독립 리뷰](2026-11-20-s2-complex-comparison-independent-review.md)

첫 응답을 봉인한 뒤 서버 모델명이 없어 일시 중단했다. 사용자가 모델명 누락은 ‘서버 미확인’으로 표시하고 명시적 불일치에서 중단하도록 승인했다. 기존 첫 응답을 보존한 채 남은 17회만 수집했다. 18건 모두 정상 종료했고 서버 모델명은 18건 모두 미확인이다. 따라서 이 보고서에서 Sol은 요청 모델을 뜻한다. 원응답을 모두 봉인한 뒤 새 원본 복사본에 각각 적용했고, 추가 참가 호출이나 수동 패치 보정은 0회였다. [첫 응답과 모델 확인 상태](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/attempts/) · [시도별 사용량과 최종 판정](../../experiments/domain-model/s2/results/2026-11-20-sol-comparison/score/summary.json)

공통 입력에서 확인한 업무 과업은 두 개이며 각 과업·조건의 표본은 세 개다. B/C 자료의 구조적 대응은 확인했으나 업무 의미 동등성에 대한 사람의 최종 검토는 남아 있다. 도구를 사용하는 저장소 탐색, 자료 작성·유지에 드는 사람의 비용, FCA의 기여는 여기서 측정하지 않았다.

준비된 macOS 전체 소스와 평가 환경에서 다음 명령을 실행한다. 첫 검증은 Sol 봉인 응답으로 등급·사례별 관측·비용표와 Astra+A 대비표를 재생성한다. 둘째 검증은 보존된 Astra 18건을 재채점한다. 두 경로 모두 참가 모델을 호출하지 않는다. [재현 검증기](../../experiments/domain-model/s2/verification/2026-11-20-complex-comparison/verify.py) · [비교표 계산](../../experiments/domain-model/s2/verification/2026-11-20-sol-comparison/comparison.py)

```sh
pnpm s2:build
python3 -B experiments/domain-model/s2/verification/2026-11-20-complex-comparison/verify.py work/s2-contract-workspace-a/source work/s2-fixed-pilot/env --sol
python3 -B experiments/domain-model/s2/verification/2026-11-20-complex-comparison/verify.py work/s2-contract-workspace-a/source work/s2-fixed-pilot/env
```
