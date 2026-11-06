export type ListingStatus = 'available' | 'reserved' | 'sold';
export interface Vehicle {
  id: string;
  model: string;
  fuel: 'electric' | 'hybrid' | 'gasoline';
}
export interface Listing {
  id: string;
  vehicle: Vehicle;
  status: ListingStatus;
  price: number;
}
export interface ConsultationRequest {
  id: string;
  listingId: Listing['id'];
  channel: 'online' | 'phone';
  state: 'pending' | 'confirmed' | 'cancelled';
}
// Intentionally structurally identical; these must retain separate identities.
export interface User { id: string; name: string }
export interface Customer { id: string; name: string }
