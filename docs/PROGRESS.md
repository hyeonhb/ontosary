# 현재 작업 상태 — 새 세션은 이 문서부터 읽기

2026-11-12 단일 정책 시험은 **inconclusive / bounded-stop-completed**다. [인계](reviews/2026-11-12-s2-single-policy-test.md)(ADR-044). VM 이미지 다운로드가 이전 helper에서 가져온450초 명령 상한에 걸려 부팅 전 중단됐다. 승인된 환경20분을 모두 사용한 실패는 아니다. VM 등록1회, 부팅/container/실제 OCI 대조/후보 적용/CLI/model 각각0회이며 소유 등록·전용 경로·불완전 cache를 정리했다. 과거 감사11+close1 및 이번 고정 분석6개/이후 closing 분리를 구현했다. pnpm check304·새 회귀13개·기존 trial/verification1,682파일 불변을 확인했다. 다음은 중단 결과와 새 준비 예산 리뷰다. R11 unresolved·readyForTrial/trialAuthorized=false·results=null을 유지한다. 아래는 당시 기록이다.

2026-11-12 namespace 독립 리뷰 및 단일 정책 시험 승인: main `1aefc85`의 원시 trace·실제 정책·실행 입력 연결을 대조해 proposal-ready에 동의했다. 증거66파일/16archive/내부665파일·기존2521파일 불변, pnpm check304·감사5테스트를 확인했고 새 VM 재실행은 하지 않았다. 저장 audit11개와 종료 snapshot 포함 최종12개의 개수 차이는 새 감사 범위 명시로 보완한다. 사용자는 **clone arg0=2013397009 추가 allow 한 행만 적용하는 새45분 시험**을 승인했다(ADR-043). [현재 지시](reviews/2026-11-12-s2-single-policy-test-instructions.md)는 동일 이미지/추적 옵션의 원래 정책1회와 후보1회, 시작 전 실제 OCI 한 행 차이 확인, 다음 차단에서 중단·종료/정리를 정한다. 추가 권한 확대·credential/provider/model·본 비교는 결과 리뷰 뒤 결정한다. R11 unresolved·trialAuthorized/readyForTrial=false·results=null을 유지한다. 이번 세션은 문서 작성이고 정책 적용/시험은 미실행이다. 작성 후 pnpm check304테스트·타입 검사·예제 build와 문서 로컬 링크256개를 확인했다. 아래는 당시 기록이다.

2026-11-11 namespace 진단: **proposal-ready, 독립 리뷰 대기**. [결과](reviews/2026-11-11-s2-namespace-diagnosis.md), [비활성 후보](reviews/2026-11-11-s2-namespace-policy-proposal.md). 동일 보안 정책의 기준1/추적1에서 bwrap namespace clone flags `0x78020011`·EPERM을 관찰하고 실제 seccomp mask와 대조했다. 정책 적용 없이 첫 차단점 후보를 문서로만 제시했으며 AppArmor 독립 기여/후속 mount 경계와 후보 충분성은 미확인이다. 소유 자원 정리, pnpm check304·새 증거5테스트, 기존 입력2521파일 불변을 확인했다. 비모델 CLI4회·새 정책/credential/provider/model/trial0, R11 unresolved·trialAuthorized/readyForTrial=false·results=null이다. 직전 전체 config 미열람 표현은 전체 TOML 파싱/허용값만 기록으로 새 보고서에서 정정했다. 다음은 결과 리뷰이며 아래는 당시 기록이다.

2026-11-11 CLI 차단 독립 리뷰 및 다음 진단 승인: main `bbb43c9`의 보고/구현/원시 기록을 대조해 **blocked 판정에 동의**했다. 증거68파일·20archive 무결성, pnpm check304테스트·S2 build·collector13/cleanup3 회귀를 확인했으며 새 VM 재실행은 하지 않았다. 올바른 CLI 명령과 unshare의 실패/실제 OCI 제한은 일치하지만 bwrap 첫 실패 syscall과 AppArmor의 독립 기여는 미확인이다. 전체 사용자 config 미열람이라는 보고 표현은 전체 TOML 파싱/허용 값만 기록으로 정정해야 한다. 사용자는 **동일 후보·기존 정책 유지·새60분의 원인 진단 및 비활성 최소 변경안 작성**을 승인했다(ADR-041). [개발 지시](reviews/2026-11-11-s2-namespace-diagnosis-instructions.md)는10/25/40/50/60분 점검과 정책 적용 금지를 명시한다. 실제 정책 변경·credential 전달·provider/model·본 비교는 결과 리뷰 뒤 별도 결정한다. R11 unresolved·trialAuthorized/readyForTrial=false·results=null을 유지한다. 이번 세션은 지시/맥락 문서 작성이며 진단은 미실행이다. 작성 후 pnpm check304테스트·타입 검사·예제 build와 문서 로컬 링크242개를 확인했다. 아래는 당시 기록이다.

2026-11-11 CLI 비모델 타당성 결과: **blocked, 독립 리뷰 대기**. [인계](reviews/2026-11-11-s2-cli-feasibility.md). 고정 CLI는 기동했지만 비특권 container의 native sandbox namespace 생성이 거부됐다. parent 허용 작업은 성공했고 올바른 profile의 payload는 시작하지 못했다. 준비2컨테이너·비모델 CLI10회(성공6/실패4), 정상 경계2회/timeout/네트워크 검증·lifecycle 등록은0회다. 권한 확대 없이 환경 단계에서 탐색을 중단했고 소유 자원을 정리했다. pnpm check304테스트·S2 build·collector13/cleanup3·과거 실제 fixture의 production/live 거부 회귀를 통과했다. R11 unresolved·trialAuthorized/readyForTrial=false·results=null, 실제 credential 전달/로그인/갱신/provider/model/본 비교 각각0회를 유지한다. 다음은 실패 증거 리뷰와 재개 조건 선택이며 아래는 당시 기록이다.

2026-11-11 CLI 비모델 타당성 검증 승인: 사용자는 **기존 container 안의 CLI 본체/명령 sandbox 분리, 가짜 인증·내부 서버 검증과 새90분 상한**을 승인했다(ADR-039). [개발 지시](reviews/2026-11-11-s2-cli-feasibility-instructions.md)는 실행별 상태/설정·셸 HOME 분리, 가짜 인증의 직접/환경/FD 접근 거부, parent 양성 서버 대조와 sandbox 네트워크 차단, 새 정상2단위·timeout/정리를 요구한다. 환경20분/핵심45분/탐색70분/총90분이며 실제 자격 증명 전달·로그인/갱신/provider·모델 호출·본 비교는 결과 리뷰 뒤 별도 결정한다. 이번 세션은 지시·맥락 문서만 작성했고 CLI/VM 검증을 실행하지 않았다. pnpm check(304테스트·타입 검사·예제 빌드), pnpm s2:build, 문서 로컬 링크233개를 확인했다. R11 unresolved·R12 기존 범위·production/live 거부·trialAuthorized/readyForTrial=false·results=null을 유지한다.

2026-11-11 Linux 평가 독립 검토: main `bcab22e`의 보고·구현·원시 증거를 대조해 **linux-evaluation-reproduced**에 동의했다. 증거210파일/16archive 내부993파일 hash, 실제7단위 재대조 차이0, common9경로와 역사적 Program hash 대응, 입력109,157항목 불변성과 실행본·전체 종료 이후 수집·17등록 단위 정리를 확인했다. pnpm check304테스트·타입/예제 build, S2 build, Python26회귀와 production/live 승격 거부도 통과했다. 새 VM 설치/평가 재실행은 하지 않았으며 검토 범위의 추가 차단 결함은 없었다. 기존 외부 파일의 `<typescript>/<basename>` 축약은 후속 기술 부채로 남긴다. 아래는 리뷰 전 인계 기록이다.

2026-11-11 S2 Linux 평가: **linux-evaluation-reproduced, 독립 리뷰 대기**. [인계](reviews/2026-11-11-s2-linux-evaluation.md). 고정 Linux 설치/common build와 기존 `openEnvironment()`를 통과했고 새 경계의 필수7단위·공개 타입4회·timeout/유한 writer 대조·공유 lifecycle 실제5회귀를 확인했다. macOS common 선언9개의 경로 표기 차이를 원문/동일 hash로 분류하고 정확한 대응표를 새 검증 전에 고정했다. 최초/중간3단위와 최종7단위의 분모를 분리했다. 전체17개 등록 단위·VM·새 cache를 정리했고 pnpm check304테스트, Python26회귀를 통과했다. R11 unresolved·R12 기존 범위·production/live 거부·trialAuthorized/readyForTrial=false·results=null·실제 CLI/model/provider/본 비교0회를 유지한다. 다음은 결과 리뷰이며 아래는 각 시점의 기록이다.

2026-11-11 Linux 평가 재현 검증 승인: lifecycle fixture의 독립 검토 후 사용자는 **같은 경계의 Linux Vendure baseline/reference 재현과 새3시간 상한**을 승인했다(ADR-037). [개발 지시](reviews/2026-11-11-s2-linux-evaluation-instructions.md)는 Linux 불변 환경1회 준비·읽기 전용 완전 소스·실행별 새 평가 container·출력만 수집하는 구조다. baseline/reference 각2회·부정2종·reference delta1회, 공개 타입 검사·timeout 통합·macOS/반복/입력 방식 대조를 확인한다. 환경45분/핵심90분/탐색150분/총180분이며 기존 Program hash 검사·평가 의미를 유지한다. 이번 세션은 지시·맥락 문서 작성이고 Linux 설치/평가는 미실행이다. pnpm check(304테스트·타입 검사·예제 빌드), pnpm s2:build, 문서 로컬 링크224개를 확인했다. 실제 CLI·인증/provider·본 비교는 결과 리뷰 뒤 별도 진행하며 R11 unresolved·R12 기존 범위·trialAuthorized/readyForTrial=false·results=null을 유지한다.

2026-11-11 lifecycle 독립 검토: main `d840669`의 코드·최종25개 원시 기록·종료/수집/결과 철회·두 VM83개 등록 단위 정리 증거를 대조했고 검토 범위에서 새 차단 결함 없이 fixture-boundary-passed에 동의했다. 구현20/증거774/archive 내부3,202파일 hash, pnpm check304테스트·타입/예제 build 및 Python16회귀를 확인했다. VM을 재생성한 독립 실행은 아니며 RuntimeMaxSec 도달/불명확 create 중 감독자 사망의 실제 주입은 미검증이다. 이 검토가 R11 전체 해결이나 Linux/실제 agent 검증을 대신하지 않는다. 아래 인계는 독립 리뷰 전 기록으로 보존한다.

2026-11-11 S2 lifecycle fixture: **fixture-boundary-passed, 독립 리뷰 대기**. [인계](reviews/2026-11-11-s2-lifecycle-fixture.md). 독립 systemd 감독자·실행별 persistent slice·전체 종료 후 manager 수집을 구현했다. 수정본의 필수24개와 공개 직후 감독자 사망1개가 통과했고, 정상/timeout/래퍼 사망은 각각2회다. 늦은 쓰기를 허용했던 최초 supervisor 실패와 공개 직후 실패 경로를 보완하고 두 VM의83개 등록 단위/소유 자원을 정리했다. pnpm check304테스트와 Python16회귀, 실제 fixture의 production/live 승격 거부를 확인했다. R11 unresolved·R12 기존 범위·trialAuthorized/readyForTrial=false·results=null·실제 모델/provider/본 비교0회를 유지한다. 후속 Vendure/실제 CLI/평가 준비는 결과 리뷰 뒤 별도 결정한다. 아래는 각 시점의 기록이다.

2026-11-10 R11 fixture 경계 검증 승인: smoke 결과의 독립 대조 후 사용자는 **독립 게스트 감독자·실행별 cgroup·전체 종료 확인 뒤 관리자 수집**과 새3시간 상한을 승인했다(ADR-035). [개발 지시](reviews/2026-11-10-s2-lifecycle-fixture-instructions.md)는 환경20분/핵심 경로90분/탐색150분/마감180분, 정상·timeout·래퍼/감독자 사망·수집 실패/다음 실행 격리 검증을 정한다. fixture 전용 결과만 만들고 기존 production/live 경로는 계속 거부한다. 이번 세션은 지시·맥락 문서 작성이며 경계 구현/실험은 미실행이다. pnpm check(303테스트·타입 검사·예제 빌드)와 문서 로컬 링크215개를 확인했다. 성공해도 Vendure·실제 CLI/provider·평가·본 비교는 결과 리뷰 뒤 별도로 정한다. R11 unresolved·R12 기존 판정·trialAuthorized/readyForTrial=false·results=null을 유지한다.

2026-11-10 동일 후보 최소 실행: **smoke-passed, 결과 리뷰 대기**. [인계](reviews/2026-11-10-s2-container-smoke.md). 현재 native image target→config→rootfs chain→실제 container를 연결했고, 비특권 셸/Node22.19.0 반복·exit7 전달·Codex0.167.0-alpha.3.2 version/help를 새4컨테이너에서 확인했다. chain ID 검증식의 국소 수정1회와 실패본을 보존했다. 환경 청구477.002초/이전 합산1,728.267초, 유료0이며 VM/image/새 cache를 모두 정리했다. 호스트303테스트(skip0) 통과. R11 unresolved·R12 기존 범위·trialAuthorized/readyForTrial=false·results=null·실제 모델/provider/본 비교0회를 유지한다. Vendure 준비나 종료/수집/평가 adapter는 시작하지 않았고 다음 범위·예산은 리뷰 뒤 결정한다.

2026-11-10 동일 후보 최소 실행 재검증 승인: 사용자는 Lima/VZ + containerd/nerdctl을 유지해 **이미지 식별자 수정과 모델 없는 최소 실행을30분 한도**로 확인하기로 했다(ADR-033). [개발 지시](reviews/2026-11-10-s2-container-smoke-instructions.md)는20분 탐색/10분 검증·정리·인계, 원인을 확인한 국소 재시도, image target과 실제 container 연결, 비특권 셸·Node·CLI version/help를 요구한다. 이번 회차의 누적 비용을 이전 실패와 분리 기록하며 기존90분/4시간을 재개하지 않는다. 성공해도 Vendure 준비·R11 adapter/평가·실제 모델/본 비교로 진행하지 않고 결과 리뷰를 기다린다. 이번 세션은 지시·맥락 문서 작성이며 실제 재검증은 미실행이다. pnpm check(303테스트·타입 검사·예제 빌드)와 문서 로컬 링크200개를 확인했다. R11 미해결·R12 기존 판정·trialAuthorized/readyForTrial=false·results=null을 유지한다.

2026-11-10 컨테이너 타당성 조사: **inconclusive, R11 차단 유지**. [인계](reviews/2026-11-10-s2-container-feasibility.md). Lima/VZ VM과 Linux 준비 이미지 build는 성공했지만 로컬 image 식별자 호출 오류와 수정1회 실패로 중단했다. CLI/종료·접근·수집/평가 probe와 Linux Vendure 설치·평가는 미실행이다. VM/image/cache는 정리했고 후보1개·신규 비용0, 환경 준비 보수적20분51초/90분을 기록했다. 호스트303테스트(skip0)·비교4/4·18 usage fixture·84배포/4735원본 hash와 production 거부를 확인했다. R12 기존 판정과 모델/평가 계약은 유지한다. 다음은 같은 후보의 이미지 연결 수정에 새 한정 예산을 줄지 결과 리뷰에서 결정하는 단계다. 실제 모델/본 비교0회·trialAuthorized/readyForTrial=false·results=null이다.

2026-11-10 컨테이너 경계 타당성 검증 승인: 사용자는 **일회성 컨테이너 우선·기존 CLI/셸 유지**로 진행하기로 했다(ADR-031). [개발 지시](reviews/2026-11-10-s2-container-feasibility-instructions.md)에 총4시간·환경 준비90분·마지막30분 마무리·후보1개·신규 유료 비용0과 중단/부분 인계 기준을 정했다. 모델 없는 실행/평가 단위 종료·권한·전체 수집·Linux 환경/기존 평가 재현을 확인한다. 이번 세션은 지시·맥락 문서 작성이며 컨테이너 설치/실험을 수행하지 않았다. pnpm check(303테스트·타입 검사·예제 빌드)와 문서 로컬 링크196개를 확인했다. R11은 미해결이고 R12 해결 판정을 유지한다. 본 비교는 결과 리뷰 이후이며 실제 모델/본 비교0회·trialAuthorized/readyForTrial=false다.

2026-11-10 R11/R12 독립 재검토: **R12 검증 범위에서 해결, R11 미해결·실제 비교 차단 유지**. [독립 보고](reviews/2026-11-10-s2-runtime-accounting-independent-review.md).303테스트(skip0)·비교4/4·29제출60파일·참조52사례/trace를 재현했다. usage 순차 조합3,279개·추가20사례·기록18fixture가 일치했고 macOS22실행의 늦은 쓰기8건과 production 차단을 재확인했다. agent84파일·세 ID와 execution manifest 재생성도 일치했다. 추가 차단 결함은 발견하지 않았으며 지시의 ‘R12 완료 + R11 차단 인계’는 충족했다. 다음은 사용자와 R11 실행 경계/허용 도구 정책을 결정한다. 새 플랫폼·API를 채택하지 않았고 실제 모델/본 비교0회·trialAuthorized/readyForTrial=false·사람 검토 pending을 유지한다. 아래는 당시 자체 검증 기록이다.

2026-11-10 R11/R12 보완: **R12 구현·자체 검증 완료, R11 종료 경계 unresolved**. [인계](reviews/2026-11-10-s2-runtime-accounting-fix.md). turn 상태·중복 철회·unknown 입력/overflow·종료/EOF/절단을 결합했고303테스트(skip0)·비교4/4·29제출60파일 일치를 확인했다. 현재 runtime은 정상 부모 종료에도 모든 writer의 정지를 증명하지 못하므로 production 수집/평가와 전체 usage 확정을 차단한다. 진단과 알려진 참조 교정을 분리했으며 실제 macOS 반복에서 detached/손자/열린 핸들의 늦은 쓰기를 재현했다. TASK/B/C84파일·모델·세 ID는 그대로다. 다음은 독립 리뷰와 R11의 별도 경계/도구 정책 선택이다. 새 플랫폼·API·권한을 도입하지 않았고 실제 모델/본 비교0회, trialAuthorized/readyForTrial=false·results=null·사람 검토 pending을 유지한다. 아래는 각 시점 기록이다.

2026-11-10 R11/R12 보완 지시: 사용자가 기존 CLI·macOS 범위의 보완을 승인했다. [개발 지시](reviews/2026-11-10-s2-runtime-accounting-fix-instructions.md)는 종료 확인→전체 제출 수집 경계, turn 상태 기반 usage·불완전 계측, 실제 모델 없는 회귀와 새 실행 증거 동결을 다룬다. API/새 플랫폼·token hard cap 확대 없이 진행하며, native 경계가 성립하지 않으면 R12 완료와 R11 차단을 구분해 인계한다. 이번 변경은 지시·맥락 문서 작성이며 R11/R12를 수정한 것이 아니다. pnpm check(252테스트·타입 검사·예제 빌드)와 문서 내 로컬 링크 경로153개를 확인했다. 본 비교는 보완 결과 리뷰 뒤 진행하고 trialAuthorized/readyForTrial=false를 유지한다.

2026-11-10 S2 실행 전 준비 독립 리뷰: **자료/평가 방향 유지, R11 종료 차단 재현·R12 usage 완료 판정 보완 필요**. [독립 보고](reviews/2026-11-10-s2-trial-preparation-independent-review.md).252테스트(skip0)·비교4/4·29제출60파일/준비157파일 재현, 실제 A/B/C84파일·공개/private 타입7제출·참조 snapshot52사례를 확인했다. B68view와 C의12해석/22주장/30인용/방향 관계를 대조했고 사람 승인은 pending이다. detached 자손의 deadline 뒤 쓰기가 재현됐으며, 모순된 완료 이벤트가 후속 미완료 turn을 가려 usage를 complete=true로 만드는 새 반례를 확인했다. token hard cap 제외·API 확대 없음은 유지한다. 다음은 두 경계 보완과 C 사람 검토/실제 CLI 미검증 조건 확인이다. 실제 모델/본 비교0회, trialAuthorized/readyForTrial=false다. 아래는 당시 기록이다.

2026-11-10 S2 실행 전 준비: **자료·평가·계측 준비 구현, 전체 실행 환경은 차단 상태**. [인계](reviews/2026-11-10-s2-trial-preparation.md). 사용자 후속 결정에 따라 token hard cap을 필수 조건에서 제외하고30분 제한·raw usage/누락/참고선 초과 기록을 채택했다. 동일 TASK/공개 안내, 일반 문서 C와68view·1511단위 대응/사람 검토 묶음, 공개 타입 검사, 실행/수집 대역을 구현했다.252테스트(skip0)·비교4/4,29제출60파일·새 준비157비시간 파일 재현, A/B/C 실제 배포를 확인했다. 모델12항목/16링크·승인0과 B68view는 유지했고 agent 자료는84파일·새 bundleId다. macOS 파일/네트워크 거부와 package.json 예외의 명시적 차단을 검증했지만 **분리된 자식 프로세스의 종료 탈출**이 남아 실제 실행과 불변 제출 보장을 차단한다. 실제 모델 호출0·본 비교0, trialAuthorized/readyForTrial=false·results=null·사람 동등성/의미 검토 pending이다. 다음은 종료 경계 보완과 독립/사람 리뷰이며 API·새 플랫폼 투자는 하지 않았다. 아래는 각 시점 기록이다.

2026-11-10 S2 실행 전 준비 승인: 사용자가 **무요청 종료 정책·일반 설명 문서 C·기존 제한 평가·동일 설정 각3회** 조합을 승인했다(ADR-028). 다음 개발 세션은 [비교 실행 전 준비 지시](reviews/2026-11-10-s2-trial-preparation-instructions.md)에 따라 과업/실행 계약, C 양방향 의미 대응·사람 검토 자료, 격리/계측 환경, 새 배포 동결을 준비한다. 이번 세션은 지시·현재 맥락 문서만 작성했고 문서 링크200개와 pnpm check(230테스트·타입 검사·예제 빌드)를 확인했다. 이는 후속 준비 구현의 검증이 아니다. 본 비교는 준비 결과의 독립 리뷰 후 별도 진행하며 실제 비교 agent 실행·사람 의미 승인·H-O/H-F·S3는 수행하지 않았다. trialAuthorized/readyForTrial=false를 유지한다. 아래는 각 시점 기록이다.

2026-11-10 S2 modal 독립 재검토: **R9 잔여 해결, R8/R10 해결 유지, S2 준비 구현 보완 완료**. [독립 보고](reviews/2026-11-10-s2-modal-independent-review.md). 230테스트(skip0)·비교4/4·24제출50파일/새 준비147비시간 파일 재현, 기존 독립 modal 두 반례의 진단0 후 payload 실패, complete-root/delta의 요청·trace 일치와 실제 RxJS 경계를 확인했다. agent142파일·세 ID·모델/근거는 유지됐다. 검토 범위 내 추가 결함은 확인하지 않았다. 다음은 사용자와 과업 정책·B/C 의미 동등성·제한된 평가 범위·실제 격리/agent 실행 조건을 확정하는 단계다. readyForTrial=false·본 비교/H-O/H-F/S3 미실행을 유지한다. 아래는 당시 기록이다.

2026-11-09 R9 modal 연결 보완: **구현·자체 검증 완료, 독립 재검토 대기**. [인계](reviews/2026-11-09-s2-modal-fix.md), [평가 v3](../experiments/domain-model/s2/evaluation/TASK-REVIEW.md). 제출 부모의 실제 constructor identity/locals로 dialog를 구독 시 실행하고 resolve→부모→요청을 연결했다. 주문 ID/active 반례는 진단0 후 payload 실패이며 기존 R8/R10·13결함도 유지한다. 전체230테스트(skip0)·비교4/4,24제출50파일/modal trace 재현, 완전한 제출 CLI와 delta의 판정/요청/trace 일치, 기존 agent142파일·세 ID/모델 보존을 확인했다. 다음은 잔여 R9의 독립 재검토다. readyForTrial=false·미정 정책/사람 검토/격리/agent 조건을 유지하고 본 비교·H-O/H-F·S3를 수행하지 않았다. 아래 기록은 각 시점의 상태다.

2026-11-09 R9 modal 보완 지시: 사용자가 잔여 데이터 전달 문제의 개발 지시 작성을 요청했다. 다음 개발 세션은 [modal 연결 보완 지시](reviews/2026-11-09-s2-modal-fix-instructions.md)를 따른다. 실제 component/locals로 dialog를 실행하고 resolve 결과를 부모 흐름에 연결하며, 주문 ID/active 변형을 타입 통과 후 payload assertion에서 거부한다. 기존 R8/R10·13동작 결함·모델/배포 경계를 유지한다. 이번 세션은 지시·맥락 문서만 작성했으며 구현·본 비교·미정 정책 동결은 하지 않았다. 문서 링크와 pnpm check(214테스트·타입 검사·예제 빌드)를 확인했으며 이는 잔여 결함 수정의 검증이 아니다. readyForTrial=false다.

2026-11-09 S2 보완 독립 재검토: **R8/R10 해결, R9 부분 해결**. [최신 독립 리뷰](reviews/2026-11-09-s2-contract-independent-review.md). 214테스트(skip0)·비교4/4·22제출46파일/준비147파일 재현,142 agent 파일·세 ID·실제 A/B/C workspace hash를 확인했다. 그러나 modal 대역이 실제 component/locals를 무시해 부모의 잘못된 주문 ID·active 전달도 타입 진단0·52/52·sourceBinding=true로 통과한다. 같은 제출 메서드에 실제 전달값을 연결하면 잘못된 주문 취소/부분 취소 lines 누락이 관찰된다. 다음은 이 R9 데이터 전달 경계 보완·재검토이며 큰 구조 변경은 필요하지 않다. 준비 전체 완료/본 비교는 보류, readyForTrial=false·미정 정책/격리/agent 조건을 유지한다. 아래 인계는 당시 자체 검증 기록이다.

2026-11-09 S2 R8/R9/R10 보완: **구현·검증 완료, 독립 재검토 대기**. [인계](reviews/2026-11-09-s2-contract-fix.md), [평가 v2 계약](../experiments/domain-model/s2/evaluation/TASK-REVIEW.md). 완전한 제출/명시적 delta를 구분하고 원래 타입 문맥·추가 helper와 실행 snapshot을 hash로 결합했다. 요청 payload를 독립 기대값과 대조하고 환불만/혼합 환불 reason을 보존한다. 전체214테스트(skip0)·비교4/4, 22제출 교정 반복, 준비147파일 재현을 확인했다. baseline 진단0·보존16/16, 새 참조/helper 진단0·52/52, 역사적 참조 진단5 거부, 동작 결함13종은 타입 통과 후 검출했다. 기존142 agent 파일·세 ID는 그대로이며 evaluator run-plan만 갱신했다. 독립 reviewer의 해결 판정을 대신하지 않으며 readyForTrial=false·본 비교 미실행·H-O/H-F 미검증을 유지한다. 아래 기록은 각 시점의 상태다.

2026-11-09 S2 보완 지시: 사용자가 R8/R9/R10 보완 작업 지시 작성을 요청했다. 다음 개발 세션은 [S2 평가 계약 보완 지시](reviews/2026-11-09-s2-contract-fix-instructions.md)를 따른다. 제출 타입/구문 검사와 동작 판정을 분리하고, 유효한 참조 수정·핵심 요청 인자 검증·환불만 경로 보존을 먼저 완료한다. 동작 결함 변형은 타입 검사 통과 후 해당 assertion에서 거부해야 한다. 이번 세션은 지시·맥락 문서만 작성했으며 구현/과업 최종 동결/본 비교는 하지 않았다. 문서 링크와 pnpm check(196테스트·타입 검사·예제 빌드)를 확인했다. 이는 보완 구현의 검증이 아니다. readyForTrial=false와 기존 합의 구조를 유지한다.

2026-11-09 S2 준비 독립 리뷰: **방향·세션/모델/조회/배포 구조 유지, 평가기 R8/R9와 참조 수정 R10 보완 필요**. [독립 보고](reviews/2026-11-09-s2-preparation-independent-review.md). 196테스트(skip0)·비교4/4·새 준비 두 번 및 커밋 결과의147비시간 파일/세 ID 일치, 12항목/16링크·A/B/C 배포 hash를 확인했다. 그러나 참조 수정은 oracle24/24에도 실제 TS 진단5개가 있고, 잘못된 주문 ID·환불 결제/금액 변형도24/24를 통과한다. 환불만+공백 reason 보존 사례에서는 참조 수정이 회귀한다. 준비 전체 완료는 보완 재검토까지 보류하며 readyForTrial=false다. H-O/H-F·사람 의미 승인·본 비교·S3는 미검증이다. 아래 개발 인계와 과거 리뷰는 당시 기록이다.

2026-11-08 S2 준비 구현: **구현·실제 배포 자료·제출 코드 oracle·재현 검증 완료, 독립 리뷰 대기**. [인계 보고](reviews/2026-11-08-s2-preparation.md), [모듈/명령](../experiments/domain-model/s2/README.md). 단일 Program 세션·동결 모델·순수 조회로 기존 12항목/16링크와 승인0을 보존하고 B/C 자료를 만들었다. 전체196테스트(skip0)·비교4/4·두 준비의 비시간147파일/세 ID 일치, baseline/참조 수정/6결함 변형 검증을 확인했다. **readyForTrial=false**이며 본 비교는 실행하지 않았다. 다음은 과업 실패 처리·B/C 의미 동등성·oracle 원문 충실성의 독립 검토와 agent 버전/예산·실제 격리 동결이다. H-O/H-F·사람 의미 승인·S3는 미검증이다. 아래 기록은 각 시점의 상태를 보존한다.

2026-11-08 S2 구조 합의·개발 지시: 사용자는 단일 준비 세션, 동결 모델/순수 조회, 사전 생성 view와 동일 파일 도구, 타입 검사되는 실험 내부 모듈 구조를 승인했다(ADR-024). **다음 개발 세션은 [S2 준비 구현 지시](reviews/2026-11-08-s2-development-instructions.md)를 따른다.** 선행 부채→세션→모델→조회→B/C 제공 자료→평가 하네스/실행 명세→독립 리뷰 인계 순서다. 이번 리뷰는 문서만 작성했고 구현/본 비교는 미실행이다. 미정 실행 조건은 준비 자료로 만들어 별도 동결하며 변경 후 모델 갱신은 S3로 유지한다.

2026-11-08 S2 범위 결정: 사용자는 **변경 전 모델의 agent 수정 지원 효과부터 검증**하기로 했다(ADR-023). [선행 부채·분석 세션/모델/조회 아키텍처 제안](reviews/2026-11-08-s2-architecture-proposal.md)을 작성했다. 단일 준비 세션·동결 모델·순수 조회/사전 생성 view·실험 내부 모듈은 아직 합의 전 권고다. 구조 합의 뒤 개발 지시를 작성하며, 이번에는 제품 구현·S2 실행을 하지 않았다. 코드 변경 후 모델 유지/갱신은 S3 범위로 둔다.

2026-11-08 구현 아키텍처 감사: **조사 완료 / 다음 아키텍처·개발 지시는 미확정**. [상세 평가와 논의 안건](reviews/2026-11-08-architecture-audit.md). 기존 Vendure cache의 3회 측정에서 V2 전체 중앙값 8.25초, 역할 추출 5.60ms/FCA 0.67ms였고 Program·입력 감사의 3중 실행을 확인했다. core scan JSON은 약 23MB다. snapshot 수명주기, 탐색 관계/근거 의존 분리, ID·freshness·agent 조회 계약을 우선 논의하도록 권고한다. 174테스트·타입 검사·예제 빌드, 새 V2 마지막 실행의 비시간 15파일 일치 확인. 제품 구현·과거 증거는 그대로이며 S1/R6/R7 완료를 유지한다.

2026-11-08 V2 독립 리뷰: **R6/R7 해결, S1 보완 완료 인정**. 174테스트·비교 4/4·새 V2 15파일/V1 12파일 일치, 12개 ID 탐색과 standalone 5상황·제공 hash 9개를 확인했다. [최신 독립 리뷰](reviews/2026-11-08-domain-model-contract-independent-review.md). 사용자 요청에 따라 다음 단계의 큰 아키텍처·구현 범위는 대화로 정한 뒤 착수한다. S2와 agent 효용 검증은 아직 미실행이다.

2026-11-08 R6/R7 보완: **V2 구현·회귀 검증 완료, 독립 재검토 대기**. incoming/outgoing 한 단계 탐색과 전체 분석 입력/anchor 분리 검사를 제공한다. 모델 의미·78×6 context·후보5/추가 의미0은 유지한다. [최신 사용 경로](../experiments/domain-model/v2/README.md). [검증 인계](reviews/2026-11-08-domain-model-contract-fix.md): 174테스트·기존 비교4/4·15비시간 파일 재현 통과. S2는 미실행이다. 아래 리뷰/관찰은 당시 상태로 보존한다.

마지막 갱신: **2026-11-08, Asia/Seoul**.

## 현재 단계

2026-11-08 S1 독립 리뷰: **방향 유지 / S1 조건부 완료, R6/R7 Medium 보완 필요**다. PR #15/main `4480438`에서 163테스트·기존 비교 4/4·비시간 12파일 재현·64부분집합 FCA 독립 대조가 통과했다. R6은 개념→동작 안내와 relatedItems 방향 불일치, R7은 standalone validator의 대상 선언/분석 입력 변경 미검출이다. 전체 runner의 입력 검사는 R7 변조를 거부하며 기존 고정 결과의 오류는 아니다. [최신 독립 리뷰](reviews/2026-11-08-domain-model-independent-review.md), [현재 보완 지시](reviews/2026-11-08-domain-model-review-next-plan.md)를 따른다. 이번 리뷰는 제품/실험 구현을 고치지 않았고 원시 결과를 보존했다. S2는 보완 재검토 뒤 계약·fixture/oracle를 동결한다.

2026-11-08 S1 구현: **Vendure 도메인 모델 12항목·근거 검증기·동일 context의 단순 그룹/FCA 대조를 완료**했다. 모두 검토 대기이며 승인 지식은 없다. 네 클래스 78메서드×6역할(468셀, unknown 0)에서 형식 개념 8/후보 5를 얻었지만 후보 전부 단순 그룹과 extent가 같다. 새 의미 항목/추가 교집합은 0이다. 정상 검증·변조 8개 거부·27개 새 회귀, 전체 163테스트·기존 비교 4/4, 비시간 12파일 재현이 통과했다. [최신 인계](reviews/2026-11-08-domain-model-prototype.md), [실험/모델](../experiments/domain-model/README.md). 다음 권고는 독립 리뷰 후 S2 reason 계약·fixture/oracle 동결이다. S2 비교·Vendure 변경·사람 승인·agent 효용은 미실행/미검증이다.

2026-11-08 목표 정렬: **최종 목표는 기존 프로젝트를 agent가 도메인을 이해하고 수정하기 좋은 프로젝트로 점진적으로 전환하도록 돕는 것**이다. 업무 개념·관련 코드 탐색은 첫 사용 경로이고, 온톨로지는 명시적 도메인 모델의 수단, FCA는 구축 부담을 줄일 후보 발견 수단이다. ADR-020과 PRODUCT/RESEARCH/ROADMAP에 반영했다. 당시 다음 한 작업은 [S1 도메인 모델 개발 지시](reviews/2026-11-08-domain-model-next-plan.md)다. 당시 리뷰 세션은 지시·맥락 문서만 준비했으며 모델/validator·agent 변경 실험은 아직 구현/실행하지 않았다.

2026-11-08 준비 후 독립 리뷰: **PR #13의 준비·실패 경계 관찰을 인정하고 새 수정 필요 결함은 확인하지 않았다.** main `b4449c3`에서 136테스트·비교 4/4, 같은 설치 cache의 9개 관찰 파일·5개 입력 감사 파일 일치, 18개 fingerprint·11개 anchor·Program 경계·예산 기록 정합성을 확인했다. 전체 context를 facts로 재구성했고 기존 진입 파일만으로도 129객체/314속성이다. 설치/빌드 독립 재현·모델/agent 효용은 미검증이다. [최신 독립 리뷰](reviews/2026-11-08-vendure-preparation-independent-review.md), [새 근거](reviews/evidence/2026-11-08-vendure-review-verification.json)를 참조한다. 아래 준비/과거 계획은 당시 기록이다.

2026-11-08 Vendure 준비 후속: **환경 준비 성공 / 탐색 비교 범위 미확보로 종료**했다. 고정 의존성 설치·common 빌드 후 기존 4진입 설정의 진단은 0개다. 전체 context 2,264객체/4,288속성이 기본 128/64를 넘어 그룹/FCA를 실행하지 않았다. 원래 Admin UI 설정은 test 이름 오류 495개가 남았다. 30분 마감 안에서 총 359.668초를 사용했고 동일 설치 cache의 9개 관찰 파일이 재현됐다(설치/빌드 독립 재현은 미검증). 136테스트·기존 비교 4/4가 통과했다. [최신 인계](reviews/2026-11-08-vendure-preparation.md)와 [재현/경계](../experiments/public-app/prepared-v1/README.md)가 현재 상태다. 다음 권고는 과업 범위 선택 계약 검토이며 이번에 구현하지 않았다. 사람 효용·Gate 2~4는 미검증이다.

2026-11-08 준비 전 독립 리뷰: **PR #11의 과업/실패 관찰 완료를 인정하며 이번 범위의 새 결함은 확인하지 않았다.** 136개 테스트·기존 비교 4/4, 새 archive/inventory·Program·outcome·검색 결과 대조, 동일 cache 반복의 비시간 13개/17개 byte 재현을 확인했다. 분석 표본과 사람 효용은 여전히 미확보다. 사용자는 다음 작업으로 **Vendure 준비를 총 30분 한도로 한 번 더 검증**하기로 선택했다(ADR-019). [독립 리뷰](reviews/2026-11-08-public-app-independent-review.md)와 [현재 개발 지시](reviews/2026-11-08-vendure-preparation-next-plan.md)가 당시 판단이다. 설치 성공과 FCA 범위 적합성을 분리하며, 네 진입 파일의 현재 함수 inventory도 129개로 객체 상한 128을 넘는다.

2026-11-08 공개 업무 앱 적합성 점검: **과업/원문 근거와 재현 자료를 준비했고, 이번 예산에서는 분석 표본 미선정**이다. Saleor는 원래 strictNullChecks 전제에서 거부됐고 별도 과업 설정에서도 컴파일 오류가 남았다. 추가 후보 Vendure Admin UI는 strict를 유지하지만 미설치 의존성·workspace 빌드 경계로 실패했다. [실제 결과 인계](reviews/2026-11-08-public-app-suitability.md)와 [실험 README](../experiments/public-app/README.md)가 당시 준비 상태다. 사람 효용·Gate 2~4는 미검증이며 코어·기존 corpus는 그대로다.

직전 독립 판정(2026-11-08): **R5의 보고된 잔여 오류 해결, R4 해결 유지, 이번 변경 범위의 추가 결함 없음**이다. 136개 테스트·기존 비교 4/4, 원래 독립 사례 9/9·인접 사례 27/27·새 경계 사례 8/8, V1/V2/V3 비시간 14/16/16개 재현을 확인했다. [독립 리뷰](reviews/2026-11-08-type-context-independent-review.md)를 참조한다. 사용자는 다음 표본을 **공개 TypeScript 업무 앱 후보부터 조사**하기로 선택했다. [후보 조사](reviews/2026-11-08-public-app-candidates.md)와 [현재 개발 지시](reviews/2026-11-08-public-app-next-plan.md)는 이번 적합성 점검의 입력이다. 당시 앱 선정/scan·사람 효용 검증은 미완료였다.

2026-11-08 최신 구현: **R5 타입 선언 문맥을 V3로 보완하고 회귀·재현 검증을 완료**했다. 원래 독립 probe 기대 일치는 7/9 → 9/9, 인접 사례는 18/27 → 27/27이다. 전체 136개 테스트·기존 비교 4/4, V1/V2/V3 비시간 14/16/16개 재현이 통과했다. 현재 기본 corpus 명령은 V3이며 입력은 변경 없는 V2 계약이다. [새 인계](reviews/2026-11-08-type-context-fix.md)와 [V3 README](../experiments/corpus/v3/README.md)가 최신 구현 상태다. 독립 재검토·사람 승인·제품 효용은 별개로 남아 있다.

수정 전 독립 판정(2026-11-08): **R4 해결, R5 부분 해결**이다. V2의 함수 선언 이름 오인은 차단됐지만 지역 타입 매개변수/인터페이스 필드 선언 이름을 실제 사용으로 인정하는 Medium 잔여 결함을 확인했다. 99개 테스트·기존 비교 4/4·V1 14개/V2 16개 비시간 파일 재현은 통과했다. [독립 리뷰](reviews/2026-11-08-corpus-contract-independent-review.md)와 [현재 개발 지시](reviews/2026-11-08-contract-review-next-plan.md)가 이번 수정의 근거다. 업무 개념 탐색 우선 방향은 유지한다.

2026-11-08 구현 후속: **평가기 V2로 R4/R5를 보완**했다. 제품 코어와 역사적 V1은 그대로이며, 당시 기본 corpus 명령은 V2였다. 전체 99개 테스트·예제 비교 4/4, V1 비시간 14개·V2 16개 재현 일치를 확인했다. [수정 인계](reviews/2026-11-08-corpus-contract-fix.md), [V2 계약/재현](../experiments/corpus/v2/README.md), [새 검토표](../experiments/corpus/results/2026-11-08-v2/review.md)는 V2 당시의 구현 인계다. 아직 독립 재검토나 사람 승인으로 표시하지 않는다.

직전 독립 판정: 원시 corpus 결과는 재현됐지만 평가기 R4/R5 보완이 필요했다. 사용자는 다음 제품 실험을 **업무 개념·관련 코드 탐색 우선**으로 선택했다. [corpus 독립 리뷰](reviews/2026-11-07-corpus-independent-review.md)와 [이행한 개발 지시](reviews/2026-11-07-corpus-review-next-plan.md)가 이번 수정의 기준이며, 아래 관찰 자료는 과거 실행으로 보존한다.

2026-11-07 새 NEXT_PLAN의 **실제 corpus 관찰 자료 구축을 완료**했다. 공개 TS corpus 2개를 revision·라이선스·20개 파일 hash로 고정하고, 첫 scan 전에 코드 사실 라벨 24개를 작성했다. 라벨 22개 일치/2개 클래스 모델링 미지원, 함수 전체 predicate 지원 0건, 사전 날짜 비교 0/2 지원을 관찰했다. p-queue 전체 FCA는 속성 상한 초과이며 작은 범위 결과와 함께 보존했다. 사람의 업무 의미 승인·검토 시간·검색/LSP 대비 효과는 아직 미검증이다. [관찰 보고서](reviews/2026-11-07-corpus-observation.md)와 [검토표](../experiments/corpus/results/2026-11-07/review.md)는 구현 세션의 관찰 인계다.

첫 PoC의 구성 요소 구현 후, 독립 리뷰가 발견한 **R1/R2 false proof 차단을 완료**했다. 2026-11-07 독립 재검토에서 R1/R2/R3 해결을 확인했고 Gate 1을 제한된 지원·검증 범위에서 통과로 재평가했다. 모든 TS 문법에 대한 건전성이나 제품 유용성을 입증한 상태는 아니다. R3(mixed TS/JS 파일 집계 계약)도 수정·회귀 검증했다. NEXT_PLAN의 직접 수정·검증 지시와 명시된 후속 결함 R3까지 완료했으며, 이후 실제 corpus 관찰은 아래와 같이 수행했고 사용자 과업 비교는 후속 연구 단계다.

[R1/R2 개발 인계](reviews/2026-11-06-normalization-fix.md)와 [NEXT_PLAN 이행 점검·R3 인계](reviews/2026-11-06-next-plan-completion.md)에 전후 판정·검증·남은 위험을 정리했다. 과거 [리뷰](reviews/2026-11-04-poc-review.md)와 [NEXT_PLAN](reviews/NEXT_PLAN.md)은 당시 지시와 관찰로 보존했다. 이 문서가 최신 구현 상태다.

## 저장소와 개발 규칙

- `origin`: `https://github.com/hyeonhb/ontosary.git`.
- 원격 초기 LICENSE 커밋 `5d33ab6` 기반으로 `chore/initial-poc`에 기존 작업을 `a054f4f`로 커밋했다.
- 기존 두 커밋은 [PR #1](https://github.com/hyeonhb/ontosary/pull/1)로 원격 main에 병합했다(`7671a1a`). main은 origin/main을 추적한다. R3는 그 main에서 만든 `fix/analyzed-file-manifest`에서 구현하고, [PR #2](https://github.com/hyeonhb/ontosary/pull/2)를 2026-11-07 squash 병합했다(`b894137`). 로컬 main도 해당 원격 커밋까지 fast-forward 동기화했다.
- 사용자는 이후 작업도 검증 후 branch push → PR 생성·검토 → merge → main 동기화까지 자동 수행하도록 지속 승인했다. 별도 지시가 없으면 반복 승인 없이 이 절차를 따른다.
- [CONTRIBUTING](../CONTRIBUTING.md)의 GitHub Flow와 Conventional Commits를 준수한다. 작업 브랜치·작은 커밋·PR 검토·검증 기록이 기준이다. GitHub 보호 규칙이나 CI를 설정했다고 가정하지 않는다.
- 사용자 선택으로 원격 Apache-2.0 LICENSE를 유지하고 패키지·README를 통일했다. ADR-009가 최초 MIT 선택을 대체한다.

## 실제 구현된 기능

- TypeScript 타입·필드·함수·참조·조건·소스 근거와 진단을 JSON으로 추출.
- 작은 Formal Context/NextClosure, 후보 필터, 일반화 관계, 결과 상한.
- 제한된 논리 IR, 유한 열거·동치·양방향 함의·반례·Unknown/Unsupported.
- JSON CLI `scan`, `concepts`, `compare`.
- Vehicle/Listing/ConsultationRequest의 React+Vite 예제.
- 맥락 문서, 회귀 테스트, 재사용 가능한 실험·리뷰 증거.

이번 수정: enum 멤버의 타입만 보고 receiver 실행을 생략하던 경로를 차단했다. 직접 enum 선언 식별자(괄호·named import alias 포함)만 허용하고 optional/call/assertion/non-null/nested receiver·enum 객체 별칭을 거부한다. explicit this는 전체 predicate와 개별 condition 모두 Unsupported다. parameters는 원래 소스 signature이며, 지원된 IR의 argN만 런타임 인자 위치다.

## 실행 명령

```sh
pnpm install --frozen-lockfile
pnpm build
pnpm ontosary scan examples/react-vite --json
pnpm ontosary concepts examples/react-vite --json
pnpm ontosary compare examples/react-vite canConsultFromCard canConsultFromDetail --assume-same-input --json
pnpm exec vitest run tests/normalization-soundness.test.ts
pnpm check
pnpm experiment
node docs/reviews/evidence/2026-11-04-independent-check.mjs
pnpm example:dev
```

동명 함수는 전체 ID로 지정한다. Unknown/Unsupported 종료 코드 2, 프로젝트/컴파일/인수 오류는 1이다. probe 스크립트는 관찰 결과를 출력하므로 exit 0만으로 Gate 통과를 판단하지 않는다.

## 최신 검증 결과

환경: Node 22.19.0, pnpm 11.19.0, TypeScript 5.9.3. 새 의존성을 추가하지 않았다.

2026-11-07 중단 복구: PR #2 생성 후 병합 전 상태에서 재개했다. 구현 변경 없이 검증한 head `bb2dfe2`를 확인했고 `pnpm check`를 다시 실행해 82개 테스트·타입 검사·production build가 모두 통과했다. 원격 검사 목록은 비어 있었으며 CI 통과를 주장하지 않는다. 기존 실험·독립 probe 증거는 같은 구현에 대한 이전 실행 결과로 유지했다.

- 수정 전 targeted regression: 진단 0개인 fixture에서 34개 중 29 실패/5 통과.
- 수정 후 targeted regression: 한도 검사 추가 후 **35개 통과**.
- `pnpm check`: 코어/예제 타입 검사, **5개 파일/82개 테스트 통과**, Vite production build 성공.
- `pnpm experiment`: 기존 4개 비교 기대값 통과. 타입 6, 함수 13, 지원 predicate 6/미지원 7; FCA 13×26, 형식 개념 20/후보 8/관계 8, 잘림 없음. 실험 수치·비교 결과는 동일하며 scan JSON의 파일 범위 설명만 갱신했다.
- 새 회귀 테스트: 20개 거부 receiver 사례, 함수/메서드/branch의 explicit this, 정상 9개 함수/81쌍 실제 진리표 및 반례 재실행, named import·문자열/숫자 enum, 4,096/8,192 경계, core/CLI 상태 일치.
- 기존 독립 probe: 정상 144회 실행·IR 대조, 256쌍, 반례 336개, FCA 4×3 관계 4,096개 대조 통과. R1 optional/call, R2 first/second 비교가 모두 Unsupported/평가 0으로 바뀜. CLI 재현은 종료 2.
- R3 targeted regression은 수정 전 6개 모두 실패, 수정 후 6개 모두 통과했다. TS/TSX/MTS/CTS·JS/JSX/MJS/CJS·선언 파일, imported JS 참조, JS-only, allowJs만 설정한 경우, 제외 JS의 오류 진단, CLI/API manifest 일치를 검사했다.
- 독립 probe를 R3 적용 후 다시 실행하여 files=[input.ts], 제외 근거 ignored.js, 기존 R1/R2 거부와 정상 계산 검증을 확인했다. 새 증거는 `2026-11-06-file-manifest-results.json`이다.
- 초기 PoC의 브라우저 smoke check는 2026-11-03 기록이다. 이번 수정은 UI를 변경하지 않았으며 브라우저 확인을 반복하지 않았다.

## 남은 문제와 제약

- **R3 해결:** files는 실제 방문하는 TS/TSX/MTS/CTS 구현 파일만 포함한다. 제외된 구현 파일은 각각 omissions의 근거 경로·위치·이유로 보고한다. 타입 해석·참조·진단은 유지한다. 이 파일 수를 프로젝트 전체 coverage 비율로 해석하면 안 된다.
- enum namespace 경로·값 별칭·explicit this를 보수적으로 거부한다. 지원 확대는 별도 실행 대조가 필요하다.
- 기존 단일 반환식·필수 유한 입력·한 단계 속성 제한, strictNullChecks, 런타임 타입 준수·안정적인 plain data·입력 독립성 전제는 유지된다.
- 소스 ID의 편집 안정성, 재귀 project references, 최상위 조건·클래스 필드·프레임워크 의미, 큰 프로젝트 비용은 미해결/미검증이다.
- 승인 워크플로·LLM·SMT·MCP·자동 수정은 미구현이다. FCA 후보가 업무 개념이거나 조건 차이가 버그라는 뜻은 아니다.
- Gate 1은 2026-11-07 독립 리뷰에서 제한된 지원·검증 범위로 통과 판정했다. 모든 TS 입력의 건전성이나 Gate 2~4의 제품 효과를 입증한 것은 아니다.

## 2026-11-07 독립 재검토

PR #1~#3가 반영된 main `c6e0fc7`을 별도 리뷰 세션에서 재검증했다. **R1/R2/R3 해결, 검토 범위 내 추가 결함 없음**으로 판정했다. `pnpm check` 82개·타입 검사·예제 빌드와 `pnpm experiment` 4개 비교가 통과했다. 기존 독립 probe와 새 receiver/this/import/file 경계 probe도 통과했다. Gate 1은 제한된 지원·검증 범위에서 통과로 재평가했으며 Gate 2~4의 제품 효과는 여전히 미검증이다. 원격 check-runs/status 목록은 비어 있어 CI 성공을 주장하지 않는다.

[독립 리뷰](reviews/2026-11-07-post-merge-review.md), [당시 다음 개발 지시](reviews/2026-11-07-next-plan.md), [리뷰 맥락](reviews/REVIEW_CONTEXT.md)을 참조한다. 초기 NEXT_PLAN과 과거 원시 증거는 이행된 지시·관찰로 보존했다. 아래 corpus 연구 방향을 유지하며 이번 리뷰에서 제품 소스·테스트·설정을 수정하지 않았다.

## 2026-11-07 실제 corpus 관찰 검증

- 기준 main `c1a542c`에서 `codex/corpus-observation`으로 작업했다. 제품 소스·기존 지원 경계·FCA/논리 상한·의존성은 그대로다.
- p-queue `7f272ab5`의 production 5파일 및 priority-queue 4파일, date-fns v4.1.0 `313b902b`의 요일 함수와 local imports 9파일을 분석했다. 원래 p-queue 설정의 shared config 부재 실패도 기록했다.
- 라벨 24개 중 22개 일치, 2개 명시적 클래스/필드 모델 미지원. 사람 검토 0개, 승인 지식 0개. 조건 원문 추출의 일치와 정규화 지원을 구분했다.
- predicate 지원: p-queue production 0/103, 구성요소 0/15, date-fns 0/5. 범위 간 중복을 합산하지 않는다. 사전 날짜 비교 2쌍 모두 Unsupported/평가 0회.
- FCA: production은 103×188로 입력 상한 초과; 구성요소 15×31의 후보 23개, weekday 5×13의 후보 3개, 둘 다 잘림 없음. 같은 facts의 단순 그룹도 저장했다. 후보 수는 품질 점수가 아니다.
- `pnpm check`: 6파일/89테스트·타입 검사·예제 production build 통과. `pnpm experiment`: 기존 4/4 비교 통과, 과거 결과 변경 없음.
- 두 새 scanner 실행의 비시간 파일 14개 byte 일치. 재현 환경·hash·wall time·원시 결과는 `experiments/corpus/results/2026-11-07*`에 있다. 다운로드 준비 4,773ms, 사람의 준비 노력·검토 시간 미측정.
- 새 입력/runner/해석 보고는 날짜별 기존 리뷰·NEXT_PLAN을 보존한 채 추가했다. 정적 관찰만 수행했으며 원본 corpus 코드를 실행하지 않았다.

## 2026-11-07 corpus 독립 리뷰

main `a58a88b`을 독립 검토해 `pnpm check` 89개·기존 실험 4/4 및 새 corpus 실행의 비시간 파일 14개 일치를 확인했다. 원시 관찰은 재현됐으나 평가기가 라벨의 주장보다 약한 조건으로 correct를 내는 R4와 선언 이름을 사용 참조로 오인하는 R5(Medium 2건)를 재현했다. 제품 코어의 새 false proof는 확인하지 않았다. 기존 22/24는 현 평가기 판정이며 자연어 주장 전체가 자동 검증됐다는 의미로 확대하지 않는다.

사용자는 다음 제품 실험으로 **업무 개념·관련 코드 탐색 우선**을 선택했다. [독립 리뷰](reviews/2026-11-07-corpus-independent-review.md), [현재 개발 지시](reviews/2026-11-07-corpus-review-next-plan.md), ADR-014를 참조한다. 원래 corpus 보고서·라벨·raw 결과는 당시 관찰로 보존했다.

## 2026-11-08 R4/R5 평가 계약 보완

- 기준 main `7adf2d1`, `codex/corpus-evaluator-contract`에서 작업했다. src/core·CLI·lockfile·원본 corpus/manifest·V1 평가기/라벨/runner·과거 결과는 그대로다.
- V2는 타입 kind와 명시적 type 기대값을 검사한다. 함수 generic/클래스 소속/상속처럼 자동 검증하지 않는 문구는 claim에서 분리해 unverified로 출력한다.
- reference/property는 source/use/target anchor 및 실제 AST 역할과 정확한 edge를 대조한다. 선언 이름은 거부하고 재귀/import 사용은 인정한다. useEvidence/targetEvidence를 별도로 기록한다.
- 최초 actual-scan 회귀 8개 중 6개 실패/2개 통과 → 보완·추가 후 10개 통과. 전체 `pnpm check`는 7파일/99테스트·타입 검사·빌드 통과, `pnpm experiment`는 4/4 통과했다.
- V1 재현의 비시간 14파일, V2 재현의 비시간 16파일이 각각 byte 일치했다. 두 버전의 core 분석 산출물 11개도 동일하다.
- 두 버전 모두 라벨 22 correct/2 unsupported지만 검사 내용과 일부 claim이 달라졌으므로 성능 전후 차이로 읽지 않는다. 24개 전후 대조와 변경 이유는 `results/2026-11-08-v2/label-changes.json`에 있다.
- 당시 `pnpm experiment:corpus <새 경로>`는 V2, `pnpm experiment:corpus:v1 <새 경로>`는 역사적 V1이다. V1 결함을 수정 완료 버전으로 오인하지 않는다.
- [후속 제품 실험 초안](experiments/concept-exploration-protocol.md)은 미실행이다. 대상·정답·참가자를 확정하지 않았고 사람 시간/업무 의미/도구 효용 결과를 만들지 않았다.

## 다음 작업

최신 순서: [CLI 비모델 타당성 지시](reviews/2026-11-11-s2-cli-feasibility-instructions.md)의90분 검증 → 결과 독립 리뷰 → 실제 자격 증명/모델 연결과 전체 수정 소스 수집·평가의 후속 구조 결정 → C 사람 검토·전체 준비 재검토와 본 비교 별도 승인. Linux 알려진 제출 재현은 독립 검토 범위에서 통과했고 R12도 기존 검증 범위에서 해결됐으며 R11 전체 해결은 아직 아니다. 아래 합의 순서는 이 후속 경계를 포함해 해석한다.

1. R6/R7 보완은 독립 검증 범위에서 완료됐다. 최신 소비 경로는 V2이며 V1/과거 실패 증거는 보존한다.
2. S2 범위·큰 구조는 ADR-023/024, 과업 정책·비교 조합은 ADR-028로 합의했다. [실행 전 준비 지시](reviews/2026-11-10-s2-trial-preparation-instructions.md)에 따라 계약·C 의미 대응 검토 자료·격리/계측·새 배포 동결을 구현한다.
3. 준비 결과의 독립 리뷰와 사람 동등성 검토·남은 실행 조건 확인을 마친 뒤 별도 승인으로 본 비교를 진행한다. H-O/H-F와 코드 사실/후보/사람 승인을 분리하며 큰 기술·방향 선택은 사용자와 결정한다.

핵심 코드: `src/core/{analyzer,logic,fca,model}.ts`, `src/cli/index.ts`. 최신 평가기: [V3 README](../experiments/corpus/v3/README.md), [수정 인계](reviews/2026-11-08-type-context-fix.md). 지원 경계는 [ARCHITECTURE](ARCHITECTURE.md), 결정은 [DECISIONS](DECISIONS.md), 실험 해석은 [RESEARCH](RESEARCH.md), 순서는 [ROADMAP](ROADMAP.md)를 따른다.

## 사람을 위한 안내 문서

2026-11-08 사람 대상 문서: [안내서](guide/README.md)에 핵심 아이디어와 아키텍처 설명을 추가하고, 개념 흐름·구현 코어·모델 근거 읽기·합의된 S2 설계의 Mermaid 원본/SVG를 함께 관리한다. 일회성 개발 지시와 분리한 지속 관리 문서다. 확인 기준은 main `f080e39`이며 병행 개발 중인 S2를 완료로 표시하지 않았다. 제품 구현은 변경하지 않았다.
