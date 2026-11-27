# 후속 변경 조사 범위

2026-11-27에 `git ls-remote --symref https://github.com/excalidraw/excalidraw.git HEAD`로 확인한 기본 브랜치는 master, 끝은 `dabd83c4aa6b9e42d0dd0a42be62200eb8e3cce9`이다. 첫 부모 이력에서 교정 커밋 `1161f1b8ba860a34602fc4aa211ea9f5b28c30eb` 직후부터 이 끝까지 조사한다. 동결 자료는 Ontosary `cc5a8d67e80b51efde14bddf0b7801e8d1cfd051`의 지우개 기록, Git blob `d2a5f20ed74f44cafa2873f94b558f5415cbb62d`이다.

이력을 부모부터 자식 순으로 보며, 제목이 아래 대소문자 무시 정규식에 맞거나 첫 부모와 비교해 `packages/excalidraw/eraser/` 아래를 변경한 커밋을 검토한다. 제목 검색으로 다른 모듈의 사용자 동작도 포함한다.

```text
eras(e|er|ing|ure)|free[ -]?(draw|hand)|pencil|pen pressure|stylus|pointer[ -]?(up|cancel)|small stroke|single[ -]?(point|dot)
```

각 후보는 직전 트리의 교정 커밋 포함 여부, 사용자 요구의 독립성, 동결 관계 한 가지가 구별하는 구체적인 판단, 전후 차이와 보존 장면의 독립 판정 가능성을 확인한다. 이식·되돌리기·같은 장면의 반복은 제외한다. 처음 모두 충족하는 건에서 멈춘다. 범위 안에 없으면 가장 가까운 사례와 탈락 이유를 남긴다.
