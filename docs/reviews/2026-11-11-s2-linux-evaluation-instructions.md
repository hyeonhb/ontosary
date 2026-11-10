# S2 Linux Vendure 평가 재현 검증 개발 지시

사용자는 lifecycle fixture 독립 검토 후 **같은 실행 경계에서 Linux Vendure baseline/reference 평가를 재현하는 작업과 새3시간 상한**을 승인했다. 이번 산출물은 Linux 준비 절차, 알려진 제출만 평가하는 최소 adapter, 실제 재현 증거와 인계 보고서다. 실제 CLI·인증/provider 연결과 본 비교는 결과 리뷰 뒤 별도로 진행한다.

이 환경은 실행 간 파일·프로세스 간섭을 막고 평가 조건을 맞추는 실험 기반이다. 이번에는 그 기반에서 기존 평가의 의미가 유지되는지 확인한다. agent 변경 효용(H-O)이나 FCA의 모델 구축 기여(H-F)를 검증하는 단계는 아니다. 제품 코어·모델/조회 아키텍처로 일반화하지 않는다.

## 1. 시작점과 유지할 계약

최초 명령에서 UTC/monotonic 시계를 기록하고 이후 읽기·설계·환경 준비·구현·대기·검증·정리·보고를 모두 같은 회차에 청구한다. 이어 AGENTS, PROGRESS, ARCHITECTURE, ROADMAP, CONTRIBUTING과 아래 자료를 읽는다. 시작 시계 누락은 실제 누락과 보수적 추정치를 공개하며 예산을 다시 시작하지 않는다.

- [lifecycle 결과](2026-11-11-s2-lifecycle-fixture.md), [구현 설명](../../experiments/domain-model/s2/trial/container/lifecycle/README.md), [당시 지시](2026-11-10-s2-lifecycle-fixture-instructions.md).
- [평가 계약](../../experiments/domain-model/s2/evaluation/TASK-REVIEW.md), `evaluation/{evaluate,submission,behavior,execute,modal,stream,variants,run,oracle-check,verify}.ts`.
- `vendure-baseline.ts`, `trial/{environment,public-check}.ts`, `trial/container/prepare-vendure.sh`와 고정 manifest/lockfile.
- [기존 macOS 평가 증거](../../experiments/domain-model/s2/verification/2026-11-10-trial-preparation/oracle/)와 [실행 계약](../../experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix/execution/execution-manifest.json).

지시 작성 기준은 main `d840669`(PR #42)다. 개발 시작 시 원격/브랜치/변경을 확인하고 최신 main의 전용 짧은 작업 브랜치를 사용한다. 다른 checkout이나 사용자 변경을 전환·덮어쓰지 않는다. 기준 이후 관련 변경이 있으면 차이를 먼저 기록한다.

직전 독립 검토는 코드·기록된 실제25개·원시 archive/hash·정리 증거 및 호스트 회귀를 대조한 것이다. 새 VM 실행을 반복한 리뷰는 아니다. fixture-boundary-passed를 인정하지만 R11 전체 해결로 판정하지 않았다. RuntimeMaxSec 도달과 불명확한 create 요청 중 감독자 사망의 실제 주입은 여전히 미검증이다.

다음은 고정한다.

- 동일 Lima2.3.0/VZ + containerd/nerdctl2.4.2 후보, 기존 pinned base와 Node22.19.0·TypeScript5.9.3. 실제 Linux/커널/npm 버전·이미지 지문은 새로 관측한다.
- Vendure revision `534e6003534f74761e82de1b8c6061cba89945d1`, 원본 inventory·lockfile·strict scope·Program 입력 계약. 기존 `/tmp/ontosary-vendure-preparation-20261108/vendure`는 읽기 전용 원본으로 취급한다. 부재하면 고정 revision의 기존 준비 절차로 확보하며 같은45분 한도에 포함한다.
- 기존 과업 정책, 52사례(보존16/요구36), 평가 지원 범위·모델12항목/16링크·승인0·A/B/C 지식과 배포84파일. baseline/model/bundle/evaluator 지문을 시작 시 기록하고 종료 시 대조한다.
- 기존 production 수집/평가/live 거부, R12 기존 검증 범위, `trialAuthorized:false`, `readyForTrial:false`, 본 비교 `results:null`. 이번 교정 보고서는 별도 증거이며 본 비교 결과 칸에 쓰지 않는다.

## 2. 구조와 책임

```text
관리자 Linux 준비 1회
  ├─ 고정 Vendure 소스 + Linux 의존성 + common build → 불변 환경
  ├─ inventory baseline + 기존 variantDelta → 완전한 제출 입력
  └─ 동일 evaluator/공개 타입 검사 + 계약 자료 → 읽기 전용 도구
             ↓ 실행마다 새 container / 출력·임시 공간
독립 guest supervisor → 고정 Node 평가 entrypoint(PID 1)
             ↓ 전체 종료 확인 + pending/runtime 확인
관리자 출력 수집 → manifest/hash 검증 → service 성공·cleanup 확인
             ↓
회차 전용 finalized 교정 결과 → macOS 및 Linux 반복/입력 방식 대조
```

**Linux 환경 준비와 실행별 평가를 분리한다.** 설치·빌드 중에만 준비용 네트워크를 허용한다. 완성된 환경은 읽기 전용으로 반복 사용하되, 매 평가의 container·cgroup·출력·tmp·작업 ID는 새로 만든다. 모든 실행은 순차로 한다. 실행 간 공유하는 것은 검사된 불변 입력뿐이며 이전 출력·임시 파일을 다음 실행에 노출하지 않는다.

**이미 알려진 제출을 관리자 입력으로 조립한다.** baseline inventory는4,735파일·약76.7MB여서 기존128파일/16MiB 수집기에 전체 source를 통과시키지 않는다. 기존 `variantDelta`와 baseline으로 reference 및 부정 사례의 완전한 소스 트리를 관리자 영역에서 만들고, 원래 파일과 patch의 hash·전체 manifest·submissionId를 기록한다. complete-root는 실제 완전한 트리를 `readSubmission`으로 읽는다. 누락 파일을 실행 시 baseline으로 복원하지 않는다. explicit-baseline-delta는 별도7번째 실행에서 기존 명시적 delta 계약으로 평가하고 두 입력 방식의 source identity를 비교한다.

**수집 범위는 이번 실행의 보고서와 진단 출력이다.** source/environment/tools는 RO bind, 출력만 RW bind, tmp는 유한 tmpfs다. collector의 일반 파일·디렉터리/no-follow·hardlink 거부와128파일/16MiB/깊이16/로그1MiB 상한을 유지한다. 제한에 맞추기 위해 보고서를 자르거나 필드를 누락하지 않는다. 기존 단일 평가 JSON은 약2.4MB이므로 먼저 원형 그대로 사용한다. 부족하면 실제 크기·원인을 보고하고 상한 변경을 자동 채택하지 않는다. 향후 임의 agent 제출 전체 수집기는 이번에 만들지 않는다.

**고정 평가 job만 추가한다.** 실험 내부 `trial/container/` 아래에 Linux 준비·평가 job·증거 비교를 둔다. lifecycle의 등록/감독/종료/수집/실패 처리 기능을 재사용하되 거대한 범용 runner나 명령 문자열 실행 API를 만들지 않는다. 예를 들어 `linux-evaluation/` 보조 모듈과 기존 lifecycle의 작은 job 분기로 충분하다. 제품 코어나 기존6개 evaluator 모듈의 의미를 바꾸지 않는다.

평가 job의 Node entrypoint 자체를 PID1로 실행한다. 기존 fixture의 holding PID1 + 별도 exec 패턴이나 worker의 `ready.json`을 정상 종료 권한으로 일반화하지 않는다. manager가 정한 image/container/run identity와 native runtime의 시작·종료/exit code로 상태를 연결한다. pending 생성/시작 요청이 불명확하면 빈 cgroup만으로 완료 처리하지 않는다. 로그의 완료 문자열·JSON 생성·stdout EOF는 종료 증거가 아니다. 공개 타입 검사는 같은 고정 entrypoint에서 함수 호출 또는 고정 자식 명령으로 실행할 수 있으며 그 자식도 같은 경계에서 종료한다.

worker는 기존 UID/GID1000, cap drop ALL, no-new-privileges, read-only root/cgroup, network none, CPU2·메모리4GiB·PID256·tmp64MiB를 유지한다. manager 제어 경로·containerd socket·호스트 home/인증·다른 실행·과거 결과는 mount하지 않는다. 평가에 필요한 repository 자료만 고정 hash의 도구/계약 입력으로 제공하고, 실제 mount와 EROFS 쓰기 거부를 확인한다. Linux 의존성 내부의 정상 workspace symlink는 불변 환경 내부로만 해소돼야 하며 output 수집의 symlink 허용으로 확대하지 않는다.

## 3. 구현 순서와 시간 예산

새 회차 총180분이다. 아래 마감은 모두 최초 시각 기준이며 단계 시작마다 재설정하지 않는다. 신규 유료 비용0, 후보/버전 교체·호스트 관리자 권한/전역 서비스 변경은 승인하지 않는다. 기존 회차의 잔여 예산을 재개하지 않는다.

| 마감 | 확보할 결과 | 미충족 시 |
| --- | --- | --- |
| 45분 | VM 최소 실행, Linux 의존성/common build, 기존 입력 검증과 baseline 환경 열기 | 탐색 중단, 환경 차이/실패 증거를 인계 |
| 90분 | baseline/reference complete-root 각1회가 새 경계에서 종료·수집·최종 승인되고 의미 대조 통과 | 새 확장 중단, 실패 원인·부분 결과 인계 |
| 150분 | 아래7단위·짧은 timeout 통합 probe·필요한 회귀/대조 확보 | 새 실행·수정·재준비 중단, 미완료 명시 |
| 180분 | 검사·자원 정리·증거 동결·최소 보고 완료 | 한도 초과를 숨기지 않고 남은 상태/복구 방법 보고 |

환경 재준비·다운로드·실패/재시도·대기도 전체 비용에 포함한다. 같은 후보에서 원인을 확인한 국소 수정은 남은 시간 안에 허용하되, 새 근거 없는 반복은 하지 않는다.150분 직전 새 작업을 시작해 마무리 시간을 잠식하지 않는다. 명령별 timeout은 다음 중간 마감까지의 잔여 시간을 넘지 않게 한다. 최초 실패/중간 실행도 보존하고 최종 통과 분모와 구분한다. Git 게시/PR/merge 전달 시간은 기존 회차처럼 별도 기록하되 구현·검증을 그 시간으로 넘기지 않는다. 경계 불확실 시 새 실행을 차단하고 소유 자원 안전 정리를 우선한다.

### 순서 A — Linux 준비와 기존 계약 확인

1. 시작 inventory와 비용 ledger, 원본/정적 배포/평가기 지문을 기록한다. 기존 VM은 정리된 상태이므로 새 소유 prefix로 같은 후보를 준비한다. 현재 native target→config→rootfs chain→실제 container를 다시 확인하며 과거 image digest를 현재 build의 실행 ID로 하드코딩하지 않는다.
2. macOS `node_modules`·Node 바이너리·APFS clone을 복사하지 않는다. `trial/environment.ts`의 `/bin/cp -cR` 경로와 별개로 Linux 준비 함수를 둔다. 원본 inventory·고정 config/lockfile에서 Linux 복사본을 만들고 다음 기존 명령을 우선 사용한다.

   ```sh
   npm ci --ignore-scripts --no-audit --no-fund --workspace=@vendure/admin-ui --workspace=@vendure/common --include-workspace-root
   npm run build --workspace=@vendure/common
   ```

   설치 전후 lockfile·source hash와 실제 npm/의존성 버전을 기록한다. 필요한 common build만 명시적으로 실행한다. lockfile 갱신, scope/strict 완화, 추가 workspace 전면 빌드, 의존성 버전 변경으로 통과시키지 않는다. 기존 라이선스와 설치 출처를 기록한다.
3. 동일 TS5.9.3로 평가 도구를 build하고 실행할 JS·package/module 해석·TypeScript 라이브러리·RxJS 경로를 고정한다. 호스트에서 만든 portable JS를 쓴다면 실제 Linux가 읽은 hash와 evaluatorId를 확인한다. ESM 해석을 전역 `NODE_PATH` 가정으로 대신하지 않는다. 기존6개 evaluator 모듈의 compiled hash 차이가 나면 원인을 분류하고 기능 변경을 숨기지 않는다.
4. **기존 `openEnvironment()`를 먼저 그대로 통과시킨다.** 이 함수는 원본뿐 아니라 역사적 Program 입력 hash를 검사한다. Linux에서 불일치하면 파일별 source/타입 라이브러리/common 산출물/플랫폼 차이로 분류한다. 검사 우회·자동 재고정·누락 입력 무시로 통과하지 않는다. 의미 있는 입력 계약 변경이 필요하면 이번 성공 판정을 중단하고 차이와 후속 선택지를 인계한다.

### 순서 B — 평가 lifecycle 연결

5. 알려진 job 명세를 manager가 등록하고 불변 입력 manifest와 실제 bind를 확인한다. worker 수명주기는 등록 후 최초 runtime 생성/시작 요청 직전부터 **180초**로 제한해 시작 요청 정체도 포함한다. guest heartbeat lease5초와 독립 감독자를 유지한다. 종료 확인10초·출력 수집10초, 새 평가 job service의 RuntimeMaxSec는210초, TimeoutStartSec5/TimeoutStopSec12, 외부 단위 상한240초로 둔다. 기존 작은 fixture의10/5/40/60초 설정은 별도로 유지한다. 상태 전이/cleanup 전체가 외부 상한 안에 들어오는지 확인하며 상한을 자동 늘리지 않는다.
6. admission 닫기→persistent parent inode/전체 `populated=0`→runtime/task/pending 확인→종료 기록→no-follow 수집/검증→원자 공개→service 성공/cleanup 완료를 유지한다. 소비자는 finalized와 성공 cleanup을 확인한 결과만 비교한다. 공개 직후 service 실패의 격리·next 거부도 유지한다. PID1 exit만 보고 곧바로 수집하지 않는다.
7. timeout/OOM/wrapper loss·시작/종료 불확실·수집 실패는 **인프라 실패 또는 진단**이다. 우연히 생성된 평가 JSON을 정상 교정 결과로 채택하지 않는다. 정상 runtime exit0도 평가 내용의 pass를 뜻하지 않는다. 기존 `evaluation/run.ts`는 baseline의 `overall:failed` 보고서를 정상 생성하고 exit0일 수 있다. manager 실행 상태, evaluator의 타입/동작/overall 판정, 교정 기대값 일치를 각각 기록한다.
8. 새 결과 종류는 known-submission calibration임을 명시한다. `fixtureOnly:true`/`validSubmission:false`와 같은 기존 비생산 경계를 유지하고, 이번 전용 소비 경로에서만 읽는다. 기존 production/live dispatcher를 열거나 알려진 제출 결과를 실제 agent 제출 receipt로 변환하지 않는다.

### 순서 C — 필수7단위와 통합 회귀

먼저 baseline/reference 각1회로90분 마감을 판단한 뒤 남은 반복·부정 사례로 진행한다. 한 container에서 여러 제출을 batch 평가해 새 단위 반복을 대신하지 않는다. 각 단위는 고정 환경을 새로 열고 입력 및 결과를 새 출력에 기록한다.

| 제출 / 입력 방식 | 새 단위 수 | 기대 판정 |
| --- | ---: | --- |
| baseline / complete-root | 2 | 타입 passed, 보존16/16, 요구6/36, overall failed, sourceBinding=true |
| reference / complete-root | 2 | 타입 passed, 전체52/52, overall passed, sourceBinding=true |
| helper-type-error / complete-root | 1 | 타입 failed, 동작 not-run, overall passed 금지 |
| wrong-modal-order / complete-root | 1 | 타입 passed, 동작 failed, 잘못된 주문 전달을 기존 payload assertion에서 검출 |
| reference / explicit-baseline-delta | 1 | complete-root와 동일 submissionId·소스/타입/동작 판정·payload/trace, 전체52/52 |

baseline/reference의4개 complete-root 실행에는 공개 `publicCheck`도 실행해 private 타입 검사와 passed·진단0을 대조한다. 공개 검사는 타입 전용이며 private 동작 oracle과 합치지 않는다. 부정2종은 새 변형을 설계하지 않고 기존 `variantDelta`를 그대로 사용한다. 이번에는 전체29변형 교정·실제 agent 수정 제출·전체 Angular/server 동작 평가를 기본 요구로 확대하지 않는다.

새 평가 job 경로에는 **짧은 timeout + 지연 writer** 통합 probe를 추가한다. 실제 새 PID1/시작 관측/출력 수집 경로를 사용하되 알려진 유한 테스트 workload로 제한한다. 예를 들어2초 timeout·5초 지연 쓰기와6초 관찰, kill을 미룬 유한 대조로 writer가 실제 동작함을 확인한다. timeout 뒤 전체 종료·추가 쓰기 없음·정상 평가 채택 금지·다음 단위 오염 없음을 대조한다. 주7단위와 별도 분모로 기록한다.

공유 lifecycle를 수정했다면 기존 normal/timeout/wrapper loss·supervisor death·공개 후 실패 격리의 실제 핵심 회귀를 변경 영향에 맞게 반복한다. collector13·cleanup3의 호스트 회귀와 기존 production/live 거부도 확인한다. 모든25개 반복은 변경된 경계가 요구할 때만 수행하며 미실행 범위를 명시한다. 새 job에 특화된 시작/exit/pending 처리를 작은 실패 사례로 확인하고 실제로 주입하지 않은 RuntimeMaxSec/불명확 create 사망을 통과로 쓰지 않는다.

## 4. 의미 대조와 증거

**기존 macOS 결과 대조, Linux의 새 단위 반복 대조, complete-root/delta 대조를 각각 보고한다.** baseline/reference와 부정2종의 원문 보고를 기존 날짜 증거와 연결하고, 적어도 다음을 자동 대조한다.

- 사례별 status·실패/미지원 이유·요청 payload·modal/stream trace. 총점만 같고 실패 사례가 다른 것을 재현으로 인정하지 않는다.
- 전체 submittedManifest·submissionId·checkedFiles·executedFiles·sourceBinding·sourceMapping. Linux 입력 조립과 실행 코드가 동일한 제출을 가리켜야 한다.
- 진단 code/위치/message·실제 Program 파일 집합/입력 hash·scope/strict 설정. 공개/private 판정은 공통 타입 범위에서 비교한다.
- 환경·evaluatorId/모듈 hash·Node/TS/RxJS·lockfile/common build·image target/config/실행 snapshot과 run identity. 플랫폼별 실행 환경 metadata는 숨기지 말고 별도 비교한다.

비교에서 제외할 항목은 시간·run ID·명시적으로 대응한 실행 root 등으로 **필드 경로별 목록을 사전 고정**한다. macOS 기록은 explicit delta이고 새 완전 소스 평가는 complete-root이므로 inputMode의 의도된 차이를 따로 표기하고 source identity를 대조한다. 의미 필드·진단·dependency/build 지문을 광범위한 문자열 치환으로 지우지 않는다. 기존 `evaluation/verify.ts`의 시간 제외 재현 계약을 완화하지 말고, 새 플랫폼 대조 wrapper에서 허용 차이/미해결 차이를 모두 보고한다. 원문은 보존한다.

준비 완료·각 실행 전후·마감에 불변 환경/입력 지문을 확인한다. 실행 wall time·환경 준비·평가/종료/수집 지연·출력 크기는 운영 비용으로 기록하고 agent 효용 수치로 해석하지 않는다. 시간은 같은 clock domain 안에서 계산하고 host/guest 차이는 따로 표시한다.

새 `experiments/domain-model/s2/verification/<실제 날짜>-linux-evaluation/`에 명령·exit·버전·최초 실패와 수정본·각 실행 metadata·raw 보고서·대조 결과·정리 상태·비용을 보존한다. 이미 있으면 새 suffix를 사용한다. 당시 실행한 Python/JS/shell/설정과 evaluator·입력 manifest를 재귀 hash로 묶고, archive 내부도 검증 가능하게 남긴다. node_modules/전체 VM/비밀은 커밋하지 않는다. 설치 재현 명령과 의존성 지문을 남기며 원본 cache를 변경하지 않는다.

## 5. 중단 기준과 완료 판정

중간/최종 시간 한도 미충족, 설명되지 않는 의미 차이, Linux Program 입력 불일치, 종료·결과 승인 경계 회귀, 추가 자원/collector 상한 필요, lockfile·scope·strict·평가 의미 완화나 후보/플랫폼/버전 교체가 필요하면 새 탐색을 멈춘다. 원인 확인된 국소 packaging/path/시작 상태 처리 수정은 상한 안에서 가능하지만 초기 실패와 수정 후 증거를 모두 남긴다. 보정해서 성공으로 만드는 것과 원래 계약을 구현하는 것을 구분한다.

판정은 다음 중 하나다.

- **linux-evaluation-reproduced:** 필수7단위·공개 타입 검사·timeout 통합·영향 범위 회귀·의미/입력 대조·불변성·종료/수집/최종 승인·정리까지 충족했다.
- **inconclusive:** 시간 또는 증거가 부족하다. 통과/실패/미실행을 항목별로 구분한다.
- **blocked:** 승인 범위 안에서 진행할 수 없는 원인이나 계약 불일치를 확인했다. 해결에 필요한 선택지와 예상 비용을 인계한다.

성공에는 raw 증거·실행본 지문·실패 보존·비용/분모·재현 명령·잔존 자원 확인이 모두 필요하다. 실패 인계도 같은 공통 조건을 갖추면 이번 조사 작업을 마칠 수 있다. 미완료 필수 검사를 통과로 간주하지 않는다.

성공하더라도 **R11 전체 해결, 실제 agent 실행 독립성 전체, 본 비교 준비 완료를 선언하지 않는다.** 실제 CLI helper/도구 inventory·세션/전역 지시·인증/provider/네트워크·usage 실측·C 사람 의미 동등성 검토는 별도다. CLI version/help 반복이나 실제 모델 연결 시험도 이번 필수 범위에 넣지 않는다. 실제 모델/provider/본 비교0회와 본 비교 차단을 유지한다.

## 6. 마감과 개발 인계

150분 이후 새 구현/탐색을 멈추고 검사·증거·정리·보고에 집중한다. 소유 container·task·systemd unit/slice·VM/image/volume·작업 prefix와 이번에 새로 생성한 cache만 제거한다. 시작 전 inventory와 URL/hash로 소유권을 확인하며 공용 prune이나 기존 cache 삭제는 하지 않는다. 실제 부재/종료를 확인하고, cleanup 실패면 대상 ID/경로·상태·복구 명령을 인계한다. VM 삭제를 개별 단위의 종료/수집 성공 증거로 대체하지 않는다.

`pnpm check`, `pnpm s2:build`, 변경 경계의 의미 있는 호스트/guest 회귀를 실행한다. 제품 분석·원래 fixture 의미를 바꾸지 않으므로 `pnpm experiment`는 기본 요구가 아니다. 시간이 부족하면 검사 미완료를 기록하고 검증하지 않은 head를 merge하지 않는다.

`docs/reviews/<실제 날짜>-s2-linux-evaluation.md`는 결론/범위 →7단위와 비교표 → Linux 준비·평가 lifecycle 변경 → 최초 실패/수정 → 비용·정리 → 후속 미검증 순서로 작성한다. 이전 회차·이번 회차·누적 비용을 분리하며3시간을 결과가 나올 때까지 연장하지 않는다. PROGRESS·ARCHITECTURE·ROADMAP·REVIEW_CONTEXT·관련 README를 실제 결과와 독립 리뷰 대기로 갱신하고 중요한 선택은 DECISIONS에 기록한다.

지속 승인에 따라 staged diff 검토 → commit → push → PR/자체 검토 → 필수 검사·검증한 head 확인 후 merge → 자신의 로컬 main 동기화까지 진행한다. 원격 게시 승인은 모델 연결이나 본 비교 승인으로 확장하지 않는다. **완료 후 실제 CLI·인증 연결과 본 비교에 착수하지 않고 결과 리뷰를 기다린다.**
