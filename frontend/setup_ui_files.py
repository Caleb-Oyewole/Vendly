import os

files = {
    "src/components/ConfirmDialog.tsx": """import React from 'react';

export default function ConfirmDialog({ title, text, onConfirm, onCancel, confirmText = 'Confirm' }: any) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/50">
      <div className="w-full max-w-md rounded-card bg-white p-6 shadow-xl">
        <h3 className="text-lg font-semibold text-ink">{title}</h3>
        <p className="mt-2 text-sm text-muted">{text}</p>
        <div className="mt-6 flex justify-end gap-3">
          <button onClick={onCancel} className="rounded-btn border border-line px-4 py-2 text-sm font-medium text-ink hover:bg-slate-50">Cancel</button>
          <button onClick={onConfirm} className="rounded-btn bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand/90">{confirmText}</button>
        </div>
      </div>
    </div>
  );
}
""",
    "src/components/DataTable.tsx": """import React from 'react';

export default function DataTable({ children }: any) {
  return <div className="overflow-x-auto"><table className="w-full text-left text-sm">{children}</table></div>;
}
""",
    "src/components/states/Empty.tsx": """import React from 'react';

export default function Empty({ message, action }: any) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-line rounded-card bg-surface/50">
      <p className="mb-4 text-sm font-medium text-muted">{message}</p>
      {action}
    </div>
  );
}
""",
    "src/components/states/Error.tsx": """import React from 'react';

export default function ErrorState({ message, onRetry }: any) {
  return (
    <div className="p-4 bg-status-declined/10 text-status-declined rounded border border-status-declined/20">
      <p className="text-sm font-medium mb-2">{message}</p>
      {onRetry && <button onClick={onRetry} className="text-sm underline hover:no-underline">Retry</button>}
    </div>
  );
}
""",
    "src/components/states/Skeleton.tsx": """import React from 'react';

export default function Skeleton({ rows = 3 }: { rows?: number }) {
  return (
    <div className="space-y-4 animate-pulse">
      {Array(rows).fill(0).map((_, i) => (
        <div key={i} className="h-24 bg-line rounded-card w-full"></div>
      ))}
    </div>
  );
}
"""
}

for filepath, content in files.items():
    with open(filepath, 'w') as f:
        f.write(content)
print("UI files written")
