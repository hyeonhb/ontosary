# S2 진단·봉인·정리 보완 독립 리뷰

2026-11-17. [PR #54](https://github.com/hyeonhb/ontosary/pull/54)의 `d97007213c527fc06cc7d3708d7c546b14077d9b`와 [개발 보고서](https://github.com/hyeonhb/ontosary/blob/d970072/docs/reviews/2026-11-17-s2-seal-recovery.md)를 검토했다. **기본 정책 필수 7단위의 기대 결과와 증거 회수는 확인했다. R13·R14·R15·R16은 이번 fixture 범위에서 확인됐지만, R17의 최상위 정리 호출 경로가 남아 PR #54 병합은 보류한다.** 실제 이번 회차의 VM/임시 경로 정리는 완료됐다.

## R17 잔여 · Medium · 감사 기록 예외가 정리 호출을 막는다

위치: [round.py 227–233행](https://github.com/hyeonhb/ontosary/blob/d970072/experiments/domain-model/s2/trial/container/execution-lifecycle/round.py#L227).

`prepare` 또는 `fixtures`가 실패하면 최상위 `main()`은 분석 범위를 동결하고 closing registry와 cleanup snapshot을 기록한 뒤 `r.cleanup()`을 호출한다. 그런데 이 기록 절차를 보호하는 별도 예외 처리/finally가 없다. `analysis-scope.json`·`closing-registry.json` 쓰기나 snapshot 생성이 실패하면 **새 `recovery.cleanup()`에 도달하지 못한다.** 기록 I/O나 snapshot 검증 오류가 VM stop/delete 시도까지 차단한다. 직전 지시의 “기록 실패가 정리를 막지 않는다”는 계약이 최상위 경로에서는 미충족이다.

[독립 재현 스크립트](evidence/2026-11-17-probe-cleanup-dispatch.py)는 실제 `Round` 생성자와 `main()`을 실행하되 prepare/fixtures·cleanup·snapshot의 외부 작업을 대역화한다. 두 action 각각에 scope 쓰기, registry 쓰기, snapshot 오류를 주입한 **6개 사례 모두 cleanup 호출 0회**다. 기록 오류가 없는 대조 2개는 cleanup을 호출하고 최초 실행 오류를 다시 전달한다. VM/네트워크/실제 외부 명령은 실행하지 않았다. 결과는 [검증 JSON](evidence/2026-11-17-s2-seal-recovery-independent.json)에 포함했다.

하위 `recovery.cleanup()`의 회수 오류 분리 자체는 확인됐다. 따라서 해당 모듈을 재설계하기보다 **최상위 감사 기록과 정리 호출을 분리**하면 된다. 감사 등록 실패를 표시하고 유효한 포장/다음 실행은 계속 거부하되, 소유권을 검증하는 기존 cleanup 시도는 반드시 이어져야 한다. 최초 작업 오류와 기록/정리 오류를 함께 보존하고 미등록 snapshot을 성공한 closing 증거로 자동 편입하지 않는다.

이 결함은 이번 7단위의 통과를 뒤집거나 실제 자원이 남았다는 뜻이 아니다. 준비·실행 실패에 감사 기록 실패가 겹치는 별도 경로이며, 기존 로컬 테스트는 cleanup 함수 내부를 검증해 이 진입점 연결을 놓쳤다.

## 확인한 보완

| 항목 | 독립 판단 |
| --- | --- |
| R13 runtime 환경/Spec | 고정 PATH와 알려진 hook 배열 계약을 유지했고 실제 native Spec 7개를 전체 비교기로 재대조했다. 과거 유실됐던 원문·실행 도구 근거가 이번에는 보존됐다. |
| R14 준비물 재사용 | cache hit·download/build/save 0회·새 VM import 1회가 기록됐다. 보관 준비물 4개의 실제 바이트/크기/hash와 이미지 key binding을 다시 대조했다. 준비는 환경 진입부터 47.920초다. |
| R15 metadata/진단 | 전달 UID501 파일을 내용/hash 검증 뒤 UID0/mode0600으로 게시한 기록을 확인했다. 봉인 result와 관리자 진단을 구분하며 거부된 worker 원본을 다시 읽지 않는다. per-file 거부·누적 상한·원자 공개·오류 receipt는 로컬 회귀로, 정상/기대 실패 회수는 실제 archive로 확인했다. |
| R16 service 봉인 | 시작 전 active target reference, InvocationID 연결, 원시 종료 조회와 finalizer 대조, seal 기록 뒤 reference 해제를 확인했다. 실제 7개 invocation과 봉인 증거가 남았다. 이전 실패의 정확한 GC 원인을 소급 확정하지 않는다. |
| R17 회수/정리 | 하위 cleanup의 transport/copy/기록/stop/delete 오류 분리와 유한 회수·정리 reserve는 확인했다. 실제 최종 VM/소유 root 부재도 기록됐다. 위 최상위 감사 실패 경로만 잔여다. |

## 실제 7단위와 검증 한계

| 단위 | 기대 outcome / start 수 | collection | 단위 전체 시간 |
| --- | --- | --- | ---: |
| 정상 1 | exit / 1 | collected | 3.093초 |
| 사전 검사 거부 | precheck-rejected / 0 | suppressed | 2.247초 |
| 시작 실패 | start-failed / 0 | suppressed | 2.224초 |
| timeout | timeout / 1 | collected | 24.770초 |
| host wrapper 사망 | wrapper-death / 1 | collected | 24.325초 |
| 작업 supervisor 사망 | supervisor-death / 1 | suppressed | 24.205초 |
| 정상 2 | exit / 1 | collected | 2.845초 |

모두 단위 120초 제한 안에서 기대 결과·종료/삭제·봉인을 충족한다. collected는 이 fixture의 제한 수집 상태이며 실제 비교 제출의 유효성을 뜻하지 않는다. timeout/wrapper 사망의 늦은 쓰기 검사와 정상 2의 이전 경로 24개 접근 거부도 확인했다. supervisor 사망 뒤 결과 철회·차단과 명시적 복구를 거쳤으며 차단을 무시하고 바로 다음 단위를 실행한 것으로 해석하지 않는다.

준비 1회·각 단위 7회·최종 정리 1회의 회수 envelope 9개가 남았다. 실제 실행에서 진단 파일 거부/partial/error-receipt나 독립 관찰자 사망·transport 장애를 추가 주입한 것은 아니다. 그 부분은 로컬 실패 회귀 범위이며 실제 전체 장애 공간 검증을 주장하지 않는다. 실제 CLI native sandbox/인증 연결과 정책 pair는 여전히 미실행이다.

## 독립 검증

- 검토 head에서 `pnpm check` 304개(skip 0)·타입·예제 build와 Python execution-lifecycle 114개, 공유 lifecycle 16개, 감사 44개, 총 174개를 통과했다.
- 새 verifier의 259파일·분석 5/closing 3, whole Spec 7개·service seal 7개·회수 9개를 재현했다. 과거 두 회차 verifier도 통과했으며 원시 실패 기록은 보존됐다.
- final-source 81파일이 검토 head와 일치한다. 전달 archive 36파일의 hash와 현재 전달 코드가 일치하고 실행 후 변경된 전달 코드는 없다. 최초 3,230파일 중 3,213파일 불변·허용 변경 17개·예상 밖 변경 0개를 다시 확인했다. 최종 문서 변경은 실행 코드 변경과 구분한다.
- 실제 보관 준비물 4개와 이미지 binding을 다시 읽어 확인했다. 저장 cleanup은 evidenceStatus=diagnostic, cleanupStatus=complete, 오류 없음, VM/root 부재이며 정리 1.006초다. VM 폐기를 개별 단위 종료 증명으로 대신하지 않는다.
- 이 리뷰에서는 새 VM·정책·자격 증명·모델 호출을 하지 않았고 제품/실험 구현을 수정하지 않았다. TS 분석/FCA/평가 의미가 불변이므로 `pnpm experiment`와 Linux Vendure 평가를 반복하지 않았다.

## 방향과 다음 작업

기존 경계를 바꿀 근거는 없다. 준비 비용이 47.920초로 줄고 7단위가 83.830초에 완료됐으며 원시 진단도 회수돼, 앞선 반복의 핵심 병목이 해소됐다. 남은 문제는 호스트 오류 처리의 연결 하나다. 새 범용 실행기나 추가 VM 시험을 만드는 대신 [로컬 60분 상한의 보완 지시](2026-11-17-s2-cleanup-dispatch-instructions.md)를 함께 제공한다. 이 지시는 합의된 실패 정리 계약의 보완이며 새 아키텍처/권한/실제 실행 승인이 아니다.

PR #54는 보완 결과 리뷰까지 미병합으로 둔다. 보완 후에는 기존 7단위 증거와 새 호스트 회귀를 함께 판단하고 다음 정책/CLI 단계의 범위와 예산을 별도로 정한다. R11 unresolved·R12 기존 범위·production/live 거부·fixtureOnly=true·validSubmission=false·trialAuthorized/readyForTrial=false·results=null을 유지한다. 이 성과는 실험 운영 기반의 진전이며 도메인 모델의 agent 변경 효용(H-O)이나 FCA의 모델 구축 기여(H-F)를 입증한 결과는 아니다.
