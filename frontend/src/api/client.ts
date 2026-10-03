import { mockApi } from '../mocks/mockApi';

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
