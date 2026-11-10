# 구현 전 선택 기록 — 2026-11-10

기준 ef60bc9. 실제 모델 호출 없이 기존 CLI/macOS의 최소 기능을 조사했다.

- 같은 CLI profile의 기존 detached 반례를 두 새 임시 경로에서 재현했다. process-group SIGKILL은 새 세션/그룹 자손을 포함하지 않는다. 부모 종료·pipe close는 writer 종료 증거가 아니다.
- 설치 macOS 26.6.2의 launchd.plist 설명은 AbandonProcessGroup의 정리 범위를 같은 process group으로 한정한다. 따라서 이 설정으로 옮겨도 현재 탈출 경로가 남는다. persistent launch job은 설치하지 않았다.
- 설치 SDK sys/event.h는 NOTE_TRACK/NOTE_CHILD를 미지원으로 명시한다. 실제 EVFILT_PROC + NOTE_TRACK 등록의 EV_RECEIPT는 error45(ENOTSUP)를 반환했다. kqueue로 자동 자손 소유권을 확보하는 구현은 채택하지 않는다. [Apple 공개 헤더](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/sys/event.h).
- Endpoint Security는 별도 [entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.endpoint-security.client)가 필요한 다른 배포/권한 경계다. 이번에 요청·활성화하지 않는다. ps 폴링/이름 검색/재부모화 추적을 보안 경계로 대체하지 않는다.

**선택:** 현재 범위에서 검증된 모든-writer 종료 경계를 확보하지 못했다. R11은 unresolved로 남긴다. 기존 process-group 정리는 진단용 best effort로만 유지하고 반환 대기를 제한한다. 실행 결과의 task 종료와 collection 허용을 분리하며 production collection/evaluation은 fail-closed로 차단한다. 진단 snapshot은 별도 kind/실행 경로·receipt에 결합하고 정상 제출로 승격하지 않는다. 알려진 참조 교정은 명시적인 별도 fixture 경로에서만 검증한다.

정상 종료/실패/timeout/spawn 오류/처리 가능한 SIGINT·SIGTERM 모두 같은 blocked 경계를 반환한다. 정리는 최대250ms 추가 대기이며 모델/도구 작업 예산의 연장이 아니다. supervisor 자체 SIGKILL·호스트 장애는 자손 종료를 보장하지 못한다. 다음 live 실행은 시작하지 않는다. 이미 열린 핸들·분리 자손의 deadline 이후 쓰기도 여전히 가능하므로 수집 보장을 주장하지 않는다. 추가 권한은 필요 없고 작은 상태·증거 코드만 유지한다.

후속 선택지: (1) 커널이 전체 작업 단위를 소유·종료하는 별도 VM/container 경계는 설치·이미지/의존성·CLI 인증·공정성 재검증 비용이 크다. (2) 관리자/entitlement 기반 native 서비스는 배포·권한·보안 유지 비용이 크며 완전한 종료 정책은 별도 검증 대상이다. (3) subprocess를 금지하고 제한된 도구만 제공하는 방식은 구현이 작아질 수 있지만 기존 셸/도구 계약을 바꾼다. 어느 것도 자동 채택하지 않으며 사용자 결정 전 기존 실행 차단을 유지한다. 구체적 공수는 미측정이다.
