import os

with open('src/mocks/mockApi.ts', 'r') as f:
    mock_api = f.read()

# Add POST /events/{id}/vendors
if "/events/1/vendors" not in mock_api:
    new_post = """    if (path.match(/^\\/events\\/\\d+\\/vendors$/)) {
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
"""
    # Find where to inject
    mock_api = mock_api.replace("if (path === '/notify/send')", new_post + "    if (path === '/notify/send')")


old_patch = """  patch: async (path: string, data: any) => {
    await delay(300);
    return { ...data, id: parseInt(path.split('/').pop() || '0') };
  },"""

new_patch = """  patch: async (path: string, data: any) => {
    await delay(300);
    if (path.match(/^\\/events\\/\\d+\\/vendors\\/\\d+$/)) {
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
  },"""
  
mock_api = mock_api.replace(old_patch, new_patch)

with open('src/mocks/mockApi.ts', 'w') as f:
    f.write(mock_api)
print("Updated mockApi")
