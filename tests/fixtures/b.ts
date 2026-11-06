export interface Item { status: 'available' | 'reserved' | 'sold' }
export function check(item: Item) { return item.status !== 'sold'; }
