import { mockEventsList, mockEventStatus } from './fixtures';
import type { EventStatus } from '../api/schema';

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

let statusState = JSON.parse(JSON.stringify(mockEventStatus)) as EventStatus;
let startTime = Date.now();
let hasConfirmed = false;

export const mockApi = {
  get: async (path: string, params?: Record<string, any>) => {
    await delay(300);
    
    if (path === '/events') return mockEventsList;
    if (path.match(/^\/events\/\d+\/status$/)) {
      // Simulate polling version change: vendor confirms after 5 seconds
      if (!hasConfirmed && (Date.now() - startTime) > 5000) {
         hasConfirmed = true;
         // Set one pending/sent vendor to confirmed
         const pendingVendor = statusState.vendors.find(v => v.status === 'sent' || v.status === 'pending');
         if (pendingVendor) {
             const oldStatus = pendingVendor.status;             
             pendingVendor.status = 'confirmed';
             statusState.summary.confirmed += 1;
             if (oldStatus === 'sent') statusState.summary.sent -= 1;
             if (oldStatus === 'pending') statusState.summary.pending -= 1;
             
             statusState.version += 1;
             statusState.activity.unshift({
                id: Date.now(),
                type: 'vendor_confirmed',
                vendor_id: pendingVendor.id,
                text: `${pendingVendor.name} (${pendingVendor.role}) confirmed via WhatsApp`,
                created_at: new Date().toISOString()
             });
         }
      }

      if (params?.since == statusState.version) {
         return { changed: false, version: statusState.version };
      }
      return { ...statusState, changed: true };
    }
    if (path.match(/^\/events\/\d+\/budget$/)) {
      return {
         event_id: 1, currency: "NGN", mode: "sandbox",
         totals: { budget: 97500000, deposits_paid: 20000000, balances_paid: 0, outstanding: 77500000 },
         vendors: [
           { vendor_id: 11, role: "DJ", name: "Kola Beats", vendor_status: "confirmed",
             deposit: { amount: 5000000, status: "paid", paid_at: "2026-11-10T14:10:00Z" },
             balance: { amount: 10000000, status: "due", paid_at: null } }
         ]
      };
    }
    throw new Error(`Mock NOT FOUND for GET ${path}`);
  },
  post: async (path: string, data: any) => {
    await delay(300);
    if (path === '/events') {
      return { id: 1, name: data.name, status: "draft", version: 1, vendors: data.vendors.map((v: any, i: number) => ({ id: 10+i, role: v.role, status: "pending" })) };
    }
    if (path.match(/^\/events\/\d+\/vendors$/)) {
      const newVendor = {
        id: Date.now(),
        role: data.role || '',
        name: data.name || '',
        phone: data.phone || '',
        arrival_time: data.arrival_time || '',
        status: 'pending',
        status_updated_at: new Date().toISOString(),
        deposit: { amount: data.deposit_amount || 0, status: 'not_due' },
        balance: { amount: data.balance_amount || 0, status: 'not_due' }
      };
      statusState.vendors.push(newVendor as any);
      statusState.summary.total += 1;
      statusState.summary.pending += 1;
      statusState.version += 1;
      return newVendor;
    }
    if (path === '/notify/send') {
      // Simulate sending notifications
      const ids = data.vendor_ids || statusState.vendors.map(v => v.id);
      ids.forEach((id: number) => {
         const v = statusState.vendors.find(v => v.id === id);
         if (v && v.status !== 'confirmed') v.status = 'sent';
      });
      statusState.version += 1;
      return { results: ids.map((id: number) => ({ vendor_id: id, ok: true })) };
    }
    if (path.match(/^\/budget\/\d+\/disburse$/)) {
      return { payment_id: 5, kind: data.kind, status: "paid" };
    }
    throw new Error(`Mock NOT FOUND for POST ${path}`);
  },
  patch: async (path: string, data: any) => {
    await delay(300);
    if (path.match(/^\/events\/\d+$/)) {
      statusState.event = { ...statusState.event, ...data };
      statusState.version += 1;
      return statusState.event;
    }
    if (path.match(/^\/events\/\d+\/vendors\/\d+$/)) {
      const vid = parseInt(path.split('/').pop() || '0');
      const idx = statusState.vendors.findIndex(v => v.id === vid);
      if (idx !== -1) {
         statusState.vendors[idx] = { 
           ...statusState.vendors[idx], 
           ...data,
           deposit: { ...statusState.vendors[idx].deposit, amount: data.deposit_amount !== undefined ? data.deposit_amount : statusState.vendors[idx].deposit.amount },
           balance: { ...statusState.vendors[idx].balance, amount: data.balance_amount !== undefined ? data.balance_amount : statusState.vendors[idx].balance.amount }
         };
         statusState.version += 1;
         return statusState.vendors[idx];
      }
    }
    return { ...data, id: parseInt(path.split('/').pop() || '0') };
  },
  delete: async (_path: string) => {
    await delay(300);
    return { success: true };
  }
};
