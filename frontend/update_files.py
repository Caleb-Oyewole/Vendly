import os

vendor_grid = """import React, { useState } from 'react';
import { useFieldArray, type Control, type UseFormRegister, type UseFormWatch } from 'react-hook-form';
import { naira } from '../lib/money';
import { formatPhone } from '../lib/phone';

export interface VendorFormRow {
  role: string;
  name: string;
  phone: string;
  arrival_time: string;
  deposit: string | number;
  balance: string | number;
}

export interface EventFormValues {
  name: string;
  date: string;
  start_time: string;
  venue: string;
  vendors: VendorFormRow[];
}

interface VendorGridProps {
  control: Control<EventFormValues>;
  register: UseFormRegister<EventFormValues>;
  watch: UseFormWatch<EventFormValues>;
}

export default function VendorGrid({ control, register, watch }: VendorGridProps) {
  const { fields, append, remove, replace } = useFieldArray({
    control,
    name: 'vendors',
  });

  const [showPaste, setShowPaste] = useState(false);
  const [pasteData, setPasteData] = useState('');

  const vendors = watch('vendors') || [];
  
  const totals = vendors.reduce(
    (acc: { deposits: number; balances: number }, vendor: VendorFormRow) => {
      const dep = Number(vendor.deposit) || 0;
      const bal = Number(vendor.balance) || 0;
      return { deposits: acc.deposits + dep, balances: acc.balances + bal };
    },
    { deposits: 0, balances: 0 }
  );

  const grandTotal = totals.deposits + totals.balances;

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    if (e.key === 'Enter' && index === fields.length - 1) {
      e.preventDefault();
      append({ role: '', name: '', phone: '', arrival_time: '', deposit: '', balance: '' });
    }
  };

  const handlePaste = () => {
    if (!pasteData.trim()) return;
    const lines = pasteData.split('\\n');
    const newVendors: VendorFormRow[] = [];
    
    for (const line of lines) {
      if (!line.trim()) continue;
      const cols = line.split('\\t');
      newVendors.push({
        role: cols[0] || '',
        name: cols[1] || '',
        phone: formatPhone(cols[2] || ''),
        arrival_time: cols[3] || '',
        deposit: cols[4] || '',
        balance: cols[5] || ''
      });
    }
    
    // Replace empty initial rows if they haven't been touched
    const isInitialEmpty = vendors.length === 5 && vendors.every((v: VendorFormRow) => !v.role && !v.name && !v.phone);
    if (isInitialEmpty) {
      replace(newVendors);
    } else {
      append(newVendors);
    }
    
    setPasteData('');
    setShowPaste(false);
  };

  return (
    <div className="rounded-card border border-line bg-white p-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-base font-semibold text-ink">Vendors</h2>
        <span className="text-xs font-medium text-muted">{fields.length} vendors</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-line text-xs font-medium text-muted">
              <th className="pb-3 font-medium">Role</th>
              <th className="pb-3 font-medium">Vendor name</th>
              <th className="pb-3 font-medium">WhatsApp phone</th>
              <th className="pb-3 font-medium">Arrival</th>
              <th className="pb-3 font-medium">Deposit</th>
              <th className="pb-3 font-medium">Balance</th>
              <th className="pb-3"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line/50">
            {fields.map((field, index) => (
              <tr key={field.id}>
                <td className="py-2 pr-2">
                  <input
                    list="roles"
                    {...register(`vendors.${index}.role` as const)}
                    className="w-full rounded-input border border-line px-3 py-1.5 text-sm focus:border-brand focus:outline-none"
                    placeholder="e.g. DJ"
                  />
                  <datalist id="roles">
                    <option value="DJ" />
                    <option value="Caterer" />
                    <option value="Photographer" />
                    <option value="Decorator" />
                    <option value="MC" />
                    <option value="Security" />
                  </datalist>
                </td>
                <td className="py-2 pr-2">
                  <input
                    {...register(`vendors.${index}.name` as const)}
                    className="w-full rounded-input border border-line px-3 py-1.5 text-sm focus:border-brand focus:outline-none"
                    placeholder="Vendor name"
                  />
                </td>
                <td className="py-2 pr-2">
                  <input
                    {...register(`vendors.${index}.phone` as const, {
                      setValueAs: v => formatPhone(v),
                      pattern: { value: /^\\+[1-9]\\d{7,14}$/, message: "Use intl format e.g. +2348012345671" }
                    })}
                    className="w-full rounded-input border border-line px-3 py-1.5 text-sm focus:border-brand focus:outline-none"
                    placeholder="+234..."
                  />
                </td>
                <td className="py-2 pr-2">
                  <input
                    type="time"
                    {...register(`vendors.${index}.arrival_time` as const)}
                    className="w-full rounded-input border border-line px-3 py-1.5 text-sm focus:border-brand focus:outline-none"
                  />
                </td>
                <td className="py-2 pr-2">
                  <input
                    type="number"
                    min="0"
                    {...register(`vendors.${index}.deposit` as const)}
                    className="w-full rounded-input border border-line px-3 py-1.5 text-sm focus:border-brand focus:outline-none"
                    placeholder="0"
                  />
                </td>
                <td className="py-2 pr-2">
                  <input
                    type="number"
                    min="0"
                    {...register(`vendors.${index}.balance` as const)}
                    onKeyDown={(e) => handleKeyDown(e, index)}
                    className="w-full rounded-input border border-line px-3 py-1.5 text-sm focus:border-brand focus:outline-none"
                    placeholder="0"
                  />
                </td>
                <td className="py-2 text-center text-muted">
                  <button type="button" onClick={() => remove(index)} className="hover:text-status-declined px-2">
                    &times;
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 flex flex-col gap-4">
        <div className="flex items-center gap-4">
          <button
            type="button"
            onClick={() => append({ role: '', name: '', phone: '', arrival_time: '', deposit: '', balance: '' })}
            className="text-sm font-medium text-brand hover:underline"
          >
            + Add vendor
          </button>
          <button type="button" onClick={() => setShowPaste(!showPaste)} className="text-sm font-medium text-brand hover:underline">
            Paste from spreadsheet
          </button>
        </div>
        
        {showPaste && (
          <div className="p-4 border border-line rounded-card bg-surface/50">
            <p className="text-xs text-muted mb-2">Paste tab-separated rows: Role, Name, Phone, Arrival, Deposit, Balance</p>
            <textarea
              className="w-full p-2 border border-line rounded text-sm mb-2 focus:outline-none focus:border-brand"
              rows={4}
              value={pasteData}
              onChange={(e) => setPasteData(e.target.value)}
              placeholder="DJ	Kola Beats	08012345671	14:00	50000	100000"
            />
            <div className="flex justify-end gap-2">
              <button type="button" onClick={() => setShowPaste(false)} className="text-xs px-3 py-1 border border-line rounded hover:bg-slate-50">Cancel</button>
              <button type="button" onClick={handlePaste} className="text-xs px-3 py-1 bg-brand text-white rounded hover:bg-brand/90">Import</button>
            </div>
          </div>
        )}
      </div>

      <div className="mt-6 flex flex-col sm:flex-row sm:items-center justify-between rounded-card bg-surface p-4 border border-line">
        <div>
          <div className="flex gap-4 text-xs font-medium text-muted">
            <span>Deposits {naira(totals.deposits * 100)}</span>
            <span>Balances {naira(totals.balances * 100)}</span>
          </div>
          <div className="mt-1 text-lg font-semibold text-ink">Total {naira(grandTotal * 100)}</div>
        </div>
        <div className="mt-4 flex gap-3 sm:mt-0">
          <button type="submit" name="action" value="draft" className="rounded-btn border border-line bg-white px-4 py-2 text-sm font-medium text-ink hover:bg-slate-50">
            Save draft
          </button>
          <button type="submit" name="action" value="send" className="rounded-btn bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand/90">
            Create and send confirmations
          </button>
        </div>
      </div>
    </div>
  );
}
"""

create_event_page = """import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import VendorGrid, { type EventFormValues, type VendorFormRow } from '../components/VendorGrid';
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
"""

with open('src/components/VendorGrid.tsx', 'w') as f:
    f.write(vendor_grid)
    
with open('src/pages/CreateEventPage.tsx', 'w') as f:
    f.write(create_event_page)

print("VendorGrid and CreateEventPage updated")
