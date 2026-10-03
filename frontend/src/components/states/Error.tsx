

export default function ErrorState({ message, onRetry }: any) {
  return (
    <div className="p-4 bg-status-declined/10 text-status-declined rounded border border-status-declined/20">
      <p className="text-sm font-medium mb-2">{message}</p>
      {onRetry && <button onClick={onRetry} className="text-sm underline hover:no-underline">Retry</button>}
    </div>
  );
}
