# S2 일회성 VM 직접 CLI 타당성 — 준비 단계 중단

2026-11-17. [C안 검증 지시](2026-11-17-s2-vm-cli-feasibility-instructions.md)의 결과는 **inconclusive**다. 최초15분 안에 최소 구현과 실패 정리 경로의 로컬 검증을 완료하지 못했다. 단계 마감 초과 시 새 실험을 중단한다는 계약에 따라 **VM 생성0, 실제 CLI sandbox0, 필수4단위 중 관측0**으로 종료한다. C안이 기술적으로 불가능하다는 근거도, 다음 통합에 사용할 수 있다는 근거도 얻지 못했다. 구현 완료나 타당성 통과로 인계하지 않는다.

이번 산출물은 비활성 실행 초안, 공개 준비물 확인, 로컬 회귀, 중단 증거와 전환 비용 검토다. [새 디렉터리](../../experiments/domain-model/s2/trial/vm-cli-feasibility/README.md)의 runtime 진입점은 실행을 거부한다. PR은 독립 결과 리뷰 전에 병합하지 않는다.

## 시작·시간·기준

[최초 명령](../../experiments/domain-model/s2/verification/2026-11-17-vm-cli-feasibility/first-command.json)은 UTC `2026-11-17T12:52:33.929495+00:00`, host monotonic `233538.356099125`, 당시 head `ade291f0891e20bd8a4545cb126dc3b29196761a`와 깨끗한 git 상태를 함께 기록했다. 원격을 확인하고 최신 `origin/main` **5a39504**에서 `codex/s2-vm-cli-feasibility`를 만들었다. 지시 기준 `fdd7f29` 이후 차이는 PR #66의 지시문과 PROGRESS/ARCHITECTURE/ROADMAP/DECISIONS 갱신5파일이며 실행 코드 변경은 없다. 다른 checkout은 수정하지 않았다.

15분 마감은 UTC **13:07:33.929495**, monotonic **234438.356099125**다. 구현 파일들의 문법 검사가 끝난 뒤 시계를 확인한 시각은 **13:10:20 UTC**, 시작 후 **17분46.071초**였다. 최소 구현/정리 경로 검증이 그 마감 전에 완료됐다는 증거가 없고, 실제로 로컬 회귀도 이후에 작성·수행했다. 마감을2분46초 늦게 감지한 운영상 누락을 기록한다. 이를15분 통과로 소급하거나 최초 시각을 재설정하지 않았다. [중단 기록](../../experiments/domain-model/s2/verification/2026-11-17-vm-cli-feasibility/stop.json)에 당시 초안 hash와 미실행 상태를 보존했다.

30/50/65/75분의 VM 준비·접근·실패 종료·반복 단계는 진행하지 않았다. 중단 이후에는 runtime 거부 처리, 로컬 검사, 이미 확인한 공개 cache의 재대조, 증거 검증·보고만 수행했다. [회차 기록](../../experiments/domain-model/s2/verification/2026-11-17-vm-cli-feasibility/round.json)에 검사/보고 종료 UTC·monotonic과90분 상한을 연결한다. Git 게시와 원격 CI는 별도이며 추가 실험에 사용하지 않는다.

실행한 코드 commit/정책/command 고정과 guest 입력 bundle은 완성하지 못했다. 따라서 `executionCodeHashes=null`이며 실행 head·실제 argv를 만들어 넣지 않는다. 시작/기준 head, 중단 당시 초안 hash와 최종 로컬 코드 hash를 분리한다. 최종 게시 head는 PR 본문에 기록하며, [index](../../experiments/domain-model/s2/verification/2026-11-17-vm-cli-feasibility/index.json)의 source hash로 이 보고서가 검증한 코드를 식별한다.

## 실제 확인한 준비물과 재사용

[공개 cache 조회](../../experiments/domain-model/s2/verification/2026-11-17-vm-cli-feasibility/public-cache.json)는 기존 `s2-prepared-v1`의 등록 입력과 실제 SHA-256을 확인했다. cache body 합계는 **1,706,231,724 bytes**, 등록 metadata를 포함한 store 사용량은 **1,706,236,958 bytes**로10GiB 상한 이하다. 다운로드·build·image save·Vendure 재설치는 각각0회다. 기존 cache 내용을 변경하거나 다른 버전을 설치하지 않았다.

| 공개 준비물 | 고정 출처/버전 | 이번 관측 |
| --- | --- | --- |
| Lima | 2.3.0 Darwin ARM64 | archive hash 일치; 새 VM 실행 없음 |
| Ubuntu | 26.04 ARM64, 20261016 | image hash 일치; guest boot 없음 |
| nerdctl full | 2.4.2 Linux ARM64 | 기존 Lima 준비물 hash 일치; worker container 미사용/미실행 |
| 기존 trace OCI archive | Node22.19.0 / Codex0.167.0-alpha.3.2 고정 입력 | archive/manifest/config/chain·11 blobs 확인; binary 실행 없음 |

[archive 관찰](../../experiments/domain-model/s2/verification/2026-11-17-vm-cli-feasibility/archive-inspection.json)은 Node·license/changelog·package metadata·native codex/bwrap/rg 등9개 regular member, 합계404,265,757 bytes를 읽어 hash와 경로를 기록한다. 고정 codex SHA-256은 `e7f91e14eab4ba3a0f65047c1757b593409d4ce791ccb6ac65c67c970dfed76f`, bwrap은 `0f543a7356ab343b4827222f910461d4196778f328b28acd6c126ef18e9557ab`다. 실제 추출/설치0이며 Node/CLI 버전 명령의 관측값은 없다. archive의 provenance를 guest 실행 버전 증명으로 대체하지 않는다. [종료 재대조](../../experiments/domain-model/s2/verification/2026-11-17-vm-cli-feasibility/cache-closure.json)에서도4개 body hash가 같았다.

선택 추출 함수는 작은 합성 OCI로 경로 이탈·ancestor symlink/hardlink·whiteout·중복 교체·누락·누적 바이트 상한을 검사했다. 전체 rootfs 설치, 전역 정책 적용, 공개 cache 재생성은 수행하지 않았다. 실제 guest 라이브러리 호환성, 배포할 라이선스 구성, 선택 바이너리의 직접 실행은 여전히 미검증이다.

## 검증 분모와 미실행 범위

| 필수 단위 | 기대 | 이번 관측 |
| --- | --- | --- |
| VM1 정상 | native payload 시작/완료, 양성 접근·거부 대조, 종료 후 수집 | 미실행 |
| VM1 새 상태 timeout | detached/손자 포함 전체 종료, 예정된 지연 쓰기 없음 | 미실행 |
| VM1 새 상태 wrapper 사망 | 실제 host SIGKILL 뒤 독립 감독/회수 | 미실행 |
| 새 VM2 정상 | VM1 폐기 뒤 동일 입력 반복·새 identity·이전 상태 없음 | 미실행 |

VM 생성/삭제는0/0, CLI version/help/설정 탐색0/8, 실제 sandbox0/4다. 실제 credential 전달·로그인·갱신·provider 요청·model 호출·본 비교도 각각0회다. 호스트 Python 로컬 회귀와 archive 읽기는 이 CLI 분모에 포함하지 않는다.

source/materials/HOME/scratch 허용, 가짜 표식의 직접·symlink·부모 proc·상속 FD/env 접근, 관리자/sudo/cgroup 이동/신호 거부, IPv4/IPv6/Unix 양성/음성 대조는 모두 **미관측**이다. worker UID/capabilities/NNP, CPU2·4GiB·TasksMax256, 외부 egress 차단, 실제 config/hash/argv/PID 연결, InvocationID·전체 cgroup 종료·봉인/회수도 확인하지 않았다. `PrivateNetwork=yes` 등 초안의 설정문은 실제 보안 상태의 근거가 아니다. container 검사는 직접 VM에서 적용 대상이 없으며, 그 대신 필요한 service 근거 역시 이번에는 없다.

[정리 기록](../../experiments/domain-model/s2/verification/2026-11-17-vm-cli-feasibility/closure.json)은 `cleanupStatus=not-created`, `recoveryStatus=not-applicable-no-guest`와 구분된다. 소유권/실행 등록 파일이 없고, 계획 중이던 두 host root와 그 경로를 사용하는 process가 없음을 확인했다. VM을 만들지 않았으므로 삭제를 시험해 성공했다고 기록하지 않는다. 새 VM/SSH key/worker writable state/전송 bundle/추출 바이너리는 남지 않았다. 기존 공개 cache와 작은 작업 기록만 유지한다.

## 초안과 남은 구현 결함

`host.py`·`guest.py`·`worker.py`·`payload.mjs`는 실행되지 않은 설계 초안이다. 별도 비특권 service, worker 밖 감독자, host watchdog, 공유 deadline/artifact/recovery/no-follow collector 연결과 합성 양성 대조를 작성했지만 최소 실행/실패 경로까지 검증하지 못했다. 모든 직접 runtime 진입점과 host 실행 함수는 무조건 거부하며 활성화 인자를 제공하지 않는다. 기존 runtime·공유 도구는 수정하지 않았다.

초안의 거부문만 삭제해서 다음 회차에 사용해서는 안 된다. 인계 검토에서 host watchdog의 마감 예외가 disposal 전에 빠져나갈 수 있는 경로, 실제 argv/hash/PID/cgroup에 대한 결과 검증기 연결 누락, cgroup 실제 제한과 network namespace 비교 누락, 실제 지연 쓰기 예약 시각이 아닌 등록 시각을 기준으로 한 관찰을 확인했다. service reference/InvocationID 유지, pending 명령 정리와 회수 누적30초도 실제 연결 검증이 남았다. 이 결함들을 수정한 runtime 실험을 이번 회차에서 재개하지 않았다. 준비 코드의 양을 줄이고 실패 정리 연결부터 먼저 완료해야 한다.

새 `verify.py`는 보존한 **중단 기록의 일관성과 hash**만 확인한다. 필수 분모4와 관측0, 실제 실행 hash 부재, 고정 중단 시각·승격 금지·자원 미생성·과거 자료 불변을 확인하며 `consistent-inconclusive-record`만 출력한다. 실제 VM 증거가 없으므로 성공 판정은 지원하지 않는다. 향후 실제 검증기는 저장된 argv/유효 설정/도구 hash·양성/음성·service/cgroup·VM 분모를 독립 대조하도록 별도로 완성해야 한다.

## 로컬 검사와 증거 재현

[검사 기록](../../experiments/domain-model/s2/verification/2026-11-17-vm-cli-feasibility/validation.json)과 원시 로그를 보존했다.

- `pnpm check`:304테스트·타입 검사·예제 build 통과, skip0.
- 새 로컬25개: 선택 추출7, 정리/시간 제한/수집/초안 거부9, 중단 증거 부정 회귀9 통과.
- 재사용 경로 관련 기존 Python60개: lifecycle16·deadline/감사44 통과. 전체 Python257개를 이번에 재실행했다고 주장하지 않는다.
- 초기 로컬 import 충돌6건과 최초 verifier의 cache body/store metadata 크기 혼동1건은 로그로 보존했다. 테스트가 대상 파일을 명시적으로 로드하도록 하고, verifier가 body 합계와 store 사용량을 구분하도록 고쳤다. 실제 단위 재시도는 없다.
- [불변 검사](../../experiments/domain-model/s2/verification/2026-11-17-vm-cli-feasibility/immutability.json): 기존 제품/테스트/실험3474파일, 그중 과거 verification2397파일의 hash 변경/누락0. 공유 runtime/parser/collector/평가 의미를 바꾸지 않아 과거 verifier 전체·`pnpm experiment`·Linux baseline/reference 전체 반복은 하지 않았다.

저장 기록은 다음 명령으로 로컬 재대조한다. 검증 통과는 타당성 통과와 다르다.

```sh
python3 -m unittest discover -s experiments/domain-model/s2/trial/vm-cli-feasibility -p 'test_*.py' -v
python3 experiments/domain-model/s2/trial/vm-cli-feasibility/verify.py experiments/domain-model/s2/verification/2026-11-17-vm-cli-feasibility
```

index는 명시적으로 선택한 이번 작은 로그/JSON만 포함한다. 과거 snapshot 전체나 미분류 파일을 복제하지 않았다. source hash와 과거 파일 hash 목록은 현재 checkout 바이트와 비교하며, 자료의 진위나 실제 격리를 hash만으로 증명한다고 보지 않는다.

## 전환 비용과 다음 결정

| 대상 | 재사용할 근거 | 새 작업/비용의 성격 |
| --- | --- | --- |
| 공개 준비물 | 검증된4개 archive·고정 입력/버전·조회/상한 도구 | 작음~중간: 선택 binary/license bundle·guest dependency·직접 실행 호환성 확인. 새 패키지가 필요하면 별도 중단 판단 |
| VM 실행 경계 | 기존 VM 설정·host deadline·artifact hash·bounded reader | 중간 이상: 위 초안 결함 보완과 실제4단위. 기존 OCI Spec/RO root/컨테이너 종료 검증은 전용 불가 |
| 전체 Vendure 연결 | 기존 동결 배포·workspace 자료 계약 | 중간 이상: guest 전송/동일 자료 제공/작업 경로 검증. 이번 합성 fixture로 비용 확정 불가 |
| 최종 제출 수집 | 기존 no-follow·파일/byte 상한 원리 | 큼: 전체 수정 소스·삭제·symlink·oversize·종료 불명 처리의 새 연결과 부정 회귀. 합성 allowlist로 대체 불가 |
| 기존 Linux 평가기 전달 | 평가 의미·baseline/reference·기존 검증 그대로 | 중간: VM 밖 제출 포장/ID/hash 인계와 실제 평가 재검증. 평가기를 agent VM에 옮기지 않음 |
| 실제 인증/turn 도구 | 이번 회차에서 재사용 가능한 실제 관측 없음 | 별도 범위/비용 결정: 인증 전달·갱신·native file/tool 권한·설정 변경 가능성·provider/model 사용 검증 |

이 비용은 남은 작업의 상대적 크기이며 완료 일정 추정이 아니다. C안 채택 권고는 **보류**한다. 먼저 이 중단과 준비 과다를 독립 리뷰하고, 계속할 경우 최소 구현·실패 정리·동결 계획을 실제 시작 전에 검증할 수 있는 별도 범위와 예산을 정한다. 이 회차의 시계를 재시작하거나 다른 A/B 구조·추가 권한·sysctl/AppArmor 완화로 전환하지 않는다.

R11 unresolved·R12 기존 범위·production/live 거부·`fixtureOnly=true`·`validSubmission=false`·`trialAuthorized=false`·`readyForTrial=false`·`results=null`을 유지한다. H-O/H-F는 미검증이다. 실제 credential/model·전체 전환·본 비교는 결과 리뷰 이후 별도 결정이다.
