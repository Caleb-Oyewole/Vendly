import { useQuery } from '@tanstack/react-query';
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
