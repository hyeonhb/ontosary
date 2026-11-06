import { check as importedCheck, type Item as ImportedItem } from './a';
export function usesAlias(item: ImportedItem) { return importedCheck(item); }
type Status = 'available' | 'reserved' | 'sold';
export const primitive = (status: Status) => status === 'available';
export const reversed = (status: Status) => 'available' === status;
export const complement = (status: Status) => !(status === 'available');
export const wide = (status: Status) => status === 'available' || status === 'reserved';
export const deMorgan = (status: Status) => !(status !== 'available' && status !== 'reserved');
export const outside = (status: 'available' | 'sold') => status === 'available';
export const unbounded = (status: string) => status === 'available';
export const loose = (status: Status) => status == 'available';
export const call = (status: Status) => status.startsWith('a');
export const optional = (item: { status?: Status }) => item.status === 'available';
export const optionalChain = (item?: { status: Status }) => item?.status === 'available';
export const destructured = ({ status }: { status: Status }) => status === 'available';
export const asyncPredicate = async (status: Status) => status === 'available';
export function mutation(status: Status) { status = 'sold'; return status !== 'available' as string; }
export function narrowed(status: Status) {
  if (status === 'available') return status === 'available';
  return status !== 'sold';
}
export function shadow(status: Status) {
  return ['x'].some(status => status === 'available');
}
export enum Channel { Online = 'online', Phone = 'phone' }
export const enumOnline = (channel: Channel) => channel === Channel.Online;
export const enumPhone = (channel: Channel) => channel !== Channel.Phone;
export enum Stage { Pending, Confirmed, Cancelled }
export const numericEnum = (stage: Stage) => stage === Stage.Pending;
export const numericEnumEquivalent = (stage: Stage) => !(stage !== Stage.Pending);
export const twoVariables = (a: Status, b: Status) => a === 'available' && b !== 'sold';
export const all = (_a: Status) => true;
export const none = (_a: Status) => false;
export const computed = (item: ImportedItem) => item['status'] === 'available';
export const correlated = (item: { kind: 'a'; status: 'available' } | { kind: 'b'; status: 'sold' }) => item.status === 'available';
export class WithAccessor { get status(): Status { return 'available'; } }
export const accessor = (item: WithAccessor) => item.status === 'available';
export function defaults(status: Status, other = console.log('side effect')) { return status === 'available'; }
