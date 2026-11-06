import type { ConsultationRequest, Listing, Vehicle } from './domain';

// UI-specific examples, not an assertion of the service's official policy.
export function canConsultFromCard(listing: Listing) {
  return listing.status === 'available';
}
export function canConsultFromDetail(listing: Listing) {
  return listing.status !== 'sold';
}
export const canConsultEquivalent = (item: Listing) => !(item.status !== 'available');
export function canConsultReserved(listing: Listing) {
  return listing.status === 'reserved';
}
export function canConfirmRequest(request: ConsultationRequest) {
  return request.state === 'pending' && request.channel === 'online';
}
export function isElectric(vehicle: Vehicle) {
  return vehicle.fuel === 'electric';
}
export function formatPrice(listing: Listing) {
  return `${listing.price.toLocaleString('ko-KR')}원`;
}
// Expected unsupported case: numeric range plus arithmetic is outside this PoC.
export function isPremium(listing: Listing) {
  return listing.price > 50_000_000;
}
