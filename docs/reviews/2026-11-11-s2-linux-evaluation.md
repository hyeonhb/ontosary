# S2 Linux Vendure 평가 재현 인계 — 2026-11-11

**linux-evaluation-reproduced, 독립 리뷰 대기.** 같은 Lima2.3.0/VZ·containerd/nerdctl2.4.2 후보에서 Linux 설치/common build, 원래 입력 검증, 새 실행별 평가/종료/수집/승인과 필수7단위를 확인했다. 이는 알려진 제출의 교정이다. 실제 CLI/model/provider/본 비교는0회이며 R11 unresolved·R12 기존 범위·production/live 거부·`trialAuthorized:false`, `readyForTrial:false`, `results:null`을 유지한다.

[지시](2026-11-11-s2-linux-evaluation-instructions.md), [구현](../../experiments/domain-model/s2/trial/container/linux-evaluation/), [원시 증거](../../experiments/domain-model/s2/verification/2026-11-11-linux-evaluation/). 기준은 최신 main `0760477`(PR43)이며 지시 기준 `d840669` 이후에는 지시/맥락 문서만 추가됐다. 다른 checkout은 변경하지 않았다. 최초 명령의 UTC `2026-11-11T11:01:10.452079+00:00`/host monotonic `147476.560882041`부터 읽기·설계·준비·대기·구현·검증·정리·보고를 모두 같은 회차에 포함했다.

## 필수7단위와 대조

아래는 경로 대응표 v2와 전체 입력 지문을 고정한 **최종 새7단위**다. 최초 경로 차이를 발견한2개와 전체 입력 지문을 추가하기 전 중간 baseline1개는 별도 분모로 보존했다. 모든 최종 단위는 새 container/cgroup/output, UID/GID1000, 새 환경 열기, runtime exit0, 전체 종료 확인, finalized와 systemd 성공 cleanup을 충족했다.

| 제출 / 방식 | run ID | 타입 / 동작 | 기대값 확인 | 외부 단위 시간 |
| --- | --- | --- | --- | ---: |
| baseline / complete-root 1 | `c61ec1982e8a` | passed / failed | 보존16/16·요구6/36·overall failed·binding true | 29.391s |
| reference / complete-root 1 | `3d00fe8ad333` | passed / passed | 52/52·overall passed·binding true | 28.937s |
| baseline / complete-root 2 | `b8aed72d4cc7` | passed / failed | 첫 baseline과 동일 | 37.958s |
| reference / complete-root 2 | `b77835e79d66` | passed / passed | 첫 reference와 동일 | 26.600s |
| helper-type-error / complete-root | `bdf544e23a77` | failed / not-run | TS2322, helper1행53열; overall failed | 23.493s |
| wrong-modal-order / complete-root | `db0897c598ec` | passed / failed | payload assertion에서8실패(44/52통과) | 22.347s |
| reference / explicit-baseline-delta | `0f9de71a1032` | passed / passed | complete-root와 동일 submissionId·52/52 | 22.764s |

baseline/reference complete-root4개는 공개 `publicCheck`도 passed·진단0·Program1,638파일로 private 타입 결과와 일치했다. 공개 타입 검사를 private 동작 oracle로 대체하지 않았다. 평가/공개 검사 자체의 job 시간은 약9.9~16.0초이며 위 외부 시간에는 입력 지문·등록·감독·종료·수집·승인·증거 복사도 포함한다. 결과 출력은 약2.4MB로128파일/16MiB 수집 한도 안에 원형 보존했다.

| 대조 | 결과 / 범위 |
| --- | --- |
| 기존 macOS ↔ Linux | 정확한9개 경로 대응 및4개 wall-time 필드·선언된 inputMode 차이 외 전체 필드 일치 |
| Linux baseline/reference 반복 | 전체 소스 manifest/ID, 입력/checked/executed 파일·hash, 진단, sourceMapping/binding, 사례별 status/이유/payload/modal/stream trace 일치 |
| complete-root ↔ delta | 동일 reference source/submissionId·타입·동작·52사례·payload/trace |
| 시작/종료 불변성 | 최종 실행 전후와 마지막의 환경·도구·제출109,157항목 지문 동일 |
| 정책/배포/평가기 | TASK52·모델12항목/16링크/승인0·84배포·baseline/model/bundle/evaluator ID 유지 |

`seven-comparison.json`과 `core-comparison-v2.json`이 자동 대조 결과다. raw 보고서와 실제 mount/native identity/종료/수집 records는 `guest-records.tar.gz`의 `linux-evaluation/runs/<run ID>/result/` 및 단위별 원래 `raw.tar.gz`에 있다. 원래 `evaluation/verify.ts`의 시간 제외 계약과 evaluator6모듈은 수정하지 않았다.

## Linux 준비와 lifecycle 변경

원본 cache는 읽기 전용으로 검증했다. inventory4,735파일과 고정 scope/lockfile에서 Linux 복사본을 만들고 기존 두 명령만 실행했다.

```sh
npm ci --ignore-scripts --no-audit --no-fund --workspace=@vendure/admin-ui --workspace=@vendure/common --include-workspace-root
npm run build --workspace=@vendure/common
```

Node22.19.0·npm10.9.3·TypeScript5.9.3·RxJS7.8.2, Linux arm64 kernel7.0.0-38-generic·systemd259를 실제 관측했다. 설치는2233packages이며 lock hash `36f9848d…`와 원본 파일은 설치 전후 동일했다. root/node_modules/common 산출물90,161항목 지문과 lock의 출처/integrity/license metadata를 남겼다. 호스트 Node/node_modules/APFS clone을 복사하지 않았고 새 프로젝트 의존성도 추가하지 않았다. Vendure와 기존 패키지의 라이선스는 그대로 유지한다.

원래 `openEnvironment()`가6,053개 입력 지문과 baseline 타입 passed·진단0을 확인했다. 역사적 Program 입력1,638파일을 무시하거나 refreeze하지 않았다. `typescript`는 이미지 `/opt/s2-tools/node_modules/typescript`로 명시적으로 ESM 해석하며 RxJS는 `/environment/node_modules/rxjs`를 읽는다. evaluatorId는 기존 `b7b6407b46b40d25e760f4e44e9a1839fddf8629c2c20c9d2c1430e760ec3aae`다.

현재 image target은 `sha256:a23653100c38a3568df64b5377c33e410c6a7c92e76fb36aab43a1e0eba15f04`, config는 `sha256:23fc228dfc45fcad50bf0538460826698fba92e68ca34cec2b27d269549560ae`다. OCI bytes→config/rootfs chain→각 container의 native snapshot parent/label과 실제 image를 대조했다. 과거 build의 target을 실행 ID로 재사용하지 않았다.

관리자 `assemble.mjs`는 기존 `variantDelta`로 완전 소스를 만든다. `readSubmission`은 실제 완전 트리를 읽고 누락을 baseline으로 복원하지 않는다. 전체 소스는 collector를 통과시키지 않는다. `linux_job.py`와 manager/supervisor의 작은 분기는 기존 `stop_confirm`/collector/cleanup을 재사용한다. Node PID1 자체가 평가하며 worker ready 표식·EOF·JSON 생성을 종료 권한으로 쓰지 않는다. 이미지의 `docker-entrypoint.sh`는 Node로 exec하며 `/proc`에서 실제 PID1/Name=node를 확인했다.

최초 create 직전180초, guest lease5초, 종료10초, 수집10초, RuntimeMaxSec210/TimeoutStart5/TimeoutStop12, 외부240초다. 기존 fixture의10/5/40/60초는 유지했다. native pending 요청이 불명확하면 빈 cgroup으로 완료시키지 않는다. UID/GID1000·cap drop ALL·NNP·network none·readonly root/cgroup·CPU2·4GiB·PID256·tmp64MiB와 실제 RO mount/EROFS를 확인했다. manager/socket/home/다른 출력은 mount하지 않는다. tools의 정확한 TypeScript 링크는 불변 이미지로만 연결하고 환경 dependency symlink는 환경 내부로 제한한다.

## 최초 실패와 수정

1. **원문 경로 대조 실패:** 최초 baseline `8e1cbfa9a6ce`와 reference `be4086d0a3ba`의 타입·동작·source identity는 같았지만 `checkedFiles` 정렬 및 `inputHashes` 이름에서6,588개 raw 차이가 나왔다. 고유 원인은 common 선언9개의 이름이었다. macOS `/tmp`의 canonical root는 `/private/tmp`이고 기존 evaluator는 모든 root 밖 파일을 `<typescript>/<basename>`으로 표기한다. Linux는 실제 `packages/common/lib/…`를 기록한다. 역사적 Program audit도 이9개 실제 경로와 같은 hash를 이미 기록하고 있었다.
2. **정확한 대응과 새 분모:** v1 raw 실패와 정책을 보존하고9개 file/hash·두 필드 위치만 대응하는 v2를 새 실행 전에 고정했다. 해시 차이·alias 충돌·중복은 거부한다. 중간 baseline `829ddb7e5d9c`는 환경만 지문 확인했던 실행으로 별도 보존하고, 도구/완전 소스를 더한 지문 뒤 최종7단위를 새로 실행했다. 원문 evaluator나 입력 hash를 바꾸지 않았다.
3. **검증 도구 국소 수정:** 호스트 시작 실패 테스트2개가 macOS의 `/proc` 부재로 오류여서 해당 Linux 관찰을 mock으로 제공했다. native argv 감사는 pinned 이미지의 `docker-entrypoint.sh` prefix를 포함하고 실제 Node PID1도 확인하도록 바로잡았다. 이는 actual worker 실패나 evaluator 수정이 아니다. 초기 호스트 도구3본은 실행 전 source hash snapshot이 없어 기록된 수정에서 재구성했다고 표시했다. 초기 비교기는 당시 정책/원문으로 재실행하여 최초 전체 출력 bytes까지 일치함을 확인했다. 실제 guest 실행본과 최종7단위의 code/input hash는 archive에 보존했다.
4. **정리 확인 반환값:** 모든17단위/image 제거 뒤 native image inspect가 missing image에도0/빈 출력을 반환해 첫 부재 assertion이 실패했다. 원시 실패를 보존하고 독립 empty image listing과 빈 inspect 출력의 동시 확인으로 보완했다. 재실행은 정리/증거 export만 이어갔으며 새 VM이나 평가를 시작하지 않았다.

## timeout·회귀와 정리

같은 job PID1 경로의 timeout `7ca7f2d67f77`은2초에 전체 종료되고 진단만 수집됐다.5초 지연 writer가 관찰 구간까지 쓰지 않았으며 source/수집본이 같았다. 다음 유한 control `5cc2eee10641`에서는 writer가 실제 쓰고 정상 종료했으며 새 출력 baseline은 비어 있었다. 이2개는7평가 단위와 별도다.

공유 경로는 normal `5e60f7315a2d`, timeout `18337cad4718`, wrapper `65f07b2af18a`, supervisor `9663965c4f93`, publish-supervisor `b24131f5093a`를 각1회 재검증했다. 정상/timeout/wrapper의 늦은 쓰기 없음, 감독자 사망의 차단, 공개 후 실패의 quarantine·next 거부/명시적 복구를 확인했다. 이전25개 전체 반복으로 표현하지 않는다.

호스트 검증은 `pnpm check`(304tests·타입 검사·예제 build), `pnpm s2:build`, 기존 collector13+cleanup3, 새 job/대조10회귀다. 실제 교정 receipt의 production 수집/평가/live 승격은 모두 거부됐다. `pnpm experiment`는 제품 분석 의미를 바꾸지 않아 실행하지 않았다.

등록 단위는 최종7+최초/중간3+job probe2+공유 regression5=**17**이다. 별도 준비 container4개도 제거됐다. 각 등록 단위의 pending/종료/cleanup을 확인한 뒤 container/task/unit/slice/image를 제거했다. VM 삭제를 개별 종료 증거로 대신하지 않았다. VM·소유 prefix/process와 이번에 새로 생성한 두 URL/hash 확인 cache leaf도 부재를 확인했다. shared prune은 사용하지 않았고 원본 cache4,735파일·scope/lock와 기존 기록을 보존했다.

## 비용과 증거 재현

최초 시계 누락은 없다. 환경 확보는45분, 새 핵심 대조는90분, 필수 실행/회귀는150분, 검사·정리·증거·보고는180분 안이다. [비용 원장](../../experiments/domain-model/s2/verification/2026-11-11-linux-evaluation/cost.json)은 이전 회차·이번·누적과 세부 계측 범위를 분리한다. host/guest 시간은 각 clock domain 안에서만 차감하며 새로운 유료 비용0, 후보1/VM준비1회다. Git 전달 시간은 이후 별도다.

<!-- COST_TABLE -->
| 구분 | 이전 누적 | 이번 회차 | 새 누적 |
| --- | ---: | ---: | ---: |
| 환경 보수 청구 | 2576.144s | 1164.585s | 3740.729s |
| 전체 회차(이전 추정 포함) | 6209.386s | 2710.783s | 8920.169s |

이번 환경 청구는 최초 시계부터 최종 검증 첫 단위 시작까지로 읽기/설계·초기3개 실행·경로 진단도 포함한 보수적 값이다. 직접 계측한 VM/설치/조립 준비 명령 합계는357.802s이며 전체 wall과 중복해 더하지 않는다. 원래 환경 열기 642.343s, 핵심 대조 1293.673s, 필수 실행/회귀 1610.321s에 각각 확보했다. 최종 시각은 `2026-11-11T11:46:21.152162+00:00`다.
<!-- END_COST_TABLE -->

`evidence-index.json`의 재귀 파일 hash와 archive-member hash를 확인하고 `guest-records.tar.gz`를 별도 임시 디렉터리에 풀면 원문 evaluator 출력, runtime/전체 종료/수집/cleanup, full 입력 지문, 의존성 metadata, 실제 guest Python/JS/계약 자료를 볼 수 있다. 호스트 helpers/초기 실행본과 raw 단위 archive도 보존했다. 원본 inventory 전체 전달 archive는 중복 공개 소스이므로 커밋하지 않고 전체 member hash·전달 archive hash·고정 revision/재구성 절차를 보존한다. node_modules/전체 VM/비밀은 포함하지 않는다.

## 후속 미검증

RuntimeMaxSec 실제 도달, 불명확 create 중 supervisor 사망의 실제 주입은 여전히 미검증이다. 새 create/start timeout은 호스트 대역에서 pending 유지/종료 거부를 확인한 것이며 실제 runtime fault 주입으로 표현하지 않는다. 일반 agent helper/도구 inventory·세션/전역 지시·인증/provider/네트워크·usage 실측·C 사람 의미 동등성은 별도다. 임의 agent 소스 전체 수집기, 전체 Angular/server 평가, H-O/H-F 효용도 이번 결과가 입증하지 않는다. 이번은 결과 리뷰 인계에서 멈춘다.
