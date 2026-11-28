import defaultCompiler from 'typescript';
import { scanWithCompiler } from './analyzer.js';
import type { ScanResult } from './model.js';

export function scan(projectPath: string): ScanResult {
  return scanWithCompiler(projectPath, defaultCompiler);
}

export * from './model.js';
export { selectFunction } from './analyzer.js';
export { compare, evaluate } from './logic.js';
export { buildContext, formalConcepts, discoverConcepts } from './fca.js';
