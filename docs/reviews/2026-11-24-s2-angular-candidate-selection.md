# Vendure Angular 취소 과업 선정 · 배송비 취소 후 남는 세액

**#4348을 본 비교 후보로 권고한다.** 해결 직전 Angular Admin UI의 직접 취소와 환불에 동반되는 취소는 같은 배송비 취소 요청으로 이어진다. 동결된 B/C는 이 연결을 설명한다. 참가자가 추가로 찾아야 할 곳은 서버에서 배송비를 조정하고 주문 금액을 재계산하는 경로다. 원본은 세금 포함 주문에서, 그럴듯한 부분 수정은 세금 별도 주문에서 실패했다. 업스트림 수정은 두 가격 방식과 배송비를 그대로 두는 일부 취소를 모두 충족했다. 예비 실행 포함 참가 모델 호출은 **0회**다. [업무 이슈 #4348](https://github.com/vendurehq/vendure/issues/4348) · [병합 PR #4370](https://github.com/vendurehq/vendure/pull/4370) · [선정 기준](2026-11-24-s2-angular-candidate-selection-instructions.md)

## 조사 범위와 후보

Vendure 기본 브랜치를 `a67242a6b685d6a98a7beebb109c19db07550369`에 고정했다. 동결된 근거 30개에서 시작한 8개 경로의 비병합 커밋 이력 96개를 조회했다. 주문 상세 템플릿·클래스, 취소 템플릿·클래스, 환불 클래스, 모달 서비스, 주문 데이터 서비스, GraphQL 정의에서 환불 템플릿과 서버 취소 요청 처리까지 따라갔다. 취소·환불 이슈와 병합 PR을 조회해 실제 사용자 행동이 구체적인 세 후보를 직전 소스에서 비교했다. 아래의 ‘인용 존재’는 해당 파일 안에 같은 문자열이 있는 수다. 위치가 바뀐 짧은 인용은 해당 심볼·관계를 별도로 읽었다. [8개 경로·이력 지문·후보별 30개 인용](../../experiments/domain-model/s2/results/2026-11-24-angular-selection/audit.json)

| 이슈와 해결 | 해결 직전에서의 근거 | 선별 이유와 사후 정보 확인 |
| --- | --- | --- |
| [#3150](https://github.com/vendurehq/vendure/issues/3150) · [PR #3151](https://github.com/vendurehq/vendure/pull/3151) · [부모 34e9031](https://github.com/vendurehq/vendure/tree/34e90316829c91c5025963261843731fb11d2590) | 파일 해시 3/8, 위치까지 일치 3/30, 인용 존재 30/30. 주문 상세가 환불 대화상자를 열고 취소 입력을 보낸다. 오류는 별도 환불 템플릿의 할인 배분 단가 열에 있다. | 표시만 틀렸고 제출 금액 계산에는 이미 배분 단가가 쓰였다. 이슈 보고자도 금액 계산이 맞다고 확인했다. 표시만 고쳐서 놓치는 두 번째 업무 동작을 확인하지 못했다. 자료 기준은 사후지만 B/C에 교체할 템플릿 식이나 정답 테스트는 없었다. |
| [#2608](https://github.com/vendurehq/vendure/issues/2608) · [닫은 커밋 913e6d8](https://github.com/vendurehq/vendure/commit/913e6d8e082c0ac04f836aa6c305e3465849c4dc) · [부모 9ab2e4d](https://github.com/vendurehq/vendure/tree/9ab2e4df707692ff4f7c51a2ce23afc7577e94b9) | 파일 해시 1/8, 위치까지 일치 1/30, 인용 존재 26/30. 환불 중 조건부 취소는 있으나 부모는 단일 환불을 제출한다. B/C의 복수 환불 순회와 그 인용은 사후 형태다. | 같은 항목의 두 번째 취소를 막던 조건이 수량 입력·선택에 공통으로 쓰였다. 닫은 커밋에 연결된 병합 PR은 확인되지 않았다. B/C에 비교식 자체는 없지만 다른 제출 구조가 노출되어 동시대 자료로 쓰기 어렵다. |
| [#4348](https://github.com/vendurehq/vendure/issues/4348) · [PR #4370](https://github.com/vendurehq/vendure/pull/4370) · [부모 8dbb6e4](https://github.com/vendurehq/vendure/tree/8dbb6e4063248c3084e5768d613347a3453eda41) | 파일 해시 8/8, 인용·UTF-16 위치 30/30. 두 대화상자가 같은 취소 서비스를 호출하는 관계와 배송비 포함 여부가 유효하다. | 세금 포함 배송비의 잔액, 세금 별도 주문의 기존 처리, 일부 상품만 취소한 경우의 금액을 대조할 수 있다. B/C 기준 소스는 부모의 조상이며 같은 서버 오류가 남아 있다. 이 후보에만 세 변형을 실행했다. |

## 참가자가 받는 자료와 찾아야 할 관계

[참가자용 요청 초안](../../experiments/domain-model/s2/trial/angular-shipping/public/request.txt)은 관리자가 관측한 잔액, 가격 방식별 전체 취소 결과, 환불 동반 취소와 일부 취소에서 보존할 동작을 제시한다. 공통 소스·일반 문서는 부모 `8dbb6e4063248c3084e5768d613347a3453eda41`의 Git 아카이브로 제공한다. A는 이 공통 입력, B는 여기에 68개 조회 결과, C는 대신 네 문서(guide, observations, roles, evidence)를 더한다. 동결 디렉터리의 옛 과업 지시·실행 설명은 이번 입력에 포함하지 않는다. Git 이력·원격 조회, 해결 PR·사후 테스트, 이 보고서·재생기·예상값은 평가자 쪽에 둔다. 실제 세션의 접근 경계는 이번에 실행하지 않았다.

- **B/C에서 찾을 수 있는 관계.** 주문 상세는 승인 결제면 직접 취소 대화상자, 정산 결제가 있는 비활성 주문이면 환불 경로를 연다. 직접 취소는 전체 선택을 배송비 취소로 전달한다. 환불 대화상자는 선택한 상품의 취소 입력을 환불 입력과 별도로 만들며, 취소할 행이 있을 때 같은 취소 서비스로 보낸다. B의 fact-1·5·7·11~13 및 item-7, C의 해당 관찰과 관계에 대응한다. item-7은 사람의 승인을 기다리는 후보이고 정적 호출 근거에는 런타임 보장이 없다. [B 관계와 한계](../../experiments/domain-model/s2/results/2026-11-10-trial-preparation/B/views/item-7.json) · [C의 관찰](../../experiments/domain-model/s2/results/2026-11-10-trial-preparation/C/observations.md) · [부모의 분기](https://github.com/vendurehq/vendure/blob/8dbb6e4063248c3084e5768d613347a3453eda41/packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts#L466-L474) · [부모의 환불 경로](https://github.com/vendurehq/vendure/blob/8dbb6e4063248c3084e5768d613347a3453eda41/packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts#L601-L655)
- **자료 공백.** B/C는 환불 입력과 취소 입력이 분리된다는 사실까지 기록한다. 환불 화면에서 배송 선택이 취소 입력으로 변환되는 구체식, 서버가 배송 행의 저장 가격 기준에 맞게 차감할 금액을 정하는 과정, 조정 후 세전·세후 합계를 만드는 경로는 부모 소스에서 더 찾아야 한다. 정상 변경은 두 화면이 공유하는 서버 로직 한 곳에 있다. 두 Angular 컴포넌트를 수정하는 것은 성공 조건이 아니다. [환불 입력 구성](https://github.com/vendurehq/vendure/blob/8dbb6e4063248c3084e5768d613347a3453eda41/packages/admin-ui/src/lib/order/src/components/refund-order-dialog/refund-order-dialog.component.ts#L177-L203) · [서버 서비스](https://github.com/vendurehq/vendure/blob/8dbb6e4063248c3084e5768d613347a3453eda41/packages/core/src/service/services/order.service.ts#L1886-L1923) · [취소와 재계산](https://github.com/vendurehq/vendure/blob/8dbb6e4063248c3084e5768d613347a3453eda41/packages/core/src/service/helpers/order-modifier/order-modifier.ts#L344-L366)
- **사후 정보 점검.** 자료 작성은 PR 병합 뒤였지만 그 기준 소스 v3.5.0(`534e600`)에서 이미 같은 두 UI 경로와 잘못된 서버 차감식을 확인했다. 72개 자료 파일은 11월 10일 동결본과 바이트가 일치하고 원래 감사기의 B/C 대응 단위 1,511개가 통과했다. 본문·인용에 #4348의 세금 기준 선택식이나 정답 테스트가 없으며, PR이 추가한 전용 테스트 파일은 부모에도 없다. B/C를 수정하지 않았다. [자료 기준의 배송 취소 코드](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/core/src/service/helpers/order-modifier/order-modifier.ts) · [해결 커밋의 변경 파일](https://github.com/vendurehq/vendure/commit/e30fd9e94214135de85c95631edc6f2fcedd0da1)

부모의 일반 변경 이력에는 앞선 배송 취소 수정 #3393이 남아 있다. 세금이 붙는 배송을 취소해도 음수가 되지 않아야 한다는 보존 요구의 당시 근거이며, A/B/C 모두가 읽을 수 있다. 그 수정 뒤에도 세금 포함 사례가 실패하는지는 아래 원본 대조에서 별도로 확인했다. [부모 CHANGELOG](https://github.com/vendurehq/vendure/blob/8dbb6e4063248c3084e5768d613347a3453eda41/CHANGELOG.md#L1072) · [이전 PR #3393](https://github.com/vendurehq/vendure/pull/3393)

## 같은 행동에서 관측한 금액

사례별 기대값을 먼저 고정했다. 한 주문에는 단가 100인 상품 2개와 세율 20%의 배송 한 건이 있다. 배송비는 두 가격 방식에서 동일하게 세전 1,000, 세후 1,200이며 주문 전체는 세전 1,200, 세후 1,400이다. 단위는 통화의 최소 단위다. 다음 값은 **취소 후 세후 배송비 / 세후 주문 합계**다. 세전 두 값, 대화상자에서 실제 만들어진 입력·환불액, 남은 수량은 원시 결과에 있다. [평가자용 고정 사례](../../experiments/domain-model/s2/trial/angular-shipping/cases.json) · [18개 실행의 관측값](../../experiments/domain-model/s2/results/2026-11-24-angular-selection/behavior.json)

| 관리자 행동 | 가격 방식 | 기대 | 원본 | 세후 금액을 항상 차감 | 업스트림 정상 |
| --- | --- | ---: | ---: | ---: | ---: |
| 승인 결제에서 전체 취소 | 포함 | 0 / 0 | 200 / 200 | 0 / 0 | 0 / 0 |
| 승인 결제에서 전체 취소 | 별도 | 0 / 0 | 0 / 0 | −240 / −240 | 0 / 0 |
| 정산 결제에서 2개와 배송을 환불·취소 | 포함 | 0 / 0 | 200 / 200 | 0 / 0 | 0 / 0 |
| 정산 결제에서 2개와 배송을 환불·취소 | 별도 | 0 / 0 | 0 / 0 | −240 / −240 | 0 / 0 |
| 승인 결제에서 1개만 취소, 배송 유지 | 포함 | 1,200 / 1,300 | 1,200 / 1,300 | 1,200 / 1,300 | 1,200 / 1,300 |
| 정산 결제에서 1개만 환불·취소, 배송 유지 | 별도 | 1,200 / 1,300 | 1,200 / 1,300 | 1,200 / 1,300 | 1,200 / 1,300 |
| **충족한 사례** | | **6/6** | **4/6** | **4/6** | **6/6** |

부분 수정은 사용자가 지불한 세후 배송비를 그대로 차감한다. 신고된 세금 포함 문제는 고치지만 세금 별도 주문에서는 세전 1,000을 기준으로 하는 배송 행에서 1,200을 빼고 다시 세금을 적용해 세후 −240이 된다. 원본과 부분 수정의 총점은 같고 실패한 주문은 다르다. 정상 수정은 배송 행에 저장된 가격 기준에 따라 차감한다. 환불 경로가 만든 환불 요청액은 세 변형 모두 전체 1,400, 일부 100이었다.

이 대조는 Angular 주문 상세의 분기, 두 대화상자의 선택·제출 메서드, 그 취소 입력을 받은 Vendure의 상품별 취소 메서드, 배송 엔티티의 가격 계산과 기본 세금 전략·주문 합계 getter를 실행한다. 저장소는 메모리 대역이고, 대화상자 출력에서 서버 메서드까지는 관측기가 입력을 전달한다. 템플릿 클릭·GraphQL 전송·DB 재조회·실제 결제 환불 성공은 관측 범위 밖이다. 업스트림 E2E는 별도의 API 사례로 참고했고 이번에 실행한 것은 고정된 세 변형의 메서드 대조다. 전체 전송·지속성 검증이 필요하면 Vendure 잠금 의존성과 테스트 서버·DB를 갖춘 환경에서 Admin API로 취소 후 재조회하는 투자가 필요하다. [관측 코드](../../experiments/domain-model/s2/trial/angular-shipping/replay.mjs) · [업스트림 API 검사](https://github.com/vendurehq/vendure/blob/e30fd9e94214135de85c95631edc6f2fcedd0da1/packages/core/e2e/order-cancel-shipping.e2e-spec.ts)

## 독립 재현

Ontosary의 잠금 의존성, Python 3, Node와 Git을 사용한다. Vendure 패키지는 설치하지 않는다. 평가자용 저장소는 아래 경로에 복제하거나 동일한 업스트림 커밋을 포함하는 기존 저장소로 대체한다. 두 출력 모두 보관본과 바이트 단위로 대조할 수 있다.

```sh
pnpm install --frozen-lockfile
scratch=work/review-angular-shipping
mkdir -p "$scratch"
git clone --bare --single-branch --no-tags https://github.com/vendurehq/vendure.git "$scratch/vendure.git"
trial=experiments/domain-model/s2/trial/angular-shipping
results=experiments/domain-model/s2/results/2026-11-24-angular-selection
python3 -B "$trial/audit.py" "$scratch/vendure.git" > "$scratch/audit.json"
node "$trial/replay.mjs" "$scratch/vendure.git" > "$scratch/behavior.json"
cmp "$results/audit.json" "$scratch/audit.json"
cmp "$results/behavior.json" "$scratch/behavior.json"
```

두 출력의 재생 일치를 확인했다. 저장소의 `pnpm check`는 타입 검사·테스트 304개·예제 빌드를 통과했고, `pnpm experiment`는 기존 비교 4/4를 통과했다. 실제 비교 여부와 예산은 독립 리뷰 뒤 결정한다. 비교를 진행한다면 같은 부모 소스에서 수정 전 발견한 관계·근거, 최종 변경·보존 동작, 실패 포함 비용을 기록한다. 이 단계의 4/6·6/6은 평가자 대조 결과다.
