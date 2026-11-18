# EROFS 사전 준비 대조 독립 리뷰

**ADR-062의 대조를 완료로 판정한다.** 첫 회차는 실패 지점을 관측하고 VM을 정리했다. 추가 회차는 새 VM 안에서 기준 실행, 디렉터리 준비, 대조 실행을 모두 마쳤다. 두 회차를 합치면 VM 2개, native 기준 2회, 대조 1회다. 검토한 head는 9305eb7이며 PR #79는 fff4f52로 병합했다. [첫 회차](2026-11-18-s2-erofs-observation.md) · [추가 대조](2026-11-18-s2-erofs-comparison.md)

| 같은 VM의 관측 | 기준 | 사전 준비 후 |
| --- | --- | --- |
| 서비스가 본 상태 | 읽기 전용 /tmp, 대상 없음 | 읽기 전용 /tmp, 대상 디렉터리 UID/GID 22002·0700 |
| helper의 디렉터리 접근 | mkdirat가 EROFS를 반환 | mkdirat가 EEXIST를 반환하고 openat 성공 |
| 마지막으로 확인한 단계 | bwrap 인자 구성 중 종료 | bwrap 실행 후 loopback 주소 설정의 RTM_NEWADDR 권한 오류, native exit 1 |

대조에서 Node payload의 시작 표식과 출력 파일이 모두 없었다. 이 조건에서는 해당 디렉터리의 사전 준비로 원래 차단을 통과했다. 다음 권한 오류는 bwrap의 진단에서 확인했다. 저장된 trace에는 netlink 응답을 거부한 커널 정책을 식별할 근거가 없다. [기준 trace](../../experiments/domain-model/s2/verification/2026-11-18-erofs-comparison/baseline.trace) · [대조 trace](../../experiments/domain-model/s2/verification/2026-11-18-erofs-comparison/comparison.trace)

독립 대조에서 두 outer의 stdout을 파싱한 값은 각각의 worker JSON과 같았고, native stderr는 보존한 trace와 일치했다. 서비스·CLI 인자, CLI 환경·cwd, 바이너리·설정·payload 해시와 자원 제한도 일치했다. 소스 10개는 실행 commit b9a672d로 대조했다. 첫 실행이 남긴 모든 내부 상태를 초기화한 실험은 아니므로 결론은 관측된 실패 지점 통과에 한정한다.

판독기는 같은 PID의 helper 실행 성공과 목표 경로의 EROFS를 연결한 뒤에만 사전 준비를 허용한다. 준비 코드는 기존 항목이 있으면 중단하고 새로 연 디렉터리의 소유자와 모드를 확인한다. 관측 회귀 4개와 기존 smoke 회귀 32개, pnpm check의 테스트 304개·타입 검사·예제 빌드가 통과했다. 저장 기록에서 VM 폐기, 소유 프로세스·임시 root·watchdog 부재를 확인했다. 리뷰는 저장 증거와 로컬 검사로 진행했다.

추가 보완은 요구하지 않는다. S2 본 비교에 필요한 CLI 실행은 payload 시작 전에서 막혀 있다. 다음 범위 논의에서는 기존 격리 조건에서 loopback 설정 실패를 더 조사할 비용과, S2의 도메인 모델 효용 검증까지 남은 거리를 함께 판단한다.
