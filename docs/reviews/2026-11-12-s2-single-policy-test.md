# S2 단일 정책 시험 — 2026-11-12

회차 상태는 **bounded-stop-completed**, 기술 관찰은 **inconclusive**다. 유일한 Lima 준비 명령이 Ubuntu 이미지 다운로드 중450초 상한에 도달했다. VM 부팅·container 생성·원래 정책 대조·후보 적용을 하지 못했다. 감사 범위 보완·오프라인 정책 검증·소유 자원 정리와 인계를 완료했으며, 정책 시험 성공이나 환경의 근본적 불가능성을 뜻하지 않는다.

## 범위와 중단 근거

[지시](2026-11-12-s2-single-policy-test-instructions.md)의 기준은 main `1aefc85`, 실제 시작 head는 `aa4939f`(PR #49)다. 차이는 이번 지시·맥락 문서뿐이다. 별도 작업 브랜치 `codex/s2-single-policy-test`에서 시작했고 사용자 변경은 없었다. 다른 worktree의 main은 수정하지 않는다.

첫 UTC는 `2026-11-12T06:36:08.718831+00:00`, host monotonic은 `161536.760681875`다. 계획·기대·허용 차이·중단 조건과 과거 snapshot 분류는10분 안에 고정했다. 환경 명령은06:40:27부터450.023초 뒤 exit124로 종료됐다. 이전 helper의450초 명령 상한을 그대로 가져온 것은 이번 환경20분 상한보다 짧은 설정이었다. **20분을 모두 소진한 결과가 아니며**, 더 긴 다운로드 대기가 성공했을지 판단할 수 없다. 다운로드 속도나 정책을 바꾸거나 환경을 재생성하는 재시도는 하지 않았다. 지시의 시한 초과 시 중단·정리 조건을 적용했다.

| 실행 분모 | 이번 실제 횟수 |
| --- | ---: |
| 같은 Lima/VZ 후보 등록·시작 시도 | 1 |
| VM 부팅 / container 생성 | 0 / 0 |
| 원래 정책 / 후보 정책 실행 | 0 / 0 |
| 실제 OCI 정책 대조 / 후보 적용 | 0 / 0 |
| CLI / strace / bwrap 실행 | 0 / 0 / 0 |
| credential 전달·로그인·갱신·provider·model·본 비교 | 각각0 |
| 실행 전 기계적 수정 / runtime 재시도 | 0 / 0 |

blocked 사유는 `preboot-image-download-command-timeout`다. clone-still-denied나 first-clone-passed-next-blocked를 사용하지 않는다. 새 원시 syscall trace·실제 OCI diff·게스트 런타임 버전 관측은 없다. 이전 clone EPERM 증거를 이번 실행 결과로 재사용하지 않았다.

## 감사 범위 보완과 정책 검사

[증거 index](../../experiments/domain-model/s2/verification/2026-11-12-single-policy-test/index.json), [범위](../../experiments/domain-model/s2/verification/2026-11-12-single-policy-test/snapshot-scope.json), [감사](../../experiments/domain-model/s2/verification/2026-11-12-single-policy-test/host/audit.json), [도구](../../experiments/domain-model/s2/trial/container/single-policy-test/README.md)를 보존했다.

과거 분석11개와 close1개의 ID·manifest/archive SHA-256 목록을 새 메타데이터에 고정했다. close ID는 `1794405538783847000`이다. 원래11개 분석 결과는 close snapshot 추가 여부와 무관하게 동일하게 재현된다. 과거 audit/index/원시 자료는 변경하지 않았다. 이번 분석은 사전에 고정한6개 snapshot만 검사한다. 이후 검증·종료·포장 snapshot은 최종 scope의 closing 목록으로 구분한다. 전체 index는 closing까지 모든 파일과 archive 내부 파일을 검증하며 미분류 snapshot을 거부한다. index 자체는 자기 hash 대상에서 제외한다.

정책 검증기는 과거 실제 OCI를 fixture로 사용하여 정확한 clone allow 한 행을 추가한 객체만 통과시킨다. 추가 allow·flags 확대·default 변경·NNP 변경·custom profile 미적용·mount 접근 변경을 거부한다. 이는 **동일 identity의 OCI Spec 전체를 엄격 비교하는 오프라인 객체 검증**이며 실제 적용 확인을 대신하지 않는다. 동적 runtime 경로를 정규화하는 검증기는 이번에 배포하지 않는다. 고정 [containerd WithProfile 구현](https://github.com/containerd/containerd/blob/b7a25261e029d68978bbf290df0a62fc819b3c51/contrib/seccomp/seccomp.go)은 OCI LinuxSeccomp 객체를 직접 읽으므로 계획의 변환은 identity다. 원문과 hash를 보존했다.

초기 snapshot에 포함된 원래/후보 실행·종료 helper 초안은 전달하거나 실행하지 않았다. 검증되지 않은 실행기를 배포하는 것으로 오인하지 않도록 최종 도구 트리에서 제외했다. 승인된 정확한 규칙, 동일 이미지/trace/합성 입력, 실제 OCI 비교·persistent cgroup 종료 후 수집이라는 계획은 `host/plan.json`에 남았다. 새 범용 lifecycle adapter나 공유 종료 코드 변경은 없다.

## 정리·검증·비용

Lima 목록은 부팅 전 `Stopped`였다. VM 디렉터리에는 cloud-config/lima-version/lima.yaml/vz-identifier만 있고 basedisk/diffdisk/host-agent 기록은 없었다. 등록을 삭제한 뒤 VM 목록과 소유 프로세스가 비었음을 확인했다. 전용 root도 제거했다. guest/task/cgroup 종료를 검증했다고 주장하지 않는다. 실행 자체가 없었다.

Ubuntu 캐시는 이번 전용 시작 전 없었고, 정확한 URL hash 경로에 유일한 다운로드 임시 파일 `data.tmp.54244.1`이 남았다. 완료 이미지가 아닌784,252,928바이트의 부분 파일이며, SHA-256과 소유 근거를 기록한 뒤 삭제했다. 기대 이미지 digest와 일치했다고 표현하지 않는다. nerdctl cache는 생성되지 않았다. 공유 prune을 하지 않았고 기존 Vendure 소스 cache는 유지했다. [정리 기록](../../experiments/domain-model/s2/verification/2026-11-12-single-policy-test/host/host-cleanup.json)에 잔여 자원 없음이 기록돼 있다.

- `pnpm check`:304테스트·타입 검사·예제 build 통과.
- 새 Python 회귀13개: 실제 과거11+1 자료·분석 누락/변조 거부·close 추가 시 안정성·close 변조의 전체 index 거부·미분류 snapshot 거부 및 정책7사례 통과.
- 시작 시 hash를 기록한 기존 trial/verification1,682파일 불변. 변경 범위 검사로 제품·기존 모델/B/C·평가기·배포 ID·공유 lifecycle·과거 증거가 변경되지 않았음을 확인했다.
- 문서 로컬 링크, 저장 archive 분석 범위와 전체 최종 index 재검증 통과. TS/평가기 변경이 없어 S2 build·Vendure7·pnpm experiment는 반복하지 않았다.

회차 비용: **1193.853초**, 이전 누적11408.175213083973초, 새 누적 **12602.029초**. 읽기·구현·조사·대기·실패·검사·정리·보고를 첫 시계부터 포함한다. 최종 cost/index 직렬화에는 별도 최대5초를 포함한 보수적 상한을 기록하며 그 안에 종료했는지 검사한다. 신규 유료 비용0이며 Git 게시/PR/merge는 종료 후 별도 집계한다. [비용](../../experiments/domain-model/s2/verification/2026-11-12-single-policy-test/host/cost.json), [명령 ledger](../../experiments/domain-model/s2/verification/2026-11-12-single-policy-test/host/budget.json)를 참조한다.

후속은 이 중단 결과 리뷰다. 재개 시 실제20분 환경 상한과 내부 다운로드 명령 상한을 먼저 일치시키고 같은 후보의 새 준비 예산을 정해야 한다. 정확한 한 행 이외의 권한 완화나 실제 자격 증명/model 호출을 추정 승인하지 않는다. R11 unresolved·R12 기존 검증 범위·production/live 거부·fixtureOnly=true/validSubmission=false·trialAuthorized/readyForTrial=false·results=null을 유지한다.
