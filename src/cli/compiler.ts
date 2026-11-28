import { createRequire } from 'node:module';
import type ts from 'typescript';

const load = createRequire(import.meta.url);

export function selectCompiler(requested: string): typeof ts {
  let compiler: typeof ts;
  switch (requested) {
    case '5.9.3':
      compiler = load('typescript');
      break;
    case '4.9.4':
      // Load only the locked Ontosary dependency, resolved relative to this CLI.
      compiler = load('typescript-4-9-4');
      break;
    default:
      throw new Error(`Unverified TypeScript version '${requested}'. Supported versions: 4.9.4, 5.9.3.`);
  }
  if (compiler.version !== requested) {
    throw new Error(`Requested TypeScript ${requested}, loaded ${compiler.version}; analysis did not start.`);
  }
  return compiler;
}
