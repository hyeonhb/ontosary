# Excalidraw 화살표 지우기 변경에서 기록을 전달한 결과

**동결 기록을 받은 C는 2/2, 공통 소스만 받은 A는 1/2, 같은 내용을 서술형 문서로 받은 B는 1/2 완전 성공했다.** 제출된 네 패치는 모두 두 장면과 올가미 6건을 통과했다. 성공 수의 차이는 다음 호출이 차단되기 전에 첫 패치를 제출했는지에서 생겼다. A도 자료 없이 같은 편집기 동작을 구현했고, 미제출 두 건의 숨은 장면 결과는 관측하지 않았다.

## 제출과 편집기 동작

직전 소스에서 (160, 70)에 포인터를 누르고 중간 표본 없이 (160, 140)까지 이동해 뗐다. 일반·잠금 화살표를 함께 둔 장면과 경로 밖 화살표를 추가한 장면을 각각 실행했다. 직전본에서는 두 장면 모두 일반 화살표가 남았고 기준 수정본에서는 두 장면 모두 지워졌다. 잠금·경로 밖 화살표는 해당하는 모든 장면에서 남았다. 올가미는 양쪽 6/6이었다. 다음 표의 ‘삭제’는 원래 ID의 삭제 플래그 true와 비삭제 장면에서의 제외를 모두 뜻하고, ‘보존’은 플래그 false와 장면 포함을 뜻한다. [직전본 관측](../../experiments/first-use/excalidraw-arrow-comparison/observations/original.json) · [기준 수정본 관측](../../experiments/first-use/excalidraw-arrow-comparison/observations/reference.json)

| 배정 순서 | 첫 제출·적용 | 경로 안 일반 (두 장면) | 잠금 (두 장면) | 경로 밖 (세 요소 장면) | 올가미 | 독립 판정 |
| --- | --- | --- | --- | --- | ---: | --- |
| C1 | [첫 패치](../../experiments/first-use/excalidraw-arrow-comparison/observations/8369fe26da/first.patch) 적용 | 삭제 | 보존 | 보존 | 6/6 | [완전 성공](../../experiments/first-use/excalidraw-arrow-comparison/observations/grades/8369fe26da.json) |
| A1 | [첫 패치](../../experiments/first-use/excalidraw-arrow-comparison/observations/bd89a84cc4/first.patch) 적용 | 삭제 | 보존 | 보존 | 6/6 | [완전 성공](../../experiments/first-use/excalidraw-arrow-comparison/observations/grades/bd89a84cc4.json) |
| B1 | [입력 한도·미제출](../../experiments/first-use/excalidraw-arrow-comparison/observations/9e69be050c/seal.json) | 미실행 | 미실행 | 미실행 | 미실행 | 미제출 |
| A2 | [입력 한도·미제출](../../experiments/first-use/excalidraw-arrow-comparison/observations/cc0fde7f8d/seal.json) | 미실행 | 미실행 | 미실행 | 미실행 | 미제출 |
| B2 | [첫 패치](../../experiments/first-use/excalidraw-arrow-comparison/observations/b189cc3b88/first.patch) 적용 | 삭제 | 보존 | 보존 | 6/6 | [완전 성공](../../experiments/first-use/excalidraw-arrow-comparison/observations/grades/b189cc3b88.json) |
| C2 | [첫 패치](../../experiments/first-use/excalidraw-arrow-comparison/observations/001e08a5f9/first.patch) 적용 | 삭제 | 보존 | 보존 | 6/6 | [완전 성공](../../experiments/first-use/excalidraw-arrow-comparison/observations/grades/001e08a5f9.json) |

## 조사에서 확인한 판단

- **첫 묶음 C와 A**는 각각 두 포인터 표본 사이를 한 번 이동하는 테스트를 먼저 만들었다(C 8번째, A 11번째 응답). 일반 화살표가 남아 단언이 실패했지만 처음에는 테스트 장면의 크기도 원인이었다. C는 앱 가시 영역을, A는 DOM 경계를 지정한 뒤 수정 소스에서 통과했다. 두 패치는 기존 한 점과의 거리 허용치를 보존하고 지우개 선분과 화살표가 교차하는 경우를 추가한다. C가 2번째 응답에서 기록을 열어본 사실과 A가 문서 없이 같은 판단에 이른 사실을 함께 확인할 수 있다. [C 조사](../../experiments/first-use/excalidraw-arrow-comparison/observations/8369fe26da/trace.jsonl) · [A 조사](../../experiments/first-use/excalidraw-arrow-comparison/observations/bd89a84cc4/trace.jsonl)
- **첫 묶음 B**는 첫 응답에서 서술 자료를 열었다. 18번째 응답에서 가시 화살표를 확인하는 테스트를 직전 소스에 실행해 잠금 해제 사례만 실패하는 것을 봤다. 이때 기본 임시 경로의 `mktemp`가 격리에서 거부되어 수정 파일 자동 복원이 실패했다. 19번째 응답에서 교차 판정을 다시 적용하자 자체 테스트 두 건이 통과했다. 마지막 응답은 임시 파일 정리와 상태 조회였고, 한도에 도달해 제출이 없었다. **둘째 묶음 A**도 두 표본으로 자체 테스트를 실행하고 마지막 응답에서 가시 영역을 지정한 뒤 통과했다. 두 작업 사본 모두 독립 채점용 패치가 봉인되지 않았다. [B 조사](../../experiments/first-use/excalidraw-arrow-comparison/observations/9e69be050c/trace.jsonl) · [A 조사](../../experiments/first-use/excalidraw-arrow-comparison/observations/cc0fde7f8d/trace.jsonl)
- **둘째 묶음 B와 C**는 모두 첫 응답에서 문서를 열었다. B는 직선·둥근 설정을 나누고 경로 밖 화살표까지 회귀 테스트에 남겼다. 교차 검사에는 경계가 폭이나 높이 0인 경우를 고려한 임곗값을 전달했다. C의 16번째 응답에는 수정 파일을 원본으로 되돌려 자체 테스트가 실패하고, 같은 테스트를 수정 소스에 복원해 관련 테스트 16건이 통과한 기록이 있다. C의 패치에도 잠금·경로 밖 보존 단언이 들어 있다. [B 조사](../../experiments/first-use/excalidraw-arrow-comparison/observations/b189cc3b88/trace.jsonl) · [C 전후 검산](../../experiments/first-use/excalidraw-arrow-comparison/observations/001e08a5f9/trace.jsonl#L16)

네 제출 모두 신규 회귀 파일을 포함했다. 제출에 들어간 **테스트 변경만** 깨끗한 직전본에 적용했을 때 A1 1/1, B2 2/2, C1 1/1, C2 1/1이 예상한 삭제 단언에서 실패했다. 참가자의 초기 실패만으로는 가시 영역 문제와 화살표 결함을 구분하기 어려웠던 세션도, 최종 테스트가 결함을 검출한다는 점은 이 대조로 확인했다. C2는 작업자 자신이 최종 테스트를 양쪽 소스에서 검산했다. 이 검산은 완전 성공 점수에 가산하지 않았다. [회귀 파일 단독 대조 로그](../../experiments/first-use/excalidraw-arrow-comparison/observations/witness) · [재현 도구](../../experiments/first-use/excalidraw-arrow-comparison/test_witness.py)

## 참가 비용

각 응답 뒤 CLI 원시 사용량을 기록하고 다음 요청 전에 세션·전체 합계를 확인했다. 각 모델 요청에는 해당 참가자의 공개 입력과 그 세션의 행동·결과 이력이 다시 들어간다. 아래 입력에는 재전송한 명령 출력과 읽은 자료가 포함된다. 셸 횟수는 한 번의 명령 묶음을 한 건으로 센 값이다. 괄호는 셸 종료 코드가 0이 아닌 횟수다. 파이프 또는 후속 명령이 앞선 테스트 실패를 가린 경우는 원문 로그에서 확인한다. B2와 C2에서 각각 한 번씩 형식이 잘못된 모델 응답도 모델 호출과 토큰 합계에 포함했다.

| 세션 기록 | 모델 요청 | 셸 (비정상 종료) | 경과 초 | 입력 | 캐시 입력 ⊆ 입력 | 출력 | 추론 ⊆ 출력 | 세션 입력 초과 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| [C1](../../experiments/first-use/excalidraw-arrow-comparison/observations/8369fe26da/trace.jsonl) | 18 | 17 (2) | 126.6 | 356,998 | 5,504 | 3,181 | 661 | 0 |
| [A1](../../experiments/first-use/excalidraw-arrow-comparison/observations/bd89a84cc4/trace.jsonl) | 19 | 18 (5) | 142.3 | 428,242 | 19,712 | 3,859 | 1,120 | 28,242 |
| [B1](../../experiments/first-use/excalidraw-arrow-comparison/observations/9e69be050c/trace.jsonl) | 20 | 20 (3) | 145.2 | 438,601 | 36,352 | 3,408 | 479 | 38,601 |
| [A2](../../experiments/first-use/excalidraw-arrow-comparison/observations/cc0fde7f8d/trace.jsonl) | 19 | 19 (3) | 130.5 | 422,217 | 24,704 | 3,265 | 484 | 22,217 |
| [B2](../../experiments/first-use/excalidraw-arrow-comparison/observations/b189cc3b88/trace.jsonl) | 18 | 16 (3) | 131.4 | 402,876 | 50,560 | 3,233 | 652 | 2,876 |
| [C2](../../experiments/first-use/excalidraw-arrow-comparison/observations/001e08a5f9/trace.jsonl) | 17 | 15 (3) | 158.0 | 360,028 | 54,656 | 3,872 | 787 | 0 |
| **합계** | **111** | **105 (19)** | **834.0** | **2,408,962** | **191,488** | **20,818** | **4,183** | **91,936¹** |

¹ 세션별 초과분의 합이다. 전체 입력 한도는 여섯 세션의 실제 입력 합계로 별도 판정했다.

전체 **입력 2,408,962개 중 캐시 입력 191,488개**, **출력 20,818개 중 추론 출력 4,183개**다. 마지막 C2 요청 직전까지 확인한 전체 입력은 2,373,826개였고 제출 응답에 35,136개가 추가됐다. 전체 초과 8,962개를 포함해 원시 사용량 전부를 집계했다. 세션 한도 초과는 A1·B1·A2·B2의 마지막 응답에서 관측했고 이후 해당 세션을 재호출하지 않았다. 세션 간 한도 이전, 대체 실행, 시간 만료는 각 0건이다. 참가 시간은 총 834.013초(13분 54초), 최장 158.005초다. 모든 세션에서 시간과 출력은 한도 이내였다.

| 조건 | 완전 성공 | 미제출 포함 입력 | 출력 | 참가 시간(초) | 셸 호출 |
| --- | ---: | ---: | ---: | ---: | ---: |
| A · 소스 | 1/2 | 850,459 | 7,124 | 272.8 | 37 |
| B · 서술형 | 1/2 | 841,477 | 6,641 | 276.6 | 36 |
| C · 동결 원문 | 2/2 | 717,026 | 7,053 | 284.6 | 32 |

주 비교에서 C는 A보다 한 건 더 제출하고 합계 입력을 133,433개 덜 썼으며 참가 시간은 11.8초 더 들었다. 같은 품질에 도달한 첫 묶음에서는 C가 A보다 입력 71,244개, 출력 678개와 15.7초를 덜 썼다. 둘째 묶음 A는 제출이 없어 같은 품질까지의 비용 방향을 반복 검증할 수 없다.

B와 A는 각각 한 건 성공했고 성공한 묶음이 서로 달랐다. C와 B가 모두 성공한 둘째 묶음에서 C는 입력 42,848개를 덜 썼으나 출력은 639개, 시간은 26.6초 더 들었다. 기록에 있는 두 좌표와 삭제 확정의 관계는 참가자의 테스트와 부합한다. 다만 문서를 열어 본 기록만으로 판단의 출처를 확정하기 어렵고, 잠금 보존은 세 조건의 공통 요구였다. 이 과업의 각 조건은 두 번뿐이다. FCA의 기록 작성 기여와 사람의 사용 의향은 이번 측정 범위 밖이다.

## 전달과 일회성 비용

수정 직전 소스·일반 문서와 같은 설치본을 세션마다 복제했다. Git 트리는 upstream과 일치하고 사본에는 부모 없는 로컬 스냅샷 한 개가 있다. 도구 호출은 새 프로세스에서 같은 격리 정책으로 실행했다. 세션 간 파일·대화 공유는 없고, 공개 요청은 기록이 없거나 B/C용 선택 파일을 안내하는 것만 다르다. 조건별 가용 도구와 자료·링크 지문은 첫 참가 호출 전 커밋 `face060`에 고정했다. 기존 ChatGPT 로그인과 Codex CLI를 사용했고, 로컬에서 캡처한 요청은 Sol·medium과 내장 도구 0개였다. 참가 응답 111건의 서버 모델명은 모두 `gpt-6.2-sol`이었다. [전달본과 주장 대조](../../experiments/first-use/excalidraw-arrow-comparison/materials.md) · [배정과 요청 설정](../../experiments/first-use/excalidraw-arrow-comparison/allocation.json) · [격리 대조](../../experiments/first-use/excalidraw-arrow-comparison/observations/isolation.json)

| 일회성 항목 | 관측 비용 |
| --- | --- |
| 기존 C 기록 작성 | 당시 자료 수집 약 8초, 읽기·CLI·기록 고정 약 1분 48초 |
| 기존 기록 검산 | 기록 고정 뒤 추가 단언·새 사본까지 약 4분. 별도 재현 스크립트 50.6초. 독립 리뷰의 작업 시간과 과거 토큰은 결측 |
| 이번 B 변환 | 준비 시계 시작부터 B 초안 저장·링크 열 개 대조까지 약 23초. 문단별 주장 검토 시간과 작성자 토큰은 별도 계측하지 않음 |
| 공통 환경 준비 | 설치·격리 점검·채점 대조·자료 동결을 포함한 준비 계측 구간 258.6초. B 변환이 이 구간과 겹침. 배치 시작 및 각 앞 세션 종료부터 다음 첫 요청까지의 사본 준비·정리 간격 합계 약 80.0초 |
| 채점 | 참가 전 원본·기준 교정 두 건 30.1초, 제출 네 건의 적용·독립 채점 63.6초. 제출 회귀 파일만 직전본에서 별도 검산한 네 건은 사본 준비 포함 111.3초. 모두 참가 경과 시간에서 제외 |

작성 비용의 과거 근거와 해당 자료의 소스 라이선스도 함께 보관했다. [당시 작성·검산 기록](2026-11-27-excalidraw-eraser-preparation.md) · [Excalidraw MIT 라이선스](../../experiments/first-use/excalidraw-eraser/LICENSE.excalidraw)

## 독립 재현

macOS, Xcode 명령줄 도구, Node 22.19.0, Python 3, rg, npm, Git이 있는 환경에서 저장소 루트에서 실행한다. 첫 두 단계에는 공개 upstream과 잠금 파일의 의존성을 받기 위한 네트워크가 필요하다. 이미 설치된 기준 사본으로 채점할 때 참가 모델 계정은 필요 없다. 아래 경로는 새 디렉터리로 잡는다.

```sh
study=experiments/first-use/excalidraw-arrow-comparison
scratch=$(mktemp -d)
git clone -q --bare https://github.com/excalidraw/excalidraw.git "$scratch/upstream.git"
python3 "$study/snapshot.py" "$scratch/upstream.git" "$scratch/template"
python3 "$study/replay.py" --grade "$scratch/template" "$scratch/upstream.git" "$scratch/regraded"
```

보관한 사용량과 채점 결과는 Python만으로도 검토할 수 있다. `python3 experiments/first-use/excalidraw-arrow-comparison/replay.py`를 실행한다. 각 모델 요청의 공개 입력을 다시 조립해 SHA-256을 대조하고 사용량을 합산한다. 재채점은 조건표를 열기 전에 익명 ID의 패치만 읽는다. 각 사본에 패치를 적용한 뒤 같은 관측 코드와 동결된 올가미 테스트를 배치한다. 두 장면의 ID별 삭제 플래그와 비삭제 장면 포함 여부, 관측 2건, 올가미 6건, 프로세스 종료 상태가 모두 맞아야 완전 성공이다. [채점기](../../experiments/first-use/excalidraw-arrow-comparison/grade.py) · [재현 및 사용량 검산](../../experiments/first-use/excalidraw-arrow-comparison/replay.py)

참가자 회귀 테스트의 직전본 대조는 같은 템플릿을 준비한 뒤 다음과 같이 재현한다.

```sh
for patch in "$study"/observations/*/first.patch; do
  id=$(basename "$(dirname "$patch")")
  python3 "$study/test_witness.py" "$scratch/template" "$patch" "$scratch/$id-witness.json"
done
```

새 아카이브에 의존성을 다시 설치한 뒤 원본·기준·첫 패치 네 건을 재채점했다. 여섯 판정에서 패치 지문, 적용, 두 장면, 테스트 결과와 완전 성공 여부가 기존 기록과 일치했다. [새 사본 대조](../../experiments/first-use/excalidraw-arrow-comparison/observations/recheck.json)

저장소 검사에서 `pnpm check`는 308개 통과·기존 5개 건너뜀·예제 빌드 성공, `pnpm experiment`는 기존 비교 4/4였다.
