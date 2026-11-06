// Controlled, executable regression fixture. Never execute scanned user projects.
export type S = 'a' | 'b';
export enum E { A = 'a', B = 'b' }
export enum N { A, B }
export function optionalEnum(e?: typeof E) { return e?.A === 'a'; }
export function always(e?: typeof E) { return true; }
export function getEnum(): typeof E { throw new Error('not total'); }
export function callEnum(e?: typeof E) { return getEnum().A === 'a'; }
export function reversedCall() { return 'a' === getEnum().A; }
export function wrappedCall() { return ((getEnum())).A === 'a'; }
export function assertedEnum(e?: typeof E) { return (e as typeof E).A === 'a'; }
export function nonNullEnum(e?: typeof E) { return e!.A === 'a'; }
export function parameterEnum(e: typeof E) { return e.A === 'a'; }
export function nestedEnum(box: { e: typeof E }) { return box.e.A === 'a'; }
export function nestedOptional(box: { e?: typeof E }) { return box.e?.A === 'a'; }
export function optionalParent(box?: { e: typeof E }) { return box?.e.A === 'a'; }
export function assertedDirect() { return (E as typeof E).A === 'a'; }
export function computedEnum() { return E['A'] === 'a'; }
export function optionalDirect() { return E?.A === 'a'; }
const alias = E;
export function aliasedObject() { return alias.A === 'a'; }
type EnumObject = typeof E;
export function shadowedEnum(E: EnumObject) { return E.A === 'a'; }
export function underAnd(s: S, e?: typeof E) { return s === 'a' && e?.A === 'a'; }
export function underNot() { return !(getEnum().A !== 'a'); }
export function underConstant() { return false && getEnum().A === 'a'; }
export class Holder { get e(): typeof E { throw new Error('getter evaluated'); } }
export function accessorEnum(holder: Holder) { return holder.e.A === 'a'; }
export namespace Domain { export enum Nested { A = 'a', B = 'b' } }
export function namespacedEnum(s: S) { return s === Domain.Nested.A; }

export function withThis(this: void, a: S, b: S) { return a === 'a'; }
export function first(a: S, b: S) { return a === 'a'; }
export function second(a: S, b: S) { return b === 'a'; }
export function withThisConstant(this: void) { return true; }
export function thisBranch(this: void, a: S) {
  if (a === 'a') return true;
  return false;
}
export const methods = {
  withThisMethod(this: void, a: S, b: S) { return b === 'a'; },
};

export function directEnum(s: S, other: S) { return s === E.A; }
export function reverseEnum(s: S, other: S) { return E.A === s; }
export function enumParameter(e: E) { return e === E.A; }
export function numericEnum(n: N) { return n === N.A; }
export function numericComplement(n: N) { return !(n !== N.A); }
export function directConstant(s: S, other: S) { return E.A === 'a'; }
export function parenthesizedEnum(s: S, other: S) { return s === ((E)).A; }
export function negated(s: S, other: S) { return !(s === E.A); }
export function nestedLogic(s: S, other: S) { return (s === E.A || other === E.B) && !(s !== E.A && other !== E.B); }
export function nestedEquivalent(s: S, other: S) { return s === 'a' || other === 'b'; }
