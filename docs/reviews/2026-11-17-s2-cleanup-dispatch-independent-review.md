# S2 최상위 정리 호출 보완 독립 리뷰

2026-11-17. [인계 보고서](2026-11-17-s2-cleanup-dispatch-fix.md)와 PR #54의 `153f8878b1e929f2ef221cf63143d3b8c312c146`을 검토했다. 실행 구현은 `e4474f29c715bacf01793de7b78e2163f28ea581`과 같다. **R17 잔여는 해결됐다. 이번 변경 범위에서 추가 차단 결함을 발견하지 않았으며, PR #54를 검증한 head로 병합했다.** 병합 commit은 `7f2f1794b6240086079828338dff5f4c3f505e1a`다. 다음은 기존 후보 한 행의 제한된 정책 대조를 검토할 수 있는 상태다. 실제 인증·모델 호출·S2 본 비교 준비 완료라는 판정은 아니다.

## R17 해결 근거

[round.py](../../experiments/domain-model/s2/trial/container/execution-lifecycle/round.py)의 `failed_dispatch()`는 감사 등록을 시도하는 try와 cleanup을 호출하는 finally를 분리했다. scope/registry/snapshot 생성·등록·검증 오류가 있어도 cleanup 호출 지점에 도달한다. 파일/출력 진단의 최종 시도는 cleanup 뒤에 있고, 그것이 실패해도 정리를 다시 호출하지 않는다.

추가 오류가 없으면 최초 예외 객체를 그대로 다시 전달한다. 추가 오류가 있으면 최초 오류와 감사/정리/기록/출력 오류를 ExceptionGroup에 보존한다. cleanup 호출 여부와 cleanup의 성공 여부도 구분한다. 이 구조는 기존 회수/소유권/삭제 구현을 바꾸지 않으면서 최상위 연결을 고친다.

감사 실패를 숨겨 성공한 회차로 포장하지 않는다. 기존 부분 registry를 지우지 않고 실제 등록/ID/hash/명령을 검증한다. 등록 도중 남은 orphan은 실제 package가 거부한다. 실패 marker가 유실돼도 seal은 유효한 cleanup closing 등록을 먼저 요구하므로 seal snapshot을 추가해 감사 누락을 덮지 않는다. 다음 분석 실행의 진입점도 동결/실패/정리 기록이 있으면 거부한다.

[새 회귀](../../experiments/domain-model/s2/trial/container/execution-lifecycle/test_dispatch.py)는 실제 main/argparse/Round와 snapshot/package를 사용한다. 기존 cleanup까지 연결한 사례에서는 가짜 export 오류 후 stop→delete→부재 확인까지 도달하고 임시 소유 root가 제거된다. mock된 cleanup 호출 횟수만 검증한 보완이 아니다.

## 독립 검증

- 검토 head에서 `pnpm check` **304개**, skip 0·타입·예제 build 통과. Python execution-lifecycle **133**, 공유 lifecycle **16**, 감사/deadline/package **44**, 총 **193개**가 통과했다. 새 dispatcher 테스트는 19개다.
- 개발 테스트와 별도로 [독립 probe](evidence/2026-11-17-probe-cleanup-dispatch-fixed.py)를 실행했다. prepare/fixtures 각각 scope 쓰기·registry 쓰기·snapshot 실패 6개 모두 cleanup **1회**, 최초 오류 보존, 감사 불완전 표시와 seal 거부를 확인했다. 기록 성공 대조 2개도 cleanup 1회이며 실제 감사 등록을 통과했다. 외부 명령/VM 실행은 0회다.
- 새 로컬 evidence의 index 대상 **17파일**을 바이트/크기/hash와 대조했고 두 실행 코드의 최종 hash도 일치했다. `d970072`의 verification 및 docs/reviews/evidence 전체를 기준으로 기존 **2,324파일** 불변을 확인했다. 이 수는 개발 보고서의 2,229파일보다 넓은 Git 경로 집합을 센 것이며 같은 분모로 비교하지 않는다.
- 과거 11월 14일·15일·17일 저장 verifier 3개를 재실행했다. 실제 7단위 자료는 **259파일·분석5/closing3·Spec7개·service seal7개·회수9개**로 유지된다. 이번에 새 runtime을 실행한 것은 아니다.
- 변경은 round.py·새 test_dispatch.py와 문서/새 로컬 증거다. recovery/guest/engine/reference/exporter·정책/cache·공유 감사/package·제품/FCA/모델/평가 의미는 불변이다. `pnpm experiment`와 Linux Vendure 전체 평가를 반복할 이유는 없었다.

검증 요약은 [JSON](evidence/2026-11-17-s2-cleanup-dispatch-independent.json)에 남겼다. 구현 PR은 검사와 자체 리뷰 후 정확한 head로 병합했으며 다른 사람의 승인을 받았다고 주장하지 않는다.

## 남는 한계와 다음 판단

파일 시스템 전체가 실패하면 영속적인 실패 marker까지 보장할 수 없다는 보고는 타당하다. 이번 계약은 현재 호출의 정리 시도·오류 전달·감사 없는 seal 거부다. 호스트 자체의 사망/전원 손실까지 해결했다는 주장은 없으며 이를 이유로 새 영속 실행 플랫폼을 만들 필요도 없다.

최초 UTC와 monotonic을 동시에 기록하지 못한 점은 절차상 한계다. 더 이른 UTC부터 745.750초를 계산해 60분 상한을 충분히 지켰고 실제 runtime은 없으므로 병합 차단 사유로 보지 않는다. 다음 실제 회차는 첫 명령에서 두 시계를 함께 기록해야 한다.

R13~R17 보완과 기본 정책 fixture 수명주기는 이번까지의 검증 범위에서 완료다. 검증된 준비물 재사용·일회성 VM·공통 종료/수집 경계를 유지한다. 다음은 [기존 정책 한 행 대조 재개 지시](2026-11-17-s2-policy-pair-resume-instructions.md)를 권고한다. 동일한 원래 정책1회/후보1회에 한정하고 첫 clone 통과 또는 다음 차단점을 관찰한다. 후보의 전체 CLI sandbox 충분성은 아직 알 수 없다.

이 리뷰와 지시 작성에서는 새 VM·정책 적용·인증·모델 호출을 하지 않았다. R11 unresolved·R12 기존 범위·production/live 거부·fixtureOnly=true·validSubmission=false·trialAuthorized/readyForTrial=false·results=null을 유지한다. S2 모델 효용(H-O)과 FCA 기여(H-F)는 여전히 미검증이며, 운영 기반 완료를 제품 가설의 성과로 계산하지 않는다.
