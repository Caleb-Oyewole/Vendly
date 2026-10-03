

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
