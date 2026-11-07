# 실제 corpus 관찰 — 2026-11-07

**재현 가능한 실제 소스 2개와 코드 사실 라벨 24개를 준비했다. 사실 추출은 라벨 22개와 일치했고, 2개는 클래스 모델링 미지원으로 설명됐다. 하지만 함수 전체 비교는 선정 범위에서 한 건도 지원되지 않았다. 다음 한 작업은 사람의 과업 검토이며, 이 관찰만으로 새 문법 지원을 결정하지 않는다.**

## 고정 대상과 선택 편향

분석기 기준은 `c1a542c44b4e59f6be166c52036469e386de0188`이다. 이 작업에서 src/core, src/cli, 기존 지원 문법·한도를 수정하지 않았다. source/lockfile 및 실행 dist 해시는 [summary](../../experiments/corpus/results/2026-11-07/summary.json)에 있다. Node 22.19.0, TS 5.9.3, pnpm 11.19.0, 기존 @types/node 22.20.5를 사용했다.

| Corpus | Revision / 라이선스 | 수집·선정 범위 |
| --- | --- | --- |
| [p-queue](https://github.com/sindresorhus/p-queue/tree/7f272ab5ff2254c0dc2537b7977e88ede1cd55e8) | `7f272ab5` / MIT | 큐 상태·우선순위 처리를 위해 production TS 5개 모두 수집. main snapshot이며 release라고 주장하지 않음 |
| [date-fns](https://github.com/date-fns/date-fns/tree/313b902b9a72c64501074db9bc2b9897d2db5140) | `313b902b` (v4.1.0) / MIT | 요일 규칙 3개와 원래 local import closure 9개 파일 |

[manifest](../../experiments/corpus/manifest.json)에 전체 SHA, 파일별 hash·크기, 라이선스 고지 경로, 다운로드 URL, 원본/분석용 설정의 차이가 있다. 총 20개 파일에는 소스뿐 아니라 원래 tsconfig/package/license도 포함한다. 라이선스 고지는 별도로 보존했다. 원본 코드를 바꾸거나 실행하지 않았으며 새 패키지를 설치하지 않았다.

두 표본은 공개 utility library다. 실제 업무 애플리케이션·프레임워크·비공개 코드·큰 저장소 대표성이 없다. date-fns의 다른 함수/테스트/locale 구현/scripts는 제외했다. p-queue의 작은 범위는 전체 production 결과와 구분한다. 성공하기 쉬운 새 함수를 만들지 않았고, 모든 선택·24개 라벨·비교 2쌍을 첫 scan/FCA 전에 기록했다.

## 설정과 실패를 포함한 관찰

| 실행 범위 | 분석 파일 | 함수 predicate 지원 | 추출 condition 지원 | 단순 그룹 | FCA |
| --- | ---: | ---: | ---: | ---: | --- |
| p-queue 원래 config | 산출 실패 | 분모 없음 | 분모 없음 | 미실행 | 미실행 |
| p-queue production | 5 | 0 / 103 | 10 / 148 | 100 | 103객체·188속성, 기본 128/64 입력 상한 초과 |
| p-queue priority-queue | 4 | 0 / 15 | 0 / 28 | 16 | 15×31, 형식 개념 37·후보 23·관계 71, 잘림 없음 |
| date-fns weekday | 9 | 0 / 5 | 0 / 11 | 6 | 5×13, 형식 개념 8·후보 3·관계 2, 잘림 없음 |

p-queue 원래 tsconfig는 수집하지 않은 `@sindresorhus/tsconfig`를 extends하여 읽기에 실패했다. 이 실패를 지우지 않고 [raw failure](../../experiments/corpus/results/2026-11-07/p-queue-original-config-failure.json)에 남겼다. 별도 production 설정은 ES2022/NodeNext/strict/DOM과 현재 Node 22 타입을 명시했다. 원본 개발 의존성의 Node 26/TS 6 및 shared config를 재현한 upstream build가 아니다. 작은 구성요소 설정은 ambient types=[]로 scheduler를 제외하되 원래 local imports를 유지했다.

date-fns는 원래 설정을 extends하고 root 3개와 types=[]만 제한했다. 두 분석용 corpus의 모든 scan은 컴파일 진단 0개였다. 진단 때문에 모든 predicate가 거부된 결과가 아니다.

분모의 함수는 nested 함수·접근자·overload를 포함하는 FunctionFact 수다. p-queue 범위 둘은 겹치므로 합산하지 않는다. condition 지원 10건은 개별 식의 지원이며 함수 전체나 경로를 증명하지 않는다. 분석 files를 전체 저장소 coverage로 표현하지 않는다.

추출 omission은 production 11개(클래스 3·computed access 8), 작은 queue 7개(클래스 1·computed access 6), weekday 1개(computed access)다. 모든 위치·진단·거부 사유는 압축 raw scan과 summary에 보존했다. TypeChecker가 타입 문자열에 넣는 절대 import 경로의 현재 workspace 접두사는 출력에서만 `<workspace>/`로 치환했다. 초기 치환 전 관찰은 로컬 work에 보관하고, 공개 자료는 치환 정책을 고정해 두 번 다시 실행했다. 소스·offset·판정·수치는 바꾸지 않았다. FCA 상한은 그대로 유지했고 전체 실패 후 작은 범위 결과로 대체하지 않았다.

## 라벨·비교·검토 자료

[입력 라벨](../../experiments/corpus/labels.json)은 원본을 읽어 agent가 작성한 코드 사실 12개씩, 총 24개다. 선언 identity, 실제 참조 대상, 반환/분기 원문, 필드, 구조가 비슷한 서로 다른 선언을 포함했다. 고유 anchor/행/offset과 원본 SHA를 재검증하고 exact 위치의 fact를 대조했다. 결과 후보를 정답으로 삼지 않았다. 평가기에서 declaration self-reference가 사용 관계로 오인되지 않도록 보강했으며, 최초 관찰과 최종 판정 수치는 동일했다.

| 자동 판정 | 수 / 사전 라벨 24개 |
| --- | ---: |
| 코드 사실 일치 | 22 (p-queue 10, date-fns 12) |
| 명시적 미지원 | 2 (PriorityQueue 클래스 선언·#head 필드 모델링) |
| 누락 / 오연결 / 판정 불가 | 각각 0 |
| 사람이 검토한 라벨 | 0 |

22/24는 목적 표본의 라벨 추출 일치이며 전체 precision/recall이 아니다. 미지원 2개는 TypeFact/field 모델에 대한 라벨이다. 메서드의 property reference에 #head가 나타난다는 사실과 충돌하지 않는다. condition 원문이 추출돼 correct여도 normalization은 Unsupported일 수 있다.

[라벨별 결과](../../experiments/corpus/results/2026-11-07/labels.json)와 [사람 검토표](../../experiments/corpus/results/2026-11-07/review.md)에 원본 링크·주장·근거·판정을 연결했다. 업무 의미 후보는 별도 unreviewed, 승인 지식은 0개다.

사전 선정 비교는 isSaturday/isWeekend, isSunday/isWeekend 두 쌍이다. 같은 DateArg와 같은 옵션/context, 안정적인 날짜·시간대/context 동작을 전제로 명시했으나 둘 다 **Unsupported, 평가 0회**, 지원 0/2다. 숫자 비교, 함수 호출, optional 입력과 지역 변수/복수 문장이 현재 경계를 벗어난다. 반환된 첫 거부 사유 하나를 해결하면 전체 함수가 지원된다고 추정하지 않는다. 큐는 상태 변이·서로 다른 반환 의미 때문에 같은 입력의 순수 판정 쌍을 정당화하지 못해 비교하지 않았다. 반례나 정책 위반을 발견했다고 주장하지 않는다.

FCA와 같은 facts의 단순 type/property 그룹을 함께 저장했다. date-fns formal-3은 세 요일 함수를 묶지만 단순 getDay/in 공유 그룹에서도 같은 함수 집합을 찾을 수 있다. formal-0은 Date/DateArg를 공유하는 5개 함수 전체다. p-queue에는 RunFunction, Array, private state 공유로 넓은 그룹과 overload가 섞인다. 이 관찰은 후보의 의미적 유용성이나 FCA 순증분의 입증이 아니다.

## 비용·재현·검사

- 다운로드·hash 검증: 첫 준비에서 20개 파일, **4,773ms**. agent의 선정/설정/라벨 작성 노력과 사람 검토 시간은 **미측정**이다.
- 보존한 실행의 scan wall time: 원래 config 실패 7ms, production 566ms, 작은 queue 143ms, weekday 134ms. FCA는 각각 미실행/1ms(한도 거부)/3ms/1ms다. 단일 로컬 관찰이며 benchmark가 아니다.
- 같은 workspace/dependency layout에서 독립적인 두 scanner 실행의 **비시간 결과 14개 파일이 byte 단위로 일치**했다. [재현 기록](../../experiments/corpus/results/2026-11-07-reproduction.json). TypeScript 라이브러리 상대 경로를 포함한 ID이므로 다른 설치 레이아웃에 대한 재현 보장은 없다.
- `pnpm check`: 6개 테스트 파일 / **89개 테스트**, 코어·예제 타입 검사, production build 통과. 새 7개는 라벨 평가기의 identity 충돌·자기 참조·진단·누락·조건 추출/정규화 구분과 출력 경로 치환을 검증한다.
- `pnpm experiment`: 기존 인공 예제 비교 **4/4** 통과. 기존 결과·역사적 리뷰 증거는 수정하지 않았다.
- 제품의 지원 경계를 확장하지 않았고 임의 corpus 코드를 실행하지 않았다. 새 false proof를 관찰하지 않았다는 것이 전체 지원 경계의 추가 건전성 증명은 아니다.

재현 절차와 raw gzip 읽기는 [실험 README](../../experiments/corpus/README.md)에 있다. 자동 검사는 corpus 실패를 성공으로 바꾸지 않는다. 이 보고서는 구현 담당의 관찰·self-review이며 독립된 사람의 승인으로 표시하지 않는다.

## 다음 한 작업

**사람이 위 24개 코드 사실과 그룹 자료로 사용자 과업을 검토한다.** 관련 규칙 위치 찾기 / 후보 검토 / 조건 차이 설명을 검색·LSP/소스 읽기와 비교하고, 실제 시간·쓸모없는 그룹·오해·판단 보류를 기록한다. 현재 FCA는 날짜 corpus에서 단순 그룹과 같은 extent를 내며, 논리 비교는 0/2로 기능 확장 하나를 고를 유용성 근거가 부족하다. 숫자·호출·클래스 지원을 이번 관찰만으로 추천하지 않는다. Gate 2~4는 여전히 미검증이다.
