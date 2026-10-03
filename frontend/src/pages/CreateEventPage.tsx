
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import VendorGrid, { type EventFormValues,  } from '../components/VendorGrid';
import { api } from '../api/client';
import { Toast } from '../components/Toast';

export default function CreateEventPage() {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorToast, setErrorToast] = useState('');
  
  const { register, control, handleSubmit, watch, setError } = useForm<EventFormValues>({
    defaultValues: {
      name: '',
      date: '',
      start_time: '',
      venue: '',
      vendors: Array(5).fill({ role: '', name: '', phone: '', arrival_time: '', deposit: '', balance: '' })
    }
  });

  const onSubmit = async (data: EventFormValues, e: any) => {
    setIsSubmitting(true);
    const submitAction = e?.nativeEvent?.submitter?.value; // 'draft' or 'send'
    
    try {
      // Filter out entirely empty vendor rows
      const filledVendors = data.vendors.filter(v => v.name || v.role || v.phone);
      
      const payload = {
        ...data,
        event_date: data.date,
        vendors: filledVendors.map(v => ({
          role: v.role,
          name: v.name,
          phone: v.phone,
          arrival_time: v.arrival_time,
          deposit_amount: (Number(v.deposit) || 0) * 100,
          balance_amount: (Number(v.balance) || 0) * 100
        }))
      };

      // 1. Create Event (E1)
      const newEvent = await api.post<any>('/events', payload);
      
      // 2. If 'send', call E8
      if (submitAction === 'send' && newEvent.id && newEvent.vendors?.length > 0) {
        const vendorIds = newEvent.vendors.map((v: any) => v.id);
        const notifyRes = await api.post<any>('/notify/send', {
          event_id: newEvent.id,
          vendor_ids: vendorIds
        });
        
        const failed = notifyRes.results?.filter((r: any) => !r.ok).length || 0;
        if (failed > 0) {
          setErrorToast(`${failed} of ${vendorIds.length} failed. Resend from the dashboard.`);
          // Still navigate, just maybe show toast on dashboard (in real app using context)
        }
      }
      
      navigate(`/events/${newEvent.id}`);
      
    } catch (err: any) {
      if (err?.error?.code === 'VALIDATION_ERROR' && err.error.fields) {
        Object.entries(err.error.fields).forEach(([field, message]) => {
          setError(field as any, { type: 'server', message: String(message) });
        });
        setErrorToast('Check the highlighted fields');
      } else {
        setErrorToast('Something went wrong');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <h1 className="text-xl font-semibold text-ink">New event</h1>
      {errorToast && <Toast message={errorToast} type="error" onClose={() => setErrorToast('')} />}

      <div className="rounded-card border border-line bg-white p-5">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
          <div className="sm:col-span-2">
            <label className="mb-1 block text-xs font-medium text-muted">Event name</label>
            <input
              {...register('name', { required: true })}
              disabled={isSubmitting}
              className="w-full rounded-input border border-line px-3 py-2 text-sm focus:border-brand focus:outline-none disabled:opacity-50"
              placeholder="e.g. Amara's 30th Birthday Gala"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-muted">Date</label>
            <input
              type="date"
              {...register('date')}
              disabled={isSubmitting}
              className="w-full rounded-input border border-line px-3 py-2 text-sm focus:border-brand focus:outline-none disabled:opacity-50"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-muted">Start time</label>
            <input
              type="time"
              {...register('start_time')}
              disabled={isSubmitting}
              className="w-full rounded-input border border-line px-3 py-2 text-sm focus:border-brand focus:outline-none disabled:opacity-50"
            />
          </div>
          <div className="sm:col-span-4">
            <label className="mb-1 block text-xs font-medium text-muted">Venue</label>
            <input
              {...register('venue')}
              disabled={isSubmitting}
              className="w-full rounded-input border border-line px-3 py-2 text-sm focus:border-brand focus:outline-none disabled:opacity-50"
              placeholder="e.g. Eko Hotel, Lagos"
            />
          </div>
        </div>
      </div>

      <fieldset disabled={isSubmitting} className="disabled:opacity-75">
        <VendorGrid control={control} register={register} watch={watch} />
      </fieldset>
    </form>
  );
}
