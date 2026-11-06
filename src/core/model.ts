/** JSON-only public model. IDs are project-relative source coordinates, not names. */
export interface Evidence {
  file: string;
  symbol: string;
  start: { line: number; column: number; offset: number };
  end: { line: number; column: number; offset: number };
}
export interface Reference {
  id: string;
  name: string;
  evidence: Evidence;
}
export type Value = string | number;
export type Logic =
  | { op: 'constant'; value: boolean }
  | { op: 'eq' | 'neq'; variable: string; value: Value }
  | { op: 'and' | 'or'; left: Logic; right: Logic }
  | { op: 'not'; operand: Logic };
export interface Variable {
  key: string;
  sourceName: string;
  domain: Value[];
  declaration: Reference;
}
export type Normalization =
  | { status: 'supported'; logic: Logic; variables: Variable[]; assumptions: string[] }
  | { status: 'unsupported'; reason: string };
export interface ConditionFact {
  id: string;
  kind: 'return' | 'if' | 'conditional' | 'loop';
  text: string;
  evidence: Evidence;
  normalization: Normalization;
}
export interface FunctionFact extends Reference {
  parameters: { name: string; type: string; evidence: Evidence }[];
  returnType: string;
  referencedTypes: Reference[];
  properties: Reference[];
  references: { target: Reference; evidence: Evidence }[];
  conditions: ConditionFact[];
  predicate: Normalization;
  predicateEvidence?: Evidence;
}
export interface TypeFact extends Reference {
  kind: 'interface' | 'alias' | 'enum';
  type: string;
  fields: { name: string; type: string; declaration: Reference }[];
}
export interface ScanResult {
  schemaVersion: 1;
  category: 'code-facts';
  project: string;
  /** Actually analyzed implementation files; unsupported local implementations appear in omissions. */
  files: string[];
  types: TypeFact[];
  functions: FunctionFact[];
  diagnostics: { category: string; code: number; message: string; evidence?: Evidence }[];
  omissions: { reason: string; evidence?: Evidence }[];
  limitations: string[];
}
export interface FormalContext {
  objects: string[];
  attributes: string[];
  incidence: Record<string, string[]>;
}
export interface Concept { id: string; extent: string[]; intent: string[] }
export interface Comparison {
  status: 'Equivalent' | 'Implies' | 'Different' | 'Unknown' | 'Unsupported';
  equivalent?: boolean;
  leftImpliesRight?: boolean;
  rightImpliesLeft?: boolean;
  direction?: 'left-to-right' | 'right-to-left';
  counterexample?: Record<string, Value>;
  leftOnly?: Record<string, Value>;
  rightOnly?: Record<string, Value>;
  evaluatedAssignments: number;
  assumptions: string[];
  reason?: string;
}
