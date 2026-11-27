# 지우개 기록의 후속 과업 후보 · 빠르게 가로지른 화살표

**Excalidraw #10006의 화살표 지우기 동작을 선정했다.** 동결 기록에는 지우개가 최근 두 위치 사이를 지나며 보이는 잠금 해제 요소를 삭제 후보에 넣는다는 관계가 있다. 이 관계로 같은 드래그에서 구별할 두 결과를 정할 수 있다. 두 포인터 표본 사이에 있는 일반 화살표는 손을 뗀 뒤 사라져야 하고, 함께 가로지른 독립된 잠긴 화살표는 남아야 한다. 지우개 장면의 전후 결과는 아래의 소스 기반 예측이다. [참가자에게 전달할 업무 요청](../../experiments/first-use/excalidraw-followup/request.md) · [upstream 변경 요청](https://github.com/excalidraw/excalidraw/pull/10006)

## 선정 경로

조사 전 기본 브랜치 master의 끝 SHA, 제목 검색어, 지우개 디렉터리, 첫 부모 순서와 중단 기준을 고정했다. 교정 커밋 직후부터 끝까지 첫 부모 커밋은 345개였고 제목 또는 경로 필터에 8개가 걸렸다. 첫 적격 후보까지 아래 두 건의 내용을 검토했다. [고정한 범위와 순서](https://github.com/hyeonhb/ontosary/blob/ff75f00e7fa09fd95c9e8b06d4c53e3b1a0393d2/experiments/first-use/excalidraw-followup/search.md)

| 순서 | 후보 | 판단 |
| --- | --- | --- |
| 1 | [#9979 자유 그리기 내부 판정](https://github.com/excalidraw/excalidraw/pull/9979) | 보류. PR은 이동 없는 클릭을 명시하지만 변경된 내부 검사는 궤적에 두 점이 있어야 호출된다. 누르기와 제자리 해제만 보내면 시작점 하나와 별도의 위치 조회로 끝난다. PR에서 설명한 입력으로 달라질 최종 장면을 확정할 수 없었다. [시작 시 한 점](https://github.com/excalidraw/excalidraw/blob/1161f1b8ba860a34602fc4aa211ea9f5b28c30eb/packages/excalidraw/animated-trail.ts#L96-L108) · [두 점 조건](https://github.com/excalidraw/excalidraw/blob/1161f1b8ba860a34602fc4aa211ea9f5b28c30eb/packages/excalidraw/eraser/index.ts#L72-L101) · [클릭 해제 경로](https://github.com/excalidraw/excalidraw/blob/1161f1b8ba860a34602fc4aa211ea9f5b28c30eb/packages/excalidraw/components/App.tsx#L9707-L9735) |
| 2 | [#10006 화살표 지우기 정밀도](https://github.com/excalidraw/excalidraw/pull/10006) | 선정. PR의 화살표 지우기 요구와 병합 코드의 빠른 이동 설명을 연결할 수 있다. 동결 기록의 후보 선정 조건이 빠른 횡단과 잠금 보존 검사를 모두 뒷받침한다. |

검토 기준 소스는 직전 `e32836f799b65f978cbf4877eab7ffc42c6e6494`, 직후 `a89a03c66ccbd3d44078be78a82d7adfb8f05953`이다. 전자는 교정 커밋 `1161f1b8ba860a34602fc4aa211ea9f5b28c30eb`의 후손이고, 후자는 전자를 유일한 부모로 하여 master에 들어갔다. 교정 과업은 아주 작은 자유 그리기 획을 지우는 것이었다. 이번 변경은 화살표·열린 선의 접촉과 곡선에서 얻는 선분을 바꿨다. PR에는 올가미 선택도 언급된다. 참가자 문구는 지우개 사용자의 요구에 한정했으며, 좌표·잠금 대조는 당시 코드에서 검토자가 구체화했다. [첫 upstream 커밋](https://github.com/excalidraw/excalidraw/commit/54ca52e0634970fab29abcafaebc1ae534c9eeed) · [병합 diff와 부모](https://github.com/excalidraw/excalidraw/commit/a89a03c66ccbd3d44078be78a82d7adfb8f05953)

## 기록에서 재사용할 판단

> 이동 시 마지막 두 장면 좌표로 만든 선분을 보이는 잠금 해제 요소에 검사한다.

동결 기록의 세 번째 관계다. 원문 blob은 `d2a5f20ed74f44cafa2873f94b558f5415cbb62d`다. 후속 변경 직전에도 EraserTrail은 최근 두 점으로 선분을 만들고 보이는 요소 중 잠긴 요소를 걸렀다. App은 이동 때 받은 ID를 삭제 대기 집합으로 바꾸고, 포인터를 뗀 뒤 해당 요소에 삭제 표시를 했다. 따라서 **포인터가 화살표 위에서 멈춘 사례만 검사하면**, 두 표본은 모두 화살표 밖이지만 그 사이가 몸통을 가로지르는 누락을 발견할 수 없다. 반대로 잠금 필터를 건너뛰고 교차하는 모든 요소를 지우면 같은 입력에서 보존할 화살표까지 사라진다. [동결 기록](https://github.com/hyeonhb/ontosary/blob/cc5a8d67e80b51efde14bddf0b7801e8d1cfd051/experiments/first-use/excalidraw-eraser/note.md) · [직전 선분과 후보 필터](https://github.com/excalidraw/excalidraw/blob/e32836f799b65f978cbf4877eab7ffc42c6e6494/packages/excalidraw/eraser/index.ts#L86-L105) · [삭제 대기](https://github.com/excalidraw/excalidraw/blob/e32836f799b65f978cbf4877eab7ffc42c6e6494/packages/excalidraw/components/App.tsx#L6327-L6339) · [장면 반영](https://github.com/excalidraw/excalidraw/blob/e32836f799b65f978cbf4877eab7ffc42c6e6494/packages/excalidraw/components/App.tsx#L10065-L10085)

**시점에 따라 달라진 사실도 있다.** 기록 작성 당시 자유 그리기는 일반 교차 함수를 거쳤다. 후속 변경 직전에는 이미 #9946의 획 윤곽·줌 허용 거리와 #9979의 내부 판정을 사용했다. 또한 화살표의 개별 접촉 판정은 후보 선분을 받아도 그 한쪽 좌표와 화살표의 거리만 검사했다. 동결 문장을 “모든 요소가 이미 경로 전체와의 교차를 검사한다”로 읽으면 바로 이 결함을 놓친다. [직전 자유 그리기·화살표 분기](https://github.com/excalidraw/excalidraw/blob/e32836f799b65f978cbf4877eab7ffc42c6e6494/packages/excalidraw/eraser/index.ts#L236-L278)

## 검토자용 판정 장면

줌 1, 장면 오프셋·스크롤 0에서 수평인 직선 화살표 두 개를 둔다. 일반 화살표 A는 (100, 100)→(220, 100), 잠긴 화살표 B는 (100, 115)→(220, 115)다. 둘 다 획 두께 2, 거칠기·회전 0, 그룹·프레임·결합 텍스트가 없고 화면 안에 있다. Alt 없이 지우개로 (160, 70)을 누른 뒤 **중간 표본 없이** (160, 140)으로 한 번 이동하고 같은 곳에서 뗀다. 이 장면은 손의 속도 대신 편집기가 받는 입력 두 위치를 고정한다.

| 해제 뒤 확인할 ID | 변경 직전 예상 | 수정본 예상 | 근거 |
| --- | --- | --- | --- |
| A · 두 위치 사이의 일반 화살표 | 남음 · isDeleted=false | 삭제 · isDeleted=true | 직전에는 검사하는 표본이 몸통에서 30만큼 떨어져 허용 거리 4를 넘는다. 수정본은 드래그 선분과 몸통 선분이 교차해 거리가 0이다. |
| B · 같은 드래그가 가로지른 잠긴 화살표 | 남음 · isDeleted=false | 남음 · isDeleted=false | 두 버전 모두 직접 접촉 후보에서 잠긴 요소를 제외한다. 그룹 등 다른 ID를 통해 함께 지워질 조건도 없다. |

제3자는 두 요소를 같은 장면에 넣고 위 이벤트를 두 리비전에 그대로 보낸 후, 원래 ID별 삭제 플래그와 비삭제 장면 포함 여부를 확인하면 된다. 손을 뗀 위치는 시작점과 달라 클릭 전용 추가 조회를 타지 않는다. 위 좌표의 **지우개 통합 동작은 미실행**이며, 이전 자유 그리기 교정 결과를 이 화살표의 관측값으로 사용하지 않았다. [직전의 한 좌표와 거리 비교](https://github.com/excalidraw/excalidraw/blob/e32836f799b65f978cbf4877eab7ffc42c6e6494/packages/excalidraw/eraser/index.ts#L268-L278) · [수정본의 선분 거리 비교](https://github.com/excalidraw/excalidraw/blob/a89a03c66ccbd3d44078be78a82d7adfb8f05953/packages/excalidraw/eraser/index.ts#L270-L288) · [거리 함수의 교차 처리](https://github.com/excalidraw/excalidraw/blob/a89a03c66ccbd3d44078be78a82d7adfb8f05953/packages/math/src/segment.ts#L181-L194) · [해제 시 클릭과 드래그 구분](https://github.com/excalidraw/excalidraw/blob/e32836f799b65f978cbf4877eab7ffc42c6e6494/packages/excalidraw/components/App.tsx#L9719-L9747)

**실행한 기존 검사.** 이 변경은 올가미가 공유하는 선분 계산도 수정했다. 각 리비전의 별도 사본에서 동일한 기존 올가미 테스트를 실행해 각각 6/6 통과했다. 이 파일은 선형 요소를 하나 선택하는 사례 등을 검사하며 지우개 해제 이벤트는 보내지 않는다. 두 리비전의 테스트 파일 blob은 `d84ce1ffb9fe629beae768f8f2a89a2dda6f2b2f`다. [공유 선분 구성](https://github.com/excalidraw/excalidraw/blob/a89a03c66ccbd3d44078be78a82d7adfb8f05953/packages/element/src/bounds.ts#L312-L365) · [기존 올가미 검사](https://github.com/excalidraw/excalidraw/blob/a89a03c66ccbd3d44078be78a82d7adfb8f05953/packages/excalidraw/tests/lasso.test.tsx#L877-L920)

각 upstream 체크아웃의 루트에서 다음 명령을 실행했다. Git 메타데이터가 없는 아카이브라면 첫 설치 전에 그 사본에서 `git init -q`를 실행한다.

```sh
npx --yes --package=yarn@1.22.22 -c 'yarn install --frozen-lockfile --non-interactive'
./node_modules/.bin/vitest run packages/excalidraw/tests/lasso.test.tsx
```

이력 확인은 upstream 저장소에서 아래와 같이 재현할 수 있다. 제목 필터는 [사전 기록](../../experiments/first-use/excalidraw-followup/search.md)의 정규식을 쓰고, 지우개 경로 이력과 합친 뒤 첫 명령의 순서로 읽었다.

```sh
span=1161f1b8ba860a34602fc4aa211ea9f5b28c30eb..dabd83c4aa6b9e42d0dd0a42be62200eb8e3cce9
git log --first-parent --reverse --format='%H %s' "$span"
git log --first-parent --full-history --format='%H' "$span" -- packages/excalidraw/eraser/
git merge-base --is-ancestor 1161f1b8ba860a34602fc4aa211ea9f5b28c30eb e32836f799b65f978cbf4877eab7ffc42c6e6494
git show -s --format='%H %P' a89a03c66ccbd3d44078be78a82d7adfb8f05953
```

참가 모델 호출은 0회다. 이번 선정으로 확인한 것은 동결 기록에서 구체적인 회귀 판단을 끌어낼 수 있다는 점이다. 기록이 실제 작업자의 판단이나 비용을 개선하는지는 미측정이며 선정 결과 리뷰로 인계한다.
