# S2 단일 namespace 정책 시험 개발 지시 — 2026-11-12

## 목적과 승인 범위

동일 후보에서 관찰된 namespace `clone`의 첫 차단점을 **제안된 정책 한 행만 추가해** 시험한다. 새 회차 총 상한은45분이다. 원래 정책과의 대조, 감사 대상 snapshot 범위 보완, 실제 적용 정책 확인, 유한 비모델 실행·정리·보고까지 진행한다. 첫 차단점 통과와 전체 sandbox 성공을 구분한다.

사용자는 이 한 행을 일회성 시험 container에 적용하는 것만 승인했다. 추가 syscall/flags 허용, capability·AppArmor·sysctl·NNP 변경, sandbox 해제·후보 교체, 실제 자격 증명 전달·로그인/갱신·provider/모델 호출·본 비교는 결과 리뷰 뒤 별도로 결정한다. 이번 세션에서 후속 승인을 추정하지 않는다.

## 기준과 선행 리뷰

최초 작업 명령에서 UTC와 host monotonic을 기록한 뒤 AGENTS, PROGRESS, ARCHITECTURE, ROADMAP, CONTRIBUTING을 읽고 원격/브랜치/사용자 변경을 확인한다. 코드·증거 기준은 main `1aefc85`(PR #48)다. 이 지시 병합 후 실제 시작 head와 차이를 기록한다.

- [진단 결과](2026-11-11-s2-namespace-diagnosis.md)와 [정책 후보](2026-11-11-s2-namespace-policy-proposal.md)를 따른다. 독립 리뷰는 proposal-ready에 동의했다. 원시 trace·실제 보안 설정·실행 입력 연결, 증거66파일/16archive/내부665파일, 기존2521파일 불변, pnpm check304·새 감사5테스트를 확인했다. 새 VM 재실행은 하지 않았다.
- 실제 flags는 `0x78020011`(`2013397009`)이며 기존 clone 허용 조건의 namespace mask `0x7e020000`에 걸린다. AppArmor 독립 기여와 후속 syscall/mount 차단은 미확인이다. 정책 후보가 전체 실행을 가능하게 한다고 가정하지 않는다.
- 저장된 이전 audit은 snapshot11개를 검증했고 최종 배포는 close 단계 snapshot까지12개다. 독립 재실행은 이 개수만 달랐고 나머지 결과/해시는 일치했다. 과거 보고/원시 증거는 덮어쓰지 않고 새 회차에서 감사 범위를 명시한다.
- 기존 모델/B/C·평가기·배포 ID·공유 lifecycle와 제품 코어를 유지한다. R11 unresolved·R12 기존 검증 범위·production/live 거부·trialAuthorized/readyForTrial=false·results=null을 유지한다.

## 비용과 중간 마감

읽기·설계·환경 재준비·자료 조사·구현·대기·실패/수정·검증·정리·보고를 같은45분에 포함한다. 최초 시계를 놓쳤으면 누락과 보수적 추정을 기록하고 초기화하지 않는다. 이전 누적은11408.175초이며 이번 실제 소요와 새 누적을 분리한다. Git 게시/PR/merge 시간은 실험 마감 이후 별도다. 신규 유료 비용0, 동일 후보·소유 VM 최대1개다.

| 경과 | 마감과 판단 |
| --- | --- |
| 10분 | 감사 범위 보완과 시험 계획/기대/중단 조건 고정 |
| 20분 | 환경·동일 추적 이미지 준비, 원래 정책 대조 및 후보의 실제 정책 차이 확인. 준비가 안 되면 후보 실행을 시작하지 않고 인계 |
| 30분 | 후보1회 관찰 완료를 목표로 한다. 다음 차단점을 해결하는 추가 탐색은 하지 않음 |
| 35분 | 새 실행·수정·탐색 종료, 검증·정리·보고만 진행 |
| 45분 | 회차 종료. 미완료·잔여 자원·후속 필요를 명시 |

실행 단위는 **원래 정책1개와 후보 정책1개, 최대2개 container**다. 후보를 실제 시작한 뒤 결과가 불편하다는 이유로 다시 실행하지 않는다. 실행 전 인자/경로/직렬화 같은 기계적 오류는 원인이 확인되면1회 수정 가능하되, 보안 정책의 의미를 넓히거나 container 상한을 늘리지 않는다. 정리 시간을 확보할 수 없으면 마감 전에도 탐색을 중단한다.

## 1. 감사 대상 snapshot 범위를 먼저 고정한다

새 감사 결과에는 검사한 snapshot의 ID·manifest/archive hash 목록을 명시하고, 그 목록에서 검증 수를 계산한다. 감사 실행 시점의 디렉터리를 glob한 개수만 최종 결과로 사용하지 않는다. 감사 실행 전 입력 목록을 고정하며 감사/종료 기록이 자기 자신의 결과 hash를 요구하는 순환 구조를 만들지 않는다.

분석 감사 대상과 이후 종료·포장 증거를 구분한다. 종료 후 snapshot이 추가되더라도 원래 감사 결과는 같은 범위에서 동일하게 재현되어야 한다. 최종 evidence index는 **종료·포장 증거까지 포함한 전체 파일/아카이브**를 검증한다. 목록 밖 snapshot을 조용히 무시하지 말고 종료 단계 증거인지 명시하며, 분류되지 않은 파일은 오류로 처리한다.

검증은 실제 이전 자료의11개 감사 범위와 후속 close snapshot을 새 메타데이터로 설명하는 사례, 감사 대상 누락/변조 거부, 종료 snapshot 추가 뒤 감사 결과 안정성, 최종 index의 종료 증거 변조 거부를 포함한다. 과거 audit/index/snapshot은 수정하지 않는다. 이번 도구에서 필요한 작은 구현만 하고 범용 감사 프레임워크로 확대하지 않는다.

## 2. 원래 정책과 후보의 비교 계약을 고정한다

기존 Lima/VZ·게스트/runtime 버전, CLI0.167.0-alpha.3.2·Node22.19.0, binary/resource hash와 CLI 권한 config를 유지한다. 진단 이미지에 strace가 필요하면 기존처럼 도구 layer만 추가하고 image target/config/rootfs chain·버전/라이선스·실행본을 기록한다. **두 단위는 동일 image와 동일 trace 옵션·동일 합성 입력/CLI 명령**을 사용해 정책 차이와 instrumentation 차이를 섞지 않는다. 실행별 source/output/CLI 상태/셸 HOME은 새로 만들고 공유하지 않는다.

원래 정책 단위는 runtime의 기존 기본 정책을 사용한다. 실제 native OCI Spec에서 seccomp 전체와 나머지 보안 설정을 확보해 직전 증거와 대조한다. 예상 밖 차이가 있으면 자동 재고정하지 않는다. 후보는 이 원본 정책을 복제하여 아래 한 행만 추가한다. 원본 규칙·default action/errno·architecture·flags와 다른 모든 항목을 유지한다.

```json
{
  "names": ["clone"],
  "action": "SCMP_ACT_ALLOW",
  "args": [{"index": 0, "op": "SCMP_CMP_EQ", "value": 2013397009}]
}
```

이 규칙은 특정 실행 파일만이 아니라 같은 profile의 모든 자식과 기존 ARM/AARCH64 architecture 범위에 영향을 준다. 범용 namespace 허용이나 ARM 전용 규칙으로 바꾸지 않는다. unshare/setns/mount/pivot_root/clone3와 AppArmor·sysctl·capability·NNP는 그대로다.

고정 runtime이 받는 custom profile 형식을 실제 지원에 맞춰 확인한다. OCI 객체와 입력 JSON 형식이 다르면 변환 규칙을 명시하고 누락/기본값 변경을 거부한다. **입력 파일의 한 행 diff만으로 적용 성공을 판단하지 않는다.** 후보 container를 create한 뒤 start 전에 실제 native Spec을 읽어 원래 정책 대비 의미상 추가 allow 행 하나뿐인지 확인한다. custom profile이 무시되거나 default가 달라지거나, 동일한 정책을 표현할 수 없다면 시작하지 않는다.

UID/GID1000, capability0, NNP1, 기존 AppArmor, RO root/cgroup, network none, CPU2·메모리4GiB·PID256·tmp64MiB를 유지한다. 동적 ID/경로의 허용 차이를 사전에 열거하고 mount의 권한·대상 역할도 대조한다. 후보 파일은 관리자 소유·읽기 전용·해당 container에만 명시적으로 전달하며 기본 runtime 설정/기존 profile/호스트 정책을 바꾸지 않는다. worker에게 정책 파일 수정 권한을 주지 않는다.

## 3. 기준 대조 후 후보를 한 번 관찰한다

1. 각 단위 생성 전 command·input/정책/image/helper hash·trace 범위·기대 결과·시한을 남긴다. 실행 전 snapshot에서 실제 전달 입력으로 연결한다.
2. 원래 정책에서 동일한 첫 namespace clone/flags의 EPERM과 parent 합성 source/material 양성 동작을 확인한다. baseline이 예상과 다르게 성공하거나 trace를 얻을 수 없으면 후보를 실행하지 않고 차이를 보고한다.
3. 실제 정책 한 행 차이 확인 후 후보를 시작한다. 같은 clone의 반환값과 부모/자식 관계를 관찰한다. clone 성공은 양의 PID 등 직접 근거로 판단하고, 오류 메시지가 달라졌다는 사실만으로 통과 판정하지 않는다. CLI 내부 사전 점검과 실제 명령 준비의 bwrap 호출을 분리해 기록한다.
4. 첫 clone 이후 실패하면 그 위치/errno/관련 로그를 기록하고 시험을 끝낸다. 추적 범위는 사전에 clone/clone3/unshare/setns·exec/exit와 후속 mount/pivot_root/권한 설정 등 필요한 호출로 한정하며 두 단위에 같게 적용한다. 포착하지 못한 다음 원인은 미확인으로 남기고 추적/권한을 연속 확대하지 않는다. 현재 권한으로 읽을 수 있는 해당 단위 시간창의 kernel/LSM 로그만 사용하고 로그 부재를 허용 근거로 쓰지 않는다.
5. 예상과 달리 전체 합성 payload가 성공하면 그 사실까지만 보고한다. 파일/가짜 인증/네트워크/상태 반복/CLI timeout의 전체 경계 시험이나 실제 모델 연결로 이어가지 않는다.

합성 payload는 source 읽기·쓰기/자료 읽기만 하는 유한 명령이다. 실제 auth/config/env·키체인·host home/socket은 제공하거나 조사하지 않는다. ptrace는 자신의 직접 자식 추적에만 사용하고 SYS_PTRACE 등을 추가하지 않는다. provider 접속·내부 서버·실제 인증 파서 시험은 이번 범위가 아니다.

payload 최대15초, create부터 단위 외부 상한120초를 지킨다. 후보에서는 새 namespace 자손이 실제로 생길 수 있으므로 부모 CLI exit나 spawnSync timeout만으로 정리를 완료하지 않는다. 기존 검증된 종료/정리 도구를 좁게 재사용하여 시험 소유 cgroup·runtime task/PID·pending 요청·container 부재를 확인한 뒤 진단 결과를 수집한다. 정상/실패 모두 같은 종료 확인을 거친다. 필요한 종료 확인을 시간 내 마련하지 못하면 후보를 시작하지 않는다. 새 범용 lifecycle adapter는 만들지 않으며 이번 준비 단위를 R11 전체 종료 보장의 검증으로 승격하지 않는다.

## 4. 중단·복구와 결과 분류

다음 경우 새 실행을 중단하고 정리·보고로 전환한다.

- 원래 정책 실패가 재현되지 않거나 image/CLI/보안 설정이 기준과 다르다.
- 후보의 실제 정책 차이가 한 행을 초과하거나 권한/architecture/default action의 보존을 확인할 수 없다.
- 같은 clone이 여전히 거부되거나 다른 syscall/LSM 단계에서 실패한다. 이를 해결하기 위한 두 번째 정책 변경은 하지 않는다.
- 관찰/종료 확인에 추가 권한, 새로운 후보/도구 체계 또는 실자격 증명/모델 호출이 필요하다.
- 시한 초과, 소유 자원/종료 상태 불명확, 예기치 않은 파일·네트워크 접근이나 입력 변경이 나타난다.

소유 container/task/cgroup을 확인하고 전용 profile·image·VM·이번에 생성한 cache만 제거한다. 원래 정책/프로젝트 입력이 유지됐는지 대조한다. 정리 실패는 다음 실행을 막고 잔여 자원과 필요한 복구를 보고한다. VM 삭제 자체를 종료·수집 계약의 증명으로 대체하지 않는다. 모든 결과는 fixtureOnly=true/validSubmission=false이고 production/live 경로는 열지 않는다.

기술 관찰과 회차 완료를 별도로 기록한다. 관찰은 `first-clone-passed-next-blocked`, `clone-still-denied`, `synthetic-payload-completed`, `inconclusive` 중 실제 근거에 맞는 상태로 보고한다. 아직 clone 성공을 직접 확인하지 못했으면 첫 상태를 쓰지 않는다. 기준 불일치/정책 오류/종료·정리 실패는 별도 blocked 사유다. 다음 차단점을 찾는 부정 결과도 이번 목적에 맞는 유효한 결과이며 성공 실행을 강제하지 않는다.

## 검증·산출물과 완료 조건

새 결과는 `docs/reviews/2026-11-12-s2-single-policy-test.md`, 증거는 `experiments/domain-model/s2/verification/2026-11-12-single-policy-test/`에 둔다. 실제 날짜가 바뀌면 날짜를 맞춘다. 필요한 도구는 `trial/container/single-policy-test/`에 한정하고 과거 실행본/원시 증거를 보존한다.

보고서에 감사 대상 목록과 종료 증거 범위, 원래/후보 입력 및 실제 OCI 정책 diff, 두 단위 원시 trace·실행 분모·결과, 권한/미확인, 자원 정리,45분 비용/재시도 ledger와 후속 판단을 포함한다. 후보 적용 횟수와 credential/provider/model0회를 분리한다. 같은 후보의 내부 bwrap 두 호출을 독립 시험 두 회로 합산하지 않는다.

`pnpm check`, 문서 링크/변경 범위 검사, 새 감사 범위와 정책 차이 검증 테스트를 실행한다. 정책 검증은 정확히 한 행인 정상 입력 및 추가 allow/flags 확대·default/NNP 변경·custom profile 미적용을 거부하는 사례를 포함한다. 실제 보존 자료로 감사 결과와 전체 index를 재검증한다. 공유 종료 코드를 수정해야 한다면 먼저 이번 범위에서 가능한지 판단하고 영향 회귀를 추가한다. TS/제품/평가기 변경이 없으면 S2 build·Vendure7·pnpm experiment 전체 반복은 필요 없다.

완료 조건은 **승인된 차이만 적용한 대조 시험 또는 근거 있는 중단**, 감사 범위 재현, 검사 결과 공개, 자원 정리와45분 내 인계다. 검사 실패/정리 미완료를 성공 완료로 표시하지 않는다. PROGRESS·ARCHITECTURE·ROADMAP·REVIEW_CONTEXT와 필요한 DECISIONS를 실제 결과로 갱신하고 CONTRIBUTING의 검증·자체 리뷰·저장소 반영 절차를 따른다. 추가 권한 확대·자격 증명 전달·모델 호출과 본 비교는 이 결과를 리뷰한 뒤 결정한다.
