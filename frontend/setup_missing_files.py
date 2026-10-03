import os

files = {
    "src/api/client.ts": """import { mockApi } from '../mocks/mockApi';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

export const api = {
  get: async <T>(path: string, params?: Record<string, any>): Promise<T> => {
    if (USE_MOCK) return mockApi.get(path, params) as Promise<T>;
    
    const url = new URL(`${API_URL}${path}`);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) url.searchParams.append(key, String(value));
      });
    }
    const res = await fetch(url.toString(), { headers: { 'Accept': 'application/json' } });
    if (!res.ok) throw await res.json();
    return res.json();
  },
  post: async <T>(path: string, data: any): Promise<T> => {
    if (USE_MOCK) return mockApi.post(path, data) as Promise<T>;
    const res = await fetch(`${API_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw await res.json();
    return res.json();
  },
  patch: async <T>(path: string, data: any): Promise<T> => {
    if (USE_MOCK) return mockApi.patch(path, data) as Promise<T>;
    const res = await fetch(`${API_URL}${path}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw await res.json();
    return res.json();
  },
  delete: async <T>(path: string): Promise<T> => {
    if (USE_MOCK) return mockApi.delete(path) as Promise<T>;
    const res = await fetch(`${API_URL}${path}`, {
      method: 'DELETE',
      headers: { 'Accept': 'application/json' }
    });
    if (!res.ok) throw await res.json();
    return res.json();
  }
};
""",
    "src/mocks/mockApi.ts": """import { mockEventsList, mockEventStatus } from './fixtures';

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const mockApi = {
  get: async (path: string, params?: Record<string, any>) => {
    await delay(300);
    if (path === '/events') return mockEventsList;
    if (path.match(/^\/events\/\d+\/status$/)) {
      // Simulate polling version change
      if (params?.since == mockEventStatus.version) {
         return { changed: false, version: mockEventStatus.version };
      }
      return mockEventStatus;
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
    if (path === '/notify/send') {
      return { results: data.vendor_ids?.map((id: number) => ({ vendor_id: id, ok: true })) || [] };
    }
    if (path.match(/^\/budget\/\d+\/disburse$/)) {
      return { payment_id: 5, kind: data.kind, status: "paid" };
    }
    throw new Error(`Mock NOT FOUND for POST ${path}`);
  },
  patch: async (path: string, data: any) => {
    await delay(300);
    return { ...data, id: parseInt(path.split('/').pop() || '0') };
  },
  delete: async (path: string) => {
    await delay(300);
    return { success: true };
  }
};
""",
    "src/hooks/useEventStatus.ts": """import { useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import type { EventStatus, StatusResponse } from '../api/schema';

export function useEventStatus(id: number) {
  const qc = useQueryClient();
  return useQuery({
    queryKey: ['status', id],
    queryFn: async () => {
      const prev = qc.getQueryData<EventStatus>(['status', id]);
      const res = await api.get<StatusResponse>(`/events/${id}/status`, prev ? { since: prev.version } : {});
      return (res as any).changed === false ? prev! : res as EventStatus;
    },
    refetchInterval: Number(import.meta.env.VITE_POLL_MS ?? 3000),
    refetchIntervalInBackground: false,
  });
}
""",
    "src/hooks/useEvents.ts": """import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import type { EventListItem } from '../api/schema';

export function useEvents() {
  return useQuery({
    queryKey: ['events'],
    queryFn: async () => {
      return api.get<EventListItem[]>('/events');
    }
  });
}
""",
    "src/hooks/useBudget.ts": """import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';

export function useBudget(id: number) {
  return useQuery({
    queryKey: ['budget', id],
    queryFn: async () => {
      return api.get<any>(`/events/${id}/budget`);
    },
    refetchInterval: Number(import.meta.env.VITE_POLL_MS ?? 3000),
    refetchIntervalInBackground: false,
  });
}
""",
    "src/lib/phone.ts": """export function formatPhone(phone: string): string {
  if (!phone) return phone;
  let p = phone.trim();
  if (p.startsWith('0')) {
    p = '+234' + p.substring(1);
  }
  return p;
}
""",
    "src/components/Toast.tsx": """import React from 'react';

export function Toast({ message, type = 'success', onClose }: { message: string, type?: 'success'|'error', onClose: () => void }) {
  return (
    <div className={`fixed top-4 right-4 p-4 rounded shadow-lg z-50 flex items-center gap-3 text-white ${type === 'error' ? 'bg-status-failed' : 'bg-status-confirmed'}`}>
      <span>{message}</span>
      <button onClick={onClose} className="text-white/80 hover:text-white">&times;</button>
    </div>
  );
}
"""
}

for filepath, content in files.items():
    with open(filepath, 'w') as f:
        f.write(content)

print("Files written successfully")
