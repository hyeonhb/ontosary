# Vendure 배송비 취소 파일럿 · A 탐색 중 사용량 결측

A는 54.022초 동안 모델 요청 16회를 사용했다. 16번째 요청에서 서버가 용량 부족을 반환했고 CLI에 사용량이 기록되지 않았다. 사전 중단 기준에 따라 B와 C의 요청은 각각 0회다. A의 수정 전 근거와 첫 패치는 모두 미제출이다. 따라서 이번 기록으로 도메인 자료가 수정 품질을 높였는지, 같은 결과를 더 적은 비용에 냈는지는 판정할 수 없다. [실행 지시](2026-11-26-s2-shipping-pilot-instructions.md) · [조건별 판정·비용·차이 전체 표](../../experiments/domain-model/s2/results/2026-11-26-shipping-pilot/tables.md)

| 조건 | 수정 전 근거 두 항목 | 패치와 여섯 사례 | 오류 포함 요청 | 시간 | 확인된 입력 / 출력 토큰 |
| --- | --- | --- | ---: | ---: | --- |
| A · 일반 소스 | 경로 합류·가격 기준 모두 미제출 | 미제출, 사례 실행 0건 | 16 | 54.022초 | 1~15회 44,980 / 452, 16회 결측 |
| B · 구조화 모델 추가 | 미실행 | 사례 실행 0건 | 0 | 0초 | 0 / 0 |
| C · 서술 자료 추가 | 미실행 | 사례 실행 0건 | 0 | 0초 | 0 / 0 |

## A가 확인한 소스와 사용량

A는 첫 검색으로 `cancelOrder(`를 찾아 `OrderService`와 `OrderModifier.cancelOrderByOrderLines`를 읽었다. 이어 배송 행의 할인 가격 getter를 찾고 배송을 취소하는 기존 테스트를 검색했다. 일반 검색 7회에서 51행·6,853바이트, 파일 읽기 8회에서 256행·12,627바이트를 받았다. 응답당 최댓값은 4,096바이트 이내였다. 추가 자료 조회는 0회다. 직접 취소와 환불 동반 취소의 합류 또는 배송 차감·합계의 관계를 참가자가 설명하는 `submit`은 없었다. 검색 결과만으로 점수를 부여하지 않았다. [A의 요청별 행동과 반환 지문](../../experiments/domain-model/s2/results/2026-11-26-shipping-pilot/A)

첫 15회는 모두 같은 요청 모델에 성공했다. 확인된 입력 44,980개에 캐시 입력 3,968개가 포함되며 출력 452개에 추론 출력 8개가 포함된다. 16회 모두 서버 모델 표식은 `gpt-6.2-sol`이었다. 16번째 요청은 정상 응답이나 사용량 없이 1.657초 뒤 종료됐다. CLI가 같은 오류를 오류 이벤트와 턴 실패 이벤트로 기록한 한 요청이다. 이 요청의 비용, 전체 토큰 합계 및 마지막 요청에 의한 토큰 한도 초과량은 결측이다. 재시도·대체 세션·별도 교정 호출은 0회다. [마지막 요청](../../experiments/domain-model/s2/results/2026-11-26-shipping-pilot/A/16.json) · [종료 기록](../../experiments/domain-model/s2/results/2026-11-26-shipping-pilot/A/seal.json)

예정한 세션 3개 중 1개를 시작했다. 전체 요청 한도 72회 중 16회를 사용했고, 관측된 호스트 작업은 A 한도 24회 중 15회다. B−A와 C−A에서 탐색 근거·패치 성공·동일 결과까지의 비용 차이는 산출할 수 없다. 통과·업무 실패·판정 불가 여섯 사례에 대한 실제 저장·반환 금액도 없다. 참가 제출이 없어 원본을 대신 채점하지 않았다. [사전 예산과 판정 기준](../../experiments/domain-model/s2/results/2026-11-26-shipping-pilot/freeze.json)

## 입력과 오프라인 재현

첫 요청 전 커밋 `3fb4efe`에 모델과 추론 강도, A→B→C 순서, 한도, 입력 지문, 평가 리비전, 두 근거 판정 기준을 고정했다. Vendure 부모의 독립 사본 세 개에서 추적 중인 일반 파일 4,981개의 경로·내용 지문이 같았다. 심볼릭 링크 하나와 Git 메타데이터는 공개 파일 목록에서 제외했다. B의 조회 자료 68개, C의 문서 4개는 각각의 파일 지문으로 고정했다. 로컬 HTTP 수신기로 조건마다 첫 입력 및 중립 검색 직후 입력을 받았다. 요청 모델과 medium, 직접 도구 0개, 개발자 메시지 하나와 해당 조건의 공개 요청·자기 이력만 있는 사용자 메시지 하나를 확인했다. 실제 실행은 기존 ChatGPT 로그인 CLI에서 같은 설정을 썼고 HTTP·스트림 자동 재시도를 0회로 설정했다. [수집기](../../experiments/domain-model/s2/trial/angular-shipping/pilot/collect.py) · [동결 기록](../../experiments/domain-model/s2/results/2026-11-26-shipping-pilot/freeze.json)

아래 명령은 참가 모델이나 로그인 CLI 없이 A의 호스트 응답 15개와 모델 요청 16개의 입력 지문을 검산하고 원시 사용량에서 표를 다시 만든다. 새 출력 디렉터리가 필요하다. 이미 부모 리비전이 있는 로컬 Vendure 사본이 있으면 처음 두 Git 명령을 생략하고 그 경로를 사용한다.

```sh
scratch=$(mktemp -d)
git init --bare --initial-branch=baseline -q "$scratch/vendure.git"
git -C "$scratch/vendure.git" fetch -q --depth=1 https://github.com/vendurehq/vendure.git 8dbb6e4063248c3084e5768d613347a3453eda41:refs/heads/baseline
pilot=experiments/domain-model/s2/trial/angular-shipping/pilot
result=experiments/domain-model/s2/results/2026-11-26-shipping-pilot
python3 -B "$pilot/replay.py" "$scratch/vendure.git" "$scratch/replay" > "$scratch/tables.md"
diff -u "$result/tables.md" "$scratch/tables.md"
```

부모 리비전만 새로 받은 사본에서 위 명령을 실행해 표가 바이트 단위로 일치했다. `pnpm check`에서 타입 검사·테스트 304개·예제 빌드가 통과했고 `pnpm experiment`의 기존 비교 4/4가 통과했다.

독립 리뷰에서는 이 중단 기록을 종결할지, 같은 모델의 용량이 확보된 뒤 새 비교를 승인할지 결정할 수 있다. 다시 비교할 경우 중단된 A의 비용을 이번 기록에 남기고 세션 배정과 예산을 먼저 정해야 한다.
