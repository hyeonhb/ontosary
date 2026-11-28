enum Stage { Pending, Confirmed }
export const isPending = (s: Stage) => s === Stage.Pending;
export const notConfirmed = (s: Stage) => s !== Stage.Confirmed;
const fromNumber: number = 99;
const value: Stage = fromNumber;
export const results = [isPending(value), notConfirmed(value)];

export function pendingBranch(s: Stage) {
  if (s === Stage.Pending) return true;
  return false;
}
