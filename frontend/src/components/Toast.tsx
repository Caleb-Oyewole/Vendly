

export function Toast({ message, type = 'success', onClose }: { message: string, type?: 'success'|'error', onClose: () => void }) {
  return (
    <div className={`fixed top-4 right-4 p-4 rounded shadow-lg z-50 flex items-center gap-3 text-white ${type === 'error' ? 'bg-status-failed' : 'bg-status-confirmed'}`}>
      <span>{message}</span>
      <button onClick={onClose} className="text-white/80 hover:text-white">&times;</button>
    </div>
  );
}
