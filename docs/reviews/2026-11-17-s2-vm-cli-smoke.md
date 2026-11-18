# S2 직접 VM CLI 최소 호환성 시험

2026-11-17. [축소 지시](2026-11-17-s2-vm-cli-smoke-instructions.md)에 따라 새 VM1개에서 고정 CLI sandbox 명령1회를 실행했다. 결과는 **`blocked-before-payload`**다. CLI는 `error building bubblewrap command: Read-only file system (os error 30)`을 출력하고 exit1로 종료했다. payload 시작/완료 표식과 출력 파일은 없었다. 같은 단위를 수정·재시도하거나 추가 trace를 실행하지 않았으며 **VM·소유 process·임시 root 제거를 확인했다.**

이번에는 실제 비특권 문맥의 기동과 최초 차단 원문을 얻었다. 해당 구성에서 읽기/쓰기 payload를 실행하지 못했다는 관측이며, C안 전체의 가능/불가능이나 R11 해결 판정은 아니다. 읽기 전용 오류가 발생한 정확한 경로와 그 하위 원인은 확인하지 않았다.

## 기준·시간과 실행 분모

[최초 명령](../../experiments/domain-model/s2/verification/2026-11-17-vm-cli-smoke/first-command.json)은 UTC `2026-11-17T13:43:25.981337+00:00`, host monotonic `236519.488050375`, 시작 head `ed0250bd534bedfe994814bdf0a6920cb5eb727f`와 깨끗한 Git 상태를 함께 기록했다. 최신 main **e8784ae**에서 `codex/s2-vm-cli-smoke`를 만들었다. 지시 기준 d1f0825 이후 차이는 PR #69의 지시/계획 문서다. PR #67을 병합하지 않았고 그 checkout/과거 원시 증거는 수정하지 않았다.

원래 시작에서45분 실험 마감은 **14:28:25.981337 UTC**,60분 전체 마감은 **14:43:25.981337 UTC**다. 실제 native 명령은 **13:56:27.207705–13:56:27.213587 UTC**, 약**0.0059초**였고, 외부 service 명령은 약**0.320초**로120초 안에 종료했다. guest/host monotonic 값을 직접 비교하지 않았다. VM 부팅은29.467초, 입력 전송2.372초, 실제 회차의 VM stop/delete/list는 각각0.053/0.089/0.052초였다. [14분52초의15분 점검](../../experiments/domain-model/s2/verification/2026-11-17-vm-cli-smoke/checkpoint-15m.json)에서는 이미 실제 관측/폐기가 끝나고 기록·검증만 남았음을 명시했다.15분을 완료 gate로 적용하지 않았다.

[회차/검증 기록](../../experiments/domain-model/s2/verification/2026-11-17-vm-cli-smoke/summary.json)에 최종 보고 시각과 누적 시간을 남긴다. Git 게시/원격 CI 시간은 별도이며 이후 추가 실험은 없다. 실제 VM 생성/삭제는 **1/1**, CLI version/help는 **2/4**, 실제 sandbox는 **1/1**이다. Node version1회는 CLI 탐색 분모와 별도다. 실제 모델 credential 전달·로그인·갱신·provider/model 호출·본 비교는 각각0회다.

## 최소 준비와 R19 처리

호스트는 이미 설치된 **Python3.13.13**의 실제 경로 `/opt/homebrew/Cellar/python@3.13/3.13.13_1/Frameworks/Python.framework/Versions/3.13/bin/python3.13`를 고정했다. 해당 interpreter로 실제 streaming hash와 `tarfile.extractall(filter="data")` 호출, 정상 추출과 경로 이탈 거부를 검사했다. 모든 host 자식 Python 명령도 그 경로를 사용한다. guest는 실제 응답에서 Python3.14.4를 확인했다. Python/새 패키지를 설치하지 않았다.

기존 공개 cache4개를 등록 입력/실제 hash로 조회했다. Lima2.3.0·Ubuntu26.04 ARM64 20261016·기존 nerdctl2.4.2 archive·Node22.19.0/CLI0.167.0-alpha.3.2가 든 고정 OCI archive를 유지했다. download/build/image save/Vendure 재설치/common build는 각각0회다. Lima 로그의 `Downloaded`는 인터넷 URL이 아닌 검증한 **로컬 cache 경로**에서 읽었다는 출력이며 원문을 보존한다. 기존 Lima containerd 준비는 그대로였지만 worker container는 생성/실행하지 않았다.

[provenance](../../experiments/domain-model/s2/verification/2026-11-17-vm-cli-smoke/prepared/provenance.json)에 PR #67에서 가져온 선택 추출 함수와 합성 회귀의 commit/path/hash를 기록했다. 기존 전체 runner·watchdog·socket 초안은 가져오지 않았다. 선택한9개 공개 파일은404,265,757 bytes이며 Node LICENSE/CHANGELOG·package metadata·native codex/bwrap/rg를 포함한다. rootfs 전체 설치는 하지 않았다. guest `ldd`에서 Node의 필요한 기존 OS 라이브러리가 모두 해석됐고, 실제 Node/CLI version이 각각 `v22.19.0`, `codex-cli 0.167.0-alpha.3.2`였다.

첫 **호스트 준비**는 정상 OCI root-directory `.` 항목을 `safe_name`이 거부해 실패했다. 이때 VM 등록/생성/CLI는0회였고 prefix/root는 정리됐다. [초기 기록](../../experiments/domain-model/s2/verification/2026-11-17-vm-cli-smoke/initial-preparation/result.json)을 보존한 채, 시작 전 로컬 보완 허용 범위에서 `.`/`./`의 **디렉터리 metadata만 건너뛰도록** 수정했다. 루트 regular file·절대/상위 경로·link·whiteout·중복·파일/byte 제한은 유지했다. 관련2회귀를 추가했으며 두 준비 시도는 같은 최초 시각/마감을 사용했다. 진단 상한도 두 준비를 합산하도록 연결했다. [정확한 변경](../../experiments/domain-model/s2/verification/2026-11-17-vm-cli-smoke/preparation-correction.patch)과 전후 hash를 보존한다. 실제 sandbox 이후 수정/재시도와 구분한다.

R19 중 실제 재사용한 host API 경로는 위 interpreter/함수 호출로 검증했다. R19의 Unix socket 디렉터리 결함은 이번에 **미사용·미수정**이며 R19 전체 해결이라고 선언하지 않는다. PR #67은 별도 미병합 상태로 두고 처리 여부를 독립 리뷰에 남긴다.

## 실제 worker와 고정 명령

VM 설정은 기존 VZ·4CPU·6GiB·24GiB이며 host 공유 mount 없음, host SSH 공개키 자동 로드/agent forwarding 없음 설정을 유지했다. VM 관리자 통신과 worker 통신을 구분한다. Lima의 관리 vsock/SSH·시간 동기화가 남아 있는 것을 worker의 외부 통신 허용으로 해석하지 않는다.

[guest 준비 응답](../../experiments/domain-model/s2/verification/2026-11-17-vm-cli-smoke/prepared/guest-preparation.json)과 [worker 원시 응답](../../experiments/domain-model/s2/verification/2026-11-17-vm-cli-smoke/prepared/worker.json)의 실제 관측은 다음과 같다.

| 항목 | 실제 관측 |
| --- | --- |
| 사용자/그룹 | 전용 s2smoke, UID/GID22002, 보조 그룹22002만 |
| privilege | CapEff/CapBnd 모두0, NoNewPrivs=1 |
| 자원 | cpu.max=`200000 100000`, memory.max=`4294967296`, pids.max=`256` |
| network namespace | worker `net:[4026532302]`, 관리자 `net:[4026531833]`로 다름 |
| worker interface/route | `lo`만 존재, IPv4/IPv6 route 모두 빈 배열 |
| 상속 환경 | worker 시작 환경 키 HOME/LANG/PATH만; CLI에는 고정 HOME/CODEX_HOME/TMPDIR/PATH/LANG 전달 |
| native PID/service | CLI PID2560, `/system.slice/ontosary-smoke.service`와 실제 proc cgroup 연결 |

OS `PrivateNetwork=yes` 적용을 위 namespace/interface/route로 확인한 **뒤에만** CLI 탐색/실행으로 진행했다. provider/LAN/metadata에 network probe를 보내지 않았다. sudo/관리 그룹을 추가하지 않았고 runtime/관리 socket·관리 SSH 경로는 service의 InaccessiblePaths에, cgroup은 ProtectControlGroups에 포함했다. 이 경로들에 대한 전체 공격/부정 대조는 이번 범위가 아니며 모두 검증됐다고 주장하지 않는다.

source/scratch/셸 HOME/CLI 상태는 새 전용 경로다. config는 root가0444로 배치하고 ReadOnlyPaths로 고정했으며, CLI 상태 디렉터리는 worker writable이다. ProtectSystem=strict와 명시한 writable 경로를 사용했다. 기존 fixture profile에서 공개 실행 파일의 설치 경로 `/opt/s2-smoke/public`에 read 한 행만 추가했다. [config](../../experiments/domain-model/s2/verification/2026-11-17-vm-cli-smoke/prepared/config.toml)와 원본 정책 hash/변경 이유를 보존한다. 실제 credential·기존 세션·전역 지시·skills/MCP/apps/plugins를 복사하지 않았다.

[동결 인자](../../experiments/domain-model/s2/verification/2026-11-17-vm-cli-smoke/prepared/native-command.json)는 실제 관측 argv와 일치한다. native codex를 `sandbox -P fixture -C /source -- <고정 Node 경로> /source/payload.mjs vm-smoke-20261117-134325`로 호출했다. source의 `smoke source\n` 읽기, run ID를 포함한 output 쓰기/재읽기, materials의 `smoke material\n` 읽기가 고정 기대값이다. 프로그램·입력·config·binary hash를 실행 전에 기록했고 native PID/exit/stdout/stderr를 별도로 남겼다. runtime 파일은 최종 freeze 이후 바뀌지 않았다. base head와 실행 파일 hash, 최종 게시 head는 서로 구분한다.

## 관측과 정리의 의미

CLI version/help 성공은 payload 성공이 아니다. 실제 native stdout은 빈 문자열, stderr는 위 EROFS 한 줄, exit1, timeout/truncation=false다. `outputContent=null`이며 시작/완료 이벤트 모두 없었다. 따라서 source/materials 읽기·출력 쓰기 자체는 **미관측**이다. helper를 직접 실행해 native sandbox 성공으로 세거나, 실제 결과에 맞춰 기대값을 바꾸지 않았다.

원문은 **bubblewrap 명령 구성 중 읽기 전용 파일시스템 오류**만 식별한다. 정확한 path·syscall·AppArmor/seccomp 기여, namespace/mount 검사 도달 여부는 알 수 없다. 지난 container의 clone/mount EPERM과 동일 원인이라고 단정하지 않는다. 추가 trace·쓰기 경로 확대·ProtectSystem 완화·sysctl/LSM 변경·다른 CLI로 전환하지 않았다.

외부 watchdog은 별도 host process/session으로 VM 생성 전에 등록했다. `remaining() <= 0` 또는 부모 소멸이면 소유 stop/delete/부재 확인으로 직접 연결하며, 만료된 `limit()` 예외가 disposal 전에 발생하는 옛 초안을 사용하지 않았다. 이 분기는 가짜 외부 명령으로 검사했고, 이번 실제 watchdog 사망/timeout 주입은 하지 않았다.

실제 명령 직후 추가 service stop은 `Unit ... not loaded`/exit5였다. `--wait --collect` 뒤의 이 응답을 service stop 성공으로 세지 않는다. 이후 **VM stop/delete/list는 모두 exit0**, 목록/소유 process와 host root 부재를 확인했다. watchdog PID14600도 사라졌음을 [별도 확인](../../experiments/domain-model/s2/verification/2026-11-17-vm-cli-smoke/post-cleanup.json)했다. 최초 VM 미생성 준비에서의 stop exit1도 별도 보존하며, 실제 VM 회차 cleanup errors는 빈 배열이다. `cleanupStatus=complete`는 이번 호환성 시험의 VM 안전 폐기이며, R11의 모든 writer 종료→불변 제출 수집 보장을 증명하지 않는다.

## 검사·증거와 다음 단계

`pnpm check`304테스트·타입 검사·예제 build와 새 Python17개 회귀가 통과했다. 로컬 검사는 실제 host interpreter의 hash/filtered extraction, 합성 OCI9개 사례, 준비 외부 명령 오류/만료 watchdog/진단 실패/stop 실패 뒤 실제 cleanup 명령 연결, output/timeout 상한, payload 결과의 누락·절단 거부를 포함한다. 원시 증거 변경·미등록 파일·결과 누락·절단을 넣은 별도 오프라인 부정4건도 거부했다.

공유 구현/제품/평가 의미를 수정하지 않았다. 기존 source와 과거 verification의 Git diff는 없으며 새 수천 파일 snapshot을 만들지 않았다. `pnpm experiment`·Linux 전체 평가·과거 verifier 전체 반복은 하지 않았다. 이번 증거는 작은 명시적 host JSON/원시 stdout/stderr 집합으로4MiB 상한 이하다. VM 디렉터리/임의 guest 파일 export나 제출 수집은 없다. 재현 명령은 [README](../../experiments/domain-model/s2/trial/vm-cli-smoke/README.md)에 있으며, 새 offline verifier는 raw argv/hash/버전/권한·분모·exit/출력·VM 폐기 연결을 다시 대조한다.

다음 판단은 **이번 최초 차단의 독립 리뷰**다. 공개 cache→선택 파일→새 guest→전용 사용자→native CLI까지의 연결은 재사용할 관측을 얻었다. 다음에 계속한다면 EROFS의 정확한 쓰기 대상과 그 경로가 필요한 이유를 좁히는 별도 진단이 먼저다. 권한을 먼저 넓히거나 전체 runner를 완성하는 순서로 확대하지 않는다. 이 진단의 범위·예산은 별도 결정하며 완료 일정을 약속하지 않는다. 종료/수집 통합·전체 접근/인증 경계·반복 실행·Vendure 연결·실제 turn 도구·기존 Linux 평가기 인계는 여전히 별도 작업이다.

PR #67은 자동 병합/폐기하지 않고, 이번 작업은 main 기준의 새 PR로 인계한다. **독립 결과 리뷰 전 병합하지 않는다.** R11 unresolved·R12 기존 범위·production/live 거부·fixtureOnly=true·validSubmission=false·trialAuthorized=false·readyForTrial=false·results=null·H-O/H-F 미검증을 유지한다.
