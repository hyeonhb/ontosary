# S2 직접 VM CLI smoke 독립 리뷰

2026-11-18. [PR #70](https://github.com/hyeonhb/ontosary/pull/70)의 `2008351b926aa8c7f7c762f297c0be8b43c2e2a9`와 [개발 보고서](https://github.com/hyeonhb/ontosary/blob/2008351b926aa8c7f7c762f297c0be8b43c2e2a9/docs/reviews/2026-11-17-s2-vm-cli-smoke.md)를 검토했다. **실제 1회 차단 관측과 이번 VM 정리는 인정한다. 다만 진단 예산 소진이 안전 정리 명령을 죽이는 R20(P2)을 확인해 PR 병합은 보완까지 보류한다.** 새 VM·CLI binary 실행·권한 변경·실제 인증/model 호출은 이번 리뷰에서0회다.

## 확인한 결과

직전 회차와 달리 고정 cache→선택 파일→새 guest→전용 worker→실제 native CLI 연결이 관측됐다. 전체 회차1530.223초(25분30초), VM boot29.467초, 실제 sandbox 명령 약0.0059초, VM 생성/삭제1/1·CLI 탐색2·sandbox1·payload 시작0이다. 이번 원인은 시간 부족이 아니다. 최초 준비의 OCI `.` 디렉터리 metadata 처리 보완은 VM 생성/CLI 실행 전이며 같은 최초 시각과 마감을 유지했다. 실제 sandbox 이후 수정·재시도는 없었다.

CLI exit1과 `error building bubblewrap command: Read-only file system (os error 30)` 원문, 빈 stdout·출력 파일 부재로 `blocked-before-payload` 판정을 재현했다. UID/GID22002·capability0·NNP1·CPU2/4GiB/PID256과 별도 network namespace/loopback만/빈 route를 확인했다. VM stop/delete/list exit0와 소유 root/process 부재, watchdog 종료 기록이 일치한다. GC된 service에 대한 stop exit5를 성공으로 오인하지 않았다.

EROFS가 발생한 정확한 path/syscall은 미확인이다. 설정의 `ProtectSystem=strict`와 writable 경로 목록은 향후 대조할 근거지만 특정 경로를 원인으로 확정할 수 없다. 이전 컨테이너 clone/mount EPERM과 동일 원인이라고 단정하지 않으며, 이번 결과로 C안을 채택/기각하거나 추가 쓰기 권한을 자동 허용하지 않는다.

## 독립 검증 범위

- `pnpm check`:304테스트·타입 검사·예제 build 통과. 고정 설치 Python3.13으로 새 Python17개와 저장 verifier 통과.
- 증거98파일/총121,674 bytes의 index, freeze의8개 소스 hash·5개 입력 hash, 실제 argv·권한·분모·종료/정리를 재대조했다.
- `command-*.json`과 대응 stdout/stderr를 결합해 `outer.json`과 완전히 같음을 확인하고, 원래 stdout의 JSON이 `worker.json`과 같은지도 독립 대조했다.
- 최초/실제 준비의 budget이 같고, 보존한 수정 내용으로 `materialize.py`·`run.py`의 최초 freeze hash를 역대조했다. 공개 cache4개도 실제 읽기 SHA-256으로 재확인했다.
- 제품·기존 shared container 구현의 변경은 없다. 원래 개발 checkout의 브랜치·코드를 수정하지 않았다. R19는 재사용 host API 경로만 고정 interpreter로 확인됐고 미사용 Unix socket 결함까지 해결된 것은 아니다.

## R20 P2 진단 예산이 안전 정리 실행을 중단함

`run.py:31–40`의 `Smoke.cmd()`는 safety=True에서도 기존 stdout/stderr 총량으로 capture cap을 계산한다. safety는 시간 제한 선택만 바꾼다. 로그가4MiB−64KiB에 도달하면 cap=0이다. `bounded.py:25–26`은 cap을 넘는 출력이 한 바이트라도 나오면 해당 process group을 SIGKILL한다. 이 경로를 `cleanup()`의 stop/delete/list도 사용하므로 진단이 많아질수록 정리가 중간에 죽을 수 있다.

실제 `Smoke.cleanup()`→`cmd()`→`bounded.run()`을 호출하고 외부 limactl만 유한 Python 가짜 명령으로 바꿔 재현했다. 가짜 VM 상태는 파일로 표현했다. stop/delete는 먼저 진행 문구를 출력하고150ms 뒤 완료를 기록하며, delete 완료 시 상태 파일을 없앤다. list는 남은 상태를 실제로 읽어 응답한다. VM·네트워크·실제 CLI 호출은 없다.

| 조건 | stop/delete 완료 | 가짜 VM 상태 | 판정 |
| --- | --- | --- | --- |
| 진단 예산 여유 | 둘 다 완료 | 없음 | cleanup complete |
| 각1MiB 이하의 기존 로그4개로 예산 소진 | 모두 완료0, exit−9 | 남음 | cleanup unconfirmed |

단순히 현재 검사에 실패하도록 합성 결과를 넣은 사례가 아니라 실제 subprocess가 출력 제한으로 죽는 반례다. 이번 저장 실행은 진단이 약119KiB라 해당 조건에 도달하지 않았고 실제 폐기 근거는 유효하다. 그러나 다음 회차의 실패 정리 계약을 충족하려면 보완해야 한다. 소유권 확인과 유한 시간 제한은 유지하면서 안전 정리 동작과 진단 저장 실패/용량을 분리한다. 조회 출력이 불완전하면 absence를 성공으로 바꾸지 않는다.

## 다음 작업

[R20 무실행 보완 지시](2026-11-18-s2-smoke-cleanup-budget-instructions.md)를 함께 제공한다. 기존 구조 안의 국소 결함 수정이며 새 VM·정책·CLI 시험을 승인하지 않는다. 실제 정리 분기의 출력 소진/진단 오류/timeout 회귀와 과거 관측 보존을 먼저 확인한다. PR #70은 보완 결과 리뷰 전 미병합, PR #67도 별도 보류다.

그 뒤 C안의 다음 판단에는 **EROFS 쓰기 대상 식별**이 필요하다. 저장된 고정 CLI의 출처·설정·입력 및 정확히 대응하는 코드가 있다면 읽기 전용으로 경로 후보를 좁힐 수 있다. 대응하지 않는 최신 소스나 오류 문자열만으로 원인을 확정하지 않는다. 실제 trace나 재실행이 필요하면 목적·횟수·예산을 따로 합의한다. ProtectSystem 완화·쓰기 경로 추가·namespace/LSM 권한 확대를 먼저 하지 않는다. 전체 runner·제출 수집·Vendure/인증/model 통합으로 넘어갈 단계는 아니다.

이번 축소 방식은 약25분 회차에서 최초 차단 관측을 얻었으므로 유지할 가치가 있다. 환경 작업의 성공을 제품 효용으로 확대하지 않으며 R11 unresolved·R12 기존 범위·production/live 거부·trialAuthorized/readyForTrial=false·results=null·H-O/H-F 미검증을 유지한다.
