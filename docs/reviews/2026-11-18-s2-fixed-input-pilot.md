# Vendure 주문 취소 고정 입력 패치 파일럿 · 2026-11-18

| 조건 | 첫 패치 적용 | 타입 | 기존 동작 | 변경 요구 | 전체 | 경과 시간 | 입력 / 출력 토큰 |
| --- | --- | --- | ---: | ---: | --- | ---: | ---: |
| A · 소스와 과업 | 성공 | 통과 | 16/16 | 36/36 | 통과 52/52 | 26.411초 | 37,786 / 903 |
| B · 구조화 뷰 추가 | 성공 | 통과 | 16/16 | 36/36 | 통과 52/52 | 26.126초 | 64,770 / 891 |
| C · 서술 문서와 근거 부록 추가 | 성공 | 통과 | 16/16 | 36/36 | 통과 52/52 | 19.414초 | 69,262 / 662 |

독립 세션 3/3이 첫 응답을 제출했고 전체 소스 3/3을 채점했다. 이번 과업은 A만으로도 만점에 도달했다. 지식 추가(A/B)나 표현 방식(B/C)에 따른 정확도 차이를 관측하지 못했다. [점수와 제출 지문](../../experiments/domain-model/s2/results/2026-11-18-fixed-input-pilot/results.json)

## 패치가 바꾼 동작

- **취소와 환불에 서로 다른 사유를 전달했다.** 교정 원본은 혼합 흐름에서 양쪽 요청에 모두 앞뒤 공백을 포함한 사유를 전달했다. 세 제출은 취소에 `spaced`, 환불에 원래 값 `"  spaced  "`를 전달했다. 공백만 있는 혼합 입력에서는 원본의 취소·환불 두 요청이 모두 사라졌다. 해당 사례는 `o-one/refund-reason-1`과 `o-one/refund-reason-3`이다. [원본 관측](../../experiments/domain-model/s2/results/2026-11-18-fixed-input-pilot/baseline.json.gz) · [A 관측](../../experiments/domain-model/s2/results/2026-11-18-fixed-input-pilot/4fb4a73fa9/evaluation.json.gz)
- **빈 사유를 받은 서비스가 값을 방출하지 않고 완료했다.** `o-one/api-reason-2`에서 원본은 빈 사유로 취소를 호출한 뒤 값을 한 번 방출했다. 세 패치의 서비스는 `EMPTY`를 반환했고 세 기록 모두 요청 0회, 값 0개, 완료 1회였다. [B 패치](../../experiments/domain-model/s2/results/2026-11-18-fixed-input-pilot/65f6ff9224/answer.txt) · [C 관측](../../experiments/domain-model/s2/results/2026-11-18-fixed-input-pilot/1e52ddfadf/evaluation.json.gz)

**구현 차이는 주문 상세 화면에 있었다.** A와 B의 diff 문맥은 다르지만 적용한 전체 소스의 지문은 같았다. C도 서비스와 두 대화상자에는 동일한 코드를 제출했다. A/B만 주문 상세 화면의 두 분기에서 `of(undefined)`를 `EMPTY`로 바꿨다. 취소 대화상자가 결과 없이 닫히면 전자는 다음 `switchMap`에 값을 전달하고 후자는 전달하지 않는다. 기존 `refetchOrder(undefined)`는 `fetchHistory.next()`를 호출하며, 이 신호는 구독 중인 화면의 이력 조회에 연결된다. 52개 사례의 상세 관측은 세 조건에서 모두 같았다. 실제 화면의 이력 조회 횟수는 이번 평가로 확정할 수 없다. [A 패치](../../experiments/domain-model/s2/results/2026-11-18-fixed-input-pilot/4fb4a73fa9/answer.txt) · [C 패치](../../experiments/domain-model/s2/results/2026-11-18-fixed-input-pilot/1e52ddfadf/answer.txt)

## 입력과 실행 통제

Vendure revision `534e6003534f74761e82de1b8c6061cba89945d1`의 공개 inventory에서 `packages/admin-ui/src/` 아래 파일명에 `order`, `cancel`, `refund` 중 하나가 들어간 생산 TypeScript 파일을 경로순으로 골랐다. 선언·spec·test 접미사와 generated·testing·__tests__ 디렉터리를 제외했다. 42개 파일의 원문 전체와 경로, 현행 공개 업무 요구와 지원 문법, 제출 형식을 세 조건에 똑같이 제공했다. 입력 선정기는 비공개 사례·참조 패치를 읽지 않는다. 공통 본문은 193,374바이트였고 B 전체는 289,631바이트, C 전체는 300,540바이트였다. [공개 과업](../../experiments/domain-model/s2/trial/task.ts) · [선정기](../../experiments/domain-model/s2/trial/fixed-input/packets.py) · [공통·패킷·개별 파일 SHA-256](../../experiments/domain-model/s2/results/2026-11-18-fixed-input-pilot/inputs.json)

B는 11월 10일의 변경 전 JSON 뷰 68개 전체, C는 대응하는 서술 문서 3개와 원문·메타데이터 부록 1개 전체를 그대로 받았다. 당시 대조한 단위는 해석 12개, 코드 주장 22개, 역할 후보 2개, 고유 관계 16개, 인용 30개였으며 구조 대응은 1,511개 leaf였다. 이번 조립에서는 정책이나 풀이 설명을 추가하지 않았다. 자료는 취소 요청과 환불 흐름의 연결을 설명하지만 각 모델이 어떤 자료를 사용했는지는 첫 패치에서 식별할 수 없다. 사람의 업무 의미 동등성 검토는 pending이다. [기존 독립 의미 대조](2026-11-10-s2-trial-preparation-independent-review.md) · [대응 기록](../../experiments/domain-model/s2/results/2026-11-10-trial-preparation/evaluator/information-parity.json)

세션 설정은 기존 로그인 Codex CLI `0.167.0-alpha.3.2`, 요청 모델 `gpt-6.2-astra`, reasoning `medium`이었다. 모델 카탈로그의 지원 범위 안에서 문맥을 512,000토큰으로 설정했다. 유효 문맥 486,400토큰에 대해 가장 큰 입력을 UTF-8 바이트당 최대 1토큰으로 잡고 공통 지시, framing 4,096토큰, 출력 49,152토큰의 여유를 더해도 들어갔다. 실제 제출 제한은 세 조건 모두 49,152 UTF-8 바이트, 시간은 각 1,800초였다. 시간은 CLI 시작부터 종료까지이며 출력 제한은 제출 검수에서 적용한다. 표의 입력·출력은 CLI 원시 usage다. 캐시 읽기·쓰기는 전부 0이며 출력에 포함된 reasoning은 A/B/C 각각 67/50/0이었다. 모델 내부 빌드 번호는 CLI가 보고하지 않았다. [동결한 배정·예산](../../experiments/domain-model/s2/results/2026-11-18-fixed-input-pilot/plan.json)

참가 호출 전 기존 Codex의 `debug prompt-input`에서 기본 도구 노출을 확인하고, 파일럿 설정에서 도구 목록이 비었음을 확인했다. 별도 인증이 없는 로컬 수신기로 같은 CLI에 세 패킷을 각각 넣었을 때 요청의 최상위·입력 항목 도구는 모두 0개였고 본문은 공통 developer 지시 한 개와 해당 user 패킷 한 개였다. 수신기는 모델을 호출하지 않았다. 실제 실행은 별도의 빈 디렉터리에서 임시 세션을 세 번 시작했다. 무작위 배정 순서는 B, C, A였다. 서로 다른 thread ID 세 개에서 각 1턴, 도구 이벤트 0개, 첫 답변 한 개를 확인했다. 입력·설정·교정·채점 규칙을 커밋 `2dfc437`에서 먼저 고정했고, 세 원응답의 해시를 모두 봉인한 뒤 채점했다. [사전 관측](../../experiments/domain-model/s2/results/2026-11-18-fixed-input-pilot/preflight.json) · [실행기](../../experiments/domain-model/s2/trial/fixed-input/session.py)

## 채점과 재현

첫 교정 때 기존 준비 환경의 RxJS 런타임이 빠져 있었다. 별도 복사본에서 고정 Vendure 잠금 파일의 SHA-512와 대조한 rxjs 7.8.2와 tslib 2.8.1의 누락 파일을 복원했다. 최종 참가 호출 전에 원본 전체와 참조 패치를 적용한 전체 소스로 v4를 실행했다. 두 제출 모두 타입을 통과했고, 원본은 기존 16/16·변경 6/36, 참조는 16/16·36/36을 재현했다. [교정 결과와 원시 파일 지문](../../experiments/domain-model/s2/results/2026-11-18-fixed-input-pilot/calibration.json) · [환경 복원 근거](../../experiments/domain-model/s2/results/2026-11-18-fixed-input-pilot/environment-recovery.json)

참가 제출마다 원본 전체를 새로 복사해 Git으로 패치를 적용했다. 적용 검사에 실패할 때만 `--recount`로 hunk 줄 수를 다시 계산한다. 원응답·변경 줄·문맥은 보정하지 않았다. 파일 경로와 일반 파일 여부를 검사한 뒤 macOS sandbox-exec에서 전체 제출·준비 환경·새 결과 파일을 v4에 전달했다. 네트워크·자식 프로세스·일반 파일 쓰기를 차단하고 결과 파일 쓰기만 허용했다. 세 결과에서 모두 `inputMode=complete-root`, `sourceBinding=true`와 같은 evaluatorId를 확인했다. [격리된 평가 진입점](../../experiments/domain-model/s2/trial/fixed-input/evaluate.py) · [패치 적용기](../../experiments/domain-model/s2/trial/fixed-input/grade.py) · [원시 근거](../../experiments/domain-model/s2/results/2026-11-18-fixed-input-pilot/)

실제 패킷 원문은 로컬의 `work/s2-fixed-pilot/inputs/{A,B,C}.txt`에 보존했다. 원격 리뷰어는 고정 Vendure 소스와 저장소에 있는 B/C 자료로 동일 바이트를 복원할 수 있다. 아래 두 명령은 참가 모델 호출 없이 세 패킷·봉인·교정·제출 점수를 검사한다. Vendure 원문 및 패치 속 원문 문맥에는 upstream 고지가 적용된다. [소스·라이선스 고지](../../experiments/domain-model/s2/results/2026-11-10-trial-preparation/A/SOURCE-NOTICE.txt)

```sh
python3 experiments/domain-model/s2/trial/fixed-input/packets.py "$VENDURE_ROOT" work/s2-fixed-pilot/rebuilt
python3 experiments/domain-model/s2/trial/fixed-input/verify.py experiments/domain-model/s2/results/2026-11-18-fixed-input-pilot work/s2-fixed-pilot/rebuilt
```

세 원응답을 새 복사본에 다시 적용해 각 제출 지문과 52개 상세 관측이 첫 채점과 일치함을 확인했다. 재채점에 추가 참가 호출은 없었다. 저장소 검사 `pnpm check`는 타입 검사, 304개 테스트, 예제 빌드를 통과했다.

## 다음 실험 판단

조건당 패치 한 개가 표본이다. 52개는 그 패치에 대한 검사 항목이다. 공개 과업이 분기·종료·보존할 동작을 구체적으로 지정했고, 공통 입력에 수정 대상 파일 전체가 포함됐다. A가 이 조건에서 만점에 도달했으므로 같은 입력을 반복해 얻을 추가 정확도 정보는 제한적이다. B와 C는 각자 더 긴 입력을 사용했고 C는 가장 짧은 출력을 냈다. 한 번의 생성 시간과 수정 파일 수로 표현 방식의 우열을 판단하기 어렵다.

도구를 갖춘 본 비교에 투자할 근거는 **자료가 올바른 수정 위치를 찾는 데 드는 탐색 비용을 줄이는지**에 있다. 다음 비교를 결정한다면 첫 관련 파일까지 걸린 시간과 탐색한 파일 수를 정확도와 함께 관측하는 편이 이 파일럿과 구분되는 질문에 답한다. 실제 앱 이력 갱신까지 요구하는지는 별도의 업무 계약 결정이다. 이번 결과는 본 비교의 기존 실행 차단을 해제하지 않으며, FCA의 모델 구축 기여도 측정하지 않았다.
