# S2 지연된 자식 문맥 판독 보완 지시

2026-11-17. [독립 리뷰](2026-11-17-s2-trace-reanalysis-independent-review.md)의 **R18 한 건**을 보완한다. 기존 offline parser의 부모 clone 반환 이전에 출력된 자식 이벤트에도 동일한 지원 범위 검사를 적용한다. **총30분·새 VM/container/runtime/정책 변경/유료 비용0**이다. 실제 mount 허용이나 실행 경계 변경은 범위 밖이다.

## 기준과 수정 범위

첫 명령에서 UTC와 host monotonic을 함께 저장하고 같은 명령에서 git 상태/기준 head를 확인한다. AGENTS·PROGRESS·ARCHITECTURE·ROADMAP·CONTRIBUTING·위 리뷰와 [직전 지시](2026-11-17-s2-trace-reanalysis-instructions.md)를 읽는다. 기준은 PR #63의 `8bba520a8fe91355d367642eebf2f8218133cf83`이며 최신 main의 리뷰/지시를 통합하고 기존 작업 브랜치를 이어 수정한다. 사용자 변경/과거 증거를 덮거나 공유 브랜치를 force-push하지 않는다.

변경은 trace_reanalysis.py·해당 회귀·새 파생 증거/문서에 한정한다. policy_pair.py·verify_pair.py와 과거 verifier, runtime/수명주기/정책/cache·제품/FCA/평가 의미는 불변이다. 이전 derived.json과 그 도구 hash/index도 보존한다. 완전한 strace parser나 일반 프로세스 수명 추적기를 만들지 않는다.

## 구현 순서

1. [독립 반례](evidence/2026-11-17-probe-deferred-child-context.py)를 기준 head에서 재현한다. 현재 exec-before-resume만 next-blocked로 통과하고, exec-after-resume은 inconclusive임을 기록한다. 반례의 원시 입력은 역사적 재현 자료로 보존하고 수정 후 assertion을 맞추려고 바꾸지 않는다.
2. 실패하는 회귀를 먼저 추가한다. 실제 parse_trace를 호출하고 같은 이벤트에서 부모 반환의 출력 위치만 바꾼 두 순서가 같은 보수적 판정을 내리도록 검증한다. 기존 정상 child-denial-before-resume은 유지한다.
3. 자식 PID가 확정되기 전에도 필요한 문맥 이벤트와 원문 줄 위치를 제한된 형태로 보존한다. clone 시작 이후의 해당 PID 문맥을 확정 시점에 검토하고, 자식 exec 또는 미지원 child mount가 있었으면 후속 거부를 확정 판정에 사용하지 않는다. 현재 즉시 적용하는 `children` 기반 검사와 지연 연결의 검사가 같은 지원 범위를 따르게 한다.
4. 필요한 문맥이 누락·중복·상한 초과 등으로 불명확하면 inconclusive와 이유를 남긴다. 무관한 다른 PID나 clone 시작 이전의 이벤트를 해당 자식 문맥으로 합치지 않는다. 입력을 다시 전체 순회하거나 모든 PID의 무제한 이벤트 목록을 보관하지 않는다. O(n) 순방향 처리, 기존16MiB·행/pending/관찰/오류 상한을 유지하고 추가 문맥 상태에도 명시적 상한을 적용한다.
5. 실제 원래/후보 archive를 새 출력 경로에 재분석한다. 과거 동결 결과/첫 파생 결과를 갱신하지 않는다. 새 출력의 입력 hash·도구 commit/hash·이전/새 판정·원문 근거와 변경 이유를 연결한다. runtime 재실행으로 기록하지 않는다.

자료구조는 이 작은 검증에 필요한 수준에서 선택한다. bounded PID별 문맥 요약 또는 관찰 목록을 재사용할 수 있다. 필요한 정보가 없는 경로를 추측해 연결하거나, 지원하던 모든 unfinished/resumed 입력을 일괄 거부하는 방식으로 해결하지 않는다.

## 검증과 완료 조건

| 사례 | 기대 결과 |
| --- | --- |
| 부모 반환 뒤 자식 exec→mount | 기존 inconclusive 유지 |
| 자식 exec→mount 뒤 부모 반환 | inconclusive, 원문 위치와 미지원 문맥 이유 포함 |
| 자식 mount만 먼저 나오고 부모 반환이 뒤따름 | 기존 next-blocked 유지 |
| 자식의 미지원 split mount가 부모 반환 전/후에 출력됨 | 두 순서 모두 같은 보수적 거부 |
| 두 부모의 unfinished/resumed interleaving·반환 순서 역전 | 올바른 PID별 연결, 문맥 교차 혼합 없음 |
| 무관 PID의 exec/mount 또는 clone 시작 이전 이벤트 | 해당 자식 실패의 근거로 편입하지 않음 |
| 추가 문맥 저장의 상한 도달/누락 | inconclusive·명시적 이유, 메모리/시간 상한 유지 |
| 실제 저장 원래/후보 trace | 원래 clone-still-denied, 후보 first-clone-passed-next-blocked, payload/LSM 확정 false 유지 |

새 실패 회귀만 통과시키지 말고 기존35개 판독 사례와 전체 execution-lifecycle/공유 lifecycle/감사 회귀를 실행한다. 기준 Python243개에 새 테스트를 구분하고 skip을 보고한다. `pnpm check`304개와 과거4개 verifier도 통과해야 한다. 옛 pair 자동 inconclusive·첫 파생 결과·모든 원문/hash 불변을 확인한다. TS/평가 불변이면 pnpm experiment/Vendure 전체 평가는 생략 이유를 기록한다.

읽기·재현·구현·검사·보고를 최초 동시 시계부터30분에 포함한다.20분에 새 구현 탐색을 끝내고 남은10분은 검사·인계에 쓴다. runtime/공통 감사 계약 변경이 필요하거나 상한 내 국소 해결이 어려우면 부분 인계한다. Git 게시 시간은 별도이며 새 분석을 재개하는 데 사용하지 않는다.

실제 날짜의 `docs/reviews/YYYY-MM-DD-s2-trace-context-fix.md`와 새 evidence 디렉터리를 추가한다. 변경한 문맥 보존 방식·상한·반례 전후·실제 저장 trace의 판정 유지·검사/비용/미완료 범위를 적고 PROGRESS/리뷰 맥락을 갱신한다. 검증·커밋·push·PR #63 갱신 뒤 **독립 리뷰를 기다리고 병합하지 않는다.**

완료는 지원 범위 내 로그 순서에 의해 미지원 문맥이 확정 판정으로 승격되지 않는 것이다. 실제 격리 권한·CLI 설정·자격 증명/provider/model·본 비교와 R11 전체 해결로 확대하지 않는다. fixture/trial/production 차단과 H-O/H-F 미검증을 유지한다.
