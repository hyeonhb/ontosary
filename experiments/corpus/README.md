# Real-source observation corpus

**현재 평가기는 [V3](v3/README.md)이며 V2 라벨 계약을 그대로 사용한다.** `pnpm experiment:corpus <새 경로>`는 V3, `experiment:corpus:v2`와 `experiment:corpus:v1`은 각 역사적 버전이다. V2는 R4를 보완했지만 타입 선언 이름을 사용으로 인정하는 R5 잔여 오류가 있어 V3가 조상 문맥 판정을 보완했다. 아래 2026-11-07 기록은 V1 관찰로 읽으며 `correct`를 자연어 주장 전체의 검증으로 확대하지 않는다.

2026-11-07의 [개발 인계](../../docs/reviews/2026-11-07-next-plan.md)를 실행한 자료다. 코어 기능을 바꾸지 않고 공개 TypeScript 소스의 사실 추출·지원 경계를 관찰한다. [관찰 보고서](../../docs/reviews/2026-11-07-corpus-observation.md), [사람 검토표](results/2026-11-07/review.md), [기계 요약](results/2026-11-07/summary.json)을 먼저 읽는다.

## 입력과 범위

- `manifest.json`: 두 repository의 정확한 revision, MIT 라이선스, 20개 다운로드 파일의 SHA-256/크기, 원래 tsconfig와 분석용 config 내용, 선택 이유. 소스는 수정하거나 실행하지 않는다.
- `labels.json`: **첫 scan/FCA 전에 원문을 읽어 작성한 24개 코드 사실 라벨**. 고유 anchor·원본 행·offset을 실행 전에 검증한다. agent 작성이며 사람 검토는 모두 pending. 업무 의미 후보 2개는 별도 unreviewed, approvedKnowledge는 비어 있다.
- `tasks.json`: 분석 전 선정한 날짜 비교 2쌍과 명시적 동일 입력 전제. 큐에는 적절한 순수 predicate 쌍을 선정하지 못해 비교를 강제하지 않는다.
- `analyzer-fingerprints.json`: 기준 `c1a542c`의 코어 소스와 lockfile 해시. 변경된 분석기로 같은 실험 이름을 재사용하지 못하게 검사한다. 실제 dist 해시도 결과에 남긴다.
- `licenses/`: 두 원본 MIT 저작권·허락 고지. Ontosary의 Apache-2.0과 별개다. 원본 소스는 라이선스와 함께 무시되는 `work/corpora/`에 다운로드한다. 원시 결과의 소스 인용에도 이 고지가 적용된다.

p-queue는 production 소스 5개 전체를 수집하고, 원래 설정 → 명시적 설정의 production → priority-queue 구성요소 범위를 미리 정했다. 원래 공유 tsconfig 패키지를 설치하지 않은 실패도 보존한다. 분석용 production 설정은 현재 Ontosary의 Node 22 타입을 사용한다. 원본이 개발 의존성으로 선언한 Node 26/TS 6 설정과 같다고 주장하지 않는다. priority-queue는 scheduler를 제외하고 원래의 local import 관계를 따라 4개 파일을 분석한다.

date-fns v4.1.0은 isSaturday/isSunday/isWeekend 세 함수를 root로 하고 local import closure 9개 파일을 그대로 가져왔다. 원래 tsconfig를 extends하고 include/files와 ambient types만 제한했다. 다른 날짜 함수, locale 구현, 테스트, scripts는 수집하지 않았다. 두 라이브러리는 작은 규칙·상태 코드라는 목적 표본이며 업무 애플리케이션 대표 표본이 아니다.

## 재현

저장소 루트에서 기존 lockfile의 의존성을 설치한 환경을 사용한다. 새 runtime 의존성이나 원본 프로젝트의 의존성·스크립트 실행은 필요 없다. 최초 준비는 raw.githubusercontent.com에 접속한다. 다운로드한 파일은 매 실행에서 hash 검증하며 변조된 cache를 자동 덮어쓰지 않는다.

```sh
pnpm install --frozen-lockfile
pnpm experiment:corpus:prepare
pnpm experiment:corpus:v1 work/corpus-run-a
pnpm experiment:corpus:v1 work/corpus-run-b
node experiments/corpus/verify-reproduction.mjs work/corpus-run-a work/corpus-run-b
```

출력 경로는 **존재하지 않는 새 디렉터리**여야 한다. 과거 결과를 덮어쓰지 않는다. 환경까지 같으면 저장된 `experiments/corpus/results/2026-11-07`과도 비교할 수 있다. `timings.json`만 비결정적이라 재현 비교에서 제외한다. 같은 workspace에서 두 번 실행한 14개 나머지 파일의 byte 일치는 `results/2026-11-07-reproduction.json`에 있다. pnpm/TypeScript 설치 레이아웃이 다르면 외부 Date/Array/Node 타입의 상대 경로 ID가 바뀔 수 있다. 이것은 경로 독립 재현 검증이 아니다.

원시 scan/FCA/단순 그룹은 JSON을 gzip으로 무손실 압축했다. TypeChecker의 타입 문자열에 섞이는 현재 workspace 절대 경로 접두사만 출력 시 `<workspace>/`로 치환한다. 원본 소스·offset·판정은 바꾸지 않는다. 개별 파일은 다음처럼 확인한다.

```sh
node --input-type=module -e 'import fs from "node:fs"; import {gunzipSync} from "node:zlib"; console.log(JSON.stringify(JSON.parse(gunzipSync(fs.readFileSync(process.argv[1]))), null, 2))' experiments/corpus/results/2026-11-07/date-fns-weekday-concepts.json.gz
```

## 지표와 판정 계약

- files는 실제 분석한 구현 파일 목록이다. 전체 저장소의 파일 수나 coverage 비율이 아니다.
- predicate 분모는 각 실행의 모든 FunctionFact다. nested 함수·접근자·본문 없는 overload도 포함하며 exported 업무 규칙만 세지 않는다. p-queue 두 범위는 겹치므로 합산하지 않는다.
- condition 분모는 추출된 condition 수다. 누락된 조건까지 포함한 총수나 분기 경로의 의미를 나타내지 않는다.
- 라벨 분모는 사전 선정 24개다. 선언 위치와 identity, 참조 대상, condition 원문을 대조한다. correct는 **코드 사실 추출**의 일치이지 논리 정규화 지원이 아니다. V1은 자기 선언을 제외하려 했으나 실제 함수 이름/선언의 서로 다른 offset 때문에 R5가 재현됐다. 이 계약은 V2의 실제 AST 사용 위치 검사로 보완했다.
- correct / missing / mislinked / unsupported / indeterminate를 구분한다. 해당 위치의 명시적 omission은 unsupported, 근거 없는 부재는 missing, 컴파일 오류·모호성은 indeterminate다. 기대 edge 부재만으로 잘못된 다른 edge를 단정하지 않는다.
- 사전 비교 과업은 2쌍이다. 각 결과·전제·근거를 따로 보존한다. 확정 상태인 Equivalent/Implies/Different만 supported pair로 센다.
- 컴파일 진단, omission 사유, predicate 거부 사유, FCA 한도 초과, 결과 잘림은 별도 필드다. 원래 config 실패에는 성공 파일/함수 분모를 만들지 않는다.
- 단순 기준선은 같은 facts에서 각 type/property를 공유하는 2개 이상 함수 그룹이다. FCA의 폐포·복합 intent와 비교할 검토 자료이며, 후보 수가 많다고 품질 점수를 주지 않는다. 검색/LSP baseline과 사람 시간은 아직 측정하지 않았다.

연구상 실패는 runner 오류와 다르다. scan 실행 예외/FCA 입력 상한은 실패 관찰로 저장한다. hash/anchor 불일치와 scan 외 처리 단계의 예상하지 못한 오류는 runner 실패다. 네트워크 없는 평가기 회귀 검사는 `tests/corpus-evaluation.test.ts`에 있다. 측정 자동화의 회귀 검사를 제품의 의미적 유용성 검증으로 해석하지 않는다.
