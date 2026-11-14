# S2 공통 실행 수명주기 독립 리뷰

2026-11-14. 검토 대상은 [PR #54](https://github.com/hyeonhb/ontosary/pull/54)의 `f6fc386`과 [개발 인계](https://github.com/hyeonhb/ontosary/blob/f6fc386/docs/reviews/2026-11-14-s2-execution-lifecycle.md)다. **부분 완료·blocked/inconclusive라는 판정은 타당하다. 다만 R13/R14/R15를 보완하기 전 구현 완료나 실제 7단위 재개를 승인하지 않는다.** 이 리뷰는 코드 수정/새 VM/정책 시험이 아니며 PR #54도 병합하지 않았다.

별도 요청한 Vendure 임시 cache 복구는 완료했다. [복구 기록](evidence/2026-11-14-vendure-cache-recovery.json)에 따라 고정 검증 입력만 6,106파일·84,396,041바이트 복원했고 전체 설치/스크립트 실행/기존 파일 덮어쓰기는 없었다. 원본 4,735항목·Program 1,638파일·진단0을 확인한 뒤 PR #53을 `60d5f4f`로 병합했다. 이는 전체 Vendure 실행 환경 복원이나 새 lifecycle의 검증 완료를 뜻하지 않는다.

## 확인한 결과

- PR #54 head에서도 `pnpm check` 304개(skip0), 타입 검사, 예제 build가 통과했다. 보고서의 당시 300통과/4실패는 과거 사실로 보존하되 현재 cache 차단은 해소됐다.
- 새 Python56·공유 lifecycle16·감사/deadline/package44, 합계116개가 통과했다. 저장 증거 verifier도 126파일·분석8/closing4, 전체 Spec 차이와 종료 순서를 재현했다.
- final-source archive 65파일이 검토 head와 일치했다. 최초 inventory 2,945파일 중 변경17개는 명시한 수정 범위 안이며 예상 밖 변경은 없었다. 전달 helper20개·입력 archive27파일·게스트28파일의 연결도 재검증했다.
- 의도적으로 보관한 공개 준비물4개의 실제 바이트/hash/크기가 manifest와 일치했다. 다운로드3종의 재조회는 확인됐으며 이미지 아카이브도 등록·검증·import됐다. 회차 간 이미지 빌드 생략은 아래 R14 때문에 별도 미완료다.
- 실제 필수7단위 중 시도1·기대 결과 통과0, start0이다. created Spec의 AppArmor 누락과 세 mount의 rro→ro를 감지해 시작을 거부했다. 등록 후 삭제0.854초·단위 봉인1.236초, pending false, task/container 부재, 결과 suppressed·다음 실행 차단이 원시 기록과 일치한다. 나머지 실패 경로를 통과했다고 확대하지 않은 점은 적절하다.

## R13 High runtime PATH 제거가 보안 기능 탐지를 깨뜨린다

위치: [identity.py 4–5행](https://github.com/hyeonhb/ontosary/blob/f6fc386/experiments/domain-model/s2/trial/container/execution-lifecycle/identity.py#L4), [engine.py 15–19행](https://github.com/hyeonhb/ontosary/blob/f6fc386/experiments/domain-model/s2/trial/container/execution-lifecycle/engine.py#L15).

runtime 환경을 HOME/LANG으로만 제한하고 nerdctl 본체를 절대 경로로 호출한다. 하지만 nerdctl이 내부에서 찾는 도구의 경로까지 해결되지는 않는다. 고정 v2.4.2는 AppArmor 탐지에서 `exec.LookPath("apparmor_parser")`와 `aa-exec`를 사용하고, 재귀 읽기 전용 지원 탐지에서 `exec.LookPath("runc")` 뒤 `runc features`를 호출한다. PATH가 없는 환경에서는 이 탐지가 실패한다. rro 탐지 실패 시 일반 ro로 내려가는 구현도 확인했다. [AppArmor 탐지](https://github.com/containerd/nerdctl/blob/v2.4.2/pkg/apparmorutil/apparmorutil_linux.go), [runtime 경로 탐지](https://github.com/containerd/nerdctl/blob/v2.4.2/pkg/ociruntimeutil/ociruntimeutil.go), [mount 처리](https://github.com/containerd/nerdctl/blob/v2.4.2/pkg/mountutil/mountutil_linux.go).

따라서 이번 관찰은 단순한 새 권한 차단으로 볼 수 없다. 환경 변경이 기존 보안 설정 생성에 영향을 주는 구체적인 코드 경로가 확인됐고 실제 Spec 차이와도 일치한다. PATH를 복원한 실제 대조는 수행하지 않았으므로 이 수정만으로 전체 실행이 통과한다고 주장하지 않는다.

권고: 필요한 시스템 도구를 찾을 수 있는 고정 PATH와 제한된 환경을 사용한다. nerdctl이 hook에 PATH를 추가하는 [고정 구현](https://github.com/containerd/nerdctl/blob/v2.4.2/pkg/cmd/container/create.go#L642)을 계약에 반영하되 임의 중복 env를 허용하지 않는다. 예를 들어 정확한 위치·개수·값을 검증한 알려진 PATH 추가만 처리하고 나머지는 거부한다. AppArmor/rro 차이를 정규화로 지우거나 보안 기준을 낮추지 않는다. 실제 runtime 환경에서 도구 해석과 보안 Spec 보존을 확인한 뒤 7단위를 재개해야 한다.

## R14 Medium 이미지 cache를 조회하기 전에 항상 빌드한다

위치: [round.py 68–82행](https://github.com/hyeonhb/ontosary/blob/f6fc386/experiments/domain-model/s2/trial/container/execution-lifecycle/round.py#L68), [guest.py 16–18행](https://github.com/hyeonhb/ontosary/blob/f6fc386/experiments/domain-model/s2/trial/container/execution-lifecycle/guest.py#L16).

`prepare()`는 매번 guest prepare의 build/export를 먼저 실행한 다음, 그 결과의 archive SHA/크기/image identity로 cache 요청을 구성한다. 이미지가 이미 보관돼 있어도 조회 전에 build에 도달한다. 외부 명령을 가짜로 대체한 실제 `Round.prepare()` 호출에서 모든 요청을 cache hit로 응답했지만 이미지 lookup 이전에 guest build 경로로 진입하는 것을 재현했다.

같은 회차에서 `acquire` 직후 `lookup`해 빌드0이라고 기록하는 것은 회차 간 빌드 생략을 검증하지 않는다. 새 빌드의 timestamp/출력 digest가 달라지면 동일 name의 manifest 불일치로 중단할 가능성도 있다. 이 부분은 준비물 재사용이라는 이번 목표의 핵심 미완료다.

권고: 기반 이미지·레시피·도구 버전 등 빌드 전 고정 가능한 입력으로 조회하고 hit면 보관 archive를 검증/import한다. miss에서만 build/export/등록한다. 실행별 probe/input과 이미지 빌드 입력도 구분한다. 두 번째 새 회차 계획에서 build 호출을 실패하도록 막아도 준비가 통과하는 통합 회귀를 둔다. 새 VM으로 대규모 재실행하기 전에 가짜 외부 명령으로 이 분기를 검증할 수 있다.

## R15 Medium 증거 export가 collector 거부 경계를 우회한다

위치: [guest.py 44–51행](https://github.com/hyeonhb/ontosary/blob/f6fc386/experiments/domain-model/s2/trial/container/execution-lifecycle/guest.py#L44).

export는 termination/removal만 확인하면 원본 run 하위 파일을 다시 순회해 `read_bytes()`로 읽는다. `collectionStatus=suppressed`라도 source·CLI 상태 등 원본을 포함하고, hardlink를 거부하지 않으며 용량 상한도 전체 파일을 읽은 뒤 확인한다. no-follow/bounded collector와 별도의 약한 수집 경로가 생긴다.

공개 임시 canary로 재현했다. 기존 collector는 `hardlink:source/hardlink.txt`로 거부했지만, 같은 run을 종료/삭제 확인·collection suppressed 상태로 둔 실제 `guest.export()`는 해당 내용을 archive에 포함했다. 실제 회차에서 민감 데이터가 유출됐다는 주장은 아니며, 시작0회인 이번 기록의 진위도 바꾸지 않는다. 후속 실패 경로에서 collector 거부를 보장할 수 없는 구현 결함이다.

권고: export는 검증된 수집 산출물과 명시적으로 열거한 관리자 진단만 포장한다. 수집 거부 시 worker 원본을 다시 읽지 않는다. 실패 진단에 원본 일부가 필요하다면 동일 no-follow·파일 종류·읽기 전 크기/누적 상한을 적용하는 단일 수집 경로로 다룬다. collector 거부→실제 export까지 연결한 부정 회귀를 추가한다.

## 방향과 다음 검증

준비물·실행·정책 비교를 분리한 방향은 유지할 가치가 있다. 특히 실패한 created container의 자동 삭제와 엄격한 시작 거부는 실제 근거가 생겼다. 그러나 로컬 테스트가 Store/finalizer 중심이라 전체 준비 진입점과 export를 놓쳤다. 함수별 테스트 수를 늘리기보다 **cache hit에서 build를 호출하지 않는지, collector 거부가 최종 포장까지 보존되는지**를 우선 검증해야 한다.

현재 근거로 backend를 교체하거나 권한을 확대할 이유는 부족하다. R13의 실행 환경·R14의 재사용 경로·R15의 수집 경계를 먼저 보완하고, 그 뒤 같은 정책에서 필수7단위를 확인하는 것이 적절하다. `supervisor-error`가 `supervisor-death`로 덮이는 분류는 별도 낮은 우선순위 부채로 남긴다. 실제 오류 원문은 보존돼 있어 이번 중단 판정을 바꾸지는 않는다.

이 리뷰는 다음 개발 지시나 추가 실행 예산을 승인하지 않는다. R11 unresolved·R12 기존 범위·production/live 차단을 유지하며 실제 자격 증명·모델 호출·본 비교는 결과 리뷰 뒤 결정한다. 저장한 [독립 검증/재현 요약](evidence/2026-11-14-s2-execution-independent.json)과 두 [cache 진입점 재현](evidence/2026-11-14-probe-cached-prepare.py), [export 재현](evidence/2026-11-14-probe-export.py)은 새 VM/모델 호출 없이 수행했다.

두 재현 스크립트는 검토 head `f6fc386`의 코드가 있는 checkout 루트에서 실행하는 검증 자료다. main에 아직 없는 실행기를 구현하거나 재개하는 명령이 아니다. 외부 명령은 가짜로 대체하거나 임시 디렉터리의 공개 canary만 사용한다.
