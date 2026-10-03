import { useQuery } from '@tanstack/react-query';
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
