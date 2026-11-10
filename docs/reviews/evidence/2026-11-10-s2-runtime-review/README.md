# R11/R12 독립 재검토 증거

기준 `0472c2bb5ab857f8a79eb7cda74f0be1aa29fad7`. 실제 모델 호출/본 비교0회이며 R11은 미해결이다. 합성 usage와 로컬 도구 실행을 provider 관측으로 해석하지 않는다. 제품 구현·고정 cache·과거 증거는 변경하지 않았다.

## 실행

저장소 root에서 `pnpm check`, `pnpm experiment`, `pnpm s2:build`를 실행했다. 303테스트(skip0)·타입 검사·예제 빌드·기존 비교4/4가 통과했다. 아래 `<work>`는 새 출력 디렉터리, `<codex>`는 설치 CLI 절대 경로, `<repo>`는 현재 checkout, `<cache>`는 기존 pinned Vendure cache다. 이번 출력은 `work/s2-runtime-review-20261110`이었다.

```sh
node work/s2-build/trial/runtime-accounting-probe.js <codex> <work>/runtime-probe.json
node work/s2-build/trial/isolated-command.js <codex> <repo> <cache> <work>/calibration work/s2-build/evaluation/oracle-check.js <cache> <work>/calibration/oracle
node work/s2-build/evaluation/verify.js experiments/domain-model/s2/verification/2026-11-10-trial-preparation/oracle <work>/calibration/oracle <work>/evaluation-reproduction.json
node work/s2-build/trial/freeze.js freeze experiments/domain-model/s2/results/2026-11-10-trial-preparation <work>/execution <repo> experiments/domain-model/s2/verification/2026-11-10-runtime-accounting-fix
```

모두 exit0. runtime matrix는 두 반복22실행이며 실패0·늦은 쓰기8건이다. 기존 자체 종료 fixture를 사용했고 정리 대기를 종료 인증으로 세지 않았다. `runtime-audit.json`은 다음 canary 보존·권한 거부·모든 production 차단/total=null을 추가 검증한 요약이다. 원시는 `runtime-probe.json`이다. SDK 헤더의 NOTE_TRACK/NOTE_CHILD 미지원 표시와 이전 `before/native-track.c`의 새 빌드/실행에서 ENOTSUP45를 확인했다(`native-track.json`).

참조 입력은 이전 독립 리뷰의 complete source를 사용했다. sourceId `d1c36b00ac4ffff9b7564a642bb51fbe0d9605cb9eda9515195e4c22092fd685`,4,735파일·delta3개다. 새 환경에서는 `openEnvironment`의 baseline에 `deltaSubmission`/`variantDelta('reference')`를 적용해 같은 전체 source를 만들 수 있다. 이번에는 기존 manifest의 before hash로 baseline map을 복원하고 `calibrationSnapshot(source, auxiliary, <work>/reference-diagnostic, baseline)`으로 새 진단 자료를 만들었다. trusted 참조 전체 bytes 대조는 다음 entry가 다시 수행한다.

```sh
node work/s2-build/trial/isolated-command.js <codex> <repo> <cache> <work>/reference-check work/s2-build/trial/evaluate-calibration-snapshot.js <work>/reference-diagnostic <cache> <work>/reference-check/result.json
node docs/reviews/evidence/2026-11-10-s2-runtime-review-audit.mjs <work>/independent-audit-final.json
```

두 명령 exit0. 감사 스크립트는 순차 조합3,279개·추가20사례·기록18fixture 재집계, 구현/테스트16파일·증거41파일·agent84파일 지문, manifest 자체 ID/재생성, production/live 거부, runtime22행, 참조/delta 동작 대조를 검사한다. `<work>` 아래 앞서 생성한 파일/디렉터리가 필요하다. 처음 참조/delta 비교에서 behavior.wallTimeMs까지 비교한 감사 스크립트의 오류를 시간 제외 규칙에 맞춰 수정했다. 의미 필드는 제외하지 않았다.

## 보존과 한계

- `independent-audit.json`: 최종 감사 결과와 합성20사례 원문/상태.3,279조합은 ID 없는 작은 문법이며 모든 JSONL의 증명이 아니다.
- `evaluation-reproduction.json`, `calibration-summary.json`: 새29제출60파일의 기존 v4 대조. wallTimeMs만 제외하며 중복되는 원시29제출은 기존 저장 결과와 hash로 연결한다.
- `reference-calibration.json.gz`, `reference-equivalence.json`: 새 참조 전체 결과와52사례/요청/modal/종료 trace·submissionId 대조. validTrialSubmission=false다.
- `calibration-execution.json`, `reference-execution.json`: 실제 sandbox 실행과 blocked 종료 상태. 알려진 fixture의 검증이며 임의 제출을 안전하게 실행한다는 의미가 아니다.
- `check.log`, `experiment.log`: 이번 실행 로그. 로컬 repository 절대 경로만 placeholder로 바꿨다.

공개/private7제출·환경 공급·A/B/C 접근은 해당 코드/자료 불변 확인을 바탕으로 이전 증거를 재사용했다. 실제 CLI 인증·전역 지시·모델 공급자/자원 정책·사람 승인은 검증하지 않았다. 본 비교는 계속 차단한다.
