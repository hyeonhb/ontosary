# S2 동일 후보 최소 실행 재검증 — 2026-11-10

**판정: smoke-passed.** 현재 Linux 이미지 target과 실제 컨테이너의 연결을 확인했고, 비특권 셸·Node 반복, workload exit7 전달, Codex version/help가 통과했다. 네 container와 VM/image/prefix/새 cache는 삭제했다. 이는 최소 실행 결과이며 **R11 unresolved·R12 기존 검증 범위·trialAuthorized:false·readyForTrial:false·results:null**을 유지한다. 실제 모델/provider/본 비교0회다. 이후 Vendure 준비·종료/수집 adapter·평가 작업은 시작하지 않았다.

Base: 최신 main `cb3c75df7075f03bf63acaf18da638d1c0b13c96`(지시 포함). 작업 브랜치 `codex/s2-container-smoke`; 최종 내용은 [manifest](../../experiments/domain-model/s2/verification/2026-11-10-container-smoke/manifest.json)의 재귀 hash와 이 보고서를 포함하는 PR head/merge로 식별한다. 자체 검토이며 독립 R11 승인과 구분한다.

## 이미지 연결과 수정

[nerdctl2.4.2 명령 문서](https://github.com/containerd/nerdctl/blob/v2.4.2/docs/command-reference.md#image-management)는 image ID가 target(index/manifest)의 OCI digest라고 명시한다. 이전 repo@digest 조회는 registry fallback으로 실패했고, 다음 호출은 Docker 호환 inspect의 config digest를 native image ID로 사용해 실패했다. 이번에는 재빌드 뒤 같은 endpoint `/run/containerd/containerd.sock`, namespace `default`에서 native 목록·native/Docker inspect를 모두 보존하고 **현재 target digest만** `create --pull=never`에 전달했다. 예전 digest는 재사용하지 않았다.

| 식별자 | 실제 값 |
| --- | --- |
| 정규화 이름/tag | `docker.io/library/ontosary-s2-smoke:20261110` |
| 실행 target(manifest) | `sha256:a0bdb967ba82f09eb3646daf81bdd4162fe33bd18a0253b08c468c48e0bdede5` |
| config digest | `sha256:35edd6a7243347e91578669c721c1deb52c2415272947cb185c0fc171ce6dd6a` |
| platform | Linux/arm64 |
| rootfs chain ID | `sha256:a69bf3c27762398127567b88451d993a079f4913cdcba2e8351efff72397abac` |
| 고정 base index | `sha256:4a4884e8a44826194dff92ba316264f392056cbe243dcc9fd3551e71cea02b90` |

OCI manifest 원문 hash→config 원문 hash→config의 diff IDs→누적 rootfs chain→container의 실제 snapshot parent를 연결했다. 각 container의 inspect `Image`도 target과 일치하며 create 전후 tag target 불변을 대조했다. `Config.Image` 문자열만으로 통과시킨 것이 아니다. **고정 환경에 대한 관리 metadata/실제 실행 smoke**이지 적대적 manager 변경을 방어하는 인증 체계는 아니다.

첫 준비 검사(v1)는 Docker 호환 `RootFS.Layers`가 개별 diff IDs와 같다고 가정해 assert에서 실패했다. worker 생성 전의 읽기 전용 검사 실패다. 저장한 config/manifest/native snapshot을 대조하니 해당 목록은 누적 chain IDs였다. 모든 prefix chain ID를 계산해 비교하도록 검증식 한 곳을 수정했고 v2 전체 smoke가 통과했다. **국소 수정·harness 재실행1회**, 이미지 재빌드/동일 workload 재시도0회다. 실패 원문·진단·당시 v1/v2 실행본은 [증거](../../experiments/domain-model/s2/verification/2026-11-10-container-smoke/)의 `raw/07-*`, `09-*`, `11-*`, `raw/implementation-at-execution/`에 남겼다. 여러 ID를 무작정 대입하지 않았다.

## 최소 실행 결과

| probe | container ID 앞12자리 | 결과 |
| --- | --- | --- |
| 셸 시작 표식/id + Node 고정 JSON | `5e535cd59ddb` | exit0, Node22.19.0·UID/GID1000 |
| 별도 workload exit7 | `2ba229ceb544` | 시작 표식 확인, wait manager exit0/반환7, inspect workload exit7 |
| 재빌드 없는 새 셸·Node 반복 | `c0c8d7cc23ad` | exit0, 다른 ID·같은 target/rootfs |
| 별도 Codex version/help | `4390e04f5fdc` | exit0, `codex-cli 0.167.0-alpha.3.2`, help 출력 |

전체 ID·명령/exit·시각·원문은 `raw/guest/smoke-run-v2/`에 있다. 각 probe는 create→불변 ID/metadata→start→wait/log/exit→remove 순서로 진행했고60초 이하의 단일 probe deadline을 적용했다. v2 전체 관리 명령은 약2.27초였다. 시작 표식 없는 종료는 성공으로 세지 않았다.

생성 spec과 실행 출력에서 UID/GID1000, effective capabilities0, no-new-privileges1, CPU `200000/100000`(2CPU), memory `4294967296`(4GiB), PID256을 확인했다. network none, 별도 PID/network namespace, readonly rootfs와64MiB `/tmp` tmpfs를 설정했다. host home·원본·관리 socket·credential·자료/evaluator bind mount는 없다. 이 설정 smoke를 네트워크/파일 공격 차단이나 모든 자손 종료의 증명으로 확대하지 않는다.

CLI는 container 내부의 새 빈 `/tmp/smoke-home/codex`와 HOME을 사용했고 `--version`, `--help`만 호출했다. 실제 사용자 CODEX_HOME을 복사하지 않았다. launcher SHA-256은 `e14fc83739c13c1074b12bd1acce4010c893c7f6fbfc1593b4a31d74cabb57af`, Linux native binary는 `e7f91e14eab4ba3a0f65047c1757b593409d4ce791ccb6ac65c67c970dfed76f`다. **gpt-6-astra/high config 인식·인증·모델 접근·실제 tool inventory·모델을 통한 셸 사용은 미검증**이다. 일반 셸과 CLI help의 성공을 이 경로의 성공으로 바꾸지 않는다.

## 시간·비용·정리

이번 회차는 UTC/단조 시계를 함께 기록했다. 단, 지시문의 ‘최초 읽기 전 기록’을 놓쳐 첫 읽기 직후13:23:00.806690에 시계를 기록했고 **60초를 추가 청구한13:22:00.806690을 보수적 시작**으로 사용했다. 이를 실측 최초 시작으로 표시하지 않는다. host/guest monotonic clock은 별개이며 각 명령 duration은 자기 clock 안에서 측정했다. 탐색 마감13:42:00, 전체 마감13:52:00을 넘기지 않았고13:29:57.805701에 성공 후 즉시 탐색을 끝냈다. 마지막 단계는 검증·정리·기록만 수행했다.

| 비용 | 이전 회차 | 이번 회차 | 누적/한계 |
| --- | --- | --- | --- |
| 환경 준비 청구 | 보수적1,251.264초 | 보수적477.002초 | 1,728.267초, 약28분48초 |
| 전체 작업(최종 검증까지) | 보수적1,713.452초 | 보수적875.500초(약14분36초) | 2,588.951초(약43분9초), raw/budget.json의 totalRoundSeconds/cumulativeRoundSeconds |
| 유료 비용 | 0 | 0 | 0 |
| 다운로드 관측 최소분 | archive1,261,204,908bytes + Node 약74.9MiB | 같은 세 archive1,261,204,908bytes + base/npm build 다운로드 | archive 합계2,522,409,816bytes; npm/프로토콜 전체 미계측 |
| 삭제 전 du 합계 | 10,262,836KiB | 9,891,284KiB(약9.43GiB) | 서로 다른 시점; APFS 중복 가능·peak/고유 물리 누적량 아님 |

이번 주요 단계: Lima download7.00초, VM 준비177.74초, build54.84초, 첫 검증0.44초, 수정 후 smoke2.27초, host check19.23초. 개별 진단/수정/대기/문서화도 전체 경과에서 제외하지 않는다. 이전 회차의 시작·전체 시간은 추정이 포함되며 정확한 최초 읽기 시간은 없었다. 이전/이번 모두 로그의 실측 명령 duration과 보수적 경과를 분리했다. **회차 사이 사용자 검토 대기 시간은 합산하지 않는다.** Git 게시/PR/merge 전달은 별도 기록하며 과거90분/4시간 잔여 예산을 재개하지 않았다.

원래 cache inventory에서 두 URL entry가 없음을 먼저 기록했다. 재생성 후 URL/hash를 확인해 이번에 생긴 두 entry만 삭제했다. 전용 VM stop→Stopped→delete→빈 목록과 hostagent PID10426 부재, task root/두 cache 부재를13:30:58.422985에 확인했다. 네 container는 각각 remove됐고 최종 container0개다. 보존 VM/image/volume/설치0개, 기존 cache 삭제0개, 공용 prune0회이며 추가 수동 복구 대상은 없다. `raw/cleanup.json`, `raw/ownership.json`, `raw/disk-downloads.json`을 참조한다. 이 정리는 R11의 detached/FD/wrapper 사망 반례 검증이 아니다.

## 회귀·다음 단계

`pnpm check`의15파일303테스트(skip0)·타입 검사·예제 build가 통과했다. 새 Python/shell 문법, 수집된 모든 container image/snapshot/exit 대응과 OCI byte hash, 재귀 증거 manifest를 확인했다. 제품 분석/fixture를 바꾸지 않아 지시대로 `pnpm experiment`와29제출 전체 교정은 반복하지 않았다. 호스트 회귀를 Linux 평가로 세지 않는다.

기존 Dockerfile/Lima·Node22.19.0·Codex0.167.0-alpha.3.2·TypeScript5.9.3과 base index를 유지했다. Vendure source/node_modules/평가기는 VM에 전달하지 않았다. 기존 정적 모델/자료·R12·production/live 거부·과거 증거는 보존했다. 새 manifest는 실제 준비 파일과 v1/v2 실행본·최종 smoke 도구·새 원시 증거를 포함하며 이전 manifest를 덮어쓰지 않는다.

다음은 **이번 smoke 결과 리뷰**다. R11의 전체 종료·불변 수집/별도 평가 단위와 Linux Vendure 재현에 필요한 범위·비용을 그 뒤 결정한다. 이번에 해당 adapter, 격리 공격/늦은 writer, Linux 타입/동작 평가, provider 연결 또는 본 비교를 수행하거나 승인하지 않았다.
