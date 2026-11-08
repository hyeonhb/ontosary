# 도식 관리

[사람을 위한 문서](../guide/README.md)의 그림을 관리한다. 원본은 `.mmd`이며 같은 이름의 `.svg`는 렌더링한 배포 파일이다. Markdown 본문에는 SVG를 넣어 Mermaid 지원 여부와 관계없이 읽을 수 있게 한다. 도식 자체를 다른 자료에 재사용할 때에도 개념/구현/설계 범위 설명을 함께 전달한다.

| 원본 | 설명 | 범위 |
|---|---|---|
| [idea-flow.mmd](idea-flow.mmd) | 코드 사실에서 해석·검토·모델 활용으로 이어지는 흐름 | 개념 설명 |
| [core-pipeline.mmd](core-pipeline.mmd) | 추출·정규화·FCA·논리 비교의 데이터 흐름 | 구현된 구조 |
| [model-evidence.mmd](model-evidence.mmd) | 탐색 연결과 사실·소스 근거의 차이 | S1을 바탕으로 한 읽기 예 |
| [s2-lifecycle.mmd](s2-lifecycle.mmd) | 준비 세션, 동결 모델, 조회 자료와 편집 코드 | 합의된 설계 |

## 갱신 방식

내용은 `.mmd`에서 바꾸고 SVG를 다시 생성한다. 생성된 SVG만 직접 고치지 않는다. 색상만으로 상태를 구분하지 않고 제목·노드·본문에도 의미를 쓴다. 각 원본의 `accTitle`/`accDescr`와 Markdown 대체 설명도 함께 갱신한다.

공통 서식은 [mermaid-config.json](mermaid-config.json)이다. 배경은 흰색, 기본 글꼴은 시스템 sans-serif다. 이미지에 별도 폰트 파일을 포함하지 않는다. 시스템에 설치된 한글 글꼴에 따라 줄 폭이 달라질 수 있으므로 렌더링 후 직접 확인한다.

## 재생성

확인한 렌더러는 **`@mermaid-js/mermaid-cli` 12.2.0 / Mermaid 12.3.0**, Node 22.19.0이다. Mermaid CLI는 문서 제작용이며 프로젝트의 런타임/개발 의존성이나 lockfile에는 추가하지 않았다. 설치/실행 방법은 [공식 Mermaid CLI 안내](https://github.com/mermaid-js/mermaid-cli)를 따른다. 아래 명령은 CLI 버전을 고정하지만 전이 의존성·브라우저·글꼴 차이까지 고정하는 픽셀 재현 환경은 아니다.

저장소 루트에서 다음 명령으로 생성할 수 있다. npm 실행 캐시에 도구를 설치하며 처음에는 도구/브라우저 다운로드가 발생할 수 있다.

```sh
for diagram in docs/diagrams/*.mmd; do
  stem=$(basename "$diagram" .mmd)
  npm exec --yes --package=@mermaid-js/mermaid-cli@12.2.0 -- mmdc \
    -i "$diagram" -o "docs/diagrams/$stem.svg" \
    -c docs/diagrams/mermaid-config.json \
    -b white --no-font-embed -I "ontosary-$stem"
done
```

이미 설치된 Chrome을 사용할 때는 도구 설치에 `PUPPETEER_SKIP_DOWNLOAD=true`를 적용하고, `executablePath`를 적은 로컬 JSON을 `-p`로 전달할 수 있다. 장비별 브라우저 절대 경로는 저장소에 커밋하지 않는다. 이번 생성은 그 방식으로 macOS Chrome을 사용했다.

그림마다 렌더링 성공, 한글 표시, 글자 잘림/겹침, 연결선과 화살표 방향, 좁은 화면에서의 가독성을 확인한다. 해당 안내 문서의 설명과도 대조한다. 렌더링 성공은 도식의 기술적 내용이 맞다는 검증을 대신하지 않는다.

## 내용 변경 시 확인할 것

핵심 아이디어의 역할은 [PRODUCT](../PRODUCT.md), 구현 경계는 [ARCHITECTURE](../ARCHITECTURE.md), 연구 주장은 [RESEARCH](../RESEARCH.md), 승인된 변경은 [DECISIONS](../DECISIONS.md)를 근거로 갱신한다. 설계가 구현되면 상태 표시와 [안내서의 확인 기준](../guide/README.md)을 함께 바꾼다.

도식은 날짜별 작업 지시나 완료 보고서가 아니다. 매번 새 사본을 늘리기보다 이 원본을 갱신하고 변경 이력은 Git에 남긴다. 과거 실험의 원시 증거와 리뷰 문서는 그대로 보존한다.
