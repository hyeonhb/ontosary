# 의존성 및 라이선스 확인

확인일: 2026-11-03. `npm view <package> version license engines --json`과 실제 설치 후 `pnpm licenses list --json`을 확인했다. 직접 버전은 package.json, 모든 해결 버전/integrity는 pnpm-lock.yaml에 고정되어 있다.

Node 22.19.0 / pnpm 11.19.0에서 설치·빌드·테스트했다. TypeScript 5.9.3은 Apache-2.0이고 React/React DOM, Vite, Vitest, @types 패키지는 MIT다. TypeScript는 안정적으로 사용한 JS Compiler API를 위해 의도적으로 5.9.3에 고정했다.

다음은 이 환경(darwin-arm64)에 실제 설치된 45개 패키지의 manifest 라이선스 메타데이터다. 다른 플랫폼의 선택적 바이너리 전체를 검사한 목록은 아니다. 전이 의존성에는 MPL-2.0, ISC, BSD-3-Clause도 있다. 프로젝트의 Apache-2.0 선언이 의존성 라이선스를 대체하지 않는다. 재배포 시 각 패키지의 LICENSE/NOTICE를 유지·검토해야 한다. 의존성 소스는 수정하지 않았다.

| 패키지 | 설치 버전 | 라이선스 |
| --- | --- | --- |
| @jridgewell/resolve-uri | 3.1.2 | MIT |
| @jridgewell/sourcemap-codec | 1.6.0 | MIT |
| @jridgewell/trace-mapping | 0.3.31 | MIT |
| @oxc-project/types | 0.156.0 | MIT |
| @rolldown/binding-darwin-arm64 | 1.2.16 | MIT |
| @rolldown/pluginutils | 1.0.1 | MIT |
| @types/chai | 5.2.3 | MIT |
| @types/deep-eql | 4.0.2 | MIT |
| @types/estree | 1.0.10 | MIT |
| @types/node | 22.20.5 | MIT |
| @types/react | 19.3.0 | MIT |
| @types/react-dom | 19.3.0 | MIT |
| @vitest/mocker | 5.1.0 | MIT |
| @vitest/spy | 5.1.0 | MIT |
| assertion-error | 2.0.1 | MIT |
| chai | 6.3.0 | MIT |
| csstype | 3.2.3 | MIT |
| detect-libc | 2.1.2 | Apache-2.0 |
| es-module-lexer | 2.3.2 | MIT |
| estree-walker | 3.0.3 | MIT |
| expect-type | 1.4.0 | Apache-2.0 |
| fdir | 6.5.0 | MIT |
| fsevents | 2.3.3 | MIT |
| lightningcss | 1.33.0 | MPL-2.0 |
| lightningcss-darwin-arm64 | 1.33.0 | MPL-2.0 |
| magic-string | 1.4.5 | MIT |
| nanoid | 3.3.20 | MIT |
| obug | 3.0.0 | MIT |
| picocolors | 1.1.1 | ISC |
| picomatch | 4.0.7 | MIT |
| postcss | 8.5.32 | MIT |
| react | 19.3.1 | MIT |
| react-dom | 19.3.1 | MIT |
| rolldown | 1.2.16 | MIT |
| scheduler | 0.28.0 | MIT |
| source-map-js | 1.2.2 | BSD-3-Clause |
| std-env | 4.3.0 | MIT |
| tinybench | 6.2.3 | MIT |
| tinyexec | 1.3.1 | MIT |
| tinyglobby | 0.2.17 | MIT |
| typescript | 5.9.3 | Apache-2.0 |
| undici-types | 6.21.0 | MIT |
| vite | 8.3.5 | MIT |
| vitest | 5.1.0 | MIT |
| why-is-node-running | 3.2.1 | MIT |

## 호환성 근거

- [TypeScript Compiler API](https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API)
- [Vite requirements](https://vite.dev/guide/)
- [Vitest requirements](https://vitest.dev/guide/)

npm 이름 `ontosary`는 확인 시 E404였다. 예약/배포는 하지 않았으며 공개 전에 다시 확인한다.
