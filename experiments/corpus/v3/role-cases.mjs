// Source-authored adjacent role cases. These fixtures are scanned, never executed.
export const source = `import { external as imported } from './external.js';
const key = 'slot';
export function localTypes() {
  type Box<TypeParam> = { value: TypeParam };
  interface Local { member: string }
  return true;
}
export function signatures() {
  interface LocalSignatures<InterfaceParam> {
    method<MethodParam>(methodArg: MethodParam): InterfaceParam;
    <CallParam>(callArg: CallParam): InterfaceParam;
    new <CtorParam>(ctorArg: CtorParam): object;
    [indexArg: string]: unknown;
    [key](): void;
  }
  return true;
}
export function genericClass() { class LocalClass<ClassParam> {} return true; }
export function typeExpressions() {
  type Mapped = { [MappedKey in 'a' | 'b']: MappedKey };
  type Conditional<T> = T extends Array<infer Inferred> ? Inferred : never;
  type Query = typeof imported;
  return true;
}
export function recursive(): boolean { return recursive(); }
export function importedCall() { return imported(); }
export function parameterRead(value: string) { return value; }
export function localRead() { const item = true; return item; }
export function referenceOnly() { return imported; }
export function shadow(imported: () => boolean) { return imported(); }
export function propertyRead() {
  interface RuntimeShape { actualMember: string }
  const data: RuntimeShape = { actualMember: 'value' };
  return data.actualMember;
}
export function methodCall(arg: { runtimeMethod(): boolean }) { return arg.runtimeMethod(); }
export function unused() { return true; }
`;
export const texts = { 'input.ts': source, 'external.ts': 'export function external() { return true; }\n' };
const location = (anchor, file = 'input.ts') => {
  const text = texts[file], offset = text.indexOf(anchor);
  if (offset < 0 || text.indexOf(anchor, offset + 1) >= 0) throw new Error(`Invalid fixture anchor: ${anchor}`);
  return { file, anchor, offset, line: text.slice(0, offset).split('\n').length };
};
const external = location('export function external()', 'external.ts');
export const cases = [
  ['type-parameter-name', 'localTypes', 'TypeParam> =', 'TypeParam> =', 'reference', 'reject'],
  ['interface-property-name', 'localTypes', 'member: string', 'member: string', 'reference', 'reject'],
  ['interface-type-parameter', 'signatures', 'InterfaceParam> {', 'InterfaceParam> {', 'reference', 'reject'],
  ['method-signature-name', 'signatures', 'method<MethodParam>', 'method<MethodParam>', 'reference', 'reject'],
  ['method-type-parameter', 'signatures', 'MethodParam>(methodArg', 'MethodParam>(methodArg', 'reference', 'reject'],
  ['method-parameter-name', 'signatures', 'methodArg: MethodParam', 'methodArg: MethodParam', 'reference', 'reject'],
  ['call-type-parameter', 'signatures', 'CallParam>(callArg', 'CallParam>(callArg', 'reference', 'reject'],
  ['call-parameter-name', 'signatures', 'callArg: CallParam', 'callArg: CallParam', 'reference', 'reject'],
  ['construct-type-parameter', 'signatures', 'CtorParam>(ctorArg', 'CtorParam>(ctorArg', 'reference', 'reject'],
  ['construct-parameter-name', 'signatures', 'ctorArg: CtorParam', 'ctorArg: CtorParam', 'reference', 'reject'],
  ['index-signature-parameter', 'signatures', 'indexArg: string', 'indexArg: string', 'reference', 'reject'],
  ['computed-signature-key', 'signatures', 'key](): void', "key = 'slot'", 'reference', 'reject'],
  ['class-type-parameter', 'genericClass', 'ClassParam> {}', 'ClassParam> {}', 'reference', 'reject'],
  ['mapped-type-parameter', 'typeExpressions', "MappedKey in 'a'", "MappedKey in 'a'", 'reference', 'reject'],
  ['infer-type-parameter', 'typeExpressions', 'Inferred> ?', 'Inferred> ?', 'reference', 'reject'],
  ['type-query', 'typeExpressions', 'imported;\n  return true;', external, 'reference', 'reject'],
  ['recursion', 'recursive', 'recursive(); }', 'export function recursive()', 'call', 'correct'],
  ['import-call', 'importedCall', 'imported(); }\nexport function parameterRead', external, 'call', 'correct'],
  ['parameter-read', 'parameterRead', 'value; }', 'value: string', 'reference', 'correct'],
  ['local-variable-read', 'localRead', 'item; }', 'item = true', 'reference', 'correct'],
  ['ordinary-reference', 'referenceOnly', 'imported; }', external, 'reference', 'correct'],
  ['reference-is-not-call', 'referenceOnly', 'imported; }', external, 'call', 'reject'],
  ['shadow-wrong-target', 'shadow', 'imported(); }\nexport function propertyRead', external, 'call', 'reject'],
  ['shadow-correct-target', 'shadow', 'imported(); }\nexport function propertyRead', 'imported: () => boolean', 'call', 'correct'],
  ['runtime-property-type-target', 'propertyRead', 'actualMember;\n}', 'actualMember: string', 'reference', 'correct'],
  ['runtime-method-type-target', 'methodCall', 'runtimeMethod(); }', 'runtimeMethod(): boolean', 'call', 'correct'],
  ['unused-declaration', 'unused', 'unused() {', 'export function unused()', 'reference', 'reject'],
].map(([id, name, use, target, usageKind, expected]) => ({
  id, expected,
  label: { id, contractVersion: 2, kind: 'reference', name, source: location(`export function ${name}(`),
    use: location(use), target: typeof target === 'string' ? location(target) : target, usageKind, unverified: [] },
}));
