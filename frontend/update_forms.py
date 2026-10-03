import os

event_dashboard = """import { useState } from 'react';
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
  const [toastMessage, setToastMessage] = useState('');
  const [isAddingVendor, setIsAddingVendor] = useState(false);

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
      setToastMessage(`${total - failed} sent, ${failed} failed.`);
      refetch();
    } catch (e) {
      setToastMessage('Failed to send confirmations');
    }
  };

  const handleResend = async (e: React.MouseEvent, vendor: Vendor) => {
    e.stopPropagation();
    try {
      await api.post<any>('/notify/send', { event_id: eventId, vendor_ids: [vendor.id] });
      setToastMessage(`Resent to ${vendor.name}`);
      refetch();
    } catch (err) {
      setToastMessage('Failed to resend');
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
      setToastMessage('Vendor added successfully');
      setIsAddingVendor(false);
      reset();
      refetch();
    } catch (err) {
      setToastMessage('Failed to add vendor');
    }
  };

  return (
    <div className="space-y-6 relative">
      {toastMessage && <Toast message={toastMessage} onClose={() => setToastMessage('')} />}
      
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
          <button onClick={() => alert('Edit Event slide is under construction')} className="rounded-btn border border-line bg-white px-4 py-2 text-sm font-medium text-ink hover:bg-slate-50 transition-colors shadow-sm active:scale-95">
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
"""

drawer = """import { useEffect, useState } from 'react';
import type { Vendor, Activity } from '../api/schema';
import { naira } from '../lib/money';
import { formatPhone } from '../lib/phone';
import StatusBadge from './StatusBadge';
import { useForm } from 'react-hook-form';
import { api } from '../api/client';

interface DrawerProps {
  vendor: Vendor;
  activities: Activity[];
  onClose: () => void;
  eventId: number;
  onUpdate: () => void;
}

export default function Drawer({ vendor, activities, onClose, eventId, onUpdate }: DrawerProps) {
  const [isEditing, setIsEditing] = useState(false);
  const { register, handleSubmit } = useForm({
    defaultValues: {
      role: vendor.role,
      name: vendor.name,
      phone: vendor.phone,
      arrival_time: vendor.arrival_time,
      deposit_amount: vendor.deposit.amount / 100,
      balance_amount: vendor.balance.amount / 100
    }
  });

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  const hasPaidOrProcessing = 
    vendor.deposit.status === 'paid' || vendor.deposit.status === 'processing' ||
    vendor.balance.status === 'paid' || vendor.balance.status === 'processing';

  const onEditSubmit = async (data: any) => {
    try {
      await api.patch(`/events/${eventId}/vendors/${vendor.id}`, {
        ...data,
        phone: formatPhone(data.phone),
        deposit_amount: (Number(data.deposit_amount) || 0) * 100,
        balance_amount: (Number(data.balance_amount) || 0) * 100
      });
      setIsEditing(false);
      onUpdate();
    } catch (e) {
      alert('Failed to update vendor');
    }
  };

  const onRemove = async () => {
    if (window.confirm(`Remove ${vendor.name}?`)) {
      try {
        await api.delete(`/events/${eventId}/vendors/${vendor.id}`);
        onUpdate();
        onClose();
      } catch (e) {
        alert('Failed to remove vendor');
      }
    }
  };

  const onResend = async () => {
    try {
      await api.post(`/notify/send`, { event_id: eventId, vendor_ids: [vendor.id] });
      alert('Confirmation resent');
      onUpdate();
    } catch (e) {
      alert('Failed to resend');
    }
  };

  return (
    <>
      <div 
        className="fixed inset-0 bg-ink/30 z-40 transition-opacity backdrop-blur-sm"
        onClick={onClose}
      />
      <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-surface shadow-2xl overflow-y-auto transform transition-transform border-l border-line flex flex-col">
        <div className="bg-white px-6 py-5 border-b border-line shrink-0">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-xl font-bold text-ink">{vendor.name}</h2>
              <p className="text-sm text-muted mt-1">
                {vendor.role} | {vendor.phone} | {vendor.arrival_time} arrival
              </p>
              <div className="mt-3">
                <StatusBadge status={vendor.status} />
              </div>
            </div>
            <button 
              onClick={onClose}
              className="text-muted hover:text-ink text-2xl font-light leading-none px-2 -mt-1 -mr-2"
            >
              &times;
            </button>
          </div>
        </div>

        <div className="p-6 space-y-8 flex-1">
          {isEditing ? (
            <form id="edit-vendor-form" onSubmit={handleSubmit(onEditSubmit)} className="space-y-4 bg-white p-4 rounded border border-line">
              <h3 className="text-sm font-semibold text-ink">Edit Vendor Details</h3>
              <div><label className="text-xs text-muted">Role</label><input {...register('role')} className="w-full border rounded px-2 py-1 text-sm" /></div>
              <div><label className="text-xs text-muted">Name</label><input {...register('name')} className="w-full border rounded px-2 py-1 text-sm" /></div>
              <div><label className="text-xs text-muted">Phone</label><input {...register('phone')} className="w-full border rounded px-2 py-1 text-sm" /></div>
              <div><label className="text-xs text-muted">Arrival</label><input {...register('arrival_time')} type="time" className="w-full border rounded px-2 py-1 text-sm" /></div>
              <div><label className="text-xs text-muted">Deposit (NGN)</label><input {...register('deposit_amount')} type="number" disabled={hasPaidOrProcessing} className="w-full border rounded px-2 py-1 text-sm disabled:opacity-50" /></div>
              <div><label className="text-xs text-muted">Balance (NGN)</label><input {...register('balance_amount')} type="number" disabled={hasPaidOrProcessing} className="w-full border rounded px-2 py-1 text-sm disabled:opacity-50" /></div>
              <div className="flex justify-end gap-2 mt-4">
                <button type="button" onClick={() => setIsEditing(false)} className="text-sm px-3 py-1 border rounded">Cancel</button>
                <button type="submit" className="text-sm px-3 py-1 bg-brand text-white rounded">Save</button>
              </div>
            </form>
          ) : (
            <>
              <div>
                <h3 className="text-sm font-semibold text-ink mb-4">Message timeline</h3>
                <div className="space-y-4">
                  {activities.length > 0 ? (
                    activities.map((act, index) => (
                      <div key={act.id} className="flex gap-3 items-start relative">
                        <div className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-brand z-10 relative" />
                        {index !== activities.length - 1 && (
                          <div className="absolute left-[3px] top-4 bottom-[-16px] w-[2px] bg-line" />
                        )}
                        <div className="flex-1">
                          <p className="text-sm text-ink">{act.text}</p>
                        </div>
                        <p className="text-xs text-muted shrink-0">
                          {new Date(act.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </p>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-muted">No message activity yet.</p>
                  )}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-ink mb-4">Payments</h3>
                <div className="space-y-3 bg-white p-4 rounded-card border border-line">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted">Deposit</span>
                    <div className="flex items-center gap-4">
                      <span className="text-sm font-semibold text-ink">{naira(vendor.deposit.amount)}</span>
                      <div className="w-[72px] text-right"><StatusBadge status={vendor.deposit.status} /></div>
                    </div>
                  </div>
                  <div className="flex items-center justify-between pt-3 border-t border-line/50">
                    <span className="text-sm text-muted">Balance</span>
                    <div className="flex items-center gap-4">
                      <span className="text-sm font-semibold text-ink">{naira(vendor.balance.amount)}</span>
                      <div className="w-[72px] text-right"><StatusBadge status={vendor.balance.status} /></div>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>

        {!isEditing && (
          <div className="bg-white p-5 border-t border-line shrink-0 flex items-center gap-3">
            {vendor.status !== 'confirmed' ? (
              <button onClick={onResend} className="flex-1 rounded-btn bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand/90 transition-colors">
                Resend confirmation
              </button>
            ) : (
              <div className="flex-1" />
            )}
            
            <div className="flex gap-3 shrink-0">
              <button onClick={() => setIsEditing(true)} className="rounded-btn border border-line bg-white px-4 py-2 text-sm font-medium text-ink hover:bg-slate-50 transition-colors">
                Edit
              </button>
              <button 
                onClick={onRemove}
                disabled={hasPaidOrProcessing}
                title={hasPaidOrProcessing ? "Cannot remove vendor with active payments" : ""}
                className="rounded-btn border border-status-declined/30 text-status-declined px-4 py-2 text-sm font-medium hover:bg-red-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Remove
              </button>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
"""

with open('src/pages/EventDashboardPage.tsx', 'w') as f:
    f.write(event_dashboard)

with open('src/components/Drawer.tsx', 'w') as f:
    f.write(drawer)

print("Updated drawer and dashboard")
