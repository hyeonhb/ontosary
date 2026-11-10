# 개발 세션 지시 — S2 일회성 컨테이너 경계 타당성 검증

작성: 2026-11-10. 기준 main `419c4d9fb96632c89a9db0fc419f7b98e57fefe3`(독립 리뷰 PR #36). 이 지시가 반영된 최신 main에서 시작한다. 개발·평가자 전용이며 비교 agent에게 배포하지 않는다.

## 1. 승인된 방향과 이번 완료 지점

사용자는 **일회성 컨테이너를 실행 경계로 우선 검토하고 기존 Codex CLI·셸 사용 방식을 유지**하기로 했다. macOS의 process-group 종료에서 벗어나는 자손을 전체 실행 단위와 함께 정지시킬 수 있는지, S2의 작은 비교에 감당할 만한 준비 비용인지 검증한다. macOS 호스트의 기존 환경은 보존하면서 로컬 Linux 컨테이너 후보를 검토할 수 있다. ADR-031이 ADR-029/030의 macOS 한정·컨테이너 미채택 범위를 이 타당성 검증에 한해 확장한다.

**이번 작업은 최소 실험 환경, 모델 없는 종료/권한 probe, Vendure·평가 재현과 비용 보고까지다. 본 비교는 결과를 독립 리뷰한 뒤 진행한다.** 실제 모델 요청·연결 시험·agent 과업 실행·9회 중 일부 예비 실행은 하지 않는다. 실제 provider 인증 성공과 모델 제공 가능성을 로컬 help·catalog·합성 응답으로 검증했다고 표현하지 않는다.

운영 플랫폼·관리 UI·스케줄러·다중 사용자/여러 OS 지원을 만들지 않는다. API 실행기·CLI 포크·macOS 전용 권한 서비스·제한 도구용 새 MCP 서버로 자동 전환하지 않는다. 제품 코어·FCA/논리·모델/조회·과업과 B/C 지식 의미·평가 지원 범위를 바꾸지 않는다. H-O/H-F·S3를 이번 작업의 성과로 주장하지 않는다.

## 2. 준비 비용 상한과 중단 기준

이번 지시의 운영 상한은 **총 4시간의 경과 시간**이다. 성공 예상 공수가 아니라 탐색 비용 제한이다. 읽기/조사·설치·다운로드·이미지/의존성 빌드·구현·probe·회귀의 대기도 포함한다. 시작 시각과 절대 마감, 단계별 시작/종료·명령/exit code를 기록한다. 세션 재시작이나 재시도로 예산을 초기화하지 않는다.

| 제한 | 적용 |
| --- | --- |
| 전체 | 시작 후240분.210분부터 새 탐색/환경 변경을 멈추고 마지막30분을 검증·정리·보고에 사용 |
| 환경 준비 | 런타임 설치·VM/이미지·Linux CLI·Vendure 의존성/필수 빌드를 합쳐 최대90분. 전체4시간 안에 포함 |
| 후보/재시도 | 런타임 후보1개. 원인을 확인한 환경 실패에 수정 후 재시도1회까지, 같은 예산 안에서 수행. 여러 플랫폼을 연속 설치하지 않음 |
| 신규 유료 비용 | 0. 유료 인프라·계약/구독·새 API 과금·라이선스 구매 없음 |

기존 사용 가능한 런타임을 먼저 확인한다. 없으면 한 후보의 배포/라이선스와 설치 변경 범위를 검토한다. 사용자 권한의 되돌릴 수 있는 작업용 설치·전용 VM/이미지 준비는 이 검증 범위다. 관리자 권한, 시스템 보안 설정 변경, 전역 서비스/기본 Docker context 교체, 새 계정/유료 약관 동의가 필요하면 자동 진행하지 않고 요구 사항을 인계한다. 실제 추가 디스크 사용량·다운로드량도 관측 가능한 범위에서 보고한다. 이 문서는 특정 런타임이 이미 설치됐거나 비용 없이 사용 가능하다고 전제하지 않는다.

다음이면 해당 의존 작업을 멈추고 `blocked` 또는 `inconclusive`로 인계한다.

- 환경 준비90분 또는 전체 실험210분 한도에 도달함. 남은 필수 검증이 예산에 들어오지 않는다고 확인되면 더 일찍 중단한다.
- CLI 포크/새 API 실행기, 광범위한 Vendure 업그레이드/lockfile 변경, 새 평가기/제품 코어 재설계가 필요함.
- 일반적인 컨테이너 안에서 CLI 셸을 유지하려면 privileged 모드·호스트 PID/네트워크·관리 소켓·광범위한 호스트 쓰기 권한이 필요함.
- 실행 단위 밖으로 빠져나간 writer, 종료 확인 불가, 다음 실행 접근, evaluator/다른 조건/자격 증명 canary 접근을 관찰함. 원인을 설명할 수 있는 작은 수정1회 범위만 검토하고 실패를 숨기지 않는다.
- 같은 고정 소스/과업의 공개·private 타입 검사 또는 기존 동작 교정이 달라지며 단순 환경 차이로 설명·해결되지 않음.

상한 뒤 새 탐색을 하지 않는다. 실행 중 fixture 종료·소유 임시 자원 정리·최소 증거 보존은 끝내고 불가피한 정리 초과 시간을 별도로 기록한다. 일부 검증을 생략해 통과로 만들거나 본 비교부터 실행하지 않는다. 중단 인계도 유효한 타당성 결과이며 ‘R11 해결’과 구분한다.

## 3. 입력과 출발 상태

PROGRESS → ARCHITECTURE → ROADMAP → AGENTS/CONTRIBUTING과 다음 자료를 읽는다. 원격/브랜치/사용자 변경을 확인하고 다른 checkout·cache를 덮어쓰지 않는다.

- [R11/R12 독립 리뷰](2026-11-10-s2-runtime-accounting-independent-review.md), [개발 인계](2026-11-10-s2-runtime-accounting-fix.md), [직전 보완 지시](2026-11-10-s2-runtime-accounting-fix-instructions.md).
- [실행 경계 선택 기록](../../experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix/SELECTION.md), [trial 계약](../../experiments/domain-model/s2/trial/README.md), [독립 증거](evidence/2026-11-10-s2-runtime-review/).
- `trial/{runtime,runtime-accounting-probe,telemetry,snapshot-gate,isolated-command,public-check,freeze}.ts`, `evaluation/{execute,submission,evaluate,oracle-check}.ts`와 관련 테스트.
- `experiments/domain-model/s2/results/2026-11-10-trial-preparation/` 및 v4의29제출 교정 원시 자료.

출발점은303테스트(skip0)·기존 비교4/4,29제출60파일·reference/helper52/52, agent84파일·모델12항목/16링크·승인0이다. R12는 순차 이벤트 집계의 검증 범위에서 해결됐으며 provider 관측은 미검증이다. R11은 미해결이다. 기존 macOS production 수집/평가와 live entry는 계속 거부한다.

Vendure revision `534e6003534f74761e82de1b8c6061cba89945d1`, 원래 cache `/tmp/ontosary-vendure-preparation-20261108/vendure`를 고정 입력으로 사용한다. 원래 소스·cache를 수정하지 않는다. 기존 macOS Node/의존성 바이너리를 Linux에서 그대로 쓸 수 있다고 가정하지 않는다.

## 4. 최소 구조와 수정 범위

실험 내부에 **컨테이너 생성 → 로컬 fixture 실행 → 실행 단위 종료/확인 → 전체 결과 수집 → 별도 평가 단위 실행 → 정리**를 재현하는 작은 adapter/스크립트만 둔다. 예를 들어 `experiments/domain-model/s2/trial/container/` 아래에 한 런타임의 선언·실행 adapter·probe·README를 둘 수 있다. 추상적인 다중 backend 프레임워크를 먼저 만들지 않는다.

컨테이너 밖의 관리자가 전용 실행 ID·불변 container ID·이미지 digest·경로·상한·종료 상태를 소유한다. agent가 관리 API/소켓을 호출하거나 자신의 종료/제출 권한을 승인할 수 없어야 한다. 실험용 쓰기 영역은 실행별로 분리하고 원본 checkout/cache·다른 조건·평가기·실제 사용자 홈을 제공하지 않는다. 종료 확인 후 관리자만 전체 production/auxiliary와 manifest를 회수한다.

평가 단계도 제출 코드를 실행하므로 독립적인 일회성 단위에서 수행한다. agent 실행 중에는 private evaluator·기대값·변형·교정 정답을 마운트하지 않는다. 평가 단계에는 모델 자격 증명이 필요 없다. 기존 `node:vm`의 제한된 문법/바인딩이나 timeout을 OS 격리·모든 자손 종료 보장으로 대신하지 않는다.

기존 `runTool`의 macOS 경로와 항상 거부하는 production entry는 그대로 유지한다. 새 경계의 검증 receipt를 발급하더라도 **이번에는 fixture에만 결합**하고 live dispatcher를 열지 않는다. 기존 `termination:unverified`를 전역적으로 verified로 바꾸거나 `termination:fixture`를 실제 모델 계측 근거로 쓰지 않는다. 공유 코드 변경은 필요한 작은 접합부로 제한하고 기존 부정 사례를 유지한다.

## 5. 단계별 타당성 확인

### A. 실행 환경과 CLI 경로

선택한 런타임1개, 호스트/guest OS·CPU architecture·kernel·cgroup/namespace·자원 설정·이미지 digest를 기록한다. 작업 프로세스는 일반 UID로 실행하며 privileged/host PID/host network/관리 socket을 제공하지 않는다. cgroup 이동·재위임이나 종료 관리 설정을 agent가 바꿀 수 없어야 한다. 이미지 tag만 기록하지 말고 실제 실행한 내용과 연결한다.

‘기존 CLI 유지’는 Codex CLI와 셸 사용 경로를 유지한다는 뜻이다. macOS용 바이너리를 Linux에 복사하거나 CLI를 포크하라는 뜻이 아니다. 공식 Linux 배포와 현재 고정 설정의 호환성을 확인하고 binary hash·버전·help/config 인식·셸 backend를 기록한다. 같은 CLI 버전을 우선한다. 다른 버전만 가능하면 차이를 후보로 보고하며, 이를 기존 runtime과 동일하다고 표시하거나 본 비교 버전으로 자동 확정하지 않는다. 현재 모델 식별자/추론 설정도 임의 대체하지 않는다.

help·schema·catalog·모델 없는 `sandbox`/도구 실행으로 가능한 부분만 검사한다. CLI가 config를 파싱했다는 사실과 실제 모델에 노출될 도구 inventory는 구분한다. 실제 모델 호출이 있어야 확인 가능한 항목은 `pending-live-validation`으로 남긴다. 작은 CLI probe를 위해 `exec`에 실제 과업이나 ‘hello’를 보내지 않는다.

모델 연결 통신과 도구의 네트워크 권한을 구분한 경로를 설명한다. 준비 중 이미지/패키지 다운로드는 가능하나 실험 도구의 임의 외부 네트워크를 허용하는 근거가 되지 않는다. 실제 자격 증명을 복사하지 않고 비밀이 아닌 canary로 control 경로/환경 변수 유출을 검사한다. 사용자 CODEX_HOME 전체·기존 대화·전역 plugins/skills를 이미지에 넣지 않는다. 인증 방식의 지원 여부와 실제 계정/모델 접근 성공은 별도 미검증 상태로 남길 수 있다.

### B. 종료 경계와 허용 도구

셸·검색·읽기·편집·공개 타입 검사의 사용 방식을 유지한다. ‘백그라운드를 만들지 말라’는 프롬프트만으로 종료를 보장하지 않는다. Web·서브에이전트·임의 외부 MCP/앱·외부 설치·다른 조건 접근은 기존 계약대로 제외한다. A/B/C에 같은 정책을 적용하고 B 전용 탐색/편집 도구를 추가하지 않는다.

자손이 새 session/process group을 만들어도 같은 실행 단위에 남고, 종료 명령이 그 단위 전체를 대상으로 한다는 원리를 설명한다. 단순한 CLI 부모 PID kill·`docker stop` 명령 반환·프로세스 목록 한 번만으로 종료 완료를 선언하지 않는다. 실제 kernel/runtime이 제공하는 상태를 확인하고, 남은 프로세스와 쓰기 가능성이 없는 상태에 수집을 결합한다. cgroup v2 사용 시 kill/empty 상태와 이동 권한을 함께 확인하는 식으로 선택한 구현의 근거를 남긴다.

기본 수명주기는 실행 → 종료 요청 → 전체 단위 정지 확인 → 수집이다. 정상 부모 exit, timeout, wrapper 중단에도 적용한다. wrapper가 죽으면 이를 포함한 단위가 자동 정리되는지, 별도 외부 deadline 감시자가 책임지는지 최소 구조를 정한다. wrapper와 함께 사라지는 timer만으로는 이 사례를 통과하지 못한다. runtime 상태를 읽지 못하거나 정리에 실패하면 수집/다음 실행을 차단하고 복구 필요 상태를 기록한다. 시험하려고 사용자 공용 daemon을 실제로 종료하지 말고 관리 경로 오류를 주입해 실패 처리를 검증한다.

S2 과업 제한30분과 컨테이너 준비/마감 정리 시간은 분리한다. probe는 짧은 제한을 사용하고 deadline·요청/실제 정지/수집 시각을 기록한다. 종료 지연을 추가 작업 시간으로 허용하지 않는다. **timeout 뒤 회수한 코드는 진단용이며 정상 성공 제출로 채점하지 않는다.** 작은 종료 지연이 있었다면 그대로 기록하고 정확히 deadline 순간의 snapshot이라고 표현하지 않는다. 정상 종료 뒤에도 전체 단위 정지를 확인한 후 수집한다.

CPU·memory·PID 수에 명시적인 상한을 설정하고 값을 기록한다. 기본 무제한을 사용하지 않는다. 값은 사용 가능한 호스트 자원과 고정 타입 검사 필요량을 확인해 한 번 선택하며 A/B/C에 동일하게 적용한다. 부하 시험은 작은 유한 fixture로 제한하고 호스트 자원 고갈을 유도하지 않는다. 준비·warm-up 시간을 별도 측정하고 성공하는 조건에만 상한을 늘리는 변경은 하지 않는다.

### C. Vendure와 기존 평가의 재현

고정 source·lockfile·Node/TypeScript 버전을 기준으로 Linux에서 필요한 의존성/필수 common 산출물을 별도 준비한다. 필요하면 **Linux 전용 복사본 안에서만** 고정 lockfile 설치·검토한 필수 빌드를 수행할 수 있으며90분 환경 준비 예산에 포함한다. 원본 cache·lockfile·프로젝트 버전을 수정하지 않는다. install/build 시 네트워크·스크립트 실행 내역과 산출물 hash를 남긴다. 광범위한 모노레포 재구축이 필요하면 중단한다.

OS/architecture별 의존성과 Program 구성 차이를 목록화한다. 기존 모델·원문 근거와 정적 배포 ID를 새로운 Linux 환경의 동일성 증명으로 쓰지 않는다. 현재 TASK/B/C84파일·모델 지식은 유지하고, 새 runtime/environment fingerprint를 별도로 만든다. 입력 의미를 바꿔 기존 검증을 억지로 통과시키지 않는다.

작은 baseline/reference 공개 타입 검사부터 실행한다. 이것이 실패하면29제출 전체를 먼저 돌리지 않는다. 성공하면 같은 Linux 제출로 공개/private7제출 대조와 v4의29제출 교정을 실행한다. 정상 결과의 총수만 비교하지 말고 진단 code·위치·메시지, scope/unsupported, 요청 payload·modal/종료 trace·submissionId를 비교한다. 기존 baseline 보존16/16·새 요구6/36, reference/helper52/52,20동작 결함의 타입 통과 후 실패가 유지되어야 한다.

환경 지문·비용·경로가 바뀌면 차이를 명시적으로 분리한다. 시간/정규화한 환경 경로 외 의미 차이를 ‘플랫폼 차이’라는 이유로 삭제하지 않는다. 새 fingerprint와 기존 결과의 비교 규칙·분모를 보고한다. 원래 macOS 평가 결과를 Linux 검증으로 재사용하지 않는다. host의 `pnpm check`·`pnpm experiment`와 Linux의 S2 빌드/관련 통합 검증을 구분하며, Linux에서 실행하지 않은 기존 테스트를 통과로 세지 않는다.

## 6. 필수 검증 표

모델 없는 finite fixture와 알려진 교정 제출만 사용한다. 원래 반례의 동작을 유지하고 바깥 정리 절차도 마련한다. 강제 종료로 쓰기가 안 된 것인지, fixture가 시작되지 않았던 것인지 구분할 시작 신호를 둔다. warm-up이 필요하면 고정 절차와 시간을 별도로 기록한다.

접근 검증은 관리자 쪽에서 canary의 존재를 먼저 확인한다. guest에 아예 마운트하지 않은 경로는 mount/namespace 증거와 함께 판단하고, 실제로 노출된 읽기 전용 경로는 쓰기 거부를 검사한다. 오타나 원래 없는 파일의 ENOENT를 격리 성공으로 세지 않는다.

| 경계 | 필수 사례와 판정 |
| --- | --- |
| 자손 종료 | 정상 부모 종료 후 writer, timeout·detached/새 session·손자·열린 파일 핸들·상속 pipe. 실제 단위 정지 이후 늦은 쓰기/잔존 없음. 핵심 사례는 새 단위2회 |
| 경쟁/실패 | 종료 시점의 유한 자손 생성, wrapper 강제 종료, 관리 명령 오류·상태 확인 불가. 종료 확인 없이 정상 snapshot/다음 실행을 허용하지 않음 |
| 파일/자료 | 자기 source 읽기/편집·자료/고정 의존성 읽기 성공, 자료/고정 의존성 쓰기 거부. control·외부/다른 조건/evaluator canary 읽기/쓰기 거부. symlink/상위 경로·package.json 예외도 검사 |
| 통신/관리 | 셸 외부 TCP·호스트 Unix socket·runtime socket·권한 확대/관리 경계 접근 거부. provider 경로는 stub으로 역할 분리만 확인 |
| 수집 | 전체 production/auxiliary의 추가·수정·삭제 보존, 종료 증거와 같은 unit/경로/hash 결합, 실패 staging 미노출. timeout/종료 미확인 자료는 진단으로 분리 |
| 불변/다음 실행 | 수집 결과·manifest는 평가 권한에서 변경 불가. 이전 단위가 새 단위의 source/자료/control에 접근하지 못하며 잔존 영향 없음. 정상 새 단위의 자기 경로 접근은 성공 |
| 평가 단위 | 알려진 reference를 종료/수집 경로로 전달해 complete-root와 delta의52사례/trace 일치. 평가 쪽의 지연 writer/timeout fixture도 단위 전체 종료. node:vm timeout만으로 통과 판정 금지 |
| 계측/거부 | R12 원래 반례와 종료/EOF/절단 회귀 유지, model/provider0회. fixture receipt로 live/production entry를 열 수 없고 실행 거부 유지 |

단위 종료와 Linux 평가가 통과해도 실제 CLI 모델 세션의 도구 inventory·인증/네트워크 경계까지 검증했다고 표현하지 않는다. 이번 범위에서 가능한 증거와 실제 호출 이후에만 확인 가능한 항목을 분리한다.

## 7. 산출물과 완료 조건

새 `experiments/domain-model/s2/verification/<실제 날짜>-container-feasibility/`에 선택 기록·비용 ledger·환경/이미지/CLI/소스 지문·실행 명령/exit code·원시 probe·교정 대조·cleanup inventory를 보존한다. 경로는 상대화하고 비밀·개인 대화는 넣지 않는다. 이미지/VM 디스크·node_modules는 git에 커밋하지 않는다. 자기 소유 자원만 정리하고 전역 prune을 하지 않는다. 재사용을 위해 보존한 이미지/volume/VM은 ID·크기·이유·삭제 명령을 보고하며 idle 작업 container/writer를 남기지 않는다.

새 타당성 manifest에는 Dockerfile/lockfile/adapter·shell script·새 하위 디렉터리 파일을 포함해 실제 실행에 쓰인 모든 구현과 image digest를 연결한다. 기존 `freeze.ts`의 고정 디렉터리 목록에 새 파일이 자동 포함된다고 가정하지 않는다. 옛 execution manifest를 덮어쓰지 않는다. 정적 자료가 그대로면 기존 bundle을 유지하며, 공개 RUN 안내가 바뀌어야 한다면 변경안을 별도로 인계한다. 본 비교용 재동결은 독립 리뷰 뒤 정한다.

**타당성 검증 완료의 판정은 다음 중 하나다.**

- `feasible-for-next-preparation`: 예산 안에서 한 후보의 CLI/셸 실행 경로·전체 단위 종료·자료/관리 경계·불변 수집·Linux 평가 의미 동등성을 실제 fixture로 확인했다. 실제 provider/모델·계정·사람 승인 미검증 항목은 남아 있음을 명시한다. ‘본 비교 준비 완료’나 R11 전체 독립 해결 판정이 아니다.
- `conditional`: 종료 단위 자체 등 일부는 확인했으나 CLI 버전 변경·인증 경로·환경 동일성·필수 검증 중 하나가 미확정이다. 어떤 증거가 있으며 무엇을 결정/검증해야 하는지 구체적으로 보고한다. 도입 확정/실행 승인으로 취급하지 않는다.
- `blocked` 또는 `inconclusive`: 상한·권한·환경 재현·종료/접근 반례로 후보가 성립하지 않거나 증거가 부족하다. 실패 원문·소모 비용·최소 후속 선택을 보존한다. 다음 후보로 자동 전환하지 않는다.

공통 완료 조건은 실제 결과에 맞는 상태, 비용 상한 준수/초과 내역, 재현 가능한 증거, 실행 중 자원 정리, 기존 자료/제품 계약 보존, `trialAuthorized:false`, `readyForTrial:false`, `results:null`, 실제 모델/본 비교0회다. 실패 인계도 이 조건을 충족하면 이번 조사 작업은 끝낼 수 있다. 기존 R11의 해결 판정은 별도 독립 리뷰 전까지 바꾸지 않는다.

## 8. 보고서와 저장소 반영

`docs/reviews/<실제 날짜>-s2-container-feasibility.md`에 다음을 작성한다.

1. 결론·선택한 후보·base/final commit과 위 판정. 어떤 부분을 실제 확인했는지 먼저 쓴다.
2. 총/단계별 소요 시간·환경 준비90분 사용량·재시도·디스크/다운로드 관측·잔존 자원과 정리 방법.
3. CLI/셸·모델 설정·인증/네트워크의 유지/변경/미검증 표. 버전 차이를 숨기지 않는다.
4. agent 실행과 평가 단위의 권한/종료/수집 흐름, 원래 반례 전후와 실패 시 다음 실행 차단.
5. macOS↔Linux 자료/타입/동작 대조, 테스트/skip/미실행 범위, 새 environment/implementation/이미지 지문.
6. 도입 시 남는 실제 연결 검증·사람 검토·운영 비용과 다음 리뷰에서 결정할 사항. 구현하지 않은 다음 단계를 완료로 쓰지 않는다.

PROGRESS·ARCHITECTURE·ROADMAP·REVIEW_CONTEXT와 관련 README를 실제 결과로 갱신한다. 중요한 선택은 DECISIONS에 근거와 한계를 남긴다. 검증·staged diff 검토 후 지속 승인에 따라 commit → push → PR/자체 검토 → 필수 검사 충족 및 검증한 head 병합 → 로컬 main 동기화까지 수행한다. 예산 중단 시에도 검사 실패를 통과로 표시하거나 보호 규칙을 우회하지 않는다. **저장소 반영 승인은 실제 모델 호출·본 비교 승인이 아니다.**

## 기술 참고

- [Linux cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html): cgroup.kill·populated·자원 제한의 기반 계약. 선택한 런타임/guest가 실제로 이를 제공·사용하는지는 별도 검증한다.
- [Docker bind mounts](https://docs.docker.com/engine/storage/bind-mounts/): 호스트 경로 공유와 쓰기 권한의 경계. 호스트 원본을 쓰기 가능하게 공유하지 않는다.
- [OpenAI CLI 설정](https://learn.chatgpt.com/docs/config-file/config-reference): 도구·권한 설정 참고. 설치한 Linux CLI의 실제 버전/동작과 대조한다.
- [Node.js vm](https://nodejs.org/api/vm.html): JavaScript context는 보안 격리 수단이 아니다. 평가 단위의 OS 종료 경계를 별도로 유지한다.
