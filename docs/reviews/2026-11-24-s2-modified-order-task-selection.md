# Vendure #4728 과업 선정 결과 · 주문 변경 후 환불 수량

**현재 B/C 자료로는 #4728의 A/B/C 비교 채택을 보류할 것을 권고한다.** React Dashboard의 환불 대화상자에서 원본·표시만 수정·현재 수량만 사용·업스트림 수정의 차이를 재현했다. 그러나 변경 전 구조화 모델의 코드 근거 30개는 모두 별개의 Angular Admin UI를 가리킨다. 이 조건으로 비교하면 자료에서 변경 지점을 찾는 능력과 다른 구현에서 유추하는 능력을 분리하기 어렵다. 참가 모델 호출은 0회이며, 과업 채택과 실행 예산은 독립 리뷰 뒤 결정한다. [선정 지시](2026-11-24-s2-modified-order-task-selection-instructions.md) · [원시 결과](../../experiments/domain-model/s2/results/2026-11-24-modified-order-selection/results.json)

## 자료가 설명하는 구현

기준 소스는 해결 커밋 `e7f8fe0029ceba9b450f60554226cec2cf628309`의 유일한 부모 `e30fd9e94214135de85c95631edc6f2fcedd0da1`이다. B는 11월 8일 Vendure v3.5.0 `534e6003534f74761e82de1b8c6061cba89945d1`에서 만든 S1을 사용한다. 당시 주문·결제·취소·환불 12개 항목과 수동 코드 사실 16개를 기록하고 Angular 클래스 4개의 메서드 78개에 역할 6개를 대조했다. FCA 후보를 추가한 뒤에도 업무 의미는 검토 대기였다. 11월 10일 B의 조회 결과 68개와 대응하는 C의 서술·근거 부록 4개를 고정했다. 이번에는 두 자료를 읽기만 했다. [S1 구축 범위](../../experiments/domain-model/README.md) · [동결 자료](https://github.com/hyeonhb/ontosary/tree/c6d093310ee8a2fb5e8fef61decd01dd4e51ec7d/experiments/domain-model/s2/results/2026-11-10-trial-preparation) · [Vendure 해결 커밋과 부모](https://github.com/vendurehq/vendure/commit/e7f8fe0029ceba9b450f60554226cec2cf628309)

B의 원문 근거 30개를 부모 리비전에서 다시 열었다. 8개 파일 모두 파일 SHA-256과 UTF-16 위치의 인용문이 일치했다. 30개 전부 `packages/admin-ui/`에 있고 `packages/dashboard/` 근거는 0개다. C가 B의 1,511개 말단 값에 대응하는 구간을 유지하는지도 원래 감사기로 확인했다. 아래 두 사례는 실제 설명까지 읽어 대조한 결과다. [자료별 지문과 30개 원문 위치](../../experiments/domain-model/s2/results/2026-11-24-modified-order-selection/results.json)

| 업무 관계 | B와 C에서 확인한 근거·한계 | 변경 전 Dashboard에서 확인한 경로 |
| --- | --- | --- |
| 주문 항목 → 취소·환불 입력 수량 | B `item-1`과 C guide 55행의 후보는 항목별 수량을 설명한다. fact-6과 C observations 48행의 예외는 active면 lines 생략, 그 외 양수만 포함이다. 실제 근거는 Angular `CancelOrderDialogComponent.getLineInputs`(82행)와 `RefundOrderDialogComponent.select`의 취소 입력(196행)이다. 두 자료 모두 서버 제약을 미확인으로 남긴다. | React `RefundOrderDialog`는 `order.lines`를 순회하면서 행의 노출, 표시 수량, 입력 max를 정하고 `onChange`에서 선택값을 제한한다. `useRefundOrder.onRefundQuantityChange`가 해당 line ID의 선택 상태를 갱신한다. |
| 환불과 함께 하는 조건부 취소 | B `item-7`과 C guide 151행은 취소·환불 요청과의 두 관계, 모든 환불에 취소가 필요한 것은 아니라는 예외, 다른 화면은 범위 밖이라는 한계를 함께 기록한다. 양쪽 모두 agent 작성·pending-review다. 근거는 Angular `OrderDetailComponent.refundOrder`와 환불 대화상자의 payload다. | React 훅은 선택 상태로 `refundLines`와 `cancelLines`를 만들고 조건부 취소 이후 선택된 결제에 환불 mutation을 보낸다. 업무상 유사성이 있어도 Angular 메서드의 인용으로 이 훅의 데이터 흐름을 추적할 수는 없다. |

B/C에는 구매 시점 수량과 변경 후 수량이 달라지는 관계, 결제별 환불 이력을 line ID로 모아 Failed를 제외하는 계산, 그 결과를 React의 행 노출·입력 상한·입력 처리에 연결하는 근거가 빠져 있다. 부모 소스에서 주문을 접수할 때 `orderPlacedQuantity`를 설정하며 새 행의 기본값은 0이다. 취소는 현재 `quantity`를 줄인다. Dashboard의 주문 조회는 두 수량과 환불 행을 함께 읽지만 환불 화면의 기존 상한은 접수 시점 수량을 사용했다. [B의 항목](../../experiments/domain-model/s2/results/2026-11-10-trial-preparation/B/views/item-1.json) · [B의 관계](../../experiments/domain-model/s2/results/2026-11-10-trial-preparation/B/views/item-7.json) · [C 서술](../../experiments/domain-model/s2/results/2026-11-10-trial-preparation/C/guide.md) · [C 관찰](../../experiments/domain-model/s2/results/2026-11-10-trial-preparation/C/observations.md) · [접수 시점 설정](https://github.com/vendurehq/vendure/blob/e30fd9e94214135de85c95631edc6f2fcedd0da1/packages/core/src/config/order/default-order-process.ts#L404-L423) · [취소 시 수량 변경](https://github.com/vendurehq/vendure/blob/e30fd9e94214135de85c95631edc6f2fcedd0da1/packages/core/src/service/helpers/order-modifier/order-modifier.ts#L333-L340) · [Dashboard 주문 조회](https://github.com/vendurehq/vendure/blob/e30fd9e94214135de85c95631edc6f2fcedd0da1/packages/dashboard/src/app/routes/_authenticated/_orders/orders.graphql.ts#L117-L166)

## 네 사본의 화면 관측

동일한 주문 객체로 각 사본의 실제 환불 대화상자를 열고 대상 SKU의 행, 수량 셀, 입력 상한을 읽었다. 허용 수량과 초과 수량을 각각 입력한 뒤 같은 컴포넌트를 다시 렌더링해 선택 상태에서 유지된 값을 읽었다. 추가 상품 사례에는 기존 상품도 함께 들어 있다. 표에서 ‘1 유지’는 입력창에 2를 넣어도 1만 남았다는 뜻이다. [브라우저 관측 코드](../../experiments/domain-model/s2/trial/modified-order/observe.jsx)

| 사본 | 기존 상품 1→2 · 2 입력 | 새 상품 0→1 · 1 입력 | 3개 중 2개 취소·환불 · 1과 2 입력 | 2개 전부 환불 · 중복 선택 | 통과 |
| --- | --- | --- | --- | --- | ---: |
| 부모 원본 | 1 표시, 상한 1, 1 유지 | 추가한 행 숨김 | 3개 중 1개 가능, 1 유지 | 행 숨김 | 2/4 |
| 표시만 수정 | **2 표시**, 환불 가능 표시는 1, 상한 1, 1 유지 | 추가한 행 숨김 | 3개 중 1개 가능, 1 유지 | 행 숨김 | 2/4 |
| 현재 수량만 사용 | 2 표시·선택, 상한 2 | 1 표시·선택, 상한 1 | **남은 1개의 행까지 숨김** | 행 숨김 | 3/4 |
| 업스트림 정상 수정 | 2 표시·선택, 상한 2 | 1 표시·선택, 상한 1 | 3개 중 1개 가능, 1 유지 | 행 숨김 | **4/4** |

표시만 고친 사본은 원본과 총점이 같아도 증가 사례의 수량 셀에서 구별됐다. 현재 수량만 쓴 사본은 이미 1개로 줄어든 수량에 환불 이력 2개를 다시 적용해 남은 행을 제외했다. 정상 사본은 업스트림 해결 커밋의 제품 코드 두 파일을 그대로 사용했다. 증감·추가 사례의 결제는 원 결제와 차액 결제를 모두 Settled로 구성했다. [원래 이슈](https://github.com/vendurehq/vendure/issues/4728) · [보존 사례](https://github.com/vendurehq/vendure/issues/2608) · [부모의 환불 수량 계산](https://github.com/vendurehq/vendure/blob/e30fd9e94214135de85c95631edc6f2fcedd0da1/packages/dashboard/src/app/routes/_authenticated/_orders/utils/order-utils.ts#L172-L201) · [부모의 행·입력 바인딩](https://github.com/vendurehq/vendure/blob/e30fd9e94214135de85c95631edc6f2fcedd0da1/packages/dashboard/src/app/routes/_authenticated/_orders/components/refund-order-dialog.tsx#L110-L164)

관측 경로는 네 사본 모두 Dashboard의 TSX, 실제 수량 입력 컴포넌트, 상태 훅, 주문·환불 헬퍼를 같은 Vite 설정으로 빌드해 로컬 Chrome에서 실행한다. 번역·서식·대화상자 외곽과 네트워크 공급자는 대역이다. 총점은 렌더링된 행과 입력 결과로 매기며 수정한 파일 수나 함수명을 점수로 쓰지 않는다. 주문 변경·차액 결제 후의 상태를 입력했으며 서버의 주문 전이·환불 제출이나 Dashboard 전체 빌드는 검사하지 않았다. 이 결과는 네 대조의 변별력을 확인한 것으로 임의 참가 패치에 대한 범용 채점기 인증은 아니다.

## 인계와 재현

현재 후보의 판단은 **화면 대조 충족, 자료 적합성 미충족**이다. 다음 후보는 기존 Angular 모델이 직접 가리키는 실제 변경에서 찾고, 해법이 자료 작성 전에 알려져 있었는지와 수정 전 근거의 유효성을 먼저 확인하는 편이 비용이 낮다. Dashboard를 우선할 경우에는 과업·해결 PR을 보지 않은 별도 작업에서 React 컴포넌트·훅을 포함하는 모델링 범위와 절차를 미리 정하고 부모 소스로 B를 작성한 뒤 C의 예외·근거 대응을 검토할 필요가 있다. 기존 S1의 클래스 메서드 추출을 그대로 적용하면 React 함수와 JSX 연결이 빠진다. 두 자료 작성과 사람 검토 비용은 미측정이며 이번 세션이 발견한 해법을 B/C에 추가하지 않았다.

참가자용은 업무 요청과 부모 아카이브의 소스·일반 문서다. 재생기는 `out/public/request.txt`와 `out/public/source/`를 만든다. 후속 탐색의 공통 검색 루트는 이 source로 한정하고, B/C에만 배정된 동결 자료를 제공한다. Git 이력, 이슈·PR 링크, 해결 아카이브, 변형 사본, 사례·기대값·보고서는 평가자 쪽에 둔다. 실제 참가 세션의 권한은 이번에 시험하지 않았다. [참가자용 업무 요청](../../experiments/domain-model/s2/trial/modified-order/public/request.txt)

Python 3.12.10, Node 22.19.0, pnpm 11.19.0, Vite 8.3.5, Chrome 158.0.8127.37에서 수행했다. 브라우저 대조에는 Ontosary 잠금 파일의 React/React DOM 19.3.1을 사용했다(Vendure 부모 잠금 버전 19.2.4). 기존 아카이브가 있으면 다운로드를 생략한다. 기본 브라우저 위치는 macOS Google Chrome이며 다른 설치 위치는 `CHROME_BIN`으로 지정한다. `out`은 새 경로여야 한다. 재생기는 아카이브 SHA-256을 확인하고 저장한 자료 감사·제출 소스 지문·사례별 DOM 결과와 바이트 단위로 대조한다. Vendure 원문과 빌드는 로컬 작업 경로에만 생성한다. [검증 스크립트](../../experiments/domain-model/s2/trial/modified-order/replay.py) · [고정 원본의 라이선스](https://github.com/vendurehq/vendure/blob/e30fd9e94214135de85c95631edc6f2fcedd0da1/LICENSE.md)

```sh
pnpm install --frozen-lockfile
cache=work/s2-modified-order
mkdir -p "$cache"
for rev in e30fd9e94214135de85c95631edc6f2fcedd0da1 e7f8fe0029ceba9b450f60554226cec2cf628309
do
  curl --fail --location --output "$cache/$rev.tgz" "https://codeload.github.com/vendurehq/vendure/tar.gz/$rev"
done
python3 -B experiments/domain-model/s2/trial/modified-order/replay.py "$cache" "$cache/independent-review" --verify
```

새 출력 경로에서 `--verify`가 통과했다. 저장소 검사 `pnpm check`는 타입 검사·테스트 304개·예제 빌드를 통과했고 `pnpm experiment`는 기존 비교 4/4를 통과했다.
