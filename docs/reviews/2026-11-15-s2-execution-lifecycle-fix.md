# S2 실행 수명주기 R13–R15 보완 인계

2026-11-15. **부분 구현·blocked/inconclusive·소유 실행 자원 정리 완료**다. [보완 지시](2026-11-14-s2-execution-lifecycle-fix-instructions.md)에 따라 PR #54의 `f6fc386`을 이어 최신 main `067c028`을 병합했다. ADR-048/049와 과거 증거를 보존했다. 이 결과는 독립 리뷰에 제출하며 구현 PR을 병합하지 않는다.

이미지 재사용은 실제 새 VM에서 build/download 0회로 확인했다. 첫 정상 단위는 시작 전 전체 Spec 비교를 지나 start 1회·exit 0·container 삭제까지 진행했지만, service 비활성 시각을 확인하지 못해 봉인에 실패하고 결과가 철회됐다. 뒤이은 export도 전달된 메타데이터의 관리자 소유권 검사에서 실패했다. **필수 7단위 중 시도 1·기대 결과 통과 0**이며 나머지 6개, 정책 pair, 추가 smoke, 같은 단위 재시도는 실행하지 않았다. 실제 실패 뒤 실행 코드를 수정하지 않았다.

## 판정과 수정 위치

| 항목 | 수정·로컬 검증 | 실제 관찰 및 판정 |
| --- | --- | --- |
| R13 고정 runtime 환경 | [identity.py](../../experiments/domain-model/s2/trial/container/execution-lifecycle/identity.py), [runtime_env.py](../../experiments/domain-model/s2/trial/container/execution-lifecycle/runtime_env.py), [guest.py](../../experiments/domain-model/s2/trial/container/execution-lifecycle/guest.py), 공유 image 식별 호출에 명시 env/deadline 전달. 실제 subprocess 경계·hook 배열·보안 필드 부정 회귀 통과 | 도구 검사 성공 응답과 start 1회는 확인됐다. frozen 실행 코드는 전체 Spec 비교 실패 시 시작하지 않으므로 이번에는 해당 gate를 통과한 관찰이다. 다만 최종 export 실패로 **실제 도구 해석 상세·원본 native Spec·치환/전체 diff가 보존되지 않았다. 재검증 가능한 증거가 부족하므로 부분 완료**다. |
| R14 빌드 전 조회 | [image_cache.py](../../experiments/domain-model/s2/trial/container/execution-lifecycle/image_cache.py), [round.py](../../experiments/domain-model/s2/trial/container/execution-lifecycle/round.py). 실제 prepare 진입점의 별도 회차 miss→hit, hit의 build/save/download producer 금지, probe 변경·recipe/base/tool 변경, 손상·부분 등록·import 불일치 회귀 | 옛 입력 증거와 archive를 검증한 별도 연결 기록을 추가했고 기존 manifest는 불변이다. 새 VM import의 target/config/chain 일치가 호스트 명령 출력에 남았다. **이 재사용 범위는 검증 완료**이며 새로운 빌드의 재현성을 주장하지 않는다. |
| R15 안전한 export | [exporter.py](../../experiments/domain-model/s2/trial/container/execution-lifecycle/exporter.py), 공유 [collector.py](../../experiments/domain-model/s2/trial/container/lifecycle/collector.py). collector→실제 guest.export→archive 회귀, 거부/철회/불명확 상태의 원본 미접근·FD 읽기·상한·원자 공개 검증 | 실제 결과는 봉인 실패 뒤 suppressed였다. export가 `file-owner:image-export.json`으로 거부되어 **최종 archive 0개**다. 거부된 원본을 포함한 성공 archive는 없지만 허용 진단도 함께 보존하지 못했다. **부분 완료**이며 실제 7단위 export 검증은 미완료다. |

R11 unresolved, R12 기존 검증 범위, production/live 거부를 유지한다. `fixtureOnly=true`, `validSubmission=false`, `trialAuthorized=false`, `readyForTrial=false`, `results=null`이며 실제 credential·로그인/갱신·provider/model·본 비교는 각각 0회다.

## 준비·환경·비교

최초 명령 시각은 `2026-11-15T10:22:53.745680Z`, host monotonic `203713.853282791`이다. 첫 명령 값을 시작 ledger 파일에는 10:27:53Z에 옮겼으며 비용은 원래 최초 시각부터 센다. 최초 tracked inventory 3,090파일과 원격/브랜치/깨끗한 작업 트리를 기록했다. 새 작업 경로는 `work/s2-execution-lifecycle-fix-20261115`, VM 경로는 `/tmp/ontosary-s2-execution-lifecycle-fix-20261115`다. 60/100/150/180분 마감, VM 1개·build 최대 1회·실제 단위 최대 7개·유료 0을 계획에 고정했다. 준비 진입 시 환경 마감은 `2026-11-15T11:01:36.448610Z`로 한 번만 정했다.

수정 전 두 재현은 가짜 외부 명령/공개 임시 canary로 수행했다. `before-cache.json`은 이미지 조회 전 무조건 guest build 진입, `before-export.json`은 collector가 거부한 hardlink 내용의 export 포함을 기록한다. 과거 스크립트를 바꾸지 않았다. 개발 중 추가한 metadata 용량 회귀의 첫 기대값은 제한 숫자의 직렬화 길이 변화 때문에 실패했고 테스트 예산을 수정했다. 그 실패 로그도 보존했다. 초기 재현/직접 개발 테스트 로그는 formal snapshot 등록 전 자료이며 실행 전 코드 snapshot이 없는 개발 테스트를 등록된 분석 실행으로 세지 않는다. 실제 실행 이후 보안 계약이나 기대값을 넓힌 수정은 없다.

Runtime env는 순서까지 `HOME=/root`, `LANG=C.UTF-8`, `PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`으로 고정했다. nerdctl 2.4.2 hook은 그 세 항목 뒤에 `PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/sbin:/sbin`이 정확히 한 번 추가되는 배열만 허용한다. process env의 일반 중복 거부, hook 명령/위치/개수, 소유 run/mount 식별자, AppArmor/rro/seccomp/capability/NNP/network/resource 전체 비교는 유지한다. 옛 기대 환경의 변환은 별도로 기록하며 원본을 바꾸지 않는다. 과거 PATH 없는 실패는 기존 날짜의 증거 그대로다.

새 VM 준비 코드는 같은 env에서 실제 경로/소유권, nerdctl/containerd/runc 버전, `runc features`, AppArmor parser/package/help/활성 여부와 `aa-exec true`를 검사하고 전달된 모든 입력 hash를 검증한다. 호스트에는 `toolsVerified=true`, kernel `7.0.0-38-generic` 응답이 남았지만 세부 JSON은 실패한 guest export에 의존해 유실됐다. 따라서 이번 자료만으로 이전 raw Spec과 새 raw Spec의 독립 전체 대조를 재현할 수 없다.

## 이미지 재사용 근거와 비용

입력 key 스키마는 `s2-image-input-v1`, JSON은 key 정렬·compact separator로 직렬화해 SHA-256을 계산한다. Dockerfile/context 실제 바이트, `BASE_IMAGE` digest, platform, nerdctl/containerd/runc 버전과 전체 도구 bundle digest가 입력이다. 결과 archive SHA·size·image identity와 실행별 round/probe/fixture/policy는 lookup key에 넣지 않는다. 이번 key는 `4bc8ef40b201ccadb928faec44031c95d15e0831716cea76f24d9c41f33e02a4`다.

옛 `inputs.tar.gz`의 build/Dockerfile 단일 context, transfer hash, 실제 build 명령, 버전 출력, 도구 bundle, 전체 과거 evidence index와 저장 archive를 검증한 후 `.image-key-<key>.json` 연결 기록 2,634바이트를 추가했다. 옛 manifest/데이터 4개의 SHA·크기는 작업 전후 일치한다. 검증 실패는 miss로 위장하지 않는다. 레시피의 apt/npm 외부 조회가 완전히 고정되지 않았으므로 같은 입력의 새 빌드가 항상 동일 바이트라는 주장은 하지 않는다.

| 실제 준비 | 값 |
| --- | --- |
| 공개 artifact 네트워크 다운로드 / 이미지 build / save | 0 / 0 / 0 |
| 새 VM / 이미지 import | 1 / 1 |
| 환경 진입부터 완료 | 52.764초 (prepare 명령 자체 39.831초) |
| 저장 archive SHA-256 | `c15c09d5fbdcdbc1641238bc7875dd8c2e732aa2f6919b98eaed8e595afc9d68` |
| archive 크기 | 445,026,816바이트 |
| target / config | `64e3601e5f0cb3d8e48f0c1e3206ca952e276a5c16b7368b356cbaf3ba18293e` / `e3ab6ef0491100a63b97719f8dd7e7c12e682485b887eb2a2421c85963508f6d` |
| rootfs chain | `3b5f9851906e2c4005a4f4ee0055626d8d719e61e060244b6f96e6a69cf8f7ee` |
| 보관량 | 1,706,236,958바이트, 10GiB 이내. 기존 공개 4개+새 연결 metadata만 유지 |

`image-artifact.json`에는 입력/출력 binding과 archive 검증, `prepare-…-command-14.log`에는 새 VM의 actual image와 import 확인 응답이 있다. `retained-store-verification.json`은 과거 manifest/바이트 불변과 임시 항목 0개를 확인한다. 기존 Lima 공유 cache를 재설치하거나 Vendure 입력을 수정하지 않았다.

## 실제 단위와 실패

| 계획 단위 | 실제 결과 |
| --- | --- |
| 정상 1 | create 1/start 1/exec 0, exit 0. 종료·task/container 부재와 삭제 확인. collection 이후 service 비활성 시각 확인 실패로 결과 철회. 기대 결과 실패 |
| 생성 후 사전 검사 실패 | 미실행 |
| 시작 실패 | 미실행 |
| timeout | 미실행 |
| wrapper 사망 | 미실행 |
| supervisor 사망 | 미실행 |
| 정상 2 | 미실행 |

Run `9c827ef34718`, container `5d4953c672f332f1976011f1e27fe32c98713170b5bd9185efef2551143d57bf`다. 보존된 호스트 관찰의 guest monotonic은 등록 58.591774 → stop 요청 59.967367 → 삭제 60.157990 → collection 시작 60.313361/완료 60.315306 → finalizer 완료 60.316674다. 등록 후 삭제 **1.566초**, 호스트 실패 판독 **2.336초**다. create/start/exec pending은 모두 false지만 `serviceInactiveConfirmed`와 단위 봉인 증거가 없고 `cleanupDone=false`, `collectionStatus=suppressed`, `discardVM=true`로 전환됐다. 이를 정상 완료나 120초 계약 통과로 세지 않는다.

첫 예상 밖 실패는 `seal:inactive-deadline-unconfirmed`다. 코드상 systemd의 `InactiveEnterTimestampMonotonic`이 0/누락 또는 마감 밖이면 발생한다. 원시 `systemctl show` 출력이 export 실패로 남지 않았으므로 특정 값이나 unit GC를 원인으로 확정할 수 없다. unit 상태 보존/조회 시점은 다음 리뷰 대상이며 이번에 변경·재시도하지 않았다. 봉인 실패 후 수집 결과는 quarantined 처리돼 유효 결과로 재사용하지 않는다. 실제 worker 관찰 파일도 최종 인계에는 없으므로 binary SHA/허용 읽기·쓰기 전체 검증을 독립 재현했다고 확대하지 않는다.

## export 계약과 남은 결함

공유 FD reader는 no-follow·regular/nlink 1·읽기 전 크기·chunk 읽기·변경/증가·시간 경계를 적용한다. export는 원본 run tree를 재귀 수집하지 않는다. `collectionStatus=collected`와 종료/삭제/cleanup/service inactivity, pending 없음, sealed manager 소유 result, termination/run/path/manifest/hash가 모두 맞아야 결과를 사용한다. 불명확·실패·철회 시 worker source/output/HOME/CLI-state/scratch를 열지 않는다.

관리자 진단 allowlist는 `state.json`, `events.jsonl`, `baseline.json`, `supervisor.json`, `native.json`, `identity.json`, `identity-proof.json`, `baseline-policy-verification.json`, `policy-verification.json`, `termination.json`, `removed.json`, `ready.json`, `heartbeat.json`, `recovery.json`이다. 준비/import 진단은 `events.jsonl`, `manifest.oci`, `config.oci`, `native-image.json`, `runtime-tools.json`, 전역 metadata는 `image.json`, `image-export.json`, `import-verified.json`, `gate.json`이다. 임의 run 파일은 포함하지 않는다.

Collector 128파일/16MiB와 export 1,024파일/16MiB를 유지하며 status와 외부 index도 합산한다. 임시 archive/index의 실제 members/hash 검증 후 디렉터리 rename으로 함께 공개한다. 정상 파일 정확한 포함, collector hardlink 거부→export 내용 미포함, suppressed/failed/종료 불명/철회/pending의 원본 미접근, symlink/부모 symlink/FIFO, 읽기 전 과대 거부, count/byte/time/depth, 변조 manifest·교체/증가·부분 공개 방지 회귀를 통과했다.

실제 export에서는 `image-export.json`이 root 소유가 아니라는 검사에 걸렸다. 준비 흐름은 호스트 파일을 Lima 사용자로 copy한 뒤 sudo `mv`하며, 이 동작은 소유권을 관리자 root로 바꾸지 않는다. 이는 코드 경로와 `file-owner:image-export.json` 오류에 근거한 진단이며 실제 숫자 UID는 보존되지 않았다. 안전 검사를 우회하지 않아 부분 최종 archive는 공개되지 않았지만 **관리자 진단도 함께 유실됐다**. 준비→metadata 소유권→실제 export 연결을 로컬 회귀가 놓쳤다. 다음 보완은 관리자 검증 후 metadata의 관리자 소유 게시와, 실패해도 허용 진단을 보존하는 경로를 먼저 검토해야 한다. 이번 회차에서 소유권 예외를 추가하거나 원본을 다시 수집하지 않았다.

## 검증·증거·비용

- `pnpm check`: 304통과, skip 0. 타입 검사·예제 build 포함. 최초/최종 모두 재확인했다. 별도 production/live 거부 실행은 이 304개에 포함된 1개이며 더해 세지 않는다.
- Python: execution-lifecycle 86(기존 56+새 30), 공유 lifecycle 16, 기존 감사/deadline/package 44 = **서로 다른 146개**. 개발 중 반복 실행은 새 테스트 수에 더하지 않는다.
- 과거 저장 verifier는 당시 PATH 없는 Spec 차이/126파일·분석8/closing4를 그대로 재현한다. 새 verifier의 첫 독립 실행은 공유 collector 모듈 import 경로 누락으로 실패했다. closing에서 오프라인 검증기의 `sys.path` 한 곳만 보완하고 재검증했다(`closing-source-change.json`). 이번 시도 수·cache binding·archive 미생성을 검증한다. 새 guest raw Spec이 없으므로 full Spec replay를 통과했다고 표시하지 않는다.
- TypeScript 분석/평가 의미와 TASK/B/C·모델·배포 ID·기존 증거를 바꾸지 않았다. `pnpm experiment`와 Linux Vendure 평가 전체 재실행은 이 이유로 생략했다. 최초 3,090파일 중 3,078파일 불변·허용 변경12개를 확인했다. 새 파일은 별도 Git diff로 검토하며 최초 inventory의 분모에 더하지 않는다. 변경 기록은 `validation.json`, 실행 전 gate/전달 hash는 `local-gate.json`, `input-transfer.json`, `execution-source-link.json`에 있다.
- [증거 묶음](../../experiments/domain-model/s2/verification/2026-11-15-execution-lifecycle-fix/)의 최종 index는 123파일·11 archive·내부 997파일을 포함한다. **guest 결과 archive가 아니라 호스트/snapshot 감사 자료**다. 분석 snapshot 5개를 고정하고 cleanup/validate/seal을 명시적 closing으로 등록했다. 실제 실행 경계 helper는 preflight/gate/전달 hash와 일치하며 실패 뒤 고치지 않았다. 최종 source에서 달라진 오프라인 `verify_fix.py`의 import 경로는 전/후 hash와 closing snapshot으로 별도 연결하며 VM에서는 실행하지 않았다.
- VM 1개와 전용 VM root는 삭제됐고 남은 VM/process/미완성 store 항목은 없다. VM 폐기는 단위 봉인 성공 증거가 아니다. 공개 준비물만 의도적으로 보관한다.
- 이번 실측 **1798.114초**, 이전 실측 17,286.049초, 누적 실측 **19084.163초**다. 이전 직렬화 보수 상한 20초와 이번 10초를 별도로 더한다. 시작부터 읽기·계획·구현·검증·대기·정리·보고를 포함하며 Git 게시 시간은 별도다. 신규 유료 비용 0, 실행 한도 초과 0, 실패 단위 재시도 0이다.

다음은 이 부분 결과의 독립 리뷰다. service inactivity 증거 보존과 전달 metadata/export 실패를 먼저 검토하고 새 실행 여부·범위·예산을 정해야 한다. 남은 6단위·정책 대조·실제 인증/모델·본 비교를 자동 재개하지 않는다.
