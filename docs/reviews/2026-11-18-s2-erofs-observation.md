# S2 기준 관측에서 확인한 daemon 디렉터리 EROFS

**기준 VM에서 helper PID 2503이 기존에 없던 `/tmp/codex-daemon-22002`를 0700으로 생성하려다 EROFS를 받았다.** 같은 서비스에서 확인한 /tmp 마운트는 읽기 전용이었다. 관리자 사전 준비와 대조는 0회로, 사전 준비가 원래 오류를 통과시키는지는 미검증이다. VM stop/delete/list가 성공했고 소유 프로세스, 임시 root, watchdog 부재를 확인했다. [원시 trace](../../experiments/domain-model/s2/verification/2026-11-18-erofs-observation/baseline.trace) · [정리 기록](../../experiments/domain-model/s2/verification/2026-11-18-erofs-observation/cleanup.json) · [정리 후 확인](../../experiments/domain-model/s2/verification/2026-11-18-erofs-observation/post-cleanup.json)

| 순서 | 관측 |
| --- | --- |
| 실행 직전 | UID 22002, cwd=/source, canonical /tmp=/tmp. 대상 lstat은 ENOENT여서 소유자·권한이 없다. statvfs는 read-only, mountinfo의 mount 484는 tmpfs의 /tmp를 ro로 노출했다. 같은 줄의 superblock rw는 서비스에서 보이는 mount ro와 양립한다. |
| trace 1행 | 동일 UID tracer PID 2494 아래 CLI PID 2497이 고정 native를 exec했다. CLI 인자는 sandbox -P fixture -C /source 뒤 기존 Node·payload·run ID다. |
| 18, 32–35행 | CLI thread 2498이 자식 2503을 만들었다. 자식의 helper execve 시작과 성공 반환 사이에 부모의 clone 반환 줄이 들어갔다. |
| 44–49행 | helper의 mkdirat(AT_FDCWD, 대상, 0700)이 EROFS로 실패했다. 이어 기존 bubblewrap 오류 문구, helper exit 1, 부모 wait/exit 1이 기록됐다. stdout은 비었고 payload 시작·완료 표식 및 출력 파일은 없었다. |

**자동 판독 오류가 대조를 막았다.** 실행 코드 `8bc1874`의 판독기는 helper exec와 성공 반환을 한 줄에서 찾았다. strace가 두 줄로 나눈 반환을 놓쳐 자동 결과는 baseline-unconfirmed였고, R20 finally가 VM을 폐기했다. 저장 원문에는 경로와 errno가 모두 남았다. 폐기 후 `e151d0c`에서 같은 PID의 미완료 exec와 재개된 성공 반환을 연결하도록 고쳤다. 고친 판독기로 원본 outer/worker를 읽으면 조건을 충족한 PID 2503이 나온다. 원래 결과는 그대로 보존했다. 한 VM에서 사전 준비 전후를 비교하려면 새 기준·대조 회차 결정이 필요하다. [당시 자동 결과](../../experiments/domain-model/s2/verification/2026-11-18-erofs-observation/result.json)

기준은 기존 worker·setup·payload·내부 설정·서비스 속성·CLI 입력을 재사용했다. 표준 smoke의 native-command.json은 서비스 템플릿이며 이 관측의 실제 service argv는 baseline-outer.json에 있다. 서비스 안에서 관측 wrapper가 기존 worker를 호출했고 native 구간만 고정 이미지에서 추출한 strace 아래 15초 마감으로 실행했다. CLI의 HOME/CODEX_HOME은 /home/runner/cli-state, TMPDIR은 /scratch였다. worker의 CapEff/CapBnd=0, NNP=1, 분리 network namespace의 lo만 존재하는 상태를 기존 검사로 확인했다. version/help 두 번, Node version 한 번, native 기준 한 번이다. VM 생성과 폐기는 각 한 번이다. [실제 서비스와 출력](../../experiments/domain-model/s2/verification/2026-11-18-erofs-observation/baseline-outer.json) · [worker 상태와 CLI 인자](../../experiments/domain-model/s2/verification/2026-11-18-erofs-observation/baseline-worker.json)

ptrace는 실행의 부모 PID와 스케줄링을 바꾼다. 관측된 명령 시간은 약 34ms로, 이전 무추적 smoke의 약 6ms와 직접 성능 비교할 수 없다. tracer와 CLI는 같은 서비스와 UID를 사용했고 추가 capability 없이 실행됐다. trace는 지정한 프로세스·파일·mount 연산만 담는다. 출력 스트림의 timeout·절단은 없었고 strace의 384문자 문자열 한도로 긴 profile 인자가 축약됐다. helper 이름, mkdirat 경로·모드·errno는 완전하다. payload 실행 및 사전 준비를 관측하지 못해 그 이후 차단은 판단할 수 없다.

기반 main은 `5d50f15`, 바이너리 SHA-256은 `e7f91e14eab4ba3a0f65047c1757b593409d4ce791ccb6ac65c67c970dfed76f`, strace는 `0e69fa123b3d9732645ce1ac8c89819d100f83cdc9e52a80565d9ad8e7d8cf28`이다. [실행 freeze](../../experiments/domain-model/s2/verification/2026-11-18-erofs-observation/freeze.json)와 [입력 해시](../../experiments/domain-model/s2/verification/2026-11-18-erofs-observation/input-hashes.json)를 당시 코드와 대조했다. 이전 freeze와 증거는 보존했다. 관련 Python 회귀는 기존 32개와 관측 4개가 통과했다. 실제 VM 전에는 관측 회귀 3개였고 이후 split exec 사례를 추가했다. pnpm check의 304개 테스트, 타입 검사, 예제 빌드가 통과했다. [smoke 회귀 로그](../../experiments/domain-model/s2/verification/2026-11-18-erofs-observation/smoke-tests.log) · [저장소 검사](../../experiments/domain-model/s2/verification/2026-11-18-erofs-observation/pnpm-check.log)

기록 시작 08:15 UTC부터 결과 분석·보고까지 약 7분이며 최초 지시 읽기와 원격 게시 시간은 별도다. 독립 리뷰에서 대조 회차의 필요성과 범위를 판단한다. 이번 결과가 확인한 범위는 이 서비스 조건의 시작 실패 원인까지다.
