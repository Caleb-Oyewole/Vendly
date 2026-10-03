export default function LivePill() {
  return (
    <div className="inline-flex items-center gap-1.5 rounded-badge bg-green-50 px-2.5 py-1 border border-green-200">
      <span className="relative flex h-2 w-2">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-status-confirmed opacity-75"></span>
        <span className="relative inline-flex rounded-full h-2 w-2 bg-status-confirmed"></span>
      </span>
      <span className="text-[10px] font-bold text-status-confirmed tracking-wide">LIVE</span>
    </div>
  );
}
