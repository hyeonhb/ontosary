# Ontosary

기존 TypeScript 코드에 흩어진 도메인 지식을 **근거와 함께 발견하고 검토**하기 위한 오픈소스 개발자 도구의 첫 PoC입니다. 프로젝트의 온톨로지 전환이나 코드 수정을 요구하지 않습니다.

현재는 정적 코드 사실 → FCA 형식 개념 후보 → 유한 입력에서의 조건 비교를 재현합니다. 후보는 비즈니스 사실이 아니며, 조건의 차이는 버그 판정이 아닙니다. LLM 대비 우수성이나 실무 생산성은 아직 검증하지 않았습니다.

## 시작

Node.js 22.12 이상인 22.x, 24.x 또는 26 이상, pnpm 11.19.0을 사용합니다. 검증 환경은 Node 22.19.0입니다.

```sh
pnpm install --frozen-lockfile
pnpm build
pnpm ontosary scan ./examples/react-vite --json
pnpm ontosary concepts ./examples/react-vite --json
pnpm ontosary compare ./examples/react-vite canConsultFromCard canConsultFromDetail --assume-same-input --json
```

`pnpm ontosary`는 저장소의 `ontosary` CLI를 실행합니다. `bin`도 `dist/cli/index.js`에 선언되어 있습니다. npm에는 배포하지 않았고 `private: true`입니다. 분석 결과는 기본적으로 JSON이며 `--json`은 명시용 옵션입니다. 프로젝트 경로 대신 개별 `tsconfig.json` 경로도 지원합니다.

대표 결과의 일부:

```json
{
  "status": "Implies",
  "equivalent": false,
  "leftImpliesRight": true,
  "rightImpliesLeft": false,
  "direction": "left-to-right",
  "counterexample": { "arg0.status": "reserved" },
  "evaluatedAssignments": 3
}
```

`arg0.status`는 첫 번째 매개변수의 `status`입니다. `--assume-same-input`은 양쪽의 같은 인자 순서와 속성 경로가 동일 입력을 의미한다고 사용자가 명시하는 전제입니다. 이름·타입 유사성만으로 이 전제를 추론하지 않습니다. 서로 다른 유한 도메인은 `Unknown`입니다. 이 플래그는 동일 업무 정책을 구현해야 한다는 주장이 아닙니다.

`Equivalent`는 양방향 함의, `Implies`는 한 방향만의 함의, `Different`는 양방향 모두 성립하지 않는 경우입니다. 비동치는 `equivalent: false`로 확인합니다. `leftOnly`/`rightOnly`는 각 방향의 반례입니다.

동명 함수는 오류로 보고하며 `scan`의 전체 함수 ID를 지정해야 합니다. 종료 코드는 0=결과, 1=인수·프로젝트·컴파일 오류, 2=Unknown/Unsupported입니다. `scan`은 컴파일 오류가 있더라도 진단과 사실을 출력하고 1로 종료합니다.

## 예제와 검증

```sh
pnpm example:dev       # 터미널에 출력되는 로컬 주소에서 React 예제 확인
pnpm check             # 코어/예제 타입 검사 + Vitest + Vite production build
pnpm experiment        # 고정 사례 검증 후 experiments/results/*.json 갱신
```

Vehicle → Listing → ConsultationRequest를 연결한 예제입니다. 매물 카드와 상세 UI는 의도적으로 다른 조건을 사용합니다. `reserved`에서 카드 버튼만 비활성화되며, `available`에서는 둘 다 활성화, `sold`에서는 둘 다 비활성화됩니다. 상담 요청은 메모리에만 저장됩니다.

테스트는 동명 심볼·import alias, 동치·반례·enum·미지원 문법, 입력 상한, CLI 오류, 실제 예제 함수와 IR 평가의 일치, 512개 3×3 Formal Context의 전수 대조를 포함합니다.

## 구조

| 경로 | 책임 |
| --- | --- |
| `src/core/analyzer.ts` | TS 프로젝트 읽기, 타입·함수·참조·조건·소스 근거 추출 |
| `src/core/logic.ts` | 제한된 논리 IR 및 유한 열거 비교 |
| `src/core/fca.ts` | Formal Context, NextClosure, 후보 필터·일반화 관계 |
| `src/core/model.ts` | JSON 데이터 계약 |
| `src/cli/index.ts` | 인수·출력·종료 코드 |
| `examples/react-vite` | React 실험 대상, 코어와 독립 |
| `tests`, `experiments` | 회귀 테스트·재사용 가능한 사례·결과 |

## 현재 한계

- `strictNullChecks`가 필요합니다. 타입 선언과 런타임 입력이 일치한다는 전제가 있습니다.
- 함수 전체 비교는 동기 함수의 단일 반환식만 지원합니다. 호출·별칭·변이·분기·비동기·기본 매개변수 처리는 미지원입니다.
- `===`, `!==`, `&&`, `||`, `!`, 문자열 리터럴 유니온 및 상수 enum을 지원합니다. 숫자 범위·일반 문자열·SMT는 미지원입니다.
- 입력은 직접 매개변수 또는 한 단계의 필수 속성입니다. 선택적·계산된·중첩 속성, getter, 객체 유니온은 미지원입니다.
- 필드는 안정적인 plain data이고 독립적이라고 가정합니다. 런타임 proxy, 숨은 상관관계, 업무 제약을 증명하지 않습니다.
- 기본 FCA 한도는 객체 128 / 속성 64 / 개념 256입니다. 후보는 최소 2개 함수와 타입·속성·조건 필드 중 1개 이상을 공유해야 합니다. 개념 상한에 걸리면 `truncated: true`이며 전체 격자가 아닙니다.
- 논리 비교는 최대 4,096개 입력 조합을 열거합니다. 상한 초과는 `Unknown`입니다.
- React 의미·Hook/Server 경계, 재귀 project references, 외부 선언·라이브러리 본문, 승인 워크플로는 구현하지 않았습니다.

상세 지원 범위는 [ARCHITECTURE](docs/ARCHITECTURE.md), 관찰과 미검증 가설은 [RESEARCH](docs/RESEARCH.md), 다음 작업은 [PROGRESS](docs/PROGRESS.md)를 확인하세요.

## 개발 맥락

[AGENTS](AGENTS.md) · [PRODUCT](docs/PRODUCT.md) · [ROADMAP](docs/ROADMAP.md) · [DECISIONS](docs/DECISIONS.md) · [DEPENDENCIES](docs/DEPENDENCIES.md)

Apache-2.0 License. 의존성에는 각자의 라이선스가 적용됩니다.

기여 시 [CONTRIBUTING](CONTRIBUTING.md)의 GitHub Flow와 Conventional Commits 규칙을 따릅니다.
