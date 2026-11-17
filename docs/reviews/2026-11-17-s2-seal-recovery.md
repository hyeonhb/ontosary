# S2 진단 보존·service 봉인·최종 정리 보완 결과

2026-11-17. **승인 범위의 보완·기본 정책 7단위 검증 완료, 독립 리뷰 대기**다. PR #54는 이번에 병합하지 않는다. R13 실제 도구/전체 Spec 재대조, R14 cache 재사용, R15 관리자 metadata/진단 export, R16 실제 종료 봉인, R17 회수 실패와 정리 분리를 아래 범위에서 확인했다. R11 unresolved와 R12 기존 범위를 유지하며 CLI native sandbox·모델 효용·본 비교 완료로 확대하지 않는다.

`fixtureOnly=true`, `validSubmission=false`, `trialAuthorized=false`, `readyForTrial=false`, `results=null`이다. 실제 인증·provider/model 호출·정책 pair·추가 권한·새 의존성은 각각 0회다. 원시 실패와 기존 ADR-048/050·과거 evidence는 보존했다.

## 기준·고정 계획·시간

[승인 지시](2026-11-17-s2-seal-recovery-instructions.md)와 [독립 리뷰](2026-11-17-s2-execution-lifecycle-fix-independent-review.md)를 따랐다. 기준은 PR #54 `ff7ec19ebc7e3e12380fb82cc6a377d5aaf4dd6c`, 최신 main 지시 `cd7d9ad`이며 같은 `codex/s2-execution-lifecycle` 브랜치에서 통합 commit `566adf1`을 만들었다. 사용자 docs worktree는 수정하지 않았다. 최초 tracked inventory 3,230파일과 변경 허용 범위, 소유 자원, 분석/closing 명령, reference 선택을 VM 생성 전에 기록했다.

최초 명령은 UTC `2026-11-17T08:59:47.382826+00:00`, host monotonic `222816.524831416`이다. 로컬 gate/준비/탐색/완료 마감은 UTC 09:59:47 / 10:39:47 / 11:29:47 / 11:59:47이다. 로컬 gate는 09:29:56에 통과했고 그 코드 hash를 준비·실행까지 고정했다. 환경 진입은 한 번 09:30:15, 환경 마감은 09:50:15로 고정했다. 실제 준비는 진입부터 47.920초, prepare 명령은 41.027초였다. 실제 fixture 명령은 83.830초이며 같은 단위 재시도·숨은 smoke·선택적 8번째 단위는 없다.

읽기/구현/개발 회귀/대기/검증/정리/보고를 포함한 회차 측정은 **2312.139초**, 이전 측정 19,084.162570초와 합한 누적은 **21396.302초**다. 최종 serialization은 별도 최대 10초, 이전 누적 serialization 상계는 30초다. Git 게시 시간은 이 실험 비용과 분리 기록하며 실험 재개 예산으로 쓰지 않는다. 유료 비용 0, 새 VM 1, 실제 fixture 7/7, 새 build/download/save 0, image import 1이다.

## R17: 회수와 최종 정리

첫 변경 전 독립 probe를 실제 `Round.cleanup()`에 실행했다. archive copy 실패와 export transport 예외 각각 stop/delete 호출 0, 관리 root 잔존, cleanup 기록 없음이 재현됐다. [수정 전 원문](../../experiments/domain-model/s2/verification/2026-11-17-seal-recovery/host/before-cleanup.log)을 유지한다.

`recovery.py`는 회수, stop/delete/부재 확인, 결과 확정을 분리한다. 회수는 `min(30초, finish 잔여−90초, 현재 단계 잔여, 단위 잔여)`를 사용한다. export·두 copy·기록 오류는 정리를 건너뛰지 않으며 stop 오류 뒤에도 delete를 시도한다. 두 파일의 members/hash를 확인한 단일 envelope만 원자 게시한다. 부분 copy는 삭제하고 기존 archive는 새로운 성공으로 재사용하지 않는다. 삭제/목록/소유 process 확인이 실패하면 관리 root를 보존한다. top-level prepare/fixtures 예외도 분석을 동결하고 등록된 cleanup을 거친다.

실제 최종 회수는 `diagnostic`, cleanup은 `complete`다. stop→delete→목록 확인의 오류는 없었고 VM/소유 process 부재 확인 뒤 관리 root를 제거했다. 최종 cleanup은 1.006초, 종료 시 약 8,803초가 남았으며 상한 초과는 없다. VM 폐기를 단위 종료 증거로 사용하지 않는다. 공개 준비물만 1,706,236,958바이트 유지했고 pending/회차 임시 항목은 0개다. [cleanup 원문](../../experiments/domain-model/s2/verification/2026-11-17-seal-recovery/host/cleanup.json)에 시도 순서·stderr·잔여·두 상태를 보존했다.

로컬 9개 테스트는 copy 두 종류, export exit/예외/timeout, 기록 실패, stop 실패, delete/부재 확인 실패, reserve 부족, 중복 cleanup, 소유 불일치, 정상 게시를 subcase로 포함한다. 실제 VM의 통신 실패를 별도로 주입하지 않았다.

## R15: metadata와 실패 진단

일반 사용자 전용 mode 0700 transport에서 FD 기반 no-follow 정규 파일 읽기와 UID/mode/nlink/크기/hash/스키마/binding을 검사한다. 검증한 바이트를 관리자 임시 파일에 쓰고 mode 0600으로 원자 게시한 뒤 실제 UID/mode/hash를 확인한다. 입력 helper archive도 고정 bootstrap이 FD/hash 검증한 뒤 관리자 소유로 추출한다. 임의 전달 파일을 무조건 chown/mv하지 않는다. 이미지 입력 key와 출력 archive/OCI identity 검증은 유지한다.

실제 `input-members.json`은 source UID 501 → manager UID 0, mode 0600, 3,530바이트, SHA-256 `dcc50c1a630a2336a4d17e4183fe5604bcf6a88e79d61ed534c875f1e9b8b4d1`이다. `image-export.json`은 UID 501 → 0, mode 0600, 562바이트, SHA-256 `ed925c2a6481494766dbdc36a3bc4959a50128c8b76e65e7baf6fcca1b9e14a4`다. 원문은 준비 archive의 `metadata-publication.json`에 있다. 로컬 준비 진입점이 게시 helper를 부르는지, 일반 사용자/관리자 UID 차이, 변조/owner/mode/부분 게시 거부, import→export를 검증했다. host sudo는 쓰지 않았다.

worker 원본은 export 대상이 아니다. collector가 봉인한 result만 manifest·종료·삭제·run binding 전체 검증 후 포함한다. suppressed/failed/quarantined/pending/철회 결과는 읽지 않는다. 관리자 allowlist 파일 하나 거부 시 그 파일과 이유만 제외하며 독립 진단은 보존한다. 부모 소유 범위가 불명확하면 subtree를 더 탐색하지 않는다. `complete`는 포장 완결성이지 task 성공이 아니므로 timeout/wrapper-death outcome은 그대로 실패다.

collector 128파일/16MiB, 회수 1,024파일/16MiB를 유지한다. SafeFiles는 실패한 읽기 시도도 같은 count/byte 예산에서 차감하며 결과 재검증은 이름/크기 inventory와 한 번의 body 검증을 사용한다. 상태/index/거부 목록을 선예약하고 추가 body 수집은 마감 전에 종료한다. 게시 검증 실패는 같은 소비 예산 안의 작은 `error-receipt`만 남긴다. host receipt 8KiB를 별도로 선예약하므로 guest 상한은 16MiB−8KiB다. 정상 pair는 root 소유·읽기 전용이며 worker에게 mount하지 않는다.

준비 1회, 매 단위 7회, 최종 1회로 **9개 회수 archive**를 보존했다. 준비 archive는 관리자 파일 11개, 단위별 정확한 members는 아래 표와 각 내부 `index.json`에 있다. 실제 회수의 거부/누락/partial/error-receipt는 0건이다. 최종 archive는 suppressed 결과가 섞여 `diagnostic`이며 유효한 정상 result와 상태를 개별 구분한다. 로컬 6개 새 진단 테스트와 기존 strict exporter 회귀가 파일 거부·service 원문 보존·hardlink canary 배제·부모 symlink/FIFO/과대/누적 상한·시간·게시 실패를 검사한다.

## R16: reference 수명과 실제 봉인

기존 독립 seal observer에 `BindsTo`로 연결된 manager 소유 active target을 보유자로 선택했다. target의 `After=<worker.service>`는 loaded unit reference를 유지하면서 worker start/restart를 유발하지 않는다. 선택 근거는 [systemd v260 unit 수명 문서](https://github.com/systemd/systemd/blob/v260/man/systemd.unit.xml#L512)다. 이는 이전 회차의 GC를 확정 원인으로 판정한 것이 아니다.

등록→reference 파일/상태 기록→target active/참조 확인→worker start→InvocationID pin→ExecStopPost 전체 종료/삭제/collection→raw service 관찰→durable seal receipt→reference stop/파일 제거→다음 실행 순서다. 원시 stdout/stderr/exit code·UTC/guest monotonic을 파싱 전에 저장한다. Id/LoadState/ActiveState/SubState/InvocationID/InactiveEnterTimestampMonotonic/Result/종료 code를 보존한다. observer 종료는 차단 receipt와 결과 철회를 시도하고, holder 비활성/불명확·invocation 변경·timestamp 0/누락/마감 밖이면 성공과 다음 실행을 막는다.

실제 7개 실행에서 서로 다른 InvocationID, 각각 6개 raw 조회, finalizer≤실제 inactive timestamp≤관찰≤release≤sealed≤guest finish를 확인했다. service 파일과 reference holder가 해제된 뒤에만 다음 단위를 열었다. 현재 시각으로 inactive timestamp를 대체하지 않았고 fake runtime도 명시적 전이 시각을 사용한다. 로컬 8개 새 reference 테스트가 정상/failed/deactivating/unloaded/not-found·0/누락·마감/늦은 관찰·다른 invocation·holder 실패·release 순서를 검사한다. 실제 observer 사망/통신 실패까지 새 VM에서 주입한 것은 아니며 이는 로컬 회귀 범위다.

## 필수 7단위: 기대 결과와 포장 상태

삭제/봉인 시간은 guest 등록부터, 전체는 host wrapper·관찰·회수 포함 초다. 서로 다른 host/guest monotonic을 직접 비교하지 않는다. `result 파일`에는 fixture manifest를 포함한다.

| 단위 | run ID | outcome / 성공 start 수 | collection | 삭제 / 봉인 / 전체 초 | export / 파일 / result 파일 |
| --- | --- | --- | --- | --- | --- |
| normal-1 | `8273e05aa79a` | exit / 1 | collected | 1.582 / 1.992 / 3.093 | complete / 35 / 8 |
| precheck-rejection | `cad253dd9638` | precheck-rejected / 0 | suppressed | 0.736 / 1.163 / 2.247 | diagnostic / 26 / 0 |
| start-failure | `3ead3a54c2fc` | start-failed / 0 | suppressed | 0.890 / 1.349 / 2.224 | diagnostic / 27 / 0 |
| timeout | `a6228a089adc` | timeout / 1 | collected | 15.822 / 16.319 / 24.770 | complete / 38 / 10 |
| wrapper-death | `e7dd63728e33` | wrapper-death / 1 | collected | 4.282 / 4.653 / 24.325 | complete / 38 / 10 |
| supervisor-death | `4dbc4d22afda` | supervisor-death / 1 | suppressed | 1.488 / 1.943 / 24.205 | diagnostic / 28 / 0 |
| normal-2 | `0b8f2e2ec15f` | exit / 1 | collected | 1.469 / 1.891 / 2.845 | complete / 35 / 8 |

모든 단위가 termination/removal/cleanup/serviceInactive/unitFilesRemoved를 확인했고 create/start/exec pending이 없다. 기대 실패 5개는 명시적 recovery 뒤 다음 단위로 진행했다. timeout/wrapper/supervisor 사망은 manager ready 신호 뒤 주입/관찰했으며 20초 late-write timer를 지나서도 late 파일이 없고 마지막 write 시각이 변하지 않았다. supervisor 사망은 결과 suppressed·result 파일 0을 유지했다. 정상 2는 이전 24경로 canary 접근 거부와 새 writable 상태를 확인했다.

## R13/R14·검증·재현

실제 runtime-tools 원문은 준비 archive에, 각 `native.json`·`identity.json`·`baseline-policy-verification.json`은 단위 archive에 보존했다. 과거 기본 Spec에 명시된 기존 migration만 적용하고 실제 전체 Spec 7개를 오프라인 재대조해 모두 일치했다. AppArmor enforce·rro·seccomp·network none·UID/GID 1000·capability 0·NNP 1·RO root/cgroup·CPU 2·memory 4GiB·PID 256·tmp 64MiB를 완화하지 않았다. 고정 runtime 환경과 nerdctl의 정확한 PATH hook 배열을 유지한다.

검증된 공개 준비물 4개만 재사용했다. 이미지 입력 key는 `4bc8ef40b201ccadb928faec44031c95d15e0831716cea76f24d9c41f33e02a4`, archive SHA-256은 `c15c09d5fbdcdbc1641238bc7875dd8c2e732aa2f6919b98eaed8e595afc9d68`이다. target `64e3601e5f0cb3d8e48f0c1e3206ca952e276a5c16b7368b356cbaf3ba18293e`, config `e3ab6ef0491100a63b97719f8dd7e7c12e682485b887eb2a2421c85963508f6d`, chain `3b5f9851906e2c4005a4f4ee0055626d8d719e61e060244b6f96e6a69cf8f7ee`가 새 VM import 후 일치했다. cache miss/corrupt면 재빌드하지 않는 회차다.

- `pnpm check`: 304/304, skip 0, 타입 검사·예제 build 통과. 최초/최종 반복은 새 고유 테스트로 세지 않는다.
- Python: **174개 고유 테스트**, 기존 146 + 새 28(metadata 5, diagnostics 6, reference 8, cleanup 9), skip 0. 실행 lifecycle 114·공유 lifecycle/collector 16·감사/deadline/package 44다. 로컬 gate/최종 반복과 개발 중 반복 로그는 별도이며 합산하지 않는다.
- production/live 거부 1개 재실행은 위 TS 304의 부분집합이다. 별도 example build도 통과했다.
- 과거 11-14/11-15 두 저장 verifier와 새 verifier 모두 통과했다. 이전 실패는 각각 실패로 재현하며 이번 7/7과 혼합하지 않는다.
- 제품 TS 분석/평가 의미·FCA·모델/TASK/B/C·배포 ID는 변경하지 않아 `pnpm experiment`와 Vendure 전체 평가 반복은 생략했다. 기존 입력 불변 검사를 별도로 보존한다.

[증거 디렉터리](../../experiments/domain-model/s2/verification/2026-11-17-seal-recovery/)의 최종 index는 259파일·19 archive·내부 990파일을 검증한다. 분석 snapshot 5개(수정 전 probe, gate, 환경 진입, prepare, fixtures)와 명시적으로 등록한 closing 3개(cleanup, validate, seal)를 분리했다. 개발 중 직접 Python 실행은 `dev-*.log`, 최초 제품 검증은 `initial-pnpm-check.log`로 남고 개별 실행 snapshot을 주장하지 않는다. 그 시간도 최초 clock에 포함했다. 전달 입력 hash·gate hash·실행 snapshot·최종 source와 변경 허용 범위는 `code-connections.json`과 `final-input-verification.json`에 연결한다. 새 보고 문서 이외에 실제 실행 뒤 helper 코드는 변경하지 않았다.

재현 명령(새 VM/모델 실행 없음):

```sh
python3 experiments/domain-model/s2/trial/container/execution-lifecycle/verify_recovery.py --root experiments/domain-model/s2/verification/2026-11-17-seal-recovery
python3 experiments/domain-model/s2/trial/container/execution-lifecycle/verify_fix.py --root experiments/domain-model/s2/verification/2026-11-15-execution-lifecycle-fix
python3 experiments/domain-model/s2/trial/container/execution-lifecycle/verify_saved.py --root experiments/domain-model/s2/verification/2026-11-14-execution-lifecycle
```

## 다음 단계

R13/R14 유지와 R15/R16/R17의 위 검증 결과를 독립 리뷰에 제출한다. PR #54를 commit/push/갱신하고 병합은 기다린다. 이번은 fixture 운영 경로 검증이며 production/live 지원·R11 해소·정책 대조·실제 인증/model·본 비교 승인으로 확대하지 않는다. 다음 실행이나 범위/비용 확대는 결과 리뷰 뒤 결정한다.
