import os

filepath = 'src/pages/EventBudgetPage.tsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix StatusBadge contexts for deposits and balances
content = content.replace(
    '<StatusBadge status={vendor.deposit.status as VendorStatus} />', 
    '<StatusBadge status={vendor.deposit.status as VendorStatus} context="payment" />'
)
content = content.replace(
    '<StatusBadge status={vendor.balance.status as VendorStatus} />', 
    '<StatusBadge status={vendor.balance.status as VendorStatus} context="payment" />'
)

# Replace the nextAction logic entirely
old_logic = """              if (vendor.deposit.status === 'due') {
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
              }"""

new_logic = """              if (vendor.deposit.status === 'due' || vendor.deposit.status === 'failed') {
                nextAction = (
                  <button 
                    onClick={() => handlePayDepositClick(vendor.vendor_id, vendor.name, vendor.deposit.amount)}
                    className={`rounded-btn px-4 py-1.5 text-xs font-semibold text-white shadow-sm active:scale-95 transition-all ${vendor.deposit.status === 'failed' ? 'bg-status-declined hover:bg-status-declined/90' : 'bg-brand hover:bg-brand/90'}`}
                  >
                    {vendor.deposit.status === 'failed' ? 'Retry deposit' : 'Pay deposit'}
                  </button>
                );
              } else if (vendor.deposit.status === 'paid' && (vendor.balance.status === 'due' || vendor.balance.status === 'failed')) {
                nextAction = (
                  <button 
                    onClick={() => handleReleaseBalanceClick(vendor.vendor_id, vendor.name, vendor.balance.amount)}
                    className={`rounded-btn px-4 py-1.5 text-xs font-semibold text-white shadow-sm active:scale-95 transition-all ${vendor.balance.status === 'failed' ? 'bg-status-declined hover:bg-status-declined/90' : 'bg-brand hover:bg-brand/90'}`}
                  >
                    {vendor.balance.status === 'failed' ? 'Retry balance' : 'Release balance'}
                  </button>
                );
              } else if (vendor.deposit.status === 'processing' || vendor.balance.status === 'processing') {
                 nextAction = <span className="text-status-awaiting font-medium flex items-center gap-2"><svg className="animate-spin h-3 w-3" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Processing...</span>;
              }"""

content = content.replace(old_logic, new_logic)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
