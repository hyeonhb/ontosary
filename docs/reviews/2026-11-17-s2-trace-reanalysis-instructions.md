# S2 저장 trace 오프라인 판독 보완 지시

2026-11-17. [정책 대조 독립 리뷰](2026-11-17-s2-policy-pair-independent-review.md)의 strace 안내문 혼합 형식만 보완한다. **읽기·구현·검증·보고 전체30분, VM/container/runtime/정책 변경/유료 비용0**이다. 실제 mount 차단을 해결하는 작업이 아니며 실행 경계의 다음 설계와 독립적으로 진행할 수 있다.

## 기준과 변경 범위

AGENTS·PROGRESS·ARCHITECTURE·ROADMAP·CONTRIBUTING과 위 리뷰를 읽는다. PR #61 병합 `ee7ac98` 이후 최신 main에서 새 짧은 작업 브랜치를 만든다. 최초 명령에 UTC/monotonic을 함께 기록하고 시작 head·변경 허용 목록·시간 상한을 남긴다.

입력은 `experiments/domain-model/s2/verification/2026-11-17-policy-pair/`의 저장 원문이다. 후보 `calls[-1].stderr` SHA-256은 `9a949992b23a81361f821d9ec6fd227eebcd4a6a1c1cf8801ee698660e117c5c`다. 원래 trace와 기존 정상/unfinished 사례도 회귀 입력으로 사용한다. 원시 archive·index·보고서·candidate-trace-analysis·pair-complete는 불변이다.

범위는 작은 오프라인 재분석 도구와 순수 판독 함수/테스트, 별도 파생 산출물과 문서다. 동결된 과거 parser와 기존 verifier가 이전 inconclusive를 그대로 재현하도록 유지한다. 기존 runtime 경로의 parser를 무조건 교체하거나 verifier의 저장 결과 비교를 느슨하게 하지 않는다. 새 판독은 별도 명시적 진입점으로 제공한다. 범용 parser 버전 관리 체계나 strace 전체 문법 구현은 만들지 않는다.

## 판독 계약

1. 저장 archive/index/hash를 확인하고 봉인된 결과의 trace를 읽는다. 입력 hash·기존 자동 판정·새 판독 도구 hash/commit·지원 형식·근거 범위를 새 출력에 기록한다.
2. 현재 실제 형식인 PID가 있는 clone 시작 줄 + 그 안의 정확한 strace attach 안내 + PID 없는 바로 다음 완료 줄을 제한적으로 연결한다. syscall 이름·flags·부모 PID·attach 자식 PID·반환값이 일치하는 경우만 인정한다. 중간에 다른 syscall/프로세스 출력이 끼거나 완료 줄이 불명확하면 추측하지 않는다.
3. PID별 pending 상태와 원문 줄 번호를 보존해 한 번의 행 순회로 처리한다. 지원 범위 안에서 시간 O(n), 추가 상태는 미완료 호출 수에 비례하도록 한다. 기존 회수16MiB 상한을 넘는 입력은 거부하고 불완전 행/보류 상태에도 명시적 상한을 둔다. 줄을 무제한 이어 붙이거나 원문 전체에서 `strace:` 문자열을 전역 삭제하지 않는다.
4. 단일 줄·unfinished/resumed의 기존 의미를 유지한다. 원문과 파생 해석을 분리하고 각 clone/반환/mount 관찰에 원문1기반 줄 범위를 연결한다. 부분 문자열 일치로 추가 flags를 같은 호출로 인정하지 않는다. 알 수 없는 형식·중복/다중 연결 후보·PID/자식 불일치·truncation은 inconclusive와 이유를 남긴다.
5. bwrap exec와 사전 검사/명령 준비 역할, 해당 clone의 자식 mount 거부를 연결한다. 다른 PID의 EPERM을 해당 자식의 실패로 합치지 않는다. syscall 실패 관찰만으로 seccomp/AppArmor 등 정확한 원인을 확정하지 않는다.

기존 순수 판독 코드를 재사용할 수 있지만, 새 정규화가 뺀/연결한 원문 범위와 이유가 추적돼야 한다. 임시 파생 문자열에서 결과만 통과시키고 근거 연결을 생략하지 않는다. 도구 실행은 원문/동결 결과를 수정하지 않아야 한다.

## 검증과 완료 조건

- 실제 저장 후보에서 precheck41→42(64–65행), command preparation43→44(132행), 자식 mount 거부110/178행을 재현한다. 새 파생 판정은 first-clone-passed-next-blocked, payloadStarted=false, lsmCauseConfirmed=false다. 기존 자동 판정 inconclusive도 함께 표시한다.
- 원래 정책의 두 clone EPERM, 기존 단일 줄/unfinished-resumed, 합성 payload 완료 판정은 보존한다.
- attach PID와 반환 자식 불일치, 서로 다른 부모의 interleaving, orphan 완료 줄, 잘린 호출, 추가 flags, 중복 연결, 다른 PID의 mount 실패를 부정 사례로 검증한다. 정보가 부족하면 성공 판정을 만들지 않는다.
- 원문/hash/과거 결과 불변과 새 출력의 근거 줄 대조를 검사한다. 새 출력은 별도 디렉터리에 저장하며 기존 index에 사후 편입하지 않는다. 기존4개 저장 verifier는 기존 status 그대로 통과해야 한다.
- `pnpm check`·execution-lifecycle/공유 lifecycle/감사 회귀와 새 판독 회귀를 실행한다. 기준304개·Python208개와 새 테스트 수/skip을 분리한다. TS/평가 불변이면 pnpm experiment와 Vendure 평가는 반복하지 않는다.

20분에 새 구현 탐색을 끝내고30분까지 검사·보고한다. 제한된 문법으로 확실한 연결을 만들기 어렵거나 기존 감사/판정 계약을 바꿔야 하면 부분 인계한다. 보고를 맞추기 위한 전역 치환·줄 번호 하드코딩·새 runtime 실행은 하지 않는다. Git 게시 시간은 별도 기록하며 실험 재개에 쓰지 않는다.

실제 날짜의 `docs/reviews/YYYY-MM-DD-s2-trace-reanalysis.md`와 별도 작은 evidence를 추가한다. 시작/최종 head, 지원/미지원 형식, 이전/새 판정·입력 hash·원문 근거, 검사 수와 비용을 기록하고 PROGRESS/리뷰 맥락을 갱신한다. 검증·커밋·push·PR 작성 뒤 결과 리뷰를 기다린다. 이 작업으로 과거 실제 정책 회차를 재실행했다고 기록하지 않는다.

mount 허용·추가 권한·CLI 설정/실행 경계 변경·실제 자격 증명 전달·provider/model·본 비교는 제외한다. R11 unresolved·production/live 거부·fixtureOnly=true·validSubmission=false·trialAuthorized/readyForTrial=false·results=null을 유지한다. 새 판독의 완료는 다음 아키텍처 선택이나 실제 실행 승인을 대신하지 않는다.
