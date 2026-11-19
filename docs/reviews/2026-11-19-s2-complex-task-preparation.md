# Vendure 복합 수정 비교 준비 · 2026-11-19

**예비 A의 첫 패치는 변경 2/2·보존 3/3을 통과했다. 평가용 두 과업의 참가 호출은 0회다.** 원본·참조·부분 패치로 두 평가 과업 모두에서 변경 요구 누락과 인접 동작의 회귀를 구분했다. 아래 표는 독립 리뷰 R21·R22 보완 후 동결한 `s2-complex-v3`의 재채점 결과다. 18회 비교의 실행 여부는 보완 리뷰에서 결정한다.

| 전체 소스로 채점한 제출 | 예비 · 환불액 배분 | 평가 · 환불 잔여 수량 | 평가 · 화면 동기화 |
| --- | --- | --- | --- |
| 원본 | 변경 0/2 · 보존 3/3 | 변경 0/3 · 보존 5/5 | 변경 3/9 · 보존 15/15 |
| 참조 패치 | 2/2 · 3/3 | 3/3 · 5/5 | 9/9 · 15/15 |
| 부분 패치 | 0/2 · 0/3 | 2/3 · 4/5 | 8/9 · 13/15 |
| 참가자의 첫 패치 | A 2/2 · 3/3 | 미실행 | 미실행 |

세 과업의 참조·부분 패치 모두 원본 전체 복사본에 적용됐고 타입을 통과했다. 표의 분모는 검사 항목이다. 이번 참가 표본은 예비 A 한 건이다. [과업별 원시 관측](../../experiments/domain-model/s2/results/2026-11-19-complex-grading-v3/controls/)

## v3에서 확인한 오류의 출처와 비용

채점할 때 던져진 오류에 원인이 보존돼 있으면 그 원인의 발생 근거를 확인한다. 번역 서비스가 빠진 대역의 TypeError를 새 오류로 감싸도 세 수량 변경 검사 모두 귀속 미상으로 남는다. 반대로 제출이 유효한 입력에서 직접 던진 RangeError를 새 오류로 감싸면 원래 제출 위치가 기록된다. 순환하거나 접근자를 실행해야 읽을 수 있는 원인처럼 출처를 확인하기 어려운 경우에는 효과 비교를 보류한다. [독립 리뷰](2026-11-19-s2-complex-grading-v2-independent-review.md) · [v2에서 세 반례를 재현한 기록](../../experiments/domain-model/s2/results/2026-11-19-complex-grading-v3/v2-review-replay/)

| 제출과 실제 관측 | v3 판정 | 합성 비용표의 B−A / C−A |
| --- | --- | --- |
| 대역 오류를 그대로 전달하거나 새 오류의 `cause`로 전달 | 귀속 미상. 감싼 경우에도 원래 TypeError를 기록 | 비용 보존, 효과 판단 보류 |
| 제출이 직접 던진 오류를 그대로 전달하거나 새 오류로 감싸 전달 | 업무 실패. 감싼 경우에도 최초 `throw` 위치를 기록 | 추가 성공당 입력 60 / 120토큰 |
| 실제 Subscriber의 `error(value)`, `error?.(value)`, `['error'](value)` | 세 표기 모두 업무 실패. 사례별 관측·오류 값·제출 위치가 일치 | 세 표기 모두 60 / 120토큰 |
| 실제 Subscriber의 오류 메서드가 없는 상태에서 선택 호출 | 인자를 평가하면 예외가 나는 제출이 24/24 통과 | 세 조건 모두 6/6, 추가 성공 0건 |

비용표는 매번 A 제출 한 건을 실제로 채점하고 나머지 17건의 성공과 사용량을 고정한 검증용 자료다. 조건별 분모는 6건이고 총 입력은 A 60·B 120·C 180토큰이다. 기존 일곱 대조에 독립 반례 세 건, 제출 기원의 예외를 감싼 경우, 선택 호출이 생략된 경우를 더했다. v2의 기존 대조와 예비 봉인 제출은 같은 판정을 유지했다. [12개 대조의 채점·비용 기록](../../experiments/domain-model/s2/results/2026-11-19-complex-grading-v3/regressions/) · [동결 계약](../../experiments/domain-model/s2/results/2026-11-19-complex-grading-v3/contract.json) · [봉인 예비 A 재채점](../../experiments/domain-model/s2/results/2026-11-19-complex-grading-v3/probe/submission/evaluation.json.gz)

## v2에서 확인한 R21·R22 보완 기록

**R21.** 고정 템플릿의 수량 입력과 취소 체크박스는 같은 `lineCanBeRefundedOrCancelled(line)` 조건을 사용한다. 잔여 2개인 항목은 입력이 표시되고, 수량을 0에서 1로 바꾸면 체크박스가 활성화돼야 한다. 3개가 모두 환불된 항목은 두 입력이 숨겨져야 한다. v1에서 6/6을 받은 반전 패치는 v2에서 정확히 `quantity-and-cancel-controls/available`과 `…/exhausted`에 실패해 6/8이다. 기존 6개 검사는 그대로 재실행했고 참조는 환불 전용 선택과 제출을 포함해 8/8이다. [v1 반례 재현](../../experiments/domain-model/s2/results/2026-11-19-complex-grading-v2/v1-review-replay/) · [v2 반전 패치 관측](../../experiments/domain-model/s2/results/2026-11-19-complex-grading-v2/regressions/inverted-visibility/evaluation.json.gz)

**R22.** 잔여량을 초과하는 유효한 정수를 입력하면 제출이 직접 던지는 `RangeError`가 변경 검사 3개에서 관측됐다. v1에서는 모두 미지원이었지만 v2는 제출 파일의 136번째 줄과 `throw`를 기록해 업무 실패로 집계한다. RxJS도 같은 기준으로 제출의 직접 예외와 실제 Subscriber의 오류 통지를 추적한다. 각 관측에는 동기 호출 또는 RxJS 경로, 오류 메시지, 판정 근거가 남는다. 제출에서 발생했다고 확인할 수 없는 오류는 귀속 미상으로 기록한다. [동기 예외](../../experiments/domain-model/s2/results/2026-11-19-complex-grading-v2/regressions/direct-throw/evaluation.json.gz) · [RxJS 예외](../../experiments/domain-model/s2/results/2026-11-19-complex-grading-v2/regressions/rxjs-throw/evaluation.json.gz) · [Subscriber 오류 통지](../../experiments/domain-model/s2/results/2026-11-19-complex-grading-v2/regressions/rxjs-notification/evaluation.json.gz)

| 실제 채점에 넣은 대조 제출 또는 환경 | 최종 집계 상태 | B−A·C−A의 추가 성공당 비용 |
| --- | --- | --- |
| 가시성 반전, 유효 수량에서 직접 예외, RxJS 콜백 예외, Subscriber 오류 통지 | 네 대조 모두 `behavior-failed` | 비교 가능. 입력 토큰은 각각 60·120 |
| 평가기가 실행할 수 없는 RxJS `tap` | `unsupported` · 미지원 연산자명 기록 | 판단 보류 |
| 평가지원 대역에 없는 번역 서비스 접근 후 같은 예외를 다시 던짐 | `unsupported` · 귀속 미상 TypeError 기록 | 판단 보류 |
| 실행 환경 경로 누락 | `environment-error` · 환경 열기 오류 기록 | 판단 보류 |

각 대조에서 A 한 건을 실제 제출 채점과 비용 집계에 통과시키고 나머지 17건은 성공으로 고정했다. 비용은 검증용으로 만든 값이다. 일곱 대조 모두 예정 분모는 조건별 6건, 성공은 A 5건·B와 C 각 6건, 총 입력은 A 60·B 120·C 180이다. 비교를 보류한 대조도 이 비용을 보존한다. 각 디렉터리의 `evaluation.json.gz`와 `cost.json`에서 제출 판정과 최종 집계를 대조할 수 있다. [대조별 원시 기록과 비용표](../../experiments/domain-model/s2/results/2026-11-19-complex-grading-v2/regressions/)

공개 입력·배정·예산은 v1과 같고 새 계약에 두 평가 과업의 채점 지문을 고정했다. 이번 보완의 모델 호출은 0회이며 예비 A의 봉인 답변을 새 평가기로 다시 채점했다. [v2 계약](../../experiments/domain-model/s2/results/2026-11-19-complex-grading-v2/contract.json) · [예비 A 재채점](../../experiments/domain-model/s2/results/2026-11-19-complex-grading-v2/probe/submission/evaluation.json.gz) · [당시 v1 원시 기록](../../experiments/domain-model/s2/results/2026-11-19-complex-preparation/) · [독립 리뷰](2026-11-19-s2-complex-task-preparation-independent-review.md)

## 예비와 평가를 나눈 이유

고정 Vendure 관리 화면에서 서로 다른 값과 결정 시점을 추적하는 세 후보를 골랐다. 참가 호출 전 커밋 `46ef1fd`에 분리 이유와 공개 요구를 기록했다. 세 과업은 매번 같은 Vendure 원본에서 시작하며 예비 패치나 평가 결과를 이어받지 않는다. [사전 배정](../../experiments/domain-model/s2/results/2026-11-19-complex-preparation/split.md) · [참가자용 업무 요구 세 개](../../experiments/domain-model/s2/trial/complex/public/)

| 용도 | 공개된 새 정책 | 소스에서 복원할 보존 조건 | 후보를 채택한 이유 |
| --- | --- | --- | --- |
| 예비 · 배분 | 자동 배분에서 환불 가능 잔액이 작은 선택 결제부터 소진한다. 동률은 표시 순서를 따른다. | 정산된 결제별 과거 비실패 환불액이 잔액을 바꾼다. 품목·배송·수동 합계와 화면·전송 순서는 유지한다. | 계산 순서와 주문 요청의 순서를 분리할 수 있는지 한 번 관측할 수 있다. |
| 평가 · 수량 | 편집한 항목의 수량을 주문 당시 수량에서 해당 항목의 비실패 환불 수량을 모든 결제에 걸쳐 뺀 잔여 범위로 제한한다. | 수량은 환불액과 동반 취소에 함께 쓰인다. 사용자가 해제한 취소 선택, 다른 항목, 배송과 사유를 보존한다. | 같은 숫자를 고쳐도 환불 전용 선택을 다시 취소로 바꾸는 패치가 가능하다. |
| 평가 · 동기화 | 닫기는 조용히 종료한다. 제출한 변경 요청의 업무 결과를 모두 받은 뒤 이력과 주문을 각 한 번 갱신한다. 직접 취소 거절은 오류로 알린다. | 혼합 흐름에서 취소가 거절되면 환불은 시작하지 않는다. 환불 전용 경로, 결제별 결과 안내와 요청 내용은 유지한다. | 단일 성공, 여러 결과의 부분 성공, 변경이 없는 닫기를 구분해야 한다. |

예비 A는 9.258초, 입력 37,721·출력 236토큰을 썼다. 캐시·추론 출력은 모두 0이었다. 선택 결제 배열의 복사본만 정렬해 기존 화면 순서와 제출 순서를 유지했다. 제자리 정렬을 쓴 부분 패치는 화면 순서를 바꿔 단일 선택 같은 기존 사례도 실패했다. 이 예비에서는 공통 소스만으로 필요한 관계를 찾아냈다. 한 번의 성공을 성공률로 환산하지 않았다. 평가에는 정렬 한 곳을 바꾸는 과업을 넣지 않고, 같은 정책을 지키려면 **이력·선택·제출** 또는 **업무 결과·후속 요청·화면**의 여러 관측이 함께 맞아야 하는 두 후보를 유지했다. [예비 원응답](../../experiments/domain-model/s2/results/2026-11-19-complex-preparation/probe/b360a7/answer.txt) · [사용량 이벤트](../../experiments/domain-model/s2/results/2026-11-19-complex-preparation/probe/b360a7/events.jsonl) · [봉인 후 채점](../../experiments/domain-model/s2/results/2026-11-19-complex-preparation/probe/score/evaluation.json.gz)

## 참가 입력과 의미 대응

revision `534e6003534f74761e82de1b8c6061cba89945d1`에서 지난 파일럿의 공개 파일명 규칙을 그대로 사용했다. admin-ui의 order·cancel·refund 관련 생산 TypeScript 파일 42개 전체, 공개 제약과 제출 형식을 공통으로 주고 업무 요구만 교체했다. A도 결제 잔액 계산기, 대화상자, 주문 화면과 서비스 본문을 읽을 수 있다. B에는 기존 뷰 68개, C에는 기존 서술 문서 3개와 원문·메타데이터 부록 1개를 더했다. 평가자 전용 사례·대조 패치·예비 답변은 조립기가 입력으로 읽지 않는다. 외부 채점 파일은 저장소에서 리뷰할 수 있으며 참가 세션에는 파일 접근 도구가 없다. [입력 조립기](../../experiments/domain-model/s2/trial/complex/packets.py) · [수량 입력 지문](../../experiments/domain-model/s2/results/2026-11-19-complex-preparation/heldout/quantity/inputs.json) · [동기화 입력 지문](../../experiments/domain-model/s2/results/2026-11-19-complex-preparation/heldout/refresh/inputs.json)

| B/C에서 대조한 판단 | 구조화 뷰와 서술 본문 | 고정 소스에서 확인한 범위 |
| --- | --- | --- |
| 어떤 값이 별개인가 | B의 `refund-request → line`과 `refund-request → payment`가 C의 item-4에 모두 outgoing으로 적혀 있다. item-1은 두 입력의 항목별 수량을 설명한다. | 환불 대화상자 `select()`는 결제별 환불 입력과 별도의 취소 입력을 만든다. `lineCanBeRefundedOrCancelled()`는 환불 이력을 항목 ID별로 모으고 Failed를 제외한다. |
| 환불에 언제 취소가 필요한가 | B item-7과 C 모두 두 경로의 취소 service 공유, 그리고 “모든 환불에 취소가 필수인 것은 아니다”라는 예외를 담는다. | 주문 화면은 취소할 라인이 있을 때에만 취소 결과를 먼저 분기한다. `source-refund-request`는 남은 환불 입력을 결제별 호출로 연결한다. |
| 닫으면 어떤 결과가 전달되는가 | B item-8과 C의 dismiss는 두 dialog의 인자 없는 `resolveWith()`와 실제 modal 종료에 관한 불확실성을 보존한다. item-6은 modal 결과 확인과 service 호출을 구분한다. | 두 `cancel()` 본문과 상세 화면의 `of(undefined)`, `refetchOrder()`를 대조했다. 이력 갱신 신호와 실제 주문 재조회는 별도 관측이다. |

B의 방향·예외·근거·검토 상태를 C 본문 및 부록과 대조하고 기존 1,511개 leaf 대응, 30개 발췌의 파일 SHA와 UTF-16 좌표 원문을 다시 검사했다. 관련 항목은 pending-review이고 기존 모델에는 작은 잔액 우선순위, 새 수량 상한, 작업당 갱신 횟수가 규정돼 있지 않다. 이 세 정책은 모든 조건의 공개 요구에만 넣었다. 검토한 범위에서 한쪽에만 새 해법이 담긴 사례는 발견하지 못했다. 두 표현의 업무 의미에 대한 사람의 최종 판단은 남아 있다. [B 뷰](../../experiments/domain-model/s2/results/2026-11-10-trial-preparation/B/views/) · [C 본문](../../experiments/domain-model/s2/results/2026-11-10-trial-preparation/C/guide.md) · [관찰](../../experiments/domain-model/s2/results/2026-11-10-trial-preparation/C/observations.md) · [근거 부록](../../experiments/domain-model/s2/results/2026-11-10-trial-preparation/C/evidence.md)

## 교정이 구분한 실패와 판단 범위

수량 사례에서 원본은 주문 당시 6개 중 다른 결제를 포함해 3개가 이미 환불됐는데도 5개를 받아들였다. 참조는 3개를 남겼다. 부분 패치는 상한을 적용하지만 양수로 재편집할 때마다 취소 선택을 되살린다. `manual-refund-only-under-cap`에서 수량·금액이 맞아도 취소 라인이 생겨 실패한다. 사용자 편집에서 도달한 상태와 제출 payload를 함께 검사했다. [수량 참조·부분 패치](../../experiments/domain-model/s2/trial/complex/evaluator/controls/) · [부분 패치의 관측](../../experiments/domain-model/s2/results/2026-11-19-complex-grading-v3/controls/quantity/partial/evaluation.json.gz)

동기화 사례에서 원본은 혼합 성공의 중간 취소 결과와 마지막 환불 결과에서 각각 갱신했다. 참조는 마지막 결과 뒤에 한 번 갱신한다. 부분 패치는 화면까지 흐름을 이어 주지만 취소 거절 뒤 원래 입력을 후속 단계로 보내 환불까지 실행한다. `mixed-cancel-rejected/requests`에서 대상·순서가 드러난다. 주문 재조회는 Observable의 실제 구독을, 이력 갱신은 신호를 관측한다. 동시에 요청한 두 결제의 응답을 역순으로 완료시켜 이른 재조회도 구분했다. [화면 관측기](../../experiments/domain-model/s2/trial/complex/evaluator/refresh.ts) · [부분 패치의 관측](../../experiments/domain-model/s2/results/2026-11-19-complex-grading-v3/controls/refresh/partial/evaluation.json.gz)

채점기 `s2-complex-v3`은 새 전체 제출 루트에 기존 엄격 타입 검사를 수행하고 실제 제출 메서드와 상대 helper를 실행한다. 비교 대상은 화면 값·payload·알림·호출 순서와 횟수다. 예비 A와 참조처럼 표현이 다른 코드도 같은 결과를 얻을 수 있다. 보존 실패와 요구 실패는 함께 기록한다. 실행한 소스 SHA는 타입 검사 소스와 대조한다. 최초 교정에서는 VM 배열의 realm 차이 때문에 값이 같은 관측이 실패했고, 직접 취소 참조 패치의 union 오류도 발견했다. JSON 값 비교와 참조 타입 가드를 수정한 뒤 표의 대조군을 다시 실행했다. [평가 진입점](../../experiments/domain-model/s2/trial/complex/evaluator/run.ts) · [폼·제출 관측기](../../experiments/domain-model/s2/trial/complex/evaluator/dialogs.ts)

실제 브라우저·서버·네트워크 장애는 측정하지 않는다. FormControl·DI·서버 응답은 제한된 대역이며 기존 평가기가 허용하는 TypeScript 메서드·상대 helper·동기 RxJS 범위에서 판정한다. 의미상 타당한 답이 미지원 연산자나 필드 초기화 변경을 요구하면 해당 결과를 미지원으로 인계한다. UI 쓰기 자체, 임의의 외부 입력 또는 모든 가능한 주문의 정확성까지 증명하지 않는다.

**리뷰에서 확정할 업무 가정은 두 가지다.** 수량 상한은 주문 당시 수량과 실패하지 않은 환불 이력으로 계산한다. 거절만 발생한 제출도 화면을 한 번 동기화하며 직접 취소 거절은 오류 안내를 낸다. 모두 실험용 클라이언트 정책이다. 이 선택이 바뀌면 기대값과 패킷 지문도 다시 동결해야 한다.

## 성공·비용 계약

평가 과업 2개 × 조건 3개 × 독립 반복 3회로 **총 18회, 조건별 6회**를 계획했다. 세 반복이면 과업마다 각 조건이 첫째·둘째·셋째에 한 번씩 배정된다. 두 과업의 순서를 번갈아 배치했다. 동일 모델 `gpt-6.2-astra`, reasoning `medium`, 도구 없는 임시 세션에서 첫 제출 하나만 받는다. 각 과업·반복별 A/B/C 결과를 짝지어 표시한다. 18개 모두 봉인 또는 수집 중단 상태를 기록한 뒤 채점하며 참가 재호출은 없다. [동결 순서·예산·지문](../../experiments/domain-model/s2/results/2026-11-19-complex-grading-v3/contract.json) · [도구 노출 사전 검사](../../experiments/domain-model/s2/results/2026-11-19-complex-preparation/heldout/refresh/preflight.json)

| 조건 | 수량 / 동기화 패킷 바이트 | 회당 예상 입력 | 6회 예상 입력 | 6회 예상 출력 |
| --- | ---: | ---: | ---: | ---: |
| A | 193,117 / 193,287 | 36,000~41,000 | 216,000~246,000 | 1,200~24,000 |
| B | 289,374 / 289,544 | 62,000~68,000 | 372,000~408,000 | 1,200~24,000 |
| C | 300,283 / 300,453 | 66,000~73,000 | 396,000~438,000 | 1,200~24,000 |

18회 합계 예상은 입력 **984,000~1,092,000**, 출력 **3,600~72,000토큰**이다. 지난 A/B/C 실측 약 37.8k/64.8k/69.3k와 이번 공개 입력 크기를 기준으로 잡았다. 출력 200~4,000은 복합 과업을 고려한 계획 범위다. 가장 긴 패킷 300,453바이트에 공통 지시 60, 프레이밍 여유 4,096, 출력 여유 49,152를 더해도 유효 문맥 486,400 안에 들어간다. [이전 실측](2026-11-19-s2-fixed-input-pilot-independent-review.md)

- **완전 성공**은 기회당 첫 패치가 적용되고 타입 검사, 소스 결합, 모든 변경·보존 검사 및 예산을 충족한 경우다. A가 성공한 과업과 실패 시도를 포함해 분모를 조건별 6으로 유지한다.
- **회당 예산**은 1,800초, 입력 82,000·출력 8,000토큰, 패치 49,152 UTF-8바이트다. 실행기는 시간을 초과하면 프로세스를 종료한다. 입력에는 B/C 자료를 전부 산입한다. 토큰은 CLI usage로 사후 판정하고 패치 바이트도 원응답에서 검사한다. 토큰을 초과한 시도의 실제 비용을 버리지 않는다.
- **누락·오류**는 무응답, 시간 초과, 적용 실패, 타입 실패, 업무 실패, 미지원, 환경 오류로 나눠 남긴다. usage가 없으면 미상이다. 관측된 소계와 건수를 따로 표시한다. 실패는 다른 시도로 대체하지 않는다. 환경 오류는 같은 제출·평가 지문으로 복구 후 재채점할 수 있다. 미해결 인프라·미지원·성공 예산 미확인 시 해당 조건 쌍의 효과 해석을 보류하고 예정 분모와 관측 결과를 공개한다. 깨진 봉인으로 원응답을 다시 만들지 않는다.
- **효과와 추가 비용**은 B−A, C−A 별로 전체 입력, 출력, 경과 시간의 차이와 완전 성공 건수 차이를 낸다. 추가 성공이 양수이고 비교 가능한 경우만 각 비용 차이를 추가 성공 건수로 나눈다. 캐시 입력은 입력에, reasoning은 출력에 이미 포함되므로 가산하지 않는다. 금액 환산은 생략한다. 사람의 모델 작성·의미 검토·유지 시간은 각각 미상이며 회당 모델 사용량과 별개다. [집계 구현](../../experiments/domain-model/s2/trial/complex/holdout.py)

## 참가 호출 없는 재현

고정된 전체 소스와 준비된 실행 환경이 있는 macOS에서 저장소 루트 기준으로 실행한다. 아래 예시는 이번에 검증한 로컬 캐시를 사용한다. 새 scratch 경로를 지정한다. 원본·참조·부분 9건과 봉인한 예비 A 1건을 v3로 재채점하고, 반례·대조 12건을 제출 채점부터 비용 집계까지 재현해 동결 기록과 대조한다. 기존 v4 기본 진입점으로도 원본 타입 통과·22/52를 확인했다. `pnpm check`는 타입 검사·304개 테스트·예제 빌드를 통과했고, 집계 회귀 검사 3개와 기존 `pnpm experiment` 비교 4개가 통과했다. 오프라인 집계 연습에서 참조 응답 2개와 수집 중단 표시 16개를 넣어 조건별 분모 6, 누락 비용 미상, 효과 판단 보류를 확인했다. 이 연습은 참가 결과에 포함하지 않았다. [환경의 출처와 복원 기록](2026-11-18-s2-fixed-input-pilot.md) · [재현 검사기](../../experiments/domain-model/s2/trial/complex/verify.py)

```sh
pnpm s2:build
python3 -B experiments/domain-model/s2/trial/complex/verify.py work/s2-contract-workspace-a/source work/complex-v3-review-01 --environment work/s2-fixed-pilot/env
python3 -B experiments/domain-model/s2/trial/complex/test_cost.py
pnpm check
pnpm experiment
```

도구 목록·실제 패킷까지 재점검하려면 `holdout.py stage <새 작업경로> --source <전체 원본>`을 쓴다. 로컬 수신기로 요청을 확인하며 추론은 수행하지 않는다. 리뷰 후 실행을 승인한 경우에만 같은 경로의 `collect`로 동결 순서를 실행하고, 수집 완료 뒤 `score`에 같은 전체 원본·환경과 새 출력 디렉터리를 전달한다. 준비 PR에서 실행한 참가 호출은 예비 A 1회, 예비 B/C 0회, 평가 0/18회다.
