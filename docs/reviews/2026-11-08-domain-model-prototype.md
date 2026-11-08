# S1 도메인 모델 연결 실험 — 2026-11-08

**Vendure 취소·환불의 검토 대기 모델과 근거 검증, 동일 context의 단순 그룹/FCA 대조를 구현했다.** 78메서드×6속성은 한도 내에서 실행됐지만 FCA 후보 5개 모두 단순 그룹과 extent가 같다. 추가 교집합/새 업무 항목은 0개다. 이 표본에서 FCA의 추가 구축 가치는 관찰하지 못했으며 모델의 agent 효용은 아직 검증하지 않았다.

[개발 지시](2026-11-08-domain-model-next-plan.md)의 S1만 수행했다. 기준 main은 `41f7d680ac18b0cf2bcfc89976a59463a9ae1345`, 브랜치는 `codex/domain-model-prototype`이며 미병합 의존 브랜치는 없다. [실험 README](../../experiments/domain-model/README.md), [모델 사용 예](../../experiments/domain-model/v1/MODEL.md), [고정 manifest](../../experiments/domain-model/v1/manifest.json), [원문 고지](../../experiments/domain-model/SOURCE-NOTICE.md)를 참조한다.

## 모델과 관찰 계약

FCA 실행 전에 agent가 원문 근거 16개와 모델 12항목을 작성해 [model-before.json](../../experiments/domain-model/v1/model-before.json)에 보존했다. 개념 후보는 주문·주문 항목·결제·취소 요청·환불 요청이고, 나머지는 클라이언트 분기·dialog 결과/닫기·HTML 조건·service/GraphQL 전달·환불 경로의 조건부 취소 연결이다. 모든 항목은 pending-review이고 approvedKnowledge=[]다. intendedPolicy=null로 정적 소스 관찰과 의도한 업무 정책을 분리한다.

`cancelOrRefund`의 상태/active/settled 결제 분기, 직접 취소 경로의 결과 존재 확인, 환불 경로의 `input.cancel.lines?.length`와 `input.refunds.length`를 구분했다. 두 dialog `cancel()`의 인자 없는 `resolveWith()`는 주문 취소 요청이 아니다. HTML 두 근거·service mutation·GraphQL operation은 별도 fact다. 서버 정책·권한·실제 요청 성공·RxJS 도달 가능성을 추론하지 않는다. 현재 연결은 이미 소스/리뷰에서 알려졌고 직접 참조 검색으로도 찾을 수 있는 목적 표본이다.

원래 import closure를 타입 해석에 유지하면서 네 클래스의 자체 이름 있는 메서드 전체를 파생 FCA 객체로 정의했다. 개수는 상세 화면 28, 취소 dialog 6, 환불 dialog 12, service 32다. 생성자·접근자·필드 초기화·상속 메서드·callback 별도 객체·HTML·GraphQL을 제외했다. callback 내부 호출은 소속 메서드의 원문 영역에 포함한다. core의 중첩 함수 객체나 `scan.references`를 호출 그래프로 재사용하지 않았다.

속성은 정확한 심볼에 해소되는 cancel/refund service 호출, modal 열기, mutation 전달, dialog 결과 인자 반환/인자 없는 닫기 6개다. 직접 member CallExpression의 AST 역할과 심볼 선언 identity를 대조한다. 같은 이름의 다른 클래스 호출·선언/단순 참조는 해당 호출이 아니다. no는 이 한정된 직접 호출 계약에서의 부재이며 alias/간접 실행 부재를 증명하지 않는다. unknown은 false로 변환하지 않고 전체 FCA를 중단한다. 첫 개발 관찰 뒤 모호한 union 타깃을 unknown으로 다루는 경계를 부정 테스트로 보강했으며 객체·속성 선택/실제 incidence는 유지했다.

## 실제 결과와 FCA 기여

| 항목 | 결과 |
| --- | --- |
| 원문/준비 입력 | 원문 inventory 4,735항목 불변, 준비 Program 1,638파일 hash·현재 구성원 동일 |
| live 과업 진단 | 0개; 원래 설정의 과거 test 오류 495개는 별도 결과로 유지 |
| 파생 context | 78객체 × 6속성; 기본 128/64/256 유지 |
| 셀 | 468개: yes 43 / no 425 / unknown 0 |
| 단순 그룹 | 속성별 6개, 전체 공유 intent·동일 셀 근거 제공 |
| FCA | 형식 개념 8, 검토 후보 5, 관계 1, truncated=false |
| 추가 extent 교집합 | 0; 후보 5개 모두 단순 그룹과 동일 |
| 모델 전후 | 기존 2항목에 후보 근거 링크만 추가; 업무 항목/의미 변경 0 |
| 승인된 지식·agent 효과 | 승인 0; 효과 미측정 |

[후보별 검토](../../experiments/domain-model/verification/2026-11-08/fca-review.md)는 mutation 28메서드와 modal 8메서드의 넓은 기술 그룹, 두 dialog의 결과/닫기, 두 취소 호출 경로를 구분한다. 개수 휴리스틱만으로 업무 적합성을 확정하지 않았다. `refund-also-cancels`와 `dismiss`에 추가된 후보 참조는 기존 관찰을 정리하는 근거 링크다. 공유 속성/근거를 단순 그룹에도 제공했으므로 표시 정보량 차이를 FCA 계산의 효과로 세지 않는다. 관계 1개는 formal intent 포함이며 업무 상속·동일성·인과가 아니다.

이 결과로 H-F의 일반 효과를 반증하거나 H-O를 평가하지 않는다. 속성 선택에 이미 도메인 지식이 들어갔고 사람 작성/검토 비용을 측정하지 않았다. 이번에는 후보를 본 뒤 속성을 추가하거나 성공 메서드를 고르거나 상한을 높이지 않았다.

## 검증과 재현

validator는 모델/fact/candidate/item 참조·중복 ID·필수 출처와 범위·source hash/anchor·승인 기록의 형식을 검사한다. stale fact가 의존 모델/후보 및 관련 항목을 재검토 대상으로 만든다. 형식 검사를 통과해도 업무 의미가 참이거나 실제 사람이 승인했다고 인증하지 않는다.

- 새 회귀 27개: 동명 타깃, 선언과 호출, nested callback, nested class 제외, literal/computed 접근, any/union/missing target/diagnostics unknown, 변경·누락 근거·참조·승인 부정 사례.
- 실제 모델의 복제/메모리에 적용한 변조 8개를 모두 거부했다. source 변경은 12개 모델 항목을 stale로 식별했다. Vendure 원문은 수정하지 않았다.
- 같은 고정 cache에서 서로 다른 출력 경로의 **비시간 12파일 byte 일치**. `timing.json`만 제외한다. 관찰 경로는 상대 경로로 기록하며 설치/다른 플랫폼 독립 재현은 아니다.
- `pnpm check`: 타입 검사·9파일/163테스트·Vite production build 통과. `pnpm experiment`: 기존 비교 4/4, context 13×26·개념20/후보8/관계8·잘림 없음.
- 제품 core/CLI·논리 지원·strict/상한·의존성·기존 corpus·공개 앱/준비 원시 증거는 변경하지 않았다.

[검증 자료](../../experiments/domain-model/verification/2026-11-08)와 [원시 결과](../../experiments/domain-model/results/2026-11-08)에 정상/변조/재현/로그가 있다. cache가 없으면 모델·저장 facts 검토와 고정 archive 원문에 대한 validator 검사를 분리할 수 있으나 live compiler/심볼 재관찰은 미실행으로 표시해야 한다. 종료된 설치 예산을 재개하지 않는다.

## 비용과 다음 한 가지 권고

자동 runner는 첫 보관 실행 **3.033초**, 반복 **2.768초**다. 입력 무결성·컴파일·역할 판정·그룹/FCA·검증을 포함한다. 역할 6개 정의, 원문 설명 16개, 모델 12개, 후보 해석·S2 설계는 agent가 수동 작성했다. 468개 셀은 모두 자동 관찰했지만 모델이 자동 생성됐다는 뜻은 아니다. 사람 작성/검토/갱신 시간, agent token 사용량, 실제 변경·재작업·시간 개선은 null/미측정이다. 전체 수동 작성 시간과 모델 없는 대조 작성 비용은 계측하지 않았다.

다음 한 가지는 **S1 독립 리뷰 후 S2 pilot의 로컬 취소 reason 계약과 fixture/oracle를 동결**하는 것이다. [평가자 전용 초안](../../experiments/domain-model/evaluation/S2-PROTOCOL.md)은 직접 취소와 환불 중 취소 모두 nonblank trim reason을 적용하는 작은 가상 변경, 서버/schema 변경 경계, dismiss/환불만 경로의 보존, 고정 회귀 사례를 명시한다. 같은 agent의 코드+문서(A), 모델 추가(B), 동등 정보 일반 문서(C)를 별도 세션·반복/무작위 순서로 비교하고 작성/검토/재작업 비용을 함께 측정하도록 설계했다. 모델 제공 파일과 평가용 기대 변경·실패 조건은 분리했다.

아직 S2 비교·fixture 구현·실제 Vendure 변경을 하지 않았고 모델 의미의 사람 승인과 Gate 2~4는 미검증이다. 이 인계는 구현 세션의 자체 검토이며 독립 리뷰 결과가 아니다.
