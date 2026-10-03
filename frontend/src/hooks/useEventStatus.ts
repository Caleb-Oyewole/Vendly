import { useQuery, useQueryClient } from '@tanstack/react-query';
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
