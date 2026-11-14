# S2 준비물 재사용·공통 수명주기 개발 인계 — 2026-11-14

**구현은 부분 완료, 실행은 blocked/inconclusive, 회차는 정리 후 종료했다. 독립 리뷰 전 개발 인계다.** 준비물 4개의 검증·재사용과 새 로컬 회귀는 통과했다. 실제 필수 7단위 중 첫 정상 단위는 생성된 전체 Spec에서 AppArmor 누락과 `rro→ro` 차이가 확인돼 시작 전에 차단됐다. 작업 시작 0회이며 나머지 6단위·원래/후보 정책 대조는 미실행이다. 차이를 사후 허용하거나 재시도하지 않았다.

생성된 container는 등록 후 **0.854초**에 삭제·부재 확인, **1.236초**에 service 비활성/단위 파일 정리를 마쳤다. 결과 공개와 다음 실행은 차단됐다. 실제 시작·timeout·wrapper 사망·주입한 감독자 사망·다음 실행 격리·collector 실패의 실제 검증을 대신하지 않는다. R11 unresolved, R12 기존 범위, production/live 거부, `fixtureOnly=true`, `validSubmission=false`, `trialAuthorized=false`, `readyForTrial=false`, `results=null`을 유지한다.

## 기준과 범위

사용자가 지정한 [승인 지시](https://github.com/hyeonhb/ontosary/blob/191211d21942137932d189e4229ddfb5d330fece/docs/reviews/2026-11-14-s2-execution-lifecycle-instructions.md)를 따랐다. 구현 기준과 실제 시작 head는 모두 `f62152194ffeac2ea9e203beca9fd37bab862e39`(PR #52)다. 원격 main과 구현 차이는 없었다. 지시/ADR-047은 별도 `docs/s2-execution-lifecycle-plan` 브랜치의 `191211d`에서 읽었고 해당 worktree는 수정하지 않았다. 이 회차 결정은 ADR-048에 기록했다.

최초 UTC는 `2026-11-14T05:33:20.873332Z`, host monotonic은 `174128.822953708`이다. 읽기·설계·구현·검증·대기를 모두 포함했다. 60/100/150/180분 마감은 각각 UTC 06:33:20/07:13:20/08:03:20/08:33:20이다. 준비 진입은 06:00:17, 하위 마감은 한 번만 **06:20:17**로 고정했다. 분석은 06:12:06에 동결했으며 이후 새 작업 실행은 없다.

[증거 묶음](../../experiments/domain-model/s2/verification/2026-11-14-execution-lifecycle/)의 `host/start-inventory.json`, `start.json`, `plan.json`, `budget.json`, `execution-source-link.json`이 최초 입력·변경 허용 범위·시계·실행본을 연결한다. 지시 원문은 실행 snapshot에 보존했다. 기존 과거 증거, 제품, 모델/B/C, 평가기, 배포 ID 입력을 바꾸지 않았다. TS 분석/평가 의미가 바뀌지 않아 Vendure 7단위·S2 build·전체 `pnpm experiment`는 반복하지 않았다.

## 구현과 재사용 경계

[실험 README](../../experiments/domain-model/s2/trial/container/execution-lifecycle/README.md)에 명령, 경로, 소유권과 보관/폐기를 기록했다.

| 책임 | 이번 변경 | 검증 범위 |
| --- | --- | --- |
| 준비물 | `artifacts.py`: 잠금, 전용 staging, SHA-256/크기, 원자 등록, 입력 manifest 일치, 매 hit 재해시, 10GiB 상한 | 작은 부정 fixture와 실제 4파일 재사용; 이미지 OCI blob/manifest/config/chain 및 import 뒤 identity |
| 실행 | `engine.py`: 등록 전 소유 기록, 독립 service/ExecStopPost, stop→settle→remove→collect, 독립 inactive 확인, 명시적 복구 | 실제 생성 후 비교 실패의 자동 삭제·결과 차단; 나머지는 로컬 CLI fixture |
| 정책 | `identity.py`: 소유 관계 검증→지정 위치 치환→전체 Spec 비교, 치환 근거와 diff 보존 | 과거 실제 두 Spec의 별도 기대값/부정 사례 및 이번 created Spec의 보안 차이 거부 |

기존 `lifecycle/common.py`의 cgroup·PID/task 확인과 `collector.py`의 no-follow 수집을 재사용했다. 선택적 absolute deadline/env 인자로 lock·명령·수집을 제한하며 기존 caller의 기본값을 유지했다. 공유 회귀 16개가 통과했다. `snapshot/scope/package`는 정확한 분석 명령 등록과 여러 source 디렉터리 포장을 지원하며 기존 감사 44개를 유지한다. 실패 회차의 `retry-job/guest/install/remove/export.py`는 새 실행을 거부하고 공통 경로를 안내한다. 실행 당시 원본은 과거 archive에 남아 있다. 다른 역사적 도구 전체를 이식하지 않았다.

단위 외부 120초에 호스트 전송 여유 6초를 포함하고, 게스트는 최대 114초에서 work/삭제/최종 수집을 각각 finish−40/finish−10/finish로 제한한다. payload 15초는 start 응답 뒤가 아니라 요청 직전부터 계산한다. 준비 중 VM 생성 전에 이 시작점 보완과 전체 로컬 회귀를 재확인했다. 준비 마감은 재설정하지 않았다. `pre-vm-review.json`과 전달 helper 20개의 해시가 최신 통과 gate와 일치한다. 호스트·게스트 monotonic을 직접 비교하지 않았으며 별도 UTC/왕복 시각을 보존했다.

## 준비물 확보·재사용

호스트 전용 저장소는 `/Users/hyeon/Library/Caches/ontosary/s2-prepared-v1`이다. 관리자 uid 501, 디렉터리 0700/등록 파일 0400이며 worker에 노출하지 않는다. 기존 Lima cache를 변경하거나 cache-hit 메시지를 검증 근거로 사용하지 않았다. 실제 바이트를 검증한 로컬 파일 경로를 Lima에 전달했다.

| 공개 준비물 | 실제 바이트 | 최초 확보 | 두 번째 확인 |
| --- | ---: | ---: | ---: |
| Lima 2.3.0 Darwin arm64 | 50,317,981 | 15.412초 | 0.028초, 다운로드 0 |
| Ubuntu 26.04 arm64 20261016 | 940,373,504 | 348.257초 | 0.459초, 다운로드 0 |
| nerdctl-full 2.4.2 Linux arm64 | 270,513,423 | 76.595초 | 0.127초, 다운로드 0 |
| 고정 공개 레시피의 image archive | 445,026,816 | 같은 VM에서 build/export 후 등록 | 다운로드/빌드 0, 재해시·OCI 검증·import |

전체 환경 준비는 **590.353초**로 20분 이내다. image build/export는109.329초, 최초 archive 등록·검증·두 번째 lookup 합계는1.725초, 재import/identity 확인은2.899초였다. image 최초 등록·재사용 구간별 원시 시각은 `host/image-artifact.json`, build/import 명령 시각은 `host/stage-commands.jsonl`에 있다. 최초 공개 파일 3종 확보 합계는 440.264초, 재조회 합계는 0.614초다. 이미지 재검증을 위한 두 번째 VM이나 smoke container는 만들지 않았다. 준비 image build는 작업 단위와 별도로 1회다.

등록 metadata 포함 **1,706,234,324바이트(약 1.59GiB)**를 의도적으로 보관한다. 미완성 임시 항목은 0개다. `artifact-acquisitions.json`, `artifact-reuse.json`, `image-artifact.json`, `retained-artifact-verification.json`에 URL·정확한 SHA-256/크기·버전/플랫폼·빌드 입력·owner·실제 경로를 기록했다. 종료 전에 4파일의 바이트를 다시 해시했다. 대형 바이너리는 Git에 넣지 않았다.

이미지 target은 `sha256:64e3601e5f0cb3d8e48f0c1e3206ca952e276a5c16b7368b356cbaf3ba18293e`, archive SHA-256은 `c15c09d5fbdcdbc1641238bc7875dd8c2e732aa2f6919b98eaed8e595afc9d68`이다. config/rootfs chain과 실제 container snapshot 연결은 확인했다. **worker 시작 전 중단했으므로 실행 중 Node/CLI/bwrap 바이너리 identity 확인은 미실행**이다. 이미지 재사용 성공을 전체 실행 환경 준비 완료로 확대하지 않는다. 새 패키지 의존성은 추가하지 않았고 Python 표준 라이브러리와 기존 공개 빌드 레시피를 사용했다.

## 실제 결과와 중단 근거

| 최초 계획 | 실제 관찰 |
| --- | --- |
| 정상 1 | 등록/생성 1회, 전체 Spec 사전 비교 거부, start 0회, 자동 삭제·결과/next 차단 |
| 생성 후 의도한 사전 검사 실패 | 미실행. 정상 1의 예상 밖 실패를 이 단위의 통과로 세지 않음 |
| 시작 실패 | 미실행 |
| timeout/분리 자손 | 미실행 |
| 호스트 wrapper 사망 | 미실행 |
| 주입한 감독자 사망 | 미실행 |
| 정상 2/복구 뒤 격리 | 미실행 |
| 조건부 원래 1/후보 1 | 전제 미충족으로 모두 미실행 |
| 선택적인 실제 조회/삭제 오류 | 최초 계획에서 제외; 로컬 검증만 수행 |

분모는 **필수 7 중 시도 1, 기대 결과 통과 0**이다. 새 VM 1, 작업 container 생성 1/start 0, 후보 Spec/start/clone 관찰 0, 실제 Codex CLI/version/help 0, credential/login/provider/model/본 비교 각각 0이다.

고정 nerdctl은 hook 환경에 PATH를 추가한다. 기존 Spec에 중복 PATH와 검증되지 않은 systemd 변수가 있어 새 runtime 환경을 `HOME`, `LANG`으로 한정하고 절대 경로 명령을 사용했다. 실제 hook에는 중복 키나 systemd 변수가 없었고, 환경은 원래/후보 모두에 동일하게 적용할 계획이었다. 그러나 생성된 Spec에는 아래 **보안 설정 차이**가 남았다.

- `/process/apparmorProfile`: 기존 `nerdctl-default`, 실제는 필드 없음.
- `/materials`, `/probe`, `/home/runner/cli-state/config.toml`: 실제 mount options와 대응 annotation의 `rro`가 `ro`로 바뀜.

이는 허용 식별자 치환으로 지울 수 없다. 전체 diff를 `host/observed-spec-diff.log`와 guest archive의 `baseline-policy-verification.json`에 보존했다. AppArmor/rro의 실제 커널 적용 변화는 시작하지 않은 container에서 관찰한 것이 아니며, **created Spec의 할당 차이**다. PATH 제거가 도구/기능 탐지에 영향을 줬을 가능성은 추론이고 인과관계는 미확정이다. 환경을 다시 넓히거나 보안 flag를 바꾸는 재시도는 하지 않았다. [고정 hook 구현](https://github.com/containerd/nerdctl/blob/v2.4.2/pkg/cmd/container/create.go)과 [read-only mount 의미](https://github.com/containerd/nerdctl/blob/v2.4.2/docs/command-reference.md)를 다음 리뷰의 근거로 남긴다.

원래 두 Spec은 `host/prior-pair.json`과 과거 immutable archive에서 보존하고, 상속 환경 제거 기대값을 별도 기록했다. 새 원래/후보 두 실제 Spec은 없으며 새 actual Spec은 정상 1의 하나뿐이다. 다른 run/소유 밖 경로, 중복 env/mount, 추가 hook/명령/권한/seccomp, 중첩 mount 순서 변경은 부정 회귀로 거부한다. 독립 peer mount만 고정 destination 집합·중복 부재·모든 조상 순서 확인 뒤 정규화한다.

`normal-1-observed.json`의 outcome은 `supervisor-death`다. 이는 이번에 SIGKILL 사망을 주입했다는 뜻이 아니다. 사전 비교 예외로 service가 exit-code 실패한 것을 현재 종료기가 이 값으로 분류했고, 원인 `baseline-full-spec-difference`를 별도 보존했다. 이 분류의 세분화도 후속 리뷰 대상이다.

| 게스트 monotonic 시각 | 사건 |
| ---: | --- |
| 203.546065 | 소유 기록/마감 등록 |
| 203.962437 | create 요청 등록 |
| 204.327352 | 공통 종료 요청 |
| 204.400063 | container/task 부재 확인 뒤 removal 기록 |
| 204.589673 | systemd service inactive |
| 204.782506 | 단위 파일 제거·최종 봉인 |

전체 cgroup 종료·pending false·실제 container/task 부재를 확인했고 수집은 suppressed, next는 false로 유지했다. 과업 실패와 정리 성공을 구분한다. 이번 실제 실패 경로의 삭제 지연 문제는 재현하지 않았지만, 필수 7경로 전체가 검증된 것은 아니다.

## 검증·정리·감사

새 Python **56**, 기존 collector/cleanup **16**, 감사/deadline/package **44** — 중복 import 없이 **116개**가 통과했다. 로컬 fake runtime은 실제 CLI 진입점을 통해 조회/삭제 오류·pending·중복 정리·결과 차단을 검사했으며 실제 runtime 오류 복구의 증거로 세지 않았다. production/live 거부 1개는 기존 304개 테스트 안에 포함된 사례를 별도로 재확인한 것으로 전체 수에 더하지 않는다.

`pnpm check`는 타입 검사 통과 후 **300 통과/4 실패**다. 최초와 최종 실패 이름이 같으며 모두 기존 `/tmp/ontosary-vendure-preparation-20261108/vendure`의 필수 13파일 누락과 연결된다. 기존 cache를 복구/변경하거나 테스트를 skip하도록 바꾸지 않았다. 예제 build와 production/live 거부 검사는 별도 통과했다. 따라서 전체 필수 검증은 미완료이며 PR을 게시하되 병합하지 않는다.

VM은 UTC 06:12:07에 강제 중지·삭제됐다. 첫 host 정리 확인은 Lima의 stderr “인스턴스 없음” 경고가 stdout과 합쳐진 것을 비어 있지 않은 목록으로 오인해 실패했다. closing에서만 stdout/stderr를 분리하고 이미 삭제한 VM은 다시 삭제하지 않도록 보완했다. 두 번째 확인에서 exit 0/빈 stdout/소유 등록 경로 부재와 관련 프로세스 부재를 확인한 뒤 전용 host root를 제거했다. 실행/identity/정책 코드의 실패 후 수정·재시도는 없다. 빈 부모 slice·round observer·image·writable 경로는 소유 VM 폐기로 제거됐으며, VM 폐기를 앞선 단위의 정상 종료 증거로 대신하지 않았다. 준비물 4개와 저장소 잠금 파일만 의도적으로 남는다.

분석 snapshot **8개**, 명시적으로 등록한 closing **4개**(첫 정리 실패, 정리 완료, 검증, seal)를 구분한다. 미등록/위조/중복/누락 snapshot은 포장이 거부한다. 최종 index는 **126파일 / 15 archive / 내부 1175파일**을 포함한다. `verify_saved.py`는 입력 archive 27파일·전달 helper 20해시·게스트 증거 28파일과 전체 Spec diff/종료 순서를 오프라인 재현한다. 실행 코드의 pre-VM 보완, closing 전용 보완과 실제 전달본 hash를 별도로 남겼다. 과거 snapshot/index는 수정하지 않았다. 등록 전 개발용 회귀 로그도 보존하되8개 분석 snapshot의 재현 범위와 구분한다.

```sh
python3 experiments/domain-model/s2/trial/container/execution-lifecycle/verify_saved.py \
  --root experiments/domain-model/s2/verification/2026-11-14-execution-lifecycle
```

최종 실측은 **3005.752초**, 이전 실측 14,280.296826292초와 합계 **17286.049초**다. 이전 직렬화 상한 10초와 이번 최종 포장/문서 확정 상한 10초는 별도이며 정확한 시각·합산은 `host/cost.json`에 있다. 180분을 초과하지 않았다. 유료 비용 0, Git 게시 시간은 회차 종료 뒤 따로 기록하며 그 시간에 실험을 재개하지 않는다.

다음은 이 부분 결과의 독립 리뷰다. 최소 runtime 환경이 기존 AppArmor/rro를 보존할 수 있는지와 전체 lifecycle 7단위 검증 범위를 먼저 판단해야 한다. 자동 권한 완화·다른 backend·영구 VM·API/proxy·실자격 증명·모델·본 비교를 시작하지 않는다.
