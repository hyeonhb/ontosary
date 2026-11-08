# S1 도메인 모델 독립 리뷰 — 2026-11-08

**목표와 방향은 맞고 정적 관찰 결과도 재현됐다. 다만 agent에게 제공할 탐색·검증 계약에 Medium 두 건(R6/R7)이 있어 S1을 조건부 완료로 판단한다.** 다음 한 작업은 이 두 계약의 보완이며, S2 비교 실행은 보완을 재검토한 뒤 진행한다. 제품 core의 새 결함이나 FCA 계산 오류를 발견한 것은 아니다.

## 검토 범위와 결과

- [개발 보고](2026-11-08-domain-model-prototype.md), [PR #15](https://github.com/hyeonhb/ontosary/pull/15), main `4480438b462609971cac35aea61e4aa0a2a95d6f`를 검토했다. PR head는 `0e62cacb396c15bd2a8a03224644459b8274f421`, 기준 main은 `41f7d680ac18b0cf2bcfc89976a59463a9ae1345`다.
- 모델 12항목·수동 원문 근거 16개·manifest·역할 관찰기·runner·validator·회귀·FCA raw·S2 설계를 읽었다. 제품 src/CLI·package/lockfile·기존 corpus·공개 앱 원시 자료는 변경되지 않았다.
- `pnpm check`: **9파일/163테스트**, 타입 검사·예제 production build 통과. `pnpm experiment`: 기존 비교 **4/4** 통과.
- 기존 준비 cache를 읽어 새 결과 디렉터리에 S1을 실행했다. **비시간 12파일이 저장 결과와 byte 일치**했다. 설치/다른 플랫폼 독립 재현은 아니다. runner의 원문 4,735항목·Program 1,638파일 검사 및 live 진단 0도 통과했다.
- 기존 변조 8개는 다시 거부됐다. 별도 독립 probe는 새로운 R6/R7을 재현했다. upstream 변경은 메모리 CompilerHost에서만 흉내 냈고 실제 파일은 보존했다.
- FCA는 코어 NextClosure를 쓰지 않는 **6속성의 64부분집합 완전탐색**으로 형식 개념 8개를 대조했다. 후보 5개의 extent와 단순 그룹·공유 intent가 모두 일치했다. agent 입력 manifest의 파일 hash 5개도 확인했다.

근거는 [독립 probe](evidence/2026-11-08-domain-model-review-check.mjs), [관찰 JSON](evidence/2026-11-08-domain-model-review-results.json)이다. 재현은 `node docs/reviews/evidence/2026-11-08-domain-model-review-check.mjs <준비된 Vendure root> [새 S1 결과 디렉터리]`다. 마지막 인자를 주면 저장 결과와도 대조한다. 이는 결함을 재현하는 리뷰 도구이며 exit 0은 S1 합격을 뜻하지 않는다.

## 수정이 필요한 발견

### R6 · Medium — 개념에서 동작으로 이동하는 계약과 모델의 링크 방향이 다르다

위치: `experiments/domain-model/v1/model-before.json:79`, 같은 `results/2026-11-08/model-after.json`의 링크, `v1/MODEL.md:17` 및 `:21`.

사용 안내는 `cancel-request → relatedItems → dialog-submit/cancel-transport/refund-also-cancels → factRefs`로 탐색하도록 한다. 실제 `cancel-request.relatedItems`에는 `order`, `line`만 있고, 관계 항목들이 반대로 `cancel-request`를 가리킨다. 문서화된 outgoing 링크를 순회한 독립 결과는 다음과 같다.

| 시작 항목 | 자신을 포함한 도달 항목 | 안내와의 불일치 |
| --- | --- | --- |
| order | order | branch로 이동 불가 |
| cancel-request | cancel-request, line, order | dialog-submit, cancel-transport, refund-also-cancels 모두 도달 불가 |
| refund-request | refund-request, payment, line, order | refund-transport, refund-also-cancels로 이동 불가 |

모델 전체를 읽거나 incoming 참조를 검색하면 관계를 찾을 수 있다. 따라서 지식 내용의 소실은 아니지만, 그 역방향 조회 계약/구현이 없고 안내대로 기계적으로 탐색할 수 없는 상태다. agent가 놓치기 쉬운 환불 경로를 모델로 발견하게 하려는 S1의 핵심 사용 경로를 약화한다.

권고: outgoing 링크를 보완하거나 **incoming 참조까지 조회하는 명시적 탐색 계약과 작은 조회 함수**를 제공한다. 탐색에서 양방향으로 찾는다는 의미와 업무 관계 자체가 대칭이라는 의미를 구분한다. 사용자 안내·JSON·실제 조회 결과를 맞추고 시작 개념에서 필요한 동작과 근거까지 도달하는 테스트를 둔다. 관련 없는 항목을 모두 연결하는 방식으로 통과시키지 않는다.

### R7 · Medium — 독립 validator가 역할 판정의 대상 선언 변경을 놓친다

위치: `experiments/domain-model/v1/validate-input.mjs:9`, `v1/validate.mjs:16`~`:24`. 원인은 `v1/observe.mjs:59`의 셀 evidence가 호출 위치/메서드 영역만 담고, 심볼 판정에 사용한 대상 선언/Program 입력을 이 검증 경로가 확인하지 않는 데 있다.

고정 소스의 `ModalService.fromComponent` 선언 이름만 메모리에서 바꿨다. 그 결과 저장된 `opens-modal`의 전제인 대상 선언이 없어졌다. 같은 수정 내용을 받는 fresh observer는 컴파일 진단을 별도로 전달하지 않아도 **78셀 모두 unknown**으로 바꾸며, live compiler도 오류를 보고했다. 하지만 저장 facts/model에 대한 `validateModel`은 해당 target 파일을 읽지 않고 **valid=true, staleFacts=[], staleItems=[], requiresReview=false**를 반환했다. 이 역할을 공유하는 `candidate:formal-5`는 모델의 `refund-also-cancels`에도 연결돼 있다.

**전체 `run.mjs`는 manifest/전체 Program 입력 hash를 확인하므로 이 변경을 거부한다.** 이번 고정 원문에서 저장 결과가 틀렸다는 발견은 아니다. 문제는 agent 안내가 별도 `validate-input.mjs`를 사용하게 하면서, 근거의 위치가 그대로라는 사실과 분석 전제가 유지된 사실을 구분하지 않는 점이다. 업무 의미 인증이 범위 밖이라는 설명으로 해결되는 문제도 아니다. 이미 주장한 정적 심볼 관찰의 입력 전제가 바뀐 경우다.

권고: 기존 전체 입력 검사와 standalone 검증의 계약을 연결한다. 현재 S1에서는 runner의 입력/Program 검사를 공유하는 작은 보완이 우선이다. 부분 원문만 있을 때는 anchor 검사 성공과 분석 입력 유효성을 별도로 표시하고 전체 검증 성공/재검토 불필요로 내보내지 않는다. 정확한 영향 전파가 어렵다면 관련 역할/candidate를 보수적으로 재검토시키면 된다. 일반 의미 분석기나 새 온톨로지 엔진은 필요 없다.

## 목표·방향 평가

**최종 목표에 한 단계 가까워졌다.** 기존에는 facts와 형식 개념 목록이었다. 이번에는 사람이 확인할 의미·모르는 부분·코드 근거를 한 자료로 묶고, agent가 사용할 변경 과업까지 연결했다. 모든 항목을 검토 대기로 두고, 관찰 동작과 의도 정책을 분리했으며, 취소/환불/닫기 차이를 보존한 것은 방향에 맞다. 현재의 결과는 수동으로 작성한 작은 도메인 모델 프로토타입이지 FCA가 온톨로지를 자동 생성한 제품이 아니다.

**FCA의 추가 가치가 관찰되지 않았다는 보고도 타당하다.** 역할 지지 집합은 mutation 28, modal 8, cancel 2, refund 1, 결과 반환 2, 닫기 2개다. 비어 있지 않은 속성 쌍 교집합은 cancel/refund/modal의 포함 관계 세 가지뿐이다. 나머지는 분리돼 있어 새로운 교차 묶음을 발견할 여지가 적다. 이 표본은 역할 context/근거 연결을 검증했지만, FCA가 복잡한 속성 조합에서 도메인 후보를 발견할 가능성을 강하게 시험한 표본은 아니다.

따라서 이 결과로 FCA를 제거하거나 상한/속성을 늘려 긍정 결과를 만들 이유는 없다. 먼저 H-O(모델의 agent 변경 효과)를 평가할 준비를 마친다. H-F(FCA의 구축 기여)는 별도 가설로 유지하되 작성·검토 비용을 측정하지 않은 현재를 시간 절감/품질 개선으로 표현하지 않는다. 자동 3초는 수동 역할·근거·모델 작성 비용을 포함하지 않는다.

S2 초안의 A(코드/기존 문서), B(모델), C(같은 정보를 담은 일반 문서) 분리는 적절하다. 다만 reason 변경이 이미 모델 사용 예와 대응하므로 알려진 사례의 pilot이라는 한계를 유지해야 한다. 실행 전 같은 정보를 담은 C 자료, 격리된 제공 파일 묶음, 원문과 의미가 맞는 fixture/oracle를 실제로 동결해야 한다. `exclude` 목록만 적고 전체 Ontosary 저장소를 제공하면 평가 자료가 숨겨지지 않는다. 이는 다음 준비의 조건이며 이번에 미실행된 S2의 결함 판정은 아니다.

## S1 완료 조건과 다음 작업

| 완료 조건 | 판정 |
| --- | --- |
| 모델·근거·출처·승인 구분 | 자료 존재/구분 양호. 탐색 계약은 R6 보완 |
| 취소·환불·닫기와 미확인 정책의 구분 | 원문/초안에서 확인. 업무 의미 승인 아님 |
| 같은 context의 단순 그룹/FCA·모델 전후 대조 | 재현 및 독립 수학 대조 통과. 추가 의미 0 |
| 변경 근거·잘못된 참조 탐지 | 기존 8변조 통과. 분석 입력 의존성 R7 보완 |
| 다음 과업/기준선·비용 구분 | S2 초안 있음. fixture·사람 검토·효용은 미완료 |

기존 core의 제한된 Gate 1 판정은 유지한다. S1의 agent 인계 계약은 R6/R7 보완 대상이고, Gate 2/3의 의미 품질·agent 효용은 미검증이다. Gate 4는 자동 실행 비용 관찰만 있으며 구축·유지 총비용은 미측정이다. Gate 5의 제품화 근거는 부족하다.

다음 한 작업은 [R6/R7 보완 지시](2026-11-08-domain-model-review-next-plan.md)다. S1 원시 결과를 보존하고 보완 결과를 새 버전/날짜로 남긴다. 독립 재검토 후 S2의 reason 계약·fixture/oracle 동결로 진행한다. 주요 제품 방향을 바꿀 근거는 이번에 발견하지 않았고, 모델 형식·FCA 투자·전체 코드 구조 전환의 큰 결정은 계속 사용자와 판단한다.
