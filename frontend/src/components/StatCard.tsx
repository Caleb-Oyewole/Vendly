interface StatCardProps {
  label: string;
  value: number | string;
  valueColor?: string;
  prefix?: string;
  isMoney?: boolean;
}

export default function StatCard({ label, value, valueColor = "text-ink", prefix = "", isMoney = false }: StatCardProps) {
  let displayValue = value;
  if (isMoney && typeof value === 'number') {
     displayValue = (value / 100).toLocaleString();
  }
  return (
    <div className="rounded-card border border-line bg-white p-4 shadow-sm">
      <span className="text-xs font-medium text-muted block mb-1">{label}</span>
      <div className={`text-2xl font-semibold ${valueColor}`}>{prefix}{displayValue}</div>
    </div>
  );
}
