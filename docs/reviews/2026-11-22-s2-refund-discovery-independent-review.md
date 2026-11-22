# S2 독립 리뷰 · 환불 잔액 탐색 비교 준비

2026-11-22. PR #96의 `31c3f29`를 검토했다. 기존 환경에서 탐색 기록을 남기고 조건별 작업 사본을 회수하는 경로는 재현됐다. **최종 수정의 성공과 실패를 잘못 판정하는 반례 두 건이 있어 PR 병합과 참가 실행 승인을 보류한다.** 공개 작업 형식도 첫 요청에서 추측할 필요가 없도록 보완한다. [검토한 개발 보고서](https://github.com/hyeonhb/ontosary/blob/31c3f29ca4a5ead7e25ea7fb017feb52a6bc15b7/docs/reviews/2026-11-22-s2-refund-discovery-preparation.md) · [사전 지시](2026-11-22-s2-refund-discovery-preparation-instructions.md)

## 독립 검증

고정 Vendure 소스와 준비된 macOS 환경에서 `s2:build`, 새 출력 위치의 `replay.py --verify`, `wire.py`와 원본 대조를 수행했다. 4,735개 파일에서 독립 작업 사본 6개와 A/B/C 탐색 기록 3개를 재현했다. 원본과 문구만 수정한 대조는 문구·클릭을 함께 만족한 사례가 9/11, 두 정상 구현은 11/11이었다. 조건별 첫 입력과 세 번째 작업 뒤 입력을 받은 로컬 HTTP 요청 6개도 보관 결과와 일치했다. `pnpm check`의 테스트 304개·빌드와 `pnpm experiment`의 4개 비교가 통과했다. 실제 참가 모델 호출은 0회다.

세 모의 탐색 답안은 같은 문장을 봉인했다. 도메인 자료와 대응 서술 자료에는 기존 메뉴·분기 근거가 있고 결제별 환불 잔액까지 이어지는 관계는 빠져 있다. 이 공백을 보존하고 실제 참가자가 어디서 근거를 찾아오는지 측정하는 설계는 프로젝트 목적에 맞는다. 모의 세션은 효과의 표본이 될 수 없다.

## 보완할 판정과 공개 사용법

| 항목 | 재현한 현상 | 비교에 미치는 영향 |
| --- | --- | --- |
| **R23 · Angular가 거부하는 바인딩에 만점** | 정상 A 사본의 문구 조건을 같은 잔액 계산을 인라인한 `order.payments?.some(p => …)`로 교체했다. PR 채점기는 타입 통과·메뉴 11/11·최종 성공으로 기록했다. Vendure lockfile의 Angular compiler 19.2.15로 제출 HTML을 파싱하면 화살표 함수에서 바인딩 구문 오류가 난다. 정상 대조의 파싱 오류는 0개였다. | 채점기가 제출 HTML의 바인딩을 JavaScript로 실행해 실제 화면을 구성할 수 없는 제출에도 성공을 준다. [표현식 실행](https://github.com/hyeonhb/ontosary/blob/31c3f29ca4a5ead7e25ea7fb017feb52a6bc15b7/experiments/domain-model/s2/trial/discovery/menu.ts#L82-L89) |
| **R24 · 제출 오류를 미지원으로 판정** | 별도 A 사본에서 새 잔액 메서드 본문만 명시적인 `throw new Error("Missing refund calculation")`로 바꿨다. 타입은 통과했지만 채점 결과는 `unsupported`, 관측된 사례는 0건이었다. | 출처가 분명한 제출 실패도 평가기의 한계로 집계돼 조건 간 효과 판단이 보류될 수 있다. [예외 처리](https://github.com/hyeonhb/ontosary/blob/31c3f29ca4a5ead7e25ea7fb017feb52a6bc15b7/experiments/domain-model/s2/trial/discovery/menu.ts#L94-L99) |
| **R25 · 첫 요청의 JSON 형식 누락** | 첫 공개 입력에는 `list(space,glob?,offset?)` 사용법이 있지만 필수 키 `op`가 없다. 같은 원본에서 `{"action":"list","space":"source"}`는 일반 오류를 반환하고 `{"op":"list","space":"source"}`는 성공했다. 모의 참가자는 처음부터 올바른 키를 알고 있다. | 업무 탐색을 시작하기 전에 프로토콜 추측이 요청 예산을 소모한다. 최초 공개 입력만으로 유효한 작업을 구성할 수 있어야 한다. [공개 입력](https://github.com/hyeonhb/ontosary/blob/31c3f29ca4a5ead7e25ea7fb017feb52a6bc15b7/experiments/domain-model/s2/trial/discovery/session.py#L27-L33) |

R23의 독립 대조에는 정상 A 사본의 HTML에서 `hasRefundBalance(order)` 대신 아래 조건을 사용했다. 클릭 핸들러와 TypeScript는 같은 정상 사본의 것을 사용한다. Angular 패키지는 고정 lockfile의 무결성을 대조한 뒤 임시 위치에서 `parseTemplate`로 확인했다.

```js
order.payments?.some(p => p.state === 'Settled' && p.amount > p.refunds.filter(r => r.state !== 'Failed').reduce((n, r) => n + r.total, 0))
```

## 개발 세션에 전달할 지시

기존 PR #96에서 R23~R25를 무호출로 보완해 주세요. 과업, 기존 B/C 자료와 네 가지 발견 판정 항목은 유지합니다. 수정 방식은 개발 세션이 정합니다.

1. **템플릿 판정.** 고정 Angular에서 성립하고 현재 평가기가 의미까지 관측할 수 있는 바인딩에만 성공을 부여해 주세요. 무효가 확인된 제출은 실패, 유효하지만 평가기가 판단할 수 없는 표현은 미지원으로 남깁니다. 인라인 반례, 기존 두 정상 구현, 유효하지만 지원 범위를 벗어난 템플릿으로 경계를 보여 주세요. 전체 브라우저 환경 구축은 필요하지 않습니다.
2. **오류 귀속.** 실제 제출이 일으킨 오류와 평가 대역·미지원 의존성·귀속 미상의 오류가 같은 판정으로 귀결되지 않도록 해 주세요. 위 명시적 예외와 평가 대역 쪽 대조를 전체 작업 사본 채점 경로로 검증하고, 실패 위치와 해당 사례를 결과에서 찾을 수 있게 해 주세요.
3. **공개 작업 형식.** 세 조건에 공통으로, 정답 경로나 업무 힌트가 없는 유효한 JSON 예시와 필수 키를 제공해 주세요. 첫 공개 입력의 예시를 그대로 사용해 성공하는지 확인하고 변경한 입력·모의 기록·로컬 요청을 다시 대조해 주세요.

기존 증거와 보완 결과를 구분하고 새 참가 호출 없이 대조 결과를 재현할 수 있으면 완료다. 모델 실행 예산은 그 뒤의 별도 결정이다. 특히 B/C 모의 절차는 각각 24회 한도를 모두 썼다. 이는 실제 참가자가 24회를 필요로 한다는 관측은 아니지만, 그대로 채택하면 도구 선택과 미제출이 결과에 미칠 영향을 감수해야 한다. 한도 확대나 새 실행 환경 구축은 이번 보완 범위에 포함하지 않는다.
