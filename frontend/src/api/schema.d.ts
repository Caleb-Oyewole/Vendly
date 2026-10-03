export type VendorStatus = 'pending' | 'sent' | 'confirmed' | 'declined' | 'failed';
export type PaymentStatus = 'not_due' | 'due' | 'processing' | 'paid' | 'failed';

export interface Money {
  amount: number; // in kobo
  status: PaymentStatus;
  paid_at?: string | null;
}

export interface Vendor {
  id: number;
  role: string;
  name: string;
  phone: string;
  arrival_time: string;
  status: VendorStatus;
  status_updated_at: string;
  deposit: Money;
  balance: Money;
}

export interface EventListItem {
  id: number;
  name: string;
  event_date: string;
  venue: string;
  status: 'draft' | 'active';
  vendor_count: number;
  confirmed_count: number;
  total_budget: number; // in kobo
}

export interface Activity {
  id: number;
  type: string;
  vendor_id: number;
  text: string;
  created_at: string;
}

export interface EventStatus { 
  changed: true; 
  version: number; 
  event: any; 
  summary: Record<VendorStatus | 'total', number>; 
  vendors: Vendor[]; 
  activity: Activity[];
}

export type StatusResponse = EventStatus | { changed: false; version: number };