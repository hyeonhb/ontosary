# S2 오프라인 trace 판독 독립 리뷰

2026-11-17. [PR #63](https://github.com/hyeonhb/ontosary/pull/63)의 `8bba520a8fe91355d367642eebf2f8218133cf83`와 [개발 보고서](https://github.com/hyeonhb/ontosary/blob/8bba520/docs/reviews/2026-11-17-s2-trace-reanalysis.md)를 검토했다. **실제 저장 trace의 새 판독과 과거 자료 보존은 확인했다. 다만 지연된 부모–자식 연결의 미지원 문맥을 놓치는 R18이 있어 PR #63은 병합을 보류한다.** 이 문제는 오프라인 증거 판정의 결함이며 실제 격리 경계가 뚫렸다는 의미가 아니다.

## R18 · Medium · 부모의 resumed 로그보다 먼저 나온 자식 문맥을 놓친다

위치: [trace_reanalysis.py 156–157행](https://github.com/hyeonhb/ontosary/blob/8bba520/experiments/domain-model/s2/trial/container/execution-lifecycle/trace_reanalysis.py#L156), [227–241행](https://github.com/hyeonhb/ontosary/blob/8bba520/experiments/domain-model/s2/trial/container/execution-lifecycle/trace_reanalysis.py#L227).

현재 자식 exec 거부는 `pid in children`일 때만 실행한다. `children`은 부모 clone의 반환을 읽은 뒤 등록된다. 한편 판독기는 자식의 mount 실패가 부모의 resumed 반환보다 먼저 출력되는 순서를 지원하기 위해, 끝에서 보관한 실패를 반환된 자식 PID에 연결한다. 이때 **먼저 출력된 자식 exec 등 문맥을 다시 검사하지 않는다.**

다음은 유효하게 interleave될 수 있는 합성 trace의 핵심 순서다.

```text
[pid 41] clone(...정확한 기존 flags... <unfinished ...>
[pid 42] execve("/usr/bin/other", ["other"], 0) = 0
[pid 42] mount(...) = -1 EPERM (Operation not permitted)
[pid 41] <... clone resumed>) = 42
```

다른 bwrap 역할의 정상 clone/자식 mount 거부를 함께 주면 현재 parser는 `issues=[]`, **first-clone-passed-next-blocked**를 반환한다. 부모 반환을 자식 exec보다 먼저 출력한 대조 입력에서는 동일한 exec가 `child-exec-outside-denial-scope`로 잡혀 **inconclusive**가 된다. 자식 프로그램이 바뀐 뒤 발생한 실패는 이번 parser가 명시적으로 지원하지 않는 범위인데, 출력 순서만 바뀌면 확정적인 근거로 승격된다.

[독립 반례](evidence/2026-11-17-probe-deferred-child-context.py)는 실제 `parse_trace()`를 호출한다. 세 사례는 아래와 같다.

| 순서 | 현재 결과 | 필요한 결과 |
| --- | --- | --- |
| 부모 반환 → 자식 exec → mount 거부 | inconclusive | 유지 |
| 자식 exec → mount 거부 → 부모 반환 | next-blocked, issues 없음 | inconclusive |
| 자식 mount 거부 → 부모 반환, exec 없음 | next-blocked | 지원 의미 유지 |

이 문제는 지원하는 unfinished/resumed 순서와 명시적 미지원 문맥의 교차점이다. 임의의 strace 전체 문법을 추가하라는 요구가 아니다. 같은 방식으로 `children` 등록 여부에 의존하는 unsupported-child-mount 검사도 지연 연결 시 대칭적으로 적용해야 한다. 작은 bounded 문맥 기록을 보존해 자식 PID를 확정할 때 검증하거나, 문맥을 확인할 수 없으면 명시적으로 inconclusive로 남기는 국소 보완이 적절하다.

실제 고정 후보 trace에는 이 반례의 자식 exec 전환이 없다. 따라서 이미 확인한 **clone41→42/43→44 후 각 자식의 mount EPERM**이라는 실제 관찰은 유지한다. 문제는 새 순수 parser가 지원한다고 한 입력 범위에서의 판정 정확성이다.

## 확인한 구현과 검증

- 동결 runtime parser/verifier와 별도의 명시적 오프라인 진입점이다. 기존 원문·index·자동 inconclusive는 유지됐고 VM/container/runtime/정책/인증/model 실행은0회다.
- 실제 원래 trace는 clone-still-denied, 후보는 first-clone-passed-next-blocked로 재현했다. 후보64–65/132행의 clone과110/178행의 자식 mount,55/123행의 역할 근거가 원문과 연결된다. payloadStarted/lsmCauseConfirmed는 false다.
- 새 CLI로 출력한 JSON은 저장 derived.json과 **tool.checkoutHead를 제외하고 일치**했다. 기존 산출물은 구현 commit695d7f1에서, 독립 재현은 문서 포함 head8bba520에서 실행했기 때문에 checkout 식별자가 다르다. 이를 byte-identical로 표현하지 않는다.
- 입력16MiB·행/보류/관찰/오류 개수 상한, 정확한 flags·attach/반환 일치 검사, 원문 근거 보존, 과거 출력 경로와 덮어쓰기 거부를 확인했다. 한 번의 행 순회와 bounded 상태를 유지한다. 다만 위 R18 때문에 “미지원 자식 문맥을 모든 출력 순서에서 거부한다”는 주장은 아직 성립하지 않는다.
- 검토 head에서 `pnpm check` **304개**·타입·예제 build와 Python execution-lifecycle **183**, 공유 lifecycle **16**, 감사 **44**, 총 **243개**가 통과했다. 새35개 회귀에 지연된 자식 exec 사례는 없었다. 과거4개 verifier도 통과하며 policy-pair의 옛 자동 inconclusive를 그대로 재현했다.
- 새 index 대상 **14파일**을 hash/크기로 확인했다. 기준 main의3,674파일 중 기존 변경은 문서3개뿐이고 과거 verification **2,364파일** 및 동결 parser/verifier는 불변이다. 실행 구현은 새 trace_reanalysis.py·test_trace_reanalysis.py다.

[독립 요약 JSON](evidence/2026-11-17-s2-trace-reanalysis-independent.json)에 검사와 반례를 남겼다. 원문/실행 구현을 수정하지 않았으며 새 runtime이나 권한 변경도 하지 않았다. TS/FCA/평가 의미 불변으로 pnpm experiment·Vendure 평가를 반복하지 않았다.

## 범위와 다음 작업

최초 명령의 시계 기록을 다시 놓친 것은 절차상 미준수다. 보고서가 두 번째 명령의 실제 계측과60초 가산 가정을 구분한 점은 적절하지만, 그 가산을 실제 최초 시각의 측정값으로 취급하지 않는다. 새 runtime0·계측 후 약773초라는 범위에서 별도 병합 차단으로 확대하지 않으며 다음 첫 명령은 시계와 상태를 함께 기록하도록 한다.

[R18 국소 보완 지시](2026-11-17-s2-trace-context-fix-instructions.md)를 함께 제공한다. **30분 상한·오프라인만·새 VM/정책0**이며 공통 runtime이나 실행 경계의 설계 변경은 필요 없다. 기존 산출물을 보존하고 새 도구/파생 결과로 재검증한다. 보완 결과 리뷰 전 PR #63은 미병합으로 둔다.

외부 컨테이너/VM과 내부 CLI sandbox의 책임 분담 논의는 이 작은 parser 수정과 별도로 진행할 수 있다. 추가 mount/권한·실제 인증/model·본 비교를 자동 재개하지 않는다. R11 unresolved·production/live 거부·fixtureOnly=true·validSubmission=false·trialAuthorized/readyForTrial=false·results=null과 H-O/H-F 미검증을 유지한다.
