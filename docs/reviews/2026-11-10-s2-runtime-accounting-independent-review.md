# S2 R11/R12 보완 독립 리뷰 — 2026-11-10

**R12는 검증한 계약 범위에서 해결됐다. R11은 미해결이며 실제 비교 차단을 유지한다. 이번 지시의 ‘R12 완료 + R11 차단 인계’ 조건은 충족했다.** 검토 범위에서 추가 차단 결함은 발견하지 않았다. 전체 실행 준비 완료나 실제 모델 사용량 검증으로 확대하지 않는다.

대상은 PR #35/main `0472c2bb5ab857f8a79eb7cda74f0be1aa29fad7`의 [개발 인계](2026-11-10-s2-runtime-accounting-fix.md)와 실제 구현이다. 사용자가 전달한 `2026-11-08-domain-model-contract-fix.md`는 이전 S1 R6/R7 보고서였다. 최신 PROGRESS·PR 이력에서 직전 [R11/R12 지시](2026-11-10-s2-runtime-accounting-fix-instructions.md)의 결과를 확인해 이 대상으로 검토했다. 원래 개발 checkout은 수정하지 않았고, 제품/실험 구현·고정 cache·과거 증거도 변경하지 않았다.

## 판정

| 항목 | 독립 판정 | 근거 |
| --- | --- | --- |
| R12 · 입력/turn/집계 | 검증 범위에서 해결 | 원래 다섯 반례, 추가20사례, 순차 이벤트 조합3,279개에서 잘못된 확정/이중 합산을 발견하지 않음 |
| R11 · 모든 writer 종료 | 미해결 · High 차단 유지 | 실제22실행에서 분리 자손/손자/열린 핸들의 늦은 쓰기8건 재현 |
| R11 · 진단/제출 분리 | 보완 인정 | 정상 부모 종료도 collectionAllowed=false, 위조 receipt·production 수집/평가 거부 |
| 기존 과업·모델·평가 | 보존 | 29제출60파일 재현, 참조52사례/trace 일치, agent84파일·세 ID 유지 |
| 실제 비교/사람 승인 | 미실행·대기 | live entry 거부, 배정9개 not-run, trialAuthorized/readyForTrial=false |

R11이 남았다는 사실을 새로운 결함으로 다시 번호 붙이지 않는다. 원래 지시는 기존 CLI·macOS에서 경계가 확보되지 않으면 실패와 대안을 인계하고 R12를 독립 완료할 수 있게 했다. 구현은 이 범위와 ADR-029를 따랐다.

## R12 확인

[`telemetry.ts`](../../experiments/domain-model/s2/trial/telemetry.ts)는 unknown JSON 검사 뒤 순차 활성 turn을 추적한다. event identity는 재전달 검사에만 사용하며 turn identity와 구분한다. 상충 완료/identity 재사용은 관련 turn의 기존 합계까지 무효화한다. 시작 없는 완료·미완료 turn·구조 오류는 확정 total을 만들지 않는다. cache/reasoning 중복 합산, 미관측값의0 처리, 누적 정수 overflow도 회귀에서 차단됐다.

[독립 감사 스크립트](evidence/2026-11-10-s2-runtime-review-audit.mjs)로 시작/정상 완료/실패 세 이벤트의 길이1~7 조합3,279개를 열거했다. ID 없는 이 작은 문법에서는 `(시작→정상 완료)+`만 complete가 되어야 하며 모든 판정과 합계가 일치했다. 이 검사는 전체 JSONL 언어의 증명이 아니다. 별도20사례에서는 원래 다섯 반례 외에 이전 turn의 늦은 충돌과 합계 철회, 활성 turn을 가로지르는 ID 재사용, 실패 뒤 정상 turn, unknown 이벤트, 종료/절단 상태를 확인했다. 커밋된18개 합성 fixture도 최종 reducer로 재집계해 전체 출력이 일치했다.

`usageEnd()`는 현 runtime의 종료 경계를 unverified로 전달한다. 실제 도구가 exit0·EOF를 반환해도 전체 total은 null이며, 정상 turn의 subtotal만 남는다. 실제 macOS22실행 모두 이 상태를 유지했다. 합성 정상 입력의 `termination:fixture`와 실제 종료 근거를 섞지 않는다. 따라서 이번 해결은 **순차 이벤트 집계의 정확성과 불확실성 표시**에 관한 것이다. 설치된 alpha CLI의 실제 provider 로그/청구 전체·in-flight 사용량은 아직 검증하지 않았다.

메타데이터는 행 수/행 크기/전체 bytes 상한을 갖고 ID 색인과 한 번의 순회로 처리한다. 원시 행의 hash·제외 이유를 남겨 철회 근거를 추적할 수 있다. subtotal을 공급자 소비의 하한이라고 부르지 않고 참고선 초과와 전체 미초과 여부를 구분한 점도 지시에 맞는다. 토큰 hard cap을 새로 요구할 이유는 발견하지 않았다.

## R11 확인

[`runtime.ts`](../../experiments/domain-model/s2/trial/runtime.ts)의 변경은 강제 종료 해결책이 아니라 **미확인 실행을 정상 제출로 취급하지 않는 차단**이다. 부모 exit·timeout·spawn 오류·중단과 종료 요청/반환 시각을 구분하고, pipe 정리 대기에250ms 제한을 둔다. 실제 종료 authority를 발급하는 경로는 없다. `snapshot()`과 `checkedSnapshot()`/production 평가 entry가 항상 거부하므로 호출자가 true나 manifest를 작성해 차단을 해제할 수 없다.

새 경로에서 개발 matrix를 재실행했다. 두 반복·총22실행의 assertion 실패는0이다. 부모 정상 종료 후 자식, detached, 손자, 열린 핸들 사례에서 늦은 쓰기8건을 다시 관찰했다. 다음 workspace canary는 모두 원래 내용이었고 해당 쓰기는 거부됐다. source/auxiliary/manifest/checksum 읽기 전용 검사와 진단/production 구분도 통과했다. 최대 반환 시간은 약604.5ms로,350ms task 제한과 정리 대기가 구분되어 기록됐다. 자손은 이 유한 fixture의 자체 종료 절차로 정리했으며 이를 production 종료 보장으로 해석하지 않는다. kill EPERM은 실제 권한 오류가 아닌 주입 사례다.

로컬 SDK 헤더에서 NOTE_TRACK/NOTE_CHILD 미지원 표시를 확인했고, 개발자의 최소 C probe를 다시 빌드/실행해 kqueue 등록 ENOTSUP45를 재현했다. 이는 조사한 방법이 현재 환경의 경계를 제공하지 못한다는 근거다. macOS의 모든 가능한 방법을 배제했다는 결론은 아니다. 새로운 서비스/권한/VM을 도입하지 않은 범위 선택은 적절하다.

진단 capture는 전체 source/auxiliary와 delta를 보존하며 객체 identity·경로·profile 지문에 연결된다. 이 연결은 진단 출처 확인이고, OS 불변성이나 종료 인증이 아니다. 별도 known-reference 평가 entry는 trusted baseline에서 만든 참조의 전체 source bytes와 대조하고 결과를 `validTrialSubmission:false`로 남긴다. 실제 production 제출 성공 사례를 만들거나 허위로 주장하지 않았다.

## 회귀와 동결 검증

- `pnpm check`: **303테스트/15파일, skip0**, 타입 검사·예제 production build 통과. `pnpm experiment`: 기존 비교4/4 통과.
- 현재 runtime의 읽기 전용 교정 환경에서29제출을 새로 실행했다. 기존 v4의60파일과 gzip을 해제하고 wallTimeMs만 제외해 일치했다. reference/helper52/52·baseline 보존16/16·새 요구6/36,20동작 결함의 타입 통과 후 실패가 유지됐다.
- 기존 참조 source4,735파일을 새 diagnostic으로 수집해 제한된 known-reference CLI로 평가했다. 저장된 참조 평가와 시간 외 전체 필드가 일치했고, 새 delta 교정과 submissionId·52사례/요청/modal/종료 trace가 일치했다. 처음 비교 스크립트가 behavior의 wallTimeMs까지 비교한 차이는 시간만 제외하도록 바로잡았으며 구현 차이는 아니었다.
- 구현/테스트16파일 지문과 동결 증거41파일 hash를 확인했다. execution manifest의 전체 구현 hash와 자기 ID 계산을 검증하고 새 경로 재생성 결과의 bytes 일치도 확인했다. 배정9개는 모두 not-run이고 승인/결과는 채워지지 않았다.
- agent84파일 bytes를 manifest 및 수정 전 `ef60bc9`와 대조했다. baselineId/modelId/bundleId, B/C·TASK 의미, 제품 코어·S2 lib/평가기 구현의 불변을 확인했다. 변경 없는 공개 checker/환경 공급/A/B/C 접근의 기존 증거는 재사용 범위로 유지했다. 이번에 공개/private7제출과 전체 환경 복제를 다시 실행했다고 표현하지 않는다.

새 [검증 근거](evidence/2026-11-10-s2-runtime-review/)에 check/experiment 로그, 독립 usage/동결 감사, macOS raw matrix·판정, native probe 결과,29제출60파일 비교와 교정 요약, 참조 대조·실행 기록을 보존한다. 원시 참조 결과는 압축해 추가하며 과거 원시는 덮어쓰지 않는다. 실제 모델 호출/연결 시험·본 비교는0회다.

## 방향성과 다음 결정

제품 코어와 모델/조회 계층을 건드리지 않고 실험 내부의 종료·계측 경계를 보완했다. 불확실한 종료를 성공으로 표현하지 않고 구현 투자를 현재 범위에서 멈춘 것은 합의한 방향에 맞는다. 다만 이는 H-O 측정을 위한 준비 진전이며 모델의 수정 효용이나 FCA 기여를 입증한 결과는 아니다.

다음은 R12 재수정 지시가 아니라 **R11의 실행 경계 또는 허용 도구 정책을 사용자와 정할 단계**다. 현재 차단 구현에 후손 폴링을 더 붙이는 것으로 해결을 선언하지 않는다. 별도 작업 단위 격리와 subprocess를 제한한 도구 방식 등은 기존 도구 계약·준비/운영 비용이 달라 새 구조 합의가 필요하다. 이번 리뷰에서 어느 방식을 채택하거나 본 비교를 승인하지 않았다. C 사람 의미 동등성·업무 의미 승인과 실제 CLI 도구/인증/전역 지시/모델·자원 확인도 별도로 남아 있다.
