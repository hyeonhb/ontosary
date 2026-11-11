# S2 실행 전 준비 도구

2026-11-11 [CLI 비모델 인계](../../../../docs/reviews/2026-11-11-s2-cli-feasibility.md): **blocked, 독립 리뷰 대기**. [준비 진단](container/cli-feasibility/)에서 고정 CLI 기동은 확인했지만 native sandbox namespace 생성이 거부됐다. 준비2컨테이너·로컬 CLI10회이며 정상 경계/timeout/네트워크·lifecycle 등록은0회다. 공유 runtime/collector를 수정하지 않았고 자원을 정리했다. 실제 credential/provider/model/trial0, R11/production/live 차단은 유지한다.

2026-11-11 [lifecycle fixture 인계](../../../../docs/reviews/2026-11-11-s2-lifecycle-fixture.md): **fixture-boundary-passed, 독립 리뷰 대기**. [구현](container/lifecycle/)은 독립 guest 감독자·cgroup 전체 종료·manager 전용 전체 수집을 알려진 fixture25개로 확인했다. 공개 직후 supervisor 사망 결과도 격리/차단한다. 실제 CLI/Vendure evaluator/live adapter로 연결하지 않았고 R11 unresolved와 아래 production/live 거부는 유지한다. 이전 타당성 실패 기록은 당시 결과다.

2026-11-10 [컨테이너 타당성 인계](../../../../docs/reviews/2026-11-10-s2-container-feasibility.md): **inconclusive**. [container/](container/)의 Lima/Dockerfile 준비는 VM/image build까지 성공했으나 실행 image 식별자 오류와 수정1회 실패로 중단했다. worker·CLI·Linux 평가/수집/종료 probe는 미실행이다. 자원은 삭제했고 verified receipt/live adapter를 추가하지 않았다. 아래 macOS runtime과 production/live 거부, R11 미해결/R12 기존 판정을 유지한다.

2026-11-10 다음 작업: ADR-031로 [일회성 컨테이너 경계 타당성 검증](../../../../docs/reviews/2026-11-10-s2-container-feasibility-instructions.md)을 승인했다. 기존 CLI/셸을 유지하고 실행·평가 단위의 종료/수집과 Linux 환경을 비용 상한 안에서 확인한다. 아직 컨테이너 도입/종료 검증이 완료된 것은 아니며 아래 macOS 경로와 live/production 차단은 유지한다. 본 비교는 검증 결과 리뷰 이후다.

2026-11-10 [독립 재검토](../../../../docs/reviews/2026-11-10-s2-runtime-accounting-independent-review.md): R12는 검증 범위에서 해결됐고 R11은 미해결이다. 실제22실행에서 늦은 쓰기와 production 차단을 다시 확인했다. 본 비교/실제 모델은 실행하지 않았으며 다음 실행 경계/도구 정책은 사용자와 결정한다. 아래는 구현과 당시 자체 검증 설명이다.

2026-11-10 보완: **R12 구현·자체 검증 완료, R11 종료 경계는 unresolved**다. [새 인계](../../../../docs/reviews/2026-11-10-s2-runtime-accounting-fix.md)와 [선택 기록·증거](../verification/2026-11-10-runtime-accounting-fix/SELECTION.md)를 참조한다. 전체 실행 준비나 독립 해결 판정을 뜻하지 않는다.

이번 버전은 과업·C 자료·공개 타입 검사·계측/수집과 macOS 도구 경계를 준비한다. 실제 모델 호출은 없다. `s2:trial:run`은 항상 거부한다. `trialAuthorized:false`, `readyForTrial:false`, `results:null`이며 사람 대응 검토와 별도 실행 승인이 필요하다.

## 계약

사용자 2026-11-10 후속 결정으로 누적100,000토큰 hard cap을 필수 통과 조건에서 제외했다. 100,000은 보고용 참고선이며 중단 기준이 아니다. 1,800초는 첫 모델 요청부터 도구 실행까지 포함한다. 현 도구 대역에서는 monotonic clock으로 짧은 시간 제한을 실제 검증했다. API 실행기로 확장하지 않는다.

CLI는 실제 turn_context에서 확인한 `gpt-6-astra`/`high`, 설치된 `codex-cli 0.167.0-alpha.3.2`를 기준으로 한다. immutable backend snapshot/service tier는 세션 기록에서 확인되지 않았다. 모델 seed는 검증한 CLI 옵션에 없고 배정 seed와 다르다. 고정 catalog/바이너리 hash는 검증 산출물에 기록한다. [공식 비대화 실행 문서](https://learn.chatgpt.com/docs/non-interactive-mode)와 [permission/config 문서](https://learn.chatgpt.com/docs/config-file/config-reference)를 참고했다. 실제 CLI의 help·bundled catalog·sandbox 실행을 확인했으며 model dispatch를 하지 않았다.

`telemetry.ts`의 `s2-usage-v2-turn-state`는 unknown JSON을 검사하고 순차 활성 turn을 추적한다. [공개 exec 이벤트 정의](https://github.com/openai/codex/blob/main/sdk/typescript/src/events.ts)의 시작/완료/실패/error와 input/output 필드를 지원한다. 설치 CLI의 help와 기존 자료를 함께 확인했으며 현재 공개 소스가 설치된 alpha 바이너리와 완전히 같은 schema라는 주장은 하지 않는다. 실제 공급자 로그는 생성하지 않았다. 공개 계약에는 turn ID가 없어 순차 번호를 쓰며, 임의 `turn_id` 확장은 미지원으로 표시한다.

선택적 `id`는 합성 fixture/수집 계층이 제공할 수 있는 **한 JSONL 스트림 내 이벤트 재전달 identity**다. turn ID가 아니다. 동일 ID·동일 내용의 재전달은 같은 turn 안에서 한 번 처리한다. 충돌·다른 활성 turn의 ID 재사용·시작 없는 완료·ID 없는 추가 완료는 모순으로 표시하고 해당 turn의 기존 합계를 철회한다. 서로 다른 정상 turn의 숫자가 같아도 각각 센다. 알려지지 않은 object 이벤트는 원시 행 참조를 남긴 비계측 이벤트이고, null/array/깨진 JSON/필수 필드 오류는 issue다.

`collectUsage(lines, usageEnd(runResult))`로 실제 종료/EOF/절단/읽기 오류를 넘긴다. 종료 근거를 생략하면 unknown이다. 정상 완료·code0·정상 EOF·로그 무결성·종료 근거와 모든 turn의 완료가 확인될 때만 total을 확정한다. 현재 runtime의 모든 writer 종료는 unverified이므로 실제 도구 결과의 전체 total도 null이다. 합성 입력에서만 종료를 fixture로 명시해 순수 집계의 확정 경로를 검사한다. timeout·중단·출력 절단·미완료/모순이면 total=null이다. `subtotal`은 모순 없는 정상 turn의 관찰 합계이며 공급자 소비량의 하한이라고 부르지 않는다. `consumptionLowerBound`는 null이다. cached input과 reasoning output은 input/output 안에 포함되어 다시 더하지 않고 미관측 세부값은 null이다. 개별 값과 누적 safe-integer overflow도 거부한다. 확정 초과·subtotal 초과·전체 미초과 여부를 분리하며 100,000 참고선을 중단 조건으로 쓰지 않는다.

raw JSONL은 호출부가 별도로 보존하고 집계는 1-based 행 번호/hash/turn/진단만 갖는다. 집계는 최대10,000행·행64KiB·총4MiB에서 중단하며 제한 초과도 incomplete다. 정상 EOF와 단순 수집 중단은 다르다. runtime의 stdout/stderr 합계는4MiB까지만 보존하고 절단/pipe 오류를 명시한다. 이는 completed-turn 기록의 완전성 계약이며 in-flight/공급자 내부 요청·청구 전체·임의 셸 읽기의 완전 계측을 보장하지 않는다. 실제 provider usage·자료 tokens는 미측정이며 tokenizer가 없어 자료는 bytes로만 보고한다.

## 도구와 재현

저장소 root에서 실행한다. 모든 출력 경로는 기존에 없어야 한다. `<codex>`는 설치된 CLI의 절대 경로다.

```sh
pnpm s2:prepare <pinned-cache> <bundle-a>
pnpm s2:prepare <pinned-cache> <bundle-b>
pnpm s2:verify <bundle-a> <bundle-b> <new-report.json>
pnpm s2:trial:environment <pinned-cache> <new-public-environment>
pnpm s2:trial:validate-public <codex> <public-environment> <new-public-report.json>
pnpm s2:trial:probe <codex> <new-probe.json>
pnpm s2:trial:validate-workspaces <codex> <bundle-a> <pinned-cache> <public-environment> <new-workspace-report.json>
pnpm s2:trial:freeze <bundle-a> <new-execution-artifacts> <repo> <verification-evidence>
pnpm s2:trial:run
```

마지막 명령은 준비 상태의 거부 검증이다. 실제 모델을 시작하는 방법으로 쓰지 않는다. 이후 승인도 현재 도구가 자동 추정하지 않는다. 후속 리뷰에서 격리 결함을 해결하고 승인 기록을 정확한 artifact hash에 연결한 뒤 live adapter를 별도 검토한다. 기존 `workspace.ts`는 파일 복사기이고 선택적 공통 public tools 연결만 추가했다. `trial/validate-workspaces.ts`가 실제 같은 UID·Codex permission profile에서 읽기 전용 자료·공개 검사·다른 조건 경로 거부를 검증한다.

`environment.ts`는 원래4735파일과 설치된 node_modules/admin-ui node_modules/common lib·scope config를 별도 복제한다. APFS clone을 사용하며 설치/빌드하지 않는다. 모든 dependency link는 복제 환경 내부로만 해석되는지 검사하고, 일반 dependency 파일 bytes를 원래 cache와 대조해 manifest/hash를 남긴다. 도구에는 standalone public checker와 TypeScript만 있고 평가기·기대값·변형은 없다. Node 실행 파일도 public tools로 복제하며 원래 호스트 홈 경로를 허용하지 않는다. Node/도구/환경/자료는 profile에서 read, production source와 auxiliary/scratch/새 HOME만 write다. config·credential을 위한 control 경로는 셸에서 읽을 수 없다. 실행기의 인증은 이번에 공급하지 않았다.

## 격리의 확인 범위와 차단 조건

최소 profile의 package.json 읽기 예외를 발견해 원래 cache·Ontosary checkout·호스트 홈에 명시적인 deny를 추가했다. 존재하는 package.json canary와 실제 cache/package.json 거부를 다시 검증한다. 실제 Codex macOS sandbox에서 허용 소스 읽기/편집, 자료 쓰기 거부, 존재하는 외부 canary/상위 경로/symlink/control/다른 조건/Ontosary/cache 읽기 거부, 외부 TCP/호스트 Unix socket 접근 거부를 관찰했다. 최종 snapshot profile의 파일 쓰기도 거부됐다. 존재하지 않는 파일의 ENOENT를 거부 성공으로 세지 않는다.

**분리된 자식 프로세스가 process-group 종료를 벗어나는 실제 반례가 남아 있다.** `runtime.ts`의 timeout은 실행기 그룹을 종료하지만 세션을 분리한 모든 자손을 정지시키는 보안 경계가 아니다. 따라서 실제 agent 실행과 적대적 제출 수집은 차단한다. `snapshot()`과 `checkedSnapshot()`/`evaluate-snapshot.ts`는 모든 production 제출을 거부한다. 검증된 종료 receipt 발급자가 없으므로 caller의 true 플래그나 manifest 수정으로 열리지 않는다. `collectDiagnostic()`은 같은 supervisor가 발급한 객체 identity·source/auxiliary 경로·profile 지문을 확인하고 diagnostic kind로만 수집한다. `calibrationSnapshot()`도 fixture용 diagnostic이며 sealed 제출이 아니다. 수집 실패의 임시 디렉터리는 노출하지 않는다. 실제 모델 세션의 tool inventory·인증 경로·전역 지시 배제도 미검증이며 메모리/CPU 자원 상한은 미동결이다.

runTool은 task의 exit/signal과 stop 시각·최대250ms 정리 대기·blocked 반환을 구분한다. 정상 exit도 collectionAllowed=false다. 열린 pipe·kill 오류·spawn 오류·처리 가능한 SIGINT/SIGTERM/AbortSignal에 무한 대기하지 않는다. 시간 제한부터 정리까지는 추가 작업 허용 시간이 아니며 정확한 deadline 순간 snapshot이라고 주장하지 않는다. supervisor의 SIGKILL/호스트 장애도 자손 종료를 보장하지 못하므로 live 다음 실행을 허용하지 않는다. process-group 정리는 진단용 best effort다.

설치 SDK와 실제 kqueue 등록에서 NOTE_TRACK 미지원(ENOTSUP)을 확인했고 launchd의 같은 그룹 정리도 detached 탈출을 해결하지 않는다. 폴링/재부모화 추적을 강제 경계로 채택하지 않는다. 별도 VM/container, native 권한 서비스, subprocess 금지 정책은 비용과 계약 변화가 다른 후속 선택지이며 자동 도입하지 않는다. 이번에 새 플랫폼/유료 인프라/호스트 계정·권한 변경을 하지 않았다. 토큰 hard cap 부재와 이 격리 차단을 구분한다.

## 평가·제출·실패 처리

기존52사례(보존16+요구36) 안에 invalid service의 값0·완료1·오류0·동기 예외0, dialog의 undefined resolve1 assertion을 추가했다. 별도 helper 해법도 허용한다. 참조 diff 일치로 점수를 주지 않는다. 원래24제출에 정책 반례5개를 더한29제출이다. 미지원 의존성/문법은 policy failure로 바꾸지 않는다.

알려진 교정 제출은 `isolated-command.ts`에서 필요한 평가기/근거/TypeScript만 복사한 디렉터리와 고정 cache를 read-only로, 결과만 쓰기 가능하게 두고 network와 호스트 홈을 명시적으로 차단해 검증했다. 이는 임의 제출의 프로세스 탈출까지 안전하다는 뜻이 아니다. 향후 종료 경계가 확보된 실제 제출은 전체 production과 별도 auxiliary를 불변 snapshot으로 수집해야 하며, 원본을 복구하거나 변경 파일을 빼면 안 된다. 공개 타입 검사는 실제 파일/추가 helper를 검사하고, private type/scope/snapshot/behavior gate는 별개로 보존한다.

`checkedDiagnosticSnapshot()`은 source/auxiliary 전체 hash·manifest checksum과 complete-root reader의 전체 파일 목록을 대조한다. `.git`/`node_modules` 내부 생산 파일도 조용히 제외하지 않는다. source·auxiliary·manifest 전체의 실제 read-only profile을 검증했다. checksum 자체는 권한 경계가 아니다.

`evaluate-calibration-snapshot.ts`는 trusted baseline에서 독립 생성한 **known reference 전체 bytes**와 같은 fixture만 받아 read-only 평가한다. 결과에 validTrialSubmission=false를 기록한다. production 수집 실패를 우회하는 live adapter가 아니며 R11 해결 근거로 쓰지 않는다. raw `s2:evaluate`는 기존 평가기 교정 도구이고 live 제출 수명주기 진입점이 아니다. 제한된 wrapper는 명시된 교정/거부 entry만 허용한다.

```sh
pnpm s2:build
node work/s2-build/trial/runtime-accounting-probe.js <codex> <new-report.json>
node experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix/accounting-probe.mjs <new-accounting.json>
node work/s2-build/trial/isolated-command.js <codex> <repo> <cache> <new-out> work/s2-build/trial/evaluate-calibration-snapshot.js <diagnostic-reference> <cache> <new-out>/result.json
```

[재현 README](../verification/2026-11-10-runtime-accounting-fix/README.md)는 입력·출력·exit code, cold-start 실패 증거, 재사용한 권한/공개 검사 근거의 정확한 범위를 기록한다.

9개 예정 실행은 블록별 A/B/C 각1회·위치별 각1회 균형을 갖는 seeded rotation이다. 조건 매핑과 반복 정보는 evaluator에만 있고 agent 작업공간은 blind run ID와 같은 자료 경로를 쓴다. 모두 not-run이며 52사례를52실험으로 세지 않는다. 실행 중 사람 힌트는 없다. 성공·타입/동작 실패·미지원·timeout/미제출·환경 장애를 모두 보고한다. 성능에 따른 재시도는 없고 명백한 환경 장애만 최대1회 대체한다. 원래 실패 증거와 시도를 보존하며 반복 장애·공통 평가 결함이면 전체 배치를 중단한다.

배포 manifest는 정적 내용만 식별하고 execution-manifest는 그 hash와 구현/config/평가 버전을 연결한다. executionId는 자기 필드를 제외한 canonical 내용 hash다. 사람/독립 승인·실제 결과는 빈칸으로 남긴다. 사람 재작업·과거 제작비는 실제 측정 없으면 null이다.
