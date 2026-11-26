# Vendure 부분 출고 첫 사용 · 진행자와 독립 검토자용

**작성자용 자료와 후속 agent용 요청을 준비했다.** Vendure v3.5.0의 Angular Admin UI에서 공개 CLI로 코드 위치를 조회할 수 있다. 앱 소스 범위의 `scan`은 진단 없이 끝났고, 같은 범위의 `concepts`는 객체·속성 상한을 넘어 후보를 반환하기 전에 종료됐다. 작성자는 미배정이다. 실제 작성 기록과 변경 제안은 없으며 사람의 첫 사용, 인계 성공, Ontosary와 FCA의 기여, 참가 시간은 모두 미측정이다. 참가 모델 호출과 배송비 취소 A/B/C 재실행은 각각 0회다. [준비 지시](2026-11-26-first-use-partial-fulfillment-instructions.md)

## 누구에게 무엇을 전달하는가

| 시점 | 전달물 | 회수할 자료 |
| --- | --- | --- |
| 작성 시작 | [작성자 안내](../../experiments/first-use/partial-fulfillment/author.md), 고정 Vendure 소스, Ontosary 도구와 앱 범위 설정 | 다음 개발자에게 전달할 자유 형식 `HANDOFF.md`. 경험·시간·도움·도구 관찰은 진행자가 별도로 받는다. |
| 작성 완료 뒤 | 새 세션에 [후속 요청](../../experiments/first-use/partial-fulfillment/agent.md), 같은 리비전의 깨끗한 소스, 작성자가 완성한 기록 하나 | 변경 제안, 보존 동작과 회귀 사례, 기록을 재사용한 판단과 직접 보충한 근거 |
| 검토 | 이 문서와 참가자 제출물 | 설명별 원문 위치, 확인 여부·이유. 최초 발견, 확인, 도움, 추가 탐색 비용은 구분해 기록한다. |

참가자에게는 아래에서 만든 **해당 역할 디렉터리만** 건넨다. 작성자가 Vendure 대상 코드의 작성·유지보수에 참여했는지, 답을 미리 보았는지 확인하고 Vendure·Ontosary 경험을 적는다. 응답 전의 질문과 힌트는 진행자가 기록한다. 후속 agent는 작성 대화·구두 보충 없이 시작한다. 이슈·실험·리뷰가 함께 들어 있는 Ontosary 전체 체크아웃은 진행자 작업 공간이다.

저장소 루트에서 실행한다. `repo`는 고정 커밋을 담은 Vendure Git 사본이다. 기존 사본이 없으면 아래 두 Git 명령으로 준비할 수 있다. 각 출력 경로는 새 디렉터리여야 한다.

```sh
delivery=$(mktemp -d)
repo="$delivery/vendure.git"
git init --bare -q "$repo"
git -C "$repo" fetch -q --depth=1 https://github.com/vendurehq/vendure.git 534e6003534f74761e82de1b8c6061cba89945d1:refs/heads/baseline
pack=experiments/first-use/partial-fulfillment/prepare.sh
"$pack" author "$repo" "$delivery/author"
# 작성자가 실제 기록을 제출한 뒤에만 실행
"$pack" agent "$repo" "$delivery/agent" "$delivery/author/HANDOFF.md"
```

작성자 안내는 Ontosary README의 설치·빌드·CLI 사용법을 옮겼다. 도구 소스와 잠금 파일은 `35296d436a63f9c72739859c22b1aded4bc9f57a`에서 추출한다. 참가자에게 공개하는 설정은 앱 범위만 지정하며 대상 컴포넌트나 함수 이름을 열거하지 않는다. Vendure 원본의 라이선스 파일도 각 사본에 들어 있다. [Ontosary README](../../README.md#시작) · [분석 설정](../../experiments/first-use/partial-fulfillment/tsconfig.app.json) · [소스·라이선스 기록](../../experiments/domain-model/SOURCE-NOTICE.md)

**전달물 점검.** 새 작성자 디렉터리의 최상위는 `START.md`, `vendure/`, `ontosary/`였다. agent용은 모의 전달 메모 한 줄을 사용해 `START.md`, `vendure/`, `HANDOFF.md`만 있는지 확인했다. 두 사본에서 Vendure 원본 4,735개 파일의 내용이 고정 Git blob과 모두 일치했다. agent 사본의 Vendure 파일 목록도 원본과 같았고 인계 파일은 주어진 메모와 바이트가 같았다. 역할별 `START.md`를 실제로 읽고 원본 안내와 대조했다. 작성자에게 후속 요청이, agent에게 작성 안내가 전달되는 경로는 없었다. 정답 심볼·경로 목록, 내부 검토 메모, Git 이력, 이전 참가 대화·실행 로그도 포함되지 않았다. 설치 또는 점검이 만든 scan·진단 출력은 전달 디렉터리 밖에 보관했다. 실제 인계 때는 완성된 기록으로 agent 자료를 새로 만든다.

## 준비자가 실행한 공개 경로

macOS arm64, Node 22.19.0, pnpm 11.19.0, npm 10.9.3, 분석기 TypeScript 5.9.3을 사용했다. 기존 Vendure bare Git cache에서 고정 소스를 새로 추출했다. 두 프로젝트의 설치 디렉터리와 빌드 산출물은 새 사본에서 만들었다. pnpm은 로컬 store의 47개 패키지를 재사용했고, npm은 기본 로컬 다운로드 캐시를 사용할 수 있는 상태였다. Vendure는 Admin UI와 common workspace 및 루트 의존성 2,230개를 설치하고 common의 원래 build를 실행했다. Angular 앱 구동은 필요하지 않았다.

| 준비자 점검 | 관측한 결과 | 명령 경과 |
| --- | --- | ---: |
| 작성자 자료 추출 | 완료 | 1.880초 |
| Ontosary 잠금 설치와 빌드 | 종료 0 | 2.174초 |
| Vendure 잠금 설치와 common 빌드 | 종료 0 | 18.094초 |
| 공개 `scan`, 원래 `packages/admin-ui/tsconfig.json` | 종료 1. 구현 파일 581개, 진단 495개(TS2304 292개, TS2582 203개) | 8.653초 |
| 공개 `scan`, 전달한 `ontosary.app.json` | 종료 0. 구현 파일 552개, 함수 4,097개, 타입 1,640개, 진단 0개, 누락 설명 715개. JSON 73,198,835바이트 | 8.515초 |
| 공개 `concepts`, 같은 설정 | 종료 1. 객체 4,097 / 속성 7,033, 기본 상한 128 / 64. stdout 0바이트, stderr에 상한과 실제 크기 | 8.137초 |

설치는 서로 병행했고 분석 세 명령도 병행했다. 위 시간은 이 장비에서의 개별 준비 명령 실측이다. 설정은 원래 strict·경로 매핑을 상속해 `src` TS/TSX와 typings를 포함하고 spec·테스트 진입점을 제외한다. 해당 범위에서 전체 함수 predicate 15개가 지원되고 4,082개가 미지원이었다. 아래 두 판단의 메서드는 위치가 추출됐고 다중 문장으로 인해 전체 식의 논리 정규화는 미지원이었다. 템플릿 연결은 HTML 원문에서 확인한다. 현재 범위에서는 FCA 후보의 관련성이나 검토 비용을 평가할 수 없다. 더 작은 범위를 정한다면 누가 어떤 근거로 골랐는지 남겨야 최초 발견을 해석할 수 있다.

재현은 작성자 `START.md`의 두 설치 블록과 두 CLI 명령으로 한다. 원래 설정 대조는 같은 `scan`에서 마지막 설정 파일명을 `tsconfig.json`으로 바꾼다. JSON·stderr·종료 코드는 준비자 쪽에서 확인한 뒤 초기 참가 화면에 결과를 미리 열어 두지 않는다. 다음은 scan 요약을 확인하는 예다.

```sh
node -e "const s=JSON.parse(require('node:fs').readFileSync('scan.json')); console.log(s.files.length,s.functions.length,s.diagnostics.length,s.omissions.length)"
```

## 검토자용 기준 소스와 주문 예

1. **주문 단위 진입.** 상세 템플릿은 Aggregate 주문에 출고 버튼을 표시하지 않는다. 그 외에는 `canAddFulfillment`가 활성화를 결정한다. 취소되지 않은 출고의 행을 주문 행 ID별로 합산해 주문 수량보다 적은 행이 하나 이상 있어야 한다. 또한 미정산 주문 변경이 없고, 미결제 차액이 정확히 0이며, `nextStates`에 Shipped·PartiallyShipped·Delivered 중 하나가 있어야 한다. 재고는 이 판단에서 조회하지 않는다. 클릭은 현재 주문을 대화상자로 넘긴다. [버튼 노출과 클릭](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.html#L32-L39) · [진입 판단·정산과 결제 차액](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts#L310-L355) · [대화상자와 제출 연결](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/admin-ui/src/lib/order/src/components/order-detail/order-detail.component.ts#L407-L425)
2. **품목 단위 수량.** 대화상자는 같은 주문에서 각 행의 수량에서 해당 행의 취소되지 않은 출고 수량 합계를 뺀다. 상품 변형의 재고 추적이 INHERIT이면 전역 설정을 따르고, TRUE/FALSE이면 해당 값을 쓴다. 추적하면 `min(미출고 수량, stockOnHand)`, 추적하지 않으면 미출고 수량이 상한이다. 초기 선택 수량과 최대 수량에 같은 계산값을 쓴다. 화면의 미출고 표시값과 입력의 max는 다를 수 있다. [초기화·수량·제출 판정](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/admin-ui/src/lib/order/src/components/fulfill-order-dialog/fulfill-order-dialog.component.ts#L38-L98) · [행 표시와 입력](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/admin-ui/src/lib/order/src/components/fulfill-order-dialog/fulfill-order-dialog.component.html#L16-L36)

**검토자가 원문을 따라 계산한 예.** 일반 주문이 PartiallyShipped 상태이며 다음 상태에 Shipped가 있고 미정산 변경은 없다. 세후 주문 합계와 유효 결제액은 각각 100, 환불은 0이다. 재고 추적은 두 품목 모두 INHERIT이고 전역 설정은 켜져 있다.

| 주문 행 | 주문 | 유효한 출고 | 취소된 출고 | 현재고 | 미출고 수량 | 창의 초기 선택 / 상한 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 가 | 3 | 1 | 1 | 0 | 2 | 0 / 0 |
| 나 | 1 | 1 | 0 | 9 | 0 | 0 / 0 |

가 행이 남아 주문의 출고 창은 열 수 있다. 창 안에서는 가의 재고가 0이고 나는 전량 출고되어 두 행 모두 상한이 0이다. 유효한 처리 양식에서도 선택 합계가 0이므로 제출이 비활성화된다. 가의 재고만 1로 바꾸면 창 진입은 같고 가의 상한·초기 선택은 1, 정상 양식에서 제출 가능하다. 이는 코드에서 계산한 프런트엔드 사례이며 실제 재고 예약·서버의 최종 승인·브라우저 실행 관찰은 별개다.

**후속 변경 판정.** 한 가능한 제안은 설정과 행별 상한 계산이 끝난 뒤 어느 행도 양수를 허용하지 않을 때 창에 안내를 표시하는 것이다. 미출고 여부와 재고 제한 등 확인된 원인만 안내할 수 있다. `canSubmit() === false`만으로 이유를 단정하면 사용자가 선택량을 0으로 바꾼 경우나 처리 양식이 유효하지 않은 경우까지 섞인다. 초기 빈 수량 맵도 로딩 완료로 해석할 수 없다. 위 주문에서 안내가 표시되고 생성 버튼은 비활성인 채 취소·닫기가 가능해야 한다. 가의 재고를 1로 바꾼 대조에서는 안내 없이 1개를 제출할 수 있어야 한다. 기존 주문 진입 조건, 수량·폼 검증과 제출 입력 경로를 보존하는지 본다. 문구·파일명·구현 방식이 달라도 같은 원문과 사용자 행동을 설명하면 인정한다. [초기 설정 수신](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/admin-ui/src/lib/order/src/components/fulfill-order-dialog/fulfill-order-dialog.component.ts#L38-L61) · [제출 검증과 결과](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/admin-ui/src/lib/order/src/components/fulfill-order-dialog/fulfill-order-dialog.component.ts#L84-L116) · [닫기와 생성 버튼](https://github.com/vendurehq/vendure/blob/534e6003534f74761e82de1b8c6061cba89945d1/packages/admin-ui/src/lib/order/src/components/fulfill-order-dialog/fulfill-order-dialog.component.html#L55-L59)

## 참가 이후의 판정

- **작성자 첫 사용.** 제삼자가 기록만으로 같은 리비전에서 두 판단, 적용 조건, 둘을 구별하는 주문 예를 다시 찾고 검산할 수 있는지 본다. 동등한 다른 코드 근거·수치 예도 인정한다. 누락되거나 원문과 다른 조건, 추정, 확인하지 못한 사항을 구체적으로 적는다. 답을 가리키는 도움을 받았다면 그 직전까지 스스로 설명한 범위와 이후 보충을 나누어 기록한다.
- **인계.** 제안한 위치에서 안내가 필요한 상황을 식별할 수 있는지, 기존 동작과 회귀 사례를 소스에서 확인한다. 작성자 기록에서 가져온 주장과 추가 탐색으로 보완·교정한 주장을 대응시킨다. 새로 조사해서 올바른 제안을 만든 경우 변경 제안의 타당성과 기록의 재사용 근거를 각각 판단한다.
- **도구 기여와 비용.** 작성자 기록의 핵심 근거별로 최초 발견 수단(IDE·검색·CLI), CLI로 추가 확인한 내용, 실제 열어 본 후보와 무관한 후보 검토 노력을 받는다. 검색만으로 찾았다면 검색으로 기록한다. 준비자가 해 준 설치·빌드, 작성자의 설정·조사·기록, 진행자 도움, agent의 추가 탐색을 별도 실측으로 남긴다. 사전에 채운 시간이나 추정 절감량으로 효과를 판정하지 않는다.
- **판정 경계.** 두 제출이 있기 전에는 미측정을 유지한다. 사람을 구하지 못해 새 agent 두 세션으로 대체한다면 별도 결정 뒤 **대리 검증**으로 표시한다. 그 결과의 범위는 자료로 근거를 복원하고 인계할 수 있는지까지다. 사람의 첫 사용성·사람 소요 시간·조직의 업무 정책 승인은 미확인이다.
