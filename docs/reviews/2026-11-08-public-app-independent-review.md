# 공개 업무 앱 적합성 독립 리뷰 — 2026-11-08

## 판정

**과업·원문 근거 준비와 제한된 실패 관찰은 완료로 인정한다. 이번 검토 범위에서 수정이 필요한 새 결함은 발견하지 않았다. 분석 가능한 표본 확보와 제품 효용 검증은 미완료다.** 실패와 미측정을 구분한 보고는 타당하며, 미설치 환경의 오류를 upstream 앱의 결함이나 영구 부적합으로 일반화하지 않았다.

대상은 [PR #11](https://github.com/hyeonhb/ontosary/pull/11), main `685545fe85d67a0559e5908c6cd0fda4163a65e3`, [개발 보고](2026-11-08-public-app-suitability.md)다. 기준 `87398ba` 대비 제품 src·테스트·package/lockfile·기존 corpus 변경이 없음을 확인했다. 새 prepare/run/observe/verify/search 코드, manifest와 과업 29개 근거, 원시 결과, 설정 및 실제 upstream 원문을 검토했다. 이 리뷰에서도 제품 코드를 수정하거나 앱 의존성을 설치하지 않았다.

## 독립 검증

- `pnpm check`: 8파일/136테스트, 타입 검사, 예제 production build 통과.
- `pnpm experiment`: 기존 비교 4/4 통과. 인공 예제의 13×26 context, 후보 8개, 잘림 없음 유지.
- 새 격리 cache `/tmp/ontosary-public-app-independent-20261108`에 두 immutable archive를 다시 다운로드했다. archive SHA-256과 전체 inventory(Saleor 6,419파일/Vendure 4,735파일)가 역사적 결과와 일치했다. task hash·고유 UTF-16 anchor/행 검증도 통과했다.
- 같은 새 cache에서 후보별 original/scoped를 두 번 실행했다. 비시간 파일 Saleor 13개/Vendure 17개가 byte 일치했고 process 오류 없음, 실패 outcome, 모든 predicate unsupported, 그룹/FCA 미생성을 확인했다.
- 역사적 결과와 새 실행의 outcome·실제 Program 파일/hash/import 목록·검색 기준선은 모두 일치했다. scan 전체의 경로 간 byte 동일성은 주장하지 않는다. 이번 길이의 cache에서는 Saleor scoped 타입 표시 17개, Vendure original/scoped 9개/6개 문자열이 달랐다. 다른 필드 차이는 없었다. TypeChecker가 절대 경로 길이에 따라 이미 생략한 타입 문자열은 사후 prefix 치환으로 복원되지 않는다. 개발 보고의 별도 cache 비교 2개/9개/6개와는 비교 경로가 다르며, 알려진 이식성 제한을 추가 확인한 것이다.

| 관찰 | 구현 파일 / 함수 | 오류 / omissions | 독립 결과 |
| --- | ---: | ---: | --- |
| Saleor original | 미산출 | 미산출 | strictNullChecks 전제로 Program 전 거부 |
| Saleor scoped | 806 / 4,205 | 1,713 / 506 | 보고와 일치 |
| Vendure original | 581 / 4,379 | 2,372 / 751 | 보고와 일치 |
| Vendure scoped | 327 / 2,264 | 1,058 / 440 | 보고와 일치 |

[검증 요약·hash·차이 경로](evidence/2026-11-08-public-app-review-verification.json), [요약 생성 스크립트](evidence/2026-11-08-public-app-review-check.py)를 보존했다. 새 raw 실행은 ignored `work/public-app-independent-20261108/{saleor,vendure}-{a,b}`에 있다. 재현은 [기존 README](../../experiments/public-app/README.md)의 prepare/run/verify를 새 cache/output에서 수행한 후 다음과 같이 요약한다. 요약기는 실패 상태의 고정 V1에 대한 검사이며 향후 설치 실험의 성공 검사로 재사용하지 않는다.

```sh
python3 docs/reviews/evidence/2026-11-08-public-app-review-check.py \
  work/public-app-independent-20261108 /tmp/ontosary-public-app-independent-20261108
```

## 원문 근거와 해석

Saleor의 취소 메뉴, fulfilled fulfillment 분기, 확인/차단 dialog, provider와 generated mutation 연결을 원문으로 대조했다. Vendure의 취소/환불 분기, settled payment 판정, dialog 입력과 API 문서도 대조했다. 이 원문 일치는 서버 정책의 완전성이나 사람의 업무 의미 승인이 아니다. 과업을 첫 scan 전에 작성했다는 순서는 개발 기록에 의존하며, task hash는 이후 불변성을 검증할 뿐 독립 사전등록 시각을 증명하지 않는다.

라이브 [Saleor orderCancel 문서](https://docs.saleor.io/api-reference/orders/mutations/order-cancel)의 schema 3.23.43·권한/입출력 설명과 [Vendure 주문 문서](https://docs.vendure.io/current/framework/core-concepts/orders)의 current 3.8.1 표시도 재확인했다. 고정 클라이언트 revision의 정책을 대신하지 않는다는 보고의 제한은 적절하다. upstream 라이선스 고지와 생성 파일 출처를 보존했으며 전체 의존성 재배포 검토가 끝났다고 주장하지 않았다.

이름 검색은 Saleor required 14개/Vendure 9개 모두의 **파일**에 도달하지만 anchor 시작 행은 8개/4개다. 검색어를 답을 본 뒤 정했으므로 blind 비교도, 조건 이해의 성공률도 아니다. 향후 도구의 가치는 파일 찾기뿐 아니라 조건·연결 설명의 정확성과 불필요한 검토량으로 비교해야 한다. 이번 결과만으로 FCA가 유용하거나 불필요하다고 결론 낼 수 없다.

## 다음 단계에서 분리할 세 문제

1. **환경 준비:** 현재 missing-module/tslib 오류는 실제 설치·common 빌드 후의 적합성을 알려주지 않는다. 설치 비용도 아직 미측정이다. strict를 유지하는 Vendure에 한 번 더 제한된 준비 기회를 주는 것은 타당하다.
2. **탐색/FCA 범위:** `buildContext`는 scan의 모든 함수를 객체로 삼는다. 과업 root를 네 파일로 줄여도 transitive imports를 포함해 함수 2,264개이며, 네 진입 파일의 함수만 세어도 **82+14+33+0=129개**로 기본 객체 상한 128을 넘는다. 이는 오류 상태에서 얻은 문법적 inventory이고 설치 후 유효 FCA 실행 결과는 아니다. 다만 설치 성공만으로 A/B/C 비교 자료를 만들 수 있다는 가정은 성립하지 않는다. 속성 상한 64도 별도다. 상한을 올리거나 유리한 함수만 골라 범위를 바꾸지 않는다.
3. **필수 근거 범위:** Vendure required 9개 중 두 근거는 HTML이다. 동일한 원문 접근을 모든 비교 조건에 제공하고 자동 추출/수동 보충을 구분해야 한다. 이 표본의 준비가 Angular 플러그인 개발을 정당화하지는 않는다.

이번 보고는 세 제한을 이미 공개하고 있어 새 결함 ID를 만들지 않는다. 다음 지시에서는 **설치·진단 해소 성공**과 **탐색 실험에 적합한 범위 확보**를 별도 완료 기준으로 고정한다. 반복적인 환경 복구가 제품 검증을 계속 미루게 해서는 안 된다.

## Gate와 사용자 결정

Gate 1의 기존 제한된 통과와 R1~R5 해결 상태는 유지한다. Gate 2 의미적 유용성·Gate 3 기준선 대비 효용은 미검증이다. Gate 4는 도입 장벽 관찰만 추가됐고 실제 설치·사람 준비/유지 비용은 미측정이다. 제품 확대 근거가 생긴 것은 아니다.

사용자에게 제한된 환경 준비와 탐색/논리 검증 전제 분리 설계를 제시했고, **“Vendure 준비를 30분 한도로 한 번 더 검증”**을 선택했다. ADR-019와 [다음 개발 지시](2026-11-08-vendure-preparation-next-plan.md)에 반영한다. 이번 리뷰의 완료물은 검증·판정·다음 지시이며, 설치 실험 자체는 별도 개발 작업이다. 실패/시간 초과/범위 부적합이면 근거를 보존해 재판단하고 코어 계약·상한을 자동으로 완화하지 않는다.
