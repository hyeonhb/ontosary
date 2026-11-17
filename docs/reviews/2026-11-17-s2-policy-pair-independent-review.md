# S2 clone 정책 한 행 대조 독립 리뷰

2026-11-17. [개발 보고서](2026-11-17-s2-policy-pair.md)와 PR #61의 `7a5eb53f96e48c28e972bbd059d74aa5636c4933`을 검토했다. 실행 구현은 `da4e94787209c977f3e1b7ae9bf8c08b27ea770d`와 같다. **원래1/후보1의 제한 대조와 안전한 종료·회수는 완료됐다. 보고서의 원문 관찰에 동의하며, 이번 승인 범위를 차단할 추가 결함은 발견하지 않았다.** PR #61은 검증한 head로 병합했다(`ee7ac98a1a0c599ce6ad2562d3883d9e165f1e19`).

자동 parser의 미지원 형식은 남는다. 원문에서 확인한 사실과 자동 재현의 한계를 분리해 공개했으므로, 이를 이유로 이미 완료한 대조를 다시 실행하거나 결과 기록의 병합을 막을 필요는 없다. 실제 CLI 전체 경계와 S2 본 비교 준비 완료 판정은 아니다.

## 확인한 정책 효과

| 항목 | 원래 정책 | 후보 정책 |
| --- | --- | --- |
| 실제 create/start | 1/1 | 1/1 |
| bwrap 사전 검사 | PID42의 namespace clone EPERM | PID41→42 clone 성공, 자식42 mount EPERM |
| 명령 준비 | PID43의 namespace clone EPERM | PID43→44 clone 성공, 자식44 mount EPERM |
| 관찰 probe / sandbox 명령 종료 코드 | 0 / 1 | 0 / 1 |
| 합성 payload 시작 | false | false |
| 수집·봉인·호스트 회수 | 완료, 전체3.068초 | 완료, 전체2.782초 |

회수한 실제 OCI의 seccomp 전체를 직접 비교해 기존17행에 승인한 clone arg0=2013397009 ALLOW 한 행만 추가됐음을 확인했다. 나머지 Spec도 소유 관계가 확인된 ID/경로 치환 뒤 전체 비교를 통과한다. 다른 보안 필드를 삭제한 투영 비교가 아니다. 두 실행의 probe·이미지·명령/trace 옵션·입력 근거가 같고 실행별 writable 상태/ID는 다르다.

후보 trace의64–65행은 PID41의 clone 반환값42,110행은 자식42의 mount 거부다.132행의 PID43 clone 반환값44와178행의 자식44 mount 거부도 확인했다.55행의 `/usr/bin/true` 사전 검사와123행의 명령 준비 argv,182행의 자식44 exit1을 대조했다. 별도 수동 검토의 hash와9개 발췌가 회수 원문과 일치한다. 따라서 **원문 관찰은 `first-clone-passed-next-blocked`**로 지지된다.

관찰된 mount는 `mount(NULL, "/", NULL, MS_REC|MS_SILENT|MS_SLAVE, NULL)`이고 EPERM이다. 이 결과만으로 seccomp·AppArmor·다른 kernel 검사의 정확한 기여를 분리하거나, mount 한 행 추가만으로 전체 sandbox가 된다고 결론 내릴 수 없다. 합성 관찰 probe의 exit0은 실제 sandbox 명령의 성공이 아니다.

## 자동 판독 한계와 처리

[policy_pair.py](../../experiments/domain-model/s2/trial/container/execution-lifecycle/policy_pair.py)의 `trace_observation()`은 PID 접두사가 있는 단일 줄과 unfinished/resumed 조합을 읽는다. 실제 첫 clone 줄에는 `/usr/bin/strace: Process 42 attached`가 삽입되고 다음 줄의 `) = 42`에는 PID 접두사가 없다. 이 조합을 연결하지 못해 첫 clone이 누락되고 자동 결과가 **inconclusive**로 남는다.

저장 verifier도 같은 자동 판정을 재현했다. 독립 확인에서는 원문을 보존하고 메모리 안의 임시 파생 문자열에서 해당 안내 한 건만 제거했을 때 기존 parser가 두 clone과 mount 거부를 연결하는 것도 확인했다. 이는 누락 원인을 좁힌 실험이며 원문/동결 자동 결과를 수정한 것이 아니다. 일반적인 안내문 삭제나 임의 줄 병합이 안전하다는 검증도 아니다.

미지원 내용을 성공으로 처리하지 않은 점은 적절하다. 후속은 [30분 상한의 오프라인 판독 보완](2026-11-17-s2-trace-reanalysis-instructions.md)으로 충분하다. 이전 `candidate-trace-analysis.json`·`pair-complete.json`·index와 동결 verifier 결과는 보존하고 새 판독을 별도 산출물로 연결한다. 새 VM/정책 시험은 필요 없다. 이 보완은 다음 권한 선택에 필요한 새 runtime 증거를 만들어 주지는 않는다.

## 구현·증거 검증

- 검토 head에서 `pnpm check` **304개**, skip0·타입·예제 build와 Python execution-lifecycle **148개**, 공유 lifecycle **16개**, 감사/deadline/package **44개**, 총 **208개**를 통과했다.
- 새 pair 진입점은 정확한 목적/순서/분모/고정 RULE/cacheOnly/과거7단위 근거와 코드 gate를 검사한다. baseline의 봉인·회수·예상 결과를 확인한 뒤에만 후보 profile을 게시한다. pair 예외는 기존 failed_dispatch에 연결되며 감사/회수 실패도 cleanup을 건너뛰지 않는다. 기존7개 fixtures 실행으로 분모를 혼용하지 않는다.
- 새 verifier는 **134파일·분석4/closing3·Spec2개·봉인2개·회수4개**를 재현했고, 과거3개 verifier도 통과했다. 자동 status는 inconclusive이며 verifier 통과를 CLI 성공으로 해석하지 않는다.
- final-source **85파일**, 전달 **38파일**을 실제 코드와 대조했다. 최초3,527파일 중3,520파일 불변·허용 변경7개이며 보고된 최종 변경과 일치한다. 전달 코드의 실행 후 변경은 없다. 과거 원시 자료를 새 기대값으로 덮지 않았다.
- 공개 준비물4개의 현재 바이트/크기/hash와 이미지 binding을 다시 읽어 확인했다. 실제 준비42.048초·download/build/save0·import1이다. 회수 후 cleanup은 complete·오류0·VM/임시 root 부재이며0.971초다. 개별 단위의 종료/봉인 근거는 VM 폐기와 별도로 남아 있다.
- 새 VM1·container2·재시도0·회차888.660초라는 실제 분모/비용을 확인했다. 이 리뷰의 새 runtime/정책/인증/모델 호출은0회다. 제품/FCA/평가 의미는 불변이므로 pnpm experiment·Linux Vendure 전체 평가를 반복하지 않았다.

독립 검증은 [스크립트](evidence/2026-11-17-verify-policy-pair-independent.py)와 [JSON 요약](evidence/2026-11-17-s2-policy-pair-independent.json)에 남겼다. 검토 head에서 실행하는 읽기/오프라인 도구이며 준비물 실제 hash 대조에는 로컬 보관 archive가 필요하다. PR은 자체 리뷰와 검사 뒤 병합했으며 다른 사람의 승인을 주장하지 않는다.

## 방향 판단

반복 준비의 운영 병목은 이번에 상당 부분 해소됐다. 준비42초, 두 단위와 회수 약6초, 전체 작업 약14.8분에 정책 효과와 다음 차단점까지 관찰했다. 이제 막힌 것은 설치나 정리 코드가 아니라 **현재 외부 정책과 내부 sandbox가 요구하는 동작의 호환성**이다.

따라서 같은 경계를 유지한 채 syscall 허용을 하나씩 추가하는 실험을 자동으로 이어가지 않는다. 다음 실제 시험 전에는 사용자와 외부 컨테이너/VM 및 내부 CLI sandbox 각각이 보호할 파일·제어 상태·인증·네트워크·자손 종료의 책임을 정해야 한다. 내부 sandbox를 유지하면서 필요한 권한의 전체 영향을 검토할지, 외부 경계를 중심으로 역할 분담을 재검토할지는 별도 아키텍처 판단이다. 후자의 실현 가능성이나 안전성이 이번 자료로 입증된 것은 아니다.

R11 unresolved·R12 기존 범위·production/live 거부·fixtureOnly=true·validSubmission=false·trialAuthorized/readyForTrial=false·results=null을 유지한다. mount 등 추가 권한·실제 인증/model·본 비교는 계속 보류한다. 환경 검증은 도메인 모델의 agent 변경 효용(H-O)과 FCA의 모델 구축 기여(H-F)를 위한 수단이며 두 제품 가설은 아직 검증되지 않았다.
