# S2 EROFS 정적 진단 — 고정 daemon 디렉터리 생성이 선두 후보

2026-11-18. [진단 지시](2026-11-18-s2-erofs-diagnosis-instructions.md)에 따른 읽기 전용 조사다. **가장 강한 후보는 Linux sandbox helper가 bubblewrap 인자를 만들면서 `canonicalize("/tmp")/codex-daemon-22002`를0700으로 생성하는 연산이다.** 일반적인 Linux 경로는 `/tmp/codex-daemon-22002`다. 이 코드는 `TMPDIR=/scratch`나 `daemon_auto_start=false`에 따라 생략되지 않는다. 당시 외부 서비스의 ProtectSystem=strict와 `/tmp`를 제외한 쓰기 허용 목록에 충돌할 가능성이 높다.

상태는 **정적 선두 후보·실패 지점 미확정**이다. 당시 `/tmp`의 실제 canonical 경로·mount 상태·디렉터리 존재 여부와 실패 syscall은 수집되지 않았다. 설정과 소스만으로 실제 실패 연산을 확정하지 않으며 EROFS 해결로 기록하지 않는다. 다음 권고는 **동일 조건을 유지한 제한적 동적 관측 한 회로 경로·연산·errno를 확인하는 것**이다. 이번에는 해당 시험을 구현하거나 실행하지 않았다.

## 1. 바이너리와 대응 소스

버전 문자열만 비교하지 않고 다음 연결을 확인했다. [분석 결과](../../experiments/domain-model/s2/verification/2026-11-18-erofs-diagnosis/analysis.json), [패키지 비교](../../experiments/domain-model/s2/verification/2026-11-18-erofs-diagnosis/package-comparison.json), [릴리스 asset 비교](../../experiments/domain-model/s2/verification/2026-11-18-erofs-diagnosis/release-package-comparison.json)에 식별자를 남겼다.

| 연결 | 확인한 근거 |
| --- | --- |
| 당시 실행 → OCI 선택 파일 | worker의 native SHA-256 `e7f91e14eab4ba3a0f65047c1757b593409d4ce791ccb6ac65c67c970dfed76f`, materialized.json의278,729,112bytes 파일과 일치 |
| 선택 파일 → 공개 npm 패키지 | `@openai/codex@0.167.0-alpha.3.2-linux-arm64`의 native·bwrap·package.json·codex-package.json 네 파일 hash/size가 당시 기록과 모두 일치 |
| npm archive → registry/release | 분석용으로165,822,267bytes archive를 읽었고 npm SHA-512 integrity 및 GitHub release asset SHA-256 `5cc358efffcfec91f2ca496d6805f41ec96ee1cf0795e4d16274329e3ed48fde`와 일치 |
| 패키지 → 선언된 소스 | npm provenance의 subject digest가 위 archive와 일치하고 resolvedDependencies가 `c40729ea5cf8e947481b130c59807273eda2f8e9`를 지시 |
| 태그 → 소스 | annotated tag `rust-v0.167.0-alpha.3.2`의 tag object `b4b58be9…`도 같은 commit을 지시 |

출처는 [npm 버전 metadata](https://registry.npmjs.org/@openai%2Fcodex/0.167.0-alpha.3.2-linux-arm64), [npm provenance](https://registry.npmjs.org/-/npm/v1/attestations/@openai%2fcodex@0.167.0-alpha.3.2-linux-arm64), [공식 릴리스](https://github.com/openai/codex/releases/tag/rust-v0.167.0-alpha.3.2)다. package.json에는 gitHead가 없고 codex-package.json은 layout/version/target만 제공한다. provenance와 태그가 이 빈 부분을 보완한다. 해당 commit의 [release workflow](https://github.com/openai/codex/blob/c40729ea5cf8e947481b130c59807273eda2f8e9/.github/workflows/rust-release.yml#L230)는 Cargo build와 release archive→npm 게시 경로를 포함한다.

이는 **공개 배포자가 선언한 소스 대응을 동일 패키지 bytes로 연결한 근거**다. Sigstore 서명 체인의 별도 암호학적 검증이나 재현 빌드는 하지 않았으며, 빌드된 기계어 전체가 해당 소스와 같다는 독립 증명으로 확대하지 않는다. 최신 main 소스를 옛 바이너리에 대신 적용하지 않았다. 고정 commit의 관련12파일286,638bytes만 읽었고 전체 소스는 수집하지 않았다. [source-index](../../experiments/domain-model/s2/verification/2026-11-18-erofs-diagnosis/source-index.json)는 Git blob·SHA-256·원본 URL을, [source-excerpts](../../experiments/domain-model/s2/verification/2026-11-18-erofs-diagnosis/source-excerpts.json)는 필요한 행만 원문으로 보존한다. Apache-2.0 LICENSE/NOTICE를 함께 보관했다. archive는 작업용 디렉터리에만 있으며 설치·실행하지 않았다.

## 2. 실제 명령과 환경의 단계 구분

[worker 원문](../../experiments/domain-model/s2/verification/2026-11-17-vm-cli-smoke/prepared/worker.json)의 CLI PID2560은13:56:27.207705–13:56:27.213587 UTC에 exit1로 종료했다. stdout은 비었고 stderr는 `error building bubblewrap command: Read-only file system (os error 30)` 한 줄이며 timeout/truncation은 false다. payload 표식과 output.txt는 없었다. argv는 다음과 같다.

```text
/opt/s2-smoke/public/usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-arm64/vendor/aarch64-unknown-linux-musl/bin/codex
sandbox -P fixture -C /source --
/opt/s2-smoke/public/usr/local/bin/node /source/payload.mjs vm-smoke-20261117-134325
```

| 단계 | 환경과 cwd | 근거 수준 |
| --- | --- | --- |
| Python worker | HOME=/home/worker, LANG=C.UTF-8, PATH=/usr/sbin:/usr/bin:/sbin:/bin; cwd=/source | outer.json의 실제 env-i/service 인자, worker의 환경 키 관측 |
| native CLI 초기화 | HOME와 CODEX_HOME=/home/runner/cli-state, TMPDIR=/scratch, PATH=/usr/local/bin:/usr/bin:/bin, LANG=C.UTF-8; cwd=/source | 당시 freeze와 일치하는 worker.py의 명시적 env/cwd, 실제 argv; CLI proc environ/cwd를 직접 덤프한 것은 아님 |
| Linux helper의 bubblewrap 준비 | HOME=/home/worker, TMPDIR=/scratch, PATH=/usr/local/bin:/usr/bin:/bin, CODEX_SANDBOX_NETWORK_DISABLED=1; CODEX_HOME/LANG 미상속, cwd=/source | 고정 소스와 config에서 재구성한 값; helper 환경의 직접 관측은 아님 |
| Node payload | 위 helper 환경을 거쳐 실행하도록 구성됐지만 실제 미시작 | payload 환경·파일 접근을 실행 관측으로 세지 않음 |

`debug_sandbox.rs`는 config를 읽은 뒤 [create_env](https://github.com/openai/codex/blob/c40729ea5cf8e947481b130c59807273eda2f8e9/codex-rs/cli/src/debug_sandbox.rs#L243)를 호출한다. [shell_environment.rs](https://github.com/openai/codex/blob/c40729ea5cf8e947481b130c59807273eda2f8e9/codex-rs/protocol/src/shell_environment.rs#L114)는 inherit=none으로 시작해 set의 세 값을 적용한다. 이어 [spawn_debug_sandbox_child](https://github.com/openai/codex/blob/c40729ea5cf8e947481b130c59807273eda2f8e9/codex-rs/cli/src/debug_sandbox.rs#L612)가 env_clear/envs와 network-disabled 값을 적용하고 arg0=`codex-linux-sandbox`로 같은 실행 파일을 시작한다. 따라서 최초 CLI의 CODEX_HOME을 helper의 HOME과 같다고 볼 수 없다.

당시 [outer.json](../../experiments/domain-model/s2/verification/2026-11-17-vm-cli-smoke/prepared/outer.json)에 ProtectSystem=strict, ReadWritePaths=`/source /scratch /home/worker /home/runner/cli-state`, ReadOnlyPaths=`/home/runner/cli-state/config.toml`, User/Group=s2smoke, NNP·빈 capability·PrivateNetwork 등이 실제 호출 인자로 남아 있다. PrivateTmp나 `/tmp` 쓰기 예외는 지정되지 않았다. [systemd 문서](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#ProtectSystem=)의 strict 의미상 `/tmp`도 읽기 전용 대상이다. 이 현재 문서의 설정 의미 설명을 당시 mountinfo 관측으로 대신하지 않는다.

내부 [fixture 정책](../../experiments/domain-model/s2/verification/2026-11-17-vm-cli-smoke/prepared/config.toml)은 root deny·minimal read, source/scratch/worker-home write, materials/public read, cli-state deny다. 이는 helper가 구성하려는 **내부 파일 뷰**다. 구성 전의 helper 쓰기는 이미 활성인 **외부 systemd 경계** 안에서 일어나므로 내부 deny와 외부 EROFS를 같은 시점의 판정으로 섞지 않는다.

## 3. 오류 전파와 경로 후보

고정 소스에서 오류 문자열은 [linux_run_main.rs:461](https://github.com/openai/codex/blob/c40729ea5cf8e947481b130c59807273eda2f8e9/codex-rs/linux-sandbox/src/linux_run_main.rs#L461)의 `exit_with_bwrap_build_error`에 있다. 원시 stderr는 구체적 하위 경로를 출력하지 않는다. 일반적인 도달 순서는 다음과 같다.

```text
sandbox 명령 → env를 새로 구성한 codex-linux-sandbox helper
  → run_bwrap_with_proc_fallback
  → preflight_proc_mount_support → build_preflight_bwrap_argv
  → build_bwrap_argv → create_bwrap_command_args → create_filesystem_args
  → prepare_shared_daemon_socket_directory
  → canonicalize("/tmp") + effective UID22002
  → DirBuilder(mode0700).create
  → I/O 오류 전파 → exit_with_bwrap_build_error → exit1
```

[helper 인자 생성](https://github.com/openai/codex/blob/c40729ea5cf8e947481b130c59807273eda2f8e9/codex-rs/sandboxing/src/landlock.rs#L25)에는 no-proc/inherit-pid-namespace가 없고 legacy=false다. 따라서 [mount_proc=true](https://github.com/openai/codex/blob/c40729ea5cf8e947481b130c59807273eda2f8e9/codex-rs/linux-sandbox/src/linux_run_main.rs#L274)로 proc preflight 인자부터 구성하는 정적 경로가 우세하다. 실제 helper argv/자식 trace가 없으므로 preflight에서 실패했다고 실행 사실로 확정하지 않는다. launcher 탐색이 먼저 있어 **bwrap 프로세스가 어떤 목적으로도 전혀 실행되지 않았다**고 단정하지도 않는다.

| 우선순위·후보 | 연산과 단계 | 지지 근거와 반대 근거·불확실성 |
| --- | --- | --- |
| **선두: canonical(/tmp)/codex-daemon-22002** | helper outer stage의 mkdir 계열,0700. 보통 `/tmp/codex-daemon-22002` | [daemon_directory.rs:13–38](https://github.com/openai/codex/blob/c40729ea5cf8e947481b130c59807273eda2f8e9/codex-rs/uds/src/daemon_directory.rs#L13). HOME/TMPDIR/CODEX_HOME와 무관하게 경로 계산; create_filesystem_args 첫 작업. `/tmp` 외부 쓰기 예외 없음. 다만 당시 경로 canonicalization·존재/owner/mode·실패 syscall은 미수집 |
| 낮음: canonical(/scratch)/codex-bwrap-synthetic-mount-targets-22002 | 본 인자 구성에서 create_dir_all; 이후 lock/marker 파일 쓰기 | [bwrap.rs:730](https://github.com/openai/codex/blob/c40729ea5cf8e947481b130c59807273eda2f8e9/codex-rs/linux-sandbox/src/bwrap.rs#L730), [registry 계산](https://github.com/openai/codex/blob/c40729ea5cf8e947481b130c59807273eda2f8e9/codex-rs/linux-sandbox/src/linux_run_main.rs#L962). TMPDIR를 따르며 scratch는 외부 쓰기 허용. 첫 proc preflight는 writable root가 없는 minimal 정책이라 이 인자 구성 분기의 mkdir가 도달하지 않는 경로가 우세. 이후 registry lock/marker 실패는 별도 panic 문구여서 관측 stderr와 다름 |
| 더욱 낮음: /home/runner/cli-state 아래 초기화 쓰기 | native CLI 초기화 시 config/상태 경로 | HOME/CODEX_HOME와 연관되지만 디렉터리는 외부 writable이고 config 파일만 RO. 관측 오류 prefix는 helper의 bwrap 구성 경로에 대응한다. 전체 초기화 쓰기를 열거하거나 실제 모든 성공을 관측한 것은 아님 |
| 현재 오류와 단계 불일치: /source/output.txt, 보호 metadata mount target | payload 쓰기 또는 bwrap argv 준비 이후의 mount/target 생성 | payload 미시작. 보호 metadata 처리 일부는 `/dev/null` 읽기와 argv 추가일 뿐 즉시 해당 경로를 쓰지 않는다. bwrap 자체 mount 오류나 과거 container의 clone EPERM을 이번 EROFS와 동일 원인으로 볼 근거 없음 |

선두 후보의 정확한 소스는 [daemon_directory.rs:13–38](https://github.com/openai/codex/blob/c40729ea5cf8e947481b130c59807273eda2f8e9/codex-rs/uds/src/daemon_directory.rs#L13), 호출은 [bwrap.rs:414](https://github.com/openai/codex/blob/c40729ea5cf8e947481b130c59807273eda2f8e9/codex-rs/linux-sandbox/src/bwrap.rs#L414)다. 이 디렉터리는 daemon을 시작하려고만 만드는 것이 아니라 **sandbox에서 privileged app-server socket 경로를 숨기기 전에 준비하는 공통 경로**다. daemon_auto_start=false로 생성을 차단하는 조건은 이 호출 경로에 없다. 이미 올바른 owner/mode로 존재하면 AlreadyExists를 받아 다음 단계로 넘어가므로, 존재 여부를 모르면서 실패를 확정할 수는 없다.

## 4. 다음 결정 하나

**권한 변경에 앞서, 원래 프로파일·UID·환경·바이너리를 유지하는 제한적 syscall 관측을 제안한다.** 아직 승인·구현·실행된 시험이 아니다. 일회성 VM1개에서 기존 고정 입력과 R20 정리를 재사용하고, 기존 이미지의 strace 사용 가능성을 확인해 native 명령 한 회의 파일 접근/프로세스 계열을 관측하는 정도다. 예상30~45분은 준비·관측·폐기·보고를 포함한 참고 비용이며 새 고정 gate가 아니다.

얻을 정보는 helper/CLI PID 연결, 실패 mkdir/mkdirat 또는 open 계열의 **실제 path·errno·실행 순서**, 같은 서비스 mount namespace에서 `/tmp`의 canonical 경로와 관련 mountinfo, 대상의 사전 존재/owner/mode다. 관측자는 ptrace가 필요하며 동일 UID의 trace wrapper 또는 guest 관리자의 관측 방식은 후속 설계에서 정한다. worker capability·NNP·ReadWritePaths·내부 profile을 유지하고, 제한된 trace 저장과 부모/자식 시간 제한을 사용한다. trace 도구나 ptrace 조건이 충족되지 않으면 그 회차를 미확정으로 인계하며 권한을 자동 확대하지 않는다. 이번에는 준비 스크립트도 만들지 않았다.

- 같은 daemon 경로의 mkdir와 EROFS가 관측되고 해당 경로의 RO mount가 확인되면 선두 가설을 확인한다. 이후 관리자가0700/UID22002 디렉터리를 사전 준비하는 최소 변경의 적합성 등을 별도 검토한다. `/tmp` 전체 writable이나 ProtectSystem 해제를 바로 적용하지 않는다.
- 다른 경로/연산이 EROFS라면 이 가설을 수정하고 해당 연산의 필요성과 경계를 검토한다.
- trace 부착 실패·관측 누락·오류 미재현이면 미확정이다. 같은 회차에서 설정을 바꾸며 성공할 때까지 재시도하지 않는다.

정적 정보만으로도 이 한 회의 질문을 구체화할 수 있으므로 추가 전체 소스 탐색이나 실행기 확장은 필요하지 않다.

## 5. 검사·보존·인계

작업 기준은 main `38481fd`이며 새 브랜치 `codex/s2-erofs-diagnosis`를 사용했다. 원래 freeze의 worker.py/setup.py는 현재와 동일하고 run.py/bounded.py는 R20 때문에 다르다. 환경 해석은 변경되지 않은 동결 worker/setup과 당시 원문을 근거로 했으며 현재 정리 코드를 옛 실행 코드로 취급하지 않았다. 과거 index 포함99파일을 `2008351`과 byte 비교해 불변을 확인했다.

[pnpm check 로그](../../experiments/domain-model/s2/verification/2026-11-18-erofs-diagnosis/pnpm-check.log)의304테스트·타입 검사·예제 빌드가 통과했다. 신규 실행/분석 프로그램은 저장소에 추가하지 않았다. 작업용 읽기 스크립트로 source blob/hash, archive integrity/asset digest, provenance subject/commit, 당시 binary hash, excerpt 행 대응과 문서 링크를 검사했다. 관측 값을 만들어 내는 가짜 runtime이나 관련 없는 이전 실험은 반복하지 않았다.

[요약](../../experiments/domain-model/s2/verification/2026-11-18-erofs-diagnosis/summary.json)에 조사 종료 시각·계측 시간·검사를 남긴다. 시작 기록은07:36:34 UTC이며 그 전 지시 읽기·Git 상태 조회는 해당 계측에 포함하지 않았다. 새 VM·실제 limactl/CLI·동적 trace·빌드/패키지 설치·정책 변경·credential/model/본 비교는0회다. 공개 package 분석 다운로드와 source 조회는 runtime 실행과 구분한다.

이번 문서/근거는 새 PR로 반영하며 이미 병합된 PR #70을 다시 열지 않는다. PR #67은 별도 보류다. 후속 실제 시험·설정 변경·C안 채택은 결과 리뷰 뒤 결정한다. R11 unresolved·production/live 거부·trialAuthorized/readyForTrial=false·results=null·H-O/H-F 미검증은 유지한다.
