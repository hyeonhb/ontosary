# R11/R12 보완 재현 기록

실제 모델/provider 호출0회. R12는 합성 JSONL과 로컬 도구 stub으로 검증했다. R11은 unresolved이며 정상 trial 제출을 생성하지 않는다. 현재 지문은 implementation.json, 실행 결합은 execution/execution-manifest.json을 따른다.

## 입력과 명령

저장소 root, macOS26.6.2 arm64, Node22.19.0, Codex CLI0.167.0-alpha.3.2다. `<codex>`는 설치 CLI의 절대 경로이고 `<repo>`는 현재 checkout이다. cache는 `/tmp/ontosary-vendure-preparation-20261108/vendure`이며 Vendure revision `534e6003534f74761e82de1b8c6061cba89945d1`의 기존 설치를 읽기 전용으로 사용한다. 새 설치/common 빌드는 하지 않는다. 모든 출력은 새 경로를 사용한다.

| 실행 | 결과/exit code |
| --- | --- |
| `pnpm check` | 303테스트/15파일, skip0·타입 검사·예제 빌드, 0 |
| `pnpm experiment` | 4/4, 0 |
| `pnpm s2:build` | 실험 내부 TS 빌드, 0 |
| `node docs/reviews/evidence/2026-11-10-s2-trial-review-probes.mjs <codex> <new-before.json>` (수정 전 기준에서) | before/independent.json, 0. R12 false complete/null throw 원본 |
| `node work/s2-build/trial/probe.js <codex> <new-access.json>` | access-probe.json, 접근 거부 유지·detached 탈출 재현, 0 |
| `node work/s2-build/trial/runtime-accounting-probe.js <codex> <new-runtime.json>` | runtime-probe.json, 11종×2회, assertion 실패0·R11 unresolved, 0 |
| `node experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix/accounting-probe.mjs <new-accounting.json>` | accounting-fixtures.json, 18개 합성 입력, 0 |
| `node experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix/extra-runtime-probe.mjs <codex> <new-dir>` | extra-runtime/report.json·압축 stdout prefix, 0 |
| `xcrun clang <this-dir>/before/native-track.c -o <new-binary>` 후 해당 binary 실행 | before/native-track.json, ENOTSUP45 관찰·fixture 정리, 0 |
| `node work/s2-build/trial/freeze.js run` | live-refusal.json, 의도된 거부1 |
| `node work/s2-build/trial/evaluate-snapshot.js <diagnostic-dir>` | production-evaluation-refusal.json, 소스/평가기 접근 전 거부1 |

종료 matrix는 각 fixture의 copied Node를 고정 warm-up한 뒤350ms task 제한을 적용한다. delayed writer는700ms, 열린 pipe fixture는1.6초 뒤 자체 종료한다. parent-exit/요청/반환·cleanup 시간은 원시 결과에 기록한다. 바깥 fixture 정리 대기는 production 종료 보장이 아니다. 최초 cold-start matrix는 fixture 시작 전 timeout으로 불충분했으며 cold-start-inconclusive.json에 보존했다. 당시 assertion 실패8건을 성공으로 세지 않는다. 현재 probe는 assertion 실패 시 exit1을 반환한다. 같은 한계에 약한 PID 폴링을 덧붙이지 않았다.

## 교정과 diagnostic reference

```sh
node work/s2-build/trial/isolated-command.js <codex> <repo> <cache> <new-out> work/s2-build/evaluation/oracle-check.js <cache> <new-out>/oracle
node work/s2-build/evaluation/verify.js experiments/domain-model/s2/verification/2026-11-10-trial-preparation/oracle <new-out>/oracle <new-comparison.json>
```

실제 출력은 work/s2-runtime-calibration/oracle이었다. 제한된 평가 실행 exit0, 29제출·60파일이 기존 원시 교정과 wallTimeMs만 제외하고 일치했다. evaluation-reproduction.json의 파일별 canonical hash와 calibration-summary.json/실행 로그를 보존한다. 동일한29개 제출 원시는 이전 날짜 작업 디렉터리에 그대로 있으며 중복 복사하지 않았다. 비교는 의미 필드·source/evaluator ID·진단·payload·modal/종료 trace를 제외하지 않는다.

known reference source는 앞서 검증한 complete source를 사용하고 `calibrationSnapshot(source, auxiliary, newOut, baseline)`으로 diagnostic kind만 생성했다. `collectDiagnostic()`은 실제 run receipt에 결합하는 별도 경로다. production snapshot 발급자는 없다.

```sh
node work/s2-build/trial/isolated-command.js <codex> <repo> <cache> <new-out> work/s2-build/trial/evaluate-calibration-snapshot.js <diagnostic-reference> <cache> <new-out>/result.json
```

실제 출력 work/s2-runtime-reference-check/result.json, exit0. trusted reference 전체 bytes를 다시 대조한 뒤 complete-root로52/52를 확인했다. reference-calibration.json.gz와 reference-equivalence.json은 validTrialSubmission=false다. raw `s2:evaluate`는 기존 교정 도구이며 live 수명주기 진입점이 아니다. wrapper는 oracle-check, known reference calibration, production refusal entry만 허용한다.

## 원시 기록·재사용·동결

- runtime/accounting probe의 조건·lateText·다음 canary·권한 거부·usage issue·파일 hash는 판정에서 제외하지 않는다. 시간, UUID, 임시 경로에서 유래한 binding hash는 실행별 변동값이다. 원시 시간도 보존하며0으로 정규화하지 않는다.
- rawUsage/압축 stdout은 모델이 아닌 로컬 stub이다. 마지막 turn 종료 근거에 unverified를 연결해 부모 정상 exit에서도 전체 total을 확정하지 않는다. access-probe의 참고선 사례는 subtotal100,004/관찰 초과4, total=null이다. 순수 정상 fixture는 termination=fixture로 명시한다.
- `*-pre-final-accounting.json.gz`는 최종 종료 근거 연결 전의 중간 집계다. OS 관찰 원본 추적용이며 최종 R12 통과 근거가 아니다. runtime-accounting-replay.json은 최종 reducer와 저장된 원시 stdout/end를 연결한다. 원문 prefix를 보존하지 않은 중간 matrix의 절단 행은 재집계 완료로 표시하지 않고 별도의 raw-prefix probe로 검사한다.
- preservation-and-reuse.json은 agent84파일 bytes, configuration/child environment와 public checker·환경/workspace 공급 구현의 불변 지문을 검사했다. 기존 공개/private7제출·A/B/C 권한·환경 증거를 그 범위에서만 재사용한다. 새 종료/계측은 새 probe를 따른다.
- implementation.json에는303테스트/51추가 회귀와 현재 구현·테스트 hash를 기록했다. 사용자 홈 경로를 저장소 placeholder로 바꿨으며 자격 증명이나 모델 대화 내용을 기록하지 않았다.

```sh
node work/s2-build/trial/freeze.js freeze experiments/domain-model/s2/results/2026-11-10-trial-preparation <new-execution-dir> <repo> experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix
```

runtime-accounting.json의 모든 증거 hash를 확인한 뒤 execution manifest v2를 만든다. static bundle은 유지하고 현재 구현·계측·실제 probe/명시된 재사용 범위를 연결한다. 자기 executionId를 hash 입력에 포함하지 않는다. 기술 전체 상태는 partial-blocked이고 사람 동등성/의미 승인·실제 CLI/모델/자원 확인은 여전히 별개다.
