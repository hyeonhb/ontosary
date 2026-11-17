# S2 직접 VM CLI 최소 호환성 시험 지시

사용자는 [독립 리뷰](2026-11-17-s2-vm-cli-feasibility-independent-review.md)의 제안에 따라 **총60분·새 VM 최대1개·실제 CLI sandbox 명령 최대1회**의 축소 시험을 승인했다. 개발 세션은 필요한 최소 연결과 로컬 검사, 실제 비모델 명령, 소유 VM 정리, 결과 보고까지 진행한다. 이번에 답할 질문은 **고정 CLI가 해당 VM의 비특권 문맥에서 내부 sandbox를 구성하고 작은 파일 읽기·쓰기 payload를 실행할 수 있는가**다.

직전90분 지시의15분 완료 gate·4단위·VM2 반복은 이번 회차에 적용하지 않는다. 새60분 회차의 최초 시각을 기록하고 과거 회차의 시각/미실행 결과는 보존한다. 전체 C안 채택·R11 해결·실제 자격 증명 전달·모델 호출·본 비교는 결과 리뷰 뒤 결정한다. 이 지시 작성 자체가 시험 실행 결과는 아니다.

## 1. 시작과 변경 범위

최초 명령에서 UTC와 host monotonic을 기록한다. 읽기·설계·구현·준비·대기·검사·실험·정리·보고 모두60분에 포함한다. Git 게시/원격 CI 시간은 별도 기록할 수 있지만 추가 구현·실험에 쓰지 않는다. 지시 작성 기준은 main `d1f0825`다. AGENTS/PROGRESS/ARCHITECTURE/ROADMAP/CONTRIBUTING과 독립 리뷰를 먼저 읽고, 원격·브랜치·사용자 변경을 확인한다.

최신 main의 새 작업 브랜치에서 작은 `experiments/domain-model/s2/trial/vm-cli-smoke/` 경로를 사용한다. [PR #67](https://github.com/hyeonhb/ontosary/pull/67)의 `ed0250b`는 미병합·비활성 초안이며 그대로 활성화하거나 선행 병합하지 않는다. 필요한 선택 추출 코드 등만 출처 commit/path/hash를 적고 가져올 수 있다. 과거 증거와 source hash를 바꾸지 않도록 원래 파일을 수정하지 않는다. 새 PR은 main을 기준으로 만들고 PR #67의 처리도 결과 리뷰에 남긴다.

기존 [공개 준비물/마감/정리 도구](../../experiments/domain-model/s2/trial/container/execution-lifecycle/README.md)와 [VM 설정](../../experiments/domain-model/s2/trial/container/lima.yaml)을 재사용한다. 별도 범용 runner·supervisor/봉인 프로토콜·credential broker·새 검증 프레임워크를 만들지 않는다. 제품 코어·FCA·TASK/모델/B/C·Linux 평가기·동결 배포와 기존 실행 경로는 유지한다.

## 2. 실제 실행 전에 필요한 최소 준비

### 호스트 호환성과 공개 준비물

- 사용할 Python의 실제 경로/버전을 기록하고 그 interpreter로 재사용할 함수와 명령을 검사한다. 직전 호스트 Python3.9.6에서 `hashlib.file_digest`와 `tarfile.extractall(filter="data")`가 지원되지 않았다(R19). 기존 스트리밍 hash/검증된 추출 helper를 우선 사용한다. 이미 설치된 지원 interpreter를 사용한다면 경로를 고정하고 모든 자식 호출에도 같은 계약을 적용한다. 새 Python/패키지 설치와 단순 filter 제거에 의한 보호 해제는 하지 않는다.
- 검증된 cache의 실제 hash와 입력 manifest를 대조하고, 고정 Lima/VZ·Ubuntu ARM64 base·Node22.19.0·CLI `0.167.0-alpha.3.2`를 사용한다. 선택 바이너리/필수 라이브러리/라이선스만 새 소유 임시 경로에 추출한다. rootfs 전체 설치·cache 재생성·download/build/save·Vendure 재설치/common build는0회다. 준비물 또는 필요한 라이브러리가 없으면 근거를 남기고 중단한다.
- 복사할 실행 파일·설정·payload와 실제 실행 argv를 시작 전에 고정하고 hash를 남긴다. 증거 목록은 이번 회차의 작은 파일 집합만 사용한다. 새로 수천 파일의 snapshot 체계나 과거 증거 전체 복사본을 만들지 않는다.

### 소유권·마감·실패 정리

VM 생성 전에 소유 VM 이름/임시 root·시한·정리 수단을 등록한다. 기존 관리 도구에 필요한 얇은 연결만 둔다. wrapper 밖에서 동작하는 기존 마감/VM 폐기 수단을 활용해 SSH나 payload가 멈춰도 소유 VM을 폐기할 수 있게 한다. worker는 이 제어 경로를 수정할 수 없어야 한다.

실제 명령을 가짜 외부 명령으로 대체한 로컬 검사로 **준비 예외·이미 만료된 마감·진단 실패에서도 소유 VM stop/delete와 부재 확인을 시도하는 실제 분기**를 확인한다. watchdog의 `limit()` 예외가 disposal 앞에서 빠져나가는 기존 초안을 재사용하지 않는다. 단순 callback 테스트만 통과시키고 실제 정리 연결이 검증됐다고 표현하지 않는다. 소유권 불명 또는 안전한 폐기 수단 미확보라면 VM을 시작하지 않는다.

모든 cache 조회·추출·전송·SSH·lock·VM 시작/종료 명령에 남은 시간보다 짧은 timeout을 전달한다. host와 guest의 monotonic 값을 직접 비교하지 않는다. 정리 호출은 실험 마감 예외와 분리하고 이미 끝난 실험을 재개하지 않는다.

## 3. VM과 worker의 최소 경계

새 VM1개에 기존 고정 자원 설정을 사용한다. 호스트 홈/키체인/인증·공유 mount·SSH agent forwarding·runtime/관리 socket을 worker에게 제공하지 않는다. guest 관리자가 전용 비특권 사용자를 준비할 수 있으며 worker에 sudo/관리 그룹·추가 capability를 주지 않는다. worker의 capability0·no-new-privileges와 CPU2·메모리4GiB·TasksMax256을 기본 OS service/cgroup 설정으로 적용하고 실제 상태를 기록한다. 새 service 수명주기 플랫폼은 만들지 않는다.

CLI 실행 전에 관리자 통제로 worker의 외부 통신을 차단한다. 예를 들어 기존 OS의 격리된 network namespace 설정을 사용할 수 있다. 실제 namespace/인터페이스/route를 읽어 적용 상태를 확인한다. CLI 설정이나 proxy 환경 변수만으로 차단됐다고 판단하지 않고, 외부 provider/LAN/metadata에 접속해 시험하지 않는다. VM 관리 통신은 별도다.

전용 HOME/CODEX_HOME/source/scratch와 읽기 전용 materials를 새로 만든다. 최소 환경과 고정 설정을 사용하고 호스트의 세션·인증·전역 지시·skills/MCP/apps/plugins를 상속하지 않는다. 실제 인증 파일은 읽거나 복사하지 않는다. CLI writable 상태는 필요한 worker 소유 경로로, 고정 config는 관리자 소유 불변 파일로 구분한다.

기존 CLI fixture 프로필에서 경로만 최소 이식해 내부 sandbox를 유지한다. root CLI, sandbox 우회/승격, `danger-full-access`, 추가 capabilities, AppArmor/seccomp 전역 해제, sysctl 완화, setuid 우회, 도구/후보 교체는 하지 않는다. 기존 guest 정책으로 시작할 수 없으면 차단 근거를 관측한 결과로 종료한다.

이번에는 가짜 인증·Unix socket/proc/상속 FD의 전체 부정 대조를 구현하지 않는다. 따라서 R19의 socket 생성 초안을 가져오거나 그 결함을 고치는 것을 선행 조건으로 삼지 않는다. 해당 결함은 미사용/후속 검토로 남기며 R19 전체 해결이라고 선언하지 않는다.

## 4. 실제 관측 한 번

기본 준비 뒤 고정 CLI의 version/help 등 비모델 지원 탐색은 합계 최대4회다. 실제 고정 버전에서 지원하는 인자를 사용한다. Node 버전과 필요한 도구 식별도 기록하되 별도 sandbox 시험을 먼저 실행하지 않는다.

실제 CLI `sandbox` 명령은 최대1회다. 그 명령 내부의 CLI 자체 사전 검사와 실제 payload를 구분하며, helper 직접 실행이나 version/help 성공을 payload 성공으로 세지 않는다. 관리자 측 argv·바이너리 hash·설정·시작/종료 시각·PID/worker identity·실제 exit code·원시 stdout/stderr를 남긴다.

payload는 고정된 작은 셸 또는 Node 프로그램으로 다음만 수행한다.

1. 고유 run ID와 시작 표식을 출력한다.
2. 합성 source 파일의 예상 내용을 읽고 새 파일을 쓴 뒤 같은 내용을 다시 읽는다.
3. 제공된 materials 파일의 예상 내용을 읽는다.
4. 세 확인 결과와 완료 표식을 출력하고 명시적인 exit code로 끝낸다.

숨겨진 평가 자료·실제 Vendure 과업·agent 생성 코드·네트워크 요청은 없다. 프로그램/입력 hash와 기대값을 사전에 남긴다. 시작 표식만 있거나, 완료처럼 보이는 문자열만 있고 실제 종료/내용 확인이 없으면 통과로 보지 않는다. 오류·관측 누락·출력 절단은 그대로 남긴다.

payload는 최대15초, 해당 명령의 준비/실행/종료 관측은 외부120초 이내로 제한한다. 45분 실험 종료 시각 안에 이 제한과 정리 여유가 들어가지 않으면 새 명령을 시작하지 않는다. 실제 명령을 한번 시도한 뒤 코드·설정·권한을 바꿔 재시도하거나 추가 trace 실행을 하지 않는다. 시작 전 로컬 보완은 전체 예산 안에서 가능하다.

호스트가 받은 stdout/stderr와 고정 관리 명령의 응답만 유한 진단으로 보존한다(스트림당1MiB, 전체 회차4MiB 이내; 초과/절단 명시). 임의 guest 디렉터리 export나 평가 가능한 제출 수집을 만들지 않는다. 결과 관측 직후 소유 service/VM을 정리하고 실제 VM/소유 프로세스 부재를 확인한다. 여기서 VM 폐기는 이번 호환성 시험의 안전 정리이며, 이전 R11의 모든 writer 종료→불변 제출 수집 보장을 증명한 것으로 쓰지 않는다.

## 5. 시간 운영과 중단

- **0분:** 최초 시각과60분 절대 마감을 기록한다.
- **15분:** 진행 상황·확인한 장애·남은 작업을 점검/기록한다. 최소 구현이 아직 끝나지 않았다는 이유만으로 중단하지 않는다. 필요한 준비만 남기고 범위가 커지면 축소/중단을 판단한다.
- **45분:** 실제 관측을 마치고 새 준비·실험·디버깅을 중단한다. 이후15분은 정리·로컬 검사·보고에 사용한다. 최종 VM 폐기에 최소90초를 확보한다.
- **60분:** 검사·정리·보고까지 완료한다. 안전 정리가 초과하면 정리만 계속하고 초과 시간과 잔여 자원을 공개한다.

핵심 관측을 얻으면 예산을 채우기 위해 추가 구현하지 않는다. 추가 권한/새 패키지/다른 CLI가 필요함, 공개 준비물 무결성 불일치, 외부 통신 차단 미확보, 소유권/정리 경로 불명 또는 실제 실행 실패가 확인되면 새 실험을 중단한다. 마지막 경우는 이미 얻은 원문 진단으로 판단하고 동일 후보를 반복 조정하지 않는다. C안 전체 실패와 개별 준비/명령 실패를 구분한다.

## 6. 검증과 결과 인계

로컬 검사는 실제로 재사용하는 호스트 해시/추출 경로, 마감/정리 분기, 작은 payload 기대값과 결과의 누락/절단 거부에 집중한다. 변경한 공유 함수가 있으면 영향받는 회귀를 추가 실행한다. `pnpm check`를 완료하고 실패/시간 부족은 그대로 보고한다. 제품 분석·평가 의미가 불변이면 `pnpm experiment`·Linux 평가 전체 반복·과거 verifier 전체 반복은 하지 않는다.

새 날짜별 `docs/reviews/YYYY-MM-DD-s2-vm-cli-smoke.md`와 작은 증거 디렉터리에 다음을 남긴다.

- 시작/종료·준비/실행/정리/검사/보고 시간, 기준/실행 코드 head/hash, 사용한 interpreter·공개 준비물과 실제 버전.
- 최소 구조와 적용된 worker 권한/자원·네트워크, 고정 설정/argv/payload/input hash, 원문 출력·실제 종료 결과.
- VM 생성/삭제, CLI 탐색/실제 sandbox 횟수, 예상 읽기/쓰기 결과와 미관측 목록, 정리 결과 및 남은 자원.
- 기존/PR #67에서 재사용한 부분과 수정 이유, R19의 이번 처리 범위, 다음 통합에 필요한 작업과 비용 판단.

관측은 `payload-completed`, `blocked-before-payload`, `payload-failed`, `inconclusive` 중 근거에 맞게 기록하고 cleanup 상태를 별도 둔다. `payload-completed`는 고정 입력의 읽기/쓰기와 실제 CLI 명령 종료가 확인됐다는 뜻이다. 격리 계약 전체나 다음 통합 완료를 의미하지 않는다. 로컬 검증·원문 근거·소유 자원 정리까지 확인해야 이번 작업의 완료로 인계한다. 차단/시간 부족도 근거와 정리 상태를 남겨 정직하게 인계할 수 있다.

PROGRESS/ARCHITECTURE/ROADMAP·README를 실제 결과로 갱신하고 중요한 관찰을 DECISIONS에 추가한다. 과거 실패/중단 증거를 덮어쓰지 않는다. R11 unresolved·R12 기존 범위·production/live 거부·fixtureOnly=true·validSubmission=false·trialAuthorized=false·readyForTrial=false·results=null·H-O/H-F 미검증을 유지한다. 실제 credential 전달/로그인/갱신/provider/model/본 비교는 각각0회다.

검증·커밋·push·새 PR 생성까지 인계하되 **독립 결과 리뷰 전 병합하지 않는다.** PR #67은 자동 병합/폐기하지 않는다. 종료·수집 통합, 전체 접근 경계, 반복 시험, 실제 인증·모델 호출·본 비교는 이 결과를 리뷰한 뒤 별도 결정한다.
