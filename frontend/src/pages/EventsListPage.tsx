import { Link, useNavigate } from 'react-router-dom';
import type { EventListItem } from '../api/schema';
import { naira } from '../lib/money';
import StatusBadge from '../components/StatusBadge';
import { useEvents } from '../hooks/useEvents';
import Skeleton from '../components/states/Skeleton';
import ErrorState from '../components/states/Error';

export default function EventsListPage() {
  const navigate = useNavigate();
  const { data: events, isLoading, isError, refetch } = useEvents();

  if (isLoading) return <div className="p-8"><Skeleton rows={5} /></div>;
  if (isError || !events) return <div className="p-8"><ErrorState message="Could not load events" onRetry={() => refetch()} /></div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-ink">Your events</h1>
          <p className="text-xs text-muted">Track vendor confirmations and payments in one place</p>
        </div>
        <Link
          to="/events/new"
          className="rounded-btn bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand/90 transition-colors shadow-sm active:scale-95"
        >
          + New event
        </Link>
      </div>

      {events.length === 0 ? (
        <div className="text-center p-12 bg-white rounded-card border border-line">
           <h3 className="text-lg font-bold text-ink">No events yet</h3>
           <p className="text-sm text-muted mt-2">Create your first event to get started.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {events.map((event: EventListItem) => {
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
                  <div className="mt-1.5 h-1.5 w-full rounded-full bg-slate-100 overflow-hidden shadow-inner">
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
      )}
    </div>
  );
}
