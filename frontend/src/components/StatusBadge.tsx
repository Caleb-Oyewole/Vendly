import type { VendorStatus, PaymentStatus } from '../api/schema';

interface StatusBadgeProps {
  status: VendorStatus | PaymentStatus | 'active' | 'draft';
  context?: 'vendor' | 'payment';
}

const statusConfig: Record<string, { label: string; className: string }> = {
  // Vendor statuses
  pending: { label: 'Not sent', className: 'bg-slate-100 text-slate-700' },
  sent: { label: 'Awaiting reply', className: 'bg-blue-100 text-status-awaiting' },
  confirmed: { label: 'Confirmed', className: 'bg-green-100 text-status-confirmed' },
  declined: { label: 'Declined', className: 'bg-red-100 text-status-declined' },
  // Event statuses
  active: { label: 'Active', className: 'bg-green-100 text-status-confirmed' },
  draft: { label: 'Draft', className: 'bg-slate-100 text-slate-700' },
  
  // Payment statuses
  not_due: { label: 'Not due', className: 'bg-slate-100 text-slate-700' },
  due: { label: 'Due', className: 'bg-amber-100 text-accent' },
  processing: { label: 'Processing', className: 'bg-blue-100 text-status-awaiting' },
  paid: { label: 'Paid', className: 'bg-green-100 text-status-confirmed' },
};

export default function StatusBadge({ status, context = 'vendor' }: StatusBadgeProps) {
  let config = statusConfig[status] || { label: status, className: 'bg-slate-100 text-slate-700' };

  if (status === 'failed') {
    if (context === 'payment') {
      config = { label: 'Failed', className: 'bg-red-100 text-status-declined' };
    } else {
      config = { label: 'Send failed', className: 'bg-orange-100 text-status-failed' };
    }
  }

  return (
    <span className={`inline-flex items-center rounded-badge px-2.5 py-0.5 text-xs font-medium ${config.className}`}>
      {config.label}
    </span>
  );
}
