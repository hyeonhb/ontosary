# PR #107 · 세금 포함 주문에서만 배송비를 취소한 제출

독립 리뷰의 `patch` 문자열을 그대로 단일 제출 명령에 전달했다. 같은 패치가 보완 전에는 **4통과·0실패·2판정 불가**, 보완 후에는 **4통과·2실패·0판정 불가**였다. 패치 SHA-256은 `0708892f795675ed73083f1a55e9f5eb19c5c53270994ca0c7e9e6954660801a`, 적용 후 Git 트리는 `23ef40bcdd7af8f2cc54c587905a878506da4736`으로 독립 리뷰와 일치했다. [리뷰 패치와 진단값](evidence/2026-11-26-shipping-grading-inclusive-only.json) · [단일 제출 채점 원문](../../experiments/domain-model/s2/results/2026-11-26-shipping-inclusive-only/grade.json)

이전 관측기는 배송 행 저장 호출 여부와 배송 취소 요청이 서로 다르면 예외를 냈다. 두 세금 별도 전체 취소 사례에서 주문은 이미 저장됐고 취소 메서드도 정상 반환했지만, 이 예외 때문에 금액 비교가 생략됐다. 이제 배송 행의 저장 호출 여부는 `shippingSaveObserved`에 기록한다. 판정에는 주문 저장 시점과 반환 시점의 금액, 전체 취소 반환값, 남은 상품 수량을 사용한다. [관측 코드](../../experiments/domain-model/s2/trial/angular-shipping/observe.mjs)

| 취소 경로 | 범위 · 가격 방식 | 배송 행 저장 호출 | 기대 금액 | 주문 저장 시 실제 금액 | 판정 |
| --- | --- | --- | --- | --- | --- |
| 직접 | 전체 · 세금 포함 | 있음 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 통과 |
| 직접 | 전체 · 세금 별도 | 없음 | 0 / 0 / 0 / 0 | 1000 / 1200 / 1000 / 1200 | 업무 실패 |
| 환불 동반 | 전체 · 세금 포함 | 있음 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 통과 |
| 환불 동반 | 전체 · 세금 별도 | 없음 | 0 / 0 / 0 / 0 | 1000 / 1200 / 1000 / 1200 | 업무 실패 |
| 직접 | 일부 · 세금 포함 | 없음 | 1000 / 1200 / 1100 / 1300 | 1000 / 1200 / 1100 / 1300 | 통과 |
| 환불 동반 | 일부 · 세금 별도 | 없음 | 1000 / 1200 / 1100 / 1300 | 1000 / 1200 / 1100 / 1300 | 통과 |

표의 금액은 **세전 배송비 / 세후 배송비 / 세전 주문 합계 / 세후 주문 합계** 순서다. 여섯 사례 모두 반환 시점 금액은 주문 저장 시점과 같았다. 두 실패에는 `moneyAtOrderSave`와 `moneyAtReturn` 각각의 기대값·실제값이 남는다. 관측 범위는 메모리 저장소에 전달된 값과 메서드 반환까지다. 실제 DB 재조회는 범위 밖이다.

## 기존 결과 대조

같은 `grade.py`로 기존 12개 제출을 다시 실행해 이전 보관본의 모든 필드를 대조했다. 네 기준 제출은 **4/6·4/6·6/6·6/6**, 헬퍼 변형은 4/6이었다. R26의 저장 후 재계산은 여섯 건 모두 저장 금액이 틀렸다. R27의 수량 유지도 여섯 건 모두 실패했고, 전체 취소 네 건의 거짓 반환값과 일부 취소 두 건의 잔여 2개가 그대로 기록됐다. [기존 12개 결과](../../experiments/domain-model/s2/results/2026-11-26-shipping-grading-fix/results.json)

대역에 없는 채널 필드를 읽은 제출은 해당 네 건만 판정 불가였다. 미관측 서비스, 실행되지 않은 변경 분기, 원시 DB 연결 예외는 각각 여섯 건 판정 불가였고, 문맥이 맞지 않는 패치는 적용 거부·사례 실행 0건이었다. 참가 모델 호출은 0회다.

## 재현

macOS에서 저장소의 잠금 의존성을 설치한 뒤 아래 명령을 실행한다. `scratch`는 새 실행 경로다. Vendure Git 사본이 있으면 복제 단계를 생략하고 그 경로를 사용할 수 있다.

```sh
pnpm install --frozen-lockfile
scratch=work/review-shipping-inclusive-only
mkdir -p "$scratch"
git clone --bare --single-branch --no-tags https://github.com/vendurehq/vendure.git "$scratch/vendure.git"
grader=experiments/domain-model/s2/trial/angular-shipping/submission
python3 -B "$grader/reproduce.py" "$scratch/vendure.git" "$scratch/replay" --verify
python3 -B "$grader/grade.py" "$scratch/replay/parent.git" "$scratch/replay/inclusive-only.patch" "$scratch/single"
cmp "$scratch/single/grade.json" "$scratch/replay/inclusive-only/grade.json"
```

`--verify`는 새 반례의 진단값과 보관된 단일 채점 결과, 기존 12개 제출의 기록을 검사한다. 이번에 추가한 배송 행 호출 표시는 과거 보관본과의 비교에서만 제외한다.

전체 재현과 새 사본에서의 단일 재채점이 통과했다. 기존 후보 선정 재생 출력도 보관본과 바이트 단위로 일치했다. `pnpm check`의 타입 검사·테스트 304개·예제 빌드와 `pnpm experiment`의 기존 비교 4/4가 통과했다.
