import { Link, useNavigate } from 'react-router-dom';
import { mockEventsList } from '../mocks/fixtures';
import type { EventListItem } from '../api/schema';
import { naira } from '../lib/money';
import StatusBadge from '../components/StatusBadge';

export default function EventsListPage() {
  const navigate = useNavigate();
  // 1. Cast the mock data array to the strict TypeScript type
  const events = mockEventsList as EventListItem[];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-ink">Your events</h1>
          <p className="text-xs text-muted">Track vendor confirmations and payments in one place</p>
        </div>
        <Link
          to="/events/new"
          className="rounded-btn bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand/90 transition-colors"
        >
          + New event
        </Link>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {/* 2. Remove the explicit EventListItem type here since 'events' is now correctly typed */}
        {events.map((event) => {
          const progressPercent =
            event.vendor_count > 0 ? (event.confirmed_count / event.vendor_count) * 100 : 0;

          return (
            <div
              key={event.id}
              onClick={() => navigate(`/events/${event.id}`)}
              className="cursor-pointer rounded-card border border-line bg-white p-5 transition-shadow hover:shadow-sm"
            >
              <h2 className="text-base font-semibold text-ink">{event.name}</h2>
              <p className="mt-1 text-xs text-muted">{event.event_date}</p>
              <p className="text-xs text-muted">{event.venue}</p>

              <div className="mt-4">
                <div className="flex justify-between text-xs text-muted">
                  <span>
                    {event.confirmed_count} of {event.vendor_count} confirmed
                  </span>
                </div>
                <div className="mt-1.5 h-1.5 w-full rounded-full bg-slate-100 overflow-hidden">
                  <div
                    className="h-full bg-status-confirmed transition-all duration-300"
                    style={{ width: `${progressPercent}%` }}
                  />
                </div>
              </div>

              <div className="mt-4 flex items-center justify-between border-t border-line pt-3">
                <div>
                  <span className="block text-[10px] uppercase font-medium text-muted">Total budget</span>
                  <span className="text-sm font-semibold text-ink">{naira(event.total_budget)}</span>
                </div>
                <StatusBadge status={event.status as 'active' | 'draft'} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
