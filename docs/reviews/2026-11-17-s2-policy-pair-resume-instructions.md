# S2 기존 정책 한 행 대조 재개 지시

2026-11-17. [정리 호출 보완 독립 리뷰](2026-11-17-s2-cleanup-dispatch-independent-review.md)에서 PR #54의 R13~R17 보완을 확인했다. 다음 개발 세션에는 **기존 원래 정책1회와 이미 정한 clone allow 한 행 후보1회**의 제한된 관찰을 권고한다. 같은 실행 경계를 쓰며 새 구조/후보/권한 집합을 설계하지 않는다. 권장 회차 상한은 **45분, VM1개, container 최대2개, 유료 비용0**이다. 이 문서 작성 세션에서는 실제 시험을 실행하지 않았다.

## 목표와 기준

목표는 앞서 실행 전에 막혔던 후보의 정책 효과를 처음 관찰하는 것이다. 원래 정책에서 같은 clone EPERM이 재현되는지, 후보에서 해당 clone이 통과하는지와 다음 차단점이 무엇인지 판별한다. 전체 CLI/인증/네트워크 경계나 실제 agent 수정 효용은 이번 목표가 아니다.

AGENTS·PROGRESS·ARCHITECTURE·ROADMAP·CONTRIBUTING, 위 독립 리뷰, [정책 후보](2026-11-11-s2-namespace-policy-proposal.md), [이전 재개 지시](2026-11-12-s2-policy-retry-instructions.md)를 읽는다. 코드 기준은 PR #54 병합 `7f2f179`이며 실제 시작 main과 차이를 기록하고 새 짧은 작업 브랜치를 사용한다. 기존 11월 17일 기본 정책7단위는 오프라인 증거로 유지하고 같은7개를 새 VM에서 다시 반복하지 않는다.

최초 명령에서 UTC와 host monotonic을 **동시에** 저장한다. inventory·변경 허용 범위·정확한 분석/closing 명령·소유 자원·절대 마감·원래/후보 분모를 먼저 고정한다. 과거 보고/증거/manifest를 수정하거나 과거 남은 시간을 이번 예산으로 재사용하지 않는다.

## 1. 공통 실행기에 제한된 대조를 연결한다

현재 `round.py pair`는 보완 회차용으로 명시적으로 거부하며 아래의 과거 코드는 실행 검증된 새 대조 경로가 아니다. 단순히 raise를 지우고 옛 helper를 실행하지 않는다. 새 회차의 명시적 목적·허용 mode·maximumUnits=2와 고정 후보를 확인한 경우에만 공통 unit 경로를 사용하도록 최소 연결을 만든다. 과거 보완 계획이나 목적/분모가 없는 계획에서는 pair 거부를 유지한다.

기존 7단위 통과 자료의 hash/범위를 계획에서 참조하고 로컬 회귀를 통과시킨다. 기존 `fixtures-complete`를 가짜로 만들거나 requiredUnits=7을2개 실행으로 채우지 않는다. 이번 회차의 preparation/local code gate와 각 단위 실제 Spec·봉인·회수 gate를 유지한다. 재개를 위해 새로운 범용 workflow 시스템을 도입하지 않는다.

pair의 예외도 검증된 `failed_dispatch()`와 기존 recovery를 거쳐 감사 실패와 무관하게 소유 자원 정리를 시도해야 한다. baseline 실패 시 candidate를 시작하지 않고, baseline/candidate 어느 쪽의 관찰·회수 실패도 다음 실행을 막는다. 새 실제 진입점에서 정상 대조 순서·기준 불일치·감사/회수 오류·정리 호출·무승인 계획 거부를 로컬 대역으로 검증한다. 기존 193개 Python 회귀와 정책 전체 비교/부정 회귀를 유지한다.

수정 범위는 공통 round의 제한된 대조 연결, 이번 계획/관찰·오프라인 verifier와 회귀/문서다. 공통 engine/reference/recovery/collector·권한/이미지 구조·제품/모델/평가 의미를 바꿔야 하면 이번 시험을 중단하고 근거를 인계한다. 코드 동결 이후 실제 실패를 수정해 재시도하지 않는다.

## 2. 검증된 준비물을 새 VM에서 재사용한다

같은 Lima/VZ·고정 이미지·Node22.19.0·CLI0.167.0-alpha.3.2·nerdctl 버전/바이너리 hash를 유지한다. 공개 보관 준비물의 실제 hash/입력 key/출력 archive·OCI target/config/chain을 검사하고 새 VM에 import한다. cacheOnly=true·download/build/save0·import1이며 cache 누락/불일치면 중단한다. 새로운 설치/이미지 수정으로 회차를 소비하지 않는다. 보관 상한10GiB를 유지한다.

VM·source/output/HOME/CLI 상태/scratch는 새로 만든다. 원래/후보도 서로 새로운 writable 상태와 실행 ID를 사용한다. 이미지·합성 입력·비모델 명령·trace 옵션은 같게 고정하고 그 차이와 소유 관계를 확인한다. host home·키체인·실제 auth/config/env·runtime socket을 worker에 노출하지 않는다. worker network none과 기존 보안/자원 제한을 유지한다.

## 3. 원래1회 → 후보1회만 관찰한다

1. 원래 정책에서 parent의 합성 source/material 양성 동작, 실제 CLI/Node/hash, 첫 clone flags `0x78020011`의 EPERM을 확인한다. 기준이 예상과 다르면 후보를 시작하지 않는다. baseline의 전체 Spec·trace·service 조회·봉인·회수 원문을 보존한다.
2. 해당 원래 OCI seccomp 전체를 복제해 다음 행만 추가한 container 전용 profile을 만든다. 기존 규칙/defaultAction/architecture 목록은 유지한다.

```json
{"names":["clone"],"action":"SCMP_ACT_ALLOW","args":[{"index":0,"op":"SCMP_CMP_EQ","value":2013397009}]}
```

3. 후보 create 뒤 start 전에 실제 native Spec 전체를 비교한다. 검증된 소유 ID·경로·정확한 runtime hook 환경 대응만 치환하고 원문/치환표/전체 diff를 남긴다. 유일한 정책 차이가 위 행인지 검사한다. 미분류 차이를 기대값에 추가하거나 보안 필드만 골라 비교하지 않는다.
4. 후보 시작은 최대1회다. trace에서 clone 반환값과 부모/자식 관계를 확인하고 사전 검사와 명령 준비의 bwrap 호출을 구분한다. clone이 여전히 거부되거나 다음 syscall/LSM에서 막히면 그 자리에서 멈춘다. payload가 완료되면 합성 payload 완료까지만 보고한다. 추가 trace container/숨은 smoke/동일 단위 재시도는 없다.
5. 공통 unit의 실제 종료·pending 해소·cgroup/task/container 부재·동일 service invocation 비활성·봉인·reference 해제·제한 수집을 유지한다. CLI parent exit나 VM 폐기를 단위 종료 증명으로 대신하지 않는다. 각 단위 후 진단을 회수하고 최종 VM/임시 root를 정리한다. 종료 불명 시 결과·후속 실행을 차단한다.

추가 clone flags/clone3/unshare/setns/mount 허용, capability/NNP/AppArmor/sysctl 변경, unconfined, 다른 backend/CLI/API/proxy는 제외한다. 기존 한 행은 profile을 공유하는 모든 자식에게 적용되며 특정 bwrap만 허용하는 정책이 아니다. 실제 자격 증명 전달·로그인·갱신·provider/model 호출·본 비교는 하지 않는다.

## 시간·중단 기준

읽기·국소 연결·회귀·준비·대조·정리·검사·보고를 새45분에 포함한다. 15분까지 로컬 계약/계획을 동결하지 못하면 VM을 시작하지 않고 부분 인계한다. 환경 마감은 최초 진입 때 `min(진입+20분, 회차 시작+25분)`으로 한 번만 정하고 중첩 명령은 같은 잔여를 쓴다. 35분에 새 runtime 관찰/수정을 끝내고 45분까지 검사·정리·보고한다. Git 게시 시간은 별도로 기록하며 시험 재개에 쓰지 않는다.

단위 외부120초·payload15초, 기존 게스트 마감/host transport reserve, 회수 최대30초·최종 정리 reserve90초를 유지한다. 새 단위에 필요한 시간과 정리 여유가 없으면 시작하지 않는다. UTC와 monotonic 중 이른 마감을 쓰되 host/guest monotonic을 직접 비교하지 않는다.

cache/버전/입력 불일치, 원래 정책 결과 불일치, 정책 한 행 외 차이, 추가 권한 필요, 예상 밖 접근, 소유권/종료/삭제/봉인 불명, 검사 실패 또는 상한 도달이면 새 실행을 중단한다. 같은 후보의 추가 조정을 반복하지 않는다. 안전 정리가 상한을 넘으면 그 사실과 잔여를 정확히 남기고 새 분석으로 전환하지 않는다.

## 검증과 완료 조건

관찰 상태는 `first-clone-passed-next-blocked`, `clone-still-denied`, `synthetic-payload-completed`, `inconclusive` 중 원문 근거에 맞게 정한다. 후보 시작0회는 정책 효과 미관찰이다. **완료 조건은 성공 payload가 아니라 제한된 대조 또는 근거 있는 중단, 진단 보존과 소유 자원 정리**다. 다음 차단을 해결하려고 허용 범위를 넓히지 않는다.

`pnpm check`·공통/새 진입점 Python 회귀·과거3개 verifier와 새 저장 verifier를 통과시킨다. 새 verifier는 baseline/candidate 분모·정책 한 행·trace 해석·실제 봉인/회수·감사 scope/index를 연결하고 누락/미실행을 성공으로 세지 않는다. TS/평가 불변이면 pnpm experiment와 Linux Vendure 전체 평가를 반복하지 않는다.

보고서는 실제 날짜의 `docs/reviews/YYYY-MM-DD-s2-policy-pair.md`, 원시 증거는 새 verification 디렉터리에 저장한다. 시작/최종 head, 계획/전달/실행 코드 hash, 허용 변경·불변 입력, 정책/Spec/trace, 결과와 미관찰, 정리/회수 상태, 단계별 비용과 다음 판단을 기록한다. PROGRESS/README/리뷰 맥락을 갱신하고 PR로 인계하되 **독립 결과 리뷰 전 병합하지 않는다.**

R11 unresolved·R12 기존 범위·production/live 거부·fixtureOnly=true·validSubmission=false·trialAuthorized/readyForTrial=false·results=null을 유지한다. 이번 정책 효과가 확인돼도 실제 CLI 전체 경계 검증·인증·모델 호출·본 비교는 별도 결과 리뷰 뒤 결정한다.
