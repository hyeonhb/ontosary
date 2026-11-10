# S2 fixture 전체 종료·수집 경계 결과 — 2026-11-11

실행과 마무리는 KST2026-11-10~11에 걸쳤다. 아래 UTC 시각은2026-11-10이며 증거/보고 날짜는 최종 동결일인11일이다.

## 결론과 범위

**fixture-boundary-passed, 독립 리뷰 대기.** [개발 지시](2026-11-10-s2-lifecycle-fixture-instructions.md)의 필수24개와 공개 직후 감독자 사망1개, 최종25개 실행을 통과했다. 정상·timeout·호스트 래퍼 사망은 각각 새 단위2회이며, 감독자 사망/관리 오류·유한 자손 경쟁·수집 거부·읽기 전용 소비를 포함한다. 개발 중 실패와 중간 성공도 보존했고 총83개 등록 단위의 정리를 확인했다. 동일 후보를 두 번 준비했으며 최소 환경 확인용 컨테이너2개는 별도다.

이는 선택한 Lima2.3.0/VZ + containerd/nerdctl2.4.2의 알려진 셸·Node fixture 결과다. **R11 unresolved**, R12 기존 판정·production/live 거부·`trialAuthorized:false`·`readyForTrial:false`·`results:null`을 유지한다. Vendure 준비/평가, 실제 CLI version/help/도구 세션, 인증/provider, 모델 호출, 본 비교는 이번에 실행하지 않았다. 새 라이브러리·후보·호스트 관리자 권한·전역 서비스 변경·유료 비용은0이다.

[구현](../../experiments/domain-model/s2/trial/container/lifecycle/), [증거 manifest](../../experiments/domain-model/s2/verification/2026-11-11-lifecycle-fixture/manifest.json), [최종25개](../../experiments/domain-model/s2/verification/2026-11-11-lifecycle-fixture/selected.json), [지연 실측](../../experiments/domain-model/s2/verification/2026-11-11-lifecycle-fixture/metrics.json)을 함께 읽는다. `guest-initial.tar.gz`에는 최초58개, `guest-final.tar.gz`에는 수정 후25개 manager 원시 기록과 fixture 결과가 있고, `executed-code.tar.gz`에는 당시 v1~v14 배포본과 host helper·최종 도구·Dockerfile/YAML이 있다. archive 내부 일반 파일별 hash도 manifest에 포함한다. 큰 반복 로그는 gzip으로 무손실 보존한다.

## 필수 표 결과

| 묶음 | 최종 분모 | 결과·근거 |
| --- | ---: | --- |
| 단순 exit0 / nonzero | 2 | 각각0/7 보존, nonzero는 diagnostic |
| setsid·손자 writer 정상 종료 | 2/2 | 주 작업 exit0 후에도 실제 writer FD/별도 session을 확인하고 parent slice 전체 종료 |
| timeout·상속 pipe·열린 FD | 2/2 | 5초 deadline, stdout EOF에 의존하지 않고 종료, diagnostic |
| 호스트 wrapper SIGKILL | 2/2 | ready/실제 쓰기 후 SIGKILL, host exit -9, 반복 heartbeat 중단·guest lease 만료, diagnostic |
| supervisor SIGKILL | 1 | 독립 ExecStopPost가 종료 확인, blocked·결과 없음·다음 실행 거부 |
| kill 실패 / 상태 조회 오류 | 2 | ready 후 주입, 독립 cleanup 성공 후에도 blocked 유지·명시적 manager recovery 전 next 거부 |
| kill 전 유한 대조 | 1 | 7초 예정 LATE 쓰기가 실제 발생, 약8초 주 작업 종료까지 관찰 |
| 유한 fork 경쟁 / 중복 cleanup | 1 | 최대8개 생성 시도 중6개 쓰기 표식 관측, cleanup3회(자동1+중복2), finalize1회·상태 역행/재시작 없음 |
| symlink/hardlink/FIFO/socket/device | 5 | 종류별 명시적 거부, 최종/부분 staging 없음. device는 manager가 준비한 음성 fixture |
| 파일128 / 16MiB / 깊이16 초과 | 3 | 각각 별도 거부, 정상 결과로 잘라내지 않음 |
| 복사 도중 실패 / 로그1MiB 초과 | 2 | 부분 공개 없음, 로그 초과를 blocked로 기록 |
| 읽기 전용 결과 소비 | 1 | 같은 lifecycle 사용, 읽기 성공·실제 ro mount/쓰기 EROFS, 이전 결과 hash 유지 |
| 공개 직후 감독자 사망 | 추가1 | 실제 SIGKILL, 공개 결과 격리·blocked 유지·next 거부 |
| 접근·수집 정확성 | 위25개 공통 | UID/GID·cap/NNP·cgroup·mount·canary, 전체 manifest/hash·추가/수정/삭제·auxiliary 독립 대조 |

최종25개는 모두 보완된 v14와 새 VM/image에서 실행했다. 최초 VM의 필수24개 대조 후 최종 코드 검토에서 공개 직후 실패 경로를 발견해, 같은 후보·버전·원래 마감 안에서 수정/재검증했다. 최초58개 실행은 개발·실패 증거로 보존하고 최종 분모와 분리했다. 최초 실패/증거 부족8개 등록 실행 및 감사 실패1회도 보존했다.

## 정상·timeout·사망 흐름과 실제 시각

manager가 run ID·전용 경로·persistent slice inode를 먼저 등록하고, supervisor 준비와 첫 guest 수신 heartbeat를 확인한 뒤 container를 시작한다. supervisor는 `system.slice`, worker는 `ontosary.slice/ontosary-<id>.slice` 아래의 runtime scope에 있다. 실제 PID·NSpid·NSpgid/NSsid·cgroup namespace·열린 FD/pipe를 기록했다. parent slice는 runtime 자식 scope가 지워진 뒤에도 유지된다.

정상 주 작업은 별도 exec process다. container PID1을 짧은 holding process로 두어 주 작업 exit0가 남은 손자 종료를 대신하지 않게 했다. admission 닫기 → parent `cgroup.kill` → 계층 전체 `populated=0` → STOPPED runtime task 삭제/부재 및 pending request 없음 → matching termination record → 전체 수집/검증/원자 rename 순서다. 일반 파일/디렉터리만 no-follow dir FD로 순차 복사하고 baseline을 복구하지 않는다. 결과의 `fixtureOnly:true`, `validSubmission:false`는 기존 evaluator 권한으로 승격되지 않는다.

최종25개에서 종료 요청→확인은 **0.0663~0.1024초**, 수집은 **0.0014~0.0033초**였다. timeout 요청은 deadline 뒤0.0052/0.0069초, wrapper 종료 요청은 마지막 guest heartbeat 뒤5.0078/5.0086초였다. 따라서 deadline 순간의 snapshot이라는 주장은 하지 않는다. `metrics.json`은 같은 guest monotonic domain의 차이를 사용한다.

wrapper driver는 동기식으로1초 heartbeat를 보낸다. SIGKILL 뒤 반복 sender가 남지 않았고 guest lease의 마지막 수신 이후5초에 종료했다. 원래10초 task deadline보다 먼저다. supervisor SIGKILL은 준비·실제 writer 쓰기 후 주입했으며, 별도 cleanup이 결과를 발급하지 않고 종료/next 차단을 수행했다. host injection UTC와 guest cleanup UTC 차이는 약0.149초지만 **서로 다른 clock domain의 대략적 대조**이고 정밀 단조 지연값으로 취급하지 않는다.

핵심·사망/관리 오류·race에서 종료 확인 후 ready+8초까지 관찰했다. writer는 시작7초 후 늦은 쓰기를 예약하므로 그 시점을 넘겼으며 source/result hash가 유지되고 late 파일이 없었다. kill을 미룬 유한 대조에서는 LATE가 나타났다. 이 관찰은 `populated=0`·배치·권한 증거를 보완하며 대신하지 않는다.

공개 직후 감독자가 죽으면 `result`를 manager 전용 `quarantined-result`로 이동하고 상태를 blocked로 남긴다. 이 경로는 소비 대상으로 승인되지 않는다. 수동 중복 cleanup은 아직 systemd 성공 종료가 확인되지 않았으면 admission을 열지 않으며, 후속 ExecStopPost가 성공/실패를 확정한다. 실제 공개 직후 SIGKILL과 별도3개 host 회귀로 확인했다.

## 구현 선택과 실패·수정

- **v1**: nerdctl mount의 `rw` 표기가 parser에서 거부됐다. 완료된 exit1 pre-dispatch 오류인데 createPending을 남긴 bookkeeping도 확인했다. 해당 오류 원문·container 부재·빈 parent를 대조해 별도 manager reconciliation을 기록했다. 불명확한 runtime 요청의 복구로 일반화하지 않는다.
- **v2**: native container의 `Image`가 digest가 아니라 이름인 것을 검증식이 잘못 해석했다. native image 재조회→현재 target/config/chain, container digest label/snapshot parent로 연결했다.
- **v3**: 죽은 worker의 STOPPED task metadata를 살아 있는 task로 판정했다. kernel empty 및 runtime stopped를 먼저 확인하고 그 task 기록을 삭제·재조회하도록 수정했다.
- **v4**: 빠른 정상 종료에서 worker ready 기록을 manager가 놓쳤다. exec 종료 확인 직전에도 ready/실제 writer 배치를 캡처하도록 수정했다. v5에서 정상·timeout의 종료/수집 핵심 경로를 처음 확보했다.
- **v6**: nerdctl exec가 worker exit7을 CLI exit1로 전달했다. 같은 containerd의 `ctr tasks exec`로 변경해 실제 exit7을 보존했다. worker 로그 문구를 종료 권한으로 파싱하지 않는다.
- **v7 — 실제 경계 실패**: supervisor SIGKILL 후 남은 exec client 때문에 ExecStopPost가 약12초 지연되어 LATE가 발생했다. `KillSignal=SIGKILL`로 service 내 helper를 즉시 끝내도록 수정했다. 이후 동일7초 writer를 유지한 supervisor 사망 사례가 통과했다. 최초 늦은 쓰기·journal은 보존했다.
- **v8**: 관리 오류를10초 task deadline에 주입해7초 쓰기가 먼저 발생했다. 이를 성공으로 해석하지 않고 준비/실제 쓰기 직후 오류를 주입하도록 fixture를 바로잡았다.
- **v9**: 로그 fixture의 async return 뒤 강제 exit가 출력 flush를 잘라 실제 출력은64KiB였다. overflow를 검사한 실행으로 세지 않았다. ready 뒤1MiB+32bytes를 쓰고 기다리는 v10에서 초과 거부를 확인했다.
- **감사 수정**: OCI의 재귀 read-only 옵션 `rro`를 `ro`만 허용한 검증식이 거부했다. 실제 mountinfo `ro`, 쓰기 EROFS와 함께 `rro`도 확인하도록 수정했다. consumer 재실행으로 결과를 바꾸지 않았다.

최초 image target은 `sha256:1a06fe32cc6768b5e7819b6a352d6cbd64269327c746f279524030d5550db917`, 최종 재준비 target은 `sha256:5d3979defc10e8adb7e64ec899a41b104242d1c862a1e54bf9f0819d31923223`, 최종 config는 `sha256:3be71ba17e86ad99071aca5ce2417ff498aac540fe3e0926cd5435cc11fddcee`다. 기존 base index는 유지했다. OCI 원문 hash와 현재 image/rootfs chain→실제 container 대응을 검증했으며 과거 build digest를 상수로 사용하지 않았다.

기술 근거는 [cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html), [nerdctl2.4.2 명령](https://github.com/containerd/nerdctl/blob/v2.4.2/docs/command-reference.md), [systemd service](https://github.com/systemd/systemd/blob/main/man/systemd.service.xml), [containerd ctr exec](https://github.com/containerd/containerd/blob/main/cmd/ctr/commands/tasks/exec.go)다. 문서 지원과 이번 guest 관찰을 구분했다.

## 비용·잔존 자원·회귀

첫 명령에서 읽기 전에 UTC **14:04:42.398901**, host monotonic **137627.307170416**을 기록했다. 지시의 기간을 읽은 직후 이 최초 시각에 연결해 절대 마감14:24:42 /15:34:42 /16:34:42 /17:04:42를 계산했다. 즉 **최초 시계는 읽기 전**, 절대 마감 산출은 지시 읽기 직후이며 이를 숨기거나 시작을 재설정하지 않았다. host/guest monotonic은 직접 빼지 않는다.

환경 최소 실행 완료14:14:40.706584, **598.322초/20분**. 정상·timeout 핵심 경로는14:24:22.489935에 확인했다(90분 상한 안). 최초 필수 표 감사는14:38:17.932216에 통과했지만 마무리 코드 검토에서 공개 직후 사망 경로를 발견했다. 동일 후보를14:49:11.205127~14:53:20.754331에 재준비(249.555초)했고, 최종25개 감사는14:56:52.471865에 통과했다. 그 뒤 새 probe 없이 회귀·정리·증거·보고만 수행했다. 최초20분 환경 재현 조건은598.322초에 충족했고 추가 준비 비용은 숨기지 않고 환경/전체 합계에 더했다. 전체 회차 최종 시각/실측 초와 합산은 [cost.json](../../experiments/domain-model/s2/verification/2026-11-11-lifecycle-fixture/cost.json)에 기록한다.

| 구간 | 타당성 회차 | smoke 회차 | 이번 회차 | 합산 |
| --- | ---: | ---: | ---: | ---: |
| 환경 | 1,251.264초 | 477.002초 | 847.877초(598.322+249.555) | 2,576.144초 |
| 전체 | 1,713.452초 | 875.500초 | cost.json의 measuredRoundSeconds | 이전2,588.951초 + 이번 실측 |
| 신규 유료 비용 | 0 | 0 | 0 | 0 |

이전 두 회차 값에는 최초 읽기 추정 구간이 포함되고, 표시한 소수 반올림 합과 raw 합에0.001초 차이가 있다. 이번은 최초 시계부터 읽기·구현·대기·실패·검증·정리·보고를 포함한다. 회차 사이 사용자 검토 대기와 Git 게시/PR/merge 전달은 별도다. 이전90분/4시간 잔여 예산을 재개하지 않았다.

두 VM의83개 등록 단위 모두 empty parent·runtime stopped를 재확인한 뒤 container와 임시 service/slice를 제거했다. owned image를 제거하고 VM을 stop/delete했으며 hostagent·VM directory·작업 prefix 부재를 확인했다. URL/hash/시작 전 부재를 대조한 각 준비에서 시작 전 부재를 확인한 Lima cache2개씩만 삭제했고 공용 prune이나 기존 cache 삭제는 하지 않았다. 잔존 runtime 자원0, 추가 복구 명령 없음이다. ignored work의 작은 증거 복사본은 보존한다. VM 삭제를 개별 단위 종료의 증명으로 사용하지 않았다.

`pnpm check`:16파일 **304테스트(skip0)**·타입 검사·예제 build 통과. collector13개와 publication/cleanup3개, **Python 회귀16개** 통과, `pnpm s2:build` 통과. 실제 발급 fixture로 기존 collection/evaluation/live 거부를 확인했다. 제품 분석/기존 과업 의미를 변경하지 않아 `pnpm experiment`와29제출 전체 교정은 지시대로 반복하지 않았다. 제품 코어·모델·B/C·기존 실행 manifest·과거 원시 증거는 수정하지 않았다.

## 다음 미검증 범위

다음은 이 fixture 결과의 독립 리뷰다. 악성 kernel exploit, 모든 I/O 형태·네트워크 격리 전체, RuntimeMaxSec 도달/불명확한 생성 요청 중 감독자 사망의 실제 fault injection, 실제 CLI 도구 inventory/인증/provider, Linux Vendure 설치·빌드/평가 재현은 검증했다고 주장하지 않는다. 불명확한 pending request는 코드에서 차단하며, 해당 실패 경로의 실제 주입은 이번 필수 표와 별개로 남긴다.

R11 전체 해결이나 본 비교 준비 완료가 아니다. 이 경계 코드의 성공은 모델의 agent 효용 또는 FCA 기여 결과도 아니다. 후속 범위·비용은 리뷰 뒤 결정하고 이번 회차에서 더 진행하지 않는다.
