# S2 실행 전 준비 도구

2026-11-10 독립 리뷰에서 R11 종료 탈출과 R12 usage false complete/구조 오류를 확인했다. 다음 변경은 [R11/R12 개발 지시](../../../../docs/reviews/2026-11-10-s2-runtime-accounting-fix-instructions.md)를 따른다. 아래 계측 설명은 의도한 계약이며 현재 구현이 모든 부정 사례를 충족한다는 뜻이 아니다. 보완 구현·독립 리뷰 전까지 두 항목과 실제 비교 차단을 유지한다.

이번 버전은 과업·C 자료·공개 타입 검사·계측/수집과 macOS 도구 경계를 준비한다. 실제 모델 호출은 없다. `s2:trial:run`은 항상 거부한다. `trialAuthorized:false`, `readyForTrial:false`, `results:null`이며 사람 대응 검토와 별도 실행 승인이 필요하다.

## 계약

사용자 2026-11-10 후속 결정으로 누적100,000토큰 hard cap을 필수 통과 조건에서 제외했다. 100,000은 보고용 참고선이며 중단 기준이 아니다. 1,800초는 첫 모델 요청부터 도구 실행까지 포함한다. 현 도구 대역에서는 monotonic clock으로 짧은 시간 제한을 실제 검증했다. API 실행기로 확장하지 않는다.

CLI는 실제 turn_context에서 확인한 `gpt-6-astra`/`high`, 설치된 `codex-cli 0.167.0-alpha.3.2`를 기준으로 한다. immutable backend snapshot/service tier는 세션 기록에서 확인되지 않았다. 모델 seed는 검증한 CLI 옵션에 없고 배정 seed와 다르다. 고정 catalog/바이너리 hash는 검증 산출물에 기록한다. [공식 비대화 실행 문서](https://learn.chatgpt.com/docs/non-interactive-mode)와 [permission/config 문서](https://learn.chatgpt.com/docs/config-file/config-reference)를 참고했다. 실제 CLI의 help·bundled catalog·sandbox 실행을 확인했으며 model dispatch를 하지 않았다.

`telemetry.ts`는 completed-turn usage의 원시 이벤트를 합산한다. input에 cache가 포함되고 output에 reasoning이 포함된다는 필드 계약으로 세부 수치를 중복 합산하지 않는다. 이벤트 ID가 없으면 관찰된 turn 번호로 대응한다. 중복·충돌·누락·실패 turn을 구분하며 불완전할 때 총비용을 null로 두고 관찰된 하한만 남긴다. raw JSONL을 별도로 보존해야 한다. 요청별/in-flight usage·공급자 내부 요청은 이 경로로 완전히 관찰하지 못한다. 실제 공급자 usage 검증은 별도다. 셸 읽기량과 모델 입력 token은 같지 않다. 파일 읽기 경로/bytes는 도구 이벤트에서 확인 가능한 범위만 수집하며 임의 shell 읽기 완전 추적은 미구현이다. tokenizer가 없어 전체자료 tokens는 null, bytes만 측정한다.

## 도구와 재현

저장소 root에서 실행한다. 모든 출력 경로는 기존에 없어야 한다. `<codex>`는 설치된 CLI의 절대 경로다.

```sh
pnpm s2:prepare <pinned-cache> <bundle-a>
pnpm s2:prepare <pinned-cache> <bundle-b>
pnpm s2:verify <bundle-a> <bundle-b> <new-report.json>
pnpm s2:trial:environment <pinned-cache> <new-public-environment>
pnpm s2:trial:validate-public <codex> <public-environment> <new-public-report.json>
pnpm s2:trial:probe <codex> <new-probe.json>
pnpm s2:trial:validate-workspaces <codex> <bundle-a> <pinned-cache> <public-environment> <new-workspace-report.json>
pnpm s2:trial:freeze <bundle-a> <new-execution-artifacts> <repo> <verification-evidence>
pnpm s2:trial:run
```

마지막 명령은 준비 상태의 거부 검증이다. 실제 모델을 시작하는 방법으로 쓰지 않는다. 이후 승인도 현재 도구가 자동 추정하지 않는다. 후속 리뷰에서 격리 결함을 해결하고 승인 기록을 정확한 artifact hash에 연결한 뒤 live adapter를 별도 검토한다. 기존 `workspace.ts`는 파일 복사기이고 선택적 공통 public tools 연결만 추가했다. `trial/validate-workspaces.ts`가 실제 같은 UID·Codex permission profile에서 읽기 전용 자료·공개 검사·다른 조건 경로 거부를 검증한다.

`environment.ts`는 원래4735파일과 설치된 node_modules/admin-ui node_modules/common lib·scope config를 별도 복제한다. APFS clone을 사용하며 설치/빌드하지 않는다. 모든 dependency link는 복제 환경 내부로만 해석되는지 검사하고, 일반 dependency 파일 bytes를 원래 cache와 대조해 manifest/hash를 남긴다. 도구에는 standalone public checker와 TypeScript만 있고 평가기·기대값·변형은 없다. Node 실행 파일도 public tools로 복제하며 원래 호스트 홈 경로를 허용하지 않는다. Node/도구/환경/자료는 profile에서 read, production source와 auxiliary/scratch/새 HOME만 write다. config·credential을 위한 control 경로는 셸에서 읽을 수 없다. 실행기의 인증은 이번에 공급하지 않았다.

## 격리의 확인 범위와 차단 조건

최소 profile의 package.json 읽기 예외를 발견해 원래 cache·Ontosary checkout·호스트 홈에 명시적인 deny를 추가했다. 존재하는 package.json canary와 실제 cache/package.json 거부를 다시 검증한다. 실제 Codex macOS sandbox에서 허용 소스 읽기/편집, 자료 쓰기 거부, 존재하는 외부 canary/상위 경로/symlink/control/다른 조건/Ontosary/cache 읽기 거부, 외부 TCP/호스트 Unix socket 접근 거부를 관찰했다. 최종 snapshot profile의 파일 쓰기도 거부됐다. 존재하지 않는 파일의 ENOENT를 거부 성공으로 세지 않는다.

**분리된 자식 프로세스가 process-group 종료를 벗어나는 실제 반례가 남아 있다.** `runtime.ts`의 timeout은 실행기 그룹을 종료하지만 세션을 분리한 모든 자손을 정지시키는 보안 경계가 아니다. 따라서 실제 agent 실행과 적대적 제출 수집은 차단한다. `snapshot()`은 중간 변경·symlink/특수 파일을 거부하고 전체 추가/수정/삭제와 auxiliary를 보존하지만, 살아 있는 적대적 writer가 없는 상태를 보장하지 못한 것을 해결했다고 표현하지 않는다. 실제 모델 세션의 tool inventory·인증 경로·전역 지시 배제도 미검증이며 메모리/CPU 자원 상한은 미동결이다.

후속 선택은 사용자 권한을 확대하지 않고 모든 자손 종료를 강제할 수 있는 native 경계 조사, 또는 별도 격리 runtime 도입 검토다. 이번에 새 플랫폼/유료 인프라/호스트 계정·권한 변경을 하지 않았다. 토큰 hard cap 부재와 이 격리 차단을 구분한다.

## 평가·제출·실패 처리

기존52사례(보존16+요구36) 안에 invalid service의 값0·완료1·오류0·동기 예외0, dialog의 undefined resolve1 assertion을 추가했다. 별도 helper 해법도 허용한다. 참조 diff 일치로 점수를 주지 않는다. 원래24제출에 정책 반례5개를 더한29제출이다. 미지원 의존성/문법은 policy failure로 바꾸지 않는다.

알려진 교정 제출은 `isolated-command.ts`에서 필요한 평가기/근거/TypeScript만 복사한 디렉터리와 고정 cache를 read-only로, 결과만 쓰기 가능하게 두고 network와 호스트 홈을 명시적으로 차단해 검증했다. 이는 임의 제출의 프로세스 탈출까지 안전하다는 뜻이 아니다. 실제 제출은 전체 production과 별도 auxiliary를 불변 snapshot으로 수집한 후 검증하며, 원본을 복구하거나 변경 파일을 빼면 안 된다. 공개 타입 검사는 실제 파일/추가 helper를 검사하고, private type/scope/snapshot/behavior gate는 별개로 보존한다.

`snapshot-gate.ts`는 수집 manifest와 source/auxiliary 전체 hash를 검사하고, complete-root reader가 처리한 파일 목록이 전체 source와 같은지 대조한다. `.git`/`node_modules` 등 기존 reader가 건너뛸 생산 파일도 증거를 보존한 채 명시적으로 거부한다. `evaluate-snapshot.ts`는 이 검사를 평가 전후에 실행한다. 알려진 reference snapshot은 read-only profile에서52/52를 통과했고 delta/complete-root와 동일 submissionId·판정·trace를 얻었다. 이는 살아 있는 writer의 정지를 보장하는 경계를 대신하지 않는다.

```sh
# 빌드 후, 검토한 교정 snapshot을 제한된 평가 환경에서 확인
node work/s2-build/trial/isolated-command.js <codex> <repo> <cache> <new-out> work/s2-build/trial/evaluate-snapshot.js <snapshot> <cache> <new-out>/result.json
```

9개 예정 실행은 블록별 A/B/C 각1회·위치별 각1회 균형을 갖는 seeded rotation이다. 조건 매핑과 반복 정보는 evaluator에만 있고 agent 작업공간은 blind run ID와 같은 자료 경로를 쓴다. 모두 not-run이며 52사례를52실험으로 세지 않는다. 실행 중 사람 힌트는 없다. 성공·타입/동작 실패·미지원·timeout/미제출·환경 장애를 모두 보고한다. 성능에 따른 재시도는 없고 명백한 환경 장애만 최대1회 대체한다. 원래 실패 증거와 시도를 보존하며 반복 장애·공통 평가 결함이면 전체 배치를 중단한다.

배포 manifest는 정적 내용만 식별하고 execution-manifest는 그 hash와 구현/config/평가 버전을 연결한다. executionId는 자기 필드를 제외한 canonical 내용 hash다. 사람/독립 승인·실제 결과는 빈칸으로 남긴다. 사람 재작업·과거 제작비는 실제 측정 없으면 null이다.
