# S2 일회성 VM 직접 CLI 실행 타당성 검증 지시

사용자는 **C안: 일회성 VM에서 CLI를 직접 실행하고 CLI 내부 sandbox를 유지하는 구조를 총90분 안에서 검증**하도록 승인했다. 개발 세션은 작은 합성 fixture로 최소 구현·비모델 실행·증거 수집·정리·결과 보고까지 수행한다. 이번 승인은 C안의 타당성 검증이며, 전체 실행기 전환이나 실제 인증·모델 호출·본 비교 승인이 아니다. 결과를 리뷰한 뒤 다음 단계를 정한다.

목적은 변경 전 도메인 모델의 agent 수정 효용을 비교하는 S2에 사용할 실행 경계를 선택하는 것이다. VM이 호스트·다른 실행을 분리하고, CLI 내부 sandbox가 생성된 명령의 파일·인증 상태·네트워크 접근을 제한하는 역할 분담을 검증한다. 범용 sandbox 플랫폼이나 새로운 API 실행기를 만들지 않는다.

## 1. 기준과 시작

최초 명령부터 UTC와 host monotonic을 기록한다. 읽기·설계·구현·환경 준비·대기·실패·검증·정리·보고를 모두 같은90분에 포함한다. 시작 시각을 놓쳤으면 누락과 보수적 추정을 기록하고 예산을 재시작하지 않는다. Git 게시·원격 CI 대기 시간은 별도 기록할 수 있으나 추가 개발·실험에 사용할 수 없다.

지시 작성 기준은 main `fdd7f29`이며, R18 보완은 PR #63으로 병합됐다. AGENTS, PROGRESS, ARCHITECTURE, ROADMAP, CONTRIBUTING을 읽고 원격/브랜치/사용자 변경을 확인한다. 최신 main에서 짧은 작업 브랜치를 만들고 기준 이후의 관련 차이를 기록한다. 다른 checkout과 과거 원시 증거를 변경하지 않는다.

필요한 부분부터 읽는다.

- [R18 독립 리뷰](2026-11-17-s2-trace-context-independent-review.md), [기존 정책 대조](2026-11-17-s2-policy-pair.md).
- [기존 CLI 검증 지시](2026-11-11-s2-cli-feasibility-instructions.md), [CLI 설정과 한계](../../experiments/domain-model/s2/trial/container/cli-feasibility/README.md).
- [공통 실행 수명주기](../../experiments/domain-model/s2/trial/container/execution-lifecycle/README.md), [기존 lifecycle](../../experiments/domain-model/s2/trial/container/lifecycle/README.md).
- [Linux 평가 결과](2026-11-11-s2-linux-evaluation.md), [고정 VM 설정](../../experiments/domain-model/s2/trial/container/lima.yaml).

현재 근거는 컨테이너의 제한된 clone 허용 뒤 mount EPERM, payload 미시작이다. seccomp/AppArmor/기타 kernel 검사의 정확한 기여는 분리되지 않았다. 이번에 컨테이너 정책의 추가 syscall 허용을 재개하지 않는다. 직접 VM 실행에서도 같은 CLI가 동작할지는 검증 대상이다.

## 2. 범위와 책임

```text
호스트의 신뢰된 관리자: 외부 마감, VM 소유권, 최종 폐기, 증거 접수
  └─ 일회성 VM: 호스트 공유 mount/키체인/agent forwarding 없음
       ├─ 신뢰된 guest 감독자: worker 밖에서 시한·전체 종료·수집 관리
       └─ 실행별 비특권 worker service/cgroup
            ├─ CLI 본체: 독립 CODEX_HOME·고정 설정·가짜 인증 표식
            ├─ 양성 대조 helper·유한 로컬 테스트 서버
            └─ 실제 CLI 내부 sandbox → 셸/Node fixture
                 source/scratch/셸 HOME RW, materials RO
                 CLI 상태/제어 상태/다른 실행/네트워크 deny
       전체 종료 확인 → 제한된 합성 결과 수집 → VM 폐기

숨겨진 평가 자료·reference·평가기 제어 상태: agent VM 밖에 유지
기존 Linux 컨테이너 평가기: 이번에는 실행하거나 수정하지 않음
```

실험 내부의 작은 별도 디렉터리(예: `experiments/domain-model/s2/trial/vm-cli-feasibility/`)에 진입점·fixture·검증기·README를 둔다. 기존 관리/collector/hash/deadline 도구를 재사용하되, OCI/container 존재를 전제하는 검사를 무조건 성공 처리하지 않는다. 직접 VM 실행에는 container 부재를 `not-applicable`로 기록하고 실제 service/cgroup/프로세스 근거를 요구한다. 기존 container 진입점과 검증 의미를 바꾸지 않는 얇은 연결을 우선한다.

유지할 것: 과업/TASK, 모델/B/C, 의미 동등성 검토 자료, 평가기, 동결된 배포·ID, 제품 코어/FCA, 과거 결과·봉인·index. 새로운 배포 동결이나 전체 소스 수집기 구현도 제외한다. H-O/H-F는 미검증 상태다.

## 3. 준비물과 권한 계약

### 준비물

- 기존 Lima/VZ와 고정 Ubuntu ARM64 base, Node22.19.0, CLI `0.167.0-alpha.3.2`를 유지한다. 실제 버전·바이너리 hash와 출처를 기존 manifest에 연결한다. 자동 업그레이드·다른 CLI/backend로 교체하지 않는다.
- 검증된 공개 cache를 읽기 전용으로 재사용한다. 기존 OCI archive에서 필요한 공개 바이너리와 라이브러리를 안전하게 추출하는 작은 연결은 허용한다. 이미지 전체를 guest 루트에 덮어쓰거나 컨테이너용 정책을 VM 전역에 적용하지 않는다. 추출 경로·링크·hash를 확인하고 라이선스/출처를 보존한다.
- cache 재다운로드·이미지 build/save·Vendure 재설치/common build는0회다. 준비물 누락·무결성 불일치 또는 대규모 추출/새 패키지 설치가 필요하면 blocked로 보고한다. 기존 공개 cache10GiB 상한과 과거 manifest를 유지한다.
- 고정 VM 자원 설정을 유지하고, worker에는 CPU2·메모리4GiB·TasksMax256을 적용·확인한다. guest OS의 writable 영역과 worker 쓰기 허용 영역을 구분한다. 기존 컨테이너의 RO root 보장이 그대로 남았다고 표현하지 않는다.

### 관리자와 worker 분리

- guest 관리자는 소유 자원 안에서 전용 사용자/디렉터리·service·시한·시험용 네트워크 경계를 준비할 수 있다. worker는 별도의 비특권 사용자이며 sudo/sudoers·관리 그룹·runtime socket·관리 SSH key·user service 제어 경로에 접근할 수 없어야 한다. Lima 기본 사용자를 권한 확인 없이 worker로 재사용하지 않는다.
- worker의 capabilities는0, no-new-privileges는 유지한다. cgroup 이동·새 service 등록·감독자 신호 전달을 통한 시한 탈출을 허용하지 않는다. supervisor/collector는 worker cgroup 밖에 두고 worker가 수정할 수 없게 한다.
- CLI 전용 상태와 셸 HOME/source/scratch는 분리한다. 설정은 관리자 소유 불변 파일, CLI writable 상태는 실행별 임시 경로로 둔다. 최소 환경을 사용하고 host HOME/CODEX_HOME·인증·proxy·전역 지시·skills·MCP·apps·plugins·기존 세션을 상속하지 않는다.
- 기존 fixture 권한 프로필을 최소한으로 이식하고 설정 차이를 기록한다. `danger-full-access`, sandbox 우회/승격, root CLI, 추가 capabilities, AppArmor/seccomp 전역 해제, sysctl 완화, setuid 우회는 제외한다. 직접 VM에서 기존 정책 때문에 시작하지 못하면 관측 근거를 남기고 중단한다.

### 네트워크와 실제 인증

- 시험 worker의 외부 egress는 CLI 시작 전에 관리자 통제로 차단한다. CLI 설정이나 proxy 환경 변수만을 강제 경계로 간주하지 않는다. VM 관리 통신과 fixture 통신을 구분하고, 호스트 LAN/metadata/외부 provider로 probe를 보내지 않는다.
- 양성 대조용 유한 서버는 guest loopback/Unix socket에만 두고 같은 실행의 종료 대상에 포함한다. parent/helper에는 접근 가능하고 내부 sandbox에는 차단되는지 확인한다. IPv4/IPv6/Unix socket은 사용 가능 경로를 명시하며, 없는 경로는 성공 대신 not-applicable과 근거를 남긴다.
- 시험용으로 새로 만든 가짜 표식만 사용한다. 실제 auth 파일·토큰·키체인을 읽거나 복사하지 않는다. 로그인/갱신/provider 요청/모델 호출/본 비교는 각각0회다. 가짜 표식 차단은 실제 인증 전달·갱신 동작의 증명이 아니다.

## 4. 구현과 실행 순서

### 1단계: 작은 계획과 실패 정리를 먼저 연결

준비물 조회→VM 생성→worker 시작→종료 확인→수집→VM 폐기를 한 회차의 소유권과 마감에 연결한다. 기존 finally/감사 실패 처리와 bounded collector를 재사용한다. 준비·검사·수집 오류가 정리를 건너뛰지 않게 한다. 생성 결과가 불명확하면 다음 VM을 만들지 않고 소유 이름/ID로 먼저 확인·정리한다.

실제 실행 전에 읽은 코드와 실행할 command/args·정책·도구 hash·증거 경로를 작게 고정한다. 과거 snapshot 전체를 새 증거에 복제하거나 미분류 파일을 자동 편입하지 않는다. 로컬 가짜 명령 회귀로 시간 제한·실패 정리·수집 거부 경로를 먼저 확인한다.

### 2단계: 첫 VM에서 실제 내부 sandbox와 접근 경계 확인

고정 CLI의 로컬 help/설정 지원과 실제 `sandbox` 명령으로 확인한다. 최신 문서의 인자를 고정 버전에 그대로 가정하지 않는다. 실제 CLI를 거친 payload임을 argv·버전/hash·PID/service 연결로 남긴다. helper 직접 실행은 별도 양성 대조이며 CLI 통과로 세지 않는다.

작은 source/materials와 가짜 인증/제어 표식으로 아래 검증을 수행한다. 허용 접근이 실패하면 뒤따른 거부를 격리 성공으로 인정하지 않는다.

| 검증 | 필요한 관찰 |
| --- | --- |
| 기본 실행 | sandbox payload가 실제 시작·완료하고 source 읽기/쓰기·materials 읽기가 성공 |
| 쓰기 범위 | materials 변경과 허용 경로 밖 쓰기 거부, 원래 hash 유지 |
| 인증/제어 상태 | parent helper는 표식을 읽지만 sandbox의 직접·symlink·부모 `/proc` root/env/fd·상속 FD 경유 읽기는 거부 |
| 관리 권한 | worker의 sudo/관리 socket/다른 service 제어·cgroup 이동 경로 차단 또는 비노출 확인 |
| 네트워크 | parent helper의 로컬 서버 양성 대조 성공, 동일 주소/Unix socket에 대한 sandbox 접근 거부, 외부 egress 차단 설정 확인 |
| 상태 상속 | 이번 실행에 준비하지 않은 환경·세션·전역 설정이 없음. 유효 설정과 선택한 프로필의 연결 기록 |

표식은 부모 문맥에 실제 존재하도록 만든다. 단순히 env/FD가 없는 상황을 차단 성공으로 세지 않는다. 로그에는 내용 대신 대상 ID·존재/접근 여부·반환값을 남긴다. 접근이 예상과 다르면 성공 계약을 완화하지 않고 중단한다.

CLI 비모델 명령으로 확인할 수 없는 실제 turn의 도구 목록·native 파일 도구 경계·설정 변경 가능성은 후속 검증 항목으로 남긴다. 이번 셸 경계 통과를 모든 CLI 도구의 보장으로 확대하지 않는다.

### 3단계: 정상 종료·timeout·wrapper 사망 검증

독립 guest 감독자가 worker service/cgroup을 종료하고, 호스트에는 별도 VM 폐기 마감이 있어야 한다. wrapper의 프로세스 수명이나 stdout EOF를 유일한 감독 수단으로 쓰지 않는다. 실제 fixture 단위는 최대4개로 고정한다.

| 순서 | VM | 단위와 기대 결과 |
| --- | --- | --- |
| 1 | 새 VM1 | 정상 실행과 위 접근 검사 묶음. 전체 종료 확인 뒤 합성 결과 수집 |
| 2 | VM1의 새 실행 상태 | timeout. detached/손자 프로세스의 지연 쓰기를 포함하고 전체 종료 뒤 파일이 더 변하지 않음 |
| 3 | VM1의 새 실행 상태 | host wrapper 실제 SIGKILL. 독립 감독자가 자손을 종료하고 별도 관찰자가 상태·진단을 회수 |
| 4 | VM1 폐기 확인 후 새 VM2 | 첫 정상 fixture를 같은 입력으로 반복. VM1/이전 실행 표식 부재와 새 VM/service/session identity 확인 |

각 단위의 HOME/CODEX_HOME/source/output/scratch는 새로 만든다. VM1 안의 여러 단위는 실패 경로 probe이며 본 비교 실행 간 독립성을 입증한 것으로 세지 않는다. 새 VM2 반복이 별도 검증이다. VM2 준비에 실패하거나 시간이 부족하면 반복은 미검증으로 남긴다.

worker 전체 cgroup 종료, 실제 service InvocationID/비활성 상태, 감독자/서버/자손 범위, 결과 확정 시각을 연결한다. 등록 시의120초 외부 단위 마감과 payload 최대15초를 유지한다. 지연 쓰기는 worker 마감 뒤에 예정하되, 관찰 시간까지120초 안에 들어오도록 미리 고정한다. snapshot 두 번의 불변만으로 종료를 대신하지 않는다.

종료 불명·잔존 프로세스·pending 명령이면 결과를 격리하고 정상 제출 수집을 금지한다. VM 폐기는 최종 안전 정리이며 앞선 종료/수집 성공으로 소급하지 않는다. 수집은 종료가 확인된 합성 source/output의 작은 허용 집합만 대상으로 기존 no-follow·파일/바이트 상한을 적용한다. 진단 수집 실패와 정리 실패는 별도로 보고하고 어느 실패도 VM 폐기를 막지 않는다.

### 4단계: 재사용 가능성과 전환 비용 정리

기존 공개 준비물에서 실제로 재사용한 항목, 새 adapter가 필요한 부분, 기존 검증을 재사용할 수 없는 부분을 분리한다. 전체 Vendure 연결·최종 제출 수집·기존 Linux 평가기로 전달·실제 인증/turn 도구 검증 각각의 남은 작업과 예상 비용을 적는다. 근거 없는 완료 일정을 약속하지 않는다. 이번에는 그 후속 구현으로 확장하지 않는다.

## 5. 시간·횟수 상한과 중단 기준

| 누적 마감 | 목표와 실패 시 조치 |
| --- | --- |
| 15분 | 범위·입력·준비물·최소 구현/정리 경로 확인. 대규모 새 구축이 필요하면 중단 |
| 30분 | VM1 준비와 실제 sandbox payload 시작 확인. 내부 sandbox 시작 실패면 원인 근거를 남기고 중단 |
| 50분 | 허용/거부·가짜 인증·네트워크 검사 완료. 예상 밖 접근이나 누락이면 후속 실제 단위 중단 |
| 65분 | timeout·wrapper 사망 검증 완료. 전체 종료 불명이면 VM 폐기·진단만 수행 |
| 75분 | VM2 정상 반복 및 모든 실제 실행 종료. 이후 새 실험을 시작하지 않음 |
| 90분 | 소유 자원 정리·검사·증거 검증·보고 완료 |

VM은 순차 최대2개, 동시 실행은1개, fixture 단위 최대4개다. VM 생성부터 각 준비 명령에 전체 잔여와 단계 마감의 더 짧은 제한을 전달한다. cache 확인·전송·추출·SSH·lock·수집도 무제한 대기를 하지 않는다. 회수 최대30초, 최종 VM 정리에 최소90초를 별도 확보한다. host/guest monotonic을 직접 비교하지 않고 잔여 예산을 전달한다.

비모델 CLI version/help/설정 탐색은 전체 최대8회, 실제 sandbox fixture 시작은 위4회 이내로 제한하고 명령별 횟수를 기록한다. 단위 안의 유한 검사별 결과도 남긴다. 실행 전 로컬 회귀 수정은 예산 안에서 가능하나 실제 단위 실패 뒤 코드/권한/기대값을 바꿔 같은 단위를 재시도하지 않는다. 다른 구조 A/B로 자동 전환하지 않는다.

추가 권한·정책 완화, 도구/이미지 교체, 새 패키지 구축, 예상 밖 접근, 준비물 불일치, 전체 종료/정리 불명 또는 단계 마감 초과 시 새 실험을 중단한다. 안전 정리가90분을 넘으면 정리만 계속하고 초과·잔여 자원을 명시한다. 보고 누락을 피하려고 검증 실패를 통과로 바꾸거나 검사를 skip하지 않는다.

## 6. 검증·완료 조건·인계

`pnpm check`와 변경된 adapter/공유 경로의 관련 Python 회귀를 실행한다. 새 검증기는 저장된 실제 argv/바이너리·설정 hash·양성 대조·거부 결과·실제 종료/수집·VM 분모를 대조하고 누락을 성공으로 인정하지 않아야 한다. 공유 도구를 수정했으면 영향을 받는 기존 회귀와 저장 verifier를 실행한다. 과거 증거의 변경이 없음을 diff/hash로 확인한다. 제품 분석·평가 의미가 불변이면 `pnpm experiment`와 Linux baseline/reference 전체 반복은 하지 않는다.

상태를 다음처럼 분리한다.

- `feasible-for-next-integration`: 필수4단위와 관련 로컬 검증, 격리 검사, 종료/수집, 두 VM 정리가 모두 근거와 함께 확인됨. 고정 fixture에서 다음 통합을 검토할 수 있다는 뜻이다.
- `blocked`: 권한/준비물/호환성/격리 실패 등 구체적인 차단 근거가 있음.
- `inconclusive`: 시간 부족·누락·모호한 종료 등으로 필요한 판단을 끝내지 못함.

작업 완료는 성공을 강제하지 않는다. **근거 있는 판정, 실제로 확인한 범위와 미검증 목록, 소유 자원의 정리 결과, 후속 전환 비용을 제출하면 이번 타당성 작업을 인계할 수 있다.** 판정과 cleanup/recovery 상태는 별도 필드로 남긴다. 정리 실패를 감추거나 결과를 실행 가능한 제출로 승격하지 않는다.

실제 날짜의 `docs/reviews/YYYY-MM-DD-s2-vm-cli-feasibility.md`와 새 verification 디렉터리에 다음을 기록한다.

1. 시작/최종 head·실행 코드 hash, 과거와의 차이, 실제 준비물/버전·CLI 유효 설정·guest 보안 상태.
2. 준비/각 단위/검증/정리의 시간과 명령 횟수, VM 생성/삭제 및 남은 자원.
3. 각 검사 기대값/관측값·양성 대조·증거 경로, 정상/timeout/wrapper 사망의 service/cgroup/수집 연결.
4. 새 VM 반복과 상태 분리 결과, raw 증거/index/hash를 다시 읽는 로컬 재현 명령.
5. 기존 구조에서 재사용/수정/재검증할 부분과 후속 비용, 새 구조 채택 권고 또는 중단 이유.
6. 실제 credential 전달/로그인/갱신/provider/model/본 비교 각각0회와 실제 CLI 도구 전체·인증 전달·Vendure 통합의 남은 한계.

PROGRESS/ARCHITECTURE/ROADMAP·새 README는 실제 결과로 갱신하고 중요한 판단을 DECISIONS에 추가한다. R11 unresolved·R12 기존 범위·production/live 거부·fixtureOnly=true·validSubmission=false·trialAuthorized=false·readyForTrial=false·results=null을 유지한다. 구현을 검증·커밋하고 PR로 인계하되 **독립 결과 리뷰 전 병합하지 않는다.** 실제 자격 증명 전달·모델 호출·전체 전환·본 비교는 결과 리뷰 뒤 별도 결정한다.
