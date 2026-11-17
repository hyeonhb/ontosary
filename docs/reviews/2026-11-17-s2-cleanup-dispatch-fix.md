# S2 최상위 실패 처리의 정리 호출 보완

2026-11-17. **R17 잔여 보완·로컬 검증 완료, 독립 결과 리뷰 대기**다. 감사 기록의 실패가 prepare/fixtures 실패 후 cleanup 호출을 막지 않도록 수정했다. 실제 main dispatcher의 실패 경로와 기존 cleanup 연결을 검증했으며 새 VM/runtime 실행은 0회다. 이전 실제 7단위는 저장 증거만 재대조했다. PR #54는 갱신 후 병합하지 않는다.

## 기준과 변경 범위

[지시](2026-11-17-s2-cleanup-dispatch-instructions.md), [독립 리뷰](2026-11-17-s2-seal-recovery-independent-review.md)를 따랐다. 기준 head는 `d97007213c527fc06cc7d3708d7c546b14077d9b`, 통합한 main은 `1608f23`, 통합 commit은 `bc08b84`다. 기존 `codex/s2-execution-lifecycle` 브랜치와 PR #54를 이어 사용했다. 사용자 docs worktree는 수정하지 않았으며 force-push하지 않는다.

**최종 구현 head는 `e4474f29c715bacf01793de7b78e2163f28ea581`**다. 이후 보고/맥락/evidence 문서 commit은 실행 코드를 변경하지 않는다. 코드 변경은 `execution-lifecycle/round.py`와 새 `test_dispatch.py` 두 파일이다. 기존 `recovery.cleanup()`·guest/engine/reference/exporter·정책/cache·공유 감사/package·제품 core/CLI/FCA·모델/TASK/B/C·배포 ID·평가 의미와 과거 원시 자료는 그대로다. 최종 hash/불변 검사와 명령 결과는 [새 로컬 증거](evidence/2026-11-17-cleanup-dispatch/)에 있다.

## 재현과 오류 전달

수정 전 기준 head에서 [역사적 probe](evidence/2026-11-17-probe-cleanup-dispatch.py)를 실행했다. prepare/fixtures 각각 scope 쓰기·registry 쓰기·snapshot 실패 총 **6개에서 cleanup 0회**, 기록 성공 대조 2개는 cleanup 1회였다. [수정 전](evidence/2026-11-17-cleanup-dispatch/before.json)과 [수정 후](evidence/2026-11-17-cleanup-dispatch/after.json)를 분리했다. 역사적 probe의 결함 assertion을 수정 후 성공시키도록 변경하지 않았다.

실제 `main()`이 호출하는 작은 `failed_dispatch()` 안에 감사 등록 try와 cleanup finally를 둔다. cleanup 호출 지점은 하나이며 정확히 한 번 시도한다. 최초 실패 marker 기록, 분석 동결, closing snapshot 생성/등록, 그 유효성 검사 중 어느 예외도 finally를 건너뛰지 않는다. 실패 진단의 최종 파일/출력 시도는 cleanup 뒤에 있다. cleanup 예외나 진단 쓰기/출력 예외로 재귀 정리를 시작하지 않는다.

추가 오류가 없으면 최초 예외 객체를 그대로 다시 전달한다. 추가 오류가 있으면 최초 객체와 phase별 오류를 `ExceptionGroup`에 보존해 비정상 종료한다. phase는 `audit-registration`, `cleanup`, `failure-record-before-cleanup`, `failure-record-after-cleanup`, `stderr`다. 원래 traceback/예외 객체를 메시지로 대체하지 않는다. 작은 `dispatch-failure.json`에는 action, auditRegistered, cleanupAttempted, cleanupStatus와 제한된 메시지를 기록한다. stderr도 최대 8KiB로 제한하며 문자열 변환/파일/출력 실패 자체를 오류로 남긴다. 모든 저장 경로가 실패하면 영속 기록을 주장하지 않으며 예외와 가능한 stderr만 남는다.

## 감사 실패를 성공으로 포장하지 않음

감사 성공은 기존 실제 `registered_scope()`의 명령·phase·ID·hash 대조로 확인한다. 기존 closing registry를 빈 목록으로 덮어쓰지 않는다. snapshot 생성 뒤 등록 실패로 남은 orphan은 보존되고 실제 package가 `unclassified`로 거부한다. scope/registry 불완전 상태도 포장되지 않는다.

실행 entrypoint는 동결/실패/cleanup 기록이 있으면 다음 분석 실행을 거부한다. seal은 실패 marker의 auditRegistered를 확인하고, marker까지 유실됐어도 **실제 cleanup command의 유효 closing 등록**을 먼저 요구한다. 이 검사는 새 seal snapshot 생성 전과 직접 `Round.seal()` 경로에 모두 적용한다. 누락 hash를 만들거나 미등록 snapshot을 자동 편입하지 않는다. 기존 package의 공통 감사 의미는 바꾸지 않았으며 runtime 회차의 유효 봉인 entrypoint에서 필수 등록을 검사한다.

감사 등록 성공과 자원 정리 성공은 별도다. 정상 등록 후 작업 실패의 진단 포장은 가능하지만 작업 성공으로 승격하지 않는다. cleanup 예외이면 cleanupStatus는 unknown이고, 감사 실패와 실제 소유 자원 정리 성공이 동시에 존재할 수 있다. 파일 시스템 전체 실패 시 다음 프로세스가 읽을 영속 marker까지 보장할 수는 없지만 현재 호출은 비정상 종료하며 자동 후속 작업을 하지 않는다. 유효한 감사 등록 없는 seal은 계속 거부한다.

## 실제 진입점 회귀

새 테스트는 임시 work/실제 Round 생성자·argparse/main을 사용하고 prepare/fixtures 외부 작업만 대역화한다. 실제 snapshot/등록/hash/패키지를 연결해 호출 횟수만 검사하는 테스트로 끝내지 않았다.

| 사례 | 확인 결과 |
| --- | --- |
| prepare/fixtures 최초 실패, 기록 성공 | cleanup 각각 1회, 최초 객체 유지, 분석 1/closing 1 실제 검증·진단 package 가능 |
| 두 action 각각 scope/registry/snapshot 실패 6개 | cleanup 각각 1회, 최초/감사 오류 구분, auditRegistered=false, 다음 실행·seal 거부 |
| 실제 snapshot의 registry 임시 쓰기 실패 | orphan 보존, 자동 편입 없음, 실제 package 거부 |
| 기록 실패+cleanup 예외 | 최초/감사/cleanup 오류 보존, 정리 1회·비정상 종료 |
| 실패 기록/stderr/모든 record 쓰기 실패 | cleanup 시도 유지, 출력 오류도 ExceptionGroup에 남음 |
| 실패 marker 유실+snapshot 오류 | cleanup 등록 부재를 검사해 seal snapshot 추가 전에 거부 |
| 긴 오류/문자열 변환 불가 오류 | 제한된 진단·최초 객체 유지·cleanup 1회 |
| 기존 부분 registry | 빈 목록으로 덮어쓰지 않고 검증/포장 거부 |
| action 정상 완료 2개 | 오류용 cleanup 추가 호출 0회 |
| scope 실패→실제 기존 Round.cleanup 연결 | 가짜 export timeout 뒤 stop→delete→부재 확인, 임시 소유 root 제거, cleanupStatus=complete/evidenceStatus=missing |

마지막 사례의 외부 subprocess/VM은 대역화했다. ownership 거부와 transport/copy/stop/delete 실패는 기존 recovery 테스트도 그대로 통과했다. 개발 중 테스트 binding 오류 로그와 수정 전 실패, marker 유실 회귀의 red 결과도 보존하며 새 고유 테스트 수에 반복 실행을 합산하지 않는다.

## 검증 결과와 보존한 한계

- `pnpm check`: **304/304**, skip 0, 타입 검사·예제 build 통과. production/live 거부를 포함한다.
- Python: **193개 고유 테스트 = 기존174 + 새19**, skip 0. execution-lifecycle 133, 공유 lifecycle/collector 16, single-policy 감사/deadline/package 44다. 초기 132개 통과 뒤 marker 유실 회귀 1개를 추가하고 최종133개 전체를 다시 통과했다.
- 저장 verifier 3개 통과: 11-14 원시 실패, 11-15 원시 실패, 11-17 실제7단위의 whole Spec7개·service seal7개·회수9개. 11-17 index는259파일·분석5/closing3 그대로다. **이번 실제 fixture 0개**, 과거7개 오프라인 재대조다.
- TS 분석/평가 의미 불변이므로 `pnpm experiment`와 Vendure 전체 평가 재실행은 생략했다. 기존 evidence와 변경 금지 코드의 hash를 대조했다.

새 VM/build/download/import/runtime/정책 pair/실제 credential 전달·로그인/provider/model/본 비교/유료 비용은 모두 0이다. R11 unresolved·R12 기존 범위·production/live 거부·fixtureOnly=true·validSubmission=false·trialAuthorized/readyForTrial=false·results=null을 유지한다. 이 변경은 host 실패 연결의 로컬 검증이며 새 runtime 검증이나 R11 해결이 아니다.

## 시간과 인계

최초 명령 UTC는 `2026-11-17T09:53:38Z`(초 단위)다. 첫 명령에서 monotonic을 함께 저장하지 못했고 첫 monotonic 관찰은 28.071초 뒤 `2026-11-17T09:54:06.070793Z`, `226075.220772083`이다. 이를 최초 동시 기록으로 소급 표현하지 않았다. 40분 구현/60분 완료 마감은 더 이른 최초 UTC에서 각각 10:33:38/10:53:38로 고정해 읽기 시간을 제외하지 않았다. 이 동시 기록 누락은 절차상 한계로 남긴다.

읽기·재현·구현·검증·보고의 완료까지 **745.750초**(최초 UTC 기준, 초 정밀도에 따른 1초 미만 보수적 여유 포함)이며 최초 monotonic 관찰 이후는 **717.681초**다. 지시의40/60분 상한 안에 종료했다. 기록은 [cost.json](evidence/2026-11-17-cleanup-dispatch/cost.json), Git 게시 시간은 별도 work 기록이며 실험 재개에 쓰지 않는다. 검증 후 구현 commit과 보고 commit을 push하고 PR #54를 갱신한다. **독립 결과 리뷰 전 병합하지 않는다.**
