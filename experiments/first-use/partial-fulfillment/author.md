# Vendure Admin UI 조사

이미 일부 품목을 출고한 주문에서, 운영자가 추가 출고를 시작할 수 있는지와 각 품목을 몇 개까지 출고할 수 있는지는 각각 어떻게 결정되나요? 두 판단의 관계를 주문 예 하나와 함께 설명해 주세요. 다음 개발자가 직접 확인할 수 있도록 근거를 남겨 주세요.

## 시작

이 디렉터리의 `vendure/`는 Vendure v3.5.0의 공개 소스 사본(`534e6003534f74761e82de1b8c6061cba89945d1`)입니다. 대상은 Angular Admin UI입니다. 평소 IDE와 검색을 사용하고, `ontosary/`의 CLI로 코드에서 추출한 사실이나 후보를 살펴볼 수 있습니다.

아래는 Ontosary README의 시작 절차를 이 사본에 맞춘 것입니다. 확인 버전은 Node.js 22.19.0, npm 10.9.3, pnpm 11.19.0입니다. 준비자가 설치·빌드를 마쳤다면 두 설치 블록을 건너뛰고 CLI 명령부터 실행하세요. 모든 블록은 이 안내 파일이 있는 디렉터리에서 시작합니다.

```sh
(cd ontosary && pnpm install --frozen-lockfile && pnpm build)
```

```sh
(cd vendure && npm ci --ignore-scripts --no-audit --no-fund --workspace=@vendure/admin-ui --workspace=@vendure/common --include-workspace-root && npm run build --workspace=@vendure/common)
```

```sh
(cd ontosary && pnpm --silent ontosary scan ../vendure/packages/admin-ui/ontosary.app.json --json) > scan.json
(cd ontosary && pnpm --silent ontosary concepts ../vendure/packages/admin-ui/ontosary.app.json --json) > concepts.json
```

`ontosary.app.json`은 원래 Admin UI 설정을 상속해 앱 소스를 분석합니다. 테스트 진입점과 spec은 제외합니다. `scan.json`에서 함수·참조·파일 위치와 진단을 검색하고, 위치는 설정이 있는 디렉터리 기준으로 원문과 대조하세요. HTML 템플릿도 IDE에서 열 수 있습니다. `concepts`는 함수의 공통 속성으로 FCA 후보를 찾습니다. 오류나 상한이 표시되면 터미널 메시지를 적고 가능한 도구로 조사를 이어가세요.

전체 JSON이 크면 다음 명령으로 함수 이름과 소스 위치만 검색할 수 있습니다. 마지막 문자열을 조사하면서 선택한 검색어로 바꾸세요.

```sh
node -e 'const s=JSON.parse(require("node:fs").readFileSync("scan.json")); for (const f of s.functions) if (f.name.toLowerCase().includes(process.argv[1].toLowerCase())) console.log(f.name, f.evidence.file, f.evidence.start.line)' '검색어'
```

## 제출

다음 개발자에게 넘길 짧은 자유 형식 기록을 `HANDOFF.md`로 남겨 주세요. 어떤 조건에서 설명이 성립하는지, 파일·심볼 또는 줄 위치, 수치가 있는 주문 예, 아직 확인하지 못한 점을 담아 주세요. 코드에서 본 동작과 업무 의도에 대한 추정을 구분해 주세요. 조직의 정책 승인은 미확인입니다.

진행자에게는 별도로 Vendure·Ontosary 사용 경험과 설정·조사·기록에 실제 쓴 시간을 알려 주세요. 핵심 근거를 어떤 검색이나 CLI 출력에서 처음 찾았는지, 이후 무엇으로 확인했는지, 관련 없는 후보에 쓴 노력도 짧게 적어 주세요. 도움을 받았다면 받은 시점과 내용, 그 전에 혼자 확인한 범위를 남겨 주세요. 도구가 기여한 부분이 없거나 측정하지 못한 항목도 그대로 적어 주세요.
