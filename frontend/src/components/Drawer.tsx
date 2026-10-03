import { useEffect, useState } from 'react';
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
