# S2 진단 보존과 종료 봉인 및 정리 보완 지시

2026-11-17. [독립 리뷰](2026-11-17-s2-execution-lifecycle-fix-independent-review.md)의 R15 잔여·R16·R17을 보완한다. 동일 Lima/VZ·containerd/nerdctl 경계 안에서 실패 진단 보존, service 종료 증거 확보, 증거 회수와 자원 정리의 책임 분리를 구현한다. **직전과 같은 새 3시간 상한**이며 로컬 통합 회귀 뒤 새 VM 1개에서 기본 정책의 필수 7단위까지 검증한다. 구현 PR은 결과 리뷰에 제출하고 정책 대조·추가 권한·실제 인증·모델 호출·본 비교는 진행하지 않는다.

## 기준과 범위

AGENTS, PROGRESS, ARCHITECTURE, ROADMAP, CONTRIBUTING, 위 독립 리뷰와 [직전 보완 지시](2026-11-14-s2-execution-lifecycle-fix-instructions.md)를 먼저 읽는다. 구현 기준은 PR #54의 `ff7ec19ebc7e3e12380fb82cc6a377d5aaf4dd6c`이며 원격/현재 head/사용자 변경을 확인한다. 최신 main의 리뷰와 이 지시를 통합하고 PR #54 작업 브랜치를 이어 수정한다. 의존 브랜치를 따로 쓰면 기준을 기록한다. 과거 ADR-048/050·보고서·증거는 보존하며 공유 브랜치를 force-push하지 않는다.

직전에는 pnpm check 304개와 Python 146개가 통과했다. R14는 실제 cache hit·build/download/save 0회·import 1회로 확인됐으므로 재설계하지 않는다. R13의 고정 PATH/엄격한 hook 배열·전체 Spec 비교도 유지하되 이번에 실제 도구/Spec 원문을 보존해 검증을 마친다. 첫 정상 단위의 exit 0·삭제 1.566초와 service 봉인 실패, metadata owner 거부를 구분한다. 이전 실패의 정확한 systemd 조회값이나 GC를 확정 원인으로 가정하지 않는다.

수정 범위는 `execution-lifecycle/`의 준비 metadata 게시·export·engine 봉인·round cleanup·검증기와 회귀, 필요한 최소 공유 collector/시간 처리, 관련 문서다. 제품 core/CLI, FCA, 모델·TASK/B/C·배포 ID, Vendure 평가 의미와 과거 원시 자료는 불변이다. 새로운 실행 플랫폼·상시 VM·범용 이벤트/증거 시스템·새 패키지 의존성으로 확대하지 않는다.

최초 명령에서 UTC와 host monotonic을 기록하고 최초 inventory·수정 허용 범위·실행 순서·분모·소유 자원·마감·snapshot 분석/closing 범위를 고정한다. `fixtureOnly=true`, `validSubmission=false`, `trialAuthorized=false`, `readyForTrial=false`, `results=null`, R11 unresolved·R12 기존 범위·production/live 거부를 유지한다.

## 1 R17 정리가 증거 회수 실패에 의존하지 않게 한다

가장 먼저 [독립 재현](evidence/2026-11-17-probe-cleanup.py)의 archive copy 실패와 export transport 예외를 실제 `Round.cleanup()` 회귀로 옮긴다. 수정 전에는 VM stop/delete가 호출되지 않는지 확인한다. 새 VM을 만들지 않고 가짜 외부 명령과 임시 소유 경로로 검증한다.

cleanup을 다음 세 책임으로 나눈다. 작은 함수와 기존 소유 기록으로 구현하며 별도 프레임워크를 만들지 않는다.

1. **유한 증거 회수:** export·archive/index copy의 각 결과와 오류를 기록한다. 기록 저장 자체의 실패도 후속 정리를 막지 않는다. 실패한 copy의 부분 파일은 유효 archive로 게시하지 않는다.
2. **최종 자원 정리:** 회수 성공 여부와 무관하게 소유 VM stop, delete, 부재/소유 process 확인을 시도한다. stop 오류 하나가 delete 시도를 막지 않도록 각 오류를 보존한다. 확인되지 않은 삭제를 성공 처리하거나 살아 있는 VM의 관리 root를 먼저 지우지 않는다. 소유권이 불명확하면 타 자원을 삭제하지 않고 잔여를 명시한다.
3. **결과 확정:** evidenceStatus와 cleanupStatus를 분리한다. 회수 실패/정리 성공, 회수 성공/정리 실패, 둘 다 실패를 표현한다. 최초 원인과 정리 중 추가 오류를 덮어쓰지 않는다. 중복 cleanup에서도 다른 실행을 지우거나 지난 archive를 이번 결과로 재사용하지 않는다.

최상위 예외 경로도 이 구조를 거쳐야 한다. `check=False`만 늘리거나 전체 예외를 삼키는 방식은 허용하지 않는다. 최초부터 같은 절대 마감을 전달하고 회수는 정리 reserve 이전에 끝낸다. 회차 종료 정리 진입 시 남은 시간 중 최소 90초를 stop/delete/부재 확인에 남기고, 회수는 최대 30초와 `남은 시간-90초` 중 작은 값만 쓴다. 잔여가 부족하면 회수를 생략한 사유를 기록하고 정리를 우선한다. 정리 command timeout도 각각 잔여에서 차감하며 새 예산을 시작하지 않는다.

필수 로컬 사례: export 비정상 exit, 호출 예외/timeout, archive copy 실패, index copy 실패, 회수 결과 기록 실패, stop 실패 후 delete 시도, delete/부재 확인 실패, 마감 부족, 중복 cleanup. 각 경우 명령 순서·소유권·잔여 상태·부분 파일 미공개를 검증한다. 안전 정리가 필요해 상한을 넘으면 새 실험 없이 정리만 계속하고 초과를 보고한다.

## 2 R15 전달 metadata를 관리자 소유로 게시한다

`image-export.json`의 copy→sudo mv를 검증된 관리자 게시로 바꾼다. `input-members.json` 등 같은 방식으로 전달하는 제어 metadata도 필요한 범위에서 함께 점검한다.

- 전달 staging은 worker가 접근하지 못하는 회차 소유 경로를 쓴다. 예측 가능한 임시 파일에 대한 무조건 chown/mv 대신, 정규 파일·symlink/hardlink 거부·크기 상한·기대 hash/스키마/입력 binding을 검증한다.
- 검증된 바이트를 관리자 소유 임시 파일에 작성하고 mode를 제한한 뒤 원자 게시한다. 검증한 파일을 경로로 다시 열어 교체된 내용을 게시하지 않도록 기존 FD 읽기 기능을 재사용한다. 게시 후 UID/mode/hash를 확인하고 worker 쓰기 가능 경로가 없음을 확인한다.
- 이미지 archive 입력/출력 binding과 import identity 검증을 유지한다. export의 관리자 UID 검사를 완화하거나 옛 cache manifest를 수정하지 않는다. helper/입력 archive가 보존한 ownership도 현재 계약과 충돌하지 않는지 확인한다.

준비→전달→게시→import→export의 로컬 통합 회귀를 둔다. 실제 준비 진입점이 관리자 게시 helper를 호출하는지 확인하고, 일반 사용자 소유 전달 파일을 가정한 실패/허용 흐름·내용 변조·잘못된 owner/mode·부분 게시를 검증한다. 호스트 테스트를 위해 sudo를 요구하지 말고 stat/UID 경계를 명시적으로 대역화하며, 실제 root 소유 검증은 아래 같은 VM에서 확인한다. 모든 fixture를 같은 UID로 만들어 소유권 차이가 사라지는 테스트로 끝내지 않는다.

## 3 R15 정상 결과와 실패 진단의 포장을 분리한다

worker 결과는 기존 collector가 검증·봉인한 관리자 소유 산출물만 읽는다. collection 실패/철회/종료 불명확이면 worker 원본을 다시 읽지 않는 계약을 유지한다. 정상 결과 포장은 전체 검증 후 원자 공개한다.

별도로 **검증된 관리자 진단만 담는 실패 진단 경로**를 둔다. 기존 allowlist·SafeFiles·hash/index를 재사용하고 run identity, 원본 Spec/치환/전체 diff, 도구 해석, service raw 조회, 종료/삭제 상태와 오류를 담는다. 임의 run tree나 worker 상태 파일을 관리자 진단으로 자동 편입하지 않는다.

파일 하나의 owner/kind/hash 거부는 그 파일을 제외하고 거부 이유를 index에 기록하되, 이미 검증한 독립 진단까지 폐기하지 않게 한다. 경로의 부모/소유 범위 자체를 신뢰할 수 없으면 그 subtree를 더 탐색하지 않는다. 파일 수·누적 바이트·시간 상한 도달 시 추가 수집을 중단하고 미수집 이유/범위를 표시한다. 실패 결과의 일부를 정상 결과인 것처럼 포장하지 않는다. 진단 artifact 자체의 검증/원자 게시가 실패한 경우에는 작은 관리자 오류 receipt만 남기고 정리로 넘어간다.

정상 결과·실패 진단·오류 receipt 모두 해당 회수의 **같은 누적 상한**을 사용한다. worker collector 128파일/16MiB, 회수 전체 1,024파일/16MiB와 기존 깊이/시간 제한을 유지한다. 상태·index·거부 목록도 합산하며 reserve를 작게 선할당해 상한 초과 이유를 기록할 공간을 남긴다. fallback마다 16MiB나 timeout을 새로 주지 않는다. archive/index는 함께 검증해 공개하고 partial/diagnostic/complete 상태를 명확히 구분한다.

원본 Spec·runtime 도구·service 종료 조회를 마지막 전체 export 한 번에만 의존시키지 않는다. 관리자 소유 핵심 진단을 단계별로 봉인하고 정상/실패 단위 종료 후 제한된 경로로 호스트에 회수한다. 정리 reserve 안에서 회수하지 못하면 누락으로 기록하며 VM 정리를 지연하지 않는다. 기존 snapshot 등록/closing/전체 index에 연결하고 완료되지 않은 단위의 자료를 성공 증거로 승격하지 않는다.

필수 회귀: 정상 결과와 정확한 members, metadata 하나 거부 시 다른 허용 진단 보존, service 원문 보존, 거부된 worker hardlink canary 미포함, suppressed/failed/quarantined/pending의 원본 미접근, 부모 symlink/특수 파일/과대 파일 거부, 누적 상한·시간·fallback reserve, archive/index 중간 실패 미공개. 최종 verifier는 자료가 없는 경우와 대조가 성공한 경우를 구분하고 유효 결과와 실패 진단의 판정을 혼용하지 않는다.

## 4 R16 service 상태를 봉인까지 보존한다

기존 독립 관리자 관찰자가 **실행 service의 systemd reference를 시작 전부터 봉인 또는 차단 기록 확정까지 유지**하도록 한다. 같은 systemd 안에서 구현하는 국소 변경이며 새 backend나 worker 권한 추가가 아니다. 구현 표현은 고정 환경에서 이미 이용 가능한 도구를 사용하고 최초 계획에 선택·보유자·획득/해제 시점·보유자 사망 시 처리를 적는다.

관리자 소유 loaded unit의 의존 참조 또는 살아 있는 IPC client의 reference 등 실제 수명을 유지하는 방법 중 최소 구현을 선택한다. 일회성 `RefUnit` 호출 뒤 연결 종료나 unit 파일 존재만으로 reference가 유지된다고 가정하지 않는다. 불필요하게 worker service를 다시 start/restart하는 의존 관계를 만들지 않는다. 새 라이브러리/상주 daemon/이벤트 플랫폼이 필요해지면 범위를 확대하지 말고 부분 인계한다. [systemd v260의 unit 수명 문서](https://github.com/systemd/systemd/blob/v260/man/systemd.unit.xml#L512)가 근거이며 이전 실패의 GC 발생을 확정한 것은 아니다.

구현 순서는 다음과 같다.

1. 소유 run/service 기록과 reference 보유자를 먼저 등록하고 보존이 준비됐음을 확인한 뒤 service를 시작한다. 관리자 생존/마감은 기존 독립 종료 체계 안에 둔다.
2. 조회할 때 원시 stdout/stderr·exit code·관찰 UTC/guest monotonic을 먼저 보존한다. LoadState, ActiveState, SubState, service 이름/InvocationID 등 실행 식별 근거, InactiveEnterTimestampMonotonic, Result와 필요한 종료 상태를 함께 남긴다. 같은 이름의 새 invocation/재시작·not-found/재로드를 과거 실행 종료로 오인하지 않는다.
3. 기존 전체 cgroup 종료·runtime pending 해소·task/container 부재·ExecStopPost 완료와 해당 invocation의 비활성 시각을 대조한 뒤 봉인한다. 원래 guest 마감과 외부 120초를 모두 지킨다. 종료 관찰/봉인 기록을 원자 저장한 뒤에만 reference를 해제하고 unit 파일·관리자 보유 자원을 정리한다. 다음 실행은 이 정리까지 확인된 후 연다.
4. reference 보유자 사망/보존 실패, timestamp 0/누락/마감 밖, invocation 불일치면 결과와 다음 실행을 차단하고 실패 진단을 회수한다. worker exit0·빈 cgroup·VM 폐기·현재 시각 대입으로 봉인을 대체하지 않는다. polling 주기 단축만으로 해결했다고 하지 않는다.

로컬 runtime 대역은 show마다 현재 시각을 생성하지 말고 명시적 상태/시각을 가진다. 정상·failed·deactivating·unloaded/not-found, 0/누락·마감 초과, 늦은 관찰, 같은 이름의 다른 invocation, reference 해제/보유자 실패를 검사한다. 정상 경로는 reference 획득→start→finalizer→원시 증거→봉인→release→다음 실행 순서를 확인한다. 실제 systemd 동작은 아래 첫 정상 단위에서 검증하며 대역 통과를 실제 증명으로 세지 않는다.

## 5 같은 기본 정책의 필수 7단위

위 로컬 회귀가 모두 통과한 코드 hash와 계획을 동결한 뒤 새 VM 1개를 만든다. 검증된 공개 준비물을 재사용하고 실제 cache hit의 download/build/save 0회 및 import target/config/chain을 다시 기록한다. 보관량 10GiB를 유지한다. 정상 cache가 없거나 무결성/입력 불일치면 이번은 재빌드·재다운로드 없이 부분 인계한다. 실행 상태·VM·source/output/HOME/CLI 상태/scratch는 새로 만든다.

| 단위 | 이번에 반드시 추가 확인할 연결 |
| --- | --- |
| 정상 1 | metadata의 실제 관리자 UID/mode/hash, 고정 env 도구 원문, 전체 native Spec·치환/diff, service reference와 실제 비활성 시각, 정상 봉인·archive·호스트 회수 |
| 생성 후 사전 검사 실패 | start0·자동 삭제·결과 suppressed, 실패 원인과 Spec 원문 진단 보존 |
| 시작 실패 | pending 정착·task/container 부재·service 종료·실패 진단 |
| timeout | 분리된 자손 전체 종료·늦은 쓰기 없음·제한된 진단·명시적 복구 |
| host wrapper 사망 | 호스트에 의존하지 않는 게스트 종료/삭제·봉인·진단 보존 |
| 작업 supervisor 사망 | 독립 종료 후 처리·결과 철회·다음 실행 차단·안전 복구 |
| 정상 2 | 새 상태·이전 canary 접근 거부·같은 cache 재사용·정상 봉인·최종 회수 |

기존 AppArmor/rro·seccomp·network none·UID/GID1000·capability0·NNP1·RO root/cgroup·CPU2·메모리4GiB·PID256·tmp64MiB를 유지한다. R13은 실제 도구 해석과 native Spec 원문·전체 diff를 저장하고 오프라인에서 재대조해야 완료다. 이전 PATH 없는 실패 원문을 새 기대값으로 덮어쓰지 않는다.

기대 실패 주입과 예상 밖 운영 실패를 구분한다. 준비 신호에 맞춰 주입하고 같은 단위 재시도/숨은 smoke/선택적 8번째 실패 주입/정책 pair는 하지 않는다. R17의 통신·copy 실패 주입은 우선 로컬에서 충분히 검증하며 실제 7단위의 진단 회수·최종 VM 정리 연결을 관찰한다. 이번에 추가 VM으로 transport 실패를 일부러 만들지 않는다.

## 비용과 중단 기준

읽기·계획·구현·실패·대기·검증·정리·보고를 최초 시계부터 **180분**에 포함한다. 60분까지 로컬 회귀·계획 완료, 100분까지 환경 준비, 150분에 새 runtime 관찰/구현 탐색 종료, 180분까지 정리·인계다. 60분 gate를 못 넘으면 VM을 시작하지 않는다. 환경 진입은 최초 한 번 `min(진입+20분, 회차 시작+100분)`으로 고정한다. 유료 비용0·새 VM1개·실제 fixture 최대7·build0이다.

단위 등록부터 정리/제한 수집/봉인까지 120초, 준비/실행80초·삭제110초·봉인120초, payload15초를 유지한다. reference 획득/해제와 진단 처리를 기존 마감에 포함하고 별도 무제한 wait를 만들지 않는다. 호스트/게스트 monotonic을 직접 비교하지 않는다. 새 단위120초와 회차 정리 여유가 없으면 시작하지 않는다.

필수 회귀 실패, 같은 입력/버전/owner/hash 불일치, 미분류 Spec 차이, 추가 권한 필요, 소유권·reference·종료·삭제·pending 불명, 상한 도달이면 새 실행을 멈춘다. 실제 실패 뒤 코드를 바꾸어 같은 단위를 재시도하지 않는다. 실패 진단 회수와 소유 자원 정리를 완료하고 부분 결과를 남긴다. 예산은 목표 사용량이 아니며 일찍 차단되면 즉시 정리·인계한다. Git 게시 시간은 따로 기록하고 실험 재개에 쓰지 않는다.

## 완료 조건과 제출물

- R15: 실제 관리자 metadata 게시와 정상 export, 로컬 거부 사례에서 안전한 실패 진단 보존·원본 미접근·누적 상한·원자 공개가 검증됨.
- R16: 실제 정상 service의 종료 증거와 봉인이 확인되고, 상태 소실/식별 불명/마감 초과에서는 결과를 거부함. reference와 관리자 자원이 남지 않음.
- R17: 실제 cleanup 진입점의 회수/기록/stop/delete 실패 회귀에서 후속 정리가 실행되고 실패와 잔여가 정확히 보고됨. 실제 VM 정리·부재 확인도 완료됨.
- R13 실제 도구/전체 Spec 재대조와 R14 재사용 회귀를 유지하고 필수7단위가 각 기대 결과·정리·마감·다음 실행 계약을 충족함. 미실행/증거 누락은 부분 완료로 남김.
- `pnpm check`, execution-lifecycle/공유 lifecycle·collector·감사/deadline/package·production/live 거부 회귀, 과거/새 저장 verifier를 통과함. 기준304/146에 새 테스트·skip·반복을 정확히 구분함. TS 분석/평가 불변이면 `pnpm experiment`와 Vendure 전체 평가 반복은 생략 이유를 기록함.
- 최초/전달/실행/최종 코드와 불변 입력 hash, 명시적 분석/closing snapshot·최종 index, 의도한 코드 변경을 연결함. 원시 실패를 삭제하거나 새 성공으로 대체하지 않음.

보고서는 `docs/reviews/2026-11-17-s2-seal-recovery.md`, 증거는 `experiments/domain-model/s2/verification/2026-11-17-seal-recovery/`에 저장한다. 실제 날짜가 다르면 맞추고 과거 경로를 덮어쓰지 않는다. PROGRESS/README에 실제 결과를 갱신한다. 인계에는 항목별 완료/미완료, reference 선택 근거·수명/실패 경로, metadata 게시 기록, 정상/실패 진단 members와 누락 사유, cleanup 오류/시도/잔여, 7단위 분모, raw Spec/service 대조, 비용과 원시 증거 경로를 포함한다.

커밋·push·PR #54 갱신까지 수행하고 독립 결과 리뷰를 기다린다. 이번 성공은 R11 전체 해결·모델 효용 검증이나 본 비교 승인으로 확대하지 않는다.
