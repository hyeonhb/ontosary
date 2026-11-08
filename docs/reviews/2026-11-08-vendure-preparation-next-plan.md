# 개발 세션 지시 — Vendure 준비를 30분 한도로 검증

## 목표와 승인 범위

사용자는 독립 리뷰에서 **Vendure의 기존 의존성 설치·common 빌드를 총 30분 한도로 한 번 더 검증**하기로 선택했다(ADR-019). 목적은 “고정 앱의 원래 strict 전제를 유지하고 오류 없는 분석 입력을 준비할 수 있는가, 그 비용은 얼마인가”다. FCA 지원 확대나 사람 효용 실험은 이번 목표가 아니다.

AGENTS/CONTRIBUTING/PROGRESS와 [독립 리뷰](2026-11-08-public-app-independent-review.md), [기존 관찰](2026-11-08-public-app-suitability.md), [실험 README](../../experiments/public-app/README.md)를 읽는다. 검토 기준은 PR #11/main `685545fe85d67a0559e5908c6cd0fda4163a65e3`이며 이후 리뷰 문서 커밋이 추가된다. 제품 core/CLI, 기존 corpus, V1과 과거 원시 결과는 보존한다.

## 고정 대상과 예산

- Vendure v3.5.0 Angular Admin UI, revision `534e6003534f74761e82de1b8c6061cba89945d1`. 기존 manifest의 archive/hash/license와 `vendure-task.json`을 그대로 사용한다. 새 후보 탐색·Saleor 설치·최신 Vendure로 이동하지 않는다.
- 새로운 격리 cache에서 수행한다. 환경 preflight 시작부터 설치·필요 build·최초 재분석까지 **wall clock 30분**을 하나의 마감으로 적용하고, 명령마다 남은 시간 내 timeout을 둔다. 실패 재시도도 같은 예산에 포함하며 세션 재개로 예산을 리셋하지 않는다. 보고서 정리·Ontosary 회귀 검증·PR 반영 시간은 별도로 기록한다.
- source/lockfile/config/원래 generated 파일을 고정한다. upstream 엔진·package manager·workspace 구조와 lifecycle scripts를 확인하고, lockfile을 존중하는 설치와 필요한 common 빌드만 실행한다. 준비가 workspace 전체 의존성을 요구하면 그 사실·용량·시간을 기록한다. 서비스/DB/브라우저 앱 기동은 필요 없다.
- 원문 패치·임의 any/stub·강제 dependency override·lockfile 갱신·가짜 소스 alias·strict/진단 정책 완화·FCA 상한 증가는 제외한다. 그런 변경이 필요하면 현재 실패를 보존하고 중단한다.

## 수행 순서

1. 원격/브랜치/사용자 변경을 확인하고 새 준비 manifest를 먼저 작성한다. 설치 범위·실행 명령·버전·예산 시작/마감과 중단 조건을 고정한다. upstream TypeScript로 build하는 것과 Ontosary TS 5.9.3으로 분석하는 것을 구분한다.
2. archive/hash·전체 원문 inventory와 예비 과업 anchor를 검증한다. 설치 전후 원본 파일 불변성을 검사하고, 새로 생성된 common lib 및 dependency 결과는 출처/버전/hash/라이선스 경계와 따로 기록한다. 설치 로그에 자격 증명을 넣지 않는다.
3. 기존 lockfile에 맞는 의존성 설치와 `@vendure/common`의 필요한 빌드를 시도한다. 각 명령의 종료 코드·signal·시간·실제 실패를 보존한다. install 성공, common build 성공, 앱 분석 성공을 서로 다른 상태로 기록한다.
4. 시간이 남으면 original Admin UI 설정과 기존 4진입 scoped 설정을 변경 없이 재관찰한다. 설치를 허용하지 않는 V1 runner/실패 전용 verifier를 소급 수정하지 말고 별도 후속 runner/결과를 둔다. 원래 strict/paths/generated source를 유지하고 실제 Program·진단·omissions·전체 구현 파일·함수 수를 남긴다. 호스트 Ontosary의 node_modules를 우연히 빌리지 않게 한다.
5. 오류가 남으면 그룹/FCA 결과를 만들지 않는다. 오류가 없어지면 같은 facts의 context 객체/속성 수와 기본 한도를 먼저 대조한다. **현재 네 진입 파일만의 함수 inventory도 129개로 객체 상한 128을 초과한다.** 전체 imports를 포함한 현재 함수는 2,264개다. 준비 성공이어도 상한에 맞지 않으면 “환경 준비 성공 / 탐색 비교 범위 미확보”로 중단한다. 개체 수뿐 아니라 속성 수 64도 확인한다. 성공한 작은 함수만 고르거나 상한을 높여 통과시키지 않는다.
6. 시간 내 가능하면 새 출력 경로에서 재관찰해 같은 준비 입력의 비시간 산출물을 대조한다. 설치 자체를 독립 재현하지 않았다면 의존성 설치 재현 완료라고 쓰지 않는다. 시간 부족이면 재현 미확인을 명시한다. cache 경로 길이에 따른 타입 표시 차이도 기존 제한으로 유지한다.

## 완료 조건과 후속 판단

성공 또는 근거 있는 중단 모두 완료물이다. 설치·common build·컴파일 진단 해소·범위 적합성·재현 여부를 각각 판정하고, 실제 비용 및 원시 실패를 남긴다. 사람 준비/탐색 시간·정답 승인·Gate 2~4 통과를 생성하지 않는다. HTML 필수 근거 두 개는 계속 수동 원문이며 자동 TS 분석의 성과에 넣지 않는다.

30분 만료, 원문/전제 변경 필요, 또는 FCA 범위 부적합이면 추가 투자 없이 보고한다. 그 후 검토할 선택지는 과업 범위 선택 계약, 탐색 사실과 논리 검증 전제 분리, 표본 전략 재검토다. 이번 작업에서 이들 설계를 구현하지 않는다. 핵심은 준비에 무제한 시간을 쓰지 않고 제품의 탐색 가치 검증으로 돌아갈 판단 근거를 얻는 것이다.

날짜별 후속 보고와 재현 명령/환경·예산·결과를 남기고 PROGRESS/RESEARCH를 실제 상태로 갱신한다. `pnpm check`, `pnpm experiment`로 기존 구현을 확인한다. staged diff 검토 후 지속 승인된 commit → push → PR/self-review → 검사 충족/검증 head merge → main 동기화를 완료한다. 참가자 연락·npm 배포·저장소 권한 변경은 포함하지 않는다.
