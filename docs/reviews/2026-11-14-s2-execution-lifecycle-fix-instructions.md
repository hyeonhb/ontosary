# S2 실행 수명주기 R13 R14 R15 보완 지시

2026-11-14. 별도 개발 세션에서 R13~R15를 수정하고 같은 기본 정책의 작은 fixture로 검증한다. 직전 작업과 같은 **총 3시간 상한**을 이번 보완 회차에도 적용한다. 준비물 재사용, 제한된 실행 환경, 수집 결과 포장이라는 기존 세 책임을 유지한다. 이번 문서는 개발 지시이며 보완 결과가 아니다.

Ontosary의 목적은 기존 프로젝트를 agent가 도메인을 이해하고 수정하기 좋은 프로젝트로 전환하도록 돕는 것이다. 이번 작업은 S2 비교를 위한 실행 준비의 결함 수정이다. 제품 코어·도메인 모델·FCA·평가 의미를 확장하지 않는다. 실제 자격 증명 전달·로그인/갱신·provider/모델 호출·본 비교는 결과 리뷰 뒤 결정한다.

## 기준과 수정 범위

먼저 AGENTS, PROGRESS, ARCHITECTURE, ROADMAP, CONTRIBUTING과 [독립 리뷰](2026-11-14-s2-execution-lifecycle-independent-review.md), [직전 지시](2026-11-14-s2-execution-lifecycle-instructions.md)를 읽는다. 구현 기준은 [PR #54](https://github.com/hyeonhb/ontosary/pull/54)의 `f6fc3862c124cf675270359b82e4efb1aedd333d`다. main에는 구현이 아직 없고 PR #53의 cache 복구 기록과 PR #55의 독립 리뷰가 반영돼 있다. 실제 시작 head·원격·작업 트리 변경을 확인하고 이 지시 및 최신 main 문서와 통합한다. 사용자 작업을 덮어쓰거나 공유 브랜치를 force-push하지 않는다.

PR #54의 기존 작업 브랜치를 이어 수정하는 것을 우선한다. 별도 브랜치가 필요하면 PR #54에 대한 의존성을 명시한다. 이번 보완은 PR #54를 결과 리뷰에 다시 제출하는 단계다. 커밋·push·PR 갱신까지 수행하고 **보완 구현 PR의 병합은 독립 결과 리뷰 뒤로 둔다.** 과거 보고/증거는 고치지 않고 새 날짜·경로로 추가한다. ADR-048은 PR #54의 부분 구현 기록이므로 이 지시의 ADR-049와 함께 보존한다.

허용 수정은 `experiments/domain-model/s2/trial/container/execution-lifecycle/`의 준비·환경·비교·export 및 회귀, 필요한 최소 공유 `lifecycle/collector`와 호출부, 저장 증거 검증기, 관련 README·리뷰·진행 문서다. 기존 snapshot/deadline/package·소유권·전체 종료 계약을 재사용한다. 제품 코드, TASK/B/C, 모델/배포 ID, Vendure 평가 계약, 과거 원시 증거는 불변이다. 새 backend·상시 VM·범용 cache 서버·새 의존성은 도입하지 않는다.

독립 리뷰에서 `pnpm check` 304개(skip 0)와 Python 116개가 통과했다. Vendure 임시 cache는 고정 입력만 복구했고 PR #53은 병합됐다. 시작 시 상태를 재확인하되 cache 재설치나 검사 생략을 이번 수정에 섞지 않는다. 다시 누락됐다면 경로와 실패를 분리 보고하고 임의로 환경 준비 범위를 넓히지 않는다.

회차 내내 R11 unresolved, R12 기존 검증 범위, production/live 거부, `fixtureOnly=true`, `validSubmission=false`, `trialAuthorized=false`, `readyForTrial=false`, `results=null`을 유지한다.

## 1 준비와 로컬 재현

최초 명령에서 UTC·host monotonic을 기록하고 읽기·계획·구현·대기·검증·정리·보고를 비용에 포함한다. 최초 inventory와 변경 허용 목록, 준비물 경로·목록, 실행 순서·수, snapshot 분석/closing 범위, 각 마감과 정리 소유권을 고정한다. 보관된 공개 준비물과 새 회차 VM/작업 상태를 구분한다.

[cache 진입점 재현](evidence/2026-11-14-probe-cached-prepare.py)과 [export 재현](evidence/2026-11-14-probe-export.py)을 참고해 실제 호출 흐름을 회귀 테스트로 만든다. 과거 재현 스크립트의 오류 문자열만 바꾸어 통과시키지 않는다. 수정 전 두 결함이 드러나는지 확인하고 수정 후 의도한 동작을 검증한다. 외부 명령은 가짜 실행기로 대체하고 공개 canary·임시 디렉터리만 사용한다.

## 2 R14 이미지 조회를 빌드 앞으로 옮긴다

현재 `Round.prepare()`는 guest build/export 뒤에 그 출력으로 cache 요청을 만든다. 다음처럼 **빌드 입력으로 조회하고 출력으로 검증**하는 두 단계를 분리한다.

1. 기반 이미지 digest, 실제 Dockerfile/빌드 context 내용, build args, 플랫폼, 관련 도구 버전 등 빌드 전에 알 수 있는 입력으로 결정적인 key를 만든다. key의 스키마/직렬화를 고정하고 결과 SHA·바이트·새 image ID를 입력 key로 요구하지 않는다. probe·fixture·실행 정책은 이미지에 실제 포함되는 경우에만 빌드 입력이다. 실행 입력 hash는 별도로 계속 검증한다.
2. 기존 Store의 원자 등록·잠금·해시 검증을 사용해 먼저 조회한다. hit면 저장 archive의 실제 바이트·크기·manifest/config/rootfs chain을 검증해 새 VM에 import한다. **hit 경로에서는 build/save/다운로드 producer를 호출하지 않는다.** 게스트 버전 확인·설치 준비와 이미지 빌드도 분리해 검증을 건너뛰지 않는다.
3. miss일 때만 같은 고정 레시피로 build/export하고, 검증된 출력 digest·크기·image identity를 입력 key에 연결해 등록한다. 동일 tag/name을 동일 내용의 근거로 쓰지 않는다. 새 key는 새 항목으로 다루고 동일 key의 상충 기록이나 손상은 조용히 덮어쓰지 않는다.
4. 이미 보관된 이미지의 옛 manifest에 새 key가 없다면 과거 빌드 입력 증거와 실제 archive를 검증한 **명시적 연결 기록**을 추가할 수 있다. 옛 manifest/증거를 수정하지 않는다. 필요한 입력을 입증할 수 없으면 miss로 보고하며, 예산 내 최대 1회 빌드까지만 허용한다. 이 경우 “기존 이미지 재사용 성공”으로 보고하지 않는다.

빌드 레시피의 외부 package 조회가 완전히 고정돼 있지 않다면 “동일 입력에서 항상 동일 출력”이라고 주장하지 않는다. 승인된 저장 출력의 재사용과 새로운 빌드의 결과 검증을 구분한다. 저장소 무결성 검사가 실패하면 실제 회차를 중단한다. 손상 테스트는 작은 복제 fixture로 수행한다.

필수 회귀는 **실제 준비 진입점**을 통해 수행한다. 첫 miss→등록 뒤 별도 회차/작업 디렉터리의 hit를 실행하고, 두 번째의 build/save/다운로드가 호출되면 실패하게 한다. 새 round ID/probe 변경만으로 불필요한 rebuild가 생기지 않는지, 실제 레시피/base/tool 변경은 hit를 무효화하는지, import identity 불일치·손상·부분 등록은 거부하는지 확인한다. Store 함수 단독 lookup이나 같은 acquire 직후 lookup만으로 완료 처리하지 않는다.

## 3 R13 고정 PATH와 엄격한 hook 환경 계약을 적용한다

`identity.py`의 runtime 환경과 `engine.py`의 실제 runtime 호출을 함께 수정한다. nerdctl 본체의 절대 경로 호출만으로 내부 `apparmor_parser`, `aa-exec`, `true`, `runc features` 탐지가 해결되지 않는다. 독립 리뷰의 코드 경로는 확인됐지만 PATH 복원만으로 실제 실행이 통과하는지는 이번에 검증해야 한다.

- runtime에 필요한 관리자 소유 시스템 경로만 담은 고정 PATH를 준다. 예시 `/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`은 실제 고정 이미지에서 경로·실행 파일 소유권을 확인해 채택한다. 빈 항목·상대 경로·현재 디렉터리·worker 쓰기 가능 경로·상속된 사용자 PATH는 허용하지 않는다. HOME/LANG 등 나머지 env도 명시 목록을 유지한다.
- `nerdctl v2.4.2`가 hook env에 추가 PATH를 붙이는 동작을 정확히 처리한다. process env의 일반 중복 키 거부는 유지한다. hook의 알려진 PATH 중복만 필요한 경우 고정 위치·개수·각 값·명령/version을 먼저 확인한 뒤 허용한다. dictionary 변환으로 중복을 숨기거나 임의 중복을 허용하지 않는다. 직접 전체 기대 배열을 대조하는 작은 구현도 가능하다.
- 고정된 과거 Spec을 위한 기대값 변환과 실제 Spec 검증을 구분한다. 원본은 보존하고 변경 경로·원값·기대값·근거를 기록한다. AppArmor·rro·seccomp·capability·NNP·mount·network·자원 제한 차이는 치환하거나 무시하지 않는다. 검증된 자기 실행 식별자만 대응시킨 후 전체 Spec을 비교한다.
- 새 환경은 모든 runtime 호출과 기본/후보용 공통 경로에 일관되게 사용한다. 감독자 환경의 임의 상속을 복구하지 않는다. 이번 실제 실행은 기본 정책만 사용한다.

로컬 회귀는 env 전달을 실제 호출 경계에서 포착하고, 고정 환경의 허용 사례와 누락 PATH/상속 오염/잘못된 중복 값·개수/추가 hook·다른 run 경로/보안 필드 변경을 검사한다. 과거 전체 Spec에 대한 대응과 부정 변형을 함께 확인한다. 가짜 도구 테스트는 전달 계약만 검증하며 실제 AppArmor/rro 입증으로 세지 않는다.

새 VM에서는 container 시작 전, **runtime과 정확히 같은 env**에서 필요한 도구의 실제 해석 경로·버전·소유권과 `runc features` 등 탐지 결과를 남긴다. 첫 정상 fixture의 created Spec에 기존 AppArmor와 세 mount의 rro가 유지되는지 전체 비교로 확인한 뒤 시작한다. 추가 smoke container는 만들지 않는다. 기존 PATH 없는 실패 증거와 새 관찰을 대조하고, 실제 확인 없이 원인 해결로 표시하지 않는다.

## 4 R15 검증된 산출물만 export한다

현재 `guest.export()`가 원본 run tree를 다시 순회하는 경로를 제거한다. 종료·삭제 확인은 수집 성공과 다르다. 결과 export와 관리자 진단을 다음처럼 구분한다.

- worker 결과는 기존 collector가 성공적으로 생성·봉인한 관리자 소유 수집 산출물과 manifest만 사용한다. 수집 상태·run identity·종료/삭제·manifest/hash를 검증한다. 성공 후 결과가 철회된 경우도 export에서 유효 결과로 되살리지 않는다.
- `collectionStatus=suppressed/failed`이거나 종료/삭제가 불명확하면 worker 원본 source/output/HOME/CLI 상태/scratch를 다시 읽지 않는다. 명시적으로 열거한 관리자 상태·정리/오류 진단만 포함하고 수집 거부 이유를 남긴다. arbitrary run root 파일을 관리자 진단으로 간주하지 않는다.
- 진단 파일도 동일한 no-follow/파일 종류/개수·깊이/읽기 전 크기/누적 바이트/시간 경계를 적용한다. 기존 collector의 안전한 읽기 기능을 최소 추출해 공유하거나 그 기능으로 제한된 staging을 만든다. path 검사 후 `read_bytes()`로 다시 여는 약한 별도 구현을 만들지 않는다. FD 기준 확인과 읽는 중 증가·교체 검사, hardlink/symlink/특수 파일 거부를 유지한다.
- 기존 worker collector 128파일·16MiB와 export 1,024파일·16MiB 상한을 유지한다. export에는 추가 메타데이터도 합산하고 읽기 전에 제한을 확인하며 작은 chunk로 처리한다. 원본 전체를 메모리로 읽거나 archive 생성 후에만 상한을 적용하지 않는다.
- 임시 archive/index를 만들고 검증 후 최종 공개한다. 실패 시 부분 최종 파일이나 과거 성공 archive를 이번 성공으로 오인하지 않도록 한다. 기존 snapshot 분류·원자 package 계약에 맞춰 최종 index와 실제 members를 정확히 대조한다. collector 실패를 전체 감사 자료 소실로 처리하지 말고, 허용된 관리자 진단만 별도로 보존한다.

필수 통합 회귀는 collector→실제 `guest.export()`→archive 검사까지 연결한다. 정상 파일의 정확한 포함, hardlink canary 거부 후 내용 미포함, symlink/부모 symlink/FIFO 거부, 과대 파일을 본문 읽기 전에 거부, 전체 용량/파일 수/시간 초과, 수집 실패·종료 불명·결과 철회 시 worker 원본 미접근, 변조된 수집 manifest 거부, 중간 실패의 부분 archive 미공개를 확인한다. 특수 파일 테스트는 블로킹 없이 끝나야 한다. 최종 메타데이터도 합산되는지 검사한다.

## 5 같은 기본 정책에서 필수 7단위를 검증한다

R13~R15의 로컬 통합 회귀와 기존 영향 회귀를 모두 통과한 코드 hash를 고정한 뒤 새 VM 1개로 진행한다. 기존 공개 준비물을 검증해 재사용하되 회차 VM과 source/output/HOME/CLI 상태/scratch는 새로 만든다. 보관량은 임시 파일 포함 10GiB 이내다.

| 단위 | 기대 결과와 증거 |
| --- | --- |
| 정상 종료 1 | 고정 env의 도구 탐지·AppArmor/rro/전체 Spec 보존, 허용 읽기/쓰기, 종료→삭제→수집→export |
| 생성 후 사전 검사 실패 | start 0회, 자동 삭제, 실패와 정리 상태 분리, 허용 진단만 export |
| 시작 실패 | pending 정착과 생성 자원 부재 확인, 불확실하면 결과/다음 실행 차단 |
| timeout | 분리된 자손까지 종료, 늦은 쓰기 없음, 정리·진단의 제한 준수 |
| 호스트 wrapper 사망 | 호스트 수동 정리 없이 게스트 감독자가 종료·삭제 |
| 작업 감독자 사망 | 독립 종료 후 처리, 결과 철회/다음 실행 차단, 명시적 안전 복구 |
| 정상 종료 2 | 복구 뒤 새 상태, 이전 실행 canary 접근 불가, 같은 준비물과 검증된 export 사용 |

시작 전 등록부터 종료·삭제·제한된 수집/단위 봉인까지 120초(준비·실행 80초, 삭제 110초, 봉인 120초), payload 최대 15초를 유지한다. 회차 archive export·snapshot/포장도 별도의 무제한 작업으로 두지 말고 같은 회차 마감에서 잔여를 전달한다. 준비 완료 신호에 맞춰 실패를 주입하고 create/start/exec 수·정리 시각·pending·마지막 쓰기·수집/포장 상태를 기록한다. 기대한 실패 주입과 예상 밖 운영 실패를 구분한다. 다음 실행은 기존 명시적 복구/소유권 검증을 거친 경우만 허용한다.

현재 AppArmor·network none·UID/GID1000·capability0·NNP1·RO root/cgroup·CPU2·메모리4GiB·PID256·tmp64MiB·mount 접근 제한을 유지한다. **이번 회차는 필수 7단위까지만 수행한다.** 직전 지시의 선택적 8번째 실제 실패 주입과 원래/후보 정책 대조는 재개하지 않는다. clone allow 행 추가를 포함한 정책 시험은 이번 결과 리뷰 뒤 결정한다. 로컬에 있는 기존 정책 비교 회귀는 계속 실행한다.

## 비용 상한과 중단 기준

총 180분, 신규 유료 비용 0, 새 VM 최대 1개, 실제 fixture 최대 7단위다. 생성/시작 실패도 시도 수에 포함하고 숨은 smoke나 실패 단위 재시도를 추가하지 않는다. 이미지 build는 별도로 최대 1회 기록하며 총 시간에 포함한다. 실제 보관 이미지 hit면 build 0회여야 한다.

| 최초 시작부터 | 마감과 동작 |
| --- | --- |
| 60분 | R13~R15 구현·필수 로컬 회귀·사전 계획 완료. 미달이면 VM 착수 없이 부분 인계 |
| 100분 | 준비물 검증·VM·도구 탐지·이미지 import 준비 완료. 미달이면 새 준비 중단 |
| 150분 | 실제 7단위 관찰 종료. 이후 새 실험/구현 탐색 중단 |
| 180분 | 검사·정리·증거 포장·보고 완료 |

환경 진입 때 한 번만 `min(진입+20분, 회차 시작+100분)`을 고정한다. 모든 다운로드·해제·부팅·import/build 명령은 같은 잔여를 쓰고 단계마다 시간을 초기화하지 않는다. 호스트 UTC/monotonic의 더 이른 잔여를 사용하고 host/guest monotonic 값을 직접 비교하지 않는다. 새 단위의 120초와 마무리 여유가 없으면 시작하지 않는다.

실제 실행 중 미분류 Spec 차이, 무결성/도구 버전 불일치, 예상 밖 접근, 추가 권한 필요, 소유권·pending·종료·삭제 불명, 시간/횟수 초과가 발생하면 새 실행을 중단한다. 실제 실패 후 기대값을 넓히거나 코드를 바꿔 같은 단위를 재시도하지 않는다. 로컬 수정은 마감 내 허용한다. 시작 전 단순 명령 오타의 수정은 생성 요청 전임을 확인해 총 1회만 허용하며 보안/identity/cache/수집 계약 변경은 오타가 아니다.

마감 이후에도 소유 자원의 안전 정리는 포기하지 않는다. 새 실험은 멈추고 불가피한 정리 초과와 잔여를 별도 기록한다. 이전 비용은 과거 보고에서 가져와 이번 실측·직렬화 보수 상한·누적을 구분한다. Git 게시 시간은 별도 기록하고 실험 재개에 쓰지 않는다.

## 완료 조건과 인계

R13은 실제 고정 env에서 도구 탐지와 기존 보안 Spec 보존이 확인돼야 한다. R14는 별도 회차의 실제 준비 진입점에서 build/download 0회인 hit 회귀와, 이번 VM의 cache provenance·import identity 검증을 갖춰야 한다. 기존 대형 이미지 연결이 불가능해 miss/build를 했다면 로컬 재사용 회귀와 실제 cache 재사용 미검증을 구분한다. R15는 거부된 worker 원본이 최종 export까지 포함되지 않는 통합 회귀와 실제 7단위의 허용 결과/진단 포장을 확인해야 한다. 실제 검증이 빠지거나 막히면 해당 항목은 부분 완료다.

필수 7단위는 각 기대 결과·정리·마감·다음 실행 계약을 만족해야 한다. 새 결함 없이 회차를 정리한 것과 구현 검증 완료를 구분한다. 성공해도 R11 전체 해결이나 실제 agent 실행 준비 완료로 승격하지 않는다.

`pnpm check`와 execution-lifecycle·공유 lifecycle·single-policy-test의 영향 회귀, collector/cleanup·production/live 거부, snapshot/deadline/package, 과거 및 새 저장 증거 verifier를 실행한다. 직전 304/116은 기준 수이며 새 테스트 수·중복·skip·실패를 정확히 보고한다. TypeScript 분석/평가 의미를 바꾸지 않았다면 `pnpm experiment`와 Linux Vendure 평가 전체 재실행은 생략 이유를 기록한다. 영향을 만들었다면 필요한 검증을 수행하거나 미검증으로 인계한다. 최초 inventory와 최종 코드를 대조해 허용 변경 및 불변 입력을 증명하고, 최종 코드 archive와 실제 실행/전달 코드 hash를 연결한다.

새 보고서는 `docs/reviews/2026-11-14-s2-execution-lifecycle-fix.md`, 증거는 `experiments/domain-model/s2/verification/2026-11-14-execution-lifecycle-fix/`에 저장한다. 날짜가 바뀌면 실제 날짜를 사용하고 기존 경로를 덮어쓰지 않는다. 보고서에는 다음을 포함한다.

- R13/R14/R15별 수정·검증·미해결 표와 실제 코드 위치.
- 고정 PATH·도구 해석·hook 기대 배열·원본/대응/전체 Spec diff, 기존 실패 대비 관찰.
- 빌드 입력 key와 출력 manifest, 기존 cache 연결 근거, 실제 다운로드/build/import 횟수와 비용.
- collector 상태별 export member 목록·관리자 진단 allowlist·상한·부정 회귀 결과.
- 계획 대비 실제 7단위 분모·기대 실패/예상 밖 실패·종료/삭제/수집/포장 시각·자원 잔여.
- 최초/실행/최종 코드·입력 hash, 명시적 분석/closing snapshot과 최종 index, 검사 및 미실행 항목, 시간·용량·비용.

PROGRESS와 관련 README를 실제 결과로 갱신한다. 결정 변경이 필요하면 실행으로 밀어붙이지 말고 근거와 선택지를 인계한다. 보완 PR은 리뷰 가능한 상태로 게시하고 다음 정책 대조·자격 증명·모델 호출·본 비교는 진행하지 않는다.
