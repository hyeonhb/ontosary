# S2 기존 clone 한 행 정책 대조 결과

2026-11-17. **원래1/후보1 제한 대조와 소유 자원 정리 완료, 독립 리뷰 대기**다. 원문 대조에서는 **`first-clone-passed-next-blocked`**를 관찰했다. 원래 정책은 bwrap 두 호출의 namespace clone을 EPERM으로 거부했고, 후보는 같은 flags의 clone을 통과한 뒤 자식의 mount가 EPERM으로 막혔다. 합성 payload는 실행되지 않았다.

**동결된 자동 판정은 `inconclusive`로 유지한다.** 첫 clone 줄에 strace의 attach 안내가 끼어들어 반환값이 다음 줄로 나뉘었고, 자동 parser는 이 형식을 처리하지 못했다. 원문 판독과 자동 결과를 혼합하지 않는다. 실행 코드/정책을 고쳐 재시도하거나 기존 결과를 성공으로 덮어쓰지 않았다. 자동 판독의 이 한계는 후속 독립 리뷰 대상으로 남긴다.

R11 unresolved·R12 기존 범위·production/live 거부·fixtureOnly=true·validSubmission=false·trialAuthorized=false·readyForTrial=false·results=null을 유지한다. CLI 전체 경계·인증·모델 효용·본 비교 준비 완료 판정이 아니다.

## 기준·계획과 국소 연결

[승인 지시](2026-11-17-s2-policy-pair-resume-instructions.md)와 [R17 완료 리뷰](2026-11-17-s2-cleanup-dispatch-independent-review.md)를 따랐다. 최초 checkout은 `153f887`, 코드 기준은 PR #54 병합 `7f2f1794b6240086079828338dff5f4c3f505e1a`, 실제 새 브랜치 시작 main은 `e569373`이다. 두 main commit의 차이는 독립 리뷰/재개 지시와 맥락 문서이며 실행 코드는 같다. 새 `codex/s2-policy-pair-resume` 브랜치를 사용했다. **최종 실행 구현 head는 `da4e94787209c977f3e1b7ae9bf8c08b27ea770d`**이며 이후 문서/evidence commit은 실행 코드를 변경하지 않는다.

현재 목적 `s2-clone-rule-pair-2026-11-17`, 정확한 mode 순서 `[baseline,candidate]`, maximumUnits=2·VM1·cacheOnly·build0·고정 RULE·15/80/110/120초·fixture 계약을 모두 검사한다. 기존7단위 evidence index SHA-256 `0a2a9693766d11f90d03822aea2a1b7b2cdff96ab7b30ebf93f20b0851f1f67c`와 실제7개 봉인 재현을 로컬 gate에 연결했다. 과거 계획/목적 부재/변형 후보는 거부하고, 이번 계획으로 fixtures 경로를 호출해7개를 실행하거나 가짜 fixtures-complete를 만드는 것도 거부한다.

`round.py`는 이 제한된 연결과 pair 예외의 기존 failed_dispatch 연결만 바꿨다. `policy_pair.py`는 공통 unit 완료/단계 회수 후 봉인 결과에서 관찰을 읽고, baseline 확인 뒤에만 profile을 만들어 후보를 실행한다. profile은 회수한 원래 OCI seccomp 전체에 고정 RULE 한 행을 추가한 바이트를 root 소유 mode0400으로 게시한다. guest/engine/reference/recovery/collector·정책 비교기·기존 probe·cache/image 구조·제품/FCA/평가 의미는 바꾸지 않았다. 새 `verify_pair.py`와 `test_pair.py`를 추가했다.

## 원래/후보 관찰과 분모

| 항목 | 원래 | 후보 |
| --- | --- | --- |
| run ID | `32b2c3ebb587` | `4eaa03bfb0b5` |
| create / start | 1 / 1 | 1 / 1 |
| probe exit / 실제 sandbox 명령 exit | 0 / 1 | 0 / 1 |
| seccomp syscall rule 수 | 17 | 18 |
| bwrap 사전 검사 clone | PID42 → EPERM | PID41 → 자식42 |
| bwrap 명령 준비 clone | PID43 → EPERM | PID43 → 자식44 |
| 후속 차단 | namespace 생성 전 | 자식42·44의 mount EPERM |
| 합성 payload 완료 | false | false |
| collector / 단위 회수 | collected / complete | collected / complete |
| 등록→삭제 / 등록→봉인 | 1.769 / 2.247초 | 1.613 / 1.972초 |
| host 전체(회수 포함) | 3.068초 | 2.782초 |

probe는 관찰 JSON을 작성한 뒤 exit0으로 끝나는 합성 관찰자다. 이 값과 실제 `codex sandbox` 명령의 exit1·payload 미시작을 구분한다. 실제 container는2개, 각 정책 start1회, 재시도0·추가 trace container0·기존7단위 재실행0이다. 비모델 CLI 호출은 version/sandbox 각1회씩 정책당2회, 총4회다. bwrap/strace version 명령은 각 단위에 같은 인자로 포함된다. parent의 합성 source 읽기/쓰기·materials 읽기는 모두 성공했다. Node22.19.0, CLI0.167.0-alpha.3.2와 두 바이너리 hash를 확인했다.

원래 clone flags는 `0x78020011`(`2013397009`)이며 두 호출 모두 EPERM이다. 후보의 실제 native Spec은 시작 전에 전체 대조했고, 검증된 실행별 소유 ID/경로와 고정 hook 대응을 제외한 유일한 차이는 아래 행이다. `policy-verification.json`의 fullSpecDiff는 빈 목록이며 나머지 defaultAction/architecture/규칙/보안 필드가 일치한다.

```json
{"names":["clone"],"action":"SCMP_ACT_ALLOW","args":[{"index":0,"op":"SCMP_CMP_EQ","value":2013397009}]}
```

후보 사전 검사 원문 `calls[-1].stderr` 64–65행:

```text
[pid    41] clone(child_stack=NULL, flags=CLONE_NEWNS|CLONE_NEWIPC|CLONE_NEWUSER|CLONE_NEWPID|CLONE_NEWNET|SIGCHLD/usr/bin/strace: Process 42 attached
) = 42
```

같은 trace의110행은 자식42의 아래 mount 거부다. 명령 준비는132행에서 clone이44를 반환하고178행에서 자식44가 같은 mount 오류를 낸다.

```text
mount(NULL, "/", NULL, MS_REC|MS_SILENT|MS_SLAVE, NULL) = -1 EPERM (Operation not permitted)
```

55행의 bwrap argv가 `/usr/bin/true`인 사전 검사와123행의 명령 준비 argv를 구분했고, 182행의 wait4는 자식44의 exit1을 확인한다. [trace-review.json](../../experiments/domain-model/s2/verification/2026-11-17-policy-pair/host/trace-review.json)은 원문 hash·1기반 줄 번호·그대로의 발췌·부모/자식 대응을 담는 **별도 수동 원문 검토**다. stdout 재해석이나 runtime 재실행이 아니다.

동결 parser는 정규 단일 줄과 `<unfinished ...>`/`<... clone resumed>` 형식만 처리한다. 첫 사전 검사 clone의 위 attach 안내 삽입 형식은 그 둘에 해당하지 않아 누락됐고, 둘째 clone43→44와 mount 거부만 자동 추출했다. 따라서 `candidate-trace-analysis.json`, `pair-complete.json`, 새 verifier의 status는 모두 **inconclusive**로 남는다. 자동 판독 통과로 원문 검토를 대신하지 않으며 이번 코드의 자동 판정 완결성을 주장하지 않는다.

관찰된 다음 차단은 mount syscall의 EPERM이다. seccomp/AppArmor/그 밖의 kernel 검사 중 정확한 원인 기여를 분리하지 않았다. mount/다른 clone flags·clone3·unshare·setns 허용, capability·NNP·AppArmor·sysctl 수정, unconfined 또는 다른 backend를 시도하지 않았다. 승인한 한 행은 해당 profile을 공유하는 모든 자식에 적용되며 bwrap만 선별 허용하는 규칙이 아니다.

## 준비물·격리·봉인과 정리

검증된 공개 archive4개만 재사용했다. download/build/save0·새 VM import1이며 입력 key는 `4bc8ef40b201ccadb928faec44031c95d15e0831716cea76f24d9c41f33e02a4`다. archive/OCI target/config/chain·고정 도구 원문과 전달 hash를 준비 회수에서 확인했다. 이미지 target은 `sha256:64e3601e5f0cb3d8e48f0c1e3206ca952e276a5c16b7368b356cbaf3ba18293e`다. 준비물 보관량은1,706,236,958바이트로10GiB 이내이며 기존 manifest를 변경하지 않았다.

두 실행은 서로 다른 run/container/service/InvocationID·source/output/HOME/CLI-state/scratch를 사용한다. image·probe·합성 입력·비모델 명령·trace 옵션은 같다. worker network none, AppArmor enforce·seccomp·UID/GID1000·capability0·NNP1·RO root/cgroup·CPU2·memory4GiB·PID256·tmp64MiB를 그대로 유지했다. host home/키체인/실제 auth/config/env/runtime socket은 worker에 제공하지 않았다.

각 단위에서 전체 cgroup 종료, settled pending, task/container 부재, ExecStopPost 이후 동일 invocation의 실제 inactive timestamp, durable seal, reference 해제와 unit 파일 제거를 확인했다. 원래 invocation은 `bec1b52c47354274a35209686b683861`, 후보는 `7370e3de65f14acbac2831e9a50a6697`이며 각각 raw 조회6개가 있다. VM 폐기는 이 단위 종료 증거를 대신하지 않는다.

준비/원래/후보/최종의 회수 archive4개를 보존했다. 단위 archive는 각각31/32파일이며 결과 manifest 포함 result5파일씩이다. 최종 evidenceStatus=complete, cleanupStatus=complete, 오류0이다. stop→delete→실제 VM/소유 process 부재 확인 뒤 `/tmp/ontosary-s2-policy-pair-20261117`을 제거했다. cleanup0.971초, 종료 시 약2,155초 잔여, 안전 정리 상한 초과0이다. 회수30초/최종 정리90초 reserve 계약을 유지했다. 공개 준비물만 의도적으로 보관하고 pending/소유 임시 항목은 없다.

## 로컬 검증·감사·불변 입력

- `pnpm check`304/304·skip0·타입/예제 build, 별도 example build와 production/live 거부1개 재실행 통과. 거부1개는304의 부분집합이다.
- Python **208개 고유 테스트 = 기존193 + 새15**, skip0. execution-lifecycle148·공유 lifecycle/collector16·감사/deadline/package44다. gate와 최종 반복은 합산하지 않는다.
- 새 회귀는 실제 pair main의 순서/무승인 계획/기준 drift/코드 gate/감사 오류/회수 오류/정리1회/공통 unit의 회수 실패 연결, 고정 한 행 profile,7단위 경로 거부, 미실행 verifier, 정상/unfinished trace와 자식 거부를 검사한다. 위 attach 안내 혼합 형식은 미지원 한계다.
- 과거3개 verifier와 새 pair verifier 통과. 과거7단위는 오프라인 재대조했으며 이번2개로7개 분모를 채우지 않았다. 새 verifier는 실제2개 전체 Spec/한 행/봉인/회수/명령 동일성과 자동 trace 결과를 재현하고 미실행/누락을 성공으로 세지 않는다.
- 제품 TS 분석·FCA·평가 의미·모델/TASK/B/C·배포 ID가 불변이므로 pnpm experiment와 Linux Vendure 전체 평가 반복은 생략했다.

[새 verification](../../experiments/domain-model/s2/verification/2026-11-17-policy-pair/)의 index는 134파일·13 archive·내부 903파일을 검증한다. 분석4개(local/환경 진입/prepare/pair), closing3개(cleanup/validate/seal)를 정확한 command/args/phase·ID/hash로 등록했다. 원문 수동 검토는 종료 후 보고 단계의 별도 데이터이며 새 runtime 분석 snapshot으로 주장하지 않는다. 최종 helper·전달·gate 연결은 code-connections.json, 최초 inventory 대비 최종 허용 변경은 final-input-verification.json에 있다. 동결 이후 실제 실행 helper 변경은0이다. 과거 보고서/증거·cache manifest를 덮어쓰지 않았다.

재현 명령은 새 runtime을 시작하지 않는다.

```sh
python3 experiments/domain-model/s2/trial/container/execution-lifecycle/verify_pair.py --root experiments/domain-model/s2/verification/2026-11-17-policy-pair
```

## 비용과 다음 판단

최초 명령에서 UTC `2026-11-17T10:19:15.524410+00:00`과 host monotonic `227586.685566833`을 함께 저장했다. local gate는10:25:53에 통과했고15분 마감10:34:15 이전에 동결했다. 환경 진입10:26:31에 `min(진입+20분, 시작+25분)`인10:44:15를 한 번 고정했다. 환경 준비42.048초, pair 명령6.447초이며 추가 runtime 관찰 없이10:28:19에 VM 정리를 마쳤다. 탐색/완료 마감은10:54:15/11:04:15다.

읽기·구현·회귀·준비·대조·정리·검사·보고의 회차 측정은 **888.660초**, 이전 측정22,142.052284초를 포함한 누적은 **23030.712초**다. 이전 serialization 상계45초와 이번 최대10초를 분리한다. 최종 serialization 실제값은 seal 출력에 기록한다. Git 게시 시간은 별도이며 실험 재개에 쓰지 않는다. 새 VM1·container2·유료0, credential 전달/로그인/갱신/provider/model/본 비교는 각각0이다.

다음은 원문 판독과 자동 parser의 제한을 포함한 **독립 결과 리뷰**다. 필요하면 저장된 trace만으로 혼합 줄 parsing을 보완할 수 있으나, 이번에는 동결 코드를 수정하거나 시험을 재실행하지 않았다. mount 차단을 해결할 추가 권한/정책이나 CLI 전체 경계 검증의 범위·예산은 별도로 정한다. 새 PR로 인계하고 **독립 결과 리뷰 전 병합하지 않는다.**
