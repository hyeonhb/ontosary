# S2 저장 trace 오프라인 판독 보완

2026-11-17. [보완 지시](2026-11-17-s2-trace-reanalysis-instructions.md)에 따라 **별도 오프라인 판독을 구현·검증했다.** 봉인된 후보 trace의 새 파생 판정은 `first-clone-passed-next-blocked`다. 과거 자동 판정 `inconclusive`, 원문 archive/index, 이전 보고서와 runtime parser/verifier는 그대로다. 새 VM/container/runtime·정책 변경·credential/provider/model·본 비교 실행은 모두0회다. 독립 결과 리뷰를 기다리며 이번 PR은 병합하지 않는다.

기준은 PR #61 병합 `ee7ac98` 이후 최신 main **`e358104`**다. 사용자 변경 없는 checkout을 확인하고 `codex/s2-trace-reanalysis`를 만들었다. 최종 구현·검증 head는 **`695d7f1a9fdbce9fc371fd322d4357846182e989`**이며 이후 커밋은 이 보고서·별도 파생 증거·맥락 문서만 추가한다. 최종 게시 head와 Git 게시 시간은 PR 본문에 별도로 기록한다.

## 판독 결과와 근거

[별도 파생 JSON](../../experiments/domain-model/s2/verification/2026-11-17-trace-reanalysis/derived.json)은 기존 전체 index·snapshot·archive와 공통 unit 봉인/회수를 확인한 뒤 archive 안의 `result/auxiliary/result.json`에서 trace를 읽는다. 원문 후보의 SHA-256은 `9a949992b23a81361f821d9ec6fd227eebcd4a6a1c1cf8801ee698660e117c5c`, 기존 index의 SHA-256은 `ec03d00e8026ea107691b10eee8a9ffe65e68f9b41350c8d0a48d91d8cdf9869`다. JSON에 archive·member·result hash, 이전/새 판정, 판독 도구 hash/commit과 기존 판독 의존 파일 hash를 함께 기록했다.

| 저장 입력 | 과거 자동 판정 | 새 파생 판정 | 원문 근거(1기반) |
| --- | --- | --- | --- |
| 원래 정책 | clone-still-denied | clone-still-denied | PID42/43 clone, 67/85행, 각각 EPERM |
| 후보 정책 | inconclusive | first-clone-passed-next-blocked | precheck41→42 clone 64–65행, child42 mount110행; command preparation43→44 clone132행, child44 mount178행 |

후보의 bwrap exec는55/123행이다. 각 exec·clone 시작·반환·mount 관찰에 원문 줄 번호와 정확한 문자열을 보존했다.64행의 정확한 `/usr/bin/strace: Process 42 attached`와 바로 다음65행의 `) = 42`만 연결했고, 연결한 두 줄·안내문·PID/반환 일치 이유를 별도 `joins`에 남겼다. 줄 번호는 입력에서 계산하며 앞에 진단 행을 추가하면 근거 위치도 이동하는 회귀를 통과했다.

`payloadStarted=false`, `lsmCauseConfirmed=false`다. mount의 `EPERM`은 syscall 관찰이며 seccomp·AppArmor·다른 kernel 검사의 정확한 기여를 확정하지 않는다. 두 번째 bwrap argv는 원래 strace에서 축약되어 있다. precheck의 `/usr/bin/true` 포함 여부로 역할을 나누는 기존 관례와 argv 축약 여부를 출력에 명시했고, 명령 준비 관찰을 payload exec의 증명으로 확대하지 않는다.

## 구현과 지원 경계

새 [trace_reanalysis.py](../../experiments/domain-model/s2/trial/container/execution-lifecycle/trace_reanalysis.py)는 명시적으로 실행하는 오프라인 진입점이다. 기존 `policy_pair.trace_observation()`·`verify_pair.py`·공통 runtime 호출 경로를 수정하지 않았다. 기존 verifier가 보존된 `candidate-trace-analysis.json`과 `pair-complete.json`을 이전 판정 그대로 대조한다. 새 파일은 과거 index에 편입하지 않았고 기존 증거 디렉터리로의 출력과 기존 출력 덮어쓰기를 거부한다. 도구가 커밋된 바이트와 일치해야 파생 결과를 게시한다.

지원하는 형식은 PID가 있는 단일 줄 clone, 같은 PID의 unfinished/resumed, 정확한 attach 안내가 끼어든 clone 시작 줄과 바로 다음 PID 없는 반환 줄이다. namespace flags는 전체 문자열이 정확히 일치해야 한다. 추가·재배열 flags, clone3, 다른 부모/PID·자식 반환 불일치, 중간 출력, 중복 pending/반환/자식, orphan 완료, 잘린 행·미완료 호출은 `inconclusive`와 이유를 남긴다. 줄 분할된 bwrap exec/자식 mount, 자식 exec 이후의 실패 귀속, 일반 strace 문법은 이번 지원 범위 밖이다. 관련 없는 startup/thread syscall은 namespace 증거로 사용하지 않는다.

행 판독은 한 번의 순방향 순회다. UTF-8 길이/hash도 제한된 조각으로 확인하며 전체 trace를 복제한 파생 문자열·행 배열을 만들지 않는다. PID별 pending은32개, pending 원문은각4KiB, 물리 행은64KiB, trace는16MiB, 관찰은256개, 이유는64개 상한이다. 입력·반환할 근거를 제외한 pending 상태는 미완료 호출 수에 비례하고, 관찰/역할/PID 연결도 별도 상한을 둔다. 시간은 입력 길이에 선형이며 무제한 줄 결합이나 전역 `strace:` 삭제를 하지 않는다.

unfinished 호출은 다른 PID의 출력과 섞여도 같은 부모의 resumed 반환에만 연결한다. 자식 mount가 부모의 resumed 반환보다 먼저 출력되는 경우도 clone 시작 이후의 줄인지 확인해 연결한다. 다른 PID 또는 clone 이전의 mount 실패는 해당 자식 실패로 합치지 않는다. 두 역할 모두 자식 거부 근거가 있어야 새 next-blocked 판정을 내린다. 합성 payload 완료는 flag·stdout marker·exit0와 충돌하는 자식 거부가 없는 경우에 한해 기존 의미를 유지한다.

## 검증

[검증 JSON과 원시 로그](../../experiments/domain-model/s2/verification/2026-11-17-trace-reanalysis/validation.json)에 실행 명령과 결과를 기록했다.

- `pnpm check`: **304개 통과, skip0**, 타입 검사·예제 production build 통과.
- 기존 Python **208개**: execution-lifecycle148·공유 lifecycle16·감사/deadline/package44. 새 판독 **35개**를 더해 **243개, skip0**다. execution-lifecycle 전체183과 별도 새35 실행은 중복 집계하지 않았다.
- 실제 후보/원래 trace, 단일 줄·unfinished/resumed·합성 payload 완료, attach/부모/반환 불일치·서로 다른 부모 interleaving·orphan·중복·추가 flags·truncation·다른 PID mount·각 상한·UTF-8 byte 길이·원문 근거 이동·archive 변조/후보 hash 거부를 검사했다.
- 기존4개 verifier:11-14는1시도/start0·결과 억제,11-15는1시도/통과0·guest 증거 없음,11-17 seal/recovery는7/7, policy pair는2개 봉인과 **기존 status=inconclusive**를 각각 재현했다. verifier 통과는 과거 실패를 성공으로 바꾼다는 뜻이 아니다.
- 기존 파일·모든 과거 verification 자료·동결 parser/verifier 불변과 새 JSON의 원문 근거를 확인했다. [불변 대조](../../experiments/domain-model/s2/verification/2026-11-17-trace-reanalysis/immutability.json), [별도 목록](../../experiments/domain-model/s2/verification/2026-11-17-trace-reanalysis/index.json)을 참조한다.

TS/FCA/평가 입력·의미는 불변이므로 `pnpm experiment`와 Vendure 전체 평가는 반복하지 않았다. 추가 의존성은 없다. 이 검증은 저장 자료와 합성 문자열의 오프라인 재분석이며 실제 정책 회차의 재실행이 아니다.

저장소 루트에서 별도 경로로 재현한다. 출력이 이미 있으면 새 경로를 선택한다.

```sh
python3 experiments/domain-model/s2/trial/container/execution-lifecycle/trace_reanalysis.py \
  --output work/s2-trace-reanalysis-replay.json
python3 -m unittest discover \
  -s experiments/domain-model/s2/trial/container/execution-lifecycle \
  -p 'test_trace_reanalysis.py' -v
```

## 시간·비용과 인계

[회차 기록](../../experiments/domain-model/s2/verification/2026-11-17-trace-reanalysis/round.json)에 UTC/monotonic·허용 목록·기준 head·20/30분 마감·실제 종료를 남겼다. 최초 명령에서 clock을 함께 기록하라는 요구는 놓쳤다. 최초 명령은 git 상태/문서 읽기였고, **두 번째 명령의 `2026-11-17T11:08:28.521090+00:00`, monotonic229669.873943291**을 최초 계측값으로 보존한다. 실제 최초 시각으로 소급 주장하지 않으며 예산 계산은 이 값보다60초 앞선 보수적 기준을 사용했다. 구현은 그 기준642.508초 시점에 동결했으며20분 탐색 상한 안이다. 전체 읽기·구현·검증·보고는30분 상한 안에 종료했다. 정확한 종료·경과는 round.json, 이후 Git 게시는 PR 본문에 분리한다.

VM/container/runtime/정책 적용·유료 실험 호출은0이다. 실제 mount 허용·추가 권한·CLI 설정/실행 경계 변경·실제 credential/provider/model·본 비교는 진행하지 않았다. **R11 unresolved**, R12 기존 범위, production/live 거부, `fixtureOnly=true`, `validSubmission=false`, `trialAuthorized=false`, `readyForTrial=false`, `results=null`을 유지한다. 다음은 보완 결과 리뷰와 별도 실행 경계 설계 논의이며 새 판독 완료가 실제 실행 승인이나 H-O/H-F의 검증을 대신하지 않는다.
