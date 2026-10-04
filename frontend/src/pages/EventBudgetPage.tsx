import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import type { VendorStatus } from '../api/schema';
import StatCard from '../components/StatCard';
import StatusBadge from '../components/StatusBadge';
import { useBudget } from '../hooks/useBudget';
import Skeleton from '../components/states/Skeleton';
import ErrorState from '../components/states/Error';
import { api } from '../api/client';
import { Toast } from '../components/Toast';

export default function EventBudgetPage() {
  const { id } = useParams();
  const eventId = Number(id);
  
  const { data: budgetData, isLoading, isError, refetch } = useBudget(eventId);

  const [confirmModal, setConfirmModal] = useState<{
    isOpen: boolean;
    type: 'deposit' | 'balance' | null;
    vendorId: number;
    vendorName: string;
    amount: number;
  }>({
    isOpen: false,
    type: null,
    vendorId: 0,
    vendorName: '',
    amount: 0
  });

  const [toast, setToast] = useState<{message: string, type: 'success' | 'error'} | null>(null);

  if (isLoading) return <div className="p-8"><Skeleton rows={5} /></div>;
  if (isError || !budgetData) return <div className="p-8"><ErrorState message="Could not load budget data" onRetry={() => refetch()} /></div>;

  const { totals, vendors, mode } = budgetData;

  const progressPercent = totals.budget > 0 ? ((totals.deposits_paid + totals.balances_paid) / totals.budget) * 100 : 0;

  const handlePayDepositClick = (vendorId: number, vendorName: string, amount: number) => {
    setConfirmModal({
      isOpen: true,
      type: 'deposit',
      vendorId,
      vendorName,
      amount
    });
  };

  const handleReleaseBalanceClick = (vendorId: number, vendorName: string, amount: number) => {
    setConfirmModal({
      isOpen: true,
      type: 'balance',
      vendorId,
      vendorName,
      amount
    });
  };

  const executePayment = async () => {
    if (!confirmModal.type || !confirmModal.vendorId) return;
    try {
      const res = await api.post<any>(`/budget/${confirmModal.vendorId}/disburse`, { kind: confirmModal.type });
      setToast({message: `Payment ${res.status}`, type: 'success'});
      setConfirmModal({ ...confirmModal, isOpen: false });
      refetch();
    } catch (e) {
      setToast({message: 'Payment failed', type: 'error'});
    }
  };

  return (
    <div className="space-y-6">
      {toast?.message && <Toast message={toast?.message} onClose={() => setToast({message: '', type: 'success'})} />}

      {/* Header section (re-used structure) */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-ink tracking-tight">Budget Management</h1>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-line flex gap-6">
        <Link to={`/events/${id}`} className="pb-3 border-b-2 border-transparent text-muted hover:text-ink font-medium text-sm transition-colors">
          Vendors
        </Link>
        <Link to={`/events/${id}/budget`} className="pb-3 border-b-2 border-brand font-semibold text-brand text-sm">
          Budget
        </Link>
      </div>

      {mode === 'sandbox' && (
        <div className="bg-accent/20 text-accent-800 text-sm font-medium p-3 text-center rounded-card">
          Sandbox mode: no real money moves. Payments are simulated or run against test keys.
        </div>
      )}

      {/* Stats Row */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Total budget" value={totals.budget} prefix="NGN " isMoney />
        <StatCard label="Deposits paid" value={totals.deposits_paid} prefix="NGN " isMoney valueColor="text-status-confirmed" />
        <StatCard label="Balances released" value={totals.balances_paid} prefix="NGN " isMoney valueColor="text-status-confirmed" />
        <StatCard label="Outstanding" value={totals.outstanding} prefix="NGN " isMoney valueColor="text-status-failed" />
      </div>

      {/* Progress Bar */}
      <div>
        <div className="mb-1.5 text-sm font-medium text-muted">
          {Math.round(progressPercent)}% of budget paid
        </div>
        <div className="h-3 w-full rounded-full bg-surface overflow-hidden shadow-inner">
          <div
            className="h-full bg-status-confirmed transition-all duration-500"
            style={{ width: `${Math.min(progressPercent, 100)}%` }}
          />
        </div>
      </div>

      {/* Budget Table */}
      <div className="rounded-card border border-line bg-white overflow-hidden shadow-sm mt-8">
        <table className="w-full text-left text-sm">
          <thead className="bg-surface border-b border-line">
            <tr>
              <th className="px-5 py-3 font-semibold text-muted">Vendor</th>
              <th className="px-5 py-3 font-semibold text-muted">Vendor status</th>
              <th className="px-5 py-3 font-semibold text-muted">Deposit</th>
              <th className="px-5 py-3 font-semibold text-muted">Balance</th>
              <th className="px-5 py-3 font-semibold text-muted text-right">Next action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line/50">
            {vendors.map((vendor: any) => {
              let nextAction = <span className="text-muted font-medium">Waiting</span>;
              
              if (vendor.deposit.status === 'due') {
                nextAction = (
                  <button 
                    onClick={() => handlePayDepositClick(vendor.vendor_id, vendor.name, vendor.deposit.amount)}
                    className="rounded-btn bg-brand px-4 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-brand/90 active:scale-95 transition-all"
                  >
                    Pay deposit
                  </button>
                );
              } else if (vendor.deposit.status === 'paid' && vendor.balance.status === 'due') {
                nextAction = (
                  <button 
                    onClick={() => handleReleaseBalanceClick(vendor.vendor_id, vendor.name, vendor.balance.amount)}
                    className="rounded-btn bg-brand px-4 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-brand/90 active:scale-95 transition-all"
                  >
                    Release balance
                  </button>
                );
              } else if (vendor.deposit.status === 'processing' || vendor.balance.status === 'processing') {
                 nextAction = <span className="text-status-awaiting font-medium">Processing...</span>;
              }

              return (
                <tr key={vendor.vendor_id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-5 py-4 font-bold text-ink">
                    {vendor.name} <span className="text-muted font-normal">({vendor.role})</span>
                  </td>
                  <td className="px-5 py-4">
                    <StatusBadge status={vendor.vendor_status as VendorStatus} />
                  </td>
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      <span className="font-medium text-ink w-20">{(vendor.deposit.amount / 100).toLocaleString()}</span>
                      <StatusBadge status={vendor.deposit.status as VendorStatus} />
                    </div>
                  </td>
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      <span className="font-medium text-ink w-20">{(vendor.balance.amount / 100).toLocaleString()}</span>
                      <StatusBadge status={vendor.balance.status as VendorStatus} />
                    </div>
                  </td>
                  <td className="px-5 py-4 text-right">
                    {nextAction}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* --- PROFESSIONAL PAYMENT CONFIRMATION MODAL --- */}
      {confirmModal.isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div 
            className="absolute inset-0 bg-ink/40 backdrop-blur-sm transition-opacity"
            onClick={() => setConfirmModal({ ...confirmModal, isOpen: false })}
          ></div>
          
          <div className="bg-white w-full max-w-sm rounded-card border border-line shadow-2xl relative overflow-hidden flex flex-col z-10 animate-in fade-in zoom-in-95 duration-200">
            <div className="p-6">
              <h3 className="text-lg font-bold text-ink mb-2">Confirm Payment</h3>
              <p className="text-sm text-muted">
                Are you sure you want to release the {confirmModal.type === 'deposit' ? 'deposit' : 'final balance'} of <span className="font-bold text-ink">NGN {(confirmModal.amount / 100).toLocaleString()}</span> to <span className="font-bold text-ink">{confirmModal.vendorName}</span>?
              </p>
              {mode === 'sandbox' && <p className="text-xs text-muted mt-2 italic">(Sandbox: no real money moves)</p>}
            </div>
            
            <div className="bg-surface px-6 py-4 border-t border-line flex justify-end gap-3">
              <button 
                onClick={() => setConfirmModal({ ...confirmModal, isOpen: false })}
                className="px-4 py-2 rounded-btn text-sm font-semibold text-muted hover:text-ink hover:bg-black/5 transition-colors active:scale-95"
              >
                Cancel
              </button>
              <button 
                onClick={executePayment}
                className="px-4 py-2 rounded-btn text-sm font-semibold bg-brand text-white hover:bg-brand/90 transition-colors shadow-sm active:scale-95 flex items-center gap-2"
              >
                Confirm Payment
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
