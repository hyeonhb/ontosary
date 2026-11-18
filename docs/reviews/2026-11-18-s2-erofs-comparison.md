# S2 추가 VM 대조 결과

**관리자가 `/tmp/codex-daemon-22002` 한 곳을 사전 준비하자 같은 VM에서 원래 EROFS 지점을 통과했다.** 다음 차단은 bubblewrap의 loopback 주소 설정이었다. native는 exit 1로 끝났고 Node payload의 시작 표식과 출력 파일은 없었다. 이번 추가 회차는 새 VM 한 개, native 기준 한 회, 사전 준비 한 회, native 대조 한 회로 종료했다. [기준 trace](../../experiments/domain-model/s2/verification/2026-11-18-erofs-comparison/baseline.trace) · [대조 trace](../../experiments/domain-model/s2/verification/2026-11-18-erofs-comparison/comparison.trace)

| 관측 | 기준 | 사전 준비 후 대조 |
| --- | --- | --- |
| 서비스에서 본 실행 전 상태 | /tmp 읽기 전용, 대상 없음 | /tmp 읽기 전용, 대상은 UID/GID 22002의 0700 디렉터리 |
| helper의 mkdirat | PID 2427, 44행에서 EROFS | PID 2490, 44·67행에서 EEXIST. 각각 다음 행의 openat 성공(fd 3) |
| 도달 단계 | bubblewrap 명령 구성 중 exit 1 | 52·101행에서 bwrap exec. 109행에서 `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted` |
| payload | 시작 표식·출력 파일 없음 | Node exec·시작/완료 표식·출력 파일 없음. source/materials 읽기와 쓰기 동작은 미실행 |

수정된 판독기가 **이번 기준 trace**에서 helper와 EROFS를 연결한 뒤에만 guest 관리자가 mkdir와 fchown을 수행했다. 준비한 디렉터리의 inode는 51이다. 같은 경로에서 EEXIST 뒤 열기가 성공했고 bwrap 실행까지 진행한 것이 원래 차단 통과의 근거다. 다음 오류는 bwrap의 진단 메시지로 관측했다. trace 필터는 netlink 송수신을 수집하지 않아 커널의 정확한 거부 원인까지 판별할 수 없다. [관리자 준비 결과](../../experiments/domain-model/s2/verification/2026-11-18-erofs-comparison/directory.json)

두 실행은 같은 VM에서 별도의 transient service 호출로 이뤄졌다. 실제 서비스 argv, CLI argv·환경·cwd, CLI/Node·tracer·config·payload 해시, UID/GID, capability·NNP와 자원 제한을 대조했다. 관리자가 적용한 변경은 대상 디렉터리 사전 준비 하나였다. 실행 순서에 따라 PID와 CLI 임시 경로는 달랐다. 두 실행 직전 scratch와 worker home은 비어 있었고 source와 CLI 상태의 최상위 항목 목록도 일치했다. 전체 파일시스템을 초기 상태로 되돌리거나 내부 상태 전체를 비교한 실험은 아니다. 두 번 모두 같은 UID로 strace를 사용했다. ptrace의 타이밍 영향은 가능하며 outer/native 출력의 timeout·용량 절단은 없었다. strace의 긴 인자 문자열에는 384문자 표시 제한이 있다. [실행 전 상태 대조](../../experiments/domain-model/s2/verification/2026-11-18-erofs-comparison/verification.json) · [실제 서비스 기준](../../experiments/domain-model/s2/verification/2026-11-18-erofs-comparison/baseline-outer.json) · [실제 서비스 대조](../../experiments/domain-model/s2/verification/2026-11-18-erofs-comparison/comparison-outer.json)

실행 코드는 PR #79의 `b9a672d`이며 고정 CLI SHA-256은 `e7f91e14eab4ba3a0f65047c1757b593409d4ce791ccb6ac65c67c970dfed76f`다. freeze의 소스는 해당 Git 커밋과, 입력은 실행 디렉터리의 파일과 SHA-256이 일치했다. 관측 회귀 4개와 pnpm check의 304개 테스트·타입 검사·예제 빌드가 통과했다. 08:33:47 UTC에 착수해 약 1분 뒤 두 native 실행과 정리를 마쳤다. [freeze](../../experiments/domain-model/s2/verification/2026-11-18-erofs-comparison/freeze.json) · [검사 로그](../../experiments/domain-model/s2/verification/2026-11-18-erofs-comparison/pnpm-check.log)

VM stop/delete/list가 모두 exit 0이었고 소유 프로세스·임시 root·watchdog 부재를 확인했다. PR 전체 분모는 앞선 회차를 포함해 VM 두 개, native 기준 두 회와 대조 한 회다. 두 회차의 원시 증거는 각각 보존한다. 독립 리뷰 대상은 이번 조건에서 디렉터리 사전 준비의 효과와 payload 이전에 관측된 다음 차단이다. [정리 결과](../../experiments/domain-model/s2/verification/2026-11-18-erofs-comparison/cleanup.json) · [앞선 회차](2026-11-18-s2-erofs-observation.md)
