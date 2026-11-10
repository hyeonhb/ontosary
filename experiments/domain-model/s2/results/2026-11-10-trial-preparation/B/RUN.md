# 실행 안내

매 실행은 같은 모델 설정과 파일·검색·편집·셸 도구를 사용한다. 과업/자료 공개 후 첫 모델 요청 시작부터 1,800초이며 도구 시간도 포함한다. 종료 시 단일 제출을 수집한다. 토큰 hard cap은 적용하지 않으며 cache 입력을 포함한 원시 usage, 누락 및 100,000토큰 참고선 초과를 기록한다. reasoning 출력은 출력에 이미 포함되면 다시 더하지 않는다.

source/는 생산 소스다. admin-ui의 지원되는 TypeScript 메서드와 실제 고정 Program에 포함되는 상대 helper 변경을 허용한다. 기존 타입·호출자를 보존한다. generated/server schema·설정·lock·HTML·constructor/field 초기화·상속/데코레이터 변경, 삭제·Program 미포함 파일은 미지원이다. Promise/async 및 미검토 연산자를 추가하지 않는다. 지원 동기 RxJS 목록은 of, forkJoin, EMPTY, Observable, Subject, map, mapTo, startWith, switchMap, take다. 이 안내는 특정 구현을 요구하지 않는다.

공개 검증은 작업공간 루트의 tools/public-check를 source/에서 ../tools/public-check로 실행해 생산 소스 전체를 검사한다. 추가 helper도 검사하며 원래 scope·타입 설정을 유지한다. upstream 전체 테스트가 통과한다고 가정하지 않는다. 비공개 동작 평가의 입력·결과는 제출 전에 제공되지 않는다.

자체 테스트·메모·설명·검증 기록은 auxiliary/에, 임시 파일은 scratch/에 둔다. source/의 추가·수정·삭제는 모두 최종 제출에 보존한다. 의존성·도구·준비 config·자료는 읽기 전용이다. 심볼릭 링크와 특수 파일 제출은 거부한다.

외부 네트워크·외부 검색·추가 모델·서브에이전트·다른 실행의 자료를 사용할 수 없다. 질문은 기록하지만 실행 중 새 해법 힌트나 사람 보정은 제공하지 않는다. 자신의 검증을 수행한 뒤 설명과 결과를 auxiliary/에 남긴다. 시간 종료 시 실행기와 자식 프로세스를 정지한 뒤 소스 snapshot을 수집한다.
