# S2 동일 컨테이너 후보의 이미지 식별자와 최소 실행 재검증

개발 세션은 **Lima 2.3.0/VZ + containerd/nerdctl 2.4.2 후보를 유지하고, 30분 안에서 로컬 이미지 식별자 수정과 모델 없는 최소 실행만 검증**한다. 사용자가 승인한 후속 범위다. 성공하거나 중단하면 결과를 인계하고 끝낸다. Vendure 준비, R11 종료·수집 adapter, 평가 재현, 실제 모델 호출과 본 비교는 결과 리뷰 이후에 별도로 진행한다.

이 지시는 [직전 타당성 지시](2026-11-10-s2-container-feasibility-instructions.md)의 넓은 검증을 재개하는 승인이 아니다. 이번 회차에 한해 아래 시간·재시도 정책이 이전의 ‘환경 수정 후 재시도1회’를 대체한다. 이전 지시·실패 증거는 당시 기록으로 보존한다. 제품 목표와 모델/과업/평가 계약은 그대로다.

## 1. 출발 상태와 읽을 자료

최초 읽기 전에 UTC 시작 시각과 단조 시계를 기록한다. PROGRESS → ARCHITECTURE → ROADMAP, AGENTS/CONTRIBUTING을 확인하고 원격·브랜치·사용자 변경을 점검한다. 기준은 PR #38의 `6e22bc7` 이후 최신 main과 이 지시를 포함한 commit이며, 실제 base SHA를 기록한다. 다른 checkout의 브랜치/변경과 원본 Vendure cache를 건드리지 않는다.

- [이전 결과](2026-11-10-s2-container-feasibility.md)와 [원시 증거](../../experiments/domain-model/s2/verification/2026-11-10-container-feasibility/): `raw/05-*`, `raw/06-*`, `raw/worker-image.json`, `raw/pre-cleanup-guest.log`, `raw/supplementary-commands.json`, `raw/budget.json`, `raw/cleanup.json`을 우선 확인한다.
- [기존 준비 구현](../../experiments/domain-model/s2/trial/container/): Dockerfile, lima.yaml, README와 bounded-command.py, freeze-evidence.py를 확인한다. 이 디렉터리는 실행 adapter가 아니다.
- [nerdctl 2.4.2 명령 문서](https://github.com/containerd/nerdctl/blob/v2.4.2/docs/command-reference.md#image-management): 이미지 target(index/manifest) digest와 config digest의 차이를 확인한다.

이전에는 VM 기동·이미지 빌드까지만 성공했다. repo@manifest 호출은 로컬 조회에 실패해 registry 접근으로 넘어갔고, 수정 호출은 Docker 호환 inspect의 config ID를 사용해 실패했다. 종료 전 native 이미지 목록은 manifest digest를 image ID로 표시했다. 올바른 식별자로 실행되는지는 아직 미검증이다. 이전 VM/image/cache는 삭제됐으므로 재준비 시간을 포함한다.

이전 manifest `sha256:fbea81dbc73da64f8798dd025d17d7bfb559a953671b520a235220ae9dc3e47b`와 config `sha256:c7fb3d12a1f8d73febec26ad54fbf1987cd55af0d573947b95a91d95a1e9a6d2`는 과거 증거다. 이미지 재빌드의 새 digest가 같다고 전제하거나, 과거 digest를 현재 로컬 이미지 ID로 하드코딩하지 않는다.

## 2. 시간과 비용 상한

| 항목 | 이번 회차의 계약 |
| --- | --- |
| 총 시간 | 최초 읽기부터30분 경과 시간. 조사·다운로드·재설치·VM/이미지 재생성·대기·수정·probe·회귀·정리·최소 보고를 포함 |
| 탐색 마감 | 20분에 새 설치/빌드/수정/probe 시작을 중단. 마지막10분은 실행 중 명령 종료·정리·검증·증거/보고 보존에 사용. 더 일찍 성공하면 즉시 마무리 |
| 명령 한도 | 각 명령에 남은 단계 예산 이하의 timeout을 적용.20분에 탐색 명령이 계속 실행 중이면 중단하고 미완료로 기록 |
| 후보·유료 비용 | 기존 후보1개, 신규 유료 비용0. 다른 플랫폼·새 계정·유료 서비스·호스트 관리자 권한·보안 설정/전역 서비스/기본 Docker context 변경은 제외 |
| 누적 기록 | 이전 회차와 이번 회차를 별도 열로 기록. 이전 환경 준비 보수적1,251.264초와 이번 환경 시간을 합산하고, 전체 비용은 이전 budget.json의 측정/추정 구간을 구분해 합산. 회차 사이 사용자 검토 대기 시간은 작업 시간에서 분리 |

이번30분은 새로 승인된 한 회차이며 이전90분/4시간 예산을 초기화하거나 남은 시간을 사용할 권한이 아니다. 이번 환경 시간을 모두30분으로 잡아도 누적 환경 준비는 약50분51초다. 남은 기존 예산이 있어도 이번 마감/범위에서 끝낸다. 세션 재시작·실패·재빌드로 시계를 다시 시작하지 않는다.

30분 뒤에는 새 검증을 시작하지 않는다. 실행 중 자원 정리와 이미 얻은 증거의 최소 보존만 마치고 불가피한 초과 시간·이유를 기록한다. Git 게시/PR/merge의 대기·전달 시간은 별도 기록하고 실험을 재개하지 않는다. 필요한 검사를 시간 안에 완료하지 못했다면 미완료로 인계하고, 검증 없이 merge하지 않는다.

## 3. 허용 변경과 재시도 정책

수정은 기존 `trial/container/`의 이미지 조회·실행 연결, 짧은 smoke 스크립트, 필요한 로그/마감/정리 보완과 새 증거·문서에 한정한다. 새 의존성/다중 backend 추상화/범용 실행기를 만들지 않는다. 고정 Lima·nerdctl·Node22.19.0·Codex0.167.0-alpha.3.2·TypeScript5.9.3 및 기존 base index digest를 유지한다. 버전을 바꿔 통과시키지 않는다.

동일 후보에서 이름·namespace·digest 종류·인자·작업 디렉터리 같은 국소 오류는 **시간 예산 안에서 원인을 확인한 후 수정·재시도**할 수 있다. 고정 재시도1회 제한은 적용하지 않는다. 매번 실패 명령/오류, 진단 근거, 변경한 한 요소와 기대 결과를 남긴다. 조회/inspect 같은 읽기 전용 진단도 시간에는 포함하되 실행 재시도와 구분한다.

새 증거·수정 가설 없이 동일 명령을 반복하거나 여러 ID를 무작정 대입하지 않는다. 같은 오류가 수정 후 다시 나타나면 먼저 진단하고, 남은 시간 내 구분 가능한 가설이 없으면 중단한다. 임의 sleep, 전체 재설치 반복, registry 로그인이나 권한 확대를 이미지 조회 오류의 우회로 사용하지 않는다.

## 4. 실행 순서와 최소 검증

### A. 동일 환경 재준비와 이미지 연결

기존 선언/공식 배포를 사용해 작업 전용 prefix·LIMA_HOME·VM을 준비한다. host mount·SSH agent/기존 public key 전달·일반 port forwarding은 기존처럼 비활성화한다. 관리용 guest 권한과 worker 권한을 구분하고 호스트 sudo를 사용하지 않는다. 이번에는 Vendure source/node_modules나 평가기를 VM으로 복사하지 않는다.

이미지 빌드 후 **run보다 먼저** 실제 사용 중인 containerd endpoint/namespace를 확인하고, 같은 manager 문맥에서 native 이미지 목록/metadata와 Docker 호환 inspect를 함께 보존한다. 다음을 각각 기록한다: 로컬 정규화 이름과 tag, target manifest/index digest·선택 platform, config digest, build에 사용한 선언과 실제 CLI 패키지 버전. 현재 build 결과를 기준으로 실행 대상을 선택한다.

실행 참조는 해당 버전에서 확인한 native image ID 또는 작업 전용 로컬 tag를 사용할 수 있다. tag 사용 시 manager만 이름을 관리하고, 실행 전 target digest를 고정해 생성된 container의 실제 image target과 대조한다. `Config.Image` 문자열이나 tag가 같다는 것만으로 동일성 통과를 선언하지 않는다. index/manifest/config를 구별해 연결하고, 이 대응을 확인할 수 없으면 미확정으로 남긴다. 별도 서명/registry 시스템은 만들지 않는다.

**모든 smoke 실행에 `--pull=never`를 적용**한다. 이미지 빌드 때 필요한 다운로드와 smoke의 이미지 lookup을 분리한다. container를 명시적으로 create → immutable ID/metadata 기록 → start/wait → exit code/log 수집 → remove하는 작은 흐름을 권장한다. 원인을 보기 전에 자동 삭제해 증거를 잃지 않는다.

### B. 비특권 셸과 Node 실행

worker는 UID/GID1000:1000, cap-drop ALL, no-new-privileges, network none, CPU2/memory4GiB/PID256 상한을 명시한다. privileged·host PID/network·관리 소켓·호스트 홈/원본/자격 증명 마운트를 허용하지 않는다. 이미지의 선언만 믿지 말고 생성 metadata와 실행 출력에서 설정을 대조한다. 이 확인은 권한 설정의 smoke이며 격리 공격/종료 보장의 증명은 아니다.

새 container에서 아래를 순서대로 확인한다. probe당 최대60초이며 탐색 마감이 더 가까우면 짧은 값을 적용한다.

1. `sh`에서 고정 시작 표식과 `id`를 출력하고 exit0으로 끝난다. 시작 표식 없는 exit를 성공으로 세지 않는다.
2. Node 버전이22.19.0인지 확인하고, 로컬에서 고정 JSON을 출력하는 짧은 Node 명령을 실행한다. 별도 probe의 명시적 exit7도 manager가7로 관찰해 CLI 실행 실패와 workload 종료 상태를 구분하는지 확인한다.
3. 최종 참조 방식으로 새 container 하나를 더 만들어 셸·Node 최소 probe를 반복한다. 재빌드 없이 두 실행의 target digest와 서로 다른 container ID를 대조한다.

### C. 모델 호출 없는 CLI 기동

같은 환경의 별도 새 container에서 공식 Codex CLI의 `--version`과 `--help`만 실행한다. 버전이0.167.0-alpha.3.2인지, 실제 종료 코드/출력과 launcher 및 확인 가능한 native 실행 파일의 hash를 기록한다. 사용자 CODEX_HOME을 복사하지 않고 container 안의 빈 쓰기 가능한 HOME/CODEX_HOME을 사용한다. 실제 인증정보·대화·plugins/skills를 전달하지 않는다.

`exec`, 대화형 세션, 로그인, ‘hello’ 요청, provider 연결 시험은 실행하지 않는다. 모델 gpt-6-astra/high 설정·인증·실제 도구 inventory·CLI가 모델을 통해 셸을 사용하는 경로는 미검증으로 남긴다. 일반 셸 실행과 CLI help 성공을 이 경로의 검증으로 바꾸어 서술하지 않는다. 네트워크/인증이 없어서 version/help도 동작하지 않으면 범위 내 진단 후 인계한다.

## 5. 중단과 정리

다음 중 하나면 의존 작업을 멈추고 남은 시간을 정리/보고에 쓴다.

- 탐색20분 또는 총30분 마감에 도달하거나 남은 정리 시간을 확보할 수 없음.
- 버전/후보 교체, 호스트 관리자 권한·보안/전역 설정 변경, privileged·관리 소켓 노출, CLI 포크/API 실행기가 필요함.
- 실제 인증/provider 호출·Vendure 설치/빌드·R11 adapter 구현이 있어야 다음 단계로 갈 수 있음.
- 이미지 target과 실제 container의 연결을 확인하지 못하거나, 동일 오류에 대한 새로운 진단 근거가 없음.
- 소유 worker/VM 종료 확인에 실패하거나 예상하지 않은 호스트 접근·잔존 쓰기를 관찰함. 이후 probe를 진행하지 않고 복구 필요 사항을 인계함.

성공해도 **이번 회차의 container·VM·작업 전용 설치/이미지/volume을 정리**한다. 자원 ID/소유 경로를 시작부터 기록해 scope가 명확한 stop/remove/delete를 수행한다. command timeout/process-group kill만으로 VM이 끝났다고 간주하지 않는다. 최종 VM 상태/목록·관련 hostagent 부재·작업 경로 부재 등 관측을 보존한다. 이는 smoke 자원 정리이며 R11의 적대적 자손 종료 검증이 아니다.

Lima macOS downloader가 XDG_CACHE_HOME 대신 기본 cache를 썼던 사실을 반영한다. 기존 cache는 읽기 재사용할 수 있지만 이전부터 있던 항목을 삭제하지 않는다. 새로 생성한 항목만 URL·생성 전후 inventory·hash로 소유권을 확인해 정리하며, 공용 prune을 하지 않는다. 정리 실패 시 대상·관측 상태·수동 복구 방법을 보고하고 성공으로 표시하지 않는다.

## 6. 산출물과 판정

새 증거는 `experiments/domain-model/s2/verification/<실제 날짜>-container-smoke/`, 보고는 `docs/reviews/<실제 날짜>-s2-container-smoke.md`에 둔다. 같은 날짜의 기존 feasibility 디렉터리/보고/manifest를 덮어쓰지 않는다. 같은 이름이 이미 있으면 새 suffix를 사용한다.

보고에는 아래를 포함한다.

- 이전 두 실패의 원인과 이번 수정, 선택한 최종 실행 참조, image 이름/target/config/platform → container ID의 대응과 원시 명령/출력/exit code.
- 셸·Node·반복 실행·CLI version/help의 통과/실패/미실행 표. 실행하지 않은 Linux Vendure·격리·전체 종료·수집·평가·provider 항목은 별도로 표시.
- UTC/단조 시계 기반 단계별 시간, 이번30분 사용량·재시도별 가설/비용, 이전/이번/누적 비용과 추정 여부, 다운로드/디스크 관측 및 한계.
- 실제 실행한 구현 파일 전체의 hash, 이미지 지문, readonly 진단 원문, cleanup 대상/상태. 재시도 중 구현이 바뀌면 당시 실행본도 보존. 비밀·VM 디스크·이미지·node_modules는 커밋하지 않음.

판정은 `smoke-passed`(이미지 대응·필수 최소 실행/반복·CLI 버전·정리 확인), `inconclusive`(시간/증거 부족), `blocked`(확인된 원인으로 승인 범위 내 진행 불가) 중 하나다. 부분 통과는 표에 남긴다. 이 판정은 **최소 실행에만** 적용하며 이전의 `feasible-for-next-preparation` 판정을 사용하지 않는다.

공통 완료 조건은 범위·비용 기록, 실패 포함 재검토 가능한 증거, 소유 자원 정리 또는 구체적 복구 인계, 역사 자료/기존 계약 보존이다. R11 unresolved, R12 기존 검증 범위, `trialAuthorized:false`, `readyForTrial:false`, `results:null`, 실제 모델/provider/본 비교0회를 유지한다. 실패 인계도 이 조건을 충족하면 이번 작업은 끝낼 수 있다.

## 7. 회귀와 인계

`pnpm check`를 마지막10분 안에 끝낼 수 있도록 준비하고 실제 결과를 기록한다. 이번 범위에서는 제품 분석 동작/fixture를 바꾸지 않으므로 `pnpm experiment`나 기존29제출 전체 재실행은 기본 요구가 아니다. 필요한 경우 변경한 작은 준비 스크립트의 구문/오류 처리와 본 smoke로 확인한다. 호스트 회귀 성공을 Linux 검증으로 세지 않는다.

PROGRESS·ROADMAP·ARCHITECTURE·REVIEW_CONTEXT와 container README에 이번 결과와 다음 리뷰 대기 상태를 반영한다. 새로운 결정이 있으면 DECISIONS에 당시 근거를 추가하고 과거 기록은 보존한다. 검증·staged diff 검토 후 기존 지속 승인에 따라 commit → push → PR/자체 검토 → 필수 검사와 검증한 head 확인 후 merge → 로컬 main 동기화한다. 검사 미완료/실패라면 인계하고 merge하지 않는다.

**최소 실행이 모두 통과해도 그 자리에서 후속 준비를 시작하지 않는다.** 다음 리뷰에서 R11 종료·수집/평가 경계, Linux Vendure 재현의 범위·비용을 결정한다. 본 비교 승인은 별개다.
