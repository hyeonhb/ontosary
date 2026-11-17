# S2 지연된 자식 문맥 보완 독립 리뷰

2026-11-17. [인계 보고서](2026-11-17-s2-trace-context-fix.md)와 PR #63의 `ade291f0891e20bd8a4545cb126dc3b29196761a`을 검토했다. 실행 구현은 `26c8b41cf27badd05f1bc6d84358fa465b82c384`와 같다. **R18은 해결됐다. 이번 보완 범위에서 추가 차단 결함은 발견하지 않았고, 검증한 head로 PR #63을 병합했다.** 병합 commit은 `0181606e2a3b19184de15dcfc5267f35ed63e28d`다.

## 해결 근거

[trace_reanalysis.py](../../experiments/domain-model/s2/trial/container/execution-lifecycle/trace_reanalysis.py)는 namespace clone이 pending이거나 자식이 이미 확인된 동안 exec/미지원 mount의 PID·원문·행 위치를 보존한다. 최종 연결 시 반환된 자식 PID와 clone 시작 이후인지 대조하므로, 부모 반환의 출력 시점과 관계없이 같은 문맥 검사를 적용한다. 무관 PID나 clone 시작 이전의 사건은 해당 자식 문맥으로 승격하지 않는다.

미지원 문맥이 있는 자식의 실패는 `nextDenied`에서 제외하고 `contextRejectedDenied`에 남긴다. 판정 근거로 인정하지 않는 것과 원문을 버리는 것을 구분한다. 추가 문맥128개/64KiB 상한을 넘으면 contextComplete=false·이유를 남기고 확정 판정을 거부한다. 입력을 다시 전체 순회하지 않고 최대128개 문맥만 후처리하므로 기존 선형 처리와 유한 상태 계약을 유지한다.

이전 [독립 반례](evidence/2026-11-17-probe-deferred-child-context.py)의 원시 입력을 그대로 새 parser에 전달했다.

| 사건 출력 순서 | 독립 재검증 결과 |
| --- | --- |
| 부모 반환 → 자식 exec → mount 거부 | inconclusive, 해당 자식 거부를 판정 근거에서 제외 |
| 자식 exec → mount 거부 → 부모 반환 | 위와 동일, R18 재현 해소 |
| 자식 mount 거부 → 부모 반환, exec 없음 | 기존 next-blocked 유지 |

추가로 두 부모/자식의 선행 관계를 보존한 로그 순서를 생성했다. exec 전환이 없는 **280개** 순서는 모두 next-blocked, 한 자식의 exec 전환이 있는 **756개** 순서는 모두 inconclusive이며 그 자식의 거부가 승인 근거에서 제외됐다. 이는 해당 작은 사건 집합의 순서 검증이며 모든 strace 문법이나 전체 프로세스 수명 검증을 뜻하지 않는다. [독립 probe](evidence/2026-11-17-probe-trace-context-fixed.py)는 외부 실행 없이 실제 parse_trace를 호출한다.

## 검사와 증거

- 검토 head에서 `pnpm check` **304개**·타입·예제 build와 Python execution-lifecycle **197**, 공유 lifecycle **16**, 감사 **44**, 총 **257개**, skip0을 확인했다. 새14개 회귀는 exec·split/resumed/미지원 mount의 전후 순서, 서로 다른 부모/반환 순서, 다른 PID/clone 이전 사건, 문맥 개수/바이트 상한·중복과 근거 분리를 검사한다. 독립 순서1,036개는 이 고유 테스트 수에 합산하지 않는다.
- 과거4개 verifier가 모두 통과했다. 실제 저장 원래 trace의 clone-still-denied, 후보의 first-clone-passed-next-blocked가 유지됐다. 후보 clone64–65/132행·mount110/178행·역할55/123행의 원문 연결도 같다. payloadStarted/lsmCauseConfirmed는 false다.
- 새 CLI로 생성한 파생 JSON은 **tool.checkoutHead를 제외하고 저장된 새 결과와 일치**했다. 저장본은 구현 commit26c8b41, 독립 실행은 문서 포함 ade291f라 식별자가 다르다. 첫 파생 결과와는 새 문맥 필드/도구 hash가 달라 전체 동일성을 주장하지 않으며, 이전/새 결과의 입력 hash·판정·핵심 근거 필드와 comparison.json의 hash 연결을 대조했다.
- 첫 파생 bundle의 index 대상 **14파일**, 이번 bundle의 **17파일**을 hash/크기로 검증했다. 리뷰 통합 기준 e68064f의3,696파일 중 기존 변경은 의도한5개뿐이며, 과거 verification **2,379파일**·첫 파생15파일(index 포함)·원래 반례·동결 parser/verifier는 유지됐다.
- 구현 변경은 offline parser와 해당 테스트에 한정됐다. 공통 runtime/수명주기/정책/cache·제품/FCA/평가 의미는 불변이다. 이 리뷰에서도 VM/container/runtime/권한/인증/model 호출은0회다. pnpm experiment·Vendure 전체 평가는 반복하지 않았다.

검증 요약과 로그 hash는 [독립 JSON](evidence/2026-11-17-s2-trace-context-independent.json)에 남겼다. 최초 명령의 UTC/monotonic 동시 계측도 이번에는 기록됐으며 보고된644.785초는30분 상한 안이다. PR은 실제 검사와 자체 리뷰 후 병합했으며 다른 사람의 승인을 주장하지 않는다.

## 완료 범위와 다음 단계

저장 trace의 제한된 오프라인 판독 보완은 여기서 완료한다. 추가 parser 작업 지시나 새 실제 실험을 자동으로 이어갈 필요는 없다. 일반 strace 문법, 자식 exec 이후의 동작, 정확한 LSM 원인은 여전히 지원/검증 범위 밖이며 해당 불확실성을 성공으로 해석하지 않는다.

다음은 사용자와 **외부 컨테이너/VM과 내부 CLI sandbox의 격리 책임**을 정하는 아키텍처 논의다. 현재 관찰은 clone 통과 뒤 mount EPERM이며, 이를 근거로 mount 권한을 바로 추가하거나 내부 sandbox를 제거하기로 결정하지 않는다. 파일·제어 상태·인증·네트워크·자손 종료의 보장을 어느 경계가 맡을지 먼저 합의한 뒤 다음 구현/실험 지시를 작성한다.

R11 unresolved·R12 기존 범위·production/live 거부·fixtureOnly=true·validSubmission=false·trialAuthorized/readyForTrial=false·results=null을 유지한다. 추가 정책/권한·실제 인증/model·본 비교와 H-O/H-F 검증은 진행하지 않았다. 이번 완료는 관찰 도구의 신뢰성 보완이며 도메인 모델의 agent 변경 효용을 입증한 결과는 아니다.
