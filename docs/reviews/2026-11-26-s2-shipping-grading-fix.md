# PR #107 · 배송비 취소 채점 R26·R27 보완

독립 리뷰에 보관된 두 패치를 같은 부모의 새 작업 사본에 적용하고 `grade.py`로 다시 채점했다. R26은 기존 **6건 통과 → 6건 업무 실패**, R27은 **6건 판정 불가 → 6건 업무 실패**다. 두 패치 모두 독립 리뷰의 SHA-256과 적용 후 Git 트리가 일치했다. 참가 모델 호출은 0회다. [독립 리뷰와 패치 원문](evidence/2026-11-26-shipping-grading-countercontrols.json) · [보완 후 전체 실행 기록](../../experiments/domain-model/s2/results/2026-11-26-shipping-grading-fix/results.json)

## 저장 금액과 취소 결과

R26은 주문 저장 메서드에 객체를 넘긴 뒤 합계를 재계산한다. 이제 저장 호출마다 네 숫자를 복사해 `orderSaves`에 순서대로 기록한다. 같은 주문을 여러 번 저장하면 마지막으로 전달한 금액을 채점한다. 메서드 종료 시점의 `after`도 따로 비교한다. R27은 상품 수량을 그대로 쓰는 제출이다. 정상 반환한 전체 취소 여부와 남은 수량을 각각 기대값에 대조하고, 관측한 업무 불일치를 사례의 `mismatches`에 함께 남긴다. [관측 및 비교 코드](../../experiments/domain-model/s2/trial/angular-shipping/observe.mjs)

아래 금액의 순서는 **세전 배송비 / 세후 배송비 / 세전 주문 합계 / 세후 주문 합계**이며 단위는 통화의 최소 단위다. R26의 종료 금액은 각 행의 기대값과 일치했다. R27은 일부 취소 두 건에서 반환값이 기대와 같아도 상품이 한 개 더 남았다.

| 취소 경로 | 범위 · 가격 방식 | 기대 금액 | R26 실제 저장 금액 | R27 전체 취소 반환값 (기대 → 실제) | R27 잔여 수량 (기대 → 실제) |
| --- | --- | --- | --- | --- | --- |
| 직접 | 전체 · 세금 포함 | 0 / 0 / 0 / 0 | 1000 / 1200 / 1200 / 1400 | true → false | 0 → 2 |
| 직접 | 전체 · 세금 별도 | 0 / 0 / 0 / 0 | 1000 / 1200 / 1200 / 1400 | true → false | 0 → 2 |
| 환불 동반 | 전체 · 세금 포함 | 0 / 0 / 0 / 0 | 1000 / 1200 / 1200 / 1400 | true → false | 0 → 2 |
| 환불 동반 | 전체 · 세금 별도 | 0 / 0 / 0 / 0 | 1000 / 1200 / 1200 / 1400 | true → false | 0 → 2 |
| 직접 | 일부 · 세금 포함 | 1000 / 1200 / 1100 / 1300 | 1000 / 1200 / 1200 / 1400 | false → false | 1 → 2 |
| 환불 동반 | 일부 · 세금 별도 | 1000 / 1200 / 1100 / 1300 | 1000 / 1200 / 1200 / 1400 | false → false | 1 → 2 |

R27이 넘긴 저장 금액도 원시 기록에 있다. 전체 취소 네 건은 모두 `0 / 0 / 200 / 200`, 일부 취소 두 건은 `1000 / 1200 / 1200 / 1400`이었다. 이번 저장 관측은 메모리 저장소의 호출 인자까지다. 실제 DB 쓰기와 재조회는 검증 범위 밖이다.

## 대조와 판정 한계

| 제출 | 결과 |
| --- | --- |
| 원본 / 세후 금액만 차감 / 업스트림 / 별도 헬퍼 | 통과 **4/6 · 4/6 · 6/6 · 6/6**. 원본은 세금 포함 주문에서 200을 남겼고 부분 수정은 세금 별도 주문에서 −240을 만들었다. |
| 헬퍼 본문만 잘못된 계산으로 교체 | 4/6 통과. 전체 취소 네 건에서 제출 헬퍼가 각각 한 번 호출됐다. |
| 부모 문맥이 틀린 패치 | 적용 거부, 사례 실행 0건 |
| 관측 밖 주문 서비스 / 실행되지 않은 변경 분기 | 각각 6건 판정 불가. 후자는 돈의 값이 기대와 일치해도 실행되지 않은 부분이 남았다. |
| 대역에 없는 채널 필드 | 해당 필드를 읽는 전체 취소 4건은 판정 불가, 배송을 유지한 2건은 통과 |
| 원시 DB 연결을 쓰도록 바꾼 추가 대조 | 6건 판정 불가. 대역에 해당 연결이 없어 저장소를 얻는 과정에서 예외가 발생했다. 그 예외로 실제 업무 결과를 확정할 수 없다. |

## 독립 재현

macOS에서 Ontosary 잠금 의존성과 Vendure Git 사본을 사용한다. 아래 명령은 비어 있는 새 실행 경로에 제출별 패치, 적용된 작업 사본, `grade.json`을 남기고 보관된 전체 결과와 바이트 단위로 비교한다. 기존 Vendure 사본이 있으면 복제를 생략할 수 있다.

```sh
pnpm install --frozen-lockfile
scratch=work/review-shipping-r26-r27
mkdir -p "$scratch"
git clone --bare --single-branch --no-tags https://github.com/vendurehq/vendure.git "$scratch/vendure.git"
grader=experiments/domain-model/s2/trial/angular-shipping/submission
python3 -B "$grader/reproduce.py" "$scratch/vendure.git" "$scratch/replay" --verify
```

두 반례만 단일 제출 진입점에 다시 전달하려면 다음을 실행한다. `parent.git`은 앞 명령이 생성한 해결 직전 부모 한 커밋의 저장소다.

```sh
for name in save-first wrong-quantity
do
  python3 -B "$grader/grade.py" "$scratch/replay/parent.git" "$scratch/replay/$name.patch" "$scratch/$name"
  cmp "$scratch/$name/grade.json" "$scratch/replay/$name/grade.json"
done
```

기존 대조 9개, 독립 리뷰 반례 2개, 예외 대조 1개를 같은 진입점으로 검증했다. 기존 후보 선정 재생 결과는 당시 보관본과 바이트 단위로 일치했다. `pnpm check`의 타입 검사·테스트 304개·예제 빌드와 `pnpm experiment`의 기존 대조 4/4가 통과했다. [기존 보관 결과](../../experiments/domain-model/s2/results/2026-11-26-shipping-submission-grading/results.json)
