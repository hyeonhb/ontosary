# 비활성 namespace 정책 후보 — 적용하지 않음

[진단 보고서](2026-11-11-s2-namespace-diagnosis.md)의 관찰된 첫 차단점만 다루는 **최소 후보이며 충분성 미검증**이다. 이 문서는 runtime이 읽는 설정이 아니고 적용 승인이 아니다. Dockerfile·manager·기존 seccomp/AppArmor/sysctl/NNP/capability는 변경하지 않았다.

| 필드 | 후보와 근거 |
| --- | --- |
| 기존 값 | 실제 OCI `linux.seccomp.defaultAction=SCMP_ACT_ERRNO`. clone 허용은 arg0의 namespace mask `0x7e020000`과 AND한 값이0일 때뿐이다. 추적한 flags `0x78020011`은 AND 결과 `0x78020000`이므로 조건에 맞지 않는다. |
| 제안 차이 | **기존 규칙을 유지하고** clone arg0가 정확히 `2013397009`(`0x78020011`)인 경우만 추가 허용하는 후보1개. USER·NS·IPC·PID·NET·SIGCHLD의 관찰된 조합에 한정한다. 아래 표현은 문서 예시이며 실제 profile 파일을 생성하지 않는다. |
| 적용 단위 | 별도 승인 후 일회성 시험 container 전용 profile 복제본에만 가능하다. 기본 profile·VM/host sysctl·기존 AppArmor profile을 바꾸는 안이 아니다. nerdctl은 개별 container의 custom seccomp profile을 지원하지만 이번에는 전달하지 않았다. |
| architecture | 관찰 환경은 Linux arm64. 기존 OCI architecture 목록 `SCMP_ARCH_ARM`, `SCMP_ARCH_AARCH64`를 그대로 전제로 한다. OCI syscall 행 자체에는 architecture 선택자가 없으므로 이 후보는 ARM compat 호출에도 영향을 줄 수 있다. arm64 전용이라고 잘못 표시하지 않는다. 다른 architecture로 일반화하지 않는다. |
| 필요 근거 | trace의 두 bwrap 자식이 같은 flags의 clone에서 EPERM. 실제 default 정책·arm64 arg0 mask·고정 release tag의 raw_clone 경로가 대응한다. untraced 기준도 동일 오류지만 그 실행의 syscall 순서는 직접 추적하지 않았다. |
| 권한 영향 | profile을 공유하는 CLI parent와 모든 도구 자식에게 같은 clone 능력이 생긴다. 실행 파일/호출자만 골라 허용하는 규칙이 아니다. user namespace 내부의 capability와 새 mount/IPC/PID/network namespace를 만들 수 있는 kernel 진입면이 늘어난다. 이 호출만으로 호스트 capability·파일 접근·외부 네트워크가 자동 허용되는 것은 아니지만 기존 경계 유지 역시 입증되지 않는다. |
| 남는 차단 | unshare/setns/mount/pivot_root는 그대로, clone3 ENOSYS도 그대로다. 현재 seccomp에는 mount 허용도 없고 생성된 AppArmor default template에는 deny mount가 있다. 실제 후속 순서·userns/LSM 결과·기타 syscall 요구는 미확인이다. 이 후보로 전체 bwrap가 성공한다고 예상하거나 약속하지 않는다. |
| 최소성 | 이번에 직접 관찰한 첫 namespace clone 조합만 추가하는 제안이다. 전체 sandbox에 필요한 최소 집합이나 안전한 최종 운영 정책을 증명한 것은 아니다. 숫자/flags가 바뀌면 자동으로 넓히지 않는다. |

비활성 문서 표현(기존 syscall 목록에 추가할 후보의 구조):

```json
{
  "names": ["clone"],
  "action": "SCMP_ACT_ALLOW",
  "args": [{"index": 0, "op": "SCMP_CMP_EQ", "value": 2013397009}]
}
```

runtime/manager는 이 Markdown을 읽지 않는다. `unshare` 전체 허용, mask 제거, clone3 허용, `seccomp=unconfined`, SYS_ADMIN/SYS_PTRACE 추가, NNP 해제, AppArmor 비활성, legacy Landlock 전환은 이 후보에 포함하지 않는다. 서로 다른 LSM 결과를 분리하려고 별도 정책을 추가 적용하는 것도 새 승인이 필요하다.

## 승인 후에만 가능한 시험과 복구

1. 새 회차/예산에서 동일 환경·원래 정책의 실패를 먼저 대조한다. 원본 정책·image/CLI hash·입력 hash를 고정하고 시험용 profile의 차이가 위 한 행뿐인지 확인한다. 사용자 namespace와 호스트 namespace identity를 구분한다.
2. 후보를 그 시험 container에만 적용하고 같은 명령을 한 번 관찰한다. 관찰한 clone이 여전히 실패하면 다른 계층/관측 부족으로 기록한다. clone을 넘어서 다음 syscall/LSM에서 실패해도 그 자리에서 멈추며 정책을 연속으로 넓히지 않는다. 원래 정책 음성 대조가 예상과 다르게 성공하면 환경 차이부터 조사한다.
3. 후속 변경의 범위와 위협 모델이 별도로 승인되고 실제 sandbox가 시작되는 경우에만 전체 경계를 검증한다: source RW·자료 RO 양성, control/가짜 인증 직접·symlink·proc/root/fd·상속 FD/환경 거부, parent 내부 서버 양성·명령의 IP/localhost/Unix socket 음성, 외부 egress 차단, 상태가 다른 새 정상2회, CLI 자손 timeout·8초 지연 writer의 유한 대조, 전체 종료 후 수집·성공 cleanup, 영향받는 supervisor/wrapper/공개 철회 회귀. 양성 동작 실패는 거부 통과로 계산하지 않는다.
4. 종료/PID/cgroup/runtime pending 확인이 불명확하거나 가짜 인증/제어/네트워크 경계가 새면 다음 실행을 막는다. 시험 container와 전용 profile·image·VM/새 cache만 정리하고 원본 profile hash를 다시 대조한다. 기본/전역 설정을 수정하지 않는 설계이므로 정상 복구는 시험 자원 제거다. 변경이 예상보다 넓게 적용됐으면 범위·상태·복구 필요를 보고하고 즉시 중단한다.

## 비용과 투자 판단

이번 관찰에서 VM 준비 명령은 약254초, 원래 image build·기준 실행·strace 이미지 준비·추적 두 단위를 포함한 설치 명령은 약60초였다. 각 준비 container의 생성부터 삭제까지는1초 미만이었다. 이 수치는 준비/실행 명령의 관찰값이며 문서 조사·설계·검사·정리까지의 총 회차 비용과 구분한다.

후속 **첫 차단점 정책 시험**은 새 준비·차이 검토·1회 시험·음성 대조·정리를 포함해 **30~45분 예산**을 권고한다(추정). 전체 파일/인증/네트워크/반복/종료 경계와 lifecycle 연결 회귀는 그 시험과 별도로 **최소60~90분 계획 예산**이 필요할 수 있다(미구현 범위를 포함한 추정이며 성공/상한 내 완료 보장 아님). 둘을 연속 승인으로 취급하지 않는다.

현 후보는 실제 flags와 첫 차단점까지 좁혔으므로 한 번의 제한된 정책 시험을 검토할 근거는 있다. 다만 mount/LSM 등 추가 계층 때문에 지금 전체 경계 구현에 바로 투자하는 것은 권하지 않는다. 현 조합을 중단하면 추가 runtime 비용은0이고 S2 실행은 보류된다. 다른 후보·직접 VM·API runner는 별도 설계와 기존 격리/종료/수집 검증을 다시 요구하므로 이번 단일 정책 시험보다 운영 부담이 크다. 새 후보의 신뢰할 만한 시간 추정은 아직 없으며 이번에 조사·구현하지 않았다. 최종 선택은 결과 리뷰에서 한다.
