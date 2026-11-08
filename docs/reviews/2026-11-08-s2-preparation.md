# S2 준비 구현 인계 — 2026-11-08

**합의된 S2 준비 모듈·실제 A/B/C 자료·제출 코드 평가 하네스·재현 검증을 구현했다. 독립 리뷰 대기이며 본 비교는 실행하지 않았다.** readyForTrial=false다. 과업 실패 처리, 사람의 B/C 동등성·oracle 충실성, agent 모델/예산·실제 격리는 여전히 동결 전이다. H-O/H-F나 업무 의미 승인·Gate 상승을 주장하지 않는다.

기준 main `f080e39b7a853fc0f06384294f3758897ddc5406`, 브랜치 `codex/s2-preparation`, 미병합 의존 브랜치 없음. 최종 반영 전 원격 안내 문서 PR #22/main `8df8a1a` 위로 재배치했고 병행 변경을 보존했다. [개발 지시](2026-11-08-s2-development-instructions.md), [구현 README/명령](../../experiments/domain-model/s2/README.md), [사전 설계](../../experiments/domain-model/s2/DESIGN.md).

## 완료 조건별 근거

| 조건 | 실제 구현·검증 | 남은 리뷰/제한 |
| --- | --- | --- |
| 타입 검사·모듈 경계 | analysis-session/model/validate/query/bundle/adapter/CLI, 별도 tsconfig를 pnpm check에 연결 | 제품 core/public API 미승격 |
| 실제 baseline | 원문4,735·준비 Program1,638·설정/해석 입력·S1 hash와 진단 검증, Program1회 | 고정 입력 검증이며 일반 live 원자 snapshot 아님 |
| 모델 의미/closure | 12항목·16방향 링크 의미 보존, fact22/candidate2와 선언/역할 정의 제공, 승인0 | 업무 의미 검토 pending; 전체 앱 영향 범위 아님 |
| 실제 B/C 자료 | JSON/Markdown 동일 파일 단위·명제/근거/질문/상태, allowlist/hash·GPL 고지·parity | 자동 coverage와 사람 의미 동등성은 별개 |
| 제출 코드 oracle | 실제 제출 메서드/상대 helper 실행, baseline/참조 수정/6결함 변형 교정 | Angular/서버/constructor·field·전체 비동기망 제외; fidelity pending |
| 실행 계획/readiness | 실제 파일 hash/세 ID, 미정 모델·도구·예산·seed·격리·테스트 경계 | readyForTrial=false, 본 비교 미실행 |
| 회귀/통합/재현 | 22새 항상 실행 fixture·전체196테스트/skip0·기존4/4·147파일 재현 | 독립 설치/타 플랫폼 재현 아님 |
| 인계/반영 | 새 README/날짜별 보고/현재 문서와 원시 자료 | 독립 reviewer의 승인으로 표시하지 않음 |

원래 S1/V1/V2 코드·입력·결과·독립 증거, 제품 src/core/CLI, strict/논리/FCA 알고리즘·상한은 그대로다. package에는 실험 명령과 기존 검사에 추가되는 TS 검사를 넣었다. 새 제3자 의존성·설치·agent/chat 생성은 없다. 원래 30분 준비 예산을 재개하지 않았다.

## 계약과 검증 결과

세션은 open→inspect→evidence→seal→dispose이며 예외에도 finally로 종료한다. seal은 hash cache만 확인하지 않고 원문/Program/CompilerHost 해석 입력을 재읽고 root 목록 및 file/directory lookup 상태를 확인한다. SourceTable은 canonical path hash와 필요한 텍스트/lineStarts를 재사용한다. UTF-16/배타적 end·1-based 좌표와 Unicode/CRLF를 검사한다. 내부 seal 객체만 배포 입력이 되고 외부 verified=true는 통과시키지 않는다.

모델은 구조/enum/ID·참조 종류·근거 좌표/지문·상태를 검사한다. approved metadata ingest는 지원하지 않고 기존 pending 12항목과 승인0을 유지한다. navigation은 방향 있는 related-item이고 fact/candidate 의존과 별개다. query는 fs/compiler/process 없이 소유 복제·ID/adjacency/evidence 색인으로 조회한다. 결과 변조가 내부 모델을 바꾸지 않는다. 과거 baseline 자료와 편집 중 소스는 sourceVersion/currentWorkspaceAssessment로 구별한다.

baselineId는 분석 입력·Node/TS/정책, modelId는 해석/관계/근거, bundleId는 배포 allowlist 파일/포장 버전을 식별한다. JSON key 정렬·배열 순서 보존·UTF-8/LF·상대 경로로 결정성을 유지하고 시각/자기 hash/evaluator metadata는 해당 ID 입력에서 제외한다. sourceVersion은 baseline, currentWorkspaceAssessment는 not-performed다. 타 revision 결합과 위조 baseline을 회귀로 거부했다.

[원시 검증 디렉터리](../../experiments/domain-model/s2/verification/2026-11-08)에 196테스트/비교4 로그, 의미 보존, allowlist 검사, symlink를 evaluator로 향하게 한 부정 배포 거부, 재현 hash가 있다. 새 22개 fixture는 cache 없어도 실행된다. 기존 cache 의존 테스트도 이번에는 실제로 실행되어 skip0이다. 입력 변경/누락/진단·seal 중 변경·dispose 뒤 호출, malformed model/enum/승인·중복/잘못된 참조, R6 탐색·조회 불변성, 상한/경로/기존 출력/중간 쓰기 실패, 제출 helper 변경·미지원 field·Promise/async 변경을 확인했다.

## B/C 배포와 격리

[배포 자료](../../experiments/domain-model/s2/results/2026-11-08)에서 B는 구조화 view, C는 같은 의미 값들을 명명된 단락/목록으로 제공한다. 단순 축약이나 padding이 아니다. [information-parity](../../experiments/domain-model/s2/results/2026-11-08/evaluator/information-parity.json)는 unit별 B/C 파일·line·근거·상태·semantic hash를 담는다. B 133,134 bytes, C 120,100 bytes다. tokenizer 미정으로 token 수는 null이다. 자동 leaf/참조 coverage를 확인했지만 사람이 읽은 의미 동등성은 pending이다.

12개 모델 항목과 관련 후보2개를 모두 유지했고 closure 밖 fact/candidate는 제외 이유를 기록했다. 후보 구성원은 identity/선언을 제공하고 관련 없는 cells 참조는 projection에서 제외했다. 전체23MB scan이나 MODEL.md 변경 예시·평가 정답·제작 로그·코드는 제공하지 않는다. 라이선스/출처 원문은 유지한다.

workspace builder로 조건별 원문4,735개와 해당 자료만 복사한 실제 폴더를 생성하고 allowlist/hash를 대조했다. symlink/evaluator 파일0이며 symlink 경유 유입도 거부했다. **같은 호스트의 다른 폴더는 격리가 아니므로 isolation=unverified**다. 본 실행 전 별도 OS/container에서 evaluator/checkout/다른 제출에 접근하지 못하게 해야 한다. node_modules는 workspace에 복사하지 않았으며 공통 runtime mount/권한도 동결 대상이다. 이번에 비교 agent를 만들지 않았다.

## 과업과 oracle

[과업/원문 대응·seam 검토안](../../experiments/domain-model/s2/evaluation/TASK-REVIEW.md)은 reason을 trim/nonblank로 제한하는 클라이언트 로컬 요구다. 실제 제품 정책이나 서버/schema 변경 승인으로 취급하지 않는다. invalid 입력 처리에는 요청/연쇄 환불 중단 또는 타입화 오류 처리 대안이 있고 현재 참조 oracle는 전자를 검토용으로 구현했다. 실패 처리와 stream/UI 오류 동작은 독립 검토 후 확정해야 한다.

하네스는 제출 root에서 네 클래스의 실제 본문 및 지원되는 새 상대 helper를 실행한다. 취소/환불 분기·입력 변환·오류 결과 처리는 대역 안에 재작성하지 않았다. Angular DI/constructor/field/상속/decorator·UI·서버 응답을 명시적으로 제외하며 이 excluded seam을 수정한 제출은 미지원으로 거부한다. 정상 취소+환불 호출 수/순서와 양수 lines의 값도 판정한다. 실제 고정 RxJS를 사용하고 unhandled runtime 실패를 성공으로 세지 않는다. VM은 보안 sandbox가 아니다. HTML 조건은 수동 리뷰 범위다.

| 제출 버전 | 기존 동작 | 새 요구 | 구별한 결함 |
| --- | ---: | ---: | --- |
| baseline | 6/6 | 3/18 | 기존 소스는 새 요구 일부 미충족 |
| 임시 참조 수정 | 6/6 | 18/18 | 검토용 정책 아래 통과 |
| 직접 취소만 수정 | 6/6 | 8/18 | 환불중취소/API 경계 누락 |
| trim 누락 | 6/6 | 12/18 | 공백/공백만 입력 |
| 모든 환불에 취소 | 5/6 | 18/18 | 환불만 경로 |
| dismiss에서 요청 | 5/6 | 18/18 | 취소 dialog 닫기 |
| 취소 실패 뒤 환불 | 5/6 | 18/18 | 오류 결과 처리 |
| 정상 취소 뒤 환불 누락 | 6/6 | 16/18 | 정상 경로 호출 수/순서 |

[교정 요약](../../experiments/domain-model/s2/verification/2026-11-08/oracle-summary.json)과 버전별 결과/원문 hash·anchor/임시 수정 증거를 보존했다. 실제 cache는 수정하지 않았다. 이 수치는 agent 효과가 아니라 oracle 검증이다.

## 비용과 다음 판단

실제 준비 첫4.274초/반복4.265초, 비시간147파일 및 세 ID 일치다. Program1, host reads1,762, explicit reads6,057, hash7,819, seal rereads6,134다. 원문4,735와 Program1,638을 포함한 중복 명세 입력6,386항목을 처리했다. 종료 RSS715,833,344 bytes(peak 아님), seal 비용 약212ms를 별도 기록했다. oracle8변형 검증은 약3.172초다. 전체 agent 개발/사람 작성·검토/재작업 시간과 agent trial token/time은 미측정이다. 이전 V2는 추출도 수행했으므로 속도 개선 배수로 비교하지 않는다.

재현 명령은 README의 s2:prepare(2회), s2:verify, 자체 fixture, s2:oracle-check, s2:workspace 및 pnpm check/experiment와 일치한다. [resolved run-plan](../../experiments/domain-model/s2/results/2026-11-08/evaluator/run-plan.json)에 실제 B/C hash와 미정 조건이 있다.

다음 한 작업은 독립 리뷰로 구현·B/C 동등성·oracle 원문 충실성을 확인하고 과업 실패 처리/격리/agent 버전·예산·배정 조건을 동결하는 것이다. 완료된 준비 구현과 본 비교 실행 승인을 구분한다. 아직 H-O/H-F·사람 의미 승인·S3·Gate 상승은 미검증이다.
