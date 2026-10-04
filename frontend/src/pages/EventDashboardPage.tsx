import { useState } from 'react';
import { useParams, Link, useSearchParams } from 'react-router-dom';
import { formatDate } from '../lib/time';
import type { VendorStatus, Vendor } from '../api/schema';
import LivePill from '../components/LivePill';
import StatCard from '../components/StatCard';
import StatusBadge from '../components/StatusBadge';
import ActivityFeed from '../components/ActivityFeed';
import Drawer from '../components/Drawer';
import { useEventStatus } from '../hooks/useEventStatus';
import Skeleton from '../components/states/Skeleton';
import ErrorState from '../components/states/Error';
import { api } from '../api/client';
import { Toast } from '../components/Toast';
import { useForm } from 'react-hook-form';
import { formatPhone } from '../lib/phone';

export default function EventDashboardPage() {
  const { id } = useParams();
  const eventId = Number(id);
  const [searchParams, setSearchParams] = useSearchParams();
  const vendorIdParam = searchParams.get('vendor');

  const { data: statusData, isLoading, isError, refetch } = useEventStatus(eventId);
  const [toast, setToast] = useState<{message: string, type: 'success' | 'error'} | null>(null);
  const [isAddingVendor, setIsAddingVendor] = useState(false);

  const [isEditSlideOpen, setIsEditSlideOpen] = useState(false);
  const { register: registerEvent, handleSubmit: handleEventSubmit } = useForm();

  const onEditEvent = async (data: any) => {
    try {
      await api.patch(`/events/${eventId}`, data);
      setToast({message: 'Event updated successfully', type: 'success'});
      setIsEditSlideOpen(false);
      refetch();
    } catch (e) {
      setToast({message: 'Failed to update event', type: 'error'});
    }
  };


  const { register, handleSubmit, reset } = useForm();

  if (isLoading) return <div className="p-8"><Skeleton rows={5} /></div>;
  if (isError || !statusData) return <div className="p-8"><ErrorState message="Could not load event data" onRetry={() => refetch()} /></div>;

  const { event, summary, vendors, activity } = statusData;

  const selectedVendor = vendorIdParam ? vendors.find((v: Vendor) => v.id === Number(vendorIdParam)) : null;
  const vendorActivities = vendorIdParam ? activity.filter((a: any) => a.vendor_id === Number(vendorIdParam)) : [];

  const closeDrawer = () => {
    searchParams.delete('vendor');
    setSearchParams(searchParams);
  };

  const handleSendConfirmations = async () => {
    try {
      const res = await api.post<any>('/notify/send', { event_id: eventId });
      const total = res.results?.length || 0;
      const failed = res.results?.filter((r: any) => !r.ok).length || 0;
      setToast({message: `${total - failed} sent, ${failed} failed.`, type: 'error'});
      refetch();
    } catch (e) {
      setToast({message: 'Failed to send confirmations', type: 'error'});
    }
  };

  const handleResend = async (e: React.MouseEvent, vendor: Vendor) => {
    e.stopPropagation();
    try {
      await api.post<any>('/notify/send', { event_id: eventId, vendor_ids: [vendor.id] });
      setToast({message: `Resent to ${vendor.name}`, type: 'success'});
      refetch();
    } catch (err) {
      setToast({message: 'Failed to resend', type: 'error'});
    }
  };

  const onAddVendor = async (data: any) => {
    try {
      await api.post<any>(`/events/${eventId}/vendors`, {
        ...data,
        phone: formatPhone(data.phone),
        deposit_amount: (Number(data.deposit) || 0) * 100,
        balance_amount: (Number(data.balance) || 0) * 100
      });
      setToast({message: 'Vendor added successfully', type: 'success'});
      setIsAddingVendor(false);
      reset();
      refetch();
    } catch (err) {
      setToast({message: 'Failed to add vendor', type: 'error'});
    }
  };

  return (
    <div className="space-y-6 relative">
      {toast?.message && <Toast message={toast?.message} onClose={() => setToast({message: '', type: 'success'})} />}
      
      {/* Header section */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-ink tracking-tight">{event.name}</h1>
            <LivePill />
          </div>
          <p className="text-sm text-muted mt-1.5 font-medium">
            {formatDate(event.event_date)} <span className="opacity-50 mx-1">•</span> {event.start_time} <span className="opacity-50 mx-1">•</span> {event.venue}
          </p>
        </div>
        <div className="flex gap-3">
          <button onClick={() => setIsEditSlideOpen(true)} className="rounded-btn border border-line bg-white px-4 py-2 text-sm font-medium text-ink hover:bg-slate-50 transition-colors shadow-sm active:scale-95">
            Edit
          </button>
          <button onClick={handleSendConfirmations} className="rounded-btn bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand/90 transition-colors shadow-sm active:scale-95">
            Send confirmations
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-line flex gap-6">
        <Link to={`/events/${id}`} className="pb-3 border-b-2 border-brand font-semibold text-brand text-sm">
          Vendors
        </Link>
        <Link to={`/events/${id}/budget`} className="pb-3 border-b-2 border-transparent text-muted hover:text-ink font-medium text-sm transition-colors">
          Budget
        </Link>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Total vendors" value={summary.total} />
        <StatCard label="Confirmed" value={summary.confirmed} valueColor="text-status-confirmed" />
        <StatCard label="Awaiting reply" value={summary.sent} valueColor="text-status-awaiting" />
        <StatCard label="Declined" value={summary.declined} valueColor="text-status-declined" />
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 rounded-card border border-line bg-white overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-300">
          <table className="w-full text-left text-sm">
            <thead className="bg-surface border-b border-line">
              <tr>
                <th className="px-5 py-3.5 font-semibold text-muted uppercase tracking-wider text-[11px]">Role</th>
                <th className="px-5 py-3.5 font-semibold text-muted uppercase tracking-wider text-[11px]">Vendor</th>
                <th className="px-5 py-3.5 font-semibold text-muted uppercase tracking-wider text-[11px]">Arrival</th>
                <th className="px-5 py-3.5 font-semibold text-muted uppercase tracking-wider text-[11px]">Status</th>
                <th className="px-5 py-3.5"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line/50">
              {vendors.map((vendor: Vendor) => (
                <tr 
                  key={vendor.id} 
                  onClick={() => setSearchParams({ vendor: vendor.id.toString() })}
                  className="hover:bg-slate-50 cursor-pointer transition-all duration-200 group"
                >
                  <td className="px-5 py-4.5 text-muted font-medium">{vendor.role}</td>
                  <td className="px-5 py-4.5 font-bold text-ink group-hover:text-brand transition-colors">{vendor.name}</td>
                  <td className="px-5 py-4.5 text-muted">{vendor.arrival_time}</td>
                  <td className="px-5 py-4.5">
                    <StatusBadge status={vendor.status as VendorStatus} />
                  </td>
                  <td className="px-5 py-4.5 text-right">
                    {['sent', 'declined', 'failed'].includes(vendor.status) ? (
                      <button 
                        onClick={(e) => handleResend(e, vendor)}
                        className="text-brand font-semibold text-xs hover:underline bg-brand/5 px-3 py-1.5 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        Resend
                      </button>
                    ) : (
                      <span className="text-muted text-xs opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-end font-medium">
                        View details &rarr;
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="p-4 border-t border-line bg-surface/50">
             {!isAddingVendor ? (
               <button 
                 onClick={() => setIsAddingVendor(true)}
                 className="text-sm font-semibold text-brand hover:text-brand/80 transition-colors flex items-center gap-1 active:scale-95"
               >
                 <span className="text-lg leading-none">+</span> Add vendor
               </button>
             ) : (
               <form onSubmit={handleSubmit(onAddVendor)} className="flex items-center gap-2">
                 <input {...register('role')} placeholder="Role" className="rounded-input border px-2 py-1 text-sm w-24" required />
                 <input {...register('name')} placeholder="Name" className="rounded-input border px-2 py-1 text-sm flex-1" required />
                 <input {...register('phone')} placeholder="Phone" className="rounded-input border px-2 py-1 text-sm w-32" required />
                 <input {...register('arrival_time')} type="time" className="rounded-input border px-2 py-1 text-sm w-24" />
                 <input {...register('deposit')} type="number" placeholder="Deposit" className="rounded-input border px-2 py-1 text-sm w-24" />
                 <input {...register('balance')} type="number" placeholder="Balance" className="rounded-input border px-2 py-1 text-sm w-24" />
                 <button type="submit" className="rounded bg-brand text-white px-3 py-1 text-sm font-semibold">Save</button>
                 <button type="button" onClick={() => setIsAddingVendor(false)} className="rounded border px-3 py-1 text-sm">Cancel</button>
               </form>
             )}
          </div>
        </div>

        <div className="lg:col-span-1">
          <ActivityFeed activities={activity} />
        </div>
      </div>

      
      {/* Event Edit Slide-over */}
      {isEditSlideOpen && (
        <>
          <div className="fixed inset-0 bg-ink/30 z-40 transition-opacity backdrop-blur-sm" onClick={() => setIsEditSlideOpen(false)} />
          <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-surface shadow-2xl overflow-y-auto border-l border-line p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-ink">Edit Event</h2>
              <button onClick={() => setIsEditSlideOpen(false)} className="text-muted hover:text-ink text-2xl font-light">&times;</button>
            </div>
            <form onSubmit={handleEventSubmit(onEditEvent)} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-ink mb-1">Event Name</label>
                <input {...registerEvent('name')} defaultValue={event.name} className="w-full rounded-input border border-line px-3 py-2 text-sm" required />
              </div>
              <div>
                <label className="block text-sm font-medium text-ink mb-1">Date</label>
                <input {...registerEvent('event_date')} type="date" defaultValue={event.event_date} className="w-full rounded-input border border-line px-3 py-2 text-sm" required />
              </div>
              <div>
                <label className="block text-sm font-medium text-ink mb-1">Time</label>
                <input {...registerEvent('start_time')} type="time" defaultValue={event.start_time} className="w-full rounded-input border border-line px-3 py-2 text-sm" required />
              </div>
              <div>
                <label className="block text-sm font-medium text-ink mb-1">Venue</label>
                <input {...registerEvent('venue')} defaultValue={event.venue} className="w-full rounded-input border border-line px-3 py-2 text-sm" required />
              </div>
              <div className="pt-4 flex justify-end gap-3">
                <button type="button" onClick={() => setIsEditSlideOpen(false)} className="px-4 py-2 text-sm border rounded">Cancel</button>
                <button type="submit" className="px-4 py-2 text-sm bg-brand text-white rounded">Save Changes</button>
              </div>
            </form>
          </div>
        </>
      )}

      {selectedVendor && (
        <Drawer 
          vendor={selectedVendor} 
          activities={vendorActivities} 
          onClose={closeDrawer}
          eventId={eventId}
          onUpdate={refetch}
        />
      )}
    </div>
  );
}
