# S2 최상위 실패 처리의 정리 호출 보완 지시

2026-11-17. [독립 리뷰](2026-11-17-s2-seal-recovery-independent-review.md)의 **R17 잔여 한 건**을 보완한다. 실제 기본 정책 7단위와 R13/R14/R15/R16 검증은 유지하고, 감사 기록 실패에도 소유 자원 정리 호출이 이어지도록 한다. **로컬 60분 상한·새 VM 0개·runtime 실행 0회·유료 비용 0**이다. 개발 세션은 PR #54를 갱신한 뒤 결과 리뷰를 기다린다.

## 기준과 수정 범위

AGENTS, PROGRESS, ARCHITECTURE, ROADMAP, CONTRIBUTING과 위 리뷰를 읽는다. 구현 기준은 PR #54의 `d97007213c527fc06cc7d3708d7c546b14077d9b`다. 원격/head/사용자 변경을 확인하고 최신 main의 독립 리뷰와 이 지시를 통합한다. 기존 작업 브랜치를 이어 수정하며 공유 브랜치를 force-push하지 않는다. 이전 보고서와 원시 증거는 덮어쓰지 않는다.

수정은 `execution-lifecycle/round.py`의 최상위 실패 처리, 필요하면 그 작은 전용 helper, 해당 진입점 회귀와 관련 문서로 제한한다. `recovery.cleanup()`은 기존 소유권·시간·삭제·부재 확인 계약을 유지한다. guest/engine/reference/exporter, 실행 정책, cache 구조, 제품 core/CLI/FCA, 모델·TASK/B/C·배포 ID·Vendure 평가 의미는 변경하지 않는다. 하위 정리나 guest 변경이 불가피하면 이번 범위를 확대하지 말고 근거와 미완료 범위를 인계한다.

새 VM/이미지 build·download·import·정책 pair·실제 자격 증명 전달·로그인·provider/model 호출·본 비교를 하지 않는다. 보고서의 7단위를 수정 후 새로 실행한 것처럼 기록하지 않는다. R11 unresolved·R12 기존 범위·production/live 거부·fixtureOnly=true·validSubmission=false·trialAuthorized/readyForTrial=false·results=null을 유지한다.

## 구현 순서

1. 최초 UTC/monotonic, 기준 head와 허용 변경 목록을 기록한다. [독립 재현](evidence/2026-11-17-probe-cleanup-dispatch.py)을 기준 head에서 실행해 두 action의 기록 오류 6개가 cleanup을 건너뛰는지 확인한다. 이 스크립트는 역사적 결함 재현용이므로 수정 후에도 같은 assertion을 만족시키려고 하지 않는다.
2. 실제 `main()`의 prepare/fixtures 실패 경로를 회귀 테스트로 고정한다. `Round.cleanup()`만 직접 호출하는 테스트로 대체하지 않는다. 외부 실행을 대역화하고 임시 파일만 사용한다.
3. 감사 범위 동결/closing 등록 시도와 정리 호출을 분리한다. 예를 들어 기록 절차를 보호하는 try와 반드시 cleanup을 호출하는 finally를 두되, 최종 책임이 한 곳에 있게 한다. 기록 실패를 처리하는 과정의 추가 기록 실패도 정리를 막지 않아야 한다. cleanup은 해당 실패 흐름에서 정확히 한 번 시도한다.
4. 최초 작업 오류, 감사/기록 오류, cleanup 오류를 구분해 보존하고 비정상 종료한다. 기존 예외 chaining 또는 작은 오류 목록이면 충분하며 범용 오류 프레임워크를 만들지 않는다. 파일 기록 불가 시에는 크기가 제한된 stderr 진단으로 가능한 사실을 남긴다. 진단 출력 실패 자체가 정리 호출을 막지 않게 한다.
5. 감사 등록 실패는 성공으로 복구하지 않는다. 정상 등록 가능 시에는 기존 분석/closing ID·hash·명령 대조를 유지한다. 등록 실패 시 불완전 상태를 보존하고 유효 증거 포장·다음 실행은 거부한다. 미등록 snapshot 자동 편입, 빈 목록으로 덮어써 성공 처리, 누락 hash 생성으로 봉합하지 않는다. 기존 소유권 확인 실패에서 임의 자원 삭제를 허용하지 않는다.

## 검증

| 경로 | 필수 확인 |
| --- | --- |
| prepare / fixtures의 최초 실패, 기록 성공 | cleanup 정확히 1회·최초 오류 보존·비정상 종료·기존 감사 등록 유지 |
| 각 action + analysis-scope 쓰기 실패 | cleanup 1회·최초/기록 오류 모두 식별·감사 완료로 승격하지 않음 |
| 각 action + closing-registry 쓰기 실패 | 부분 동결 상태에서 cleanup 1회·실패 상태 보존·미등록 증거 성공 포장 거부 |
| 각 action + closing snapshot 생성/등록 실패 | cleanup 1회·추가 실행 없음·자동 편입 없음 |
| 기록 실패 + cleanup 자체 예외 | 두 단계 오류와 최초 오류 식별·재귀/중복 cleanup 없음·비정상 종료 |
| 실패 기록 또는 stderr 출력까지 실패 | cleanup 시도는 유지·오류를 성공으로 삼키지 않음 |
| action 정상 완료 | 오류용 cleanup을 임의 추가 호출하지 않음·기존 명시적 cleanup 수명주기 유지 |

새 테스트는 실제 CLI dispatcher를 실행하고 외부 작업만 대역화한다. 최소 한 기록 실패 사례는 실제 기존 `Round.cleanup()`까지 연결해 가짜 외부 명령의 stop/delete/부재 확인이 도달함을 확인한다. 이때 subprocess/VM을 실제로 시작하지 않는다. 기존 recovery의 transport/copy/stop/delete 실패 회귀와 ownership 거부를 유지한다. 정상 감사 등록과 감사 불완전 상태의 package 거부는 기존 실제 snapshot/package 계약에 연결해 검증하며, 모든 helper를 mock한 호출 횟수 검사만으로 끝내지 않는다.

`pnpm check`, execution-lifecycle 전체 Python, 공유 lifecycle/collector, single-policy-test 감사/deadline/package 회귀와 과거 두 회차·11월 17일 저장 verifier를 실행한다. 기준은 제품 304개·Python 174개이며 새 테스트/skip 수를 분리한다. 기존 7단위의 Spec/봉인/회수 archive를 오프라인 재대조하되 새 runtime으로 세지 않는다. TS 분석/평가 의미 불변이면 `pnpm experiment`·Vendure 전체 평가 재실행은 생략 이유를 보고한다.

## 비용·중단·완료 조건

읽기/재현/구현/검증/보고를 최초 시계부터 총 60분에 포함한다. 40분에는 새 구현 탐색을 멈추고 남은 20분을 검증·인계에 사용한다. Git 게시 시간은 별도로 기록하되 실험 재개에 쓰지 않는다. 예산은 소진 목표가 아니며 일찍 끝나면 인계한다.

최상위 국소 수정으로 해결할 수 없음, guest/권한/감사 의미 변경 필요, 기존 증거 불일치, 필수 회귀 실패 또는 시간 상한이면 부분 완료로 인계한다. 준비물을 복구하려고 새 다운로드/VM 실행을 시작하지 않는다. 예상 밖 실패를 숨기거나 검사를 완화하지 않는다.

완료 조건은 실제 main의 기록 실패 경로 모두에서 안전한 cleanup 시도·오류 보존·유효 결과/다음 실행 차단이 확인되고, 기존 실제 7단위 증거와 제품/감사 회귀가 유지되는 것이다. 자원 정리 완료와 감사 기록 완료는 다른 상태로 보고한다. 이번은 새 runtime 검증이나 R11 전체 해결이 아니다.

새 보고서는 `docs/reviews/2026-11-17-s2-cleanup-dispatch-fix.md`에 작성하되 실제 날짜가 다르면 맞춘다. 기준/최종 head, 변경 파일, 독립 재현 전후, 실제 진입점별 테스트, 오류 전달 방식, 저장 verifier 결과, 비용과 미실행 항목을 적고 PROGRESS/README/리뷰 맥락을 갱신한다. 새로운 작은 로컬 증거만 추가하고 과거 원시 자료는 보존한다. 검증·커밋·push·PR #54 갱신 뒤 **독립 결과 리뷰를 기다리고 병합하지 않는다.**
