# S2 실제 CLI 연결의 비모델 타당성 검증 지시

사용자는 **기존 일회성 컨테이너 안에서 CLI 본체와 도구 실행의 권한을 분리하는 구조, 가짜 인증 표식·내부 테스트 서버를 이용한 검증, 새90분 상한**을 승인했다. 개발 세션은 최소 구현·실제 비모델 probe·증거·결과 보고까지 진행한다. **실제 자격 증명 전달과 모델 호출은 결과 리뷰 뒤 결정한다.** 로그인·토큰 갱신·provider 연결 시험·본 비교를 이번에 수행하지 않는다.

목적은 다음 실제 연결 시험에 사용할 구조가 성립하는지 확인하는 것이다. 컨테이너는 호스트/다른 실행을 격리하고, 그 안의 CLI 명령 sandbox는 CLI 전용 상태·인증과 도구의 파일/네트워크 접근을 나눈다. 컨테이너만 만들거나 CLI help가 실행됐다는 사실로 내부 경계까지 통과 처리하지 않는다. 이는 S2 실험 기반이며 Ontosary 제품 구조나 H-O/H-F 효용 검증이 아니다.

## 1. 시작과 유지할 계약

최초 명령에서 UTC와 host monotonic을 기록한 뒤 AGENTS, PROGRESS, ARCHITECTURE, ROADMAP, CONTRIBUTING을 읽는다. 읽기·설계·다운로드·환경 준비·대기·실패/수정·검증·정리·보고를 같은90분 회차에 포함한다. 시작 시계를 놓쳤으면 누락과 보수적 추정을 공개하고 예산을 재시작하지 않는다.

지시 작성 기준은 main `bcab22e`(PR #44)다. 작업 전 원격/브랜치/사용자 변경을 확인하고 최신 main에서 짧은 작업 브랜치를 만든다. 다른 checkout을 전환하거나 사용자 변경을 덮어쓰지 않는다. 이후 관련 변경이 있으면 차이를 기록한다.

다음 자료를 필요한 부분부터 확인한다.

- [Linux 평가 결과](2026-11-11-s2-linux-evaluation.md), [Linux job](../../experiments/domain-model/s2/trial/container/linux-evaluation/README.md), [lifecycle 구현](../../experiments/domain-model/s2/trial/container/lifecycle/README.md).
- [기존 실행 준비](../../experiments/domain-model/s2/trial/README.md), `trial/runtime.ts`의 설정/환경 생성, `snapshot-gate.ts`와 live 거부, container의 pinned Dockerfile·준비 도구.
- [smoke 인계](2026-11-10-s2-container-smoke.md)의 임시 CODEX_HOME/helper 경고, 실제 CLI 버전·당시 help 증거. macOS sandbox 명령/설정을 Linux 지원으로 가정하지 않는다.
- [공식 인증](https://learn.chatgpt.com/docs/auth), [설정과 상태](https://learn.chatgpt.com/docs/config-file/config-advanced), [권한](https://learn.chatgpt.com/docs/permissions). 현재 문서와 고정 CLI의 실제 지원을 구분한다.

직전 독립 리뷰는 Linux 원시7단위의 대조 재실행, 증거210파일/16archive 내부993파일 hash, 입력109,157항목·실행본·종료/수집/정리 증거와 호스트304테스트/Python26회귀를 확인했다. 새 VM에서 설치/평가를 반복한 리뷰는 아니다. 검토 범위의 추가 차단 결함 없이 linux-evaluation-reproduced를 인정했고, R11 전체 해결은 아니다.

고정할 사항은 다음과 같다.

- 동일 Lima2.3.0/VZ + containerd/nerdctl2.4.2 후보·기존 pinned base·CLI `0.167.0-alpha.3.2`·Node22.19.0. 자동 업그레이드/후보 교체를 하지 않는다. 현재 build의 image target/config/chain과 실제 container는 다시 연결한다.
- 비특권 UID/GID1000, cap drop ALL, no-new-privileges, read-only root/cgroup, CPU2·메모리4GiB·PID256와 기존 유한 tmp/log/collector 상한. 호스트 관리자 권한·전역 서비스 변경·privileged·광범위한 capability/seccomp 완화는 제외한다.
- 기존 과업·모델/B/C·평가기·정적 배포/ID와 과거 원시 증거를 유지한다. Vendure 의존성 재설치나 전체 소스 수집기는 이번 범위가 아니다.
- R11 unresolved·R12 기존 범위·production 수집/평가/live 거부·`trialAuthorized:false`·`readyForTrial:false`·본 비교 `results:null`을 유지한다. 실제 credential 전달/로그인/갱신/provider 요청/model call/본 비교는 각각0회로 구분 기록한다. 비모델 CLI 호출은 실제 횟수를 별도 기록한다.

## 2. 최소 구조

```text
기존 독립 guest supervisor / manager
  └─ 매 실행의 새 비특권 container / cgroup
       ├─ CLI 본체: 전용 CODEX_HOME·고정 설정·가짜 인증/상태
       ├─ 실제 CLI 명령 sandbox → 셸/Node probe
       │    ├─ 작업 source·scratch·셸 HOME: 허용 범위에서 RW
       │    ├─ 자료·공개 도구: RO
       │    └─ CLI 제어/인증·다른 실행·네트워크: deny
       └─ 내부 유한 테스트 서버: 허용 문맥의 양성 대조용
             ↓ 전체 종료 → 제한된 진단 수집 → 성공 cleanup 확인
```

실험 내부 `trial/container/cli-feasibility/` 같은 작은 디렉터리에 고정 probe·설정 생성·감사 코드를 둔다. 기존 manager/lifecycle를 재사용하는 작은 분기만 허용한다. 원래 fixture와 Linux 평가 job의 동작·시한을 덮어쓰지 않는다. 새 범용 runner·API 실행기·credential broker·가짜 모델 SSE 서버·CLI fork를 만들지 않는다.

이번 workload는 실제 CLI의 로컬 비모델 명령과 유한 셸/Node probe다. parent 문맥에서 실행한 대조 helper와 CLI sandbox를 거친 명령을 별도 분모로 기록한다. manager는 유한 명령·설정/입력 지문·native identity로 등록하며 worker 표식·stdout EOF·완료 문구를 종료 권한으로 사용하지 않는다. 모든 CLI 자손/helper/테스트 서버는 소유 실행 경계에 포함하고, 감독자는 밖에 둔다.

CLI probe의 최초 runtime create 직전부터60초, 종료 확인10초·수집10초, service RuntimeMaxSec90/TimeoutStartSec5/TimeoutStopSec12, 외부 단위120초를 최대치로 둔다. 작업에 더 짧은 시한이 가능하면 줄인다. 외부 wrapper 종료 시 기존 guest lease5초·독립 cleanup으로 정리한다. 기존 admission·pending/runtime/cgroup 확인·service 실패 시 공개 철회/next 거부를 재사용한다. 이번은 실제 모델 세션의30분 제한 구현이 아니다.

## 3. 구현 순서

### A. 같은 환경과 실제 CLI 지원 확인 — 최초20분까지

1. 비용 ledger·소유 자원 inventory·기준 commit/정적 입력 hash를 먼저 남긴다. 소유 prefix/VM을 재준비하고 기존 image/config를 사용한다. 작은 fixture만 준비하며 Vendure 설치·build를 반복하지 않는다. 다운로드 네트워크는 준비 단계로 한정한다.
2. 고정 CLI의 version/help, 실제 제공하는 config/schema/로컬 진단·sandbox 명령을 확인한다. 지원하지 않는 최신 문서 옵션을 그대로 넣지 않는다. 프롬프트를 보내는 `exec`·대화/turn 시작·resume/fork·review는 호출하지 않는다. 모델 없이 쓸 수 있는 CLI sandbox 경로가 없으면 대체 agent/API를 만들지 말고 차단 사유로 인계한다.
3. 새 CLI 전용 상태 디렉터리를 `/tmp` 아래 helper 경고가 나던 배치와 구분해 준비한다. 예: CLI 상태 `/home/runner/cli-state`, 셸 HOME `/home/worker`, scratch `/scratch`. 실제 지원에 따라 경로는 정하되 실행마다 새 저장소이고 필요한 항목만 mount한다. helper 생성/실행이 가능하고 경고의 원인이 해소됐는지 확인한다. helper 때문에 control 전체를 셸에 공개하지 않는다.
4. 현재 인증 저장 방식은 비밀을 읽지 않는 메타데이터로만 조사한다. 예: allowlist한 설정 키의 값, 인증 파일 존재 여부·권한, 저장소 사용 방식. 실제 `auth.json` 내용·키체인 값·토큰/키/계정 식별자·전체 사용자 config/env를 출력·복사·hash·archive하지 않는다. 메타데이터만으로 확인할 수 없으면 unknown과 후속 확인 방법을 남긴다. 로그인/logout/refresh 및 인증 상태 확인 중 외부 접속할 수 있는 명령을 사용하지 않는다.

### B. 실행별 설정과 가짜 인증 경계 — 최초45분까지

5. CLI용 CODEX_HOME·상태/기록 저장소와 셸용 HOME·source/scratch를 분리한다. 명령 실행 환경은 allowlist에서 만들고 호스트 proxy·인증·PATH/셸 초기화·전역 지시·skills·MCP/plugins/앱 연결·이전 세션을 가져오지 않는다. 설정은 manager가 준비해 변경 못 하게 하고 CLI가 써야 하는 임시 상태는 별도 허용한다. host home·키체인·socket·저장소 전체는 mount하지 않는다.
6. 고정 설정으로 자동 외부 기능/도구·서브 agent·사용자/프로젝트 지시 로딩을 제어한다. 실제 발견 가능한 시스템/사용자/프로젝트 설정 계층, 환경 변수와 실행 인자의 우선순위를 조사해 manifest에 남긴다. `.codex`, `.agents`, `AGENTS.md`, exec rules 등은 설치 버전의 로딩 경로를 기준으로 확인한다. fixture의 고유 무해 표식과 사용 가능한 resolved config/진단을 사용하고, 구성 파일을 만들었다는 사실만으로 적용을 증명하지 않는다. CLI native 제약이나 조직 요구사항을 우회하지 않는다.
7. 빈 설정으로 보이는 것과 모델에 제공될 실제 tool inventory를 구분한다. 모델 없이 확인할 수 있는 명령/기능/설정만 기록하고, 실제 turn의 tool inventory·지시 내용·agent 판단 경로는 미검증으로 둔다. 이를 관찰하려고 모델을 호출하거나 app-server의 turn을 시작하지 않는다.
8. CLI 전용 경로에 고유 **가짜 인증 표식**을 넣고 parent 문맥에서 읽기 가능한 양성 대조를 만든다. 실제 CLI의 로컬 인증 파서까지 관찰 가능한 경우 형식/인식만 확인하며, 가짜 파일을 정상 계정 로그인으로 보고하지 않는다. 파서 지원이 확인되지 않아도 파일 접근 경계는 별도로 측정한다.
9. 동일 유효 권한 profile의 실제 CLI sandbox에서 source 읽기·쓰기와 자료 읽기가 성공하는지 먼저 확인한다. 이어 control/가짜 인증 직접 읽기·쓰기, 그 경로로 향하는 symlink, parent의 `/proc` 환경·root/fd 등을 통한 접근과 자식 환경 상속을 검사한다. parent 대조 helper에 일부러 가짜 환경 표식·열린 canary FD를 두어 민감 값이 실제 존재함을 보인다. 환경 변수 필터만으로 `/proc`·상속 FD까지 막혔다고 주장하지 않는다. 테스트는 접근 성공 여부·표식 발견 boolean을 기록하며 표식 값 자체를 셸 stdout/일반 산출물로 출력하지 않는다.

### C. 내부 네트워크와 반복·종료 — 최초70분까지

10. 검증용 runtime에서는 인터넷/provider egress를 차단한다. 가장 작은 구성은 `--network=none`을 유지한 container의 parent loopback에서 유한 테스트 서버를 띄우고 native CLI sandbox의 네트워크 차단을 대조하는 것이다. 다른 VM 내부 배치를 쓸 경우 전용 내부 서버 외에는 route/forwarding을 허용하지 않는 실제 구성을 남긴다. 테스트를 위해 호스트 일반 서비스나 다른 실행을 노출하지 않는다. 큰 proxy·인증 주입 서버·TLS 중간자 구조를 새로 만들지 않는다.
11. parent와 같은 문맥의 고정 helper는 존재하는 테스트 서버에 접속하고, CLI sandbox 명령은 같은 주소/직접 IP/localhost 및 알려진 Unix socket에 접근하지 못해야 한다. IPv4는 필수이며 IPv6를 검사한다면 양성 listener부터 확인한다. 미지원 주소 계열은 미실행/미지원으로 기록한다. DNS 이름을 사용하면 그 해석/직접 IP 우회도 구분한다. proxy 환경 변수만 설정하거나 허용 도메인 문자열만 적은 것을 경계로 인정하지 않는다. route·network namespace·socket/접속 결과를 함께 남긴다.
12. 외부 egress 없음은 실제 namespace/route/forwarding·차단 설정과 연결 시도 결과로 확인한다. 응답하지 않는 외부 서버나 ENOENT만으로 거부를 입증하지 않는다. parent 양성 probe는 CLI의 실제 provider 요청이 아니다. provider/인증 endpoint의 지원·성공·허용 목록 확정은 이후 검토로 남긴다. 준비용 네트워크가 검증 중 남지 않았는지도 확인한다.
13. 정상 묶음을 서로 다른 새 실행2회에서 반복한다. 첫 실행의 state/history/config/source/scratch에 manager가 만든 표식을 남기고 두 번째 실행에 재사용되지 않음을 확인한다. 코드/정책은 같은 hash, 상태 저장소와 run/container/cgroup/output은 서로 다른 identity여야 한다. 빈 경로 ENOENT 관찰만으로 기존 다른 실행에 대한 접근 차단을 대신하지 않는다. 별도의 존재하는 외부 canary와 실제 mount 부재/deny 근거를 함께 확인한다.
14. 실제 CLI sandbox가 시작한 유한 자식 작업에 짧은 timeout을 주입한다. 예: 실행 준비/작동 확인 뒤5초 안에 작업 종료를 요청하고,8초 뒤 예약한 쓰기를 넘겨 관찰한다. 동작이 확인된 유한 대조에서는 쓰기가 실제 발생해야 한다. 기존 전체 종료→진단 수집→cleanup을 확인하고 timeout 결과를 정상 실행/제출로 채택하지 않는다. 시한·관찰 구간은 사전에 고정하며 모든 단위의120초 외부 상한 안에 둔다.

## 4. 필수 검증표와 해석

| 항목 | 통과에 필요한 관찰 | 주장하지 않을 것 |
| --- | --- | --- |
| 고정 CLI 기동 | 실제 version/hash, 로컬 명령, helper 생성/실행, 설정 파싱 | version/help만으로 모델 연결 성공 |
| 설정 격리 | 적용 profile/계층 근거, host 설정/지시 배제, 고정 config/hash | 실제 turn의 전체 지시·tool inventory 확인 |
| 파일 권한 | source RW·자료 RO 성공, control/외부 canary 접근 거부, 실제 mount/권한 | 존재하지 않는 파일의 읽기 실패가 보안 경계라는 주장 |
| 가짜 인증 | parent 양성 읽기, sandbox 직접/우회/환경/FD 접근 실패, 표식 비노출 | 실제 자격 증명 전달·갱신·계정 권한 검증 |
| 내부 네트워크 | 응답하는 서버에 parent 접근 성공·sandbox 접근 거부, 외부 egress 차단 | 실제 CLI provider transport·인증 endpoint 검증 |
| 실행 간 독립성 | 정상 새2단위, 설정/입력은 동일·상태는 분리, 이전 표식 미상속 | 모델 backend의 상태 독립성 증명 |
| 종료·수집 | 실제 CLI 자손 포함 종료 증거, timeout/유한 대조, 성공 cleanup 후 소비 | R11 전체 해결/임의 agent 제출 authority 발급 |

허용 동작까지 모두 실패하는 profile은 거부 검사 통과가 아니다. 접근 실패의 errno/exit·stderr·서버 수신 기록과 양성 대조를 보존한다. 가짜 표식이 자식에게 보이거나 일반 출력/수집 결과에 누출되면 실패로 기록하며 결과를 필터로 지워 성공 처리하지 않는다. manager 전용 합성 fixture 정의는 인증 유출 결과와 구분한다.

기존 collector128파일/16MiB/깊이16/로그1MiB를 유지하고 일반 파일·디렉터리/no-follow·hardlink 거부를 재사용한다. control 상태나 인증 저장소 전체를 자동 archive하지 않는다. 실제 credential은 애초 제공하지 않으며, manager가 고정한 합성 자료와 필요한 비밀 없는 증거만 수집한다. receipt는 fixtureOnly/validSubmission=false이고 기존 production/live 진입점의 거부를 실제 확인한다.

공유 lifecycle를 수정하면 normal/timeout 및 supervisor/wrapper 사망·공개 후 철회 중 변경에 영향받는 경로를 재검증한다. 회귀 범위를 코드 diff로 설명하고 원래25개/7평가를 전부 반복했다고 표현하지 않는다. native CLI sandbox 검증과 일반 helper의 실행 경계를 분리한다. RuntimeMaxSec 도달/불명확 create 중 supervisor 사망 등 실제 주입하지 않은 경로는 미검증으로 유지한다.

## 5. 비용 상한과 중단 기준

| 최초 시작 기준 마감 | 요구 결과 | 미충족 시 |
| --- | --- | --- |
| 20분 | 동일 환경의 CLI 최소 기동·설정/저장 방식 조사 | 새 탐색 중단, 최소 증거와 원인 정리 |
| 45분 | native 내부 sandbox의 허용 작업·설정/가짜 인증 핵심 경계 | 큰 우회 없이 blocked/inconclusive로 인계 |
| 70분 | 네트워크 대조·새2단위·종료/필요 회귀 확보 | 새 구현/실행/재준비 중단 |
| 90분 | 검사·소유 자원 정리·증거/보고 완료 | 초과/미완료를 공개하고 복구 인계 |

신규 유료 비용0이다. 이번/이전/누적 시간을 구분하고 이전90분·3시간·4시간 잔여 예산을 재개하지 않는다. 명령별 timeout은 다음 마감의 잔여 시간을 넘지 않게 하고 새120초 단위를 시작할 여유가 없으면 시작하지 않는다. 실패/재준비·설치 대기도 청구한다. 마지막20분은 검사·정리·보고에 사용한다. Git 게시/PR/merge 전달 시간은 별도 기록하되 구현/검증을 그 시간으로 넘기지 않는다.

가짜 인증 노출, 설정 상속·네트워크 분리 실패, 종료/수집 경계 회귀가 나오면 후속 단계 확장을 멈추고 원인을 확인한다. 동일 후보의 원인 확인된 국소 경로/설정/packaging 수정만 남은 시간 안에서 허용하며 최초 실패·수정본을 보존한다. native sandbox/권한 적용을 확인할 수 없거나, 고정 CLI/후보 교체·권한 확대·범용 proxy/broker/API runner가 필요하거나, 실제 credential/provider 호출 없이는 더 확인할 수 없거나, 중간 마감을 충족하지 못하면 회차 탐색을 종료하고 인계한다. sandbox를 꺼서 통과시키거나 불확실한 항목을 정상 처리하지 않는다.

## 6. 완료와 인계

최종 판정은 다음 중 하나다.

- **ready-for-live-connection-review:** 필수 표의 비모델 검증과 반복·종료·영향 회귀·정리 완료. 다음 실제 연결 시험을 설계할 근거가 갖춰졌다는 뜻이며 실행 승인이 아니다.
- **inconclusive:** 시간/관측 수단 부족. 항목별 통과·실패·미검증과 부족한 증거를 명시한다.
- **blocked:** 승인 범위 안에서 구조를 성립시킬 수 없는 구체적 원인 확인. 다음 선택지와 추가 비용을 제시한다.

어느 판정이든 원시 실행/실패·당시 실행 코드/설정/CLI·image/native identity·분모·단계별 시간·정리 상태가 있어야 한다. 초기 실행 도구도 **실행 전에** snapshot/hash를 남겨 나중에 재구성한 코드를 당시 실행본으로 기록하지 않는다. 명령은 고정 버전의 실제 지원을 기준으로 재현 가능하게 남긴다. 실제 비밀이 들어갈 수 있는 사용자 config/env/인증 저장소를 원시 증거라는 이유로 포함하지 않는다.

새 `experiments/domain-model/s2/verification/<실제 날짜>-cli-feasibility/`와 `docs/reviews/<실제 날짜>-s2-cli-feasibility.md`에 추가한다. 같은 경로가 있으면 suffix를 붙이고 과거 증거를 덮어쓰지 않는다. 보고서는 결론/범위 → 필수 표와 정상2회/timeout → 세션·설정/가짜 인증/네트워크 구조 → 실패·수정 → 비용·정리 → 실제 연결 전 미검증 순서로 작성한다. 설정/도구의 확인 수준, 실제 credential 전달0·provider/model0과 비모델 CLI 횟수를 명시한다.

작업 소유 container/task·테스트 서버·systemd unit/slice·내부 network/rules·VM/image/volume·prefix/cache를 정리하고 부재/종료를 확인한다. 시작 전 inventory·URL/hash로 이번 소유 자원만 식별하며 shared prune·기존 cache 삭제·호스트 인증 변경을 하지 않는다. cleanup 실패는 대상 ID/경로·관측 상태·복구 명령을 인계한다. VM 삭제로 개별 종료 검증을 대신하지 않는다.

`pnpm check`, 필요한 S2 build, 기존 collector/cleanup 및 변경한 경계의 의미 있는 회귀를 실행한다. 제품 분석·원래 평가 의미를 바꾸지 않으므로 `pnpm experiment`/Vendure7단위 전체 반복은 기본 요구가 아니다. 검증하지 못한 항목을 명시하고 검증하지 않은 head를 merge하지 않는다. PROGRESS·ARCHITECTURE·ROADMAP·REVIEW_CONTEXT·관련 README를 실제 결과/독립 리뷰 대기로 갱신하며 중요한 선택은 DECISIONS에 기록한다.

staged diff 검토 → commit → push → PR/자체 검토 → 필수 검사·검증한 head 확인 후 merge → 자신의 로컬 main 동기화까지 기존 지속 승인에 따라 진행한다. 원격 게시 권한과 실제 자격 증명/모델 호출 권한을 구분한다. **완료 후 실제 자격 증명 전달·인증/provider 연결·모델 호출·본 비교를 시작하지 않고 결과 리뷰를 기다린다.**
