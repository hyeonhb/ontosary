# Vendure 부분 출고 · 두 agent 간 첫 인계 결과

**작성자가 남긴 기록을 후속 agent가 변경 위치와 회귀 사례 선택에 재사용했다.** 작성자는 일반 검색으로 두 판단을 먼저 찾았고 Ontosary `scan`은 위치를 재확인하는 데 사용했다. 한 차례의 대리 인계에서 관찰한 결과다. 사람의 첫 사용성·소요 시간, 조직의 업무 정책 승인, 인계 기록이 없을 때와의 비용 차이는 미측정이다. [작성자의 첫 인계 기록](../../experiments/first-use/partial-fulfillment/results/2026-11-27/HANDOFF.md) · [후속 agent의 첫 제안](../../experiments/first-use/partial-fulfillment/results/2026-11-27/PROPOSAL.md)

## 두 제출을 원문과 대조한 결과

| 검토 질문 | 판정과 근거 |
| --- | --- |
| 두 업무 판단을 재확인할 수 있는가? | 충족. 작성자는 주문 단위의 버튼 노출·활성화와 창 안의 라인별 최대 수량을 구별했다. 일반 주문에서 취소되지 않은 출고의 합계가 주문 수량보다 작은 행이 있어야 하고 미정산 변경·미결제 차액이 없으며 허용된 다음 상태가 있어야 한다. 창에서는 같은 미출고 수량에 상품별 유효 재고 추적 설정을 적용한다. 기록의 상대 경로 9개가 전달 사본의 실제 파일과 줄을 가리킨다. 업무 의도는 추정으로 구분했다. |
| 기록이 후속 판단에 실제 쓰였는가? | 충족. 후속 agent는 시작 안내 다음에 인계 기록을 읽었다. “주문에서는 시작할 수 있지만 모든 행의 상한이 0일 수 있다”는 주장을 창에 안내를 두고 상세 버튼을 보존할 근거로 명시했다. 회귀 사례도 작성자의 5개·3개 주문과 Pending·Cancelled 수량을 그대로 사용하고 B의 재고 추적만 바꾸는 대조를 제시했다. |
| 후속 제안은 소스와 맞는가? | 타당하다. 제안은 비동기 설정 수신 뒤 계산된 `max`에 양수가 있는지 확인한다. 사용자 선택량이 모두 0이거나 handler 양식이 무효여서 제출할 수 없는 경우, 로딩 중인 빈 상태를 각각 구별한다. agent는 주문 조회 필드, 창을 닫은 뒤 생성 API를 부르는 위치, `markForCheck()`와 번역 리소스를 직접 찾았다. 서버 재검증은 작성자도 이미 적었고 후속 agent가 다시 확인한 내용이다. 제출물은 제안 단계로, 안내 문구의 실제 렌더링은 미측정이다. |
| Ontosary의 구체적 기여는 무엇인가? | 작성자의 최초 발견은 `rg` 검색과 TS·HTML 원문 읽기였다. 이후 `scan` 출력으로 출고 창의 수량 계산(64·73행)과 제출 검사(84행), 주문 상세의 진입 검사(310행)와 열기(407행)를 재확인했다. 후보 생성 전 `concepts`가 상한에서 종료되어 FCA 후보의 품질과 인계 기여는 미측정이다. |

주문 상세 템플릿은 Aggregate를 제외하고 상세 메서드가 버튼 활성화를 결정한다. 출고 창은 설정 수신 후 각 행의 초기 선택량과 상한을 설정한다. 선택량 합계·각 상한·양식 유효성은 생성 버튼을 제어한다. 후속 제안의 “재고 부족”과 “미출고 수량 없음”은 이 창이 가진 정보로 설명하며, 서버에서 실제 생성 가능한지까지 단정하지 않는다. [상세 버튼](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.html#L32-L39) · [활성화와 결제 조건](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts#L310-L355) · [상한 계산과 제출 검사](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/admin-ui/src/lib/order/src/components/fulfill-order-dialog/fulfill-order-dialog.component.ts#L38-L98) · [주문 조회 필드](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/admin-ui/src/lib/core/src/data/definitions/order-definitions.ts#L126-L139) · [창 결과와 API 호출](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts#L407-L425)

### 주문 예 검산

작성자 예에서 A의 미출고 수량은 5 − (Shipped 2 + Pending 1) = 2다. Cancelled 1은 제외한다. B도 3 − 1 = 2다. 작성자는 실제 TS 메서드를 추출하고 결제 합산 및 유효한 양식을 대역으로 둬 9개 단언을 검사했다. 검토자가 같은 명령을 다시 실행한 뒤 후속 제안의 대조도 확인했다. 아래의 안내 열은 제안대로 구현했을 때의 기대값이다. 나머지 열은 기존 메서드에서 관측했다. [작성자가 실행한 예](../../experiments/first-use/partial-fulfillment/results/2026-11-27/author-example.cjs) · [사전 검토 기준](2026-11-26-first-use-partial-fulfillment-preparation.md#검토자용-기준-소스와-주문-예)

| 전액 결제된 부분 출고 주문의 조건 | 창 진입 | 상한 A / B | 기존 제출 허용 | 제안된 안내 |
| --- | --- | --- | --- | --- |
| 원래 예. A 추적·재고 1, B 미추적·재고 0 | 가능 | 1 / 2 | 예 | 숨김 |
| A와 B 모두 추적·재고 0 | 가능 | 0 / 0 | 아니오 | 재고 부족 |
| 바로 위에서 B만 미추적으로 전환 | 가능 | 0 / 2 | 예 | 숨김 |
| B 상한 2에서 사용자가 선택량만 0으로 변경 | 가능 | 0 / 2 | 아니오 | 숨김 |
| B 선택량 2에서 handler 양식만 무효 | 가능 | 0 / 2 | 아니오 | 숨김 |

## 전달과 비용

승인된 로그인 경로에서 Codex CLI `0.171.0-alpha.13.2`로 역할마다 `codex exec --ephemeral` 새 프로세스와 새 대화를 시작했다. 두 역할의 요청 설정은 `gpt-6.2-sol` / `medium`이었다. 서버가 반환한 모델명은 로그에서 독립 확인하지 못했다. resume·fork 없이 작성 완료 뒤 후속 세션을 시작했고 웹 검색·앱·플러그인·메모리를 껐다. 작성자에게는 전달 디렉터리 쓰기를, 후속 agent에게는 읽기 전용 작업을 지정했다. 참가자에게 해당 디렉터리만 사용하도록 안내했고 관측한 명령은 공개 리뷰나 이전 세션을 조회하지 않았다. [실행 지시](2026-11-27-first-use-partial-fulfillment-run-instructions.md) · [요청 설정·명령 이벤트·CLI 사용량](../../experiments/first-use/partial-fulfillment/results/2026-11-27/receipts.json)

Vendure 리비전은 `534e6003534f74761e82de1b8c6061cba89945d1`, 작성자 도구 리비전은 `35296d436a63f9c72739859c22b1aded4bc9f57a`다. 기존 `prepare.sh`와 역할별 `START.md`를 그대로 사용했다. 진행자는 작성자 사본에 설치·빌드를 완료하고 그 사실만 알렸다. 조사 중 도움과 교정은 0회였다. 후속 입력은 새 Vendure 소스, 후속 요청, 최초 `HANDOFF.md`뿐이었다. 전달본과 최초 제출의 SHA-256이 일치했고 두 사본의 Vendure 원본 4,735개 파일도 각각 고정 Git blob과 일치했다. 상대 소스 링크는 역할별 사본을 기준으로 한다. 작성자의 별도 관찰은 후속 입력에서 제외했다. [준비 방식](2026-11-26-first-use-partial-fulfillment-preparation.md#누구에게-무엇을-전달하는가) · [작성자의 진행자용 관찰](../../experiments/first-use/partial-fulfillment/results/2026-11-27/author-observations.md)

| 역할 | 실제 경과 | 입력 토큰 | 그중 캐시 입력 | 출력 토큰 | 그중 추론 출력 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 작성 | 122.851초 | 267,804 | 194,176 | 5,121 | 386 |
| 후속 | 83.363초 | 145,946 | 97,920 | 2,642 | 77 |
| 합계 | 206.214초 | 413,750 | 292,096 | 7,763 | 463 |

- **준비자 비용.** 작성자 자료 추출 0.991초, Ontosary 잠금 설치·빌드 2.237초, Vendure 잠금 설치·common 빌드 11.239초였다. 두 설치 작업은 병행했다. 후속 자료 추출은 1.002초였다. 참가 시간에서 제외했다.
- **작성 경과.** 프로세스 시작 기준 10.712초에 최초 업무 검색 결과, 17.270초까지 두 주요 원문을 읽은 이벤트를 받았다. 병행한 `scan`은 7.485초, `concepts`는 7.184초였다. 후자는 4,097객체 / 7,033속성에서 한도 128 / 64로 종료했다. 번역·생성 타입 검색 결과는 별도로 추적하지 않았다고 보고했다. 73.071초에 주문 예 검사, 105.922초에 최초 파일 작성, 111.801초에 링크 9개 확인이 끝났다. 설정 확인·조사·집필에만 각각 쓴 시간은 따로 계측하지 않았다.
- **후속 경과.** 12.865초에 인계 기록 읽기 완료, 24.370초에 창 TS·HTML 원문 확인, 52.882초에 마지막 소스 조회 완료 이벤트를 받았다. 일부 추정한 번역·타입 파일 경로가 없어 파일 목록으로 다시 확인했다. 참가자는 시간을 잰 조회 배치 5개의 합을 471ms로 보고했다. 이 값은 제안 작성과 추가 탐색 전체 시간이 아니며, 진행자 계측은 위 이벤트 시각과 전체 경과까지다.
- **해석 범위.** 시간은 CLI 시작부터 종료까지의 실측이고 토큰은 역할별 `turn.completed.usage`다. 청구 금액은 미측정이다. 서로 다른 역할 각 1회이고 무기록 대조군은 없다. 사람의 첫 사용, 일반적인 속도 개선 또는 FCA 효과로 확장할 수 없다. 제품·Vendure 패치와 배송비 S2 실험은 이번 실행에 포함되지 않았다.

**모델 호출 없이 수치 재확인.** 준비 보고서의 명령으로 작성자 디렉터리를 만들고 두 설치 블록을 실행한 뒤, 저장소 루트에서 아래를 실행한다. 첫 두 제출의 지문과 세션별 원시 사용량은 위 실행 기록에 있다.

```sh
result="$PWD/experiments/first-use/partial-fulfillment/results/2026-11-27"
(cd "$delivery/author" && node < "$result/author-example.cjs")
shasum -a 256 "$result/HANDOFF.md" "$result/PROPOSAL.md"
```
