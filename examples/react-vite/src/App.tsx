import { useState } from 'react';
import type { ConsultationRequest, Listing, ListingStatus } from './domain';
import { canConfirmRequest, canConsultFromCard, canConsultFromDetail, formatPrice } from './rules';

const initial: Listing = { id: 'listing-01', vehicle: { id: 'vehicle-01', model: 'IONIQ 5', fuel: 'electric' }, status: 'reserved', price: 42000000 };
const labels: Record<ListingStatus, string> = { available: '판매 중', reserved: '예약 중', sold: '판매 완료' };

export function ListingCard({ listing, onConsult }: { listing: Listing; onConsult: () => void }) {
  return <section><p className="eyebrow">매물 카드</p><h2>{listing.vehicle.model}</h2><p>{formatPrice(listing)}</p>
    <p>{labels[listing.status]}</p><button disabled={!canConsultFromCard(listing)} onClick={onConsult}>상담 신청</button>
    <small>카드 조건: 판매 중인 매물</small></section>;
}
export function ListingDetail({ listing, onConsult }: { listing: Listing; onConsult: () => void }) {
  return <section><p className="eyebrow">매물 상세</p><h2>차량 상담</h2><p>차량과 구매 일정에 대해 상담하세요.</p>
    <p>{labels[listing.status]}</p><button disabled={!canConsultFromDetail(listing)} onClick={onConsult}>상담 신청</button>
    <small>상세 조건: 판매 완료가 아닌 매물</small></section>;
}
export default function App() {
  const [listing, setListing] = useState(initial);
  const [request, setRequest] = useState<ConsultationRequest | null>(null);
  const consult = () => setRequest({ id: 'request-01', listingId: listing.id, channel: 'online', state: 'pending' });
  return <main><p className="eyebrow">ONTOSARY · REPRODUCIBLE EXAMPLE</p><h1>같은 매물, 다른 상담 조건</h1>
    <p>매물 상태를 바꿔 두 화면의 동작을 비교하세요. 차이만으로 버그라고 단정할 수는 없습니다.</p>
    <label>매물 상태 <select value={listing.status} onChange={e => { setListing({ ...listing, status: e.target.value as ListingStatus }); setRequest(null); }}>
      <option value="available">판매 중</option><option value="reserved">예약 중</option><option value="sold">판매 완료</option>
    </select></label><div className="cards"><ListingCard listing={listing} onConsult={consult}/><ListingDetail listing={listing} onConsult={consult}/></div>
    <p role="status" aria-live="polite">{request ? `상담 요청: ${request.listingId} · ${canConfirmRequest(request) ? '온라인 확인 가능' : '확인 대기'}` : '아직 상담 요청이 없습니다.'}</p>
    <footer>실험용 예제 · 실제 상담이나 외부 전송은 발생하지 않습니다.</footer></main>;
}
