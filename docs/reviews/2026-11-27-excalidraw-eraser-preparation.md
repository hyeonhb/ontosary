# Excalidraw 자유 그리기 점을 지우는 동작의 전후 검산

**같은 드래그 뒤 대상 점은 병합 부모에서 남고 수정본에서 삭제됐다.** 경로에서 떨어진 점은 두 버전 모두 남았다. 수정 전 소스만으로도 자유 그리기의 생성·복원부터 지우개 후보 선택과 삭제 확정까지 네 관계를 기록할 수 있었다. 작성자가 지시문에서 작은 점과 전후 비교 목적을 보았으므로, 평가할 수 있는 것은 각 관계의 당시 근거까지다. 참가 모델 호출은 0회다. [준비 지시](2026-11-27-excalidraw-eraser-preparation-instructions.md) · [먼저 고정한 기록](https://github.com/hyeonhb/ontosary/blob/cc5a8d67e80b51efde14bddf0b7801e8d1cfd051/experiments/first-use/excalidraw-eraser/note.md)

## 같은 입력을 끝낸 뒤의 장면

Excalidraw 편집기를 기존 Vitest·jsdom 환경에 마운트했다. 마우스로 자유 그리기 도구를 고르고 (100, 100)과 (180, 160)을 각각 제자리에서 한 번 눌렀다 뗐다. 두 요소가 잠기지 않은 자유 그리기이고, 장면 좌표와 로컬 점열이 예상과 같으며 두 요소가 모두 지우개의 가시 후보에 들어가는지 확인했다. 지우개 도구에서 (80, 101)을 누르고 (120, 101)로 한 번 이동해 그곳에서 뗐다. 경로는 첫 점 중심에서 세로로 1만큼 떨어져 있고 두 번째 점과는 충분히 멀다.

| 장면 요소 | 예상 · 병합 부모 → 수정본 | 병합 부모 `204e06b` 해제 후 | 수정본 `1161f1b` 해제 후 |
| --- | --- | --- | --- |
| 대상 점 (100, 100) | 남음 → 삭제 | `isDeleted=false`, 살아 있는 장면에 있음 | `isDeleted=true`, 살아 있는 장면에서 빠짐 |
| 떨어진 점 (180, 160) | 남음 → 남음 | `isDeleted=false`, 살아 있는 장면에 있음 | `isDeleted=false`, 살아 있는 장면에 있음 |

뷰포트 800×600, 줌 1, 스크롤·오프셋 0, 획 두께 2, 회전 0, 누름 압력 0.5, 해제 압력 0, Alt 해제로 고정했다. 두 점의 로컬 점열은 모두 (0, 0)과 (0.0001, 0.0001)이다. 판정기는 원래 두 ID를 삭제 포함 장면에서 다시 찾고 삭제 플래그와 비삭제 장면의 멤버십을 대조한다. 한 버전에서만 통과시키는 테스트 분기는 없다. 첫 입력에서 차이가 나왔고 좌표 조정은 없었다. 이후 획 두께·각도·압력 모사 상태 단언을 추가하고 양쪽에 다시 적용했다. 새 아카이브 두 개로도 같은 네 관측을 재현했다. 실제 장치에서의 픽셀 렌더링, 다른 줌이나 펜의 감도는 측정하지 않았다. [동일 통합 테스트](../../experiments/first-use/excalidraw-eraser/probe.tsx) · [버전별 최종 상태](../../experiments/first-use/excalidraw-eraser/observations.json)

## 당시 알 수 있었던 관계와 사후에 확인한 구현

작성 시점은 PR 첫 커밋 `59df608`의 부모 `3bdaafe`다. 개발 세션이 당시 아카이브에서 일반 검색으로 App의 입력 처리, EraserTrail, 충돌 판정과 복원 테스트를 읽고, 확인한 소스의 해시와 기록을 `cc5a8d6`에 함께 고정했다. 그 뒤에 upstream PR과 병합 diff를 열었다. 기록은 입력 위치를 요소의 로컬 점으로 저장하는 관계, 제자리 해제 때의 끝점 보정과 작은 획 복원, 드래그 중 삭제 대기 ID 수집, 해제 때 실제 장면을 바꾸는 관계를 설명한다. 클릭은 해제 위치의 요소도 추가하므로, 드래그의 보존 동작을 검산하려면 두 입력을 구별해야 한다. 적정 접촉 거리와 장치별 허용 폭은 확인할 의도로 남겼다. [당시 파일·심볼·테스트별 근거](../../experiments/first-use/excalidraw-eraser/note.md) · [참조 파일 해시와 CLI 위치](../../experiments/first-use/excalidraw-eraser/source-check.json)

작성 때 Ontosary 공개 CLI의 패키지 범위 scan은 파일 370개, 함수 4,475개에서 `eraserTest`와 `intersectElementWithLineSegment` 위치를 재확인했다. 의존성을 설치하지 않은 사본에서는 진단 210개였고 concepts는 컴파일 오류로 종료했다. 기록 고정 뒤 저장소 밖 별도 사본에 당시 lockfile로 의존성을 설치하고 같은 명령을 재실행했다. 진단은 7개로 줄었지만 BufferSource·BlobPart·이벤트 타입 등의 오류가 남았다. 두 실행 모두 concepts의 종료 코드는 1, 표준 출력은 0바이트였다. FCA 열거·기본 상한 판정에 도달하지 않아 FCA 기여는 미측정이다. 분석에 사용한 Ontosary의 TypeScript는 5.9.3이고 당시 Excalidraw의 선언은 4.9.4다. 오류 전부의 원인을 버전 차이로 단정할 근거는 없다. [설치 후 진단 원문](../../experiments/first-use/excalidraw-eraser/installed-cli.json) · [CLI 오류 처리](https://github.com/hyeonhb/ontosary/blob/dd90a74/src/cli/index.ts#L22-L30) · [당시 패키지 설정](https://github.com/excalidraw/excalidraw/blob/3bdaafe4b5ecde577fe9b5c69a5d1819e37c4ccb/package.json#L37)

**사후 검산에서 확인한 사실.** 실제 병합은 `204e06b`를 유일한 부모로 두고 세 파일을 바꿨다. PR 설명에 나오는 점 중심 반경과 병합 코드에는 차이가 있다. 병합 코드는 자유 그리기의 렌더링 윤곽을 선분으로 바꿔 지우개 선분까지의 거리를 줌에 따른 허용치와 비교하고, 윤곽 내부도 검사한다. 줌 1에서 거리 허용치는 5다. 실험이 관찰한 값은 이 수정 전체를 적용한 편집기의 최종 장면이다. 개별 분기 기여와 다른 모양의 성능은 시험하지 않았다. 이 구현 설명은 작성자 기록과 분리해 보존한다. [upstream PR](https://github.com/excalidraw/excalidraw/pull/9946) · [단일 부모와 병합 diff](https://github.com/excalidraw/excalidraw/commit/1161f1b8ba860a34602fc4aa211ea9f5b28c30eb) · [병합된 지우개 판정](https://github.com/excalidraw/excalidraw/blob/1161f1b8ba860a34602fc4aa211ea9f5b28c30eb/packages/excalidraw/eraser/index.ts#L236-L267)

## 재실행과 소요 시간

아래 명령은 전체 SHA로 아카이브를 받아 독립 사본마다 같은 테스트를 설치한다. Node 22.19.0, Yarn 1.22.22, upstream Vitest 3.0.6을 사용했다. 두 사본의 yarn.lock SHA-256은 `033a69ccfaea9b182a18502b98899d361587e7cf8b100b6395cf1c5a24d286f6`으로 일치했다. 최초 준비에서 시스템 Yarn이 설정되지 않았고 Git 메타데이터가 없는 아카이브에서는 Husky 설치가 실패했다. 재현 명령은 고정한 Yarn을 npx로 실행하고 각 임시 사본에서 git init을 먼저 한다. 설치·테스트 오류 시 스크립트가 중단되며 결과 JSON 비교는 두 테스트가 끝난 뒤 수행한다. [재현 스크립트](../../experiments/first-use/excalidraw-eraser/replay.sh)

```sh
bash experiments/first-use/excalidraw-eraser/replay.sh
```

기록 자료는 아래 명령으로 준비했다. 저장소 루트에서 비어 있는 자료 디렉터리를 사용한다. scan은 컴파일 진단이 있어도 JSON에 확인된 위치를 쓰고 종료 코드 1을 낸다. 두 CLI 명령을 각각 실행한다.

```sh
mkdir -p work/eraser/source
curl -fsSL --retry 2 https://codeload.github.com/excalidraw/excalidraw/tar.gz/3bdaafe4b5ecde577fe9b5c69a5d1819e37c4ccb |
  tar -xz --strip-components=1 -C work/eraser/source
rg -n 'newFreeDrawElement|handleEraser|eraseElements|simulatePressure' work/eraser/source/packages/excalidraw/components/App.tsx
rg -n 'intersectElementWithLineSegment|imperceptibly' work/eraser/source/packages/{element/src/collision.ts,excalidraw/tests/data/restore.test.ts}
pnpm build
node dist/cli/index.js scan work/eraser/source/packages/excalidraw/tsconfig.json --json > work/eraser/scan.json
node dist/cli/index.js concepts work/eraser/source/packages/excalidraw/tsconfig.json --json > work/eraser/concepts.json
```

2026-11-27 한국 시각 기준 자료 다운로드는 20:14:53–20:15:01 약 8초, 자료를 읽고 CLI 결과·기록을 고정하기까지는 20:15:01–20:16:49 약 1분 48초였다. 고정 후 diff 검토와 테스트 준비·설치 문제 진단, 양쪽 첫 결과 확인은 20:19경까지 약 2분 10초였다. 추가 단언과 새 사본 재검산까지는 고정 시점부터 약 4분이었다. 최종 재현 스크립트 단독 실측은 로컬 패키지 캐시가 있는 환경에서 50.6초였다. 이 시간은 초기 설치 및 검산 시간과 구분한다. 저장소 검사는 `pnpm check` 299개 통과·기존 Vendure 캐시 의존 5개 건너뜀·빌드 성공, `pnpm experiment` 기존 비교 4/4였다.

세 소스 시점에서 원 라이선스의 내용과 해시가 일치했다. 원 저작권 표기는 Copyright (c) 2020 Excalidraw이며 MIT 고지를 함께 보관한다. 소스·의존성 사본은 재현 때 가져온다. [원 고지](../../experiments/first-use/excalidraw-eraser/LICENSE.excalidraw)

**동작 재현 판정**은 대상의 전후 차이와 대조 점 보존 모두 확인이다. **기록 작성 가능성 판정**은 수정 전 소스로 네 관계를 뒷받침할 수 있음이다. 사후 지식 없는 발견, 기록을 받은 동료의 변경 품질과 비용은 미측정이다. 공개 해법이 있는 교정 사례로 인계한다.
