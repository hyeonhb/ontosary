# S1 V2 · 탐색과 분석 입력 검증

최신 소비 경로는 V2다. V1 코드·모델·관찰/리뷰 증거는 보존한다. 모델 JSON의 업무 의미/relatedItems는 바꾸지 않고 incoming/outgoing 조회 계약을 추가했다. 추출·FCA는 V1을 재사용하며 새 결과의 기존 비시간 12파일도 V1과 같다.

## 실제 사용

```sh
pnpm build
node experiments/domain-model/v2/run.mjs /tmp/ontosary-vendure-preparation-20261108/vendure work/model-v2-a
node experiments/domain-model/v2/run.mjs /tmp/ontosary-vendure-preparation-20261108/vendure work/model-v2-b
node experiments/domain-model/v1/verify.mjs work/model-v2-a work/model-v2-b
node experiments/domain-model/v2/navigate.mjs work/model-v2-a/model-after.json cancel-request
node experiments/domain-model/v2/validate.mjs /tmp/ontosary-vendure-preparation-20261108/vendure work/model-v2-a
```

새 출력 경로만 사용한다. `navigate(model,id)`는 자기 fact/candidate 참조와 **한 단계** incoming/outgoing 경로를 반환한다. 각 경로는 `direction`, `declaredEdge`, 목적 항목의 kind/factRefs/candidateRefs를 갖는다. 전체 그래프 전이 폐쇄가 아니며 역방향 탐색을 업무 관계 대칭성으로 해석하지 않는다. 없는 ID는 found=false/CLI 종료1이다.

- order → branch: incoming, 선언된 링크는 branch → order.
- cancel-request → dialog-submit/cancel-transport/refund-also-cancels/dismiss: incoming.
- refund-request → refund-transport/refund-also-cancels/dismiss: incoming.

원문 fact ID를 facts.json.gz에서 찾아 파일/hash/offset/anchor를 확인한다. `refund-also-cancels`는 환불 경로의 조건부 취소 호출이고 `dismiss`는 두 dialog의 입력 없는 닫기다. 조회는 이 둘의 의미를 합치지 않는다. order에서 refund-transport 같은 전이 항목까지 자동 연결하지 않는다. 모델 밖의 추가 영향 경로도 따로 검색해야 한다.

## R7 전체 검사와 부분 검사

`inputs.mjs`는 V1 runner의 manifest/원문 inventory/준비 Program hash·구성원 및 live 진단 검사 로직을 V2 공통 함수로 옮겼다. V2 runner와 standalone validator가 이를 공유한다. 역사적 V1 runner 내부 guard는 보존되어 실행 시 중복 검사된다. 외부 의존성 설치/빌드나 원문 수정은 하지 않는다.

`validate.mjs`의 `anchorValid`는 V1 근거/참조/승인 형식 검사 결과이고, `analysisInputsValid`는 전체 입력 검사다. **둘 다 true일 때만 valid=true/exit0**이다. target 선언·설정·파일/의존 입력 변경 또는 누락이면 exit1/requiresReview=true다. 정확한 영향 계산 대신 자동 역할 fact 468개·candidate 5개와 전체 모델 12항목을 보수적으로 재검토시킨다. 업무 의미나 실제 사람 승인을 인증하지 않는다.

부분 원문만 있을 때 `--anchors-only`를 마지막 인자로 줄 수 있다. anchor가 모두 맞아도 `analysisInputsValid=false`, status=partial, valid=false/exit1이다. 이것은 전체 모델 사용 허가가 아니다. 입력이 사라지면 종료된 준비 예산을 재개하지 않는다.

원시 `validation.json`은 V1 anchor 결과로 보존하고 최신 전체 판정은 **validation-v2.json**에 둔다. 최신 소비 명령은 반드시 V2를 사용한다. [새 결과](../results/2026-11-08-v2), [CLI 변조·재현 증거](../verification/2026-11-08-v2), [제공 파일 목록](agent-input-manifest.json)을 참조한다. V2 비시간 15파일 재현이며 timing.json만 제외한다. V1 78×6·후보5/추가 의미0은 그대로다.

## 다음 단계의 경계

S2는 보완 독립 재검토 후 reason 계약·fixture/oracle·A/B/C 자료를 동결하는 별도 작업이다. 이 manifest는 S1 파일/hash 목록이며 격리된 S2 배포 묶음이 아니다. S2 실행 전 평가 자료 없는 별도 디렉터리/환경과 동등 정보 일반 문서를 실제로 만들고 확인해야 한다. 전체 Ontosary 저장소를 제공하며 exclude 목록만으로 격리를 주장하지 않는다. 알려진 사례의 pilot이고 사람 승인·agent 효용은 미검증이다. [원문 라이선스](../SOURCE-NOTICE.md)와 [평가자 전용 S2 초안](../evaluation/S2-PROTOCOL.md)은 유지한다.
