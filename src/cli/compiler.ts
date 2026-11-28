import { createRequire } from 'node:module';
import defaultCompiler from 'typescript';

export function selectCompiler(requested = '5.9.3'): typeof defaultCompiler {
  let compiler: typeof defaultCompiler;
  switch (requested) {
    case '5.9.3':
      compiler = defaultCompiler;
      break;
    case '4.9.4':
      // Load only the locked Ontosary dependency, resolved relative to this CLI.
      compiler = createRequire(import.meta.url)('typescript-4-9-4');
      break;
    default:
      throw new Error(`Unverified TypeScript version '${requested}'. Supported versions: 4.9.4, 5.9.3.`);
  }
  if (compiler.version !== requested) {
    throw new Error(`Requested TypeScript ${requested}, loaded ${compiler.version}; analysis did not start.`);
  }
  return compiler;
}
