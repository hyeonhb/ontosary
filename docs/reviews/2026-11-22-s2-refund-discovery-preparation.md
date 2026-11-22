# Vendure 환불 잔액 변경의 영향 범위 탐색 비교 준비

**탐색과 최종 수정 모두 측정 가능하다.** 고정 Vendure Admin UI에서 A·B·C 모의 세션이 업무 요청으로 시작해 수정 전에 같은 판정표로 읽을 수 있는 근거를 제출했다. 독립 작업 사본에서 회수한 정상 수정은 세 조건 모두 11/11이었다. 전액 환불 주문에서 문구만 바꾼 대조는 취소로 표시됐지만 클릭하면 환불 대화상자를 열었다. 참가 모델 호출은 0회이며 이 결과에서 Ontosary의 효과나 Sol의 성공률은 추정할 수 없다. [모의 작업 원문](../../experiments/domain-model/s2/results/2026-11-22-refund-discovery/traces.json) · [전체 관측값](../../experiments/domain-model/s2/results/2026-11-22-refund-discovery/results.json)

## 참가자가 받은 것과 찾은 것

참가자용 업무 요청은 “관리자 주문 상세에서 고객에게 돌려줄 금액이 전혀 남지 않은 주문은 환불로 안내하지 말고 취소 절차로 연결해 주세요. 환불할 금액이 남은 주문에서는 기존 취소·환불 동작을 유지하고, 원래 취소할 수 없던 주문에 새로 취소를 허용하지 마세요.”다. 첫 입력에는 이 문장과 리비전·범위·해당 조건의 도구 및 제출 방법만 들어간다. 일반 소스와 문서는 Vendure v3.5.0의 4,735개 파일 전체다. 전체 경로와 파일별 SHA-256을 기존 원본 manifest와 대조했다. [공개 입력 생성 및 동작 프로토콜](../../experiments/domain-model/s2/trial/discovery/session.py) · [Vendure 고정 리비전](https://github.com/vendurehq/vendure/tree/534e6003534f74761e82de1b8c6061cba89945d1)

| 조건 | 기본 소스 검색 / 읽기 | 추가 자료 목록 / 검색 / 읽기 | 수정 전 제출 시점 | 전체 작업 수 | 전체 도구 응답 bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| A · 일반 검색 | 6 / 7 | 0 / 0 / 0 | 13번째 | 19 | 18,656 |
| B · 모델 추가 | 6 / 7 | 1 / 2 / 2 | 18번째 | 24 | 21,512 |
| C · 서술 문서 추가 | 6 / 7 | 1 / 2 / 2 | 18번째 | 24 | 24,524 |

소스 읽기 7회 중 1회는 제출 후 수정에 사용했다. 모의 참가자는 첫 일반 검색에서 반환된 템플릿 경로와 클릭 바인딩을 따라갔다. B는 구조화된 개념 및 근거 뷰를, C는 서술과 부록을 추가 조회했다. 세 모의 참가자의 탐색 제출은 같은 내용으로 봉인됐고 4/4였다. 동일한 행동에 자료 조회를 추가한 모의 시나리오이므로 위 비용 차이로 실제 참가자의 탐색 전략을 비교할 수는 없다.

공통 호스트는 배정된 이름공간의 텍스트만 목록·검색·줄 단위로 반환한다. 잘못된 접근, 첫 제출 전 수정, 재제출, 종료 후 수정은 거부됐다. 참가자가 호출하는 셸이나 파일시스템 도구는 없다. 기존 Codex CLI의 Sol·medium 요청을 **로컬 HTTP 수신기**에서 조건별 첫 입력과 작업 3개 이후 입력으로 확인했다. 여섯 요청에서 기본 도구는 비었고 사용자 본문은 해당 조건의 공개 입력과 해당 세션의 이력에 일치했다. 수신기는 모두 400으로 끝냈다. 실제 제공자의 응답·usage·서버 모델명은 이번 측정 범위 밖이다. [요청 대조](../../experiments/domain-model/s2/results/2026-11-22-refund-discovery/wire.json)

### 변경 전 모델과 서술 자료

11월 10일 동결본의 B JSON 조회 결과 68개와 C 문서 4개를 그대로 사용했다. B의 `item-9`와 C guide의 같은 항목은 메뉴 게이트가 수동 HTML 근거이며 서버 허용 정책이 아님을 표시한다. B의 `item-5`와 C guide 129–137행은 분기와 주문·결제의 관계, PaymentAuthorized·active·정산 결제 없음 예외를 담는다. 둘 다 agent가 기록한 pending-review 후보다. B fact-0/1/2와 C observations 6–25행, 각각의 evidence-0/1/2가 메뉴 조건·클릭·Settled 존재 확인의 원래 파일과 좌표로 이어진다. 1,511개 말단 값과 대응 C 구간의 지문을 대조한 뒤 이 과업의 의미를 별도로 확인했다. [B 원본](../../experiments/domain-model/s2/results/2026-11-10-trial-preparation/B/views/) · [C 관찰](../../experiments/domain-model/s2/results/2026-11-10-trial-preparation/C/observations.md) · [C 근거 부록](../../experiments/domain-model/s2/results/2026-11-10-trial-preparation/C/evidence.md)

어느 자료도 문구 선택에서 `getRefundablePayments`의 결제별 잔액과 Failed 제외 규칙까지 연결하지 않는다. 메뉴 근거 발췌는 노출 조건이고 분기 근거 발췌는 메서드 선언이다. 새 정책이나 잔액 관계를 보충하지 않았으므로 세 조건 모두 실제 소스를 읽어 나머지 관계를 확인해야 한다.

### 발견을 판정한 사례

노출, 문구, 클릭 후 절차·예외, 결제별 잔액에 각각 1점을 둔다. 리뷰어는 자료 조건과 최종 코드를 가린 상태에서 봉인 답안의 설명과 고정 소스의 줄·심볼을 대조한다. 파일 목록만 적은 답은 0/4, 클릭 절차가 빠진 답과 Failed를 차감한 답은 각각 3/4다. 결제 자격은 UI에서, 차감 규칙은 동등한 서버 계산에서 찾아 연결한 답도 4/4로 인정한다. [판정 기준과 여섯 사례](../../experiments/domain-model/s2/trial/discovery/rubric.md)

## 변경 소스에서 관측한 결과

| 독립 작업 사본 | 타입 검사 | 메뉴 문구·노출 | 클릭 후 절차·숨김 | 둘 다 통과 |
| --- | --- | ---: | ---: | ---: |
| 원본 | 통과 | 9/11 | 9/11 | 9/11 |
| 문구만 수정 | 통과 | 11/11 | 9/11 | 9/11 |
| 템플릿과 클릭이 새 잔액 함수를 사용 · A/B/C 각각 | 통과 | 11/11 | 11/11 | 11/11 |
| 기존 공유 판별 함수의 구현만 수정 · 별도 대조 | 통과 | 11/11 | 11/11 | 11/11 |

모든 결제가 소진된 주문에서는 영어 문구가 **Cancel order or items**, 실제 호출 대상이 **CancelOrderDialogComponent**여야 한다. 원본은 **Refund & cancel order**와 **RefundOrderDialogComponent**, 문구만 바꾼 대조는 **Cancel order or items**와 **RefundOrderDialogComponent**였다. Pending이 마지막 잔액을 차지한 경우에도 같은 차이가 났다. 한 결제에만 잔액이 남은 두 순서와 Failed 환불이 있는 주문은 환불 문구·환불 절차를 유지했다. 일부 정산액이 있어도 PaymentAuthorized 또는 active인 주문은 원래의 환불·취소 문구와 직접 취소 절차를 함께 보존했다. 숨긴 메뉴 두 건은 문구가 없고 클릭을 전달하지 않았다. [입력 주문·독립 기대값과 관측 코드](../../experiments/domain-model/s2/trial/discovery/menu.ts)

사례가 성립하는지는 고정 소스에서 다음과 같이 확인했다.

- 주문 상세 쿼리는 PaymentWithRefunds의 amount·state·refunds.state·total을 가져온다. UI의 결제별 계산은 Settled만 남기고 Failed 외의 환불액을 차감한다. Pending은 Settled·Failed로 전이할 수 있다. [주문 fragment](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/admin-ui/src/lib/core/src/data/definitions/order-definitions.ts#L95-L116) · [UI 계산](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/admin-ui/src/lib/order/src/common/get-refundable-payments.ts#L12-L31) · [환불 전이](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/core/src/config/refund/default-refund-process.ts#L16-L27)
- 환불 요청은 선택한 결제에 연결되고 주문 취소 없이도 만들 수 있다. 따라서 이미 PaymentSettled에 도달한 주문에 환불 이력이 누적된 경우를 쓸 수 있다. 여러 결제는 전액·부분 소진을 개별 구성했다. [주문 환불](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/core/src/service/services/order.service.ts#L1703-L1737) · [결제별 한도](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/core/src/service/services/payment.service.ts#L291-L330)
- 주문 총액보다 적게 정산하면 ArrangingPayment에 머물 수 있다. Authorized와 Settled로 총액을 충당하면 PaymentAuthorized도 가능하다. 기본 placed 전략은 해당 전이가 일어날 때 active를 해제한다. Cancelled 전이가 없는 상태와 Aggregate는 템플릿에서 제외한다. 이 검사는 클라이언트가 받은 상태의 동작을 관측하며 서버 전이 자체를 실행하지 않는다. [결제 후 전이](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/core/src/config/payment/default-payment-process.ts#L77-L89) · [placed 전략](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/core/src/config/order/default-order-placed-strategy.ts) · [주문 상태](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/core/src/config/order/default-order-process.ts#L175-L235)

평가기는 제출 전체 파일을 회수해 지문을 확인하고 기존 strict TS Program 1,638개 파일을 검사한다. HTML은 TS 검사에서 분리한다. 제출 HTML의 해당 버튼에서 실제 노출·문구·클릭 바인딩을 읽어 영어 번역을 해석하고, 제출 컴포넌트와 상대 경로 헬퍼를 실행해 modalService가 받은 클래스와 주문을 기록한다. Angular 브라우저 DOM, 모달 내부 제출, 서버 환불 완료는 관측 범위 밖이다. 버튼 구조를 크게 바꾸거나 실행기가 해석할 수 없는 의존성이 생기면 미지원으로 남기고 해당 조건의 효과 판정을 보류한다. 그런 제출을 자동 판정하거나 실제 DOM 클릭·렌더링까지 검증하려면 Angular 브라우저 환경이 추가 가치를 갖는다.

## 후속 실행 범위와 재현

Sol·medium은 A/B/C 각각 3회, 최대 9세션이다. 탐색 4/4와 최종 성공을 각각 예정된 3회 기준으로 집계한다. 기대 비용은 9회 합계 **입력 337,500–1,327,500토큰, 출력 16,200–54,000토큰, 54–180분**이다. 제안한 운영 상한은 세션당 입력 160,000·출력 8,000토큰, 24회 요청, 30분이다. 합계는 입력 1,440,000·출력 72,000토큰, 216회 요청, 270분이다. 시간과 횟수는 실행 전에 제한하고 누적 토큰은 응답 뒤 판정하므로 마지막 호출에서 초과할 수 있다. 실패도 소비량에 포함한다. 실제 비용·사람의 자료 작성 및 유지 시간은 미측정이다. [순서·추정 산식·중단 및 결측 처리](../../experiments/domain-model/s2/trial/discovery/plan.md)

모의 이력을 실제 전달 형식으로 매번 다시 직렬화하면 한 세션의 누적 사용자 입력은 A 285,937·B 382,496·C 436,679 UTF-8 bytes다. 같은 절차를 조건별 3회 반복하고 3–4 bytes/토큰으로 단순 환산하면 사용자 본문만 A 약 21.4만–28.6만, B 28.7만–38.2만, C 32.8만–43.7만 토큰이다. 이 감도 계산에는 시스템 입력과 추론 출력이 빠지며, 실제 Sol이 다른 순서로 탐색하면 달라진다. 특히 B/C 모의 절차는 24회를 모두 사용해 추가 조회 여유가 없었다. 위 운영 상한을 적용할 때는 미제출도 예정 분모에 남는다.

승인 뒤 실시간 연결에는 같은 세션 이력으로 각 작업을 중계하고 실제 요청 수·기한·원시 usage를 기록하는 단계가 남는다. 독립 리뷰에서는 먼저 아래 무호출 재현으로 준비 범위와 예산을 판단할 수 있다. 새 VM이나 인증은 사용하지 않았다.

기존 macOS 준비 환경과 고정 CLI의 로컬 모델 카탈로그를 사용한다. 출력 경로는 새 디렉터리를 지정한다. 모의 재생은 전체 작업 사본 6개를 생성하고 원본 지문·자료 대응·경계 검사·봉인·제출별 판정을 다시 검증한다. 시간 기록은 실행마다 달라 별도로 저장한다. wire는 로컬 수신기만 사용한다. [환경 입력 준비](../../experiments/public-app/prepared-v1/README.md) · [RxJS 환경 복원 기록](../../experiments/domain-model/s2/results/2026-11-18-fixed-input-pilot/environment-recovery.json) · [발췌한 Vendure 소스의 라이선스 고지](../../experiments/domain-model/SOURCE-NOTICE.md)

```sh
pnpm s2:build
runner=experiments/domain-model/s2/trial/discovery
evidence=experiments/domain-model/s2/results/2026-11-22-refund-discovery
python3 -B "$runner/replay.py" work/s2-contract-workspace-a/source work/s2-fixed-pilot/env work/refund-independent --verify
python3 -B "$runner/wire.py" work/refund-independent/traces.json work/refund-independent/wire.json
cmp "$evidence/wire.json" work/refund-independent/wire.json
```
