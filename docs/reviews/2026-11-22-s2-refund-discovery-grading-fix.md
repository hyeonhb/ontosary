# 환불 잔액 탐색 비교 준비 · R23–R25 보완

PR #96의 모의 제출 12개를 각각 고정 Vendure 소스 4,735개에서 시작해 편집·봉인하고, 회수한 전체 소스를 같은 채점기로 판정했다. 독립 리뷰에서 만점을 받았던 인라인 화살표 바인딩은 Angular 구문 오류로 실패했다. 명시적인 제출 예외는 메뉴가 보이는 9개 사례에서 제출 실패로 기록했다. A/B/C 모두 첫 공개 입력의 예시를 그대로 전송해 검색에 성공했다. 실제 참가 모델 호출은 0회다. [독립 리뷰의 원래 반례](2026-11-22-s2-refund-discovery-independent-review.md)

## 대조별 판정

모든 사본이 고정 strict TypeScript 검사(Program 1,638개 파일)를 통과했다. 표의 동작 통과 수는 메뉴 노출·문구와 클릭 후 모달 호출을 함께 만족한 건수다. 실행 전 중단한 대조에는 점수를 부여하지 않았다. 원시 기록은 작업별 기대값, 실제 편집, 전체 제출 지문, 읽은 원본·변경 파일 지문, 사례별 기대값과 관측값을 포함한다. [12개 사본의 채점 기록](../../experiments/domain-model/s2/results/2026-11-22-refund-discovery-fix/results.json)

| 제출 | 기대한 최종 판정 | 실제 판정 | 동작 통과 | 근거 |
| --- | --- | --- | ---: | --- |
| 원본 | 실패 | 실패 | 9/11 | 전액 소진·Pending으로 잔액 소진 시 문구와 경로가 모두 어긋났다. |
| 문구만 수정 | 실패 | 실패 | 9/11 | 같은 두 사례에서 취소로 표시했지만 환불 모달을 열었다. |
| 기존 공유 판별 함수 수정 | 성공 | 성공 | 11/11 | 기존 HTML과 수정한 TypeScript를 함께 평가했다. |
| 새 잔액 함수로 문구·클릭 수정, A/B/C 각 1개 | 성공 | 모두 성공 | 각 11/11 | 세 사본의 전체 제출 지문과 봉인 답안이 일치했다. |
| R23 인라인 화살표 바인딩 | 실패 | 실패 | 실행 전 중단 | Angular가 제출 HTML 55행 35열의 바인딩에서 4종의 구문 오류를 보고했다. |
| R23 유효한 삼항식 | 미지원 | 미지원 | 실행 전 중단 | 같은 정상 함수에 `? true : false`를 붙였다. Angular 진단은 0개이고 관측기가 지원하지 않는 노드는 `Conditional`이다. |
| R24 잔액 메서드의 명시적 예외 | 제출 실패 | 제출 실패 | 2/11 | 9개 문구 평가에서 제출한 `order-detail.component.ts` 574행의 `throw new Error("Missing refund calculation")`가 실행됐다. |
| R24 Angular 폼 초기화 필요 | 평가 환경 오류 | 평가 환경 오류 | 2/11 | 제공하지 않는 `detailForm`에 접근한 9개 사례에서 평가 대역이 오류 출처를 기록했다. |
| R24 미지원 외부 의존성 | 미지원 | 미지원 | 2/11 | 타입이 유효한 `@angular/core:isDevMode` 호출을 실행기가 지원하지 않아 9개 사례에 의존성 이름을 기록했다. |
| R24 출처를 특정할 수 없는 예외 | 미지원 | 미지원 | 2/11 | 빈 주입 필드에서 `formBuilder.group`을 읽다가 난 TypeError는 9개 사례 모두 귀속 미상이다. |

R24의 네 대조에서 통과한 두 사례는 Aggregate 주문과 Cancelled 전이가 없는 주문이다. 메뉴가 숨겨져 잔액 메서드를 호출하지 않았다. 다른 9개 사례는 각각 이름, 오류 발생 단계, 오류 종류를 기록한다. 제출 파일·행은 실행된 제출의 throw 지점에서 그 예외 값을 확인했을 때 기록한다. 소스 바이트의 해시와 타입 검사는 계측 전 원문으로 확인한다. [메뉴 평가](../../experiments/domain-model/s2/trial/discovery/menu.ts) · [오류 출처 계측](../../experiments/domain-model/s2/trial/complex/evaluator/errors.ts)

## Angular가 확인한 범위

Vendure 리비전 `534e6003534f74761e82de1b8c6061cba89945d1`의 잠금 파일과 같은 버전·패키지 무결성 값으로 MIT 라이선스의 `@angular/compiler@19.2.15`를 개발 의존성에 고정했다. 채점기는 제출 HTML 전체를 `parseTemplate`로 파싱한다. 결과에 컴파일러 버전, 패키지 무결성, 실행 모듈과 제출 HTML의 SHA-256을 남긴다. Angular가 같은 오류를 후속 바인딩에 반복한 경우 메시지와 최초 위치, 발생 횟수를 기록한다.

문법 검사를 통과하면 확인된 버튼 구조 안에서 Angular가 만든 노출·문구 조건 및 클릭 구문 트리를 읽는다. 속성 읽기, 메서드 호출, 지원하는 논리·비교식 등을 해석한 뒤 제출 컴포넌트의 실제 메서드를 실행한다. 관측 범위 밖의 구문이나 템플릿 구조는 미지원이다. 이 검증은 고정 템플릿의 구문 및 해당 동작을 다루며 Angular 앱 전체의 빌드나 브라우저 렌더링을 증명하지 않는다. [지원하는 바인딩과 구조](../../experiments/domain-model/s2/trial/discovery/template.ts)

## 첫 공개 요청과 로컬 재현

세 조건 모두 공개 입력에 필수 키 `op`와 아래 예시 객체를 받는다. 모의 참가자는 예시 객체를 복사해 첫 작업으로 전송한다. 다른 키를 삽입하거나 정답 경로를 전달하는 과정 없이 세 조건이 같은 검색 결과 32행을 받았다. 모의 절차에서 이미 검색한 호출 위치를 다시 읽던 작업 하나를 제외해 기존 공통 작업 한도 안에서 끝냈다. 과업, B/C 자료와 네 가지 발견 판정 기준은 종전과 같다.

```json
{"op":"search","space":"source","query":"license"}
```

기존 CLI의 로컬 HTTP 수신기로 조건별 첫 입력, 첫 작업 직후, 세 번째 작업 직후의 요청 총 9개를 대조했다. 첫 입력에는 공개 예시가 들어 있고 첫 작업 뒤 이력에는 동일한 작업과 실제 반환값이 들어 있다. 수신 본문의 지문·도구 목록·첫 반환값의 행 수와 지문을 보관했다. 모두 루프백에서 HTTP 400으로 종료됐다. [공개 입력과 정상 사본 3개의 작업 기록](../../experiments/domain-model/s2/results/2026-11-22-refund-discovery-fix/traces.json) · [로컬 HTTP 대조](../../experiments/domain-model/s2/results/2026-11-22-refund-discovery-fix/wire.json)

기존 준비 환경에서 아래 명령을 실행한다. 출력 디렉터리는 새 경로를 지정한다. `--verify`는 원본·자료 지문과 전체 사본 회수, 각 대조의 판정·오류 출처, 보관한 결과 및 작업 기록의 바이트 일치를 검사한다. 실제 비교의 요청 수·토큰·시간 예산은 보완 리뷰 후 결정한다.

```sh
pnpm install --frozen-lockfile
pnpm s2:build
runner=experiments/domain-model/s2/trial/discovery
evidence=experiments/domain-model/s2/results/2026-11-22-refund-discovery-fix
out=work/refund-fix-independent-review
python3 -B "$runner/replay.py" work/s2-contract-workspace-a/source work/s2-fixed-pilot/env "$out" --verify
python3 -B "$runner/wire.py" "$out/traces.json" "$out/wire.json"
cmp "$evidence/wire.json" "$out/wire.json"
pnpm check
pnpm experiment
```

저장소 검사에서 타입 검사·테스트 304개·예제 빌드와 실험 비교 4/4가 통과했다. 보완 전 결과와 당시 명령은 PR의 원래 커밋에서 재현할 수 있다. [31c3f29의 준비 보고서](https://github.com/hyeonhb/ontosary/blob/31c3f29ca4a5ead7e25ea7fb017feb52a6bc15b7/docs/reviews/2026-11-22-s2-refund-discovery-preparation.md)
