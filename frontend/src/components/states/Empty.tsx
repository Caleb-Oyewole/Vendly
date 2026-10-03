

export default function Empty({ message, action }: any) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-line rounded-card bg-surface/50">
      <p className="mb-4 text-sm font-medium text-muted">{message}</p>
      {action}
    </div>
  );
}
