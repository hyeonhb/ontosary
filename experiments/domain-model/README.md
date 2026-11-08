# S1 · Vendure 도메인 모델 연결 실험

2026-11-08 R6/R7 보완: **V2 구현·회귀 검증 완료, 독립 재검토 대기**. incoming/outgoing 한 단계 탐색과 전체 분석 입력/anchor 분리 검사를 제공한다. 모델 의미·78×6 context·후보5/추가 의미0은 유지한다. [최신 사용 경로](v2/README.md). S2는 미실행이다. 아래 리뷰/관찰은 당시 상태로 보존한다.

**검토 대기 모델 12개와 근거 검증·단순 그룹/FCA 대조를 구현했다.** 78메서드×6역할 속성에서 468셀(yes 43/no 425/unknown 0), 형식 개념 8개·후보 5개를 얻었다. 5개 모두 단순 그룹과 extent가 같으며 추가 교집합/새 업무 항목은 0개다. 이 목적 표본에서 FCA의 추가 구축 가치를 관찰하지 못했다. 모델 자체의 agent 효용 H-O는 S2에서 별도로 검증할 가설이다.

[요구사항](../../docs/reviews/2026-11-08-domain-model-next-plan.md), [인계 보고서](../../docs/reviews/2026-11-08-domain-model-prototype.md), [원문 고지](SOURCE-NOTICE.md).

## 입력과 계약

[v1/manifest.json](v1/manifest.json)에 첫 관찰 전 클래스/속성/부정·unknown 기준, revision·파일/설정 hash, 범위·한계·작성자를 고정했다. Ontosary 기준 main은 `41f7d680ac18b0cf2bcfc89976a59463a9ae1345`다. [model-before.json](v1/model-before.json)의 12항목과 [source-facts.json](v1/source-facts.json)의 새 원문 근거 16개를 FCA 전에 저장했다. 기존 11개 anchor를 현재 원문에 다시 대조하고 환불 경로/입력/닫기/요청 근거 5개를 추가했다. 과거 V1/준비 결과는 변경하지 않았다.

| 객체 범위 | 메서드 수 |
| --- | ---: |
| OrderDetailComponent | 28 |
| CancelOrderDialogComponent | 6 |
| RefundOrderDialogComponent | 12 |
| OrderDataService | 32 |

네 클래스의 자체 이름 있는 MethodDeclaration 전체(접근 제한/static 무관)를 포함했다. 생성자·접근자·필드 초기화·상속 메서드·익명 callback 별도 객체·HTML·GraphQL은 제외했다. callback/중첩 함수 안 호출식은 외부 메서드의 **원문 영역 내 출현**으로 집계하고 중첩 클래스는 제외한다. core의 중첩 함수 facts나 전체 호출 그래프와 다른 파생 계약이다. 기존 전체 Program 1,638파일은 타입/심볼 해석에 유지했다.

6속성은 정확한 `OrderDataService.cancelOrder/refundOrder`, `ModalService.fromComponent`, `BaseDataService.mutate`의 직접 멤버 호출식과 두 dialog의 `resolveWith`에 인자를 주는 호출/주지 않는 호출이다. 서비스의 선언 자체는 호출이 아니며 동명 타깃의 다른 심볼은 no다. optional 호출은 정적 출현만 의미한다. 두 dialog의 결과 입력 **구성 내용**은 수동 근거이지 속성의 자동 의미 분석이 아니다.

각 셀은 yes/no/unknown, 판정 방법, 파일/hash/offset/anchor를 갖는다. no는 완전한 메서드 영역에 해당 역할의 직접 호출식이 없다는 제한된 관찰이다. identifier alias 호출, call/apply, 간접·동적 실행은 계약 밖이다. matching member의 unresolved/any, 모호한 복수 타깃, nonliteral element call, 없는 body/target, 컴파일 진단은 unknown으로 보수 처리한다. 하나라도 unknown이면 incidence/FCA를 생성하지 않는다. 초기 개발 실행 뒤 ambiguous union의 unknown 처리를 부정 테스트로 보강했으며 객체/속성 선택과 Vendure incidence는 바뀌지 않았다.

기본 128객체/64속성/256개념을 그대로 사용한다. `buildContext`, core/CLI, 논리 지원을 바꾸지 않았다. 사전 역할 정의와 대상 자체가 이미 알려진 연결에 기반하므로 blind discovery/독립 표본이 아니다.

## 모델과 대조 결과 읽기

[읽기 안내/agent 사용 예](v1/MODEL.md)에서 개념 → 관련 동작 → factRefs → 원문 → 미확인 질문을 따라간다. 관찰 동작과 의도한 정책은 별도이며 intendedPolicy=null, 승인된 지식=[]다. 모델 전후의 유일한 차이는 이미 있던 `refund-also-cancels`와 `dismiss`에 후보 근거 링크를 붙인 것이다. [model-changes.json](results/2026-11-08/model-changes.json)은 업무 항목 추가/삭제 0을 명시한다.

같은 객체·속성·incidence에서 속성별 단순 그룹에도 전체 공유 intent와 동일한 셀 근거를 제공한다. 기존 core의 NextClosure로 전체 형식 개념을 열거하고 extent≥2/intent 비어 있지 않음으로 후보를 필터했다. [candidate-review.json](results/2026-11-08/candidate-review.json), [추가 검토](verification/2026-11-08/fca-review.md)에서 후보별 단순 그룹 동일성/과도한 그룹/업무 해석 보류를 읽는다. 관계 1개는 formal intent 포함 관계이며 업무 상속·인과관계가 아니다.

## 재현 및 검증

Node 22.19.0, TypeScript 5.9.3, pnpm 11.19.0. 기존 Ontosary 의존성으로 `pnpm build` 후 실행한다. upstream은 기존 준비 cache를 **읽기만** 한다. 원문 inventory 4,735개, 설정·과업 hash, 준비된 Program 1,638파일 hash와 현재 Program 구성원 전체 동일성을 확인하고 live 컴파일 진단 0을 확인했다. 정규 앱 설정의 기존 495 test 오류를 해소하거나 설치 예산을 다시 열지 않는다.

```sh
pnpm build
node experiments/domain-model/v1/run.mjs /tmp/ontosary-vendure-preparation-20261108/vendure work/domain-model-a
node experiments/domain-model/v1/run.mjs /tmp/ontosary-vendure-preparation-20261108/vendure work/domain-model-b
node experiments/domain-model/v1/verify.mjs work/domain-model-a work/domain-model-b
node experiments/domain-model/v1/validate-input.mjs /tmp/ontosary-vendure-preparation-20261108/vendure work/domain-model-a
node experiments/domain-model/v1/negative-check.mjs /tmp/ontosary-vendure-preparation-20261108/vendure work/domain-model-a
pnpm check
pnpm experiment
```

새 출력 디렉터리만 허용한다. 보관 결과의 [12파일 byte 재현](verification/2026-11-08/reproduction.json)은 시간 파일만 제외한다. 경로를 출력에서 제외하고 실제 입력의 파일 hash를 보존했다. 설치/다른 플랫폼의 독립 재현을 뜻하지 않는다. 준비 cache가 사라지면 runner는 입력 없음으로 실패하며 설치하지 않는다. 기존 고정 archive를 별도로 확보한 원문으로 validator를 실행하거나 저장된 facts/context/model을 검토할 수 있지만 live compiler/심볼 관찰은 생략 상태로 명시해야 한다. 저장 facts만으로 live 해석 성공을 꾸미지 않는다.

validator는 깨진 fact/candidate/item 참조, ID 중복, 필수 출처/범위/승인 메타데이터, source hash/anchor를 검사한다. 변경된 fact → candidate → model 및 관련 항목을 stale/재검토로 전파한다. 업무 의미를 판정하거나 실제 사람 결정자를 인증하지 않는다. 새 27개 회귀 테스트와 실제 모델에 대한 [8개 변조 검사](verification/2026-11-08/negative-cases.json)는 임시 fixture/복제/메모리만 바꾼다. upstream 원문은 그대로다.

## 비용·남은 판단

자동 runner는 첫 보관 실행 3.033초, 반복 2.768초다. 입력 검증·컴파일·셀·그룹/FCA·모델 연결·validator를 포함하고 모델 작성·테스트·문서·PR 시간은 제외한다. 468/468셀은 AST로 자동 판정했지만 역할 정의 6개·원문 설명 16개·모델 12개·후보 해석·S2 설계는 agent가 수동 작성했다. 이들을 섞은 자동화율이나 시간 절감률은 계산하지 않는다. 사람 작성/승인/유지 비용과 agent token 사용량은 null/미측정이다.

다음 권고는 **S1 독립 리뷰 후 S2 pilot의 입력 계약·고정 fixture/oracle를 동결**하는 것이다. [평가자 전용 S2 설계](evaluation/S2-PROTOCOL.md)는 baseline/model/동등 정보 일반 문서 조건, 오염 방지, 기대 변경/실패와 비용 측정을 다룬다. 이번에 Vendure를 수정하거나 agent 비교를 실행하지 않았다. Gate 2~4·사람 업무 의미 승인은 미검증이다.
