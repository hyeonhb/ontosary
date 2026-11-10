# S2 일회성 컨테이너 타당성 — 2026-11-10

**판정: inconclusive.** Lima 2.3.0/VZ 전용 VM 기동, cgroup v2/systemd 관찰, Linux arm64 준비 이미지 빌드는 성공했다. 그러나 로컬 이미지 실행 식별자를 잘못 연결했고 한 번의 수정·재시도도 실패해 중단했다. worker/평가 단위가 시작되지 않았으므로 종료·수집·Linux 평가의 타당성은 판단하지 못했다. 런타임 자체가 불가능하다는 결론은 아니다. **R11 미해결, R12 기존 검증 범위 유지**, `trialAuthorized:false`, `readyForTrial:false`, `results:null`, 실제 모델/provider/본 비교0회다.

Base는 main `2f2acb22279c8cc34d0947e4eca40d4fd213307e`, 작업 브랜치는 `codex/s2-container-feasibility`다. 최종 내용은 [재귀 구현·증거 manifest](../../experiments/domain-model/s2/verification/2026-11-10-container-feasibility/manifest.json)의 파일 hash로 식별한다. 최종 저장소 commit은 이 보고서를 포함하는 PR의 검증된 head/merge 기록으로 확인한다. 자기 commit hash를 파일에 삽입하는 순환 지문은 만들지 않는다. 이 보고는 자체 검토이며 독립 해결 판정을 대신하지 않는다.

## 실제 진행과 중단 원인

후보는 **Lima native VZ + bundled containerd/nerdctl 2.4.2** 하나다. 호스트에 사용 가능한 런타임이 없어 공식 Darwin arm64 archive를 작업 전용 prefix에 풀었다. Homebrew 전역 설치, 호스트 sudo/보안 설정·서비스·Docker context 변경, 새 계정/유료 서비스는 사용하지 않았다. guest의 root container manager와 준비용 root 권한은 호스트 관리자 권한과 구분한다.

1. 공식 archive SHA-256 검증 후 Ubuntu 26.04.1 arm64 VM을 기동했다. kernel `7.0.0-38-generic`, cgroup v2, systemd driver를 관찰했다. VM은4CPU/6GiB/24GiB이고 host mount는 없다. host loopback·SSH agent/기존 public key 전달·일반 port forwarding을 비활성화했다. Lima의 관리 SSH/time-sync 내부 통신은 남아 있으며 worker 네트워크 거부 증거로 세지 않는다.
2. 고정 Node 22.19.0 이미지 index digest를 사용해 공식 Codex `0.167.0-alpha.3.2`, npm10.9.3, TypeScript5.9.3, 빌드용 타입 패키지를 설치한 이미지를 만들었다. npm registry의 같은 Linux arm64 배포가 존재함을 확인했다. 사용자 CODEX_HOME·자격 증명·대화·plugins/skills는 복사하지 않았다.
3. 원래 inventory4,735파일의 hash를 확인해 Linux 준비 경로에 복사했다. macOS node_modules/Node 바이너리는 복사하지 않았다. Linux 전용 `npm ci --ignore-scripts --no-audit --no-fund --workspace=@vendure/admin-ui --workspace=@vendure/common --include-workspace-root`와 원래 common build를 준비했으나 **실행되지 않았다**.
4. 첫 실행은 `ontosary-s2-feasibility@sha256:fbea81…`를 로컬에서 해석하지 못하고 registry로 조회해 `pull access denied`로 실패했다(exit1). 동시에 시도한 모델 없는 CLI preflight도 같은 원인으로 시작 전에 실패했다. 이때 설치·CLI shell·worker가 시작된 것으로 세지 않는다.
5. 허용된 작은 수정1회로 `--pull=never`와 Docker 호환 inspect의 `Id=sha256:c7fb3d…`를 사용했으나 `image not available`로 실패했다(exit1). **두 번째 수정은 하지 않았다.** 정리용 `nerdctl images --digests --no-trunc`에서는 native image ID가 manifest digest `sha256:fbea81…`로 표시됐다. config digest와 native image ID를 혼동한 호출 구현의 문제이며, 권한/격리 결함을 관찰한 것은 아니다. native manifest ID를 사용한 실행은 이번에 검증하지 않았다.

원문 오류·명령·exit code는 [증거 README](../../experiments/domain-model/s2/verification/2026-11-10-container-feasibility/README.md), `raw/05-*`, `raw/06-*`, `raw/supplementary-commands.json`에 있다. 실패한 CLI stdout 파일은 비어 있으며 tool이 반환한 stderr를 별도 보존했다. 예산을 다 쓰기 위해 무의미하게 기다리거나 후보/권한을 바꾸지 않았다.

## 비용과 정리

UTC 기준 보수적 회계 시작10:50, 첫 시계 관찰10:59, 첫 다운로드11:03:36.814, 준비/탐색 중단11:10:51.264, 자원 삭제 완료11:12:10.341이다. 정확한 최초 읽기 시작 시각은 기록하지 못했으므로10:50을 실측값이라고 부르지 않는다. 읽기·후보 조사도 빠지지 않도록 **환경 준비 청구는 보수적으로20분51초/90분**이다. 첫 다운로드부터 중단까지의 측정 구간은7분14초이며 그 안의 기록된 장기 명령 합계는4분2초다. 전체 문서화/검증 마감 시각과 소요 시간은 `raw/budget.json`의 `evidenceFreezeTime`/`totalAtEvidenceFreezeSeconds`에 기록하며, Git 전달은 별도 항목이다. 전체240분·새 탐색210분 상한 전에 종료했다. 마지막30분을 침범하지 않았다.

| 단계 | 측정 시간/상태 |
| --- | --- |
| Lima archive 다운로드 | 6.25초, exit0 |
| 이미지 다운로드·변환·nerdctl 설치·VM 기동 | 179.64초, exit0 |
| Node 이미지 pull | 12.28초, exit0 |
| 준비 이미지 build | 40.99초, exit0 |
| 최초 준비 실행 | 2.44초, exit1 |
| 수정 후 준비 실행 | 0.24초, exit1 |
| 후보/수정 재시도/유료 비용 | 1개/1회/0 |

다운로드 파일에서 관측한 Lima50,317,981 + Ubuntu940,373,504 + nerdctl270,513,423 = **1,261,204,908 bytes**, Node pull 로그 약74.9MiB가 추가된다. npm/메타데이터·프로토콜 overhead의 전체 전송량은 계측하지 않아 합산 총량을 확정하지 않는다. 삭제 직전 task root6,464,688KiB + 두 Lima cache3,798,148KiB = `du` 합계10,262,836KiB(약9.79GiB)다. APFS 공유 블록 중복 가능성이 있고 peak/고유 물리 사용량은 아니다. VM 가상 디스크24GiB와도 구분한다.

`XDG_CACHE_HOME`을 전달했으나 Lima의 macOS downloader는 기본 `~/Library/Caches/lima`에 다운로드했다. 이는 초기 작업 경로 가정과 다른 관찰로 기록했다. 원본 URL·생성 시각·hash를 확인한 **이번 두 cache entry만** 삭제했다. VM stop→Stopped 확인→delete→빈 목록, hostagent PID6311 부재, task root/두 cache 부재를 확인했다. 준비/CLI container 목록은0개였고 BuildKit의 준비 작업은 끝났다. 보존 VM·image·volume·worker는0개다. 공용 prune은 사용하지 않았다. [cleanup 기록](../../experiments/domain-model/s2/verification/2026-11-10-container-feasibility/raw/cleanup.json)에 삭제 대상을 남겼으며 잔존 runtime 자원의 추가 삭제 명령은 필요 없다. ignored work에는 작은 원시 로그만 남는다.

## CLI·권한·평가 확인 범위

| 항목 | 이번 결과 |
| --- | --- |
| Linux CLI 배포/버전 | 같은 버전의 공식 Linux arm64 npm metadata와 build 설치 성공. 실제 `--version`, binary hash, help/schema/config 인식은 미실행 |
| 모델·추론 설정 | 기존 `gpt-6-astra`/`high` 유지. Linux config parse 및 실제 inventory는 미검증; 대체 모델/CLI 버전을 확정하지 않음 |
| 셸 backend·검색/편집/공개 검사 | 실행 전 실패; 호환성 미검증 |
| 인증/provider 통신 | 실제 credentials/model 호출0. control canary/provider stub 미실행; pending-live-validation |
| worker 권한·상한 | UID1000, cap-drop ALL, no-new-privileges, network none, 2CPU/4GiB/PID256 계획만 있음. 실제 적용/거부 probe 없음 |
| 전체 단위 종료 | 정상 부모 exit·timeout·detached/setsid·손자·열린 FD/pipe·경쟁·wrapper kill·관리 오류·2회 반복 모두 미실행 |
| 파일·다음 조건·socket/cgroup 접근 | guest mount 목록만 관찰. worker canary 존재/거부·readonly·이동/재위임 거부는 미실행 |
| 종료 후 수집·불변성 | adapter/receipt 미구현. 전체 추가/수정/삭제·copy 경쟁·timeout 진단 분리·다음 단위 차단 미검증 |
| 별도 평가 단위 | reference 전달·complete-root/delta·평가 지연 writer/timeout 전부 미실행. node:vm을 OS 경계로 취급하지 않음 |
| Linux Vendure/평가 | lockfile 설치/common build·S2 build·baseline/reference 공개 타입·7제출·29제출60파일 모두 미실행 |

향후 구조는 manager가 불변 unit ID/image/경로/상한을 소유하고, worker와 분리된 감시자가 wrapper 사망에도 deadline을 책임지며, cgroup 단위 kill/empty와 이동 거부를 검증한 뒤 수집해야 한다. 정상 exit도 이 절차가 필요하다. timeout 제출은 진단이며 정상 성공 채점에서 제외한다. 제출 평가도 별도 일회성 단위여야 한다. **이 흐름은 이번에 구현/증명하지 않았다.** `bounded-command.py`의 호스트 process-group timeout은 준비 명령의 best effort일 뿐 R11 해결책이 아니다.

새 image manifest `sha256:fbea81dbc73da64f8798dd025d17d7bfb559a953671b520a235220ae9dc3e47b`, config `sha256:c7fb3d12a1f8d73febec26ad54fbf1987cd55af0d573947b95a91d95a1e9a6d2`, base index `sha256:4a4884e8a44826194dff92ba316264f392056cbe243dcc9fd3551e71cea02b90`를 분리 기록했다. 이 준비 이미지 지문은 Linux 평가 환경의 동등성 지문이 아니다. 실제 설치된 OS별 Vendure 의존성/Program 차이는 얻지 못했으며 macOS 결과를 Linux 성공으로 정규화하지 않았다.

## 보존·검증과 다음 결정

호스트 `pnpm check`:15파일303테스트·skip0·타입 검사·예제 build 통과, `pnpm experiment`:4/4, `pnpm s2:build` 통과다. R12 원래18fixture를 다시 실행해 과거 JSON과 완전히 일치했고 live/production 평가의 거부도 확인했다. 기존 macOS22실행/29제출 교정 전체를 이번에 다시 수행한 것으로 세지 않는다. Linux 테스트는0개다.

고정 Vendure revision `534e6003534f74761e82de1b8c6061cba89945d1` 원본4,735파일과 정적 agent84파일 hash를 다시 대조했다. bundle `ab522d70…`, baseline `7707db72…`, model `2ba6c772…`, evaluator `b7b6407b…`는 보존했다(전체 값은 `raw/verification.json`). 제품 코어/FCA/모델 지식/평가 v4·역사 증거는 수정하지 않았다. 새 manifest는 Dockerfile·YAML·shell/Python·하위 디렉터리와 당시 초기 helper까지 재귀 포함한다. 옛 `freeze.ts`/execution manifest를 덮어쓰지 않았다. 실제 실행된 것은 준비 명령/VM/Dockerfile이며 미실행 shell도 명시했다.

다음 리뷰에서는 **동일 후보의 로컬 이미지 식별자 연결을 고치는 짧은 새 예산을 허용할지** 먼저 결정하면 된다. 현재 증거는 후보 교체나 호스트 권한 확대를 뒷받침하지 않는다. 재시도가 승인되어도 baseline/reference 타입부터 시작해 지시문의 종료/접근/수집/평가 표 전체를 검증해야 한다. 그 뒤에도 R11 독립 리뷰, C 사람 검토, 실제 CLI 도구 inventory·계정/모델·인증과 도구 네트워크 분리 검증은 별도이며 실제 비교 승인을 의미하지 않는다.

기술 근거: [Lima 공식 설치](https://lima-vm.io/docs/installation/), [VZ user networking/host loopback](https://lima-vm.io/docs/config/network/user/), [고정 버전 downloader의 cache 처리](https://github.com/lima-vm/lima/blob/v2.3.0/pkg/downloader/downloader.go), [Linux cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html). Lima/Codex package는 Apache-2.0 metadata를 확인했다. Vendure는 원래 라이선스의 외부 고정 입력이며 source/archive/node_modules/VM/image를 저장소에 배포하지 않았다.
