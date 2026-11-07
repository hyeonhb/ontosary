# 독립 리뷰 맥락

마지막 리뷰: 2026-11-07, Asia/Seoul. [최신 보고](2026-11-07-post-merge-review.md) · [현재 다음 작업 지시](2026-11-07-next-plan.md).

## 역할과 사용자 문제

이 세션은 구현과 분리된 Technical & Product Reviewer다. 도메인 이해·관련 규칙 탐색·근거 검토·지식 유지 비용이 줄어드는지 평가한다. 온톨로지/FCA/LLM은 수단이다. [PRODUCT](../PRODUCT.md)와 [RESEARCH](../RESEARCH.md)를 참조한다.

제품 소스·테스트·설정을 직접 수정하지 않는다. 검증 명령과 독립 재현을 수행하고 리뷰 파일 및 최신 진행 기록으로 인계한다. 과거 날짜별 보고·원시 증거는 덮어쓰지 않는다. 저장소 문서 반영은 최신 AGENTS/CONTRIBUTING의 지속 승인 절차를 따른다. 별도 개발 세션에 메시지를 보내는 권한으로 확대하지 않는다.

## 검토본과 상태 변화

- 2026-11-04: 커밋 없는 초기 PoC. [첫 보고](2026-11-04-poc-review.md), [fingerprint](evidence/2026-11-04-source-fingerprints.json). 기존 41개 테스트가 통과했지만 R1/R2의 false proof와 R3 파일 집계 문제를 확인했다.
- 2026-11-06: 구현 세션이 R1/R2와 R3를 수정하고 날짜별 개발 인계·증거를 추가했다.
- 2026-11-07: PR #1~#3가 병합된 `c6e0fc7babb28ac37fde6fdd68f416af7add8e78`에 독립 재검토. **R1/R2/R3 해결, 새 확인 결함 없음.** 초기 NEXT_PLAN은 이행된 과거 지시로 보존하고 새 지시는 날짜별 파일로 작성했다.

## 검증된 내용

- `pnpm check`: 5개 파일/82개 테스트, 타입 검사, 예제 production build 통과.
- `pnpm experiment`: 비교 4/4. 타입 6/함수 13, predicate 6 supported/7 unsupported, FCA 13×26/형식 개념 20/후보 8/관계 8.
- 기존 독립 probe 재실행: 144회 runtime/IR 대조, 256쌍/336개 반례, FCA 4×3 4,096행렬, 4,096/8,192 열거 경계 통과. [새 결과](evidence/2026-11-07-independent-results.json).
- 새 독립 probe: receiver 형태와 논리 중첩 36건 거부, explicit this 4건 거부, re-export/const enum/음수 numeric enum 등 12회 정상 실행값 대조와 3쌍 비교, 빈 JS/주석 JS/JSON 제외·CLI 일치. [스크립트](evidence/2026-11-07-boundary-check.mjs), [결과](evidence/2026-11-07-boundary-results.json).
- 코드 사실·후보·승인 지식 분리, 심볼 identity와 입력 assertion, 상한·한계 출력은 유지됐다. 원격 CI 성공을 주장하지 않는다. 검토 head의 check-runs/status 목록은 비어 있었다.

## 지적 추적

| ID | 현재 상태 | 판단 근거 |
| --- | --- | --- |
| R1 | 해결 | 직접 enum 선언 식별자만 상수 경로 허용. optional/call 등 Unsupported/평가 0/CLI 2 |
| R2 | 해결 | explicit this를 전체 predicate와 개별 condition에서 거부. 잘못된 argN 대응 제거 |
| R3 | 해결 | files와 실제 AST 순회 목록 일치, 제외 파일별 위치·이유, Program의 타입·진단 유지 |

원래 실패의 공통 원인은 지원 문법 아래 숨은 미지원 평가를 정규화가 건너뛰는 것이었다. 새 문법을 지원할 때 같은 유형의 오류와 실행 가능한 반례를 확인한다. enum namespace/값 별칭/explicit this의 미지원은 공개된 제한이며 현재의 새 결함으로 세지 않는다.

## Gate와 제품 가설

Gate 1은 **제한된 지원·검증 범위에서 통과**, 통제된 실제 corpus 실험 진행을 권장한다. 모든 TS 입력의 건전성 보장은 아니며 새 false proof가 나오면 재개방한다. Gate 2/3는 미검증, Gate 4는 부분 확인이나 통과 근거 부족, Gate 5는 미통과다.

FCA의 수학적 열거와 올바른 IR의 유한 비교에는 근거가 있다. FCA의 업무 의미 유용성, 일반 도구/LLM 대비 효과, 실제 도입·유지 비용은 아직 미검증이다. 정확성 수정만으로 이 상태를 올리지 않는다. 경쟁 도구 확인은 2026-11-04의 제한된 공식 문서 확인이며 이번에 새 시장/모델 평가를 하지 않았다.

## 바로 다음 작업과 판단 기준

[2026-11-07-next-plan.md](2026-11-07-next-plan.md): 공개/허가된 작은 TS corpus 2개와 20~30개 독립 코드 사실 라벨을 고정하고 coverage·오연결·미지원·한도 초과를 기록한다. 코어 지원 범위를 동시에 넓히지 않는다.

- 출력 후보를 정답으로 사용하지 않는다. agent 작성 업무 의미 후보는 unreviewed이며 사람 승인·검토 시간을 자동 테스트로 대신하지 않는다.
- 같은 facts의 단순 속성 그룹과 FCA의 순증분을 분리해 관찰할 자료를 준비한다. 검색/LSP와의 과업 비교도 후속 기준선이다.
- 분석에 성공하는 범위만 선택한 편향을 숨기지 않는다. files.length를 프로젝트 전체 coverage로 해석하지 않는다.
- 실제 사용자 과업·유지 비용 근거 없이 LLM·SMT·플러그인·승인 UI로 확장하지 않는다. FCA 순증분이 없으면 축소하고 반례 비교가 더 유용하면 그 과업으로 제품 범위를 좁힌다.
