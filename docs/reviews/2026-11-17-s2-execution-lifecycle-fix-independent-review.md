# S2 실행 수명주기 보완 독립 리뷰

2026-11-17. [PR #54](https://github.com/hyeonhb/ontosary/pull/54)의 `ff7ec19ebc7e3e12380fb82cc6a377d5aaf4dd6c`와 [11월 15일 인계](https://github.com/hyeonhb/ontosary/blob/ff7ec19/docs/reviews/2026-11-15-s2-execution-lifecycle-fix.md)를 검토했다. **R14는 이번 이미지 재사용 범위에서 해결됐다. R13·R15는 부분 완료이며, PR #54 병합과 다음 정책/실제 agent 단계 진행은 보류한다.** 보고서가 정상 종료 코드와 전체 실행 완료를 구분하고 증거 유실을 명시한 판정에 동의한다.

## 항목별 판단

| 항목 | 판단과 근거 |
| --- | --- |
| R13 고정 PATH | env 전달과 알려진 hook 배열만 허용하는 구현·부정 회귀는 확인했다. frozen helper의 Spec gate 뒤 실제 start 1회가 기록돼 이전 시작 전 차단에서 진전했다. 그러나 실제 native Spec·도구 해석 상세·전체 diff가 유실돼 독립 재대조가 불가능하다. 부분 완료다. |
| R14 이미지 재사용 | 빌드 전 입력 key 조회, 출력 digest/identity 검증, 옛 manifest를 보존한 연결 기록, 실제 prepare 진입점의 별도 회차 miss→hit를 확인했다. 새 VM에서 다운로드/build/save 0회·import 1회와 actual target/config/chain이 보존됐다. 해당 범위 해결이다. 외부 apt/npm 조회까지 고정한 재빌드 재현성은 주장하지 않는다. |
| R15 수집과 export | 원본 run tree 재수집은 제거했고 FD 읽기·hardlink/특수 파일 거부·사전 상한·수집 실패/철회 결과의 미포함을 검증했다. 다만 준비 metadata 소유권과 export의 실패 진단 보존이 연결되지 않아 실제 archive가 0개다. 아래 보완이 남았다. |

## R15 잔여 Medium 전달 metadata와 진단 보존을 연결해야 한다

위치: [round.py 89–94행](https://github.com/hyeonhb/ontosary/blob/ff7ec19/experiments/domain-model/s2/trial/container/execution-lifecycle/round.py#L89), [exporter.py 60–63행](https://github.com/hyeonhb/ontosary/blob/ff7ec19/experiments/domain-model/s2/trial/container/execution-lifecycle/exporter.py#L60).

호스트의 `image-export.json`을 Lima 사용자로 copy한 뒤 sudo `mv`한다. 이 흐름은 전달 파일을 관리자 소유 파일로 재작성하지 않지만 export는 관리자 UID를 요구한다. 저장 traceback의 `file-owner:image-export.json`과 실제 명령 순서가 일치한다. 보고서의 원인 분석을 지지하며 실제 숫자 UID는 남아 있지 않다.

준비 단계에서 내용/hash/입력 연결을 검증한 후 관리자 소유·허용 mode로 원자 게시하고 그 결과를 확인해야 한다. export의 소유권 검사를 완화해 해결하지 않는다. 준비→import→export 회귀에는 동일 테스트 사용자로 만든 파일만 쓰지 말고 전달 파일과 관리자 파일의 소유권 차이를 반영해야 한다.

또한 현재는 마지막 전역 metadata 하나가 거부되면 앞서 수집한 정상 관리자 진단도 모두 staging과 함께 폐기된다. 이번에는 원본 Spec과 service 조회가 함께 사라져 다음 진단의 근거를 잃었다. 정상 결과 포장의 원자성은 유지하되, 거부 파일을 포함하지 않는 **실패 진단 산출물**을 별도 상태/manifest로 보존해야 한다. 각 파일의 엄격한 읽기 검증과 상한을 유지하고, 진단 실패를 성공 결과로 표현하지 않는다. 이 부분은 직전 지시의 실패 진단 보존 조건도 아직 충족하지 못한다.

## R16 Medium service 종료 증거의 수명이 관찰보다 짧을 수 있다

위치: [engine.py 225–231행](https://github.com/hyeonhb/ontosary/blob/ff7ec19/experiments/domain-model/s2/trial/container/execution-lifecycle/engine.py#L225), [fixture_runtime_cli.py 31행](https://github.com/hyeonhb/ontosary/blob/ff7ec19/experiments/domain-model/s2/trial/container/execution-lifecycle/fixture_runtime_cli.py#L31).

정상 단위는 exit 0·종료/삭제 확인·collection 뒤 `seal:inactive-deadline-unconfirmed`로 결과가 철회됐다. 실제 기록은 등록 후 삭제 1.566초이며 마감까지 기다리다 timeout 난 사례가 아니다. `seal()`은 비활성 상태의 `InactiveEnterTimestampMonotonic`이 0/누락 또는 마감 밖이면 거부한다. 현재 코드에는 그 값이 사라지기 전에 unit 상태를 유지하거나 신뢰할 종료 이벤트를 보존하는 연결이 없다. 로컬 runtime 대역은 show 때마다 현재 시각을 양수로 만들어 이 조건을 항상 만족시킨다.

systemd v260의 기본 `CollectMode=inactive`는 참조 없는 inactive unit을 unload할 수 있고, unload 때 실행 상태가 사라진다. unit 파일이 남아 있는 것만으로 실행 상태가 보존되지는 않는다. 따라서 **GC/조회 시점은 우선 검증할 구체적 가설**이다. 실제 show 원문이 없으므로 이번 실패의 정확한 값이나 GC를 확정 원인으로 보고하지 않는다. [systemd v260 공식 문서](https://github.com/systemd/systemd/blob/v260/man/systemd.unit.xml#L512).

다음 수정 전 종료 증거를 안정적으로 확보할 방법을 정해야 한다. 예를 들어 검증 완료까지 unit reference를 유지하거나 신뢰할 종료 이벤트를 먼저 보존하는 방법을 검토할 수 있다. polling 간격 축소, 0을 현재 시각으로 대체, worker exit/빈 cgroup/VM 삭제만으로 봉인하는 방식은 해결이 아니다. inactive/failed/unloaded·누락/0/마감 초과·늦은 관찰을 구분하고 원시 조회를 실패 진단에도 남겨야 한다. 이 문제는 이번에 새로 변경된 줄의 회귀가 아니라 PR #54의 공통 수명주기가 실제 정상 경로에 도달하면서 드러난 미완료다.

## R17 Medium 증거 회수 예외가 VM 정리를 건너뛴다

위치: [round.py 169–175행](https://github.com/hyeonhb/ontosary/blob/ff7ec19/experiments/domain-model/s2/trial/container/execution-lifecycle/round.py#L169).

`cleanup()`에서 guest export와 성공 archive/index의 호스트 copy를 VM stop/delete보다 먼저 실행한다. copy는 기본 `check=True`이며 예외를 분리 처리하는 finally 경로가 없다. 따라서 export 성공 뒤 archive copy가 실패하면 VM 종료·삭제와 cleanup 기록에 도달하지 않는다. export 호출 자체의 transport 예외도 같은 결과다. guest export의 비정상 exit를 `check=False`로 받는 것만으로 전체 실패 경로가 처리되지는 않는다.

실제 `Round.cleanup()`에 외부 명령만 가짜로 연결한 [독립 재현](evidence/2026-11-17-probe-cleanup.py)에서 두 오류 모두 stop/delete 0회·소유 root 잔존·cleanup 기록 없음이었다. 실제 VM은 생성하지 않았다. 이번 저장 회차는 export가 비정상 exit를 반환해 이후 VM 정리가 실행됐으므로 **이번에 VM이 남았다는 주장은 아니다.** 미검증 transport/copy 실패 경로의 구현 결함이다.

증거 회수의 성공/실패와 자원 정리의 최종 책임을 분리해야 한다. 회수 오류를 기록한 뒤에도 소유 VM stop/delete/부재 확인을 시도하고, 정리 자체가 실패하면 잔여와 원인을 별도 기록한다. 자원 삭제 전에 진단 회수는 유한 시간만 사용하고 정리 reserve를 소진하지 않게 한다. export 비정상 exit·호출 예외·archive/index copy 실패·stop/delete 실패를 실제 cleanup 진입점에서 확인해야 한다.

## 독립 검증과 한계

- 검토 head에서 `pnpm check` 304개(skip 0)·타입·예제 build, Python execution-lifecycle 86/공유 lifecycle 16/감사 44, 총 146개를 통과했다.
- 새 저장 verifier는 123파일·분석 5/closing 4와 실제 1시도/0통과/guest archive 없음 판정을 재현했다. 과거 verifier도 126파일·분석 8/closing 4와 이전 PATH 없는 Spec 차이를 재현했다. 새 verifier 통과는 유실된 새 native Spec의 대조가 아니다.
- final-source 73파일은 검토 head와 같고, 전달 archive 32파일의 hash를 확인했다. 전달본과 현재 도구의 차이는 보고된 오프라인 `verify_fix.py` 한 곳이다. 최초 3,090파일 중 3,078파일 불변·허용 변경12개, 예상 밖 변경0을 확인했다.
- 실제 보관 중인 공개 준비물4개의 바이트/크기/SHA-256을 다시 읽어 대조했고 새 image key 연결 기록도 보존된 binding과 같았다. 실제 준비 기록은 환경 진입부터52.764초, 다운로드/build/save0·새 VM/import1이다.
- 호스트에 남은 state에서 start1·exit0·종료/삭제 true·pending false·collection suppressed·discardVM true를 확인했다. 전체7단위 통과, 새 raw Spec/도구 상세/worker 파일의 독립 검증은 할 수 없다. 다음6단위와 정책 pair는 미실행이다.
- 새 VM/정책/인증/모델 실행은 하지 않았다. 리뷰 중 구현 수정도 없다. 검증 요약은 [별도 JSON](evidence/2026-11-17-s2-lifecycle-fix-independent.json)에 남겼다.

## 방향과 다음 판단

현재 경계를 교체하거나 권한을 확대할 근거는 없다. 이미지 재사용으로 반복 준비 비용은 실제로 줄었고, 차단은 관리자 상태의 수명·전달 파일의 소유권·회수 실패 시 정리라는 운영 코드의 연결에서 발생했다. 테스트 수 증가보다 준비→전달→봉인→진단 회수→정리의 연결 회귀가 우선이다.

다음은 R15 잔여와 R16/R17의 작은 구조를 먼저 정하고 보완하는 순서가 적절하다. 실패 시에도 진단이 남는 경로를 먼저 갖춘 뒤 같은 기본 정책에서 정상 봉인과 나머지 실패 단위를 검증한다. 이번 리뷰가 새 실행 예산이나 정책 대조 재개를 승인하지는 않는다. PR #54는 미병합, R11 unresolved·R12 기존 범위·production/live 차단과 실제 credential/model/본 비교 보류를 유지한다. H-O/H-F 제품 가설은 여전히 미검증이다.

독립 재현 스크립트는 검토 head `ff7ec19`의 checkout 루트에서 실행한다. 임시 디렉터리와 가짜 외부 명령만 사용하며 main에 아직 없는 실행기를 배포하거나 VM을 만드는 명령이 아니다.
