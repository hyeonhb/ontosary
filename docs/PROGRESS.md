# 현재 작업 상태 — 새 세션은 이 문서부터 읽기

2026-11-27 [Vendure 부분 출고 첫 사용 실행 지시문](reviews/2026-11-27-first-use-partial-fulfillment-run-instructions.md)을 작성했다. 사용자는 작성 agent 한 세션과 독립된 후속 agent 한 세션의 대리 검증을 선택했다. 지시문 작성 시점의 참가 결과는 미측정이다.

2026-11-26 [부분 출고 첫 사용 준비 독립 리뷰](reviews/2026-11-26-first-use-partial-fulfillment-independent-review.md)를 마쳐 PR #117을 병합했다. 두 전달본·CLI의 분석 범위와 FCA 상한·프런트엔드 주문 대조를 재현했다. 다음 결정은 작성자 배정 또는 대리 검증 여부이며 참가 결과는 미측정이다.

2026-11-26 [Vendure 부분 출고 첫 사용 준비](reviews/2026-11-26-first-use-partial-fulfillment-preparation.md)에서 작성자·후속 agent용 자료를 분리하고 고정 소스의 주문 진입·행별 수량 근거와 검산 사례를 확인했다. 공개 CLI의 앱 범위 scan은 진단 0개, concepts는 기본 객체·속성 상한 초과였다. 작성자는 미배정이고 참가 모델 호출은 0회다. 첫 사용·인계·도구 기여는 미측정으로 준비 결과 리뷰에 인계한다.

2026-11-26 [Vendure 부분 출고 첫 사용 검증 준비 지시](reviews/2026-11-26-first-use-partial-fulfillment-instructions.md)를 작성했다. 공개 코드를 처음 보는 작성자와 별도 agent 간 인계를 우선 확인하기로 했다. 참가자 자료·검토자 근거의 준비와 리뷰가 다음 작업이며, 참가 및 도구 기여는 미측정이다.

2026-11-26 [PR #114 독립 확인](reviews/2026-11-26-s2-shipping-pilot-independent-review.md#2026-11-26-결과표-보완-확인)에서 미제출·적용 거부·실행 수 표기를 재현해 결과표 보완을 마감했다. 참가 모델 재호출은 0회이며 새 A/B/C 배치의 실행·예산 결정이 남았다.

2026-11-26 [배송비 파일럿 결과표](../experiments/domain-model/s2/results/2026-11-26-shipping-pilot/tables.md)에 봉인된 패치 제출 여부, 적용 단계와 실제 사례 실행 수를 표시했다. 과거 적용 거부 대조를 A에 배정하면 제출 1건·적용 거부 1건·사례 실행 0건과 Git 거부 사유를 복원한다. 실제 중단 배치는 세 건수 모두 0이었다. [오프라인 회귀 검사](../experiments/domain-model/s2/trial/angular-shipping/pilot/test_replay.py)에서 적용 완료 뒤 사례 실행이 0건인 대조와 6건인 대조도 확인했다. 참가 모델 호출은 0회다.

2026-11-26 [배송비 취소 파일럿 독립 리뷰](reviews/2026-11-26-s2-shipping-pilot-independent-review.md)에서 중단 기록을 재현해 PR #112를 병합했다. A의 16번째 요청에서 용량 부족과 사용량 결측이 발생했고 B/C는 미실행이었다. 제출과 사례 실행이 모두 0건이라 자료 효과는 미측정이다. 다음 실행 전 표의 적용 거부 표기를 보완하고 새 배치 예산을 결정한다.

2026-11-26 [배송비 취소 파일럿 중단 결과](reviews/2026-11-26-s2-shipping-pilot.md). A의 16번째 요청에서 서버 용량 부족과 사용량 결측이 발생해 B/C를 보류했다. 첫 15회에 입력 44,980·출력 452토큰을 확인했다. 수정 전 근거와 첫 패치는 미제출이며, 오프라인 탐색·비용 재현 결과를 독립 리뷰로 인계한다.

2026-11-26 [Vendure 배송비 취소 A/B/C 파일럿 지시문](reviews/2026-11-26-s2-shipping-pilot-instructions.md)을 작성했다. 조건별 독립 세션 1회에서 수정 전 코드 근거, 첫 패치의 여섯 동작, 실패 포함 비용을 비교한다. 문서 작성 단계의 참가 호출은 0회다.

2026-11-26 [#4348 참가 패치 채점 보완 종료](reviews/2026-11-26-s2-shipping-grading-close.md). 같은 부분 수정에서 4통과·2실패를 재현하고 기존 12개 제출의 판정 보존을 확인해 PR #107을 병합했다. 참가 호출은 0회다. 다음 결정은 A/B/C 각 한 세션의 실행과 예산이다.

2026-11-26 [PR #107 배송 행 저장 관측 보완](reviews/2026-11-26-s2-shipping-inclusive-only-grading.md)으로 세금 포함 주문만 고친 제출을 4통과·2실패로 판정했다. 세금 별도 전체 취소 두 건에서 기대 0인 세후 배송비와 주문 합계가 각각 1,200으로 저장됐다. 기존 12개 제출의 판정과 근거를 재현했다. 참가 호출 0회로 독립 리뷰에 인계한다.

2026-11-26 [PR #107 R26·R27 보완](reviews/2026-11-26-s2-shipping-grading-fix.md)에서 주문 저장 시점의 금액과 전체 취소 반환값·잔여 수량을 대조했다. 독립 리뷰의 두 패치는 각각 6건 모두 업무 실패로 판정됐고, 네 기준 제출은 4/6·4/6·6/6·6/6을 유지했다. 참가 호출 0회로 보완 결과를 독립 리뷰에 인계한다.

2026-11-26 [#107 독립 리뷰와 보완 지시](reviews/2026-11-26-s2-shipping-submission-grading-independent-review.md)에서 기존 대조 9건을 재현했다. 주문 저장 후 재계산한 제출이 6/6을 받고 수량을 줄이지 않은 제출이 전부 판정 불가였다. R26·R27 보완을 확인할 때까지 병합과 A/B/C 참가 실행을 보류한다.

2026-11-26 [배송비 취소 과업의 참가 패치 채점](reviews/2026-11-26-s2-shipping-submission-grading.md)에서 독립 사본 네 개를 같은 경로로 판정했다. 원본 4/6, 부분 수정 4/6, 업스트림과 별도 헬퍼 정상 수정 각 6/6이다. 패치 적용 거부와 업무 실패, 미관측 변경·대역 한계의 판정 불가를 재현했다. 참가 호출 0회이며 A/B/C 실행·예산은 독립 리뷰 뒤 결정한다.

2026-11-26 Vendure #4348을 S2 비교 과업으로 채택했다. 다음은 [참가 패치 채점 확인](reviews/2026-11-26-s2-shipping-submission-grading-instructions.md)이다. 참가 호출 0회로 기존 세 대조와 별도 헬퍼를 쓰는 정상 수정을 같은 제출 경로에서 확인한다. A/B/C 실행 여부와 예산은 준비 결과 리뷰 뒤 결정한다.

2026-11-26 [#107 보완 독립 리뷰와 후속 지시](reviews/2026-11-26-s2-shipping-grading-fix-independent-review.md)에서 R26을 닫고 R27의 수량 반례 해결을 확인했다. 세금 포함 주문에서만 차감한 제출의 금액 오류 두 건이 판정 불가로 남았다. 이 반례의 보완 뒤 병합과 참가 실행을 결정한다.

2026-11-24 [배송비 취소 과업 독립 리뷰](reviews/2026-11-24-s2-angular-candidate-selection-independent-review.md)에서 PR #104를 병합했다. 변경 직전 근거와 원본·부분·정상 수정의 4/6·4/6·6/6을 재현해 Vendure #4348 채택을 권고한다. 참가 호출은 0회다. 채택과 예산을 결정하면 참가 패치의 채점 범위를 첫 호출 전에 확정한다.

2026-11-24 [Angular 실제 변경 후보 선정](reviews/2026-11-24-s2-angular-candidate-selection.md)에서 Vendure #4348 배송비 취소 과업을 권고했다. 해결 직전 근거 30/30이 일치했고, 두 UI 경로와 세금 포함·별도 주문을 대조해 원본 4/6, 부분 수정 4/6(서로 다른 실패), 정상 수정 6/6을 관측했다. 참가 호출 0회이며 채택과 실행 예산은 독립 리뷰 뒤 결정한다.

2026-11-24 [Angular 자료 범위에서 실제 변경 후보 선정](reviews/2026-11-24-s2-angular-candidate-selection-instructions.md)을 인계한다. 취소·환불의 동결 근거가 실제 변경 직전에도 같은 구현에 연결되는지 먼저 확인하고, 유력 후보 한 건만 동작 대조한다. 실제 참가 호출과 예산은 별도 결정 대상이다.

2026-11-24 [#4728 선정 독립 리뷰](reviews/2026-11-24-s2-modified-order-selection-independent-review.md)에서 PR #101을 병합했다. 화면 대조 2/4·2/4·3/4·4/4를 재현했고 부모의 React 19.2.4에서도 관측값이 같았다. 기존 B/C 근거는 Angular Admin UI에 한정돼 이 자료로 하는 #4728 본 비교는 보류한다. 참가 모델 호출은 0회다.

2026-11-24 [Vendure #4728 과업 선정 결과](reviews/2026-11-24-s2-modified-order-task-selection.md)는 **현재 B/C로 채택 보류 권고**다. 부모 리비전에서 동결 근거 30개가 모두 Angular 파일 8개에 일치했다. React Dashboard 화면 대조는 원본 2/4, 표시만 수정 2/4, 현재 수량만 사용 3/4, 업스트림 수정 4/4였다. 참가 호출은 0회이며 과업과 예산 결정은 독립 리뷰에 인계한다.

2026-11-24 [주문 변경 후 환불 수량 후보 검증](reviews/2026-11-24-s2-modified-order-task-selection-instructions.md)을 인계한다. Vendure #4728을 대상으로 같은 변경 전 구현에 대응하는 B/C 자료와 부분 수정 대조의 변별력을 무호출로 확인한다. 과업 채택과 본 비교 예산은 준비 결과 리뷰 뒤 결정한다.

2026-11-24 [환불 잔액 준비 종료 리뷰](reviews/2026-11-24-s2-refund-preparation-close.md)에서 같은 제출의 잘못된 만점이 미지원으로 바뀌고 기존 12개 대조와 로컬 요청이 유지됨을 확인했다. R23~R25를 닫고 PR #96을 병합했다. 실제 참가 호출은 0회이며 다음 단계는 Vendure 실제 복합 변경 후보 선정이다.

2026-11-24 [바깥 메뉴 바인딩 대조](../experiments/domain-model/s2/results/2026-11-24-refund-outer-gate/)에서 같은 제출의 판정이 11/11 성공에서 미지원으로 바뀌었다. 바깥 버튼의 `ngIfThen`을 진단하고 동작 평가 전에 멈춘다. 안쪽 `else cancelOnly`를 사용하는 기존 12개 대조와 루프백 요청 9개를 재현했다. 참가 호출은 0회다. [독립 리뷰의 종료 조건](reviews/2026-11-24-s2-refund-grading-fix-independent-review.md)

2026-11-22 [PR #96의 R23–R25 보완](reviews/2026-11-22-s2-refund-discovery-grading-fix.md)에서 독립 작업 사본 12개를 같은 채점기로 판정했다. Angular 무효 바인딩은 실패, 지원 밖 삼항식은 미지원, 명시적 제출 예외는 9개 사례의 제출 실패로 구분했다. A/B/C의 공개 검색 예시와 로컬 HTTP 요청을 대조했다. 참가 호출 0회이며 실제 비교 예산은 보완 리뷰 뒤 결정한다.

2026-11-22 [환불 잔액 탐색 비교 준비](reviews/2026-11-22-s2-refund-discovery-preparation.md)에서 A/B/C의 단일 탐색 제출과 독립 변경 소스를 회수했다. 원본·문구만 수정은 각각 9/11이며 부분 수정은 전액 소진에서도 환불 대화상자를 열었다. 두 정상 구현은 11/11이다. 참가 호출 0회로 Sol·medium 최대 9세션의 판정 기준과 예산을 독립 리뷰에 인계한다.

2026-11-22 다음 과업은 [환불 잔액 변경의 영향 범위 탐색 비교 준비](reviews/2026-11-22-s2-refund-discovery-preparation-instructions.md)다. 기존 환경에서 일반 검색·모델 조회·서술 문서 조회의 탐색 결과를 비교할 수 있는지 먼저 확인한다. 최종 수정 평가는 동등한 소스 수집이 가능할 때 포함한다. 승인 범위는 무호출 준비이며 실제 비교는 준비 결과 리뷰 후 결정한다.

2026-11-22 [PR #96 독립 리뷰와 보완 지시](reviews/2026-11-22-s2-refund-discovery-independent-review.md)에서 준비 재생과 로컬 요청을 재현했다. Angular 표현식의 잘못된 성공 판정, 제출 예외의 미지원 판정, 첫 요청 JSON 사용법을 R23~R25로 인계한다. PR #96 병합과 실제 참가 실행은 보류한다.

2026-11-24 [PR #96 보완 독립 리뷰](reviews/2026-11-24-s2-refund-grading-fix-independent-review.md)에서 R24·R25를 닫고 탐색 준비를 마감했다. R23은 유효한 추가 Angular 입력을 무시한 채 11/11을 주는 사례가 남았다. 최종 수정 채점 승인과 병합은 이 사례를 구분한 뒤 결정한다. 환불 과업의 참가 실행 없이 실제 복합 변경 후보 선정으로 넘어갈 수 있다.

2026-11-22 [Sol 비교 독립 리뷰](reviews/2026-11-22-s2-sol-comparison-independent-review.md)를 마치고 PR #93을 병합했다. 두 배치 36건의 공식 결과를 재현했다. Sol의 공식 적용 거부 3건은 별도 진단에서 문맥 요구를 완화하자 같은 업무 검사를 모두 통과했다. Sol의 완전 성공은 A 4/6·B 5/6·C 5/6이며, 자료가 복구한 업무 동작은 관측하지 못했다. 다음 과업과 실행 범위는 별도 논의 대상이다.

2026-11-20 Sol 요청 배치 18/18을 봉인하고 v3로 채점했다. A 4/6, B 5/6, C 5/6이다. A의 두 실패는 패치 적용에서 발생했고, 실행된 업무 검사에서 A가 놓친 요구를 B/C가 충족한 사례는 확인하지 못했다. 잔여 수량은 Sol+A·C, 화면 동기화는 Sol+B가 기존 Astra+A와 같은 3/3을 얻었다. 전체 6/6에 도달한 Sol 조건은 없다. 서버 모델명은 18건 모두 미확인이며 승인된 표기 기준을 적용했다. [첫 패치·비용 비교 및 무호출 재현](reviews/2026-11-20-s2-sol-comparison.md)

2026-11-20 Sol 배치의 계약·여섯 패킷과 결과 위치를 첫 호출 전 `ac71ba7`에 동결했다. 첫 기회(수량 B·반복 1)는 요청 모델 Sol·medium으로 응답과 사용량을 봉인했다. 해당 CLI 실행 기록에서 서버가 회신한 모델명을 확인할 수 없어 수집을 1/18에서 중단했다. 나머지 17건은 미실행이고 Sol은 채점 전이다. 기존 Astra 18건의 등급과 비용은 모델 호출 없이 재현했다. [Sol 실행 지시](reviews/2026-11-20-s2-sol-comparison-instructions.md) · [Sol 계약과 봉인 기록](../experiments/domain-model/s2/results/2026-11-20-sol-comparison/)

2026-11-20 다음 개발 세션에 [Sol 고정 입력 비교](reviews/2026-11-20-s2-sol-comparison-instructions.md)를 인계한다. 같은 두 과업·자료·v3 평가기로 Sol 내부의 A/B/C를 먼저 대조하고, 기존 Astra+A와 성공 및 비용을 비교한다. 지시 작성 시점의 Sol 참가 실행은 0/18이다.

2026-11-20 [복합 비교 독립 리뷰](reviews/2026-11-20-s2-complex-comparison-independent-review.md)에서 Python 3.12.10으로 18개 등급·업무 관측·비용표를 재현해 PR #90을 병합했다. A가 두 과업의 세 반복을 모두 해결했고 B/C의 추가 성공은 없었다. B 패치 두 건은 동결된 Git 적용 조건에서 실패했다. Python 3.9.6의 시간 합계 반올림 차이를 재현 문서에 기록했다. 후속 모델·과업 실행은 별도 결정 대상이다.

2026-11-20 Vendure 복합 수정 과업의 첫 응답 18/18을 봉인하고 v3로 채점했다. 완전 성공은 A 6/6, B 4/6, C 6/6이다. B의 화면 동기화 패치 2건이 적용되지 않았고 적용된 16건은 모두 타입·동작 검사를 통과했다. 추가 성공은 B−A가 −2, C−A가 0이며 총 입력 1,030,206·출력 11,639토큰이다. 결과 PR을 독립 리뷰에 인계한다. [시도별 결과·비용·무호출 재현](reviews/2026-11-20-s2-complex-comparison.md)

2026-11-20 [고정 입력 A/B/C 비교 실행 지시](reviews/2026-11-20-s2-complex-comparison-instructions.md)를 작성했다. 사용자가 두 실험용 업무 정책과 v3 예산으로 18회 비교를 승인했다. 지시 작성 시점의 평가 참가 실행은 0/18이다.

2026-11-19 [v3 독립 리뷰](reviews/2026-11-19-s2-complex-grading-v3-independent-review.md)에서 R21·R22를 닫고 준비 PR #85를 `9e2b197`로 병합했다. 기존 대조·예비·회귀 22건과 독립 변형 3건을 채점했다. 평가 참가 실행은 0/18이다. 다음 결정은 두 실험용 업무 정책과 동결 예산으로 실제 비교를 진행할지 여부다.

2026-11-19 PR #85의 `s2-complex-v3`에서 R22 독립 반례 세 건을 재채점했다. 누락된 평가 대역의 예외를 감싸도 비용을 보존하고 효과 판단을 보류한다. 같은 오류를 통지하는 Subscriber 호출 세 표기는 같은 업무 실패로 집계했다. 선택 호출이 생략된 대조는 24/24, 봉인한 예비 A는 5/5였다. 기존 7건을 포함한 12건의 제출·비용 대조를 동결했다. 새 모델 호출 0회, 평가 실행 0/18이며 PR은 독립 재검토를 기다린다. [v3 판정과 재현 명령](reviews/2026-11-19-s2-complex-task-preparation.md)

2026-11-19 [S2 채점 보완 독립 리뷰와 후속 지시](reviews/2026-11-19-s2-complex-grading-v2-independent-review.md). PR #85의 `a073296`에서 R21을 닫고 R22의 직접 예외 처리를 재현했다. 원인이 보존된 평가 대역 오류와 두 형태의 Subscriber 호출에서 비용 비교 판정이 달라져 R22의 국소 보완을 요청한다. PR #85는 미병합이며 평가 참가 실행은 0/18이다.

2026-11-19 PR #85에서 복합 과업 채점기를 `s2-complex-v2`로 동결했다. R21 반전 패치는 잔여·소진 항목의 편집 진입 검사에서 실패했고 수량 참조는 8/8, 동기화 참조는 24/24였다. R22의 직접 예외·RxJS 오류는 비용을 포함한 업무 실패로 집계하고 미지원·귀속 미상·환경 오류 대조는 효과 판단을 보류했다. 봉인된 예비 A 재채점은 5/5, 이번 모델 호출은 0회, 평가 실행은 0/18이다. 보완 결과는 독립 재검토를 기다린다. [준비 보고서와 재현 명령](reviews/2026-11-19-s2-complex-task-preparation.md)

2026-11-19 [Vendure 복합 과업 준비 결과](reviews/2026-11-19-s2-complex-task-preparation.md). 예비 A 첫 제출 1/1은 변경 2/2·보존 3/3을 통과했다. 예비 B/C 0회, 평가 0/18회다. 평가 수량·화면 동기화 각각 원본·참조·부분 패치를 전체 소스로 교정했고, 참조는 6/6·24/24, 부분 패치는 환불 전용 선택·취소 거절 뒤 환불 중단 보존에 실패했다. 과업별 세 반복의 성공·추가 비용 계약을 동결해 독립 리뷰에 인계한다.

2026-11-19 [Vendure 복합 수정 과업 준비 지시](reviews/2026-11-19-s2-complex-task-preparation-instructions.md)를 작성했다. 기존 고정 입력 환경에서 예비 과업의 A 조건으로 난이도를 가늠하고, 별도 평가 과업과 A/B/C 성공·비용 비교 기준을 동결하는 단계다. 지시 작성 시점에 새 참가 호출은 예비 0회·평가 0회다. 실제 비교는 준비 결과 리뷰 뒤 결정한다.

2026-11-19 [복합 수정 준비 독립 리뷰 및 보완 지시](reviews/2026-11-19-s2-complex-task-preparation-independent-review.md)에서 PR #85의 대조 제출 9개와 예비 A 1개의 결과를 재현했다. R21은 편집 가능 여부를 뒤집어도 수량 과업 만점, R22는 유효 입력에서 제출이 던진 예외를 미지원으로 분류해 효과 비교가 보류되는 문제다. PR #85와 평가 실행 0/18을 유지하고 모델 호출 없는 채점 보완을 먼저 검토한다.

2026-11-19 [고정 입력 파일럿 독립 리뷰](reviews/2026-11-19-s2-fixed-input-pilot-independent-review.md)에서 세 원응답의 제출 지문과 52개 사례별 관측을 재현하고 PR #82를 병합했다. 조건당 첫 패치 하나가 모두 만점이었고 B/C는 A보다 입력 토큰을 각각 71.4%·83.3% 더 썼다. 다음 제안은 변경 전 도메인 지식이 필요한 복합 수정 과업에서 같은 예산의 성공 건수와 추가 비용을 비교하는 것이다. 후속 실행 범위는 미정이다.

2026-11-18 [Vendure 고정 입력 패치 파일럿](reviews/2026-11-18-s2-fixed-input-pilot.md)에서 도구 없는 독립 Codex 세션 실행 3/3·첫 응답 봉인 3/3·전체 소스 채점 3/3을 완료했다. 원본 22/52·참조 52/52를 재현했다. A/B/C 모두 타입 통과, 기존 16/16·변경 36/36이다. A/B의 적용 결과는 동일하고 C는 주문 상세 화면을 덜 수정했다. 본 비교의 실행 차단은 유지하며 결과 PR을 독립 리뷰에 인계한다.

2026-11-18 개발 세션이 수행할 [고정 입력 패치 파일럿 지시](reviews/2026-11-18-s2-fixed-input-pilot-instructions.md)를 작성했다. 조건별 독립 모델 응답 한 개씩을 기존 v4 평가기로 외부 채점한다. 지시 작성 시점의 파일럿 실행은 0/3이다.

2026-11-18 같은 VM 대조에서 사전 준비 후 EROFS 통과와 payload 시작 전 RTM_NEWADDR 오류를 확인했다. 검증한 PR #79를 fff4f52로 병합했다. [독립 리뷰](reviews/2026-11-18-s2-erofs-comparison-independent-review.md)

2026-11-18 추가 승인된 같은 VM 기준·대조에서 daemon 경로 mkdirat가 EROFS에서 EEXIST로 바뀌고 openat가 성공했다. 다음 차단은 bwrap loopback RTM_NEWADDR 권한 오류이며 payload 시작 전 exit 1이다. VM·소유 프로세스·watchdog 정리 완료, PR #79 독립 리뷰 대기다. [추가 VM 대조 결과](reviews/2026-11-18-s2-erofs-comparison.md)

2026-11-18 기준 VM에서 helper PID 2503의 mkdirat(/tmp/codex-daemon-22002, 0700) EROFS와 서비스의 /tmp ro를 확인했다. 실행 당시 분리된 execve 반환을 놓쳐 관리자 사전 준비·대조는 0회였고 VM·root·소유 프로세스·watchdog 부재를 확인했다. 저장 trace로 판독기를 보완했다. [EROFS 관측 결과](reviews/2026-11-18-s2-erofs-observation.md)

2026-11-18 사용자는 다음 제한 관측과 조건부 최소 조치의 개발 지시를 요청했다. [새 지시](reviews/2026-11-18-s2-erofs-observation-instructions.md)는 일회성 VM1개에서 기준 관측과 가설 확인 시 daemon 디렉터리 사전 준비 대조를 수행하는 범위다. 60~90분은 참고 예상이며 고정 상한이 아니다. 실제 실행은 개발 세션 과업이며 이번 작성에서는 수행하지 않았다. 문서 변경은 `pnpm check`의304개 테스트·타입 검사·예제 build와 링크/diff 검사를 통과했다. 리뷰의 잘한 점/개선점 구분은 가독성을 위한 것이며, 매번 회고나 수정 과업을 만들지 않도록 AGENTS를 정정했다.

2026-11-18 [EROFS 독립 리뷰](reviews/2026-11-18-s2-erofs-diagnosis-independent-review.md): **정적 진단 완료·추가 보완 결함 없음**. PR #76은 이미6042f23으로 병합됐으며, 고정 소스12개/발췌20개·공개 archive/파일4개 hash·provenance 연결·당시 원문·과거99파일과 pnpm check304를 재검증했다. 선두 후보는 canonical(/tmp)/codex-daemon-22002 생성이며 실제 실패 syscall은 미확정이다. 다음 제한 관측과 조건부 국소 조치를 한 과업으로 합의하는 방안을 권고하되 이번에 실행/설정 변경은 승인하지 않는다. 앞으로 리뷰에 잘한 점과 관리자 측 개선점도 포함한다.

2026-11-18 [EROFS 읽기 전용 진단](reviews/2026-11-18-s2-erofs-diagnosis.md): 선두 후보는 helper의 `canonical(/tmp)/codex-daemon-22002` 생성이며 **실패 경로는 아직 미확정**이다. 공개 npm archive integrity·release asset digest·당시 native/bwrap hash와 provenance/tag의 소스 commit c40729e를 연결했다. 고정 소스는 TMPDIR/daemon_auto_start와 무관하게 bwrap 인자 구성 전에 이 디렉터리를 준비한다. 외부 ProtectSystem=strict와 충돌 가능성이 높지만 당시 syscall/mount 상태가 없어 EROFS 해결로 판정하지 않는다. 다음 권고는 같은 조건의 최소 동적 관측이며 이번에는 구현/실행하지 않았다. pnpm check304·과거99파일 불변 확인, VM/실제 CLI/trace/model0이다. 아래는 당시 기록이다.

2026-11-18 사용자는 EROFS 쓰기 경로 진단의 개발 지시를 요청했다. [진단 지시](reviews/2026-11-18-s2-erofs-diagnosis-instructions.md)는 고정 CLI와 당시 소스·환경·정책 근거로 경로/연산 후보를 좁히는 읽기 전용 조사다. 구현·조사 순서는 개발 세션이 선택하며 30~60분은 참고 예상이고 확정 상한이 아니다. 이번은 지시 작성이며 실제 진단/실행 결과는 없다. `pnpm check`의 304개 테스트·타입 검사·예제 build와 새 문서 링크4개·diff 검사를 통과했다. 후속 trace·재실행·권한 변경은 결과 리뷰 뒤 결정한다.

2026-11-18 [R20 독립 리뷰](reviews/2026-11-18-s2-r20-cleanup-independent-review.md): **R20 해결·추가 병합 차단 결함 없음**. head3f3cc13에서 Python32·pnpm check304·역사 verifier/원래 반례·독립 복합 실패3개와 무한 출력 timeout을 확인했다. 과거99파일 bytes와 새4개 코드 hash 일치를 검증하고 PR #70을ca576e4로 병합했다. 다음은 고정 CLI의 EROFS 쓰기 대상 진단 범위·예산 합의다. 새 실제 실행/권한 변경0·PR #67/실제 인증/model/본 비교 보류·R11/H-O/H-F 미검증을 유지한다.

2026-11-18 [R20 보완 결과](reviews/2026-11-18-s2-r20-cleanup.md)(ADR-060): 진단 예산 소진·조회/저장 실패와 소유 정리 실행을 분리했다. 수정 전 가짜 VM 잔존을 재현했고 수정 후 실제 대체 stop/delete 완료·상태 제거를 확인했다. 명령 오류와 진단 오류·최종 부재 근거를 구분하며 불완전한 조회는 unconfirmed다. Python32·pnpm check304 통과, 원래 2008351 코드로 저장 증거 재검증·과거99파일 불변이다. 최신 main78ff102를 반영한 PR #70을 갱신하며 독립 보완 리뷰 전 미병합, PR #67 별도 보류다. 새 VM/실제 CLI/model 실행0, EROFS·R11 unresolved·H-O/H-F 미검증을 유지한다. 아래는 당시 기록이다.

2026-11-18 R20 지시 개정: [목적·완료 기준 중심의 새 지시](reviews/2026-11-18-s2-r20-outcome-instructions.md)가 이전 지시를 대체한다. 구현·검증 순서는 개발 세션에 맡기며 기존 45분·로컬 검증 범위와 보류 상태는 유지한다. 이번 작업은 지시문 작성이며 R20 구현은 진행하지 않았다. `pnpm check`의 304개 테스트·타입 검사·예제 빌드와 문서 링크 대상·diff 검사를 통과했다.

2026-11-18 개발 지시 운영 변경(ADR-059): 사용자와 합의해 [개발 지침](../AGENTS.md)의 지시 방식을 목적·완료 기준·필수 경계 중심으로 정리했다. 구현·진단·검증 순서와 범위 내 국소 수정은 개발 세션에 맡기고, 지시의 세부 방법 준수 자체를 리뷰 기준으로 삼지 않는다. 과도한 준비 gate와 첫 관측 전 구현 범위도 실패 원인으로 검토한다. 제품 코드·실험 경계·기존 예산과 보류 상태는 변경하지 않았다. `pnpm check`의 304개 테스트·타입 검사·예제 빌드와 diff 검사를 통과했다.

2026-11-18 [직접 VM smoke 독립 리뷰](reviews/2026-11-18-s2-vm-cli-smoke-independent-review.md): PR #70 head2008351의 **실제1회 blocked-before-payload·VM 폐기 근거는 확인**했다. 전체1530.223초·VM1/CLI sandbox1·payload0, EROFS 정확한 path는 미확인이다. pnpm check304·Python17·증거98파일/121674bytes·원시 outer/worker 연결·공개 cache4개를 재대조했다. 다만 진단 예산 소진이 safety stop/delete까지 SIGKILL하는 R20(P2)을 실제 정리 함수+가짜 외부 명령으로 재현했다. [45분 무실행 보완 지시](reviews/2026-11-18-s2-smoke-cleanup-budget-instructions.md)를 제공하며 PR #70은 보완 리뷰 전 미병합이다. 새 VM/정책/CLI 재실행0·PR #67 보류·R11 unresolved·H-O/H-F 미검증을 유지한다. 아래는 당시 기록이다.

2026-11-17 [직접 VM CLI smoke 결과](reviews/2026-11-17-s2-vm-cli-smoke.md)(ADR-058)는 **blocked-before-payload·정리 완료**다. 새 VM1개에서 전용 UID/GID22002·capability0/NNP·CPU2/4GiB/Tasks256·외부 route 없는 별도 network namespace를 확인한 뒤 고정 CLI sandbox1회를 실행했다. 명령 구성 중 `Read-only file system (os error 30)`/exit1, payload 표식·출력 없음으로 재시도 없이 중단했다. VM/소유 process/root와 watchdog 부재를 확인했다. pnpm check304·Python17·오프라인 부정4건 통과, 기존 코드/증거 불변이다. 정확한 실패 경로는 미관측이며 다음은 독립 리뷰다. 새 PR과 PR #67은 리뷰 전 미병합, R11 unresolved·R19 socket 미사용/미수정·인증/model/본 비교 보류·H-O/H-F 미검증을 유지한다. 아래는 당시 기록이다.

2026-11-17 사용자는 [직접 VM CLI 최소 호환성 시험](reviews/2026-11-17-s2-vm-cli-smoke-instructions.md)을 **총60분·새 VM1개·실제 sandbox 명령1회**로 승인했다(ADR-057). 15분은 중간 점검이며45분부터 새 실험을 중단하고 정리/검증/보고한다. 고정 도구·준비물과 최소 마감/폐기 수단을 재사용하고 R19의 실제 재사용 경로만 보완한다. 전체 비활성 runner·인증/socket 부정 대조·새 봉인/제출 수집·VM2 반복은 제외한다. 이번은 지시 작성이며 pnpm check304테스트·타입/예제 build와 문서 링크280개를 확인했다. 새 VM/CLI/인증/model 실행은 없다. 구현은 새 PR로 인계하고 독립 리뷰 전 병합하지 않는다. PR #67·전체 C안 채택·R11 해결·본 비교는 보류한다. 아래는 당시 기록이다.

2026-11-17 [C안 타당성 독립 리뷰](reviews/2026-11-17-s2-vm-cli-feasibility-independent-review.md): PR #67 head ed0250b의 **inconclusive 기록을 재현**했다. 90분 소진이 아니라15분 최소 구현 gate 미달로 VM0/단위0에서 중단했고 전체1831.075초였다. pnpm check304·Python98·18파일/과거3474파일·공개 cache4개 hash를 대조했다. 비활성 초안의 호스트 Python API와 Unix socket 디렉터리 권한 불일치(R19), 기존 watchdog 마감 예외를 확인했다. C안 불가능 근거는 없으며 검증 순서 축소를 권고한다. 새60분·VM1·payload1 호환성 시험은 미합의 제안이다. PR #67 미병합·새 runtime/인증/model0·R11 unresolved를 유지한다. 아래는 당시 기록이다.

2026-11-17 사용자는 **C안: 일회성 VM에서 CLI 직접 실행 + CLI 내부 sandbox 유지의 타당성 검증을 총90분 한도로 승인**했다(ADR-055). [개발 지시](reviews/2026-11-17-s2-vm-cli-feasibility-instructions.md)는 검증된 공개 준비물·고정 CLI를 재사용하고 정상/timeout/wrapper 사망/새 VM 정상 반복을 최대4단위·순차 VM2개 안에서 확인한다. 비특권 worker와 관리자를 분리하고 가짜 인증·로컬 네트워크 양성/음성 대조·전체 자손 종료 후 제한 수집을 검증한다. 이번은 지시 작성이며 pnpm check304테스트·타입/예제 build와 문서 로컬 링크277개를 확인했다. 새 runtime/인증/model 실행은 없다. C안의 전체 전환은 미확정이며 구현 PR은 독립 결과 리뷰 뒤 병합한다. R11 unresolved·production/live 거부·H-O/H-F 미검증을 유지한다. 아래는 당시 기록이다.

2026-11-17 [R18 보완 독립 리뷰](reviews/2026-11-17-s2-trace-context-independent-review.md): **R18 해결·추가 차단 결함 없음**. ade291f에서304+257검사·과거4개 verifier·기존 반례3개 및 독립 순서1036개를 확인했다. 실제 원래/후보 판정과 근거 유지, 새 파생 결과는 checkoutHead 제외 일치, 첫14/새17 index 대상·과거2379 verification 불변을 확인했다. PR #63을 검증한 head로 병합(0181606)했다. 오프라인 판독 보완은 완료하며 다음은 외부 컨테이너/VM과 내부 CLI sandbox의 책임 분담을 사용자와 논의한다. 새 runtime/추가 권한/인증/model/본 비교는 진행하지 않았고 R11 unresolved·H-O/H-F 미검증을 유지한다. 아래는 당시 기록이다.

2026-11-17 [R18 지연된 자식 문맥 보완](reviews/2026-11-17-s2-trace-context-fix.md): **로컬 보완 검증 완료·독립 리뷰 대기**다. 기준8bba520에 main35dbc3d를 통합하고 구현26c8b41에서 clone 반환 전·후의 exec/미지원 mount를 같은 bounded 문맥 검사로 처리했다. 128개/64KiB 상한·누락 시 inconclusive·부적격 거부의 별도 보존을 적용했다. 독립 반례는 두 순서 모두 inconclusive, 정상 지연 mount와 실제 원래/후보 판정은 유지한다. pnpm check304·Python243+새14=257(skip0)·과거4개 verifier 통과, 이전 파생/원문 불변·runtime0이다. PR #63을 갱신하고 독립 리뷰 전 미병합, R11/production/live·본 비교 보류를 유지한다.

2026-11-17 [오프라인 trace 판독 독립 리뷰](reviews/2026-11-17-s2-trace-reanalysis-independent-review.md): head8bba520에서304+243검사·과거4개 verifier·새14파일 hash·기존2364 verification 불변과 실제 파생 결과(checkoutHead 제외) 일치를 확인했다. 다만 R18은 자식 exec가 부모 resumed보다 먼저 출력되면 미지원 문맥을 놓쳐 next-blocked로 승격되는 반례다. 실제 고정 후보의 clone→mount 결론은 유지하며 PR #63은 보완 리뷰까지 미병합이다. [30분 오프라인 국소 지시](reviews/2026-11-17-s2-trace-context-fix-instructions.md)를 함께 제공한다. 새 runtime/권한/인증/model/본 비교는 보류하고 실행 경계 책임 논의는 별도로 진행할 수 있다. 아래는 당시 기록이다.

2026-11-17 [저장 trace 오프라인 보완](reviews/2026-11-17-s2-trace-reanalysis.md): **별도 판독 구현·검증 완료, 독립 리뷰 대기**다. 최신 main e358104에서 최종 구현695d7f1로 후보의 precheck41→42(64–65행)·명령 준비43→44(132행)와 자식 mount EPERM(110/178행)을 자동 연결했다. 새 파생 판정은 first-clone-passed-next-blocked, payloadStarted/lsmCauseConfirmed=false다. 기존 parser·원문·index·과거 inconclusive는 보존했고 기존4개 verifier는 이전 상태 그대로 통과했다. pnpm check304·Python 기존208+새35=243(skip0), 새 runtime/정책/credential/model0이다. PR은 결과 리뷰 전 미병합이며 R11 unresolved·production/live 거부·본 비교 보류를 유지한다. 아래는 당시 기록이다.

2026-11-17 [정책 대조 독립 리뷰](reviews/2026-11-17-s2-policy-pair-independent-review.md): **제한 대조·종료/회수 완료, 추가 병합 차단 없음**. head7a5eb53에서304+208검사·4개 verifier·134파일/Spec2/봉인2/회수4·final-source85/전달38·준비물4개 hash를 확인했다. 원문은 clone 통과 후 mount EPERM이며 자동 inconclusive는 미지원 혼합 줄 때문에 그대로 보존한다. PR #61을ee7ac98로 병합했다. [30분 오프라인 판독 지시](reviews/2026-11-17-s2-trace-reanalysis-instructions.md)를 함께 제공한다. 새 VM/정책 재시도 없이 저장 trace를 별도 재분석하고, 다음 실제 시험 전 외부/내부 sandbox의 책임·권한을 사용자와 논의한다. 추가 mount/권한·인증/model/본 비교 보류·R11 unresolved를 유지한다. 아래는 당시 기록이다.

2026-11-17 [기존 clone 한 행 정책 대조](reviews/2026-11-17-s2-policy-pair.md)(ADR-054): **원래1/후보1 관찰·정리 완료, 독립 리뷰 대기**다. 원래 두 bwrap clone은 EPERM, 후보의 같은 clone은 자식42/44를 만들고 mount(MS_SLAVE)가 EPERM으로 막혔다. 원문 검토는 first-clone-passed-next-blocked지만, 동결 parser가 strace attach 안내가 섞인 첫 반환 줄을 놓쳐 자동 판정은 inconclusive로 보존했다. payload 미시작·추가 정책/재시도0이다. 전체 Spec 두 개는 정확한 allow 한 행 차이로 검증됐고 두 service 봉인/회수·VM 정리 완료다. pnpm check304·Python208(새15)·과거3/새 verifier 통과. 새 PR은 독립 리뷰 전 미병합, R11/production/live·실제 인증/model/본 비교 보류를 유지한다.

2026-11-17 [최상위 정리 보완 독립 리뷰](reviews/2026-11-17-s2-cleanup-dispatch-independent-review.md): **R17 잔여 해결·추가 차단 결함 없음**. head153f887에서 pnpm check304·Python193·독립 dispatcher8사례·과거3개 verifier를 통과했고 새17파일 hash/기존2324증거 불변을 확인했다. 기존 실제7/7·Spec/봉인7개·회수9개를 유지한다. PR #54는 검증한 head로 병합(7f2f179)했다. R13~R17은 해당 fixture 범위 완료이며 다음은 [같은 정책 한 행 대조 재개 지시](reviews/2026-11-17-s2-policy-pair-resume-instructions.md)를 권고한다(45분·VM1개·원래1/후보1·cacheOnly). 이번 리뷰에서는 새 VM/정책 실행0회다. R11 unresolved·실제 인증/model/본 비교 보류·H-O/H-F 미검증을 유지한다. 아래는 당시 기록이다.

2026-11-17 [최상위 cleanup 호출 잔여 보완](reviews/2026-11-17-s2-cleanup-dispatch-fix.md)(ADR-053): **로컬 보완 검증 완료·독립 리뷰 대기**다. prepare/fixtures의 감사 기록 오류6개에서 cleanup0회인 결함을 재현하고, 기록과 finally의 단일 정리 호출을 분리했다. 최초/감사/정리/출력 오류를 보존하며 marker 유실 시에도 cleanup 등록 없는 seal을 거부한다. pnpm check304·Python193(기존174+새19, skip0)·과거3회차 verifier를 통과했다. 새 VM/runtime0이며 과거 실제7단위는 오프라인 재대조만 했다. PR #54 갱신 후 미병합·R11/production/live·정책 pair/인증/model/본 비교 보류를 유지한다. 아래는 당시 기록이다.

2026-11-17 [진단·봉인 보완 독립 리뷰](reviews/2026-11-17-s2-seal-recovery-independent-review.md): PR #54 head d970072에서 pnpm check304·Python174, 저장259파일·Spec/봉인7개·회수9개를 재현했다. final-source81/전달36파일·최초3230파일 중 예상 밖 변경0·보관 준비물4개 hash를 확인했다. R13/R14/R15/R16은 fixture 범위에서 확인됐고 실제7/7·VM 정리 완료다. 다만 R17은 최상위 감사 기록 오류가 cleanup 호출을 막는 잔여를 발견했다(prepare/fixtures의 6개 오류 주입에서 호출0회). [로컬60분 보완 지시](reviews/2026-11-17-s2-cleanup-dispatch-instructions.md)를 함께 제공하며 새 VM 없이 실제 dispatcher 회귀와 저장 증거를 검증한다. PR #54 미병합·정책/인증/model/본 비교 보류·R11 unresolved를 유지한다. 이번 리뷰는 구현 수정/새 VM 실행 없이 수행했다. 아래는 당시 기록이다.

2026-11-17 [진단/봉인/정리 보완 결과](reviews/2026-11-17-s2-seal-recovery.md)(ADR-052): **승인 범위 검증 완료·독립 리뷰 대기**다. R15 관리자 metadata 게시/실패 진단, R16 실제 service reference/봉인, R17 회수 오류와 VM 정리 분리를 보완했다. 새 VM1개·기본 정책 필수7단위 모두 기대 결과/120초 제한을 충족했고 raw Spec7개·service seal7개·단계별 회수9개를 저장/재대조했다. cache build/download/save0·import1, 소유 VM/임시 경로 정리 완료다. pnpm check304·Python174(기존146+새28, skip0)·과거2회차/새 verifier를 통과했다. PR #54를 갱신하고 독립 결과 리뷰 전 병합하지 않는다. R11 unresolved·production/live 거부·실제 credential/model/정책 pair/본 비교 보류·trialAuthorized/readyForTrial=false·results=null을 유지한다. 아래는 당시 기록이다.

2026-11-17 사용자는 R15 잔여·R16·R17의 보완 지시를 요청했다. [진단/봉인/정리 지시](reviews/2026-11-17-s2-seal-recovery-instructions.md)(ADR-051)는 회수 실패와 최종 정리 분리→관리자 metadata 게시→실패 진단 보존→service reference를 봉인까지 유지하는 순서다. 직전과 같은3시간·VM1개·기본 정책7단위·build0 상한을 적용한다. 이번은 지시 작성이며 구현/VM 시험은 하지 않는다. 작성 후 pnpm check304테스트·타입/예제 build와 문서 로컬 링크295개를 확인했다. 제품/실험 코드는 불변이다. 구현 PR #54는 보완 결과 리뷰 뒤 병합하며 정책 pair·권한 확대·실제 인증/model·본 비교는 보류한다. 앞으로 합의된 범위의 보완은 리뷰와 함께 지시문을 제공하고 중요한 방향/아키텍처·권한/비용 확대는 먼저 논의한다.

2026-11-17 [R13~R15 보완 독립 리뷰](reviews/2026-11-17-s2-execution-lifecycle-fix-independent-review.md): PR #54 head ff7ec19에서 pnpm check304·Python146·새123파일(분석5/closing4)·과거126파일 재현, final-source73/전달32파일 연결과 준비물4개 실제 hash를 확인했다. R14는 새 VM의 build/download0·import1 범위에서 해결됐다. R13은 실제 Spec 원문 유실로 부분 완료, R15는 전달 metadata 소유권/실패 진단 보존이 남는다. 정상1 start1/exit0/삭제1.566초 후 service 봉인 실패(R16), 필수7 기대통과0이다. 추가로 archive copy/export 호출 예외가 VM 정리를 건너뛰는 R17을 가짜 외부 명령으로 재현했다. PR #54 미병합·새 실행 예산 미승인·R11/production/live 차단·실제 credential/model/본 비교 보류를 유지한다. 이번은 코드/저장 증거 리뷰이며 새 VM 실행은 없다. 아래는 당시 기록이다.

2026-11-15 [R13–R15 보완 인계](reviews/2026-11-15-s2-execution-lifecycle-fix.md)(ADR-050): **부분 완료·blocked/inconclusive·자원 정리 완료**다. 실제 새 VM에서 기존 이미지 build/download 0회·import identity 일치와 준비52.764초를 확인했다(R14). 첫 정상 단위는 전체 Spec gate를 지나 start1/exit0·삭제1.566초까지 진행했으나 service 비활성 시각 확인 실패로 결과가 철회됐다. export도 전달 metadata의 관리자 소유권 검사에서 실패해 guest raw Spec/진단 archive가 없으므로 R13/R15는 부분 완료다. 필수7 중 시도1/기대통과0, 나머지6·pair·재시도0이며 실제 실패 뒤 코드 변경은 없다. pnpm check304·Python146(새30 포함)을 검증하고 PR #54를 갱신하되 독립 리뷰 전 병합하지 않는다. 공개 준비물만 유지하며 R11 unresolved·production/live 거부·trialAuthorized/readyForTrial=false·results=null이다. 아래는 당시 기록이다.

2026-11-14 사용자는 R13~R15 보완 지시 작성을 요청했다. [후속 지시](reviews/2026-11-14-s2-execution-lifecycle-fix-instructions.md)(ADR-049)는 PR #54의 이미지 조회 선행(R14), 고정 PATH와 엄격한 hook 환경 대조(R13), 검증된 수집 결과만 export(R15)를 정한다. 직전과 같은3시간 상한·로컬 회귀 우선·새 VM1개·기본 정책 필수7단위로 제한하고 선택적 실패 주입/정책 대조는 결과 리뷰 뒤로 둔다. 이번은 지시 작성이며 구현/VM 시험은 미실행이다. 작성 후 pnpm check304테스트·타입 검사·예제 build와 변경 문서의 로컬 링크252개를 확인했다. 제품/실험 코드는 변경하지 않았다. PR #54 보완은 게시 후 독립 리뷰를 기다리며 R11 unresolved·production/live 차단·실제 credential/model/본 비교 보류를 유지한다.

2026-11-14 공통 실행 보완 독립 리뷰: [PR #54 head f6fc386 검토](reviews/2026-11-14-s2-execution-lifecycle-independent-review.md)는 부분 완료·blocked/inconclusive에 동의하며 R13(runtime PATH로 보안 기능 탐지 실패), R14(이미지 조회 전 무조건 build), R15(거부된 원본을 export가 다시 수집)의 보완을 요구한다. cache 복구 뒤 해당 head에서도 pnpm check304·Python116·저장 증거 재현이 통과했다. final-source65파일 일치·최초2945파일 중 허용17변경·보관 준비물4개 hash를 확인했다. 실제 시도1/start0/필수7 기대통과0, 삭제0.854초/봉인1.236초만 검증됐으며 새 VM/정책 시험은 하지 않았다. PR #54는 미병합, R11/production/live 차단과 실제 credential/model/본 비교 보류를 유지한다. 아래는 당시 기록이다.

2026-11-14 후속 검증: 사용자 요청으로 누락된 Vendure 임시 cache의 고정 검증 입력만 복구했다. [복구 기록](reviews/evidence/2026-11-14-vendure-cache-recovery.json)에 따라 원본 inventory와 npm integrity/파일 hash를 대조해6,106파일·84,396,041바이트를 추가했고 기존 파일/링크를 덮어쓰지 않았다. 전체 설치·lifecycle script 실행은0회다. V2 원본4,735항목·Program1,638파일·진단0·anchor/input valid와 pnpm check304(skip0)·타입·예제 build 통과를 확인했다. 아래 지시 작성 당시의300통과/4실패 기록은 보존한다. PR #53의 검증 차단은 해소됐으며 새 lifecycle 구현의 검토와는 별개다.

2026-11-14 정책 재시도 독립 리뷰 후 사용자는 **준비물 재사용·공통 실행 수명주기·정책/식별자 비교를 새3시간에 정리**하기로 승인했다(ADR-047). [개발 지시](reviews/2026-11-14-s2-execution-lifecycle-instructions.md)는 검증된 공개 준비물만 보관하고 회차 VM/실행 상태는 새로 만들며, 사전 검사 실패도 독립 종료·삭제·수집 경로로 처리한다. 로컬 회귀→실제 필수7단위→조건부 원래1/후보1 대조 순서이며 선택적 마지막 실패 주입을 포함해 fixture 최대8·전체 최대10단위, VM1개다. 60/100/150/180분 마감·환경 진입 후 최대20분·준비물10GiB·단위120초를 적용한다. 이번 세션은 지시/맥락 문서 작성이며 보완 구현·새 VM/정책 시험은 미실행이다. 문서 로컬 링크278개와 타입/예제 build를 확인했으나 pnpm check는 기존 /tmp Vendure cache 파일 누락으로300통과/4실패다. 제품/테스트/실험 코드는 불변이며 cache는 수정하지 않았다. 실제 credential/provider/model·본 비교는 결과 리뷰 뒤 결정하며 R11 unresolved·R12 기존 범위·trialAuthorized/readyForTrial=false·results=null을 유지한다. 아래는 당시 기록이다.

2026-11-14 [공통 실행 수명주기 개발 인계](reviews/2026-11-14-s2-execution-lifecycle.md)(ADR-048): **부분 구현·blocked/inconclusive·소유 실행 자원 정리 완료**다. 공개 준비물4개(1.59GiB)의 실제 해시/manifest 재사용과 이미지 import identity를 검증했고 환경 준비는590.353초였다. 필수7단위 중 첫 정상 단위가 created Spec의 AppArmor 누락·rro→ro 차이로 시작 전 차단됐다. 생성1/start0, 삭제0.854초/단위 봉인1.236초를 확인했고 나머지6단위·원래/후보 대조는 실행하지 않았다. 실제 Node/CLI 바이너리 identity와 나머지 실패 경로는 미검증이다. Python116(새56+기존16+감사44)·production/live 거부·예제 build는 통과했지만 pnpm check는 기존 Vendure cache13파일 누락으로300통과/4실패가 유지된다. 검증 미완료로 PR 게시 후 병합 보류다. 준비물만 의도적으로 보관하며 다음은 독립 리뷰, 자동 재시도는 없다. R11 unresolved·trialAuthorized/readyForTrial=false·results=null을 유지한다. 아래는 당시 기록이다.

2026-11-12 [감사/deadline 보완과 정책 재시도](reviews/2026-11-12-s2-policy-retry.md)(ADR-046): **보완 검증 완료·시험 blocked/inconclusive·정리 완료**다. 정확한 closing 실행 등록/원자 포장과 같은 환경20분 절대 마감을 구현했다. VM 준비538.536초로 과거450초 차단을 넘었고, 원래 정책1회에서 clone EPERM을 재현했다. 후보 created Spec은 승인한 seccomp 한 행뿐이지만 미등록 MEMORY_PRESSURE_WATCH 감독자 경로 차이로 시작이 거부됐다. 후보 시작/커널 적용0회이며 실패 container 삭제181.412초는120초 계약 위반으로 별도 차단한다. 모든 소유 자원을 정리했다. pnpm check304·Python44(새31+기존13)·기존 S2 입력2,385파일 불변을 확인했다. 같은 후보를 자동 재시도하지 않고 부분 결과/추가 투자 가치를 리뷰한다. R11 unresolved·trialAuthorized/readyForTrial=false·results=null이다. 아래는 당시 기록이다.

2026-11-12 단일 정책 회차 독립 리뷰와 재개 승인: `5d723b4`의 부팅 전 중단/정리와58파일·13archive·내부657파일, 분석6/closing6 재현·기존1682파일 불변, pnpm check304·Python13테스트를 확인했다. 새 VM 실행은 하지 않았다. 미등록 실행 snapshot이 package에서 closing으로 자동 편입되는 결함을 임시 복제본으로 재현했고, 준비450초 종료 시 환경20분까지491.351초가 남았음을 확인했다. 사용자는 두 보완 후 동일 정책 한 행 시험 재개를 승인했다(ADR-045). [현재 지시](reviews/2026-11-12-s2-policy-retry-instructions.md)는 새45분 안에 명시적 closing 등록/거부·공통 환경 deadline 전달을 먼저 검증하고 원래1/후보1 대조를 수행한다. 추가 권한·credential/provider/model·본 비교는 리뷰 뒤 결정한다. 이번 세션은 지시 작성이며 보완 구현/정책 적용은 미실행이다. pnpm check304테스트·타입 검사·예제 build와 문서 로컬 링크267개를 확인했다. R11 unresolved·trialAuthorized/readyForTrial=false·results=null을 유지한다. 아래는 당시 기록이다.

2026-11-12 단일 정책 시험은 **inconclusive / bounded-stop-completed**다. [인계](reviews/2026-11-12-s2-single-policy-test.md)(ADR-044). VM 이미지 다운로드가 이전 helper에서 가져온450초 명령 상한에 걸려 부팅 전 중단됐다. 승인된 환경20분을 모두 사용한 실패는 아니다. VM 등록1회, 부팅/container/실제 OCI 대조/후보 적용/CLI/model 각각0회이며 소유 등록·전용 경로·불완전 cache를 정리했다. 과거 감사11+close1 및 이번 고정 분석6개/이후 closing 분리를 구현했다. pnpm check304·새 회귀13개·기존 trial/verification1,682파일 불변을 확인했다. 다음은 중단 결과와 새 준비 예산 리뷰다. R11 unresolved·readyForTrial/trialAuthorized=false·results=null을 유지한다. 아래는 당시 기록이다.

2026-11-12 namespace 독립 리뷰 및 단일 정책 시험 승인: main `1aefc85`의 원시 trace·실제 정책·실행 입력 연결을 대조해 proposal-ready에 동의했다. 증거66파일/16archive/내부665파일·기존2521파일 불변, pnpm check304·감사5테스트를 확인했고 새 VM 재실행은 하지 않았다. 저장 audit11개와 종료 snapshot 포함 최종12개의 개수 차이는 새 감사 범위 명시로 보완한다. 사용자는 **clone arg0=2013397009 추가 allow 한 행만 적용하는 새45분 시험**을 승인했다(ADR-043). [현재 지시](reviews/2026-11-12-s2-single-policy-test-instructions.md)는 동일 이미지/추적 옵션의 원래 정책1회와 후보1회, 시작 전 실제 OCI 한 행 차이 확인, 다음 차단에서 중단·종료/정리를 정한다. 추가 권한 확대·credential/provider/model·본 비교는 결과 리뷰 뒤 결정한다. R11 unresolved·trialAuthorized/readyForTrial=false·results=null을 유지한다. 이번 세션은 문서 작성이고 정책 적용/시험은 미실행이다. 작성 후 pnpm check304테스트·타입 검사·예제 build와 문서 로컬 링크256개를 확인했다. 아래는 당시 기록이다.

2026-11-11 namespace 진단: **proposal-ready, 독립 리뷰 대기**. [결과](reviews/2026-11-11-s2-namespace-diagnosis.md), [비활성 후보](reviews/2026-11-11-s2-namespace-policy-proposal.md). 동일 보안 정책의 기준1/추적1에서 bwrap namespace clone flags `0x78020011`·EPERM을 관찰하고 실제 seccomp mask와 대조했다. 정책 적용 없이 첫 차단점 후보를 문서로만 제시했으며 AppArmor 독립 기여/후속 mount 경계와 후보 충분성은 미확인이다. 소유 자원 정리, pnpm check304·새 증거5테스트, 기존 입력2521파일 불변을 확인했다. 비모델 CLI4회·새 정책/credential/provider/model/trial0, R11 unresolved·trialAuthorized/readyForTrial=false·results=null이다. 직전 전체 config 미열람 표현은 전체 TOML 파싱/허용값만 기록으로 새 보고서에서 정정했다. 다음은 결과 리뷰이며 아래는 당시 기록이다.

2026-11-11 CLI 차단 독립 리뷰 및 다음 진단 승인: main `bbb43c9`의 보고/구현/원시 기록을 대조해 **blocked 판정에 동의**했다. 증거68파일·20archive 무결성, pnpm check304테스트·S2 build·collector13/cleanup3 회귀를 확인했으며 새 VM 재실행은 하지 않았다. 올바른 CLI 명령과 unshare의 실패/실제 OCI 제한은 일치하지만 bwrap 첫 실패 syscall과 AppArmor의 독립 기여는 미확인이다. 전체 사용자 config 미열람이라는 보고 표현은 전체 TOML 파싱/허용 값만 기록으로 정정해야 한다. 사용자는 **동일 후보·기존 정책 유지·새60분의 원인 진단 및 비활성 최소 변경안 작성**을 승인했다(ADR-041). [개발 지시](reviews/2026-11-11-s2-namespace-diagnosis-instructions.md)는10/25/40/50/60분 점검과 정책 적용 금지를 명시한다. 실제 정책 변경·credential 전달·provider/model·본 비교는 결과 리뷰 뒤 별도 결정한다. R11 unresolved·trialAuthorized/readyForTrial=false·results=null을 유지한다. 이번 세션은 지시/맥락 문서 작성이며 진단은 미실행이다. 작성 후 pnpm check304테스트·타입 검사·예제 build와 문서 로컬 링크242개를 확인했다. 아래는 당시 기록이다.

2026-11-11 CLI 비모델 타당성 결과: **blocked, 독립 리뷰 대기**. [인계](reviews/2026-11-11-s2-cli-feasibility.md). 고정 CLI는 기동했지만 비특권 container의 native sandbox namespace 생성이 거부됐다. parent 허용 작업은 성공했고 올바른 profile의 payload는 시작하지 못했다. 준비2컨테이너·비모델 CLI10회(성공6/실패4), 정상 경계2회/timeout/네트워크 검증·lifecycle 등록은0회다. 권한 확대 없이 환경 단계에서 탐색을 중단했고 소유 자원을 정리했다. pnpm check304테스트·S2 build·collector13/cleanup3·과거 실제 fixture의 production/live 거부 회귀를 통과했다. R11 unresolved·trialAuthorized/readyForTrial=false·results=null, 실제 credential 전달/로그인/갱신/provider/model/본 비교 각각0회를 유지한다. 다음은 실패 증거 리뷰와 재개 조건 선택이며 아래는 당시 기록이다.

2026-11-11 CLI 비모델 타당성 검증 승인: 사용자는 **기존 container 안의 CLI 본체/명령 sandbox 분리, 가짜 인증·내부 서버 검증과 새90분 상한**을 승인했다(ADR-039). [개발 지시](reviews/2026-11-11-s2-cli-feasibility-instructions.md)는 실행별 상태/설정·셸 HOME 분리, 가짜 인증의 직접/환경/FD 접근 거부, parent 양성 서버 대조와 sandbox 네트워크 차단, 새 정상2단위·timeout/정리를 요구한다. 환경20분/핵심45분/탐색70분/총90분이며 실제 자격 증명 전달·로그인/갱신/provider·모델 호출·본 비교는 결과 리뷰 뒤 별도 결정한다. 이번 세션은 지시·맥락 문서만 작성했고 CLI/VM 검증을 실행하지 않았다. pnpm check(304테스트·타입 검사·예제 빌드), pnpm s2:build, 문서 로컬 링크233개를 확인했다. R11 unresolved·R12 기존 범위·production/live 거부·trialAuthorized/readyForTrial=false·results=null을 유지한다.

2026-11-11 Linux 평가 독립 검토: main `bcab22e`의 보고·구현·원시 증거를 대조해 **linux-evaluation-reproduced**에 동의했다. 증거210파일/16archive 내부993파일 hash, 실제7단위 재대조 차이0, common9경로와 역사적 Program hash 대응, 입력109,157항목 불변성과 실행본·전체 종료 이후 수집·17등록 단위 정리를 확인했다. pnpm check304테스트·타입/예제 build, S2 build, Python26회귀와 production/live 승격 거부도 통과했다. 새 VM 설치/평가 재실행은 하지 않았으며 검토 범위의 추가 차단 결함은 없었다. 기존 외부 파일의 `<typescript>/<basename>` 축약은 후속 기술 부채로 남긴다. 아래는 리뷰 전 인계 기록이다.

2026-11-11 S2 Linux 평가: **linux-evaluation-reproduced, 독립 리뷰 대기**. [인계](reviews/2026-11-11-s2-linux-evaluation.md). 고정 Linux 설치/common build와 기존 `openEnvironment()`를 통과했고 새 경계의 필수7단위·공개 타입4회·timeout/유한 writer 대조·공유 lifecycle 실제5회귀를 확인했다. macOS common 선언9개의 경로 표기 차이를 원문/동일 hash로 분류하고 정확한 대응표를 새 검증 전에 고정했다. 최초/중간3단위와 최종7단위의 분모를 분리했다. 전체17개 등록 단위·VM·새 cache를 정리했고 pnpm check304테스트, Python26회귀를 통과했다. R11 unresolved·R12 기존 범위·production/live 거부·trialAuthorized/readyForTrial=false·results=null·실제 CLI/model/provider/본 비교0회를 유지한다. 다음은 결과 리뷰이며 아래는 각 시점의 기록이다.

2026-11-11 Linux 평가 재현 검증 승인: lifecycle fixture의 독립 검토 후 사용자는 **같은 경계의 Linux Vendure baseline/reference 재현과 새3시간 상한**을 승인했다(ADR-037). [개발 지시](reviews/2026-11-11-s2-linux-evaluation-instructions.md)는 Linux 불변 환경1회 준비·읽기 전용 완전 소스·실행별 새 평가 container·출력만 수집하는 구조다. baseline/reference 각2회·부정2종·reference delta1회, 공개 타입 검사·timeout 통합·macOS/반복/입력 방식 대조를 확인한다. 환경45분/핵심90분/탐색150분/총180분이며 기존 Program hash 검사·평가 의미를 유지한다. 이번 세션은 지시·맥락 문서 작성이고 Linux 설치/평가는 미실행이다. pnpm check(304테스트·타입 검사·예제 빌드), pnpm s2:build, 문서 로컬 링크224개를 확인했다. 실제 CLI·인증/provider·본 비교는 결과 리뷰 뒤 별도 진행하며 R11 unresolved·R12 기존 범위·trialAuthorized/readyForTrial=false·results=null을 유지한다.

2026-11-11 lifecycle 독립 검토: main `d840669`의 코드·최종25개 원시 기록·종료/수집/결과 철회·두 VM83개 등록 단위 정리 증거를 대조했고 검토 범위에서 새 차단 결함 없이 fixture-boundary-passed에 동의했다. 구현20/증거774/archive 내부3,202파일 hash, pnpm check304테스트·타입/예제 build 및 Python16회귀를 확인했다. VM을 재생성한 독립 실행은 아니며 RuntimeMaxSec 도달/불명확 create 중 감독자 사망의 실제 주입은 미검증이다. 이 검토가 R11 전체 해결이나 Linux/실제 agent 검증을 대신하지 않는다. 아래 인계는 독립 리뷰 전 기록으로 보존한다.

2026-11-11 S2 lifecycle fixture: **fixture-boundary-passed, 독립 리뷰 대기**. [인계](reviews/2026-11-11-s2-lifecycle-fixture.md). 독립 systemd 감독자·실행별 persistent slice·전체 종료 후 manager 수집을 구현했다. 수정본의 필수24개와 공개 직후 감독자 사망1개가 통과했고, 정상/timeout/래퍼 사망은 각각2회다. 늦은 쓰기를 허용했던 최초 supervisor 실패와 공개 직후 실패 경로를 보완하고 두 VM의83개 등록 단위/소유 자원을 정리했다. pnpm check304테스트와 Python16회귀, 실제 fixture의 production/live 승격 거부를 확인했다. R11 unresolved·R12 기존 범위·trialAuthorized/readyForTrial=false·results=null·실제 모델/provider/본 비교0회를 유지한다. 후속 Vendure/실제 CLI/평가 준비는 결과 리뷰 뒤 별도 결정한다. 아래는 각 시점의 기록이다.

2026-11-10 R11 fixture 경계 검증 승인: smoke 결과의 독립 대조 후 사용자는 **독립 게스트 감독자·실행별 cgroup·전체 종료 확인 뒤 관리자 수집**과 새3시간 상한을 승인했다(ADR-035). [개발 지시](reviews/2026-11-10-s2-lifecycle-fixture-instructions.md)는 환경20분/핵심 경로90분/탐색150분/마감180분, 정상·timeout·래퍼/감독자 사망·수집 실패/다음 실행 격리 검증을 정한다. fixture 전용 결과만 만들고 기존 production/live 경로는 계속 거부한다. 이번 세션은 지시·맥락 문서 작성이며 경계 구현/실험은 미실행이다. pnpm check(303테스트·타입 검사·예제 빌드)와 문서 로컬 링크215개를 확인했다. 성공해도 Vendure·실제 CLI/provider·평가·본 비교는 결과 리뷰 뒤 별도로 정한다. R11 unresolved·R12 기존 판정·trialAuthorized/readyForTrial=false·results=null을 유지한다.

2026-11-10 동일 후보 최소 실행: **smoke-passed, 결과 리뷰 대기**. [인계](reviews/2026-11-10-s2-container-smoke.md). 현재 native image target→config→rootfs chain→실제 container를 연결했고, 비특권 셸/Node22.19.0 반복·exit7 전달·Codex0.167.0-alpha.3.2 version/help를 새4컨테이너에서 확인했다. chain ID 검증식의 국소 수정1회와 실패본을 보존했다. 환경 청구477.002초/이전 합산1,728.267초, 유료0이며 VM/image/새 cache를 모두 정리했다. 호스트303테스트(skip0) 통과. R11 unresolved·R12 기존 범위·trialAuthorized/readyForTrial=false·results=null·실제 모델/provider/본 비교0회를 유지한다. Vendure 준비나 종료/수집/평가 adapter는 시작하지 않았고 다음 범위·예산은 리뷰 뒤 결정한다.

2026-11-10 동일 후보 최소 실행 재검증 승인: 사용자는 Lima/VZ + containerd/nerdctl을 유지해 **이미지 식별자 수정과 모델 없는 최소 실행을30분 한도**로 확인하기로 했다(ADR-033). [개발 지시](reviews/2026-11-10-s2-container-smoke-instructions.md)는20분 탐색/10분 검증·정리·인계, 원인을 확인한 국소 재시도, image target과 실제 container 연결, 비특권 셸·Node·CLI version/help를 요구한다. 이번 회차의 누적 비용을 이전 실패와 분리 기록하며 기존90분/4시간을 재개하지 않는다. 성공해도 Vendure 준비·R11 adapter/평가·실제 모델/본 비교로 진행하지 않고 결과 리뷰를 기다린다. 이번 세션은 지시·맥락 문서 작성이며 실제 재검증은 미실행이다. pnpm check(303테스트·타입 검사·예제 빌드)와 문서 로컬 링크200개를 확인했다. R11 미해결·R12 기존 판정·trialAuthorized/readyForTrial=false·results=null을 유지한다.

2026-11-10 컨테이너 타당성 조사: **inconclusive, R11 차단 유지**. [인계](reviews/2026-11-10-s2-container-feasibility.md). Lima/VZ VM과 Linux 준비 이미지 build는 성공했지만 로컬 image 식별자 호출 오류와 수정1회 실패로 중단했다. CLI/종료·접근·수집/평가 probe와 Linux Vendure 설치·평가는 미실행이다. VM/image/cache는 정리했고 후보1개·신규 비용0, 환경 준비 보수적20분51초/90분을 기록했다. 호스트303테스트(skip0)·비교4/4·18 usage fixture·84배포/4735원본 hash와 production 거부를 확인했다. R12 기존 판정과 모델/평가 계약은 유지한다. 다음은 같은 후보의 이미지 연결 수정에 새 한정 예산을 줄지 결과 리뷰에서 결정하는 단계다. 실제 모델/본 비교0회·trialAuthorized/readyForTrial=false·results=null이다.

2026-11-10 컨테이너 경계 타당성 검증 승인: 사용자는 **일회성 컨테이너 우선·기존 CLI/셸 유지**로 진행하기로 했다(ADR-031). [개발 지시](reviews/2026-11-10-s2-container-feasibility-instructions.md)에 총4시간·환경 준비90분·마지막30분 마무리·후보1개·신규 유료 비용0과 중단/부분 인계 기준을 정했다. 모델 없는 실행/평가 단위 종료·권한·전체 수집·Linux 환경/기존 평가 재현을 확인한다. 이번 세션은 지시·맥락 문서 작성이며 컨테이너 설치/실험을 수행하지 않았다. pnpm check(303테스트·타입 검사·예제 빌드)와 문서 로컬 링크196개를 확인했다. R11은 미해결이고 R12 해결 판정을 유지한다. 본 비교는 결과 리뷰 이후이며 실제 모델/본 비교0회·trialAuthorized/readyForTrial=false다.

2026-11-10 R11/R12 독립 재검토: **R12 검증 범위에서 해결, R11 미해결·실제 비교 차단 유지**. [독립 보고](reviews/2026-11-10-s2-runtime-accounting-independent-review.md).303테스트(skip0)·비교4/4·29제출60파일·참조52사례/trace를 재현했다. usage 순차 조합3,279개·추가20사례·기록18fixture가 일치했고 macOS22실행의 늦은 쓰기8건과 production 차단을 재확인했다. agent84파일·세 ID와 execution manifest 재생성도 일치했다. 추가 차단 결함은 발견하지 않았으며 지시의 ‘R12 완료 + R11 차단 인계’는 충족했다. 다음은 사용자와 R11 실행 경계/허용 도구 정책을 결정한다. 새 플랫폼·API를 채택하지 않았고 실제 모델/본 비교0회·trialAuthorized/readyForTrial=false·사람 검토 pending을 유지한다. 아래는 당시 자체 검증 기록이다.

2026-11-10 R11/R12 보완: **R12 구현·자체 검증 완료, R11 종료 경계 unresolved**. [인계](reviews/2026-11-10-s2-runtime-accounting-fix.md). turn 상태·중복 철회·unknown 입력/overflow·종료/EOF/절단을 결합했고303테스트(skip0)·비교4/4·29제출60파일 일치를 확인했다. 현재 runtime은 정상 부모 종료에도 모든 writer의 정지를 증명하지 못하므로 production 수집/평가와 전체 usage 확정을 차단한다. 진단과 알려진 참조 교정을 분리했으며 실제 macOS 반복에서 detached/손자/열린 핸들의 늦은 쓰기를 재현했다. TASK/B/C84파일·모델·세 ID는 그대로다. 다음은 독립 리뷰와 R11의 별도 경계/도구 정책 선택이다. 새 플랫폼·API·권한을 도입하지 않았고 실제 모델/본 비교0회, trialAuthorized/readyForTrial=false·results=null·사람 검토 pending을 유지한다. 아래는 각 시점 기록이다.

2026-11-10 R11/R12 보완 지시: 사용자가 기존 CLI·macOS 범위의 보완을 승인했다. [개발 지시](reviews/2026-11-10-s2-runtime-accounting-fix-instructions.md)는 종료 확인→전체 제출 수집 경계, turn 상태 기반 usage·불완전 계측, 실제 모델 없는 회귀와 새 실행 증거 동결을 다룬다. API/새 플랫폼·token hard cap 확대 없이 진행하며, native 경계가 성립하지 않으면 R12 완료와 R11 차단을 구분해 인계한다. 이번 변경은 지시·맥락 문서 작성이며 R11/R12를 수정한 것이 아니다. pnpm check(252테스트·타입 검사·예제 빌드)와 문서 내 로컬 링크 경로153개를 확인했다. 본 비교는 보완 결과 리뷰 뒤 진행하고 trialAuthorized/readyForTrial=false를 유지한다.

2026-11-10 S2 실행 전 준비 독립 리뷰: **자료/평가 방향 유지, R11 종료 차단 재현·R12 usage 완료 판정 보완 필요**. [독립 보고](reviews/2026-11-10-s2-trial-preparation-independent-review.md).252테스트(skip0)·비교4/4·29제출60파일/준비157파일 재현, 실제 A/B/C84파일·공개/private 타입7제출·참조 snapshot52사례를 확인했다. B68view와 C의12해석/22주장/30인용/방향 관계를 대조했고 사람 승인은 pending이다. detached 자손의 deadline 뒤 쓰기가 재현됐으며, 모순된 완료 이벤트가 후속 미완료 turn을 가려 usage를 complete=true로 만드는 새 반례를 확인했다. token hard cap 제외·API 확대 없음은 유지한다. 다음은 두 경계 보완과 C 사람 검토/실제 CLI 미검증 조건 확인이다. 실제 모델/본 비교0회, trialAuthorized/readyForTrial=false다. 아래는 당시 기록이다.

2026-11-10 S2 실행 전 준비: **자료·평가·계측 준비 구현, 전체 실행 환경은 차단 상태**. [인계](reviews/2026-11-10-s2-trial-preparation.md). 사용자 후속 결정에 따라 token hard cap을 필수 조건에서 제외하고30분 제한·raw usage/누락/참고선 초과 기록을 채택했다. 동일 TASK/공개 안내, 일반 문서 C와68view·1511단위 대응/사람 검토 묶음, 공개 타입 검사, 실행/수집 대역을 구현했다.252테스트(skip0)·비교4/4,29제출60파일·새 준비157비시간 파일 재현, A/B/C 실제 배포를 확인했다. 모델12항목/16링크·승인0과 B68view는 유지했고 agent 자료는84파일·새 bundleId다. macOS 파일/네트워크 거부와 package.json 예외의 명시적 차단을 검증했지만 **분리된 자식 프로세스의 종료 탈출**이 남아 실제 실행과 불변 제출 보장을 차단한다. 실제 모델 호출0·본 비교0, trialAuthorized/readyForTrial=false·results=null·사람 동등성/의미 검토 pending이다. 다음은 종료 경계 보완과 독립/사람 리뷰이며 API·새 플랫폼 투자는 하지 않았다. 아래는 각 시점 기록이다.

2026-11-10 S2 실행 전 준비 승인: 사용자가 **무요청 종료 정책·일반 설명 문서 C·기존 제한 평가·동일 설정 각3회** 조합을 승인했다(ADR-028). 다음 개발 세션은 [비교 실행 전 준비 지시](reviews/2026-11-10-s2-trial-preparation-instructions.md)에 따라 과업/실행 계약, C 양방향 의미 대응·사람 검토 자료, 격리/계측 환경, 새 배포 동결을 준비한다. 이번 세션은 지시·현재 맥락 문서만 작성했고 문서 링크200개와 pnpm check(230테스트·타입 검사·예제 빌드)를 확인했다. 이는 후속 준비 구현의 검증이 아니다. 본 비교는 준비 결과의 독립 리뷰 후 별도 진행하며 실제 비교 agent 실행·사람 의미 승인·H-O/H-F·S3는 수행하지 않았다. trialAuthorized/readyForTrial=false를 유지한다. 아래는 각 시점 기록이다.

2026-11-10 S2 modal 독립 재검토: **R9 잔여 해결, R8/R10 해결 유지, S2 준비 구현 보완 완료**. [독립 보고](reviews/2026-11-10-s2-modal-independent-review.md). 230테스트(skip0)·비교4/4·24제출50파일/새 준비147비시간 파일 재현, 기존 독립 modal 두 반례의 진단0 후 payload 실패, complete-root/delta의 요청·trace 일치와 실제 RxJS 경계를 확인했다. agent142파일·세 ID·모델/근거는 유지됐다. 검토 범위 내 추가 결함은 확인하지 않았다. 다음은 사용자와 과업 정책·B/C 의미 동등성·제한된 평가 범위·실제 격리/agent 실행 조건을 확정하는 단계다. readyForTrial=false·본 비교/H-O/H-F/S3 미실행을 유지한다. 아래는 당시 기록이다.

2026-11-09 R9 modal 연결 보완: **구현·자체 검증 완료, 독립 재검토 대기**. [인계](reviews/2026-11-09-s2-modal-fix.md), [평가 v3](../experiments/domain-model/s2/evaluation/TASK-REVIEW.md). 제출 부모의 실제 constructor identity/locals로 dialog를 구독 시 실행하고 resolve→부모→요청을 연결했다. 주문 ID/active 반례는 진단0 후 payload 실패이며 기존 R8/R10·13결함도 유지한다. 전체230테스트(skip0)·비교4/4,24제출50파일/modal trace 재현, 완전한 제출 CLI와 delta의 판정/요청/trace 일치, 기존 agent142파일·세 ID/모델 보존을 확인했다. 다음은 잔여 R9의 독립 재검토다. readyForTrial=false·미정 정책/사람 검토/격리/agent 조건을 유지하고 본 비교·H-O/H-F·S3를 수행하지 않았다. 아래 기록은 각 시점의 상태다.

2026-11-09 R9 modal 보완 지시: 사용자가 잔여 데이터 전달 문제의 개발 지시 작성을 요청했다. 다음 개발 세션은 [modal 연결 보완 지시](reviews/2026-11-09-s2-modal-fix-instructions.md)를 따른다. 실제 component/locals로 dialog를 실행하고 resolve 결과를 부모 흐름에 연결하며, 주문 ID/active 변형을 타입 통과 후 payload assertion에서 거부한다. 기존 R8/R10·13동작 결함·모델/배포 경계를 유지한다. 이번 세션은 지시·맥락 문서만 작성했으며 구현·본 비교·미정 정책 동결은 하지 않았다. 문서 링크와 pnpm check(214테스트·타입 검사·예제 빌드)를 확인했으며 이는 잔여 결함 수정의 검증이 아니다. readyForTrial=false다.

2026-11-09 S2 보완 독립 재검토: **R8/R10 해결, R9 부분 해결**. [최신 독립 리뷰](reviews/2026-11-09-s2-contract-independent-review.md). 214테스트(skip0)·비교4/4·22제출46파일/준비147파일 재현,142 agent 파일·세 ID·실제 A/B/C workspace hash를 확인했다. 그러나 modal 대역이 실제 component/locals를 무시해 부모의 잘못된 주문 ID·active 전달도 타입 진단0·52/52·sourceBinding=true로 통과한다. 같은 제출 메서드에 실제 전달값을 연결하면 잘못된 주문 취소/부분 취소 lines 누락이 관찰된다. 다음은 이 R9 데이터 전달 경계 보완·재검토이며 큰 구조 변경은 필요하지 않다. 준비 전체 완료/본 비교는 보류, readyForTrial=false·미정 정책/격리/agent 조건을 유지한다. 아래 인계는 당시 자체 검증 기록이다.

2026-11-09 S2 R8/R9/R10 보완: **구현·검증 완료, 독립 재검토 대기**. [인계](reviews/2026-11-09-s2-contract-fix.md), [평가 v2 계약](../experiments/domain-model/s2/evaluation/TASK-REVIEW.md). 완전한 제출/명시적 delta를 구분하고 원래 타입 문맥·추가 helper와 실행 snapshot을 hash로 결합했다. 요청 payload를 독립 기대값과 대조하고 환불만/혼합 환불 reason을 보존한다. 전체214테스트(skip0)·비교4/4, 22제출 교정 반복, 준비147파일 재현을 확인했다. baseline 진단0·보존16/16, 새 참조/helper 진단0·52/52, 역사적 참조 진단5 거부, 동작 결함13종은 타입 통과 후 검출했다. 기존142 agent 파일·세 ID는 그대로이며 evaluator run-plan만 갱신했다. 독립 reviewer의 해결 판정을 대신하지 않으며 readyForTrial=false·본 비교 미실행·H-O/H-F 미검증을 유지한다. 아래 기록은 각 시점의 상태다.

2026-11-09 S2 보완 지시: 사용자가 R8/R9/R10 보완 작업 지시 작성을 요청했다. 다음 개발 세션은 [S2 평가 계약 보완 지시](reviews/2026-11-09-s2-contract-fix-instructions.md)를 따른다. 제출 타입/구문 검사와 동작 판정을 분리하고, 유효한 참조 수정·핵심 요청 인자 검증·환불만 경로 보존을 먼저 완료한다. 동작 결함 변형은 타입 검사 통과 후 해당 assertion에서 거부해야 한다. 이번 세션은 지시·맥락 문서만 작성했으며 구현/과업 최종 동결/본 비교는 하지 않았다. 문서 링크와 pnpm check(196테스트·타입 검사·예제 빌드)를 확인했다. 이는 보완 구현의 검증이 아니다. readyForTrial=false와 기존 합의 구조를 유지한다.

2026-11-09 S2 준비 독립 리뷰: **방향·세션/모델/조회/배포 구조 유지, 평가기 R8/R9와 참조 수정 R10 보완 필요**. [독립 보고](reviews/2026-11-09-s2-preparation-independent-review.md). 196테스트(skip0)·비교4/4·새 준비 두 번 및 커밋 결과의147비시간 파일/세 ID 일치, 12항목/16링크·A/B/C 배포 hash를 확인했다. 그러나 참조 수정은 oracle24/24에도 실제 TS 진단5개가 있고, 잘못된 주문 ID·환불 결제/금액 변형도24/24를 통과한다. 환불만+공백 reason 보존 사례에서는 참조 수정이 회귀한다. 준비 전체 완료는 보완 재검토까지 보류하며 readyForTrial=false다. H-O/H-F·사람 의미 승인·본 비교·S3는 미검증이다. 아래 개발 인계와 과거 리뷰는 당시 기록이다.

2026-11-08 S2 준비 구현: **구현·실제 배포 자료·제출 코드 oracle·재현 검증 완료, 독립 리뷰 대기**. [인계 보고](reviews/2026-11-08-s2-preparation.md), [모듈/명령](../experiments/domain-model/s2/README.md). 단일 Program 세션·동결 모델·순수 조회로 기존 12항목/16링크와 승인0을 보존하고 B/C 자료를 만들었다. 전체196테스트(skip0)·비교4/4·두 준비의 비시간147파일/세 ID 일치, baseline/참조 수정/6결함 변형 검증을 확인했다. **readyForTrial=false**이며 본 비교는 실행하지 않았다. 다음은 과업 실패 처리·B/C 의미 동등성·oracle 원문 충실성의 독립 검토와 agent 버전/예산·실제 격리 동결이다. H-O/H-F·사람 의미 승인·S3는 미검증이다. 아래 기록은 각 시점의 상태를 보존한다.

2026-11-08 S2 구조 합의·개발 지시: 사용자는 단일 준비 세션, 동결 모델/순수 조회, 사전 생성 view와 동일 파일 도구, 타입 검사되는 실험 내부 모듈 구조를 승인했다(ADR-024). **다음 개발 세션은 [S2 준비 구현 지시](reviews/2026-11-08-s2-development-instructions.md)를 따른다.** 선행 부채→세션→모델→조회→B/C 제공 자료→평가 하네스/실행 명세→독립 리뷰 인계 순서다. 이번 리뷰는 문서만 작성했고 구현/본 비교는 미실행이다. 미정 실행 조건은 준비 자료로 만들어 별도 동결하며 변경 후 모델 갱신은 S3로 유지한다.

2026-11-08 S2 범위 결정: 사용자는 **변경 전 모델의 agent 수정 지원 효과부터 검증**하기로 했다(ADR-023). [선행 부채·분석 세션/모델/조회 아키텍처 제안](reviews/2026-11-08-s2-architecture-proposal.md)을 작성했다. 단일 준비 세션·동결 모델·순수 조회/사전 생성 view·실험 내부 모듈은 아직 합의 전 권고다. 구조 합의 뒤 개발 지시를 작성하며, 이번에는 제품 구현·S2 실행을 하지 않았다. 코드 변경 후 모델 유지/갱신은 S3 범위로 둔다.

2026-11-08 구현 아키텍처 감사: **조사 완료 / 다음 아키텍처·개발 지시는 미확정**. [상세 평가와 논의 안건](reviews/2026-11-08-architecture-audit.md). 기존 Vendure cache의 3회 측정에서 V2 전체 중앙값 8.25초, 역할 추출 5.60ms/FCA 0.67ms였고 Program·입력 감사의 3중 실행을 확인했다. core scan JSON은 약 23MB다. snapshot 수명주기, 탐색 관계/근거 의존 분리, ID·freshness·agent 조회 계약을 우선 논의하도록 권고한다. 174테스트·타입 검사·예제 빌드, 새 V2 마지막 실행의 비시간 15파일 일치 확인. 제품 구현·과거 증거는 그대로이며 S1/R6/R7 완료를 유지한다.

2026-11-08 V2 독립 리뷰: **R6/R7 해결, S1 보완 완료 인정**. 174테스트·비교 4/4·새 V2 15파일/V1 12파일 일치, 12개 ID 탐색과 standalone 5상황·제공 hash 9개를 확인했다. [최신 독립 리뷰](reviews/2026-11-08-domain-model-contract-independent-review.md). 사용자 요청에 따라 다음 단계의 큰 아키텍처·구현 범위는 대화로 정한 뒤 착수한다. S2와 agent 효용 검증은 아직 미실행이다.

2026-11-08 R6/R7 보완: **V2 구현·회귀 검증 완료, 독립 재검토 대기**. incoming/outgoing 한 단계 탐색과 전체 분석 입력/anchor 분리 검사를 제공한다. 모델 의미·78×6 context·후보5/추가 의미0은 유지한다. [최신 사용 경로](../experiments/domain-model/v2/README.md). [검증 인계](reviews/2026-11-08-domain-model-contract-fix.md): 174테스트·기존 비교4/4·15비시간 파일 재현 통과. S2는 미실행이다. 아래 리뷰/관찰은 당시 상태로 보존한다.

마지막 갱신: **2026-11-08, Asia/Seoul**.

## 현재 단계

2026-11-08 S1 독립 리뷰: **방향 유지 / S1 조건부 완료, R6/R7 Medium 보완 필요**다. PR #15/main `4480438`에서 163테스트·기존 비교 4/4·비시간 12파일 재현·64부분집합 FCA 독립 대조가 통과했다. R6은 개념→동작 안내와 relatedItems 방향 불일치, R7은 standalone validator의 대상 선언/분석 입력 변경 미검출이다. 전체 runner의 입력 검사는 R7 변조를 거부하며 기존 고정 결과의 오류는 아니다. [최신 독립 리뷰](reviews/2026-11-08-domain-model-independent-review.md), [현재 보완 지시](reviews/2026-11-08-domain-model-review-next-plan.md)를 따른다. 이번 리뷰는 제품/실험 구현을 고치지 않았고 원시 결과를 보존했다. S2는 보완 재검토 뒤 계약·fixture/oracle를 동결한다.

2026-11-08 S1 구현: **Vendure 도메인 모델 12항목·근거 검증기·동일 context의 단순 그룹/FCA 대조를 완료**했다. 모두 검토 대기이며 승인 지식은 없다. 네 클래스 78메서드×6역할(468셀, unknown 0)에서 형식 개념 8/후보 5를 얻었지만 후보 전부 단순 그룹과 extent가 같다. 새 의미 항목/추가 교집합은 0이다. 정상 검증·변조 8개 거부·27개 새 회귀, 전체 163테스트·기존 비교 4/4, 비시간 12파일 재현이 통과했다. [최신 인계](reviews/2026-11-08-domain-model-prototype.md), [실험/모델](../experiments/domain-model/README.md). 다음 권고는 독립 리뷰 후 S2 reason 계약·fixture/oracle 동결이다. S2 비교·Vendure 변경·사람 승인·agent 효용은 미실행/미검증이다.

2026-11-08 목표 정렬: **최종 목표는 기존 프로젝트를 agent가 도메인을 이해하고 수정하기 좋은 프로젝트로 점진적으로 전환하도록 돕는 것**이다. 업무 개념·관련 코드 탐색은 첫 사용 경로이고, 온톨로지는 명시적 도메인 모델의 수단, FCA는 구축 부담을 줄일 후보 발견 수단이다. ADR-020과 PRODUCT/RESEARCH/ROADMAP에 반영했다. 당시 다음 한 작업은 [S1 도메인 모델 개발 지시](reviews/2026-11-08-domain-model-next-plan.md)다. 당시 리뷰 세션은 지시·맥락 문서만 준비했으며 모델/validator·agent 변경 실험은 아직 구현/실행하지 않았다.

2026-11-08 준비 후 독립 리뷰: **PR #13의 준비·실패 경계 관찰을 인정하고 새 수정 필요 결함은 확인하지 않았다.** main `b4449c3`에서 136테스트·비교 4/4, 같은 설치 cache의 9개 관찰 파일·5개 입력 감사 파일 일치, 18개 fingerprint·11개 anchor·Program 경계·예산 기록 정합성을 확인했다. 전체 context를 facts로 재구성했고 기존 진입 파일만으로도 129객체/314속성이다. 설치/빌드 독립 재현·모델/agent 효용은 미검증이다. [최신 독립 리뷰](reviews/2026-11-08-vendure-preparation-independent-review.md), [새 근거](reviews/evidence/2026-11-08-vendure-review-verification.json)를 참조한다. 아래 준비/과거 계획은 당시 기록이다.

2026-11-08 Vendure 준비 후속: **환경 준비 성공 / 탐색 비교 범위 미확보로 종료**했다. 고정 의존성 설치·common 빌드 후 기존 4진입 설정의 진단은 0개다. 전체 context 2,264객체/4,288속성이 기본 128/64를 넘어 그룹/FCA를 실행하지 않았다. 원래 Admin UI 설정은 test 이름 오류 495개가 남았다. 30분 마감 안에서 총 359.668초를 사용했고 동일 설치 cache의 9개 관찰 파일이 재현됐다(설치/빌드 독립 재현은 미검증). 136테스트·기존 비교 4/4가 통과했다. [최신 인계](reviews/2026-11-08-vendure-preparation.md)와 [재현/경계](../experiments/public-app/prepared-v1/README.md)가 현재 상태다. 다음 권고는 과업 범위 선택 계약 검토이며 이번에 구현하지 않았다. 사람 효용·Gate 2~4는 미검증이다.

2026-11-08 준비 전 독립 리뷰: **PR #11의 과업/실패 관찰 완료를 인정하며 이번 범위의 새 결함은 확인하지 않았다.** 136개 테스트·기존 비교 4/4, 새 archive/inventory·Program·outcome·검색 결과 대조, 동일 cache 반복의 비시간 13개/17개 byte 재현을 확인했다. 분석 표본과 사람 효용은 여전히 미확보다. 사용자는 다음 작업으로 **Vendure 준비를 총 30분 한도로 한 번 더 검증**하기로 선택했다(ADR-019). [독립 리뷰](reviews/2026-11-08-public-app-independent-review.md)와 [현재 개발 지시](reviews/2026-11-08-vendure-preparation-next-plan.md)가 당시 판단이다. 설치 성공과 FCA 범위 적합성을 분리하며, 네 진입 파일의 현재 함수 inventory도 129개로 객체 상한 128을 넘는다.

2026-11-08 공개 업무 앱 적합성 점검: **과업/원문 근거와 재현 자료를 준비했고, 이번 예산에서는 분석 표본 미선정**이다. Saleor는 원래 strictNullChecks 전제에서 거부됐고 별도 과업 설정에서도 컴파일 오류가 남았다. 추가 후보 Vendure Admin UI는 strict를 유지하지만 미설치 의존성·workspace 빌드 경계로 실패했다. [실제 결과 인계](reviews/2026-11-08-public-app-suitability.md)와 [실험 README](../experiments/public-app/README.md)가 당시 준비 상태다. 사람 효용·Gate 2~4는 미검증이며 코어·기존 corpus는 그대로다.

직전 독립 판정(2026-11-08): **R5의 보고된 잔여 오류 해결, R4 해결 유지, 이번 변경 범위의 추가 결함 없음**이다. 136개 테스트·기존 비교 4/4, 원래 독립 사례 9/9·인접 사례 27/27·새 경계 사례 8/8, V1/V2/V3 비시간 14/16/16개 재현을 확인했다. [독립 리뷰](reviews/2026-11-08-type-context-independent-review.md)를 참조한다. 사용자는 다음 표본을 **공개 TypeScript 업무 앱 후보부터 조사**하기로 선택했다. [후보 조사](reviews/2026-11-08-public-app-candidates.md)와 [현재 개발 지시](reviews/2026-11-08-public-app-next-plan.md)는 이번 적합성 점검의 입력이다. 당시 앱 선정/scan·사람 효용 검증은 미완료였다.

2026-11-08 최신 구현: **R5 타입 선언 문맥을 V3로 보완하고 회귀·재현 검증을 완료**했다. 원래 독립 probe 기대 일치는 7/9 → 9/9, 인접 사례는 18/27 → 27/27이다. 전체 136개 테스트·기존 비교 4/4, V1/V2/V3 비시간 14/16/16개 재현이 통과했다. 현재 기본 corpus 명령은 V3이며 입력은 변경 없는 V2 계약이다. [새 인계](reviews/2026-11-08-type-context-fix.md)와 [V3 README](../experiments/corpus/v3/README.md)가 최신 구현 상태다. 독립 재검토·사람 승인·제품 효용은 별개로 남아 있다.

수정 전 독립 판정(2026-11-08): **R4 해결, R5 부분 해결**이다. V2의 함수 선언 이름 오인은 차단됐지만 지역 타입 매개변수/인터페이스 필드 선언 이름을 실제 사용으로 인정하는 Medium 잔여 결함을 확인했다. 99개 테스트·기존 비교 4/4·V1 14개/V2 16개 비시간 파일 재현은 통과했다. [독립 리뷰](reviews/2026-11-08-corpus-contract-independent-review.md)와 [현재 개발 지시](reviews/2026-11-08-contract-review-next-plan.md)가 이번 수정의 근거다. 업무 개념 탐색 우선 방향은 유지한다.

2026-11-08 구현 후속: **평가기 V2로 R4/R5를 보완**했다. 제품 코어와 역사적 V1은 그대로이며, 당시 기본 corpus 명령은 V2였다. 전체 99개 테스트·예제 비교 4/4, V1 비시간 14개·V2 16개 재현 일치를 확인했다. [수정 인계](reviews/2026-11-08-corpus-contract-fix.md), [V2 계약/재현](../experiments/corpus/v2/README.md), [새 검토표](../experiments/corpus/results/2026-11-08-v2/review.md)는 V2 당시의 구현 인계다. 아직 독립 재검토나 사람 승인으로 표시하지 않는다.

직전 독립 판정: 원시 corpus 결과는 재현됐지만 평가기 R4/R5 보완이 필요했다. 사용자는 다음 제품 실험을 **업무 개념·관련 코드 탐색 우선**으로 선택했다. [corpus 독립 리뷰](reviews/2026-11-07-corpus-independent-review.md)와 [이행한 개발 지시](reviews/2026-11-07-corpus-review-next-plan.md)가 이번 수정의 기준이며, 아래 관찰 자료는 과거 실행으로 보존한다.

2026-11-07 새 NEXT_PLAN의 **실제 corpus 관찰 자료 구축을 완료**했다. 공개 TS corpus 2개를 revision·라이선스·20개 파일 hash로 고정하고, 첫 scan 전에 코드 사실 라벨 24개를 작성했다. 라벨 22개 일치/2개 클래스 모델링 미지원, 함수 전체 predicate 지원 0건, 사전 날짜 비교 0/2 지원을 관찰했다. p-queue 전체 FCA는 속성 상한 초과이며 작은 범위 결과와 함께 보존했다. 사람의 업무 의미 승인·검토 시간·검색/LSP 대비 효과는 아직 미검증이다. [관찰 보고서](reviews/2026-11-07-corpus-observation.md)와 [검토표](../experiments/corpus/results/2026-11-07/review.md)는 구현 세션의 관찰 인계다.

첫 PoC의 구성 요소 구현 후, 독립 리뷰가 발견한 **R1/R2 false proof 차단을 완료**했다. 2026-11-07 독립 재검토에서 R1/R2/R3 해결을 확인했고 Gate 1을 제한된 지원·검증 범위에서 통과로 재평가했다. 모든 TS 문법에 대한 건전성이나 제품 유용성을 입증한 상태는 아니다. R3(mixed TS/JS 파일 집계 계약)도 수정·회귀 검증했다. NEXT_PLAN의 직접 수정·검증 지시와 명시된 후속 결함 R3까지 완료했으며, 이후 실제 corpus 관찰은 아래와 같이 수행했고 사용자 과업 비교는 후속 연구 단계다.

[R1/R2 개발 인계](reviews/2026-11-06-normalization-fix.md)와 [NEXT_PLAN 이행 점검·R3 인계](reviews/2026-11-06-next-plan-completion.md)에 전후 판정·검증·남은 위험을 정리했다. 과거 [리뷰](reviews/2026-11-04-poc-review.md)와 [NEXT_PLAN](reviews/NEXT_PLAN.md)은 당시 지시와 관찰로 보존했다. 이 문서가 최신 구현 상태다.

## 저장소와 개발 규칙

- `origin`: `https://github.com/hyeonhb/ontosary.git`.
- 원격 초기 LICENSE 커밋 `5d33ab6` 기반으로 `chore/initial-poc`에 기존 작업을 `a054f4f`로 커밋했다.
- 기존 두 커밋은 [PR #1](https://github.com/hyeonhb/ontosary/pull/1)로 원격 main에 병합했다(`7671a1a`). main은 origin/main을 추적한다. R3는 그 main에서 만든 `fix/analyzed-file-manifest`에서 구현하고, [PR #2](https://github.com/hyeonhb/ontosary/pull/2)를 2026-11-07 squash 병합했다(`b894137`). 로컬 main도 해당 원격 커밋까지 fast-forward 동기화했다.
- 사용자는 이후 작업도 검증 후 branch push → PR 생성·검토 → merge → main 동기화까지 자동 수행하도록 지속 승인했다. 별도 지시가 없으면 반복 승인 없이 이 절차를 따른다.
- [CONTRIBUTING](../CONTRIBUTING.md)의 GitHub Flow와 Conventional Commits를 준수한다. 작업 브랜치·작은 커밋·PR 검토·검증 기록이 기준이다. GitHub 보호 규칙이나 CI를 설정했다고 가정하지 않는다.
- 사용자 선택으로 원격 Apache-2.0 LICENSE를 유지하고 패키지·README를 통일했다. ADR-009가 최초 MIT 선택을 대체한다.

## 실제 구현된 기능

- TypeScript 타입·필드·함수·참조·조건·소스 근거와 진단을 JSON으로 추출.
- 작은 Formal Context/NextClosure, 후보 필터, 일반화 관계, 결과 상한.
- 제한된 논리 IR, 유한 열거·동치·양방향 함의·반례·Unknown/Unsupported.
- JSON CLI `scan`, `concepts`, `compare`.
- Vehicle/Listing/ConsultationRequest의 React+Vite 예제.
- 맥락 문서, 회귀 테스트, 재사용 가능한 실험·리뷰 증거.

이번 수정: enum 멤버의 타입만 보고 receiver 실행을 생략하던 경로를 차단했다. 직접 enum 선언 식별자(괄호·named import alias 포함)만 허용하고 optional/call/assertion/non-null/nested receiver·enum 객체 별칭을 거부한다. explicit this는 전체 predicate와 개별 condition 모두 Unsupported다. parameters는 원래 소스 signature이며, 지원된 IR의 argN만 런타임 인자 위치다.

## 실행 명령

```sh
pnpm install --frozen-lockfile
pnpm build
pnpm ontosary scan examples/react-vite --json
pnpm ontosary concepts examples/react-vite --json
pnpm ontosary compare examples/react-vite canConsultFromCard canConsultFromDetail --assume-same-input --json
pnpm exec vitest run tests/normalization-soundness.test.ts
pnpm check
pnpm experiment
node docs/reviews/evidence/2026-11-04-independent-check.mjs
pnpm example:dev
```

동명 함수는 전체 ID로 지정한다. Unknown/Unsupported 종료 코드 2, 프로젝트/컴파일/인수 오류는 1이다. probe 스크립트는 관찰 결과를 출력하므로 exit 0만으로 Gate 통과를 판단하지 않는다.

## 최신 검증 결과

환경: Node 22.19.0, pnpm 11.19.0, TypeScript 5.9.3. 새 의존성을 추가하지 않았다.

2026-11-07 중단 복구: PR #2 생성 후 병합 전 상태에서 재개했다. 구현 변경 없이 검증한 head `bb2dfe2`를 확인했고 `pnpm check`를 다시 실행해 82개 테스트·타입 검사·production build가 모두 통과했다. 원격 검사 목록은 비어 있었으며 CI 통과를 주장하지 않는다. 기존 실험·독립 probe 증거는 같은 구현에 대한 이전 실행 결과로 유지했다.

- 수정 전 targeted regression: 진단 0개인 fixture에서 34개 중 29 실패/5 통과.
- 수정 후 targeted regression: 한도 검사 추가 후 **35개 통과**.
- `pnpm check`: 코어/예제 타입 검사, **5개 파일/82개 테스트 통과**, Vite production build 성공.
- `pnpm experiment`: 기존 4개 비교 기대값 통과. 타입 6, 함수 13, 지원 predicate 6/미지원 7; FCA 13×26, 형식 개념 20/후보 8/관계 8, 잘림 없음. 실험 수치·비교 결과는 동일하며 scan JSON의 파일 범위 설명만 갱신했다.
- 새 회귀 테스트: 20개 거부 receiver 사례, 함수/메서드/branch의 explicit this, 정상 9개 함수/81쌍 실제 진리표 및 반례 재실행, named import·문자열/숫자 enum, 4,096/8,192 경계, core/CLI 상태 일치.
- 기존 독립 probe: 정상 144회 실행·IR 대조, 256쌍, 반례 336개, FCA 4×3 관계 4,096개 대조 통과. R1 optional/call, R2 first/second 비교가 모두 Unsupported/평가 0으로 바뀜. CLI 재현은 종료 2.
- R3 targeted regression은 수정 전 6개 모두 실패, 수정 후 6개 모두 통과했다. TS/TSX/MTS/CTS·JS/JSX/MJS/CJS·선언 파일, imported JS 참조, JS-only, allowJs만 설정한 경우, 제외 JS의 오류 진단, CLI/API manifest 일치를 검사했다.
- 독립 probe를 R3 적용 후 다시 실행하여 files=[input.ts], 제외 근거 ignored.js, 기존 R1/R2 거부와 정상 계산 검증을 확인했다. 새 증거는 `2026-11-06-file-manifest-results.json`이다.
- 초기 PoC의 브라우저 smoke check는 2026-11-03 기록이다. 이번 수정은 UI를 변경하지 않았으며 브라우저 확인을 반복하지 않았다.

## 남은 문제와 제약

- **R3 해결:** files는 실제 방문하는 TS/TSX/MTS/CTS 구현 파일만 포함한다. 제외된 구현 파일은 각각 omissions의 근거 경로·위치·이유로 보고한다. 타입 해석·참조·진단은 유지한다. 이 파일 수를 프로젝트 전체 coverage 비율로 해석하면 안 된다.
- enum namespace 경로·값 별칭·explicit this를 보수적으로 거부한다. 지원 확대는 별도 실행 대조가 필요하다.
- 기존 단일 반환식·필수 유한 입력·한 단계 속성 제한, strictNullChecks, 런타임 타입 준수·안정적인 plain data·입력 독립성 전제는 유지된다.
- 소스 ID의 편집 안정성, 재귀 project references, 최상위 조건·클래스 필드·프레임워크 의미, 큰 프로젝트 비용은 미해결/미검증이다.
- 승인 워크플로·LLM·SMT·MCP·자동 수정은 미구현이다. FCA 후보가 업무 개념이거나 조건 차이가 버그라는 뜻은 아니다.
- Gate 1은 2026-11-07 독립 리뷰에서 제한된 지원·검증 범위로 통과 판정했다. 모든 TS 입력의 건전성이나 Gate 2~4의 제품 효과를 입증한 것은 아니다.

## 2026-11-07 독립 재검토

PR #1~#3가 반영된 main `c6e0fc7`을 별도 리뷰 세션에서 재검증했다. **R1/R2/R3 해결, 검토 범위 내 추가 결함 없음**으로 판정했다. `pnpm check` 82개·타입 검사·예제 빌드와 `pnpm experiment` 4개 비교가 통과했다. 기존 독립 probe와 새 receiver/this/import/file 경계 probe도 통과했다. Gate 1은 제한된 지원·검증 범위에서 통과로 재평가했으며 Gate 2~4의 제품 효과는 여전히 미검증이다. 원격 check-runs/status 목록은 비어 있어 CI 성공을 주장하지 않는다.

[독립 리뷰](reviews/2026-11-07-post-merge-review.md), [당시 다음 개발 지시](reviews/2026-11-07-next-plan.md), [리뷰 맥락](reviews/REVIEW_CONTEXT.md)을 참조한다. 초기 NEXT_PLAN과 과거 원시 증거는 이행된 지시·관찰로 보존했다. 아래 corpus 연구 방향을 유지하며 이번 리뷰에서 제품 소스·테스트·설정을 수정하지 않았다.

## 2026-11-07 실제 corpus 관찰 검증

- 기준 main `c1a542c`에서 `codex/corpus-observation`으로 작업했다. 제품 소스·기존 지원 경계·FCA/논리 상한·의존성은 그대로다.
- p-queue `7f272ab5`의 production 5파일 및 priority-queue 4파일, date-fns v4.1.0 `313b902b`의 요일 함수와 local imports 9파일을 분석했다. 원래 p-queue 설정의 shared config 부재 실패도 기록했다.
- 라벨 24개 중 22개 일치, 2개 명시적 클래스/필드 모델 미지원. 사람 검토 0개, 승인 지식 0개. 조건 원문 추출의 일치와 정규화 지원을 구분했다.
- predicate 지원: p-queue production 0/103, 구성요소 0/15, date-fns 0/5. 범위 간 중복을 합산하지 않는다. 사전 날짜 비교 2쌍 모두 Unsupported/평가 0회.
- FCA: production은 103×188로 입력 상한 초과; 구성요소 15×31의 후보 23개, weekday 5×13의 후보 3개, 둘 다 잘림 없음. 같은 facts의 단순 그룹도 저장했다. 후보 수는 품질 점수가 아니다.
- `pnpm check`: 6파일/89테스트·타입 검사·예제 production build 통과. `pnpm experiment`: 기존 4/4 비교 통과, 과거 결과 변경 없음.
- 두 새 scanner 실행의 비시간 파일 14개 byte 일치. 재현 환경·hash·wall time·원시 결과는 `experiments/corpus/results/2026-11-07*`에 있다. 다운로드 준비 4,773ms, 사람의 준비 노력·검토 시간 미측정.
- 새 입력/runner/해석 보고는 날짜별 기존 리뷰·NEXT_PLAN을 보존한 채 추가했다. 정적 관찰만 수행했으며 원본 corpus 코드를 실행하지 않았다.

## 2026-11-07 corpus 독립 리뷰

main `a58a88b`을 독립 검토해 `pnpm check` 89개·기존 실험 4/4 및 새 corpus 실행의 비시간 파일 14개 일치를 확인했다. 원시 관찰은 재현됐으나 평가기가 라벨의 주장보다 약한 조건으로 correct를 내는 R4와 선언 이름을 사용 참조로 오인하는 R5(Medium 2건)를 재현했다. 제품 코어의 새 false proof는 확인하지 않았다. 기존 22/24는 현 평가기 판정이며 자연어 주장 전체가 자동 검증됐다는 의미로 확대하지 않는다.

사용자는 다음 제품 실험으로 **업무 개념·관련 코드 탐색 우선**을 선택했다. [독립 리뷰](reviews/2026-11-07-corpus-independent-review.md), [현재 개발 지시](reviews/2026-11-07-corpus-review-next-plan.md), ADR-014를 참조한다. 원래 corpus 보고서·라벨·raw 결과는 당시 관찰로 보존했다.

## 2026-11-08 R4/R5 평가 계약 보완

- 기준 main `7adf2d1`, `codex/corpus-evaluator-contract`에서 작업했다. src/core·CLI·lockfile·원본 corpus/manifest·V1 평가기/라벨/runner·과거 결과는 그대로다.
- V2는 타입 kind와 명시적 type 기대값을 검사한다. 함수 generic/클래스 소속/상속처럼 자동 검증하지 않는 문구는 claim에서 분리해 unverified로 출력한다.
- reference/property는 source/use/target anchor 및 실제 AST 역할과 정확한 edge를 대조한다. 선언 이름은 거부하고 재귀/import 사용은 인정한다. useEvidence/targetEvidence를 별도로 기록한다.
- 최초 actual-scan 회귀 8개 중 6개 실패/2개 통과 → 보완·추가 후 10개 통과. 전체 `pnpm check`는 7파일/99테스트·타입 검사·빌드 통과, `pnpm experiment`는 4/4 통과했다.
- V1 재현의 비시간 14파일, V2 재현의 비시간 16파일이 각각 byte 일치했다. 두 버전의 core 분석 산출물 11개도 동일하다.
- 두 버전 모두 라벨 22 correct/2 unsupported지만 검사 내용과 일부 claim이 달라졌으므로 성능 전후 차이로 읽지 않는다. 24개 전후 대조와 변경 이유는 `results/2026-11-08-v2/label-changes.json`에 있다.
- 당시 `pnpm experiment:corpus <새 경로>`는 V2, `pnpm experiment:corpus:v1 <새 경로>`는 역사적 V1이다. V1 결함을 수정 완료 버전으로 오인하지 않는다.
- [후속 제품 실험 초안](experiments/concept-exploration-protocol.md)은 미실행이다. 대상·정답·참가자를 확정하지 않았고 사람 시간/업무 의미/도구 효용 결과를 만들지 않았다.

## 다음 작업

최신 순서: [CLI 비모델 타당성 지시](reviews/2026-11-11-s2-cli-feasibility-instructions.md)의90분 검증 → 결과 독립 리뷰 → 실제 자격 증명/모델 연결과 전체 수정 소스 수집·평가의 후속 구조 결정 → C 사람 검토·전체 준비 재검토와 본 비교 별도 승인. Linux 알려진 제출 재현은 독립 검토 범위에서 통과했고 R12도 기존 검증 범위에서 해결됐으며 R11 전체 해결은 아직 아니다. 아래 합의 순서는 이 후속 경계를 포함해 해석한다.

1. R6/R7 보완은 독립 검증 범위에서 완료됐다. 최신 소비 경로는 V2이며 V1/과거 실패 증거는 보존한다.
2. S2 범위·큰 구조는 ADR-023/024, 과업 정책·비교 조합은 ADR-028로 합의했다. [실행 전 준비 지시](reviews/2026-11-10-s2-trial-preparation-instructions.md)에 따라 계약·C 의미 대응 검토 자료·격리/계측·새 배포 동결을 구현한다.
3. 준비 결과의 독립 리뷰와 사람 동등성 검토·남은 실행 조건 확인을 마친 뒤 별도 승인으로 본 비교를 진행한다. H-O/H-F와 코드 사실/후보/사람 승인을 분리하며 큰 기술·방향 선택은 사용자와 결정한다.

핵심 코드: `src/core/{analyzer,logic,fca,model}.ts`, `src/cli/index.ts`. 최신 평가기: [V3 README](../experiments/corpus/v3/README.md), [수정 인계](reviews/2026-11-08-type-context-fix.md). 지원 경계는 [ARCHITECTURE](ARCHITECTURE.md), 결정은 [DECISIONS](DECISIONS.md), 실험 해석은 [RESEARCH](RESEARCH.md), 순서는 [ROADMAP](ROADMAP.md)를 따른다.

## 사람을 위한 안내 문서

2026-11-08 사람 대상 문서: [안내서](guide/README.md)에 핵심 아이디어와 아키텍처 설명을 추가하고, 개념 흐름·구현 코어·모델 근거 읽기·합의된 S2 설계의 Mermaid 원본/SVG를 함께 관리한다. 일회성 개발 지시와 분리한 지속 관리 문서다. 확인 기준은 main `f080e39`이며 병행 개발 중인 S2를 완료로 표시하지 않았다. 제품 구현은 변경하지 않았다.
