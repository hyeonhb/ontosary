# S2 지연된 자식 문맥 판독 보완

2026-11-17. [R18 보완 지시](2026-11-17-s2-trace-context-fix-instructions.md)에 따라 **부모 clone 반환보다 먼저 출력된 자식 문맥의 누락을 수정하고 로컬 검증을 마쳤다.** 자식 exec/미지원 mount가 반환 전·후 어느 순서에 나오든 `inconclusive`이며, 지원하던 정상 child-denial-before-resume은 유지한다. 실제 저장 원래/후보 판정도 그대로다. PR #63은 보완 결과의 독립 리뷰 전 병합하지 않는다.

기준 head는 `8bba520a8fe91355d367642eebf2f8218133cf83`이고 기존 `codex/s2-trace-reanalysis` 브랜치를 이어 사용했다. 최신 main `35dbc3d`의 리뷰/지시를 merge `e68064f`로 통합했다. PROGRESS/REVIEW_CONTEXT의 앞부분 충돌은 새 독립 리뷰와 이전 구현 기록을 모두 보존해 해결했다. 최종 구현 head는 **`26c8b41cf27badd05f1bc6d84358fa465b82c384`**이며 이후 변경은 보고/증거/맥락 문서다. 최종 게시 head·Git 게시 시간은 PR 본문에 별도로 기록한다.

## 반례와 수정

기준 head에서 [독립 반례](evidence/2026-11-17-probe-deferred-child-context.py)를 그대로 실행해 결함을 재현했다. 그 스크립트와 기존 assertion은 수정하지 않았다. [수정 전 원시 입력/결과](../../experiments/domain-model/s2/verification/2026-11-17-trace-context-fix/before.json)를 보존하고, 수정 후에는 같은 저장 trace를 실제 `parse_trace()`에 전달해 [새 결과](../../experiments/domain-model/s2/verification/2026-11-17-trace-context-fix/after.json)를 기록했다.

| 같은 사건의 출력 순서 | 수정 전 | 수정 후 |
| --- | --- | --- |
| 부모 반환 → 자식 exec → mount 거부 | inconclusive | inconclusive |
| 자식 exec → mount 거부 → 부모 반환 | first-clone-passed-next-blocked, issues 없음 | inconclusive, exec 원문 위치·이유 포함 |
| 자식 mount 거부 → 부모 반환, exec 없음 | first-clone-passed-next-blocked | 동일 |

먼저 새 회귀9개를 추가해 기존35개와 함께44개를 실행했고 실패6건(하위 사례 포함)을 확인했다. 이후 문맥 상한·중복·거부 근거 분리 검사를 더해 새 회귀는14개다. 최종 순서 대조는 exec/mount 사건을 그대로 두고 부모의 반환 위치만 그 앞/뒤로 옮긴다. split/resumed mount·미지원 성공 mount도 두 순서에서 같은 보수적 거부를 확인한다.

변경은 [trace_reanalysis.py](../../experiments/domain-model/s2/trial/container/execution-lifecycle/trace_reanalysis.py)의 문맥 보존/근거 승인과 해당 회귀에 한정했다. namespace clone이 pending이거나 PID가 이미 자식으로 확정됐을 때, **exec와 미지원 mount 두 종류**의 문맥만 PID·이유·원문 위치와 함께 보존한다. 최종 판정 전에 반환 PID와 clone 시작 위치를 사용해 이 작은 목록을 한 번 확인한다. 즉시/지연 순서 모두 같은 포착·검사 경로를 거친다.

해당 자식의 clone 시작 이후에 미지원 문맥이 있으면 위치와 이유를 `childContext`/`issues`에 기록하고 그 자식의 거부는 `nextDenied`에서 제외한다. 원시 거부는 `contextRejectedDenied`에 남기므로 누락과 부적격 근거를 구분한다. 무관 PID 또는 clone 시작 이전의 이벤트는 자식 문맥으로 편입하지 않는다. 부모 둘의 interleaving·반환 순서 역전·다른 부모가 먼저 끝나는 순서에서도 문맥을 지우거나 교차 연결하지 않는다. 중복 문맥은 명시적 이유를 더하고 확정 판정에 사용하지 않는다.

추가 문맥은 **128개·원문 합계64KiB**로 제한한다. 상한 때문에 필요한 사건을 저장하지 못하면 `contextComplete=false`, `child-context-limit`와 원문 줄 위치를 남기고 자식 거부를 확정 근거로 승인하지 않는다. 저장 개수/바이트와 한도도 출력한다. 정확히 상한만큼 저장되고 손실이 없는 경우와 초과해 문맥이 누락된 경우를 구분해 검사했다. 기존16MiB 입력·64KiB 행·32개 pending/각4KiB·256개 관찰·64개 오류 한도는 불변이다. 입력은 한 번 순방향으로 읽고 추가 확인은 최대128개 문맥에만 수행하므로 O(n)이며 모든 PID의 무제한 사건 목록이나 일반 프로세스 수명 추적기를 도입하지 않았다.

## 실제 저장 trace와 과거 자료

[새 파생 출력](../../experiments/domain-model/s2/verification/2026-11-17-trace-context-fix/derived.json)은 기존 전체 index·archive·봉인/회수 검증을 거쳐 별도 디렉터리에 생성했다. [전후 연결](../../experiments/domain-model/s2/verification/2026-11-17-trace-context-fix/comparison.json)에 첫 파생 출력/index의 hash·당시 도구 commit/hash, 새 도구 commit/hash·입력 hash와 R18 변경 이유를 연결했다.

실제 원래 trace는 **clone-still-denied**, 후보는 **first-clone-passed-next-blocked**다. 후보 precheck41→42의64–65행, command preparation43→44의132행, 자식 mount110/178행 및 exec55/123행의 원문 연결은 첫 파생 결과와 같다. `payloadStarted=false`, `lsmCauseConfirmed=false`이며 EPERM의 정확한 seccomp/AppArmor 원인을 확정하지 않는다. 추가 문맥 필드와 도구 식별자가 있으므로 첫 파생 JSON과 전체 byte-identical이라고 표현하지 않는다.

과거 `policy_pair.py`·`verify_pair.py`·나머지 저장 verifier, runtime/수명주기/정책/cache, 원시 archive/index, 첫 `derived.json`과 도구 hash/index, 이전 보고서는 그대로다. [불변 대조](../../experiments/domain-model/s2/verification/2026-11-17-trace-context-fix/immutability.json)와 [새 증거 목록](../../experiments/domain-model/s2/verification/2026-11-17-trace-context-fix/index.json)을 남긴다. 과거 index에 새 산출물을 편입하지 않았다.

## 검사·시간·인계

[검증 기록](../../experiments/domain-model/s2/verification/2026-11-17-trace-context-fix/validation.json)과 같은 디렉터리의 원시 로그를 참조한다.

- `pnpm check`:304개·skip0·타입 검사·예제 production build 통과.
- Python: 기존243개+새14개=**257개**, skip0. execution-lifecycle197(기존 trace35+새14 포함)·공유 lifecycle16·감사44다.
- 과거4개 verifier 모두 통과하며11-14/11-15의 실패·부분 결과,11-17 seal/recovery의7/7, 옛 pair 자동 **inconclusive**를 그대로 재현했다.
- 반례 전후와 실제 저장 판정·원문 근거, 문맥 순서/상한/중복/다른 PID/clone 이전 사건, 첫 파생 결과와 모든 과거 원시 자료 불변을 확인했다.

TS/FCA/평가 의미는 불변이라 `pnpm experiment`·Vendure 전체 평가는 반복하지 않았다. 새 의존성은 없고 새 VM/container/runtime·정책 적용·유료 실험·실제 credential/provider/model·본 비교는 모두0회다.

[회차 기록](../../experiments/domain-model/s2/verification/2026-11-17-trace-context-fix/round.json)의 최초 UTC는 `2026-11-17T11:49:51.604133+00:00`, host monotonic은 `231190.526571166`이다. 첫 명령에서 두 시계와 git 브랜치/변경 상태를 함께 기록했다. 전체 head SHA 조회는 바로 다음 명령에서 수행했으며 그 사이 변경은 없었다. 구현은20분 탐색 마감 전에 동결했고 읽기·재현·구현·검사·보고는30분 안에 마쳤다. 실제 종료와 경과를 round.json에 기록하며 이후 Git 게시 시간은 별도다.

다음은 R18 보완 결과의 독립 리뷰다. 지원 밖 문법은 여전히 보수적으로 거부하며 완전한 strace 판독이나 실제 격리 경계 해결을 주장하지 않는다. **R11 unresolved**, R12 기존 범위, production/live 거부, `fixtureOnly=true`, `validSubmission=false`, `trialAuthorized=false`, `readyForTrial=false`, `results=null`, H-O/H-F 미검증을 유지한다. mount 허용·CLI 설정/실행 경계·인증/model·본 비교는 별도 결정이다.
