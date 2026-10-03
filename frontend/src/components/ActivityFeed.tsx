import type { Activity } from '../api/schema';

export default function ActivityFeed({ activities }: { activities: Activity[] }) {
  return (
    <div className="rounded-card border border-line bg-white p-5 h-full shadow-sm">
      <h2 className="text-base font-semibold text-ink mb-4">Live activity</h2>
      <div className="space-y-4">
        {activities.map((activity) => (
          <div key={activity.id} className="flex gap-3">
            <div className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-status-confirmed" />
            <div>
              <p className="text-sm text-ink">{activity.text}</p>
              <p className="text-xs text-muted">
                {new Date(activity.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
